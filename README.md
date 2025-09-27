# AI-Powered Market Intelligence Assignment

**Candidate:** Rajat Gupta  
**Position:** Applied AI Engineer  

## Overview

This repository contains my submission for the AI-Powered Market Intelligence assignment at Kasparro. The project takes app data from various sources, cleans it, normalizes it, generates insights using LLMs, and provides actionable outputs for decision-making. 

There is also an optional Phase 5 extension for D2C funnel and SEO analytics, along with AI-generated creative outputs.

## Repository Structure

ai-market-intelligence/  
├─ data/ # Raw and processed datasets  
├─ src/ # Python scripts (data pipelines, insights, report, Streamlit)  
├─ outputs/ # Cleaned datasets, JSON insights, reports  
├─ requirements.txt  
├─ README.md  
└─ .gitignore  

## Key Deliverables

- **Clean Combined Dataset:** `outputs/clean_combined_apps.csv`  
- **Insights JSON:** `outputs/insights.json` (with confidence scores and recommendations)  
- **Executive Report:** `outputs/report.pdf` / `outputs/report.md`  
- **Query Interface:** Streamlit app to explore insights (`src/streamlit_app.py`)  
- **Phase 5 (Optional):** D2C funnel and SEO insights plus 2 to 3 AI-generated outputs  

## Setup & Run

1. Clone the repo:  
```bash
git clone https://github.com/<USERNAME>/ai-market-intelligence.git
cd ai-market-intelligence

pip install -r requirements.txt
OPENAI_API_KEY=your_openai_api_key
RAPIDAPI_KEY=your_rapidapi_key
python src/kaggle_ingest.py
python src/appstore_fetch.py
python src/merge_normalize.py
python src/insights_generator.py
python src/report_generator.py
streamlit run src/streamlit_app.py
```  
