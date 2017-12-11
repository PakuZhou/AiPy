'''
    jieba学习小例子
'''

import jieba
import jieba.posseg
testSentence=(u'我正在教室里学习文本挖掘的入门与实践')


#---------------------分词-----------------------

seg_list1=jieba.cut(testSentence,cut_all=False)
print("精准模式："+"/".join(seg_list1))

seg_list2=jieba.cut(testSentence,cut_all=True)
print("全模式："+"/".join(seg_list2))

seg_list3=jieba.cut_for_search(testSentence)
print("搜索模式："+"/".join(seg_list3))

seg_list4=jieba.cut(testSentence)
print("默认模式："+"/".join(seg_list4))

'''
精准模式：我/正在/教室/里/学习/文本/挖掘/的/入门/与/实践
  全模式：我/正在/教室/室里/学习/习文/文本/挖掘/的/入门/与/实践
搜索模式：我/正在/教室/里/学习/文本/挖掘/的/入门/与/实践
默认模式：我/正在/教室/里/学习/文本/挖掘/的/入门/与/实践
'''

#-------------------词性----------------------------
words = jieba.posseg.cut(testSentence)
for item in words:
    print(item.word+"---"+item.flag)

result = jieba.tokenize(testSentence)
for tk in result:
    print("word %s \t\t start: %d \t\t end:%d ;"%(tk[0],tk[1],tk[2]))
