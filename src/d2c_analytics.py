import pandas as pd

def compute_cac_roas(df):
    """
    Compute CAC (Cost per Acquisition) and ROAS (Return on Ad Spend)
    Assumes df has columns: Spend, Conversions, Revenue
    """
    df = df.copy()
    df['CAC'] = df['Spend'] / df['Conversions'].replace(0, 1)
    df['ROAS'] = df['Revenue'] / df['Spend'].replace(0, 1)
    return df

def seo_opportunities(df):
    """
    Identify SEO categories with high potential
    Assumes df has columns: Category, SearchVolume, AvgPosition, ConversionRate
    """
    df = df.copy()
    # Score: higher search volume + higher conversion + lower average position
    df['SEO_Score'] = df['SearchVolume'] * df['ConversionRate'] / df['AvgPosition'].replace(0, 1)
    df = df.sort_values(by='SEO_Score', ascending=False)
    return df
