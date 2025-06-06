import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from scraper import run_scraping, ensure_files_exist

st.set_page_config(page_title="Comparador de Preços Adcos vs Principia", layout="wide")

DATA_FILE = "matched_prices.csv"
HISTORY_FILE = "matched_prices_history.csv"
KEYWORDS_FILE = "keywords.json"

# Garante que os arquivos existam
ensure_files_exist(DATA_FILE, HISTORY_FILE)

# Lista fixa de produtos Adcos
ADCOS_PRODUCTS = [
    {"name": "Adcos Derma Complex Vitamina C 20", "price": 299.00},
    {"name": "Adcos Retinol Concentrado", "price": 289.00},
    {"name": "Adcos Peeling Mandélico", "price": 199.00},
]

# Sidebar para configuração de palavras‑chave
st.sidebar.header("Configuração de Palavras‑Chave")

if not os.path.exists(KEYWORDS_FILE):
    default_keywords = {
        "Vitamina C": "https://www.principiaskin.com/products/serum-10-vitamina-c",
        "Retinol": "https://www.principiaskin.com/products/retinol-0-3",
        "Ácido Mandélico": "https://www.principiaskin.com/products/mandelico-10",
    }
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(default_keywords, f, ensure_ascii=False, indent=2)

with open(KEYWORDS_FILE, encoding="utf-8") as f:
    keywords_dict = json.load(f)

keywords_df = pd.DataFrame([
    {"keyword": k, "url": v} for k, v in keywords_dict.items()
])

edited_df = st.sidebar.data_editor(
    keywords_df,
    num_rows="dynamic",
    key="keywords_editor",
    use_container_width=True,
    hide_index=True,
)

if st.sidebar.button("Salvar Palavras‑Chave"):
    new_dict = {row["keyword"]: row["url"] for _, row in edited_df.iterrows() if row["keyword"] and row["url"]}
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_dict, f, ensure_ascii=False, indent=2)
    st.sidebar.success("Palavras‑chave salvas! Recarregue a página para usar as novas configurações.")

st.sidebar.markdown("---")

# Botão de scraping
if st.sidebar.button("Atualizar Preços (Scraping)"):
    with st.spinner("Executando scraping..."):
        run_scraping(ADCOS_PRODUCTS, keywords_dict, DATA_FILE, HISTORY_FILE)
    st.sidebar.success("Scraping concluído! Dados atualizados.")

# Conteúdo principal
st.title("Comparador de Preços: Adcos vs Principia")

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    st.subheader("Tabela de Preços Comparados (última execução)")
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.subheader("Comparação de Preços")
        bar_df = df.melt(id_vars=["adcos_product", "keyword"], value_vars=["adcos_price", "competitor_price"],
                         var_name="Fonte", value_name="Preço")
        bar_df["Fonte"] = bar_df["Fonte"].map({"adcos_price": "Adcos", "competitor_price": "Principia"})
        chart = (
            bar_df
            .set_index(["adcos_product", "Fonte"])["Preço"]
            .unstack()
            .plot(kind="bar", figsize=(10, 4), ylabel="Preço (R$)")
        )
        st.pyplot(chart.figure)

# Histórico
if os.path.exists(HISTORY_FILE):
    hist_df = pd.read_csv(HISTORY_FILE, parse_dates=["date"])
    if not hist_df.empty:
        st.subheader("Histórico de Variações de Preço")
        pivot = hist_df.pivot_table(index="date", columns="keyword", values="competitor_price")
        st.line_chart(pivot)
