# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from zhihuuser.items import UserItem






class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    user_query_include = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    followees_query_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_query_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'


    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query_include),callback=self.parse_user)
        yield Request(self.followees_url.format(user=self.start_user,include=self.followees_query_include,offset=0,limit=20),callback=self.parse_followees)
        yield Request(self.followers_url.format(user=self.start_user,include=self.followers_query_include,offset=0,limit=20),callback=self.parse_followers)


    def parse_user(self, response):
        #json.loads()把str转成dict
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield Request(self.followees_url.format(user=result.get('url_token'),include=self.followees_query_include,limit=20,offset=0),callback=self.parse_followees)
        yield Request(self.followers_url.format(user=result.get('url_token'),include=self.followers_query_include,limit=20,offset=0),callback=self.parse_followers)



    def parse_followees(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query_include),callback=self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end')==False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,callback=self.parse_followees)




    def parse_followers(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query_include),
                              callback=self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_followers)
