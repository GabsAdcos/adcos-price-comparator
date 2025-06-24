import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
# ⬇️ ajuste se necessário
client = MongoClient(mongo_uri)
db = client["precos"]
collection = db["sallve"]

# puxa tudo e converte em DataFrame
dados = list(collection.find({}, {"_id": 0}))  # remove _id
df = pd.DataFrame(dados)

# salva em CSV
df.to_csv("produtos_unificados.csv", index=False, encoding="utf-8-sig")
print("✅ Exportação concluída: produtos_unificados.csv")
