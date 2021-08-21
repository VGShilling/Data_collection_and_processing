# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparesrPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.scrapy_vacancies

    def process_item(self, item, spider):
        if spider.name == 'sjru':
            item['salary'] = self.process_salary_sj(item['salary'])
        elif spider.name == 'hhru':
            item['salary'] = self.process_salary_hh(item['salary'])

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):
        min_s = None
        max_s = None
        cur = None
        if salary is not None:
            salary_list = salary.replace("\xa0", "").split(" ")
            if len(salary_list) == 5:
                min_s = salary_list[1]
                max_s = salary_list[3]
                cur = salary_list[4]
            elif len(salary_list) == 3 and salary_list[0] == 'от':
                min_s = salary_list[1]
                cur = salary_list[2]
            elif len(salary_list) == 3 and salary_list[0] == 'до':
                max_s = salary_list[1]
                cur = salary_list[2]
        return {'min_salary': min_s, 'max_salary': max_s, 'currency': cur}

    def process_salary_sj(self, salary):
        min_s = None
        max_s = None
        cur = None
        if salary is not None:
            salary_list = salary.replace("\xa0", "").split(" ")
            if len(salary_list) == 4:
                min_s = salary_list[0]
                max_s = salary_list[1]
                cur = salary_list[-1]
            elif len(salary_list) < 4 and salary_list[0].isdigit():
                min_s = salary_list[0]
                cur = salary_list[-1]
            elif salary_list[0] == 'от':
                min_s = "".join(filter(str.isdigit, salary_list[2]))
                cur = "".join(filter(str.isalpha, salary_list[2]))
            elif salary_list[0] == 'до':
                max_s = "".join(filter(str.isdigit, salary_list[2]))
                cur = "".join(filter(str.isalpha, salary_list[2]))
        return {'min_salary': min_s, 'max_salary': max_s, 'currency': cur}
