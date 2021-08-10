from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import pandas as pd


def min_max_salary(salary_info):
    min_salary = None
    max_salary = None
    currency = None
    if salary_info is not None:
        salary_info_list = salary_info.getText().replace("\u202f", "").split(" ")
        if salary_info.getText()[0].isdigit():
            min_salary = salary_info_list[0]
            max_salary = salary_info_list[2]
            currency = salary_info_list[3]
        elif salary_info.getText()[0] == 'о':
            min_salary = salary_info_list[1]
            currency = salary_info_list[2]
        elif salary_info.getText()[0] == 'д':
            max_salary = salary_info_list[1]
            currency = salary_info_list[2]

    return min_salary, max_salary, currency


position = input('Введите должность: \n')
num_of_pages = input('Введите количество страниц для анализа: \n')
page = 0
vacancies = []

# https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=python&page=1
url = 'https://hh.ru'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
params = {'area': '1',
          'fromSearchLine': 'true',
          'st': 'searchVacancy',
          'text': position,
          'page': str(page)}

response = requests.get(url+'/search/vacancy', params=params, headers=headers)
soup = bs(response.text, 'html.parser')
vacancy_list = soup.find_all('div', {'class': 'vacancy-serp-item'})
print()
while len(vacancy_list) > 0:
    for vacancy in vacancy_list:
        vacancy_data = {}
        vacancy_info = vacancy.find('a', {'class': 'bloko-link'})
        vacancy_data['name'] = vacancy_info.getText()
        vacancy_salary_info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['salary_currency'] = min_max_salary(vacancy_salary_info)
        vacancy_data['link'] = vacancy_info.get('href')
        vacancy_data['url'] = url

        vacancies.append(vacancy_data)

    if page + 1 == int(num_of_pages):
        break

    page += 1
    params['page'] = str(page)

    response = requests.get(url+'/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancy_list = soup.find_all('div', {'class': 'vacancy-serp-item'})

pd.set_option('display.max_columns', None)
df = pd.DataFrame(vacancies)
df.to_csv('vacancies.csv', index=False)

print(df)
