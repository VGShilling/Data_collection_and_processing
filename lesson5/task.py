from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

import time


def data_to_db(data):
    client = MongoClient('127.0.0.1', 27017)
    if client['letters'].mail:
        client['letters'].mail.drop()
    db = client['letters']
    collection = db.mail

    collection.insert_many(data)
    return collection


chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)
driver.get("https://mail.ru/")

login = driver.find_element_by_name('login')
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)

wait_passwrd_input = WebDriverWait(driver, 3)
wait_passwrd_input.until(EC.visibility_of_element_located((By.NAME, 'password')))

passwrd = driver.find_element_by_name('password')
passwrd.send_keys('NextPassword172!!!')
passwrd.send_keys(Keys.ENTER)

wait_inbox_load = WebDriverWait(driver, 20)
wait_inbox_load.until(EC.presence_of_element_located((By.CLASS_NAME, 'dataset__items')))

inbox_set = set()
href_1, href_2 = ("0", "1")

while href_1 != href_2:
    href_1 = href_2
    inbox = driver.find_elements_by_xpath("//a[contains(@class, 'llc ')]")
    for letter in inbox:
        inbox_set.add(letter.get_attribute('href'))
    actions = ActionChains(driver)
    actions.move_to_element(inbox[-1])
    actions.perform()
    time.sleep(1)
    href_2 = inbox[-1].get_attribute('href')

letters_list = []
for el in inbox_set:
    driver.get(el)
    letter_data = {}
    wait_letter_load = WebDriverWait(driver, 20)
    wait_letter_load.until(EC.presence_of_element_located((By.CLASS_NAME, 'letter-contact')))

    letter_data['author'] = driver.find_element_by_class_name('letter-contact').text
    letter_data['date'] = driver.find_element_by_class_name('letter__date').text
    letter_data['subject'] = driver.find_element_by_class_name('thread__subject').text
    letter_data['text'] = driver.find_element_by_class_name('letter__body').text

    letters_list.append(letter_data)


mail = data_to_db(letters_list)
