import pandas as pd
from datetime import timedelta

df_program = pd.read_csv('tv_program.csv', sep=';', encoding='utf-8-sig')
df_meta = pd.read_csv('filmy_vsechny_metadata.csv', encoding='utf-8-sig')


df_merged = df_program.merge(df_meta, on='title', how='left')

df_merged['slunec'] = pd.to_datetime(df_merged['slunec'], dayfirst=True)

# Seřazení podle title, channel, slunec
df_sorted = df_merged.sort_values(['title', 'channel', 'slunec']).reset_index(drop=True)

# Testovací vzorek
df_test = df_sorted

# Deduplikace
seen = {}
keep = []
merged_info = []

for _, row in df_test.iterrows():
    key = (row['title'], row['channel'])
    datum = row['slunec']
    
    if key not in seen:
        seen[key] = datum
        keep.append(True)
    else:
        diff = datum - seen[key]
        if diff <= timedelta(days=7):
            merged_info.append(f"SLOUČENO: {row['title']} ({row['channel']}) {datum.date()} → zachován {seen[key].date()}")
            keep.append(False)
        else:
            seen[key] = datum
            keep.append(True)


df_final = df_test[keep]
df_final.to_csv('tv_program_final.csv', index=False, encoding='utf-8-sig')