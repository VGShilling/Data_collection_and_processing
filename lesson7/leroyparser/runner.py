from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson7.leroyparser.spiders.lmru import LmruSpider
from lesson7.leroyparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    # answer = input('')
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LmruSpider, search='стул')

    process.start()
