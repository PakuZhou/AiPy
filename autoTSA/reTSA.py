import warnings
import itertools
from collections import defaultdict
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import time
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.sandbox.stats.diagnostic import acorr_ljungbox
from findSARIMA import autoTSA

plt.style.use('fivethirtyeight')


def dataFrame2List(ts):
    '''
    将一个dataFrame类转换成list
    :param ts: 时间序列
    :return:  装换之后的列表
    '''
    y_list = np.array(y).tolist()
    return [v[0] for v in y_list]

def adfStationary(tsList):
    '''
    adf检验，并将结果格式化输出。
    :param tsList: 时间序列转换之后的列表
    :return: 是否满足平稳性
    '''
    adf = sm.tsa.stattools.adfuller(tsList)
    print('\n\t\t###ADF Results###')
    print('adf:%.5f\tp_value:%.5f\n'%(adf[0],adf[1]))
    print('critical values:\n{}\n'.format(adf[4]))
    if adf[0] < adf[4]['1%']:
        print("Yeah! It's Stationary ~~~\n")
        return True
    elif adf[0] > adf[4]['10%']:
        print("Oh! Tt's NOT Stationary !!!\n")
        return False
    else:
        print("May Stationary ...\n")
        return False

def calAcfPacf(ts,visualization = False):
    '''
    计算自相关系数和偏置相关系数
    :param ts: 时间序列
    :param visualization: 是否画图
    :return: 自相关系数[列表],偏置相关系数[列表]
    '''
    sm.graphics.tsa.plot_acf(ts,lags = 40)
    plt.savefig('./tsa1_data_acf')
    sm.graphics.tsa.plot_pacf(ts,lags = 40)
    plt.savefig('./tsa1_data_pacf')
    if visualization:
        plt.show()
    acf,acfConfInt = sm.tsa.acf(ts.values,alpha=.05)
    pacf,pacfConfInt = sm.tsa.pacf(ts.values,alpha=.05)
    # print(acf)
    # print(pacf)
    # print(acfConfInt)
    # print(pacfConfInt)
    return acf,acfConfInt,pacf,pacfConfInt

def getpq(ts):
    '''
    获取自相关系数和偏自相关系数中大于两倍标准差的阶数
    :param ts: 时间序列
    :return: 两个延迟阶数的列表
    '''
    acf,acfConfInt,pacf,pacfConfInt = calAcfPacf(ts)
    p = []
    q = []
    for i in range(len(acf)):
        # print('{},{},{}'.format(acf[i],acfConfInt[i][0],acfConfInt[i][1]))
        if acf[i] >= (acfConfInt[i][1]-acf[i]) or acf[i] <= (acfConfInt[i][0]-acf[i]):
            p.append(i)
        if pacf[i] >= (pacfConfInt[i][1]-pacf[i]) or pacf[i] <= (pacfConfInt[i][0]-pacf[i]):
            q.append(i)
    return p,q

def loadData(file,index,visualization=False):
    '''
    加载数据
    :param file: 文件名
    :param index: 数据索引
    :return: 时间序列数据[列表]
    '''
    data=pd.read_csv(file,encoding='utf-8',index_col=index)
    data.index=pd.to_datetime(data.index)
    print('length of data:{}\n'.format(len(data)))
    data.plot()
    plt.savefig('./ts')
    if visualization:
        plt.show()
    return data

def diflist(lst):
    '''
    对列表进行查分
    :param lst: 待差分的列表
    :return:  差分之后的列表
    '''
    dif = []
    for i in range(len(lst)):
        if i == len(lst)-2:
            break
        dif.append(lst[i+1]-lst[i])
    return dif

def difStationary(ts):
    '''
    计算将时序差分到平稳需要几阶
    :param ts: 时间序列
    :return: 可行的阶数列表以及对应的时间序列[字典]
    '''
    stationSeries = defaultdict(list)
    existStation = False
    for i in range(0,5):
        ts_diff = sm.tsa.statespace.tools.diff(ts)
        ts_diff_list = dataFrame2List(ts_diff)
        stationary = adfStationary(ts_diff_list)
        if stationary:
            existStation = True
            stationSeries[i] = ts_diff
            break
        ts = ts_diff
    if existStation:
        return stationSeries
    else:
        print('Can NOT diff to stationary!')
        return stationSeries

def paraSignf(pvalues):
    return (max(pvalues) < 0.05)

def modlSignf(pval):
    print(min(pval))
    return (min(pval) > 0.05)

def findSimModel(ts):
    '''
    寻找序列的简单模型，如果不存在则返回空
    :param ts: 时间序列
    :return:   是否是简单模型，拟合之后的模型
    '''

    #对序列差分得到平稳序列
    stationSeries = difStationary(ts)

    exitSimModel = False
    isSimModel = True

    #查分的阶数
    d = list(stationSeries.keys())[0]

    p,q = getpq(stationSeries[d])
    if len(p) > 8 or max(p) >=12:
        isSimModel = False
        print('自相关系数超过两倍标准差的阶数有：{}'.format(p))
    if len(q) > 8 or max(p) >=12:
        isSimModel = False
        print('偏自相关系数超过两倍标准差的阶数：{}'.format(q))

    #确定该序列的p，q
    if isSimModel:
        ARp = max(p)
        MAq = max(q)
    else:
        res = sm.tsa.arma_order_select_ic(y, ic=['aic'], trend='nc')
        ARp = int(res.aic_min_order[0])
        MAq = int(res.aic_min_order[1])
        print('AIC MIN ORDER:{}'.format(res.aic_min_order))
    model = SARIMAX(stationSeries[d],
                        order=(1,d,1),
                        seasonal_order=(0, 0, 0, 12),
                        enforce_stationarity=False,
                        enforce_invertibility=False)
    results = model.fit()
    p_values = results.pvalues
    t_values = results.tvalues
    resid = results.resid
    qljungbox, pval, qboxpierce, pvalbp=acorr_ljungbox(resid, boxpierce=True) #只有当参数boxpierce=True时, 才会输出Q统计量.
    print("qlb=")
    print(qljungbox[0:60])
    print("pval=")
    print(pval[0:60])
    print("t_values = ")
    print(t_values)
    print("p_value = ")
    print(p_values)
    paraSign = paraSignf(p_values)
    modlSign = modlSignf(pval)
    print(paraSign)
    print(modlSign)
    if paraSign and modlSign:
        exitSimModel = True

    if exitSimModel:
        print("存在合适的拟合模型！")
        return isSimModel,model
    else:
        print("没有合适的拟合模型！")
        return isSimModel,None

def isWN(ts):
    qljungbox, pval, qboxpierce, pvalbp=acorr_ljungbox(ts, boxpierce=True) #只有当参数boxpierce=True时, 才会输出Q统计量.
    print(qljungbox)
    print(pval)
    return  not(modlSignf(pval))


if __name__ == "__main__":


    file = '../autoTSA/tsa_data.csv'
    index = 'Date'

    y=loadData(file,index)
    isWhiteNoise =  isWN(y)

    isSim,model = findSimModel(y)

    if not isSim:
        comModel = autoTSA(y)
                           # pMIN=0,pMax=1,
                           # dMIN=1,dMax=2,
                           # qMIN=1,qMax=2,
                           # PMIN=1,PMax=2,
                           # DMIN=0,DMax=1,
                           # QMIN=0,QMax=1)
        comModel.fitModel(pdq=(0,1,1),spdq=(1,0,0,12))
        startTime = '2015-01-01'
        comModel.valFore(startTime)
        comModel.forecast(steps=5)



