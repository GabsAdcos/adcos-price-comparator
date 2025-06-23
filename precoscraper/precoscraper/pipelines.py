# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PrecoscraperPipeline:
    def process_item(self, item, spider):
        return item


import os
import pymongo
from dotenv import load_dotenv

class MongoPipeline:
    def open_spider(self, spider):
        load_dotenv()

        mongo_uri = os.getenv("MONGO_URI")
        mongo_db = os.getenv("MONGO_DB", "precos")
        mongo_collection = os.getenv("MONGO_COLLECTION", "produtos")



        self.client = pymongo.MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=10000,  # tempo para localizar servidor
                connectTimeoutMS=10000,          # tempo para conectar
                socketTimeoutMS=10000            # tempo de inatividade por socket
            )
        self.db = self.client["precos"]
        self.col = self.db["sallve"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        filtro = {"marca": item["marca"], "produto": item["produto"]}

        # atualiza apenas campos mutáveis (ex: preco, descricao, url)
        update = {
            "$set": {
                "descricao": item["descricao"],
                "preco": item["preco"],
                "url_produto": item["url_produto"],
                "categoria": item["categoria"],
            }
        }

        # mantém o mesmo _id (uuid) se já existe, ou insere novo
        existente = self.col.find_one(filtro)
        if existente:
            update["$set"]["id"] = existente["id"]
        else:
            update["$set"]["id"] = item["id"]

        self.col.update_one(filtro, update, upsert=True)
        return item

