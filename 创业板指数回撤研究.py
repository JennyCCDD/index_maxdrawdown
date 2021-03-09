# -*- coding: utf-8 -*-
"""
@author: Mengxuan Chen
@description:
# 课题需求，创业板指数（399006.SZ）上市以来回测
# 1.全量样本最大回撤分布、最大亏损分布
# 2.各估值分位数最大回撤分布
# 3.各指数点位区间最大回撤分布
# 4.当最大回撤达到20%/25%/30%/35%/40%时,指数在反弹至期初点位的概率及期限分布

@revise log:
    2021.03.08 创建程序
                完成1.2.3
    2021.03.09 完善1.2.3，完成4

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re,os
import warnings
import time
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False   # 步骤二（解决坐标轴负数的负号显示问题）


class Para():
    data_path = './data/'
    result_path = './result/'
    index = '399006.SZ'
    begin_date = '2010-06-01'
    end_date = '2021-03-08'
    win = 360
    maxddbound = 0.4
    pass



# In[]
def YearProcess(portfolio, period='all'):
    '''
    Splite the data by year for calculating
    :param portfolio: DataFrame
    :param period: period:str(all,2010-2015)
    :return: DataFrame
    '''
    if period == '2010':
        portfolio = portfolio[portfolio['Year'] == period]
    elif period == '2011':
        portfolio = portfolio[portfolio['Year'] == period]
    elif period == '2012':
        portfolio = portfolio[portfolio['Year'] == period]
    elif period == '2013':
        portfolio = portfolio[portfolio['Year'] == period]
    elif period == '2014':
        portfolio = portfolio[portfolio['Year'] == period]
    elif period == '2015':
        portfolio = portfolio[portfolio['Year'] == period]
    elif period == 'all':
        pass
    else:
        assert 0, "input period:all or 2010-2015"

    return portfolio


def maxdropdown(rt_series=None):
    '''


    Parameters
    ----------
    函数功能：计算最大回撤,返回最大回撤开始时间及结束时间
    rt_series : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''

    rt_series = rt_series.copy()
    rt_series = (rt_series + 1).cumprod()
    maxdrawdown = ((rt_series.cummax() - rt_series) / rt_series.cummax()).max()# .squeeze()
    enddate = ((rt_series.cummax() - rt_series) / rt_series.cummax()).idxmax(axis=0) #.squeeze()
    stdate = rt_series.loc[:enddate, :].idxmax(axis=0) #.squeeze()
    return maxdrawdown, stdate, enddate

def MaxDrawdown(portfolio,colname = 'close',period = 'all'):
    '''
    Calculate MDD
    :param portfolio: DataFrame
    :param colname: str
    :param period: str(all,2010-2015)
    :return:
    '''
    portfolio = YearProcess(portfolio,period=period)
    data = portfolio[colname].values
    end = np.argmax((np.maximum.accumulate(data) - data))
    if end == 0:
        return 0
    begin = np.argmax(data[:end])
    return ((data[begin] - data[end])/data[begin]), begin, end

def MaxLoss(portfolio,colname = 'close',period = 'all'):
    '''
    Calculate maxloss
    :param portfolio: DataFrame
    :param colname: str
    :param period: str(all,2010-2015)
    :return:
    '''
    portfolio = YearProcess(portfolio,period=period)
    data = portfolio[colname].values
    end = np.argmin(np.minimum.accumulate(data))
    begin = np.argmin(data[0])
    return (-1)*(data[end] - data[begin])/data[begin], begin, end

# print('全量样本最大回撤分布：','%.4f' % MaxDrawdown(portfolio,colname = para.index, period='all'))

def plot_distribution(dataA,dataB):
    fig, axes = plt.subplots(figsize=(20, 10),    # 图表区的大小
        facecolor='cornsilk',)    # 图表区的背景色
    plt.rcParams['font.size'] = 20
    plt.plot(dataA,dataB)
    plt.xlabel('日度最大回撤',fontproperties='SimHei')
    plt.ylabel('频次',fontproperties='SimHei')
    plt.title("创业板指最大回撤分布图",fontproperties='SimHei')
    plt.tight_layout()
    plt.savefig('创业板指最大回撤分布图.png')

# plot_distribution(portfolio.index,portfolio['最大回撤'])

def check_consecutive(lst):
    x=0
    for k in range(len(lst)-1):
        if lst[k+1]-lst[k] ==1:
             x += 1
    if x==len(lst):
        return True
    else:
        return False

def cal(df, fun = MaxDrawdown,window = 360):
    maxdd_list = []
    for i in range(len(df.index)):
        maxdd = fun(df.iloc[i:i+window], colname='close', period='all')
        maxdd_list.append(maxdd)
    df['group_max'] = maxdd_list
    return df



if __name__ == '__main__':
    para = Para()

    isExists = os.path.exists(para.data_path + para.index + '.csv')
    if not isExists:
        from WindPy import *
        w.start()
        close = w.wsd(para.index, "close", para.begin_date, para.end_date, "")
        pe_ttm = w.wsd(para.index, "pe_ttm", para.begin_date, para.end_date, "")

        close = pd.DataFrame(np.array(close.Data).T, columns=close.Codes, index=close.Times)
        pe_ttm = pd.DataFrame(np.array(pe_ttm.Data).T, columns=pe_ttm.Codes, index=pe_ttm.Times)
        datas = pd.concat([close, pe_ttm], axis=1)
        datas.columns = ['close', 'pe_ttm']
        datas['nav'] = datas['close'].apply(lambda x: x / datas['close'].iloc[0])
        # 标记年份
        year = []
        temp = datas.index.astype(str)
        for i in temp:
            year.append(datetime.strptime(i, "%Y-%m-%d").strftime("%Y"))
        datas['Year'] = year
        del temp
        # 标记百分比分位数比例
        section = []
        for i in range(len(datas.index)):
            section_i = datas.loc[:, 'close'].iloc[i] / max(datas['close']) * 10
            section.append(int(section_i) / 10)
        datas['percent'] = section
        # 标记pe_ttm分位数比例
        section_pe = []
        for i in range(len(datas.index)):
            section_pe_i = datas.loc[:, 'pe_ttm'].iloc[i] / max(datas['pe_ttm']) * 10
            section_pe.append(int(section_pe_i) / 10)
        datas['percent_pe'] = section_pe

        datas.reset_index(inplace=True)
        datas.reset_index(inplace=True)
        datas.columns = ['number', 'date', 'close', 'pe_ttm', 'nav', 'year', 'percent', 'percent_pe']

        # group打标签
        datas['group_percent'] = [0] * len(datas.index)
        group = 0
        for k in range(len(datas) - 1):
            if datas['percent'].iloc[k] != datas['percent'].iloc[k + 1]:
                group += 1
            datas['group_percent'].iloc[k + 1] = group

        datas['group_pe'] = [0] * len(datas.index)
        group_l = 0
        for l in range(len(datas) - 1):
            if datas['percent_pe'].iloc[l] != datas['percent_pe'].iloc[l + 1]:
                group_l += 1
            datas['group_pe'].iloc[l + 1] = group_l

        datas.to_csv(para.result_path + para.index + '.csv', encoding='utf8')
    else:
        datas = pd.read_csv(para.result_path + para.index + '.csv', index_col=0)

    # In[]
    # 1. 计算整个区间的反向最大回撤、反向最大亏损的分布

    maxdd_list = []
    maxdd_begin_list = []
    maxdd_end_list = []
    for i in range(len(datas.index)-1):
        maxdd,maxdd_begin,maxdd_end = MaxDrawdown(datas.iloc[i:],colname = 'close', period='all')
        maxdd_list.append(maxdd)
        maxdd_begin_list.append(maxdd_begin)
        maxdd_end_list.append(maxdd_end)
    maxdd_list.append(0)
    maxdd_begin_list.append(0)
    maxdd_end_list.append(0)
    datas['maxdd'] = maxdd_list
    datas['maxdd_begin'] = maxdd_begin_list
    datas['maxdd_end'] = maxdd_end_list
    datas['maxdd_time'] = datas.apply(lambda x: x['maxdd_end']-x['maxdd_begin'],axis=1)

    maxl_list = []
    for j in range(len(datas.index)):
        maxl,_,_  = MaxLoss(datas.iloc[j:],colname = 'close', period='all')
        maxl_list.append(maxl)
    datas['maxl'] = maxl_list


    # In[]
    # 2.3. 各估值分位数/指数点位分位数反向最大回撤分布, 反向最大亏损分布，360个交易日内
    maxdd_list_win = []
    maxl_list_win = []

    for i in range(len(datas.index)-1):
        maxdd,_,_  = MaxDrawdown(datas.iloc[i:i + para.win], colname='close', period='all')
        maxl,_,_  = MaxLoss(datas.iloc[i:i + para.win],colname = 'close', period='all')
        maxdd_list_win.append(maxdd)
        maxl_list_win.append(maxl)
    maxdd_list_win.append(0)
    maxl_list_win.append(0)
    datas['maxdd_group_%s'%para.win] = maxdd_list_win
    datas['maxl_group_%s'%para.win] = maxl_list_win

    datas_pe = datas.groupby(['group_pe']).apply(lambda x: x.iloc[-1])
    datas_percent = datas.groupby(['group_percent']).apply(lambda x: x.iloc[-1])


    # In[]
    # 4. 当反向最大回撤达到20%/25%/30%/35%/40%时,指数在反弹至期初点位的概率及期限分布
    datas4 = datas.copy(deep=True)

    datas4['maxdd_backtime_bound=%s'%para.maxddbound]=[0]*len(datas4)
    datas4['flag'] = [0]*len(datas4)
    datas4.loc[datas4['maxdd']>para.maxddbound]['flag'] = 1
    dates4 = datas4.loc[datas4['maxdd']>para.maxddbound,'number'].tolist()

    for date_i, index_i in enumerate(dates4):
        datas5 = datas4.iloc[index_i:]
        begin_index = int(datas5['close'].iloc[0])
        dates_begin = index_i
        dates_back = datas5.loc[(datas5['close']>begin_index)&
                                (datas5['close']<(1+begin_index))].number.values

        if len(dates_back) > 1:
            backtime = max(dates_back)-dates_begin
            datas4.loc[datas4['number'] ==  max(dates_back),'maxdd_backtime_bound=%s' % para.maxddbound] \
                = backtime

    datas4.to_csv(para.result_path+'datas4.csv',encoding='utf8')



