from scrapy import signals
import datetime

class StatsReporter:
    def __init__(self):
        self.start_time = None

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        self.start_time = datetime.datetime.now()
        spider.logger.info("📈 StatsReporter iniciado.")

    def spider_closed(self, spider):
        finish_time = datetime.datetime.now()
        duration = (finish_time - self.start_time).total_seconds()
        stats = spider.crawler.stats.get_stats()

        items = stats.get("item_scraped_count", 0)
        retries = stats.get("retry/count", 0)
        code_429 = stats.get("downloader/response_status_count/429", 0)
        avg_time_per_item = duration / items if items else 0

        spider.logger.info("🟩 EXECUÇÃO FINALIZADA")
        spider.logger.info(f"⏱️ Tempo total: {duration:.2f}s")
        spider.logger.info(f"📦 Itens raspados: {items}")
        spider.logger.info(f"⚖️ Tempo médio por item: {avg_time_per_item:.2f}s")
        spider.logger.info(f"🔁 Requisições reprocessadas: {retries}")
        spider.logger.info(f"🛑 Respostas 429 recebidas: {code_429}")
