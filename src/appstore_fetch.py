# src/appstore_fetch.py
import requests
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "apple-app-store-scraper.p.rapidapi.com"

if not RAPIDAPI_KEY:
    raise EnvironmentError("RAPIDAPI_KEY not found in environment variables. Set it in your .env file.")

HEADERS = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Retry on exceptions like HTTPError or network failures
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=20),
    stop=stop_after_attempt(6),
    retry=retry_if_exception_type(Exception),
)
def fetch_app_by_id(app_id: str) -> dict:
    """
    Fetch app details from the RapidAPI Apple App Store Scraper.
    Raises Exception on HTTP errors.
    """
    url = f"https://{RAPIDAPI_HOST}/v1/appstore"
    params = {"appid": app_id, "country": "us"}

    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)

    if resp.status_code == 403:
        raise PermissionError(f"API key not subscribed for this API. Got 403 for app {app_id}")
    if resp.status_code == 429:
        raise Exception(f"Rate limited (429) for app {app_id}")
    resp.raise_for_status()

    return resp.json()


def cached_fetch(app_id: str) -> dict:
    """
    Fetch app data, using cache if available.
    """
    cache_file = CACHE_DIR / f"{app_id}.json"
    if cache_file.exists() and cache_file.stat().st_size > 0:
        return json.loads(cache_file.read_text())

    data = fetch_app_by_id(app_id)
    cache_file.write_text(json.dumps(data))
    time.sleep(0.25)  # polite pacing
    return data


def bulk_fetch(app_ids: list[str]) -> dict:
    """
    Fetch multiple apps and return a dictionary of {app_id: data}.
    """
    results = {}
    for app_id in app_ids:
        try:
            data = cached_fetch(app_id)
            results[app_id] = data
            print(f"✅ Fetched app {app_id}")
        except Exception as e:
            print(f"❌ Failed to fetch {app_id}: {e}")
    return results


if __name__ == "__main__":
    # Example usage: Netflix & Spotify app IDs
    example_ids = ["284910350", "544007664"]  
    data = bulk_fetch(example_ids)

    # Save all results to a combined JSON for later CSV conversion
    OUTPUT_FILE = Path("outputs/all_apps.json")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ All app data saved to {OUTPUT_FILE}")
