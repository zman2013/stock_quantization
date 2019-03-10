import time
import datetime

import pandas as pd

import json
import os
import sys

sys.path.append("../..")
import setting


dir_path = setting.root_dir + '/index/'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)


# 加载股票日线信息
def load_daily(index_code, start_date):
    df = None
    try:
        df = pd.read_csv(dir_path+index_code)
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
def save_daily(index_code, df):
    old_df = load_daily(index_code=index_code, start_date=None)
    if old_df is not None:
        df = df.append(old_df, ignore_index=True)

        # 排序
        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)
        df = df.sort_index(ascending=False)

        # 去重
        df = df.drop_duplicates(subset='trade_date', keep='first')

    file_path = dir_path + index_code
    df.to_csv(file_path, index=False)


# 加载股票日线信息
def load_pe(index_code, start_date=None):
    df = None
    try:
        df = pd.read_csv(dir_path+index_code+".pe")

        date_index = pd.to_datetime(df['searchDate'], format='%Y-%m-%d')
        df.set_index(date_index, inplace=True)

        # df['trade_date2'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))

    except Exception as e:
        print(e)
        print( 'load pe from file failed')

    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        for index in df.index:
            if index.date() > start_date:
                df.drop(index=index)

    if df is not None:
        df['trade_date'] = df['searchDate'].apply(str)
    return df


# 保存指数pe信息
def save_pe(index_code, df):
    # 加载已有数据
    pe_df = load_pe(index_code=index_code)
    # 新旧数据拼接
    pe_df = df.append(pe_df, ignore_index=True)
    # 去重
    pe_df = pe_df.drop_duplicates(subset='searchDate')
    # 排序
    date_index = pd.to_datetime(pe_df['searchDate'], format='%Y-%m-%d')
    pe_df.set_index(date_index, inplace=True)
    pe_df = pe_df.sort_index(ascending=False)
    # 写入文件
    file_path = dir_path + index_code + ".pe"
    pe_df.to_csv(file_path, index=False)
