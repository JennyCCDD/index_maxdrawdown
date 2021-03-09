# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 10:16:05 2021

@author: Administrator
"""
import os
import sys
import numpy as np
import pandas as pd


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
    
    rt_series=rt_series.copy()
    rt_series=(rt_series+1).cumprod()
    maxdrawdown=((rt_series.cummax()-rt_series)/rt_series.cummax()).max().squeeze()
    enddate=((rt_series.cummax()-rt_series)/rt_series.cummax()).idxmax(axis=0).squeeze()
    stdate=rt_series.loc[:enddate,:].idxmax(axis=0).squeeze()
    return maxdrawdown,stdate,enddate

def annualreturn(rt_series=None):
    '''
    

    Parameters
    函数功能：计算组合年化收益率,默认月度年化，日频，242，月频：12 季频：4
    ----------
    rt_series : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''
    
    
    rt_series=rt_series.copy()
    rt_series=(1+rt_series).cumprod()
    ann_rt=(rt_series.iloc[-1,0]/rt_series.iloc[0,0])**(12/rt_series.shape[0])-1
    return ann_rt


def annstd(rt_series=None):
    '''
    

    Parameters
    ----------
    函数功能：实现计算组合的年化波动率，默认月度年化，日频，242，月频：12 季频：4
    rt_series : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''
    
    
    rt_series=rt_series.copy()
    rtstd=rt_series.std().squeeze()
    ann_std=rtstd*np.sqrt(12)
    return ann_std

def turnover_rate(weight=None):
    '''
    

    Parameters
    ----------
    函数功能:计算组合每期换手率
    weight : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''
    
    
    weight=weight.copy()
    weight.fillna(0,inplace=True)
    temp=(weight.T/weight.sum(axis=1)).T.fillna(0)
    turnoverrate=(temp-temp.shift(1,axis=0)).abs().sum(axis=1)/2
    return turnoverrate

def getportfolioret():
    '''
    

    Returns
    -------
    计算组合收益率、换手率、最大回撤、年化收益率、年化波动率、分年度收益率等
    None.

    '''
    
    
# =============================================================================
#     读入组合每期收益率数据、基准数据
# =============================================================================
    portfoliort=pd.read_csv(r"netvalue.csv",index_col=0,header=0,parse_dates=True)
    averagestylereturn=pd.read_csv(r"averagert.csv",index_col=0,header=0,parse_dates=True)
    pgindex=pd.read_csv(r'885001.csv',index_col=0,header=0,parse_dates=True)


# =============================================================================
# 组合收益计算
# =============================================================================
    allportfoliort=portfoliort.loc[:,["组合收益率"]].add(1).cumprod()
    allportfoliort["组合收益率-平均风格收益率"]=(portfoliort["组合收益率"]-averagestylereturn["平均风格收益率"]).add(1).cumprod()
    allportfoliort["组合收益率-偏股很合基金收益率"]=(portfoliort["组合收益率"]-pgindex["偏股混合基金收益率"]).add(1).cumprod()  
    allportfoliort["平均风格收益率"]=averagestylereturn["平均风格收益率"].add(1).cumprod()
    allportfoliort['pgindex']=pgindex["偏股混合基金收益率"].add(1).cumprod()
    allportfoliort.to_csv(r"组合历史绝对-相对收益率详细结果.csv",encoding='utf-8')

# =============================================================================
# 计算组合分年度收益率、最大回撤、年化波动、相对800信息比、绝对收益最大回撤、相对800最大回撤     
# =============================================================================
    porttoaverage=[]
    porttopg=[]
    yearlist=[str(year) for year in range(2009,2022)]+["全样本"]
    indicator1=['绝对收益','平均风格指数','相对平均风格超额','相对平均风格波动率','相对平均风格信息比','最大回撤','开始时间','结束时间','相对平均风格最大回撤','相对开始时间','相对结束时间']
    indicator2=['绝对收益','偏股混合基金指数','相对偏股混合基金超额','相对偏股混合基金波动率','相对偏股混合基金信息比','最大回撤','开始时间','结束时间','相对偏股混合基金最大回撤','相对开始时间','相对结束时间']
    for num,year in enumerate(yearlist):
        if year!='全样本':
            eq_portrt=annualreturn(portfoliort.loc[year,['组合收益率']])
            pgrt=annualreturn(averagestylereturn.loc[year,['平均风格收益率']])
            eq_excess800=annualreturn(allportfoliort.loc[year,['组合收益率-平均风格收益率']].pct_change().dropna(axis=0))
            eq_excess800std=annstd(allportfoliort.loc[year,['组合收益率-平均风格收益率']].pct_change().dropna(axis=0))
            eq_info800=eq_excess800/eq_excess800std
            eq_maxdrawdown,eq_sttime,eq_ettime=maxdropdown(portfoliort.loc[year,['组合收益率']])
            eq_800maxdrawdown,eq_800sttime,eq_800ettime=maxdropdown(allportfoliort.loc[year,['组合收益率-平均风格收益率']].pct_change().dropna(axis=0))
            marketwgt_portrt=annualreturn(pgindex.loc[year,['偏股混合基金收益率']])
            marketwgt_excess800=annualreturn(portfoliort.loc[year,['组合收益率-偏股很合基金收益率']].pct_change().dropna(axis=0))
            marketwgt_excess800std=annstd(allportfoliort.loc[year,['组合收益率-偏股很合基金收益率']].pct_change().dropna(axis=0))
            marketwgt_info800=marketwgt_excess800/marketwgt_excess800std
            marketwgt_800maxdrawdown,marketwgt_800sttime,marketwgt_800ettime=maxdropdown(allportfoliort.loc[year,['组合收益率-偏股很合基金收益率']].pct_change().dropna(axis=0))
            porttoaverage.append((eq_portrt,pgrt,eq_excess800,eq_excess800std,eq_info800,eq_maxdrawdown,eq_sttime,eq_ettime,eq_800maxdrawdown,eq_800sttime,eq_800ettime))
            porttopg.append((eq_portrt,marketwgt_portrt,marketwgt_excess800,marketwgt_excess800std,marketwgt_info800,eq_maxdrawdown,eq_sttime,eq_ettime,marketwgt_800maxdrawdown,marketwgt_800sttime,marketwgt_800ettime))
        else:
            eq_portrt=annualreturn(portfoliort.loc[:,['组合收益率']])
            pgrt=annualreturn(averagestylereturn.loc[:,['平均风格收益率']])
            eq_excess800=annualreturn(allportfoliort.loc[:,['组合收益率-平均风格收益率']].pct_change().dropna(axis=0))
            eq_excess800std=annstd(allportfoliort.loc[:,['组合收益率-平均风格收益率']].pct_change().dropna(axis=0))
            eq_info800=eq_excess800/eq_excess800std
            eq_maxdrawdown,eq_sttime,eq_ettime=maxdropdown(portfoliort.loc[:,['组合收益率']])
            eq_800maxdrawdown,eq_800sttime,eq_800ettime=maxdropdown(allportfoliort.loc[:,['组合收益率-平均风格收益率']].pct_change().dropna(axis=0))
            marketwgt_portrt=annualreturn(pgindex.loc[:,['偏股混合基金收益率']])
            marketwgt_excess800=annualreturn(portfoliort.loc[:,['组合收益率-偏股很合基金收益率']].pct_change().dropna(axis=0))
            marketwgt_excess800std=annstd(allportfoliort.loc[:,['组合收益率-偏股很合基金收益率']].pct_change().dropna(axis=0))
            marketwgt_info800=marketwgt_excess800/marketwgt_excess800std
            marketwgt_800maxdrawdown,marketwgt_800sttime,marketwgt_800ettime=maxdropdown(allportfoliort.loc[:,['组合收益率-偏股很合基金收益率']].pct_change().dropna(axis=0))
            porttoaverage.append((eq_portrt,pgrt,eq_excess800,eq_excess800std,eq_info800,eq_maxdrawdown,eq_sttime,eq_ettime,eq_800maxdrawdown,eq_800sttime,eq_800ettime))
            porttopg.append((eq_portrt,marketwgt_portrt,marketwgt_excess800,marketwgt_excess800std,marketwgt_info800,eq_maxdrawdown,eq_sttime,eq_ettime,marketwgt_800maxdrawdown,marketwgt_800sttime,marketwgt_800ettime))
    porttoaverage=pd.DataFrame(data=porttoaverage,index=yearlist,columns=indicator1)
    porttoaverage.to_csv(r'相对等权风格历史分年度表现.csv',encoding='utf-8')
    porttopg=pd.DataFrame(data=porttopg,index=yearlist,columns=indicator2)
    porttopg.to_csv(r'相对偏股混合历史分年度表现.csv',encoding='utf-8')