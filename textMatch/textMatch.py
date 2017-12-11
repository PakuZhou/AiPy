'''
《数据科学与大数据技术》第三次作业
Function:
    查找与查询语句文本相似度大于0的句子
Time：
    2017-11-28
Author：
    PakuZhou
'''

from gensim import corpora,models,similarities
import jieba

# 导入停用词
import io
stopwordset=set()
with io.open('./stopwords.txt','r',encoding='utf-8') as sw:
    for line in sw:
        stopwordset.add(line.strip('\n'))#去掉收尾的\n


# 1-读取原始数据集(新闻标题),分词，并转换格式
# 由于厦大新闻网部分网页无法爬取，这边将第一次作业时用到的数据导成csv文件。
import csv
titles = []
texts = []
with open('titles.csv', 'r') as f:
    reader = csv.reader(f)
    for row in  reader:
        titles.append(row[1])
        seg_list =jieba.cut(row[1])
        ############## 去停用词 ####################
        stopwords = {}.fromkeys([u'我',u'你',u'我们',u'他',u'她',u'他们',u'妳',u'你们',u'它'])
        seg_list = [seg.strip() for seg in seg_list if seg not in stopwords]
        segs =" ".join([seg.strip() for seg in seg_list if seg not in stopwordset])
        texts.append(list(segs))#转换格式："词语1 词语2 ... 词语n"
#print(texts)


# 2-基于文本建立词典
dictionary=corpora.Dictionary(texts)
featureNum=len(dictionary.token2id.keys())# 提取词典特征数
#dictionary.save_as_text("./dictionary.txt",sort_by_word=True)#保存语料库

# 3-基于词典建立新的语料库
corpus=[dictionary.doc2bow(text) for text in texts]

# 4-TF-IDF处理
tfidf=models.TfidfModel(corpus)

# 5-加载对比句子并整理其格式
query1="国家语委副主任、教育部语用司司长姚喜双一行到我校调研语言文字工作"
query2="我校新增7名享受国务院政府特殊津贴专家"
query3="学校慰问春节在岗人员"
data1=jieba.cut(query1)
data2=jieba.cut(query2)
data3=jieba.cut(query3)

new_doc1 =" ".join([seg1.strip() for seg1 in data1 if seg1 not in stopwordset])
new_doc2 =" ".join([seg2.strip() for seg2 in data2 if seg2 not in stopwordset])
new_doc3 =" ".join([seg3.strip() for seg3 in data3 if seg3 not in stopwordset])



#6-将对比句子转换为稀疏向量
new_vec1=dictionary.doc2bow(new_doc1.split())
new_vec2=dictionary.doc2bow(new_doc2.split())
new_vec3=dictionary.doc2bow(new_doc3.split())


# 7-计算相似性并存储结果
index=similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=featureNum)

resltFile=open('result.txt','w')
resltFile.truncate()

sim1=index[tfidf[new_vec1]]
resltFile.write("\n\n*******************【%s]的查询结果 *******************\n"%query1)
for i in  range(len(sim1)):
    if sim1[i] >0:
        resltFile.write("相似度为%f\t[%s]\n "%(sim1[i],titles[i]))

sim2=index[tfidf[new_vec2]]
resltFile.write("\n\n*******************【%s]的查询结果 *******************\n"%query2)
for i in  range(len(sim2)):
    if sim2[i] >0:
        resltFile.write("相似度为%f\t[%s]\n "%(sim2[i],titles[i]))

sim3 = index[tfidf[new_vec3]]
resltFile.write("\n*******************【%s]的查询结果 *******************\n"%query3)
for i in range(len(sim3)):
    if sim3[i] >0:
        resltFile.write("相似度为%f\t[%s] \n"%(sim3[i],titles[i]))

simFile=open('sim.txt','w')
simFile.truncate()
simFile=open('sim.txt','a')
simFile.write("\n\n[%s]的查询相似度结果:\n"%query1)
simFile.write(str(sim1)+"\n")
simFile.write("\n\n[%s]的查询相似度结果:\n"%query2)
simFile.write(str(sim2)+"\n")
simFile.write("\n\n[%s]的查询相似度结果:\n"%query3)
simFile.write(str(sim3)+"\n")
simFile.close()
