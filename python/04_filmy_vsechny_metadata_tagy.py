import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import ast

# 1. NAČTENÍ A SJEDNOCENÍ DAT

df_hlavni = pd.read_csv('filmy_tmdb_metadata_doplnene.csv')
df_cyklove = pd.read_csv('cyklove_filmy_metadata.csv')

print(f"Hlavní databáze: {len(df_hlavni)} filmů")
print(f"Cyklové filmy: {len(df_cyklove)} filmů")

# sjednocení do jedné tabulky
df = pd.concat([df_hlavni, df_cyklove], ignore_index=True)

# odstranění duplicit podle TMDB id (cyklové filmy mohly být částečně i v hlavní)
df = df.drop_duplicates(subset='id', keep='first')

# filmy bez tmdb_id (nenamatchované) ponech také, ale odstraň jejich duplikáty podle názvu
df_s_id    = df[df['id'].notna()]
df_bez_id  = df[df['id'].isna()].drop_duplicates(subset='title', keep='first')
df = pd.concat([df_s_id, df_bez_id], ignore_index=True)

print(f"Po sjednocení: {len(df)} filmů")

# 2. PARSOVÁNÍ KEYWORDS 
    
def parse_keywords(kw):
    if pd.isna(kw):
        return []
    if isinstance(kw, list):
        return kw
    kw = kw.strip()
    # pokud je to list jako string ['tag1', 'tag2']
    if kw.startswith('['):
        try:
            return ast.literal_eval(kw)
        except:
            return []
    # pokud je to prostý string oddělený čárkami
    return [tag.strip() for tag in kw.split(',')]

df['keywords_list'] = df['keywords'].apply(parse_keywords)

# 3. MULTILABELBINARIZER PRO QUEER TAGY

QUEER_TAGS = [
    'gay theme',
    'lgbt',
    'queer',
    'lesbian relationship',
    'male homosexuality',
    'closeted homosexual',
    'transgender',
    'transsexual',
    'drag queen',
    'coming out',
    'lgbt teen',
    'homophobia',
    'gay marriage',
    'gay',
    'lesby',
    'bisexualita',
    'homosexualita',
    'transsexuality',
    'transvestita',
]

def filter_queer_tags(kw_list):
    return [tag for tag in kw_list if tag.lower() in QUEER_TAGS]

df['queer_tags'] = df['keywords_list'].apply(filter_queer_tags)

mlb = MultiLabelBinarizer(classes=QUEER_TAGS)
tag_matrix = mlb.fit_transform(df['queer_tags'])
df_tags = pd.DataFrame(tag_matrix, columns=mlb.classes_, index=df.index)

# 4. FINÁLNÍ TABULKA A ULOŽENÍ

df_final = pd.concat([df, df_tags], axis=1)
df_final = df_final.drop(columns=['keywords_list', 'queer_tags'])

df_final.to_csv('filmy_vsechny_metadata.csv', index=False)

print(f"\nUloženo do filmy_vsechny_metadata.csv ({len(df_final)} filmů)")
print(f"\nZastoupení queer tagů:")
print(df_final[QUEER_TAGS].sum().sort_values(ascending=False).to_string())