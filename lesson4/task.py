from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient


def non_breaking_space_remover(string):
    result = list()
    for s in string:
        result.append(s.replace("\xa0", " "))
    return result


def data_to_db(data):
    client = MongoClient('127.0.0.1', 27017)
    if client['news'].yandex:
        client['news'].yandex.drop()
    db = client['news']
    collection = db.yandex

    collection.insert_many(data)
    return collection


url = 'https://yandex.ru/news'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

news = dom.xpath("//div[contains(@class, 'mg-top-rubric')][1]//article")
news_list = []

for news_item in news:
    news_data = {}
    news_data['source'] = news_item.xpath(".//a[@class='mg-card__source-link']/text()")
    news_data['name'] = non_breaking_space_remover(news_item.xpath(".//h2/text()"))
    news_data['link'] = news_item.xpath(".//h2/../@href")
    news_data['time'] = news_item.xpath(".//span[@class='mg-card-source__time']/text()")
    # Дату к новости в коде HTML не нашел.

    news_list.append(news_data)

yandex = data_to_db(news_list)

for el in yandex.find({}):
    pprint(el)
