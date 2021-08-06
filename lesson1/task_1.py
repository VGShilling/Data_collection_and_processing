# Задание 1.
# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json

user = 'VGShilling'
url = f'https://api.github.com/users/{user}/repos'

response = requests.get(url)
j_data = response.json()

for el in j_data:
    print(el['name'])

with open('repo.json', 'w') as f:
    json.dump(j_data, f)
