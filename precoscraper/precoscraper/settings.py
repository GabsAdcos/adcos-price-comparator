# Scrapy settings for precoscraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "precoscraper"

SPIDER_MODULES = ["precoscraper.spiders"]
NEWSPIDER_MODULE = "precoscraper.spiders"

ADDONS = {}

EXTENSIONS = {
    'precoscraper.extensions.StatsReporter': 500,
}

# Obedece robots.txt? (não neste caso, pois precisamos de liberdade total)
ROBOTSTXT_OBEY = False

# 🌐 User-Agent rotativo (para evitar bloqueios simples)
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
}

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# ⏱️ Controla a taxa de requisições para não tomar 429
DOWNLOAD_DELAY = 3
CONCURRENT_REQUESTS_PER_DOMAIN = 1
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 5
AUTOTHROTTLE_DEBUG = False

# 🔄 Habilita retry para erros como 429 ou 500 temporários
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

# 🧾 Exportações com encoding correto
FEED_EXPORT_ENCODING = "utf-8"

# 🚫 Desativa cookies (a menos que queira rastrear sessão)
COOKIES_ENABLED = False
ITEM_PIPELINES = {
    'precoscraper.pipelines.MongoPipeline': 300,
}

# 🧠 Evita flood acidental
LOG_LEVEL = "INFO"
