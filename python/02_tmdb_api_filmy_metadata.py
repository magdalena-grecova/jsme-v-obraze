api_key = ''
url_base = 'https://api.themoviedb.org/3/movie/'

import requests
import pandas as pd
import time
import os

df = pd.read_csv('filmy_tmdb.csv', sep=',')

def get_film_metadata(film_id): 
    time.sleep(0.1)

    try:
        #request na metadata filmu podle ID
        response = requests.get(
            f"{url_base}{int(film_id)}",
            params={
                'api_key': api_key,
                'language': 'cs-CZ',
            },
            timeout=10
        )
        data = response.json()

    #request na keywords filmu podle ID
        response_kw = requests.get(
            f"{url_base}{int(film_id)}/keywords",
            params={
                'api_key': api_key,
            },
            timeout=10
        )
        data_kw = response_kw.json()
    
        return {
            'id': data['id'],
            'title': data['title'],
            'original_title': data['original_title'],
            'release_date': data['release_date'],
            'runtime': data['runtime'],
            'budget': data['budget'],
            'genres': [genre['name'] for genre in data['genres']],
            'origin_country': data['origin_country'],
            'original_language': data['original_language'],
            'production_companies': [company['name'] for company in data['production_companies']],
            'production_company_countries': [company['origin_country'] for company in data['production_companies']],
            'production_countries': [country['name'] for country in data['production_countries']],
            'spoken_languages': [lang['name'] for lang in data['spoken_languages']],
            'vote_average': data['vote_average'],
            'vote_count': data['vote_count'],
            'keywords': [keyword['name'] for keyword in data_kw['keywords']]
        }
    except Exception as e:
            print(f"Chyba pro film {film_id}: {e}", flush=True)
            return None
    

if os.path.exists('filmy_tmdb_metadata_progress.csv'):
    results_list = pd.read_csv('filmy_tmdb_metadata_progress.csv').to_dict('records')
else:
    results_list = []


print(f"Načteno {len(results_list)} už zpracovaných filmů")

for index, row in df.iterrows():
    if index < len(results_list):
        continue

    if pd.isna(row['tmdb_id']):
        results_list.append({
        'id': None,
        'title': row['title'],  # zachovej původní český název
        'original_title': None,
        'release_date': None,
        'runtime': None,
        'budget': None,
        'genres': None,
        'origin_country': None,
        'original_language': None,
        'production_companies': None,
        'production_company_countries': None,
        'production_countries': None,
        'spoken_languages': None,
        'vote_average': None,
        'vote_count': None,
        'keywords': None
        })
        continue
    print(f"{index}/{len(df)}: {row['title']}", flush=True)
    metadata = get_film_metadata(row['tmdb_id'])
    results_list.append(metadata)
  
    # ulož po každých 100 filmech
    if index % 100 == 0 and index > 0:
        pd.DataFrame(results_list).to_csv('filmy_tmdb_metadata_progress.csv', index=False)
        print(f"--- uloženo {index} filmů ---", flush=True)

# finální uložení
df_results = pd.DataFrame(results_list)
df_results.to_csv('filmy_tmdb_metadata.csv', index=False)

