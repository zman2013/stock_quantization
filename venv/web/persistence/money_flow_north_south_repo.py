import datetime

import pandas as pd

import os
import sys

sys.path.append("../..")
import setting

# 目录
dir_path = setting.root_dir + '/money_flow_north_south/'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)

# 文件
file_path = dir_path + 'money_flow.history'

# 加载资金流向数据
def load(start_date):
    df = None
    try:
        df = pd.read_csv(file_path)
        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)

    except:
        print( 'load stock daily price from file failed')

    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        for index in df.index:
            if index.date() < start_date:
                df = df.drop(index=index)

    if df is not None:
        df['trade_date'] = df['trade_date'].apply(str)

        df = df.sort_index(ascending=False)

    return df


# 保存资金流向数据
def save(df):
    if df is None:
        return

    old_df = load(start_date=None)
    if old_df is not None:
        df = df.append(old_df)

    # 排序
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=False)

    # 去重
    df = df.drop_duplicates(subset='trade_date', keep='first')

    df.to_csv(file_path, index=False)
