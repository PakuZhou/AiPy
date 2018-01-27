# Function:
#       从数据库中读取内容，将这些内容分词后按照词频绘制词云图。
# Time:
#       2017-10-30
# Author:
#       PakuZhou
# Environment：
#       Python 3.5.2

import matplotlib.pyplot as plt
import numpy as np
import jieba
import json
import random
import seaborn as sns
import pandas as pd
import collections
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
sns.set_context(font_scale=2)
# 解决Seaborn中文乱码，如果是windows系统，字体名称不一样，请自行百度
sns.set_style("darkgrid",{"font.sans-serif":['simhei', 'Arial']}) 
#设置图片大小
plt.figure(figsize=(15,8))

# 连接数据库
import MySQLdb
db = MySQLdb.connect(host="localhost", user="root" ,passwd="mysql",db="xmunews",charset="utf8")
cursor = db.cursor()

# 从数据库中获取数据
sql = """SELECT title from newstt"""
cursor.execute(sql)
results = cursor.fetchall()
comment = ''
for c in results:
	# 结巴分词
    seg_list = jieba.cut(c[0])
    # 去停用词，这里可以根据你的情况添加你要去掉的助词，语气词等
    stopwords = {}.fromkeys([u'我',u'你',u'我们',u'他',u'她',u'他们',u'妳',u'你们',u'它',u'I',u'you',u'Do',
                            u'oh',u'Oh',u'哼',u'哼哼',u'喔',u'呦', u'哎',u'啊',u'吧',u'嘿',u'Hey',u'哇',u'哦'
                             ,u'吗',u'咿',u'呢'])
    segs = [seg.strip() for seg in seg_list if seg not in stopwords]
    comment += '/'.join(segs) + '/'
    
# 统计词频
frequency_comment = collections.Counter(comment.split('/'))

# 获取词频最高的前2000个
words = []
for f in frequency_comment.most_common(2000):
    words.append(f[0])
words = ' '.join(words)


# 设置字体。将字体文件放在当前目录。
font = './DroidSansFallbackFull.ttf'
# 生成词云
wc = WordCloud(background_color="white",width=1920,height=1200,max_words=1000,font_path=font).generate_from_frequencies(frequency_comment)
plt.imshow(wc)
plt.axis("off")
plt.show()
# 保存成文件
wc.to_file('comment.png')
