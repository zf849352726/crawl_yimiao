"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-
@Project : crawl_miaomiao
@File : main.py
@Author : 帅张张
@Time : 2023/5/9 22:22

"""
from apscheduler.schedulers.blocking import BlockingScheduler
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from crawl_miaomiao.spiders.crawl_yimiao import CrawlYimiaoSpider

scheduler = BlockingScheduler()

# 定义定时任务，例如每天定时运行一次爬虫
@scheduler.scheduled_job('interval', days=1)
def run_spider():
    # 读取Scrapy项目配置信息
    settings = get_project_settings()
    # 创建Scrapy进程和爬虫对象
    process = CrawlerProcess(settings)
    spider = CrawlYimiaoSpider()
    # 运行爬虫
    process.crawl(spider)
    process.start()

scheduler.start()
