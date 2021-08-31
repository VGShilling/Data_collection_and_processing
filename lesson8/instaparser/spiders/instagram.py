import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from lesson8.instaparser.items import InstaparserItem
from lesson8.instaparser.authentication import login, passwrd


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    insta_login = login
    insta_pass = passwrd
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    users_parse = ['verymaximus', 'm_n_shap']
    api_url = 'https://i.instagram.com/api/v1/friendships'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.insta_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pass},
                                 headers={'X-CSRFToken': csrf})

    def user_login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            for user in self.users_parse:
                yield response.follow(f'/{user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user})

    def user_data_parse(self, response: HtmlResponse, username):
        # Вместо response страницы пользователя мне в основном вылетает login
        # <200 https://www.instagram.com/accounts/login/>
        # И я так и не понял с чем это связано,
        # потому, что ничего принципиально в коде не меняя, периодически response проходит правильный.
        # Собственно, поэтому я не смог проверить, корректно ли я в итоге написал код...

        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'count': '12',
            'search_surface': 'follow_list_page'
        }
        # url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
        url_followers = f'{self.api_url}/{variables["id"]}/followers/?count={variables["count"]}'
        yield response.follow(url_followers,
                              callback=self.followers_parse,
                              cb_kwargs={'username': deepcopy(username),
                                         'user_id': deepcopy(user_id),
                                         'variables': deepcopy(variables)},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

        url_following = f'{self.api_url}/{variables["id"]}/following/?count={variables["count"]}'
        yield response.follow(url_following,
                              callback=self.following_parse,
                              cb_kwargs={'username': deepcopy(username),
                                         'user_id': deepcopy(user_id),
                                         'variables': deepcopy(variables)},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('next_max_id'):
                variables['max_id'] = j_data.get('next_max_id')
                url_followers = f'{self.api_url}/{variables["id"]}/followers/?count={variables["count"]}' \
                                f'&max_id={variables["max_id"]}&search_surface={variables["search_surface"]}'
                yield response.follow(url_followers,
                                      callback=self.followers_parse,
                                      cb_kwargs={'username': deepcopy(username),
                                                 'user_id': deepcopy(user_id),
                                                 'variables': deepcopy(variables)},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'})

            followers = j_data.get('users')
            for follower in followers:
                item = InstaparserItem(user_id=follower.get('pk'),
                                       username=follower.get('username'),
                                       picture=follower.get('profile_pic_url'),
                                       the_way='follower',
                                       parsed_user_id=user_id,
                                       parsed_username=username
                                       )
                yield item

    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('next_max_id'):
                variables['max_id'] = j_data.get('next_max_id')
                url_following = f'{self.api_url}/{variables["id"]}/following/?count={variables["count"]}' \
                                f'&max_id={variables["max_id"]}&search_surface={variables["search_surface"]}'
                yield response.follow(url_following,
                                      callback=self.following_parse,
                                      cb_kwargs={'username': deepcopy(username),
                                                 'user_id': deepcopy(user_id),
                                                 'variables': deepcopy(variables)},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'})

            followings = j_data.get('users')
            for following in followings:
                item = InstaparserItem(user_id=following.get('pk'),
                                       username=following.get('username'),
                                       picture=following.get('profile_pic_url'),
                                       the_way='following',
                                       parsed_user_id=user_id,
                                       parsed_username=username
                                       )
                yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
