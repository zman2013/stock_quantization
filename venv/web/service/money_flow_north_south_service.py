#!/usr/bin/python3

import datetime
import pandas as pd

import traceback

from setting import ts_api

from web.persistence import money_flow_north_south_repo
from web.service import index_service


# 获取资金流向周数据
def load_money_flow_weekly_df(start_date=None):
    cash_df = money_flow_north_south_repo.load(start_date)
    index_df = index_service.load_sh_index_df(start_date='20150101')

    # 按周统计数据
    i = 0
    south_money = 0
    north_money = 0
    for index, line in cash_df.iterrows():
        south_money = south_money + line['south_money']
        north_money = north_money + line['north_money']
        if i < 4:
            cash_df.loc[index, 'south_money'] = 0
            cash_df.loc[index, 'north_money'] = 0
            cash_df.loc[index, 'delta'] = 0
            i = i + 1
        else:
            i = 0
            cash_df.loc[index, 'south_money'] = south_money
            cash_df.loc[index, 'north_money'] = north_money
            cash_df.loc[index, 'delta'] = north_money - south_money
            south_money = 0
            north_money = 0

    # 标准化
    cash_df['north_money'] = cash_df['north_money'] / cash_df['north_money'].max() * 100
    cash_df['south_money'] = cash_df['south_money'] / cash_df['south_money'].max() * 100
    cash_df['delta'] = cash_df['delta'] / cash_df['delta'].max() * 100

    # 指数数据
    index_df['close'] = index_df['close'] / index_df['close'].max() * 100

    # 合并数据
    index_df.reset_index(drop=True, inplace=True)
    cash_df.reset_index(drop=True, inplace=True)
    cash_df = pd.merge(cash_df, index_df, on='trade_date')

    return cash_df


# 下载最近的资金流向数据，并保存
# 先加载已有的资金流向数据，从已有的数据最后一个时间点开始获取后续新的数据
def download():
    # 今天即结束时间
    today = datetime.datetime.today().date()
    # 起始日期
    money_flow_df = money_flow_north_south_repo.load(start_date=None)
    start_date = '20150101'
    if money_flow_df is not None:
        start_date = money_flow_df.iloc[0]['trade_date']
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    # 有效日期
    dates = index_service.load_available_dates()
    # 数据集合
    cash_df = None

    for date in dates:
        # 小于起始日志 => 忽略
        if date < start_date:
            continue

        try:

            # 获取资金数据
            df = None
            delta_year = 1

            while today > start_date:
                start_date_formatted = start_date.strftime('%Y%m%d')
                end_date = datetime.date(start_date.year + delta_year, start_date.month, start_date.day)
                end_date_formatted = end_date.strftime('%Y%m%d')

                df2 = ts_api.moneyflow_hsgt(start_date=start_date_formatted, end_date=end_date_formatted)
                if df is not None:
                    df = df2.append(df, ignore_index=True)
                else:
                    df = df2

                start_date = end_date

            cash_df = df
            date_index = pd.to_datetime(cash_df['trade_date'], format='%Y%m%d')
            cash_df.set_index(date_index, inplace=True)
            cash_df = cash_df.sort_index(ascending=False)

        except Exception as e:
            print(date, e)
            traceback.print_exc()

            return 'fail'

        break

    money_flow_north_south_repo.save(cash_df)

    return 'success'
