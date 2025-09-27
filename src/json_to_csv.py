# src/json_to_csv.py
import json
import pandas as pd
from pathlib import Path

INPUT_FILE = Path("outputs/all_apps.json")
OUTPUT_FILE = Path("outputs/clean_dataset.csv")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"{INPUT_FILE} not found. Run appstore_fetch.py first.")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    all_apps = json.load(f)

# Flatten JSON into a list of dictionaries
rows = []
for app_id, data in all_apps.items():
    app_data = data.get("data", {})  # adjust if the JSON structure differs
    row = {
    "app_id": app_id,
    "app_name": app_data.get("trackName") or app_data.get("name"),
    "category": app_data.get("primaryGenreName"),
    "rating": app_data.get("averageUserRating"),
    "review_count": app_data.get("userRatingCount"),
    "price_usd": app_data.get("price"),
    "last_updated": app_data.get("currentVersionReleaseDate"),
}

    rows.append(row)

df = pd.DataFrame(rows)

# Save CSV
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved clean dataset to {OUTPUT_FILE}")
