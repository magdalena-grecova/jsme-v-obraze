import argparse
import json
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from threading import Lock

import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Definovani promennych a konstant
# ---------------------------------------------------------------------------

START_DATE     = date(2020, 1, 1)
END_DATE       = date.today()
DEFAULT_OUTPUT = "tv_program.json"
DEFAULT_WORKERS = 4
RETRY_COUNT    = 4
RETRY_BACKOFF  = 2.0
DAY_DELAY      = 0.3   # pauza mezi dny v jednom vlakne (s)

API_URL = "https://tv.seznam.cz/api/schedules"

CHANNELS = {
    1:   "CT1",
    2:   "CT2",
    358: "CT art",
    3:   "Nova",
    78:  "Nova Cinema",
    4:   "Prima",
    92:  "Prima Cool",
    460: "Prima Max",
    226: "Prima love",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
    "Accept": "application/vnd.seznam.tv.api+hal+json;profile=web;version=1",
    "Accept-Language": "cs",
    "Accept-Encoding": "gzip, deflate, br",
    "api-password": "4b48603a7d3ac5deab5399142aac923a",
    "Referer": "https://tv.seznam.cz/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pomocne funkce
# ---------------------------------------------------------------------------

def day_to_timestamps(d: date):
    # timestamp_from = 00:00 daneho dne (Prague time = UTC+1 nebo UTC+2)
    dt_from = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)
    dt_to   = dt_from + timedelta(hours=30)
    return int(dt_from.timestamp()), int(dt_to.timestamp())


def parse_director(short_description: str) -> str | None:
    if not short_description:
        return None
    m = re.search(r"[Rr]ežie:?\s*([^.(,\n]+)", short_description)
    if m:
        return m.group(1).strip().rstrip(".,")
    return None


def parse_duration(short_description: str) -> int | None:
    if not short_description:
        return None
    m = re.search(r"\((\d+)\s*min\)", short_description)
    if m:
        return int(m.group(1))
    return None


# ---------------------------------------------------------------------------
# HTTP + parsovani
# ---------------------------------------------------------------------------

def fetch_day(d: date, session: requests.Session) -> list[dict]:
    ts_from, ts_to = day_to_timestamps(d)
    channel_ids = ",".join(str(cid) for cid in CHANNELS)

    # sestaveni URL –  aby carky nebyly jako %2C, API to odmita
    url = "{}?channel_ids={}&timestamp_from={}&timestamp_to={}".format(
        API_URL, channel_ids, ts_from, ts_to
    )

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            wait = RETRY_BACKOFF ** attempt
            if attempt < RETRY_COUNT:
                log.warning("Pokus %d/%d selhal (%s): %s – cekam %ds",
                            attempt, RETRY_COUNT, d, e, int(wait))
                time.sleep(wait)
            else:
                log.error("Vsechny pokusy selhaly (%s): %s", d, e)
                return []

    shows = []
    date_str = d.isoformat()

    for schedule in data.get("_embedded", {}).get("tv:schedule", []):
        emb = schedule.get("_embedded", {})

        # Stanice
        channel_info = emb.get("tv:channel", {})
        channel_id   = channel_info.get("id")
        channel_name = CHANNELS.get(channel_id, channel_info.get("name", ""))

        # Porady
        for prog in emb.get("tv:programme", []):
            time_from = prog.get("time_from")
            time_to   = prog.get("time_to")

            # Cas vysilani (local time Praha)
            if time_from:
                dt = datetime.fromtimestamp(time_from)
                time_str = dt.strftime("%H:%M")
                day_str  = dt.strftime("%Y-%m-%d")
            else:
                time_str = ""
                day_str  = date_str

            # Stopaz
            duration_min = None
            if time_from and time_to:
                duration_min = round((time_to - time_from) / 60)

            desc = prog.get("short_description") or ""

            # Reziser z popisu 
            director = parse_director(desc)

            # Fallback stopaze z popisu
            if not duration_min:
                duration_min = parse_duration(desc)

            shows.append({
                "date":              day_str,
                "channel":           channel_name,
                "time":              time_str,
                "title":             prog.get("name", ""),
                "type":              prog.get("type") or "",
                "short_description": desc or None,
                "director":          director,
                "duration_min":      duration_min,
                "year":              prog.get("year"),
            })

    return shows


# ---------------------------------------------------------------------------
# Vytvoreni slovniku pro JSON
# ---------------------------------------------------------------------------

class DataStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.lock = Lock()
        self.data: dict = {}

        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    self.data = json.load(f)
                log.info("Resume: nacteno %d dni z %s", len(self.data), self.path)
            except Exception as e:
                log.warning("Nepodarilo se nacist %s: %s", self.path, e)

    def has(self, d: date) -> bool:
        return d.isoformat() in self.data

    def save_day(self, d: date, shows: list):
        with self.lock:
            self.data[d.isoformat()] = shows
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            tmp.replace(self.path)


# ---------------------------------------------------------------------------
# Stazeni
# ---------------------------------------------------------------------------

def worker(d: date, store: DataStore, session: requests.Session):
    if store.has(d):
        return d, True
    try:
        shows = fetch_day(d, session)
        store.save_day(d, shows)
        time.sleep(DAY_DELAY)
        return d, True
    except Exception as e:
        log.error("Selhalo %s: %s", d, e)
        return d, False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def date_range(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    parser = argparse.ArgumentParser(description="TV scraper – tv.seznam.cz API")
    parser.add_argument("--start",   default=START_DATE.isoformat())
    parser.add_argument("--end",     default=END_DATE.isoformat())
    parser.add_argument("--output",  default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()

    try:
        start = date.fromisoformat(args.start)
        end   = date.fromisoformat(args.end)
    except ValueError as e:
        print("Chybne datum:", e); sys.exit(1)

    days  = list(date_range(start, end))
    store = DataStore(args.output)
    to_do = sum(1 for d in days if not store.has(d))
    done  = len(days) - to_do

    print("\n📺  TV Program Scraper – tv.seznam.cz API")
    print("   Stanice: CT1, CT2, CT art, Nova, Nova Cinema, Prima, Prima Cool, Prima Max, Prima love")
    print("   Obdobi:  {} -> {}  ({} dni)".format(start, end, len(days)))
    print("   Vystup:  {}".format(args.output))
    print("   Hotovo:  {}/{} (zbyvá {})".format(done, len(days), to_do))
    print()

    if to_do == 0:
        print("Vsechno stazene."); return

    failed = []
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {
                ex.submit(worker, d, store, session): d
                for d in days if not store.has(d)
            }
            with tqdm(total=to_do, unit="den", ncols=80) as bar:
                for fut in as_completed(futures):
                    d, ok = fut.result()
                    if not ok:
                        failed.append(d)
                    bar.update(1)
                    bar.set_postfix({"den": str(d), "chyby": len(failed)})

    print("\nHotovo! Celkem dni v souboru: {}".format(len(store.data)))
    print("Soubor: {}".format(str(store.path.resolve())))

    if failed:
        print("\nSelhalo {} dni – spust znovu pro retry:".format(len(failed)))
        for d in sorted(failed):
            print("   {}".format(d))

    # Ukazka
    print("\n── Ukazka (prvnich 5 poradu prvniho dne) ──")
    for day_str, shows in sorted(store.data.items())[:1]:
        print("Datum:", day_str)
        for s in shows[:5]:
            print("  {:<14} {:>5}  [{:<12}]  {}  ({}  min, reziser: {})".format(
                s["channel"], s["time"], s["type"] or "-",
                s["title"], s["duration_min"], s["director"] or "-"
            ))


if __name__ == "__main__":
    main()