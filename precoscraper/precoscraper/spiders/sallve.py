import scrapy
import uuid
import re

class SallveSpider(scrapy.Spider):
    name = "sallve"
    allowed_domains = ["sallve.com.br"]
    start_urls = ["https://www.sallve.com.br/collections/loja?page=1"]

    def parse(self, response):
        produtos = response.css("product-card.product-card")

        if not produtos:
            self.logger.info("Nenhum produto encontrado. Fim da paginação.")
            return

        for card in produtos:
            href = card.css("a[data-tracking='product-card-title']::attr(href)").get()
            url_produto = response.urljoin(href) if href else None
            if url_produto:
                yield scrapy.Request(url_produto, callback=self.parse_produto)

        current_page = int(response.url.split("page=")[-1])
        next_page = current_page + 1
        next_url = f"https://www.sallve.com.br/collections/loja?page={next_page}"
        yield response.follow(next_url, callback=self.parse)

    def parse_produto(self, response):
        nome = response.css("h1.ProductName span#ProductNameTitle::text").get(default="").strip()
        volume = response.css("h1.ProductName span.ProductWeight::text").get(default="").strip()
        preco = response.css("p.ProductPrice strong.TotalPrice::text").get(default="").strip()
        descricao = response.css("div.TweetDescription p::text").get(default="").strip()

        categoria_site = "Loja Sallve"
        categoria_padrao = self.normalizar_categoria(categoria_site)

        yield {
            "id": str(uuid.uuid4()),
            "marca": "Sallve",
            "produto": nome,
            "descricao": descricao,
            "preco": preco,
            "url_produto": response.url,
            "categoria_original": categoria_site,
            "categoria": categoria_padrao,
            "volume": volume,
        }

    def extrair_volume(self, texto):
        texto = texto.lower().replace("\xa0", " ").replace("-", " ").strip()
        match = re.search(r"\b\d+\s?(ml|g|l)\b", texto)
        return match.group(0) if match else None

    def normalizar_categoria(self, raw):
        MAPEAMENTO = {
            "Loja Sallve": "Rosto",  # fallback
            "Rosto": "Rosto",
            "Corpo": "Corpo",
            "Tratamento": "Tratamento",
            "Hidratação": "Hidratação",
            "Limpeza": "Limpeza",
            "Esfoliação": "Limpeza",
            "Protetor solar": "Proteção Solar",
        }
        return MAPEAMENTO.get(raw.strip(), raw.strip())
