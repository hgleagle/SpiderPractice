#!/usr/bin/env python3
from pymongo import MongoClient
from fake_useragent import UserAgent
import requests
import time
from lxml import etree


client = MongoClient()
db = client.test
my_set = db.set


def parse_html(html):
    s = etree.HTML(html)
    # description = s.xpath('//*[@id="job_detail"]/dd[2]/div/p/text()')   # sol2
    description = s.xpath('string(//*[@id="job_detail"]/dd[2]/div)')   # sol2
    print(description)
    with open('jd.txt', 'a', encoding='utf-8') as f:
        f.write(description)


def get_data(url, payload, headers):
    res = requests.post(url, data=payload, headers=headers)
    res.raise_for_status()
    print('{}'.format(res.status_code))
    data = res.json()
    if res.status_code == 200:
        print('spider page {}...'.format(payload['pn']))
        my_set.insert(data['content']['positionResult']['result'])
        for i in range(data['content']['positionResult']['resultSize']):
            pos_id = data['content']['positionResult']['result'][i]['positionId']
            html = requests.get('https://www.lagou.com/jobs/%d.html' % pos_id, headers=headers)
            if html is not None:
                print(html.text)
                parse_html(html.text)
    else:
        print('fail to spider {}'.format(payload['pn']))
    time.sleep(3)


def get_page_info(page_nums):
    url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0'
    ua = UserAgent()
    i = 0
    while True:
        payload = {'first': 'true', 'pn': i, 'kd': 'python'}
        user_agent = ua.random
        headers = {
            'User-Agent':
            user_agent,
            'Cookie':
            'JSESSIONID=ABAAABAAAIAACBI8D7EF882745DC240C30D90CEE4EA1773; user_trace_token=20171203160055-da95e990-a1c3-46a4-8e39-bbbb1d5e49e2; LGUID=20171203160058-18f9bfe0-d800-11e7-be14-525400f775ce; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1512288059,1512288126,1512288157; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1512288157; _ga=GA1.2.1006944311.1512288059; _gid=GA1.2.1820278865.1512288059; LGRID=20171203160237-53a670fc-d800-11e7-9bb7-5254005c3644; SEARCH_ID=4d500fd47f1e44baacf8780e32137b69',
            'Referer':
            'https://www.lagou.com/jobs/list_python?oquery=%E7%88%AC%E8%99%AB&fromSearch=true&labelWords=relative'
        }

        get_data(url, payload, headers)
        i += 1


if __name__ == "__main__":
    get_page_info(30)
