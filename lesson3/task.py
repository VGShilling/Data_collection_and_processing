from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
from pymongo import MongoClient


def vacancy_parsing(position):
    num_of_pages = input('Введите количество страниц для анализа: \n')
    page = 0
    vacancies = []

    # https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=python&page=1
    url = 'https://hh.ru'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    params = {'area': '1',
              'fromSearchLine': 'true',
              'st': 'searchVacancy',
              'text': position,
              'page': str(page)}

    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancy_list = soup.find_all('div', {'class': 'vacancy-serp-item'})
    print()
    while len(vacancy_list) > 0:
        for vacancy in vacancy_list:
            vacancy_data = {}
            vacancy_info = vacancy.find('a', {'class': 'bloko-link'})
            vacancy_data['_id'] = vacancy_info.get('href').split("/")[4].split("?")[0]
            vacancy_data['name'] = vacancy_info.getText()
            vacancy_salary_info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['salary_currency'] = min_max_salary(
                vacancy_salary_info)
            vacancy_data['link'] = vacancy_info.get('href')
            vacancy_data['url'] = url

            vacancies.append(vacancy_data)

        if page + 1 == int(num_of_pages):
            break

        page += 1
        params['page'] = str(page)

        response = requests.get(url + '/search/vacancy', params=params, headers=headers)
        soup = bs(response.text, 'html.parser')
        vacancy_list = soup.find_all('div', {'class': 'vacancy-serp-item'})
    return vacancies


def min_max_salary(salary_info):
    min_salary = None
    max_salary = None
    currency = None
    if salary_info is not None:
        salary_info_list = salary_info.getText().replace("\u202f", "").split(" ")
        if salary_info.getText()[0].isdigit():
            min_salary = int(salary_info_list[0])
            max_salary = int(salary_info_list[2])
            currency = salary_info_list[3]
        elif salary_info.getText()[0] == 'о':
            min_salary = int(salary_info_list[1])
            currency = salary_info_list[2]
        elif salary_info.getText()[0] == 'д':
            max_salary = int(salary_info_list[1])
            currency = salary_info_list[2]

    return min_salary, max_salary, currency


def data_to_new_db(data):
    client = MongoClient('127.0.0.1', 27017)
    if client['vacancies'].hh_ru:
        client['vacancies'].hh_ru.drop()
    db = client['vacancies']
    collection = db.hh_ru

    collection.insert_many(data)
    return collection


def insert_in_db(data, db):
    n = 0
    for el in data:
        if db.find_one({'_id': el['_id']}) is None:
            db.insert_one(el)
            n += 1
    print(f'------Внесено {n} новых вакансий------')
    return db


def search_by_salary(db):
    salary_value = int(input('Введите значение заработной платы в рублях: \n'))
    result = db.find({'$or': [{'$and': [{'$or': [{'salary_min': {'$gt': salary_value}},
                                                 {'salary_max': {'$gt': salary_value}}]},
                                        {'salary_currency': 'руб.'}]},
                              {'$and': [{'$or': [{'salary_min': {'$gt': (salary_value / 74)}},
                                                 {'salary_max': {'$gt': (salary_value / 74)}}]},
                                        {'salary_currency': 'USD'}]}]},
                     {'name': 1, 'salary_min': 1, 'salary_max': 1, 'salary_currency': 1, '_id': 0})
    for el in result:
        pprint(el)
    pass


search_position = input('Введите должность для поиска вакансий: \n')
parsed_vacancies = vacancy_parsing(search_position)
action = '1'
db_created = 0
while action in ['1', '2', '3']:
    print('______________________________________________________________________________________\n'
          'Выберете необходимое действие: \n'
          '1 - Запись собранных вакансий в новую БД \n'
          '2 - Поиск в БД и вывод на экран вакансий с заработной платой больше введённой суммы \n'
          '3 - Поиск новых вакансий на hh.ru и добавление в БД \n'
          '0 - Выход из программы')
    action = input(':')
    print('______________________________________________________________________________________\n')
    if action == '1':  # 1. Запись собранных вакансий в БД
        if db_created == 1:
            rewrite = input('------БД уже заполнена данными, перезаписать (y/n)------')
            if rewrite == 'y':
                hh_ru = data_to_new_db(parsed_vacancies)
                print(f'------В БД внесено {len(parsed_vacancies)} записей------')
        else:
            hh_ru = data_to_new_db(parsed_vacancies)
            print(f'------В БД внесено {len(parsed_vacancies)} записей------')
        db_created = 1
    elif action == '2':  # 2. Поиск и вывод на экран вакансий с заработной платой больше введённой суммы
        if db_created == 1:
            search_by_salary(hh_ru)
        else:
            print('------Поиск не возможен. БД отсутствует------')
    elif action == '3':  # 3. Добавление в БД только новых вакансий
        if db_created == 1:
            parsed_vacancies = vacancy_parsing(search_position)
            hh_ru = insert_in_db(parsed_vacancies, hh_ru)
        else:
            print('------Добавление вакансий не возможно. БД отсутствует------')
