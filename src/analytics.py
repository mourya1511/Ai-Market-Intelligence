# src/analytics.py
import pandas as pd
import numpy as np
from scipy import stats
from joblib import Parallel, delayed

def category_summary(df):
    g = df.groupby('category').agg(
        apps=('app_name','nunique'),
        avg_rating=('rating','mean'),
        median_price=('price_usd','median'),
        total_reviews=('review_count','sum'),
    ).reset_index()
    g['avg_rating'] = g['avg_rating'].round(2)
    return g.sort_values('apps', ascending=False)

def detect_growth(df, date_col='last_updated', window_days=90):
    df = df.copy()
    cut = pd.Timestamp.now() - pd.Timedelta(days=window_days)
    recent = df[df[date_col] >= cut]
    recent_counts = recent.groupby('category').size().rename('recent_count')
    overall_counts = df.groupby('category').size().rename('total_count')
    stats = pd.concat([recent_counts, overall_counts], axis=1).fillna(0)
    stats['recent_ratio'] = (stats['recent_count'] / (stats['total_count']+1)).round(3)
    return stats.sort_values('recent_ratio', ascending=False).reset_index()

def significance_of_rating_diff(df, cat_a, cat_b):
    a = df[df['category']==cat_a]['rating'].dropna()
    b = df[df['category']==cat_b]['rating'].dropna()
    # parametric t-test
    t, p = stats.ttest_ind(a, b, equal_var=False, nan_policy='omit')
    return {'t': float(t), 'p': float(p), 'n_a': len(a), 'n_b': len(b)}

# Example usage:
# df = pd.read_csv('outputs/clean_combined_apps.csv')
# print(category_summary(df).head())
