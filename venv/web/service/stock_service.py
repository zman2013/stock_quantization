import time
import datetime

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import *
import json
import sys

sys.path.append("..")
from persistence import stock_repo

sys.path.append("..")
from setting import ts_api


# 获取pe
def find_pe_df(stock_code, start_date):
    df = stock_repo.find_pe(stock_code, start_date)
    return df


# 获取股价日线
def find_stock_daily_price_df(stock_code, start_date):
    df = stock_repo.find_daily(stock_code, start_date)
    return df


# 下载股票pe并保存到本地
def download_pe_df(stock_code, start_date):
    df = ts_api.daily_basic(ts_code=stock_code, start_date=start_date)
    stock_repo.save_pe(stock_code, df)


# 下载股票日线图并保存到本地
def download_daily_df(stock_code, start_date=None):
    df = download(stock_code, start_date, asset='E', adj='hfq')
    stock_repo.save_daily(stock_code, df)


# 下载tu_share日线数据
def download(code, start_date=None, asset='E', adj=None):

    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

    if start_date is None:
        start_date = datetime.date(today.year - delta_year, today.month, today.day)
        start_date_formatted = start_date.strftime('%Y%m%d')
        df = ts.pro_bar(pro_api=ts_api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        while today > start_date:
            start_date_formatted = start_date.strftime('%Y%m%d')
            end_date = datetime.date(start_date.year + delta_year, start_date.month, start_date.day)
            end_date_formatted = end_date.strftime('%Y%m%d')

            df2 = ts.pro_bar(pro_api=ts_api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted,
                             end_date=end_date_formatted)
            if df is not None:
                df = df2.append(df, ignore_index=True)
            else:
                df = df2

            start_date = end_date

    return df


# print( download_pe_df(stock_code='600690.SH', start_date='20190101'))