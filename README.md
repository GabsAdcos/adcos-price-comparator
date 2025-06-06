# Adcos vs Principia Price Comparator

Web app built with **Streamlit** that compares prices of Adcos products with similar items from Principia.

## Features

- Scrapes Principia product pages using rotating *User‑Agent* headers and random delays to avoid blocking.
- Fixed list of Adcos products with prices.
- Editable keyword mapping (via sidebar) links Adcos products to Principia URLs, stored in `keywords.json`.
- Saves latest matched prices and daily history to CSV files.
- Interactive table, bar chart, and line chart for price comparison and trends.
- Button to trigger scraping and update data.
- Ready for deployment on **Heroku** (`Procfile`, `requirements.txt`).

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploying to Heroku

1. Create a new Heroku app with the **Python** buildpack.
2. Push this repository:

```bash
git push heroku main
```

Heroku will install the dependencies and launch the Streamlit server automatically.
