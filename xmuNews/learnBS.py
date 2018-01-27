'''
learn from: http://cuiqingcai.com/1319.html
'''

from bs4 import BeautifulSoup


doc='''
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title" name="dromouse"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1"><!-- Elsie --></a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>

'''
soup = BeautifulSoup(doc,'html.parser')

#soup 对象的内容，格式化输出
print (soup.prettify())
print('*********************************************')

#利用 soup加标签名轻松地获取这些标签的内容
print(soup.a)
print(soup.title)
print(soup.p)
print(soup.head)
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

# (1) Tag
# Tag 有两个重要的属性，name & attrs
#  soup 对象本身比较特殊，它的 name 即为 [document]，对于其他内部标签，输出的值便为标签本身的名称
print(soup.name)
print(soup.head.name)
# p 标签的所有属性打印输出了出来，得到的类型是一个字典。
print(soup.p.attrs)
#如果我们想要单独获取某个属性，可以这样，例如我们获取它的 class 叫什么
print(soup.p['class'])
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

# (2)NavigableString
# 获取标签内部的文字
print(soup.p.string)
print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

# 7.搜索文档树
# 最简单的过滤器是字符串.在搜索方法中传入一个字符串参数,Beautiful Soup会查找与字符串完整匹配的内容.
print('1')
print(soup.find_all('b'))
print('2')
print(soup.find_all('a'))
print('3')
import re
for tag in soup.find_all(re.compile("^a")):
    print(type(tag))
    print(tag.string)
    print(tag)
    print(tag.attrs)
    print(tag['href'])



