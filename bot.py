from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import vk_api
import requests
import time
import random
from bs4 import BeautifulSoup as bs
import apiai
import json
df_key ='f8e942456803467e862e8b2edc2772fc'
vk_session= vk_api.VkApi(token = 'f0d14c310f179e62ce4821a3dc17a23312c936de27b1a335844b33072ab56e55388bfa6f0d66e2d26a509')
from vk_api.longpoll import VkLongPoll, VkEventType
longpoll= VkLongPoll(vk_session)
vk = vk_session.get_api()
for event in longpoll.listen():
    if event.type== VkEventType.MESSAGE_NEW and event.to_me and event.text:
        if event.text == 'Найди кафе' or event.text == 'найди кафе':
            if event.from_user:
                vk.messages.send(user_id=event.user_id, message='Привет! Напиши что хочешь покушать', random_id=time.time() * 10000)
                time.sleep(15)
                req = vk.messages.getHistory(user_id=event.user_id, count=1)
                print(req)
                message = req['items'][0]['text']
                print(message)
                stroka = message.split()
                query = '+'.join(stroka)
                html_code = requests.get('https://www.afisha.ru/msk/restaurants/restaurant_list/?q='+query).text
                soup = bs(html_code, 'lxml')
                for product in soup.findAll('section', {'class': 'places_cards'}):
                    product_name = product.find('span', {'class': 'places_name'}).text
                    product_adress = product.find('span', {'class': 'places_address'}).text
                    product_link = product.a.get('href')
                    if product_name or product_adress:
                        try:
                            vk.messages.send(user_id = event.user_id, message = product_name + product_adress + ('https://www.afisha.ru/' + product_link), random_id = time.time() * 10000)
                        except:
                            vk.messages.send(user_id=event.user_id, message='Не удалось вывести данные об этом ресторане',random_id=time.time() * 10000)
        elif event.text:
            if event.from_user:
                ai_req = apiai.ApiAI(df_key).text_request()
                ai_req.lang = 'ru'
                ai_req.session_id = '123'
                ai_req.query = event.text
                responseJson = json.loads(ai_req.getresponse().read().decode('utf-8'))
                response = responseJson['result']['fulfillment']['speech']
                if response:
                    answer = response
                else:
                    answer = 'всё плохо'
                vk.messages.send(user_id=event.user_id, message=answer, random_id=time.time() * 10000)
