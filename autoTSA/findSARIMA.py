import warnings
import itertools
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import time
from statsmodels.sandbox.stats.diagnostic import acorr_ljungbox
plt.style.use('fivethirtyeight')

class autoTSA(object):

    def __init__(self,ts,
                 pMIN = 0,pMax = 2,
                 dMIN = 0,dMax = 2,
                 qMIN = 0,qMax = 2,
                 PMIN = 0,PMax = 2,
                 DMIN = 0,DMax = 2,
                 QMIN = 0,QMax = 2):
        '''
        初始化参数
        :param dataPath:数据文件路径以及文件名
        :param index:   数据索引名称
        :param PRANGE:  p的取值[0,PRANGE)
        :param DRANGE:  d的取值[0,DRANGE）
        :param QRANGE:  q的取值[0,QRANGE）
        '''

        self.pLeft = pMIN
        self.pRigt = PMax
        self.dLeft = dMIN
        self.dRigt = dMax
        self.qLeft = qMIN
        self.qRigt = qMax
        self.PLeft = PMIN
        self.PRigt = PMax
        self.DLeft = DMIN
        self.DRigt = DMax
        self.QLeft = QMIN
        self.QRigt = QMax
        self.log = open('./log.txt','w')
        self.log.truncate()
        self.y = ts
        self.model = 0

    # def lookData(self):
    #     '''
    #     显示数据时序图以及自相关图和偏置相关图
    #     :return:
    #     '''
    #
    #     self.log = open('./log.txt','a')
    #     startTime = time.time()
    #
    #     self.log.write("\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
    #     self.log.write("1- load data\n")
    #     data=pd.read_csv(self.dataPath,encoding='utf-8', index_col=self.index)
    #     data.index=pd.to_datetime(data.index)
    #     self.log.write('data type is :'+str(type(data))+'\n')
    #     y=data
    #     self.log.write('length of data:'+str(len(y))+'\n')
    #     y.plot(figsize=(16, 9))
    #     plt.savefig('./tsa1_data_ts')
    #     sm.graphics.tsa.plot_acf(y,lags = 40)
    #     plt.savefig('./tsa1_data_acf')
    #     sm.graphics.tsa.plot_pacf(y,lags = 40)
    #     plt.savefig('./tsa1_data_pacf')
    #
    #     endTime = time.time()
    #     self.log.write('This process costs {} seconds.\n'.format(endTime-startTime))
    #     self.log.close()

    def _genComb(self):
        '''
        产生pdq和PDQ的排列组合
        :return:
        '''
        self.log = open('./log.txt','a')
        startTime = time.time()

        self.log.write("\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
        self.log.write("3- generating the various combination of parameters\n")
        # Define the p, d and q parameters to take any value between 0 and 2

        p = range(self.pLeft,self.pRigt)
        d = range(self.dLeft,self.dRigt)
        q = range(self.qLeft,self.qRigt)
        P = range(self.PLeft,self.PRigt)
        D = range(self.DLeft,self.DRigt)
        Q = range(self.QLeft,self.QRigt)
        # Generate all different combinations of p, q and q triplets
        pdq = list(itertools.product(p, d, q))
        # Generate all different combinations of seasonal p, q and q triplets
        seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
        self.log.write("p : [{},{})\nd : [{},{})\nq : [{},{})\n".format(self.pLeft,self.pRigt,
                                                                        self.dLeft,self.dRigt,
                                                                        self.qLeft,self.qRigt))
        self.log.write("P : [{},{})\nD : [{},{})\nQ : [{},{})\n".format(self.PLeft,self.PRigt,
                                                                        self.DLeft,self.DRigt,
                                                                        self.QLeft,self.QRigt))
        endTime = time.time()
        self.log.close()
        return pdq,seasonal_pdq

    def _modlSignf(self,resid):
        qljungbox, pval, qboxpierce, pvalbp=acorr_ljungbox(resid, boxpierce=True) #只有当参数boxpierce=True时, 才会输出Q统计量.
        print("modlSinf =")
        print(qljungbox)
        print(pval)
        return min(pval) > 0.05

    def _paraSignf(self,modelResult):
        pvalues = modelResult.pvalues
        tvalues = modelResult.tvalues
        print("paraSignf=")
        print(pvalues)
        print(tvalues)
        return max(pvalues) < 0.05


    def _selePara(self,pdq,seasonal_pdq):
        '''
        模型定阶：根据AIC准则选出最佳的阶数
                同时记录下AIC最佳的前三组阶数
        :param pdq:
        :param seasonal_pdq:
        :return: 最佳的阶数
        '''

        self.log = open('./log.txt','a')
        startTime = time.time()

        self.log.write("\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
        self.log.write("4- iterates through combinations of parameters\n")
        warnings.filterwarnings("ignore") # specify to ignore warning messages
        aic_best = 9999.9
        aic_bter = 9999.9
        aic_good = 9999.9

        index = 0
        s_index = 0
        for param in pdq:
            s_index = 0
            for param_seasonal in seasonal_pdq:
                try:
                    mod = sm.tsa.statespace.SARIMAX(self.y,
                                                    order=param,
                                                    seasonal_order=param_seasonal,
                                                     enforce_stationarity=False,
                                                    enforce_invertibility=False)

                    results = mod.fit()
                    resid = results.resid
                    paraSignf = self._paraSignf(results)
                    modlSignf = self._modlSignf(resid)
                    if paraSignf and modlSignf:
                        if results.aic < aic_best:
                            aic_best = results.aic
                            a_best_index = index
                            a_best_sindex = s_index
                        elif results.aic < aic_bter:
                            aic_bter = results.aic
                            a_bter_index = index
                            a_bter_sindex = s_index
                        elif results.aic < aic_good:
                            aic_good = results.aic
                            a_good_index = index
                            a_good_sindex = s_index

                    # log.write(str(index)+'-'+str(s_index)+':ARIMA{}x{} - AIC:{}'.format(param, param_seasonal,results.aic)+'\n')

                    s_index += 1

                except:
                    # log.write(str(index)+'-'+str(s_index)+':ARIMA{}x{} - AIC:{}'.format(param, param_seasonal,999)+'\n')
                    s_index += 1
                    continue
            index += 1
        self.log.write("best : {} x {},AIC = {}".format(pdq[a_best_index],seasonal_pdq[a_best_sindex],aic_best)+'\n')
        self.log.write("bter : {} x {},AIC = {}".format(pdq[a_bter_index],seasonal_pdq[a_bter_sindex],aic_bter)+'\n')
        self.log.write("good : {} x {},AIC = {}".format(pdq[a_good_index],seasonal_pdq[a_good_sindex],aic_good)+'\n')

        endTime = time.time()
        self.log.write('This process costs {} seconds.\n'.format(endTime-startTime))
        self.log.close()
        return pdq[a_best_index],seasonal_pdq[a_good_sindex]

    def fitModel(self,pdq = '0',spdq = '0'):
        '''
        模型拟合。将拟合之后的模型放在 self.model
        :return:
        '''
        if pdq != '0' and spdq != '0':
            bestpdq,bestSpdq = pdq,spdq
        else:
            pdqList,seasonpdqList = self._genComb()
            bestpdq,bestSpdq = self._selePara(pdqList,seasonpdqList)

        self.log = open('./log.txt','a')
        startTime = time.time()
        self.log.write("\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
        self.log.write("5- Fit Model \n")
        mod = sm.tsa.statespace.SARIMAX(self.y,
                                order=tuple(bestpdq),
                                seasonal_order=tuple(bestSpdq),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
        results_AIC = mod.fit()
        resid = results_AIC.resid
        paraS = self._paraSignf(results_AIC)
        modlS = self._modlSignf(resid)
        self.log.write(str(results_AIC.summary().tables[0]))
        self.log.write("\n")
        self.log.write(str(results_AIC.summary().tables[1]))
        self.log.write("\n")
        self.log.write(str(results_AIC.summary().tables[2]))
        results_AIC.plot_diagnostics(figsize=(15, 12))
        plt.savefig('./tsa2_model_diagnostics_aic')
        self.model = results_AIC

        endTime = time.time()
        self.log.write('\nThis process costs {} seconds.\n'.format(endTime-startTime))
        self.log.close()

    def valFore(self,foreTime,dynamic = False):
        self.log = open('./log.txt','a')
        startTime = time.time()

        self.log.write("\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
        self.log.write("7- Validating Forecasts || dynamic={}\n".format(dynamic))
        if not self.model:
            self.log.write("No Model !\nPlease fit model first!\n")
            endTime = time.time()
            self.log.write('This process costs {} seconds.\n'.format(endTime-startTime))
            self.log.close()
            return

        pred = self.model.get_prediction(start=pd.to_datetime(foreTime), dynamic=dynamic)
        pred_ci = pred.conf_int()

        ax = self.y.plot(label='observed')
        pred.predicted_mean.plot(ax=ax, figsize=(16, 12),alpha=.7)#alpha 是透明度
        ax.fill_between(pred_ci.index,
                        pred_ci.iloc[:, 0],
                        pred_ci.iloc[:, 1], color='k', alpha=.2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Rate')
        plt.legend()
        plt.savefig('./tsa3_val_focat_dnmic={}'.format(dynamic))


        endTime = time.time()
        self.log.write('\nThis process costs {} seconds.\n'.format(endTime-startTime))
        self.log.close()

    def forecast(self,steps = 12):
        '''
        预测
        :param step:预测步数
        :return:
        '''
        self.log = open('./log.txt','a')
        startTime = time.time()
        self.log.write("\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
        self.log.write("8- Producing and Visualizing Forecasts\n")

        if not self.model:
            self.log.write("No Model !\nPlease fit model first!\n")
            endTime = time.time()
            self.log.write('This process costs {} seconds.\n'.format(endTime-startTime))
            self.log.close()
            return

        pred_uc = self.model.get_forecast(steps = steps)
        pred_ci = pred_uc.conf_int()
        ax = self.y.plot(label='observed', figsize=(16, 12))
        pred_uc.predicted_mean.plot(ax=ax, label='Forecast')

        self.log.write('\t\t\t\t'+str(len(pred_ci.iloc[:, 1]))+' step forecasts\n')
        self.log.write('==================================================\n')
        for i in range(len(pred_ci.iloc[:, 1])):
            self.log.write(str(i+1)+'\t')
            self.log.write(str(pred_uc.predicted_mean[i])+'\t')
            self.log.write(str(pred_ci.iloc[i, 0])+'\t')
            self.log.write(str(pred_ci.iloc[i, 1])+'\n')

        ax.fill_between(pred_ci.index,
                        pred_ci.iloc[:, 0],
                        pred_ci.iloc[:, 1], color='k', alpha=.25)
        ax.set_xlabel('Date')
        ax.set_ylabel('Rate')
        plt.legend()
        plt.savefig('./tsa4_forecast')
        endTime = time.time()
        self.log.write('This process costs {} seconds.\n'.format(endTime-startTime))
        self.log.close()

if __name__ == "__main__":
    dataPath= './tsa_data.csv'
    index = 'Date'
    sarima = autoTSA(dataPath,index)
    sarima.lookData()
    sarima.fitModel()
    sarima.forecast()
