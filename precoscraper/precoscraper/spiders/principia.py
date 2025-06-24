import scrapy
import uuid
import re

class PrincipiaSpider(scrapy.Spider):
    name = "principia"
    allowed_domains = ["principiaskin.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls_vistos = set()

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.principiaskin.com/produtos/produtos-individuais?p=1",
            callback=self.parse,
            meta={"page": 1}
        )

    def parse(self, response):
        produtos = response.css("li.item.product.product-item")

        if not produtos:
            self.logger.info(f"🛑 Nenhum produto encontrado em {response.url}. Encerrando.")
            return

        produtos_novos = 0

        for card in produtos:
            url_produto = card.css("strong.product-item-name a::attr(href)").get()
            if url_produto in self.urls_vistos or not url_produto:
                continue

            self.urls_vistos.add(url_produto)
            produtos_novos += 1

            yield response.follow(url_produto, callback=self.parse_produto)

        if produtos_novos == 0:
            self.logger.info("🛑 Todos os produtos já foram raspados. Encerrando.")
            return

        next_page = response.meta["page"] + 1
        next_url = f"https://www.principiaskin.com/produtos/produtos-individuais?p={next_page}"
        self.logger.info(f"➡️ Avançando para página {next_page}")
        yield scrapy.Request(
            url=next_url,
            callback=self.parse,
            meta={"page": next_page}
        )

    def parse_produto(self, response):
        nome = response.css("h1.page-title span.base::text").get(default="").strip()
        preco = response.css("span.price-wrapper > span.price::text").get(default="").strip()

        # descrição
        descricoes = response.css('div.value[itemprop="description"] p span::text').getall()
        if not descricoes:
            descricoes = response.css('div.value[itemprop="description"] p::text').getall()
        descricao = " ".join([d.strip() for d in descricoes if d.strip()])

        volume = self.extrair_volume(nome + " " + descricao)

        # categoria do breadcrumb
        breadcrumb = response.css("ul.items li a::text").getall()
        categoria_site = breadcrumb[-1].strip() if breadcrumb else "Desconhecido"
        categoria_padrao = self.normalizar_categoria(categoria_site)

        yield {
            "id": str(uuid.uuid4()),
            "marca": "Principia",
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
            "Rosto": "Rosto",
            "Corpo": "Corpo",
            "Indicações": "Rosto",
            "Remover impurezas": "Limpeza",
            "Hidratar": "Hidratação",
            # outros mapeamentos conforme necessidade
        }
        return MAPEAMENTO.get(raw.strip(), raw.strip())
