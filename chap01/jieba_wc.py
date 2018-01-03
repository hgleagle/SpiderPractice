#!/usr/bin/env python3

import jieba.analyse  # 导入结巴分词
import numpy as np  # numpy
from wordcloud import WordCloud, STOPWORDS  # 词云工具和自带的的停用词
from PIL import Image  # 图片处理

STOPWORD_NEW = {
    '公司', '团队', '介绍', '使用', '岗位职责', '就是', '不是', '回复', '以上', '设计', '任职', '要求',
    '职位', '描述', '技能', ' 岗位', '职责', '工作', '资格', '优先', '能力', '工作'
}


def handle(filename, stopword):
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()

    wordlist = jieba.analyse.extract_tags(data, topK=70)  # 分词，取前70
    wordStr = " ".join(wordlist)

    hand = np.array(Image.open('hand.jpg'))  # 打开一张图片，词语以图片形状为背景分布

    my_cloudword = WordCloud(  # wordcloud参数配置
        background_color='black',  # 背景颜色
        font_path = 'DroidSansFallbackFull.ttf',
        mask=hand,  # 背景图片
        max_words=300,  # 最大显示的字数
        stopwords=stopword,  # 停用词
        max_font_size=60,  # 字体最大值
    )

    my_cloudword.generate(wordStr)  # 生成图片
    my_cloudword.to_file('wordcloud.png')  # 保存


if __name__ == '__main__':
    handle('jd.txt', STOPWORDS | STOPWORD_NEW)
