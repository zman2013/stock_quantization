#!/usr/bin/python3
# 模拟一支股票交易，看最终剩余多少资金

import time
import datetime

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# from trade import Account
# from stock import Stock

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')


# 参数
#
# ts_code	    str	    Y	证券代码
# pro_api	    str	    N	pro版api对象
# start_date	str	    N	开始日期 (格式：YYYYMMDD)
# end_date	    str	    N	结束日期 (格式：YYYYMMDD)
# asset	        str	    Y	资产类别：E股票 I沪深指数 C数字货币 F期货 O期权，默认E
# adj	        str	    N	复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None
# freq	        str	    Y	数据频度 ：1MIN表示1分钟（1/5/15/30/60分钟） D日线 ，默认D
# ma	        list	N	均线，支持任意合理int数值

# 返回值
#
# ts_code	    str	    TS指数代码
# trade_date	str	    交易日
# close	        float	收盘点位
# open	        float	开盘点位
# high	        float	最高点位
# low	        float	最低点位
# pre_close	    float	昨日收盘点
# change	    float	涨跌点
# pct_change	float	涨跌幅
# vol	        float	成交量（手）
# amount	    float	成交额（千元）
# 下载股票数据
def download(code, start_date=None, asset='E', adj=None):

    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

    file_path = '/tmp/' + code + '.csv'

    if start_date is None:
        start_date = datetime.date(today.year-delta_year, today.month, today.day)
        start_date_formatted = start_date.strftime('%Y%m%d')
        df = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        while today > start_date:
            start_date_formatted = start_date.strftime('%Y%m%d')
            end_date = datetime.date(start_date.year+delta_year, start_date.month, start_date.day)
            end_date_formatted = end_date.strftime('%Y%m%d')

            df2 = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted, end_date=end_date_formatted)
            if df is not None:
                df = df2.append(df, ignore_index=True)
            else:
                df = df2

            start_date = end_date

    df.set_index(df['trade_date'], inplace=True)
    df = df.sort_index(ascending=True)
    df.to_csv(file_path, index=False)


def download_stock(stock_code, start_date=None):
    download(stock_code, start_date, asset='E', adj='hfq')


def download_index(index_code, start_date=None):
    download(index_code, start_date, asset='I')


# download_stock(stock_code="000001.SZ", start_date="20070101")
# download_index(index_code="399001.SZ", start_date="19910101")
# download_index(index_code='000001.SH', start_date="19910101")