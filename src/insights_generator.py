
import json
import os
from pathlib import Path
import pandas as pd

# Third-party imports first
import openai

from confidence import compute_confidence, cohen_d
from analytics import category_summary, detect_growth, significance_of_rating_diff

# Load API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")

# Set API key
openai.api_key = OPENAI_API_KEY

OUTPUT = Path("outputs/insights_debug.json")


def llm_summarize(prompt: str, model: str = "gpt-4o-mini") -> dict:
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI market analyst."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.2
        )
        text = response.choices[0].message.content
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
    except Exception as e:
        return {"error": str(e)}


def generate_insights(df: pd.DataFrame):
    print("✅ Loaded dataset with columns:", df.columns.tolist())
    print("Categories count:\n", df["category"].value_counts())

    insights = []
    cat_summary = category_summary(df).head(10)
    print("Category summary (top 10):\n", cat_summary)

    for _, row in cat_summary.iterrows():
        cat = row["category"]
        cat_ratings = df[df["category"] == cat]["rating"].dropna()
        global_ratings = df["rating"].dropna()

        print(f"\nProcessing category: {cat}")
        print(f"Number of apps in category: {len(cat_ratings)}")

        if len(cat_ratings) < 2:
            print(f"Skipping category {cat} due to too few ratings.")
            continue

        d = cohen_d(cat_ratings.values, global_ratings.values)
        sig = significance_of_rating_diff(df, cat, df["category"].mode()[0])

        last_update = pd.to_datetime(df[df["category"] == cat]["last_updated"].dropna().max()) \
            if df[df["category"] == cat]["last_updated"].notna().any() else pd.Timestamp.now()
        freshness_days = (pd.Timestamp.now() - last_update).days

        conf = compute_confidence(
            n=len(cat_ratings),
            p_value=sig.get("p", 0.05),
            effect_size=d,
            freshness_days=freshness_days,
        )

        prompt = f"""
        Summarize top actionables for category "{cat}" based on stats:
        apps={int(row.get('apps',0))}, avg_rating={row.get('avg_rating',0)}, 
        median_price={row.get('median_price',0)}, total_reviews={row.get('total_reviews',0)}.
        Return JSON keys: recommendations, hypothesis, product_idea.\
        """
        llm_json = llm_summarize(prompt)

         # Then append to insights
        insights.append({
        "insight_id": f"cat_{cat}",
        "type": "category_profile",
        "category": cat,
        "metrics": row.to_dict(),
        "llm": llm_json,
        "confidence": conf,
    })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"generated_at": str(pd.Timestamp.now()), "insights": insights}, f, indent=2)

    print(f"\n✅ Saved debug insights to {OUTPUT}")
    print(f"Total insights generated: {len(insights)}")
    return insights


if __name__ == "__main__":
    csv_path = "outputs/clean_dataset.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found!")

    df = pd.read_csv(csv_path)
    generate_insights(df)
