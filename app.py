import streamlit as st
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import numpy as np
import plotly.express as px
import re

st.set_page_config(page_title="Comparador Adcos x Sallve x Principia", layout="wide")

# ----- 1. CONEXÃO COM MONGO ATLAS -----
load_dotenv()
try:
    client = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    col = db[os.getenv("MONGO_COLLECTION")]
    produtos = list(col.find())
    st.success(f"Conectado ao MongoDB! {len(produtos)} produto(s) encontrados.")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao MongoDB: {e}")
    produtos = []

if not produtos:
    st.stop()

# ----- 2. DATAFRAME -----
df = pd.DataFrame(produtos)
df = df.dropna(subset=["descricao"])
df["descricao"] = df["descricao"].fillna("")
df["preco"] = df["preco"].str.replace("R$", "").str.replace(",", ".").astype(float)

# ----- 2.1 Extrair numérico de volume para comparar ml/g -----
def extrair_volume(valor):
    if pd.isna(valor): return np.nan
    match = re.search(r"(\d+(?:[\.,]\d+)?)", str(valor))
    if match:
        vol = match.group(1).replace(",", ".")
        return float(vol)
    return np.nan

for marca in ["Adcos", "Sallve", "Principia"]:
    df[f"Volume {marca} Num"] = df[f"volume"].apply(extrair_volume)

df["volume"] = df["volume"].fillna("")

# ----- 3. SEPARAÇÃO POR MARCA -----
adcos = df[df["marca"] == "Adcos"].reset_index(drop=True)
sallve = df[df["marca"] == "Sallve"].reset_index(drop=True)
principia = df[df["marca"] == "Principia"].reset_index(drop=True)

# ----- 4. SIMILARIDADE DE DESCRIÇÃO -----
vectorizer = TfidfVectorizer().fit(
    adcos["descricao"].tolist() +
    sallve["descricao"].tolist() +
    principia["descricao"].tolist()
)

vec_adcos = vectorizer.transform(adcos["descricao"])
vec_sallve = vectorizer.transform(sallve["descricao"])
vec_principia = vectorizer.transform(principia["descricao"])

sim_adcos_sallve = cosine_similarity(vec_adcos, vec_sallve)
sim_adcos_principia = cosine_similarity(vec_adcos, vec_principia)

# ----- 5. MATCHING 1:1:1 -----
matches = []
for i in range(len(adcos)):
    idx_sallve = np.argmax(sim_adcos_sallve[i])
    idx_principia = np.argmax(sim_adcos_principia[i])
    matches.append({
        "Produto Adcos": adcos.loc[i, "produto"],
        "Categoria": adcos.loc[i, "categoria"],
        "Volume Adcos": adcos.loc[i, "volume"],
        "Preço Adcos": adcos.loc[i, "preco"],
        "Produto Sallve": sallve.loc[idx_sallve, "produto"],
        "Volume Sallve": sallve.loc[idx_sallve, "volume"],
        "Preço Sallve": sallve.loc[idx_sallve, "preco"],
        "Produto Principia": principia.loc[idx_principia, "produto"],
        "Volume Principia": principia.loc[idx_principia, "volume"],
        "Preço Principia": principia.loc[idx_principia, "preco"],
        "Sim. Sallve": round(sim_adcos_sallve[i][idx_sallve], 3),
        "Sim. Principia": round(sim_adcos_principia[i][idx_principia], 3),
    })

df_matches = pd.DataFrame(matches)

# Cálculo de preço por ml/g
for marca in ["Adcos", "Sallve", "Principia"]:
    df_matches[f"Preço por ml {marca}"] = df_matches[f"Preço {marca}"].astype(float) / df_matches[f"Volume {marca}"].apply(extrair_volume)

# ----- 6. LAYOUT COM TABS E FILTROS -----
st.title("🧴 Comparador de Produtos - Adcos vs Sallve vs Principia")

with st.expander("🔍 Filtros Avançados", expanded=True):
    min_score_sallve = st.slider("Similaridade mínima com Sallve", 0.0, 1.0, 0.2, 0.01)
    min_score_principia = st.slider("Similaridade mínima com Principia", 0.0, 1.0, 0.2, 0.01)
    categorias = df_matches["Categoria"].dropna().unique().tolist()
    selected_categorias = st.multiselect("Filtrar por categoria", categorias, default=categorias)

# Aplicar filtros
df_filtered = df_matches[
    (df_matches["Sim. Sallve"] >= min_score_sallve) &
    (df_matches["Sim. Principia"] >= min_score_principia) &
    (df_matches["Categoria"].isin(selected_categorias))
]

# Botão para baixar CSV
st.download_button("⬇️ Baixar CSV com os matches", data=df_filtered.to_csv(index=False), file_name="matches.csv", mime="text/csv")

# Tabs para exibição
abas = st.tabs([
    "📋 Tabela Comparativa",
    "📊 Gráfico de Preços",
    "📈 Dispersão Preço vs Similaridade",
    "⚖️ Comparação de Volume",
    "💰 Preço por ml/g",
    "🧠 Insights (Clustering)"
])

with abas[0]:
    st.dataframe(df_filtered, use_container_width=True)

with abas[1]:
    df_long = df_filtered.melt(
        id_vars=["Produto Adcos"],
        value_vars=["Preço Adcos", "Preço Sallve", "Preço Principia"],
        var_name="Marca",
        value_name="Preço"
    )
    fig = px.bar(df_long, x="Produto Adcos", y="Preço", color="Marca", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

with abas[2]:
    df_sim = df_filtered[["Produto Adcos", "Preço Adcos", "Sim. Sallve", "Sim. Principia"]].copy()
    df_sim = df_sim.melt(id_vars=["Produto Adcos", "Preço Adcos"], var_name="Similaridade Com", value_name="Score")
    fig2 = px.scatter(df_sim, x="Score", y="Preço Adcos", color="Similaridade Com", hover_name="Produto Adcos")
    st.plotly_chart(fig2, use_container_width=True)

with abas[3]:
    df_volume = df_filtered[[
        "Produto Adcos", "Volume Adcos", "Volume Sallve", "Volume Principia"
    ]].copy()
    df_volume = df_volume.dropna().melt(id_vars=["Produto Adcos"], var_name="Marca", value_name="Volume")
    fig3 = px.bar(df_volume, x="Produto Adcos", y="Volume", color="Marca", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

with abas[4]:
    df_ppml = df_filtered[[
        "Produto Adcos", "Preço por ml Adcos", "Preço por ml Sallve", "Preço por ml Principia"
    ]].dropna().melt(id_vars=["Produto Adcos"], var_name="Marca", value_name="Preço por ml")
    fig4 = px.bar(df_ppml, x="Produto Adcos", y="Preço por ml", color="Marca", barmode="group")
    st.plotly_chart(fig4, use_container_width=True)

with abas[5]:
    # Clustering com preço e similaridade
    df_cluster = df_filtered[["Preço Adcos", "Sim. Sallve", "Sim. Principia"]].dropna()
    kmeans = KMeans(n_clusters=3, random_state=0).fit(df_cluster)
    df_filtered["Cluster"] = kmeans.labels_
    fig5 = px.scatter_3d(df_filtered, x="Preço Adcos", y="Sim. Sallve", z="Sim. Principia",
                         color="Cluster", hover_name="Produto Adcos", title="Cluster de Produtos")
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("Produtos agrupados com base em preço e similaridade textual.")
