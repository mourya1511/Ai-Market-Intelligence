# src/streamlit_app.py
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(layout='wide', page_title='AI Market Intel')
st.title("AI-Powered Market Intelligence")

# Check files
if not os.path.exists('outputs/insights_debug.json'):
    st.error("Insights file not found. Run insights_generator_debug.py first.")
    st.stop()

if not os.path.exists('outputs/clean_dataset.csv'):
    st.error("Clean dataset not found. Run prepare_clean_dataset.py first.")
    st.stop()

# Load files
with open('outputs/insights_debug.json', 'r', encoding='utf-8') as f:
    insights = json.load(f)['insights']

df = pd.read_csv('outputs/clean_dataset.csv')

# Sidebar
category = st.sidebar.selectbox("Choose category", options=sorted({i['category'] for i in insights}))

# Filter insights
selected = [i for i in insights if i['category'] == category]
if selected:
    ins = selected[0]
    st.header(f"Category: {ins['category']} — Confidence {ins['confidence']}")
    st.subheader("Metrics")
    st.json(ins['metrics'])
    st.subheader("LLM Recommendations")
    st.json(ins['llm'])
    st.subheader("Top apps (sample)")
    df_display = df[df['category'] == category].sort_values('review_count', ascending=False).head(10)
    df_display['review_count'] = df_display['review_count'].astype(int)
    df_display['rating'] = df_display['rating'].round(2)
    st.table(df_display[['app_name','rating','review_count','price_usd']])
else:
    st.write("No insights for selected category.")
