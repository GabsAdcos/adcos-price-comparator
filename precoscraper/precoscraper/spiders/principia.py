import scrapy
import uuid

class PrincipiaSpider(scrapy.Spider):
    name = "principia"
    allowed_domains = ["principiaskin.com"]
    start_urls = [
        "https://www.principiaskin.com/produtos/produtos-individuais"
    ]

    def parse(self, response):
        produtos = response.css("li.item.product.product-item")

        if not produtos:
            self.logger.info("Nenhum produto encontrado.")
            return

        for card in produtos:
            nome = card.css("strong.product-item-name a::text").get(default="").strip()
            descricao = card.css("div.product.description.product-item-description p span::text").getall()
            descricao = " ".join([d.strip() for d in descricao if d.strip()])
            preco = card.css("span.price::text").get(default="").strip()
            url_produto = card.css("strong.product-item-name a::attr(href)").get()

            yield {
                "id": str(uuid.uuid4()),
                "marca": "Principia",
                "produto": nome,
                "descricao": descricao,
                "preco": preco,
                "url_produto": url_produto,
                "categoria": "Produtos Individuais"
            }
