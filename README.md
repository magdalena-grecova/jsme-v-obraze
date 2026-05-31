# Jsme v obraze? 
### Queer filmy v českém televizním vysílání (2020–2026)

Projektová práce v rámci [Digitální akademie Data](https://www.czechitas.cz/kurzy/digitalni-akademie-data) – Czechitas (jaro 2026)

**Autorky:** Magdalena Grecová & Kateřina Košínová  
**Mentorky:** Petra Marková, Petra Holbová, Jana Kadlecová


## O projektu

Cílem projektu bylo zanalyzovat zastoupení queer filmů v českém televizním vysílání za posledních šest let. Sledované stanice: ČT1, ČT2, ČT Art, Nova, Nova Cinema, Prima, Prima Max, Prima Love.

**Hlavní zjištění:** Za posledních šest let bylo v českém televizním vysílání k vidění 116 queer filmů – necelé 1 % ze všech vysílaných filmů. Queer reprezentace existuje, ale zůstává spíše symbolická.


## Výzkumné otázky

- Která stanice vysílá nejvíc queer filmů?
- Která stanice filmy nejvíc opakuje?
- V jakém časovém slotu se queer filmy vysílají?
- Jaké je zastoupení českých queer filmů?
- Jaký je nejčastější žánr a země produkce?


## Zdroje dat

| Zdroj | Data |
|-------|------|
| [tv.seznam.cz](https://tv.seznam.cz) | TV program 2020–2025 (interní JSON API) |
| [TMDB API](https://www.themoviedb.org/) | Metadata filmů |
| [ČSFD](https://www.csfd.cz/) | Doplňkové queer tagy (Selenium scraping) |


## Technologie

- **Python** – web scraping, volání API, čištění dat
- **SQL / Snowflake** – finální čištění, příprava dat pro vizualizace (Keboola)
- **Tableau Public** – interaktivní vizualizace


## Struktura repozitáře

````
├── python/
│   ├── 01_tv_scraper.py                    # Stahování TV programu z tv.seznam.cz (JSON API)
│   ├── 02_tmdb_api_filmy_metadata.py       # Získávání metadat z TMDB API
│   ├── 03_program_cykly.py                 # Čištění názvů filmů – odstranění TV cyklů
│   ├── 04_filmy_vsechny_metadata_tagy.py   # Zpracování queer tagů, MultiLabelBinarizer
│   └── 05_metadata_program_merge.py        # Spojení TV programu s metadaty
├── sql/
│   ├── casove_sloty.sql                    # Analýza časových slotů vysílání
│   ├── filmy_dtb.sql                       # Základní přehled filmů
│   ├── nejcastejsi_zanr.sql                # Nejčastější žánry queer filmů
│   ├── rozdeleni_seznamu_zemi.sql          # Rozdělení podle zemí produkce
│   ├── trend_pocty_na_rok.sql              # Trend počtu queer filmů po letech
│   └── zmena_datovych_typu.sql             # Úprava datových typů
└── README.md
````

## Vizualizace

[Zobrazit dashboard v Tableau Public](https://public.tableau.com/app/profile/magdalena.grecov./viz/DA_queer_filmy/Dashboard2?publish=yes)

---

## Zajímavé technické výzvy

**Scraping TV programu** – tv.seznam.cz využívá architekturu React SPA, přímé parsování HTML nebylo možné. Řešení: interní JSON API objevené přes DevTools.

**Čištění názvů filmů** – filmy uváděné v rámci TV cyklů měly v názvu i název cyklu (např. *„Manželství po italsku, Marcello Mastroianni – 100 let"*). Kombinace automatického zpracování a ruční kontroly whitelist v Excelu.

**Deduplikace vysílání** – stejný film vysílaný na stejné stanici do 7 dní počítán jako jedno uvedení.

**Queer tagy** – celkem 19 binárních sloupců pomocí `MultiLabelBinarizer` (scikit-learn), kombinace tagů z TMDB a ČSFD.