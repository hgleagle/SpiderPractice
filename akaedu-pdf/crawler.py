# coding=utf-8
from __future__ import unicode_literals

import logging
import os
import re
import time

try:
    from urllib.parse import urlparse  # py3
except:
    from urlparse import urlparse  # py2

import pdfkit
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


logging.basicConfig(level=logging.DEBUG)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""

headers = """Host: www.liaoxuefeng.com
# Connection: keep-alive
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# Referer: https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431608990315a01b575e2ab041168ff0df194698afac000
# Accept-Encoding: gzip, deflate, sdch, br
# Accept-Language: en-US,zh-CN;q=0.8,zh;q=0.6,en;q=0.4
# Cookie: Hm_lvt_2efddd14a5f2b304677462d06fb4f964=1510629454; Hm_lpvt_2efddd14a5f2b304677462d06fb4f964=1512461956"""


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content


def delete_proxy(proxy):
    return requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def to_dict(header):
    hs = header.split('\n')
    head_dict = {}
    for h in hs:
        if h:
            key, value = h.split(':', maxsplit=1)
            head_dict[key] = value.strip()
    # logging.debug(head_dict)
    return head_dict

class Crawler(object):
    """
    爬虫基类，所有爬虫都应该继承此类
    """
    name = None

    def __init__(self, name, start_url, proxy):
        """
        初始化
        :param name: 将要被保存为PDF的文件名称
        :param start_url: 爬虫入口URL
        """
        self.name = name
        self.start_url = start_url
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.start_url))
        self.use_proxy = proxy

    @staticmethod
    def request(url, **kwargs):
        """
        网络请求,返回response对象
        :return:
        """
        response = requests.get(url, **kwargs)
        return response

    def parse_menu(self, response):
        """
        从response中解析出所有目录的URL链接
        """
        raise NotImplementedError

    def parse_body(self, response):
        """
        解析正文,由子类实现
        :param response: 爬虫返回的response对象
        :return: 返回经过处理的html正文文本
        """
        raise NotImplementedError

    def run(self):
        start = time.time()
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'cookie': [
                ('cookie-name1', 'cookie-value1'),
                ('cookie-name2', 'cookie-value2'),
            ],
            'outline-depth': 10,
        }
        htmls = []
        ua = UserAgent()
        # headers = headers % (ua.random)
        head = to_dict(headers)
        resp = self.request(self.start_url)
        logging.debug(resp.text)
        for index, url in enumerate(self.parse_menu(resp)):
            head['User-Agent'] = ua.random
            # retry_count = 5
            if self.use_proxy:
                proxy = get_proxy()
                logging.debug(proxy)
                while True:
                    try:
                        html = self.request(url, proxies={"http": "http://{}".format(proxy)}, headers=head)
                    except Exception:
                        delete_proxy(proxy)
                        proxy = get_proxy()
            else:
                html = self.request(url)
            html = self.parse_body(html)
            f_name = ".".join([str(index), "html"])
            with open(f_name, 'wb') as f:
                f.write(html)
            htmls.append(f_name)
            time.sleep(5)

        pdfkit.from_file(htmls, self.name + ".pdf", options=options)
        for html in htmls:
            os.remove(html)
        total_time = time.time() - start
        print(u"总共耗时：%f 秒" % total_time)


class SongjinshanCProgramCrawler(Crawler):
    """
    宋劲衫Learning Linux C Programming From Scratch教程
    """

    def parse_menu(self, response):
        """
        解析目录结构,获取所有URL目录列表
        :param response 爬虫返回的response对象
        :return: url生成器
        """
        soup = BeautifulSoup(response.content, "html.parser")
        menu_tag = soup.find_all(class_=["preface", "part", "chapter", "sect1"])
        for tag in menu_tag:
            logging.debug(tag)
            url = tag.a.get("href")
            if not url.startswith("http"):
                url = "".join([self.domain, "/book/", url])  # 补全为全路径
            yield url

    def parse_body(self, response):
        """
        解析正文
        :param response: 爬虫返回的response对象
        :return: 返回处理后的html文本
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            body = soup.find_all(class_=["preface", "part", "chapter", "sect1"])

            # 加入标题, 居中显示
            # title = soup.find('title').get_text()
            # logging.debug(title, body)
            # center_tag = soup.new_tag("center")
            # title_tag = soup.new_tag('h1')
            # title_tag.string = title
            # center_tag.insert(1, title_tag)
            # body.insert(1, center_tag)

            html = str(body)
            # body中的img标签的src相对路径的改成绝对路径
            pattern = "(<img .*?src=\")(.*?)(\")"

            def func(m):
                if not m.group(2).startswith("http"):
                    rtn = "".join([m.group(1), self.domain + "/book/", m.group(2), m.group(3)])
                    return rtn
                else:
                    return "".join([m.group(1), m.group(2), m.group(3)])

            html = re.compile(pattern).sub(func, html)
            html = html_template.format(content=html)
            html = html.encode("utf-8")
            return html
        except Exception as e:
            logging.error("解析错误", exc_info=True)


if __name__ == '__main__':
    start_url = "https://akaedu.github.io/book/index.html"
    crawler = SongjinshanCProgramCrawler("Linux C编程一站式学习", start_url, 0)
    crawler.run()
