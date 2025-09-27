# src/kaggle_ingest.py
import pandas as pd
import numpy as np
import re
from pathlib import Path

def parse_installs(x):
    if pd.isna(x): return np.nan
    x = str(x).strip().lower()
    x = x.replace('+','').replace(',','')
    try:
        return int(re.sub(r'[^\d]', '', x))
    except:
        return np.nan

def parse_price(x):
    if pd.isna(x): return 0.0
    x = str(x).strip().replace('$','').replace('₹','').replace(',','')
    try:
        # some are 'Free'
        if x.lower() in ('free','0'): return 0.0
        return float(re.sub(r'[^\d.]','', x))
    except:
        return 0.0

def parse_size(x):
    # like '12M', 'Varies with device'
    if pd.isna(x): return np.nan
    x = str(x).strip()
    if x.lower().startswith('varies'): return np.nan
    try:
        if x.endswith('M'):
            return float(x[:-1]) * 1024*1024
        if x.endswith('k'):
            return float(x[:-1]) * 1024
        if x.endswith('G'):
            return float(x[:-1]) * 1024*1024*1024
        return float(re.sub(r'[^\d.]','', x))
    except:
        return np.nan

def standardize(df):
    df = df.copy()
    # common column renames — adapt to actual CSV columns
    col_map = {
        'App':'app_name',
        'Category':'category',
        'Rating':'rating',
        'Reviews':'review_count',
        'Size':'size_bytes',
        'Installs':'installs',
        'Type':'type',
        'Price':'price',
        'Last Updated':'last_updated',
        'Content Rating':'content_rating',
        'Genres':'genres'
    }
    df.rename(columns={c:v for c,v in col_map.items() if c in df.columns}, inplace=True)
    if 'installs' in df.columns:
        df['installs'] = df['installs'].apply(parse_installs)
    if 'price' in df.columns:
        df['price_usd'] = df['price'].apply(parse_price)
    if 'size_bytes' in df.columns:
        df['size_bytes'] = df['size_bytes'].apply(parse_size)
    if 'last_updated' in df.columns:
        df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
    # dedupe by (app_name, category) keeping highest reviews
    if 'app_name' in df.columns and 'review_count' in df.columns:
        df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce').fillna(0).astype(int)
        df.sort_values('review_count', ascending=False, inplace=True)
        df = df.drop_duplicates(subset=['app_name','category'], keep='first')
    # basic normalization
    df['app_name'] = df['app_name'].astype(str).str.strip()
    df['category'] = df['category'].astype(str).str.lower()
    return df

def main(infile='data/raw/googleplaystore.csv', outfile='outputs/clean_google_play.csv'):
    Path('outputs').mkdir(exist_ok=True)
    df = pd.read_csv(infile)
    df_clean = standardize(df)
    df_clean.to_csv(outfile, index=False)
    print("Saved:", outfile)
    return df_clean

if __name__=='__main__':
    main()
