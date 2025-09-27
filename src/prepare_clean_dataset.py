# prepare_clean_dataset.py

import pandas as pd
from pathlib import Path

# Paths
INPUT_CSV = Path("data/raw/googleplaystore.csv")  # your raw CSV
OUTPUT_CSV = Path("outputs/clean_dataset.csv")    # cleaned dataset output

# Ensure output directory exists
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# Load raw CSV
df = pd.read_csv(INPUT_CSV)

# Basic cleaning
# 1. Remove duplicate apps
df = df.drop_duplicates(subset='App')

# 2. Rename columns to standard names
rename_map = {
    'App': 'app_name',
    'Category': 'category',
    'Rating': 'rating',
    'Reviews': 'review_count',
    'Price': 'price_usd',
    'Last Updated': 'last_updated',
    'App Id': 'app_id'  # if exists
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# 3. Clean price column (remove $ and convert to float)
if 'price_usd' in df.columns:
    df['price_usd'] = df['price_usd'].replace('[\$,]', '', regex=True)
    df['price_usd'] = pd.to_numeric(df['price_usd'], errors='coerce').fillna(0.0)

# 4. Convert numeric columns safely
for col in ['rating', 'review_count']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 5. Optional: drop rows with missing critical info
df = df.dropna(subset=['app_name', 'category'])

# Save cleaned CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"Clean dataset saved to {OUTPUT_CSV}")
