from gensim import corpora ,models,similarities
import jieba
from collections import defaultdict

#1.导入句子
sent1 = "我喜欢吃番薯"
sent2 = "番薯是个好东西"
sent3 = "利用python进行文本挖掘"

#2.分词
data1 = "".join(jieba.cut(sent1))
data2 = "".join(jieba.cut(sent2))
data3 = "".join(jieba.cut(sent3))

#3.转换格式：词语1，词语2，词语3
texts = [list(data1),list(data2),list(data3)]

#4.基于文本建立字典
dictionary = corpora.Dictionary(texts)
featureNum = len(dictionary.token2id.keys())#提取词典特征数
dictionary.save("./dict_LearnGensim.txt")

#5.基于词典建立新的语料库
corpus = [dictionary.doc2bow(text) for text in texts]

#6.TF-IDF 处理
tfidf = models.TfidfModel(corpus)

#7.加载句子并整理其格式
query = "吃东西"
dataQ = "".join(jieba.cut(query))
dataQuery = ""
for item in dataQ:
    dataQuery += item + " "
new_doc =  dataQuery

#8.将对比句子转换为稀疏向量
new_vec = dictionary.doc2bow(new_doc.split())

#9.计算相似性
index = similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=featureNum)
sim = index[tfidf[new_vec]]
for i in  range(len(sim)):
    print("查询与第%d句话相似度为%f"%(i+1,sim[i]))



