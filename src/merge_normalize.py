# src/merge_normalize.py
import pandas as pd
import json
from pathlib import Path

def load_google_play(path='outputs/clean_google_play.csv'):
    return pd.read_csv(path)

def load_appstore_cache(cache_dir='data/cache'):
    import os, json
    rows = []
    for fn in Path(cache_dir).glob('*.json'):
        j = json.loads(fn.read_text())
        # transform according to actual RapidAPI response shape
        # example mapping below:
        try:
            info = j.get('results', [])[0]
        except:
            info = j
        if not info: continue
        row = {
            'platform':'ios',
            'app_id': info.get('trackId') or info.get('id'),
            'app_name': info.get('trackName') or info.get('name'),
            'publisher': info.get('sellerName') or info.get('seller'),
            'category': info.get('primaryGenreName') or info.get('genre'),
            'rating': info.get('averageUserRating'),
            'review_count': info.get('userRatingCount'),
            'price_usd': info.get('price'),
            'last_updated': info.get('currentVersionReleaseDate'),
            'description': info.get('description'),
            'raw': info
        }
        rows.append(row)
    return pd.DataFrame(rows)

def unify(gp_df, ios_df):
    gp_df = gp_df.copy()
    gp_df['platform'] = 'android'

    # List of canonical columns
    cols = ['platform','app_name','publisher','category','rating','review_count','price_usd','last_updated','description']

    # Ensure both DataFrames have all columns
    for df in [gp_df, ios_df]:
        for c in cols:
            if c not in df.columns:
                df[c] = ''

    # Concatenate
    combined = pd.concat([gp_df[cols].fillna(''), ios_df[cols].fillna('')], ignore_index=True, sort=False)

    # Normalize
    combined['category'] = combined['category'].astype(str).str.lower().str.strip()
    combined['rating'] = pd.to_numeric(combined['rating'], errors='coerce')
    combined['review_count'] = pd.to_numeric(combined['review_count'], errors='coerce').fillna(0).astype(int)
    combined['price_usd'] = pd.to_numeric(combined['price_usd'], errors='coerce').fillna(0.0)
    combined['last_updated'] = pd.to_datetime(combined['last_updated'], errors='coerce')

    combined.to_csv('outputs/clean_combined_apps.csv', index=False)
    return combined


def main():
    gp = load_google_play()
    ios = load_appstore_cache()
    combined = unify(gp, ios)
    print("Combined shape", combined.shape)
    return combined

if __name__=='__main__':
    main()