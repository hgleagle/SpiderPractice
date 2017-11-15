#!/usr/bin/python3


import requests
import sys, os
import io
from lxml import etree
import pandas as pd
import time


headers = {
    'authorization': 'Bearer Mi4xaFBnX0FBQUFBQUFBQUFJaFF3T0pEQmNBQUFCaEFsVk5YTllMV2dBbnZseVpUZzI2SW05ZVFXcmlveG56MmhtRmRB|1508133212|36699f323ae721e1c2cb4fc47990ecc5159b3373',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}
def get_html(url):
    try:
        print(url)
        res = requests.get(url, headers = headers)
        res.raise_for_status()
        print(res.encoding)
        print(res.headers['content-type'])
        #print(res.text.encode('gb18030'))
        #print(res.text.encode('utf-8'))
        # print(res.text.encode('gbk', 'ignore'))
        # print(res.text)
        print(res.status_code)
        return res
    except Exception as exc:
        print("get html error %s" % (exc))
        return None


def get_followee_data(page):
    urls = ['https://www.zhihu.com/api/v4/members/excited-vczh/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={}&limit=20'
    .format(i*20) for i in range(page)]
    contents = [] 
    for url in urls:
        html = get_html(url)
        if html is not None:
            contents += html.json()['data'] 
        print('get page %s' % (url))
        time.sleep(1)
    return contents 


if __name__ == "__main__":
    os.chdir(os.getcwd() + '\SpiderPractice\chap01')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8') #改变标准输出的默认编码  
    contents = get_followee_data(10)
    df = pd.DataFrame.from_dict(contents)
    df.to_excel('followee.xlsx')
        
    #     contents += parse_html(html)
    # print(contents)