import pandas as pd
import json

# 1. Načtení JSON
with open('tv_program.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_items = []
for date, shows in data.items():
    all_items.extend(shows)

df = pd.DataFrame(all_items)
print(f"Celkem řádků: {len(df)}")

# 2. Filtrovat filmy
df_filmy = df[df['type'].str.lower() == 'film'].copy()
print(f"Filmů celkem: {len(df_filmy)}")

# 3. Odstranit duplicity
df_unikatni = df_filmy[['title', 'year']].drop_duplicates().copy()
print(f"Unikátních kombinací title+year: {len(df_unikatni)}")

# 4. Načtení whitelistu cyklů
cykly_df = pd.read_csv('cykly_kontrola_fin.csv', encoding='utf-8-sig', sep=';')
whitelist = set(cykly_df[cykly_df['je_cyklus'] == 1]['za_carkou'].tolist())
print(f"Cyklů v whitelistu: {len(whitelist)}")  

# 5. Oprava názvů
def oprav_nazev(title):
    if ',' not in title:
        return title
    pred_carkou = title.split(',')[0].strip()
    za_carkou = title.split(',', 1)[1].strip()
    if za_carkou in whitelist:
        return pred_carkou
    return title

df_unikatni['title_clean'] = df_unikatni['title'].apply(oprav_nazev)

# Kontrola - Kolik záznamů bylo opraveno?
opraveno = (df_unikatni['title_clean'] != df_unikatni['title']).sum()
print(f"Opravených názvů: {opraveno}")
print("\nPříklady oprav:")
print(df_unikatni[df_unikatni['title_clean'] != df_unikatni['title']][['title', 'title_clean']].head(20))

# 6. Export výsledku
df_unikatni[['title_clean', 'year']].drop_duplicates().to_csv('filmy_seznam_clean.csv', index=False, encoding='utf-8-sig')
print("\nHotovo! Uloženo do filmy_seznam_clean.csv")