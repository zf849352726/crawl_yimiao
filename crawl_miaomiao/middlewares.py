
from scrapy import signals
import random

# 导入ip_agent模块导入
from ip_agent.proxy_redis import ProxyRedis
import http.cookies
from http.cookies import SimpleCookie


class CrawlMiaomiaoSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CrawlMiaomiaoDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomProxyMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    # 初始化代理IP列表
    def __init__(self):
        self.redis = ProxyRedis()
        self.redis.get_avail_proxy()
        self.proxy_list = self.redis.lis[0]
        self.cookie_jar = {}

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # 发出请求前更换代理IP
        if request.url in spider.start_urls:
            proxy = 'http://' + random.choice(self.proxy_list)
            print(proxy)
            request.meta['proxy'] = proxy
        else:
            print(spider.success_ip)
            request.meta['proxy'] = spider.success_ip

        if 'cookie' in request.meta:
            cookie = request.meta['cookie']
            self.cookie_jar[request.url] = cookie
        else:
            if request.url in self.cookie_jar:
                cookie = self.cookie_jar[request.url]
                request.headers['Cookie'] = cookie.output(header='', sep=';')
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # if response.status != 200:
        #     self.logger.error('invalid status code: %s' % response.status)
        #     raise IgnoreRequest
        if request.url in spider.start_urls:
            spider.success_ip = request.meta['proxy']
            print(spider.success_ip)
        print(request.headers)
        set_cookie_headers = response.headers.getlist('Set-Cookie')
        if set_cookie_headers:
            cookie = SimpleCookie()
            for header in set_cookie_headers:
                cookie.load(header.decode('utf-8'))
            self.cookie_jar[response.url] = cookie
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        print("连接错误！！！！！！！！")
        return None

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


