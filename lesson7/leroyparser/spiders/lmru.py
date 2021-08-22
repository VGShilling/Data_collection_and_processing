import scrapy
from scrapy.http import HtmlResponse
from lesson7.leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath("//a[@data-qa='product-name']")
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]")
        if next_page:
            yield response.follow(next_page.attrib['href'], callback=self.parse)
        for link in ads_links:
            yield response.follow(link, callback=self.ads_parse)

    def ads_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//meta[@itemprop='price']/@content")
        loader.add_xpath('photos', "//picture/img[@alt='product image']/@src")
        loader.add_xpath('description', "//section[@id='nav-description']//p/text()")
        loader.add_xpath('specs', "//div[@class='def-list__group']/dt/text() | //div[@class='def-list__group']/dd/text()")

        yield loader.load_item()
