#!/usr/bin/python3

import time
import datetime
import pandas as pd

import traceback

from setting import ts_api

from web.persistence import margin_repo
from web.service import index_service


# 获取融资融券数据
def load(start_date=None):
    print(time.time())
    margin_df = margin_repo.load(start_date)
    print(time.time())
    index_df = index_service.load_sh_index_df(start_date='20160101')
    print(time.time())
    # 标准化
    margin_df['rzye'] = margin_df['rzye'] / margin_df['rzye'].max() * 100
    margin_df['rqye'] = margin_df['rqye'] / margin_df['rqye'].max() * 100
    margin_df['rzmre'] = margin_df['rzmre'] / margin_df['rzmre'].max() * 100

    # 指数数据
    index_df['close'] = index_df['close'] / index_df['close'].max() * 100

    # 合并数据
    index_df.reset_index(drop=True, inplace=True)
    margin_df.reset_index(drop=True, inplace=True)
    margin_df = pd.merge(margin_df, index_df, on='trade_date')

    return margin_df


# 下载最近的融资融券数据，并保存
# 先加载已有的融资融券数据，从已有的数据最后一个时间点开始获取后续新的数据
def download():
    # 今天即结束时间
    today = datetime.datetime.today().date()
    # 起始日期
    margin_df = margin_repo.load(start_date=None)
    start_date = '20160101'
    if margin_df is not None:
        start_date = margin_df.iloc[0]['trade_date']
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()

    # 有效日期
    dates = index_service.load_available_dates()
    for date in dates:
        # 小于等于起始日志 => 忽略
        if date <= start_date:
            continue

        try:
            date = date.strftime('%Y%m%d')

            print('download margin data: ' + date)

            tmp_df = ts_api.query('margin', trade_date=date, exchange_id='SSE')
            if margin_df is None:
                margin_df = tmp_df
            else:
                margin_df = margin_df.append(tmp_df, ignore_index=True)
            # sleep 1秒
            time.sleep(1)


        except Exception as e:
            print(date, e)
            traceback.print_exc()

            # return 'fail'

    margin_repo.save(margin_df)

    return 'success'
