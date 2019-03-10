import time
import datetime

import pandas as pd

import json
import os
import sys

sys.path.append("../..")
import setting


dir_path = setting.root_dir + '/stock/'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)


# 加载股票日线信息
def load_daily(stock_code, start_date):
    df = None
    try:
        df = pd.read_csv(dir_path+stock_code)
        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)

    except:
        print( 'load stock daily price from file failed')

    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        for index in df.index:
            if index.date() > start_date:
                df.drop(index=index)

    if df is not None:
        df['trade_date'] = df['trade_date'].apply(str)
    return df


# 保存股票日线信息
def save_daily(stock_code, df):
    old_df = load_daily(stock_code=stock_code, start_date=None)
    if old_df is not None:
        df = df.append(old_df)

        # 排序
        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)
        df = df.sort_index(ascending=False)

        # 去重
        df = df.drop_duplicates(subset='trade_date', keep='first')

    file_path = dir_path + stock_code
    df.to_csv(file_path, index=False)


# 加载股票日线信息
def load_pe(stock_code, start_date):
    df = None
    try:
        df = pd.read_csv(dir_path+stock_code+".pe")

        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)

        # df['trade_date2'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))

    except:
        print( 'load pe from file failed')

    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        for index in df.index:
            if index.date() > start_date:
                df.drop(index=index)

    if df is not None:
        df['trade_date'] = df['trade_date'].apply(str)
    return df


# 保存股票pe信息
def save_pe(stock_code, df):
    old_df = load_pe(stock_code=stock_code, start_date=None)
    if old_df is not None:
        df = df.append(old_df)
        # 去重
        df = df.drop_duplicates(subset='trade_date', keep='first')

    # 排序
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=False)

    file_path = dir_path+stock_code+".pe"
    df.to_csv(file_path, index=False)