import scrapy
import uuid

class AdcosSpider(scrapy.Spider):
    name = "adcos"
    allowed_domains = ["lojaadcos.com.br"]
    start_urls = [
        ("https://www.lojaadcos.com.br/tratamento-facial/produtos", "Tratamento Facial"),
        ("https://www.lojaadcos.com.br/tratamento-capilar/produtos", "Tratamento Capilar"),
        ("https://www.lojaadcos.com.br/tratamento-corporal/produtos", "Tratamento Corporal"),
    ]

    def start_requests(self):
        for url, categoria in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_listing, cb_kwargs={"categoria": categoria})

    def parse_listing(self, response, categoria):
        produtos = response.css("article.product-card")
        if not produtos:
            self.logger.info(f"Nenhum produto encontrado em {response.url}")
            return

        for produto in produtos:
            hrefs = produto.css("a::attr(href)").getall()
            href = next((h for h in hrefs if "/p?skuId=" in h and "secure" not in h), None)
            url_produto = response.urljoin(href) if href else None
            if url_produto:
                yield scrapy.Request(
                    url=url_produto,
                    callback=self.parse_produto,
                    cb_kwargs={"categoria": categoria}
                )

        # paginação
        next_page = response.css("a.action.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_listing, cb_kwargs={"categoria": categoria})


        # paginação
        next_page = response.css("a.action.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_listing)

    def parse_produto(self, response, categoria):
        nome = response.css("h1.product-heading__title::text").get(default="").strip()
        preco = response.css("div.aud-flex.aud-items-baseline > span.aud-text-xl::text").get(default="").strip()

        descricao = response.css('div[id$="product-info-match-anchor"] > div::text').get(default="").strip()
        volume = self.extrair_volume(nome)

        # breadcrumb
        breadcrumb = response.css("ul.breadcrumb__items li a::text").getall()
        categoria_site = breadcrumb[-1].strip() if breadcrumb else ""
        categoria_padrao = self.normalizar_categoria(categoria_site)

        yield {
            "id": str(uuid.uuid4()),
            "marca": "Adcos",
            "produto": nome,
            "descricao": descricao,
            "preco": preco,
            "url_produto": response.url,
            "categoria_original": categoria_site,
            "categoria": categoria_padrao,
            "volume": volume,
        }


    def normalizar_categoria(self, raw):
        MAPEAMENTO = {
            "Proteção Solar": "Protetor Solar",
            "Tonalizantes": "Tonalizante",
            "Pele Normal": "Rosto",
            "Tratamento Facial": "Rosto",
            "Tratamento Corporal": "Corpo",
            "Tratamento Capilar": "Cabelos",
        }
        return MAPEAMENTO.get(raw.strip(), raw.strip())


    def extrair_volume(self, texto):
        import re
        match = re.search(r"\b\d+\s?(ml|g|L)\b", texto.lower())
        return match.group(0) if match else None
