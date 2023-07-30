import scrapy
import sys
import json
from json.decoder import JSONDecodeError
import subprocess
from scrapy.core.downloader import handlers
import twisted
import os
import requests

from datetime import datetime
import pytz

import base64
import json
import time

import hmac


class CrawlYimiaoSpider(scrapy.Spider):
    name = 'crawl_yimiao'
    allowed_domains = ['scmttec.com']
    start_urls = ['https://miaomiao.scmttec.com/seckill/seckill/list.do?offset=0&limit=10&regionCode=4401']  # 初始url
    # possible_url0 = 'https://miaomiao.scmttec.com/seckill/seckill/log.do?id=7090'
    # 将ip_agent模块添加到python的环境变量
    sys.path.append(r'D:\python_learn')
    sys.path.append(r'D:\Anaconda\envs\qqzone_crawl\Lib\site-packages')
    sys.path.append(r'D:\python_learn\ip_agent')
    # print(sys.path)
    success_ip = None

    def __init__(self):
        self.json_data = None
        self.vaccine_id = None

    def start_requests(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6763',
            'Accept': 'application/json, text/plain, */*',
            'referer': 'https://servicewechat.com/wxff8cad2e9bf18719/37/page-frame.html',
            'xweb_xhr': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh',
            'Cookie': '_xxhm_=%7B%22id%22%3A35732963%2C%22mobile%22%3A%2213158790939%22%2C%22nickName%22%3A%22%E9%BB%8F%E6%80%A7%E7%B3%96%E6%B3%A1%E6%B3%A1%22%2C%22headerImg%22%3A%22https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2Fa3VG0NzrEAymGW8OU0fZJoosu8kNe9JK8Pv0BaL60kWfia088mweZDzwmfHmRgXNeIiaHckQ2yuQHXB1d9zA5ERA%2F132%22%2C%22regionCode%22%3A%22510107%22%2C%22name%22%3A%22%E9%BB%8E*%E7%AB%8B%22%2C%22uFrom%22%3A%22depa_vacc_detail%22%2C%22wxSubscribed%22%3A1%2C%22birthday%22%3A%222000-03-20+02%3A00%3A00%22%2C%22sex%22%3A2%2C%22hasPassword%22%3Afalse%2C%22birthdayStr%22%3A%222000-03-20%22%7D; _xzkj_=wxapptoken%3A10%3Addeec96c388734157ec423369a740cd1_55aa5692532a6294c217f3f58ba43787; b6c4=2e591cfa2fef03d66e; 42f4=085e52650cf2e238cc'
        }

        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.attain_id_parse)

    # 获取疫苗id
    def attain_id_parse(self, response):
        headers = {
            'Host': 'miaomiao.scmttec.com',
            'Connection': 'keep-alive',
            'Cookie': 'tgw_l7_route=31e26ac7a066ca4fc11361525ae43d81',
            'tk': '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6763',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, /',
            'Referer': 'https://servicewechat.com/wxff8cad2e9bf18719/37/page-frame.html',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh'
        }
        self.json_data = response.json()
        print(self.json_data)
        if self.json_data is None:
            raise Exception("请求成功，但是数据有问题")
        else:
            self.vaccine_id = self.json_data['data'][0]['id']

            token_url = 'https://miaomiao.scmttec.com/passport/wxapp/login.do?code=0a33Tw000ykFYP1SmB100FmEQq43Tw09&minaId=10'
            yield scrapy.Request(url=token_url, headers=headers, callback=self.attain_token, dont_filter=True)

    # 获取token
    def attain_token(self, response):
        print(response.json())
        cookies = {
            f'Cookie': '_xxhm_=%7B%22id%22%3A35732963%2C%22mobile%22%3A%2213158790939%22%2C%22nickName%22%3A%22%E9%BB%8F%E6%80%A7%E7%B3%96%E6%B3%A1%E6%B3%A1%22%2C%22headerImg%22%3A%22https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2Fa3VG0NzrEAymGW8OU0fZJoosu8kNe9JK8Pv0BaL60kWfia088mweZDzwmfHmRgXNeIiaHckQ2yuQHXB1d9zA5ERA%2F132%22%2C%22regionCode%22%3A%22510107%22%2C%22name%22%3A%22%E9%BB%8E*%E7%AB%8B%22%2C%22uFrom%22%3A%22depa_vacc_detail%22%2C%22wxSubscribed%22%3A1%2C%22birthday%22%3A%222000-03-20+02%3A00%3A00%22%2C%22sex%22%3A2%2C%22hasPassword%22%3Afalse%2C%22birthdayStr%22%3A%222000-03-20%22%7D; _xzkj_=wxapptoken%3A10%3Addeec96c388734157ec423369a740cd1_376d1af7a533d0861ff737500242860e; b6c4=2e591cfa2fef03d66e; 42f4=085e52650cf2e238cc'
        }

        headers = {
            'tk': 'wxapptoken:10:ddeec96c388734157ec423369a740cd1_376d1af7a533d0861ff737500242860e',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6763',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'referer': 'https://servicewechat.com/wxff8cad2e9bf18719/37/page-frame.html',
            'xweb_xhr': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh'
            # f'Set-Cookie: tgw_l7_route=31e26ac7a066ca4fc11361525ae43d81; Expires={expires}; Path=/',
        }
        next_url = f'https://miaomiao.scmttec.com/seckill/seckill/detail.do?id={self.vaccine_id}'
        yield scrapy.Request(url=next_url, headers=headers, cookies=cookies, callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        # print(response.headers)
        print(response.json())
        submit_page = 'https://miaomiao.scmttec.com/seckill/seckill/subscribe.do'  # 提交订单的链接

        headers = {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'tk': 'wxapptoken:10:ddeec96c388734157ec423369a740cd1_376d1af7a533d0861ff737500242860e',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6763',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'ecc-hs': '8a5ce619b0dc53ca94785f6f4849816b',
            'Referer': 'https://servicewechat.com/wxff8cad2e9bf18719/37/page-frame.html',
            'xweb_xhr': '1',
            'Cookie': '_xxhm_=%7B%22id%22%3A35732963%2C%22mobile%22%3A%2213158790939%22%2C%22nickName%22%3A%22%E9%BB%8F%E6%80%A7%E7%B3%96%E6%B3%A1%E6%B3%A1%22%2C%22headerImg%22%3A%22https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2Fa3VG0NzrEAymGW8OU0fZJoosu8kNe9JK8Pv0BaL60kWfia088mweZDzwmfHmRgXNeIiaHckQ2yuQHXB1d9zA5ERA%2F132%22%2C%22regionCode%22%3A%22510107%22%2C%22name%22%3A%22%E9%BB%8E*%E7%AB%8B%22%2C%22uFrom%22%3A%22depa_vacc_detail%22%2C%22wxSubscribed%22%3A1%2C%22birthday%22%3A%222000-03-20+02%3A00%3A00%22%2C%22sex%22%3A2%2C%22hasPassword%22%3Afalse%2C%22birthdayStr%22%3A%222000-03-20%22%7D; _xzkj_=wxapptoken%3A10%3Addeec96c388734157ec423369a740cd1_bffd62b809d316102e69524c334a08d9; 7720=2343b3a3d7a356ed43; tgw_l7_route=31e26ac7a066ca4fc11361525ae43d81',
            'isFormData': '[object Boolean]',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh'
        }
        formdata = {
            'seckillId': str(self.vaccine_id),
            'linkmanId': '38010177',
            'idCardNo': '511526200003205828'
        }
        # 有数据，则返回结果
        yield scrapy.FormRequest(url=submit_page, headers=headers, formdata=formdata, callback=self.if_submit)

    def if_submit(self, response):
        print(response.json())
        # print(response.headers)



