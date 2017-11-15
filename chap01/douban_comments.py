#!/usr/bin/python3


import requests
import sys, os
import io
from lxml import etree
import pandas as pd


def get_html(url):
    try:
        print(url)
        res = requests.get(url)
        res.raise_for_status()
        print(res.encoding)
        print(res.headers['content-type'])
        #print(res.text.encode('gb18030'))
        #print(res.text.encode('utf-8'))
        # print(res.text.encode('gbk', 'ignore'))
        # print(res.text)
        print(res.status_code)
        return res.text
    except Exception as exc:
        print("get html error %s" % (exc))
        return None


def parse_html(html):
    s = etree.HTML(html)
    # print(s.xpath('//*[@id="comments"]/ul/li[1]/div[2]/p/text()')) # copy from chrome
    # print(s.xpath('//*[@id="comments"]/ul/li/div[2]/p/text()'))  # sol1：get all comments
    print(s.xpath('//div[@class="comment"]/p/text()'))   # sol2
    comments = s.xpath('//div[@class="comment"]/p/text()')   # sol2
    return comments
    # print(s.xpath('//*[@id="page_list"]/ul/li[1]/div[2]/span[1]/i/text()'))
    # print(s.xpath('//*[@id="page_list"]/ul/li[1]/div[2]/div/a/span/text()'))


if __name__ == "__main__":
    os.chdir(os.getcwd() + '\SpiderPractice\chap01')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8') #改变标准输出的默认编码  
    urls = [ "https://book.douban.com/subject/19952400/comments/hot?p={}".format(str(i)) for i in range(1, 6) ]
    # url = "https://www.zhihu.com/topic/19552832/top-answers"
    # url = "http://sz.xiaozhu.com/"
    contents = []
    for url in urls:
        html = get_html(url)
        if html is not None:
            contents += parse_html(html)
    df = pd.DataFrame(contents)
    df.to_excel('comments.xlsx')