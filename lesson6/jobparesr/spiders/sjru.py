import scrapy
from scrapy.http import HtmlResponse
from lesson6.jobparesr.items import JobparesrItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[contains(@class,'icMQ_ _6AfZ9')]/@href").extract()
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name_data = response.xpath("//h1/text()").extract_first()
        salary_data = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").extract()
        salary_data = ' '.join(salary_data)
        link_data = response.url
        site_data = 'superjob.ru'
        yield JobparesrItem(name=name_data, salary=salary_data, link=link_data, site=site_data)
