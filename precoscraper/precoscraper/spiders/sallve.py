import scrapy
import uuid

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
            nome = card.css("h3.product-card__infos-title a::text").get(default="").strip()
            descricao = card.css("p.product-card__infos-fineline::text").get(default="").strip()
            preco = card.css("p.fullprice__current::text").get(default="").strip()
            href = card.css("a[data-tracking='product-card-title']::attr(href)").get()
            url_produto = response.urljoin(href) if href else None

            yield {
                "id": str(uuid.uuid4()),
                "marca": "Sallve",
                "produto": nome,
                "descricao": descricao,
                "preco": preco,
                "url_produto": url_produto,
                "categoria": "Loja Sallve", 
            }

        # próxima página
        current_page = int(response.url.split("page=")[-1])
        next_page = current_page + 1
        next_url = f"https://www.sallve.com.br/collections/loja?page={next_page}"
        yield response.follow(next_url, callback=self.parse)
