import random
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import os

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/126.0",
]
def ensure_files_exist(data_file, history_file):
    """
    Cria arquivos CSV vazios com cabeçalhos, caso ainda não existam.
    """
    if not os.path.exists(data_file):
        pd.DataFrame(columns=["adcos_product","adcos_price","competitor_product","competitor_price","keyword"]).to_csv(data_file, index=False)
    if not os.path.exists(history_file):
        pd.DataFrame(columns=["date","adcos_product","competitor_product","competitor_price","keyword"]).to_csv(history_file, index=False)


def random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def parse_price(text):
    match = re.search(r"R\$[\s\xa0]?([\d.,]+)", text)
    if match:
        number = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(number)
        except ValueError:
            return None
    return None

def get_competitor_price(url, retries=3):
    for _ in range(retries):
        try:
            resp = requests.get(url, headers=random_headers(), timeout=10)
            if resp.status_code != 200:
                time.sleep(random.uniform(1, 3))
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            selectors = [
                '[data-product-price]',
                '.price-item--regular',
                '.product__price',
                '.product-price',
                '.price',
                'meta[itemprop="price"]',
            ]
            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    price = parse_price(el.get_text(strip=True) if el.name != "meta" else el.get("content", ""))
                    if price:
                        return price

            for text in soup.stripped_strings:
                price = parse_price(text)
                if price:
                    return price
        except Exception:
            pass
        time.sleep(random.uniform(1, 3))
    return None

def run_scraping(adcos_products, keywords_dict, data_file="matched_prices.csv", history_file="matched_prices_history.csv"):
    rows = []
    history_rows = []
    today = datetime.today().date()

    for product in adcos_products:
        adcos_name = product["name"]
        adcos_price = product["price"]
        matched_keyword = None
        competitor_url = None

        for kw, url in keywords_dict.items():
            if kw.lower() in adcos_name.lower():
                matched_keyword = kw
                competitor_url = url
                break

        if not matched_keyword:
            continue

        time.sleep(random.uniform(2, 5))

        competitor_price = get_competitor_price(competitor_url)

        rows.append({
            "adcos_product": adcos_name,
            "adcos_price": adcos_price,
            "competitor_product": competitor_url,
            "competitor_price": competitor_price,
            "keyword": matched_keyword,
        })

        history_rows.append({
            "date": today,
            "adcos_product": adcos_name,
            "competitor_product": competitor_url,
            "competitor_price": competitor_price,
            "keyword": matched_keyword,
        })

    df = pd.DataFrame(rows)
    df.to_csv(data_file, index=False)
      if os.path.exists(history_file):
        try:
            hist_df = pd.read_csv(history_file)
        except pd.errors.EmptyDataError:
            hist_df = pd.DataFrame()
                hist_df = pd.concat([hist_df, pd.DataFrame(history_rows)], ignore_index=True)
    else:
        hist_df = pd.DataFrame(history_rows)
    hist_df.to_csv(history_file, index=False)

