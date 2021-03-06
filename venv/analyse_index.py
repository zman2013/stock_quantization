#!/usr/bin/python3
# 模拟一支股票交易，看最终剩余多少资金

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from trade import Account
from stock import Stock

import time
import datetime

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')


# 下载股票数据
def download(code, start_date=None, asset='E', adj=None):

    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

    file_path = '/tmp/' + code + '.csv'

    if start_date is None:
        start_date = datetime.date(today.year - delta_year, today.month, today.day)
        start_date_formatted = start_date.strftime('%Y%m%d')
        df = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        while today > start_date:
            start_date_formatted = start_date.strftime('%Y%m%d')
            end_date = datetime.date(start_date.year + delta_year, start_date.month, start_date.day)
            end_date_formatted = end_date.strftime('%Y%m%d')

            df2 = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted,
                             end_date=end_date_formatted)
            if df is not None:
                df = df2.append(df, ignore_index=True)
            else:
                df = df2

            start_date = end_date

    df.to_csv(file_path, index=False)


def download_stock(stock_code, start_date=None):
    download(stock_code, start_date, asset='E', adj='hfq')


def download_index(index_code, start_date=None):
    download(index_code, start_date, asset='I')


# 分析股票，并进行交易
def analyse(sh_index_code, sz_index_code, sh_index_df, sz_index_df):
    stock = Stock()

    # 买入日期、价格
    buy_date = []
    buy_index = []
    # 卖出日期、价格
    sell_date = []
    sell_index = []

    # 从最早时间点向后遍历股票，遇到关键点位就进行操作
    for index in range(len(sh_index_df)-80, -1, -1):
        data = sh_index_df.iloc[index]

        sh_index_check_result = check_point( index, sh_index_df)
        sz_index_check_result = check_point( index, sz_index_df)

        if sh_index_check_result != 'hold':
            stock.sh_index_point = sh_index_check_result
        if sz_index_check_result != 'hold':
            stock.sz_index_point = sz_index_check_result

        if stock.sh_index_point == 'buy' and stock.sz_index_point == 'buy':
            # if vol != 0:
            buy_date.append(data['trade_date'])
            buy_index.append(data['close'])
            # 既然买入了就重置状态
            stock.sh_index_point = 'hold'
            stock.sz_index_point = 'hold'
        elif stock.sh_index_point == 'sell' and stock.sz_index_point == 'sell':
            # if vol != 0:
            sell_date.append(data['trade_date'])
            sell_index.append(data['close'])
            # 既然卖出了就重置状态
            stock.sh_index_point = 'hold'
            stock.sz_index_point = 'hold'

    return [buy_date, buy_index, sell_date, sell_index]


# 判断是否为关键点位：'buy' 'sell' 'hold'
def check_point(index, index_df):
    data = index_df[index: index + 18]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    # 判断买入
    if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
        if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最高点就是今天
            # print( "max date %s price %0.2f, min date %s price %0.2f" % (max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close']))
            return 'buy'    # 买入

    # 判断卖出 单日跌幅 > 3% from 上证日线，如果下跌趋势已成时（从最高最多下跌>5%），某日跌幅超过3%，接下来很可能继续跌
    data = index_df[index: index + 10]
    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]
    delta = (max_line['close'] - min_line['close']) / max_line['close']

    if delta > 0.05 and data.iloc[0]['pct_chg'] <= -3:
        return 'sell'

    # 判断卖出
    data = index_df[index : index+20]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
        if delta > 0.091:                                    # 跌幅 > 9.1%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                return 'sell'

    # 判断卖出
    data = index_df[index: index + 120]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:  # 最高点在最低点之前
        if delta > 0.15:  # 跌幅 > 6%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                return 'sell'

    # 不操作
    return 'hold'


# 画出指数历史曲线
def draw_index_history(stock_code):
    file_path = '/tmp/' + stock_code + '.csv'
    df = pd.read_csv(file_path)

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    plot = df['close']
    plot.plot(zorder=1, c='333', label='index', legend=True)


# 画出股票历史曲线
def draw_stock_price_history(stock_code):
    file_path = '/tmp/' + stock_code + '.csv'
    df = pd.read_csv(file_path)

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    plot = df['close']
    plot.plot(zorder=2, c='gray', secondary_y=True, label='stock', legend=True)


# 画出交易日期和价格
def draw_trade_point(buy_date, buy_price, sell_date, sell_price):
    # 画点 买入点
    data_date = [pd.to_datetime(d, format='%Y%m%d') for d in buy_date]
    plt.scatter(data_date, buy_price, s=3, c='r', label='buy', zorder=3)
    # 画点 卖出点
    data_date = [pd.to_datetime(d, format='%Y%m%d') for d in sell_date]
    plt.scatter(data_date, sell_price, s=3, c='g', label='sell', zorder=4)


# 读取股票数据
def read_data_frame(stock_code):
    file_path = '/tmp/' + stock_code + '.csv'
    stock_df = pd.read_csv(file_path)
    return stock_df


# 补全由于停牌引起的数据缺失
def repair_stock_data(stock_df, index_df):
    for index in range(0, len(index_df)):
        index_date = index_df.iloc[index]['trade_date']
        stock_date = stock_df.iloc[index]['trade_date']
        if index_date != stock_date:
            above = stock_df.loc[:index-1]
            blow  = stock_df.loc[index:]
            missing_line = stock_df.loc[index].copy()
            missing_line['trade_date'] = index_date
            stock_df = above.append(missing_line, ignore_index=True).append(blow, ignore_index=True)

    return stock_df


# 分析指数
def analyse_index(start_date):

    # 下载股票数据SH
    sh_index_code = '000001.SH' #上证
    sz_index_code = '399001.SZ' #深指

    download_index(sh_index_code, start_date)
    download_index(sz_index_code, start_date)

    sh_index_df = read_data_frame(sh_index_code)
    sz_index_df = read_data_frame(sz_index_code)

    [buy_date, buy_index, sell_date, sell_index] = analyse(sh_index_code, sz_index_code, sh_index_df, sz_index_df)

    sh_index_df = sh_index_df[['close', 'trade_date']]
    sz_index_df = sz_index_df[['close', 'trade_date']]
    return [buy_date, buy_index, sell_date, sell_index, sh_index_df, sz_index_df]


# 获取指数数据
def fetch_index_df(index_code, start_date):
    download_index(index_code, start_date)
    index_df = read_data_frame(index_code)

    return index_df


# 画图
def draw():
    # 下载股票数据SH
    sh_index_code = '000001.SH'  # 上证
    sz_index_code = '399001.SZ'  # 深指

    start_date = '20110601'
    [buy_date, buy_index, sell_date, sell_index] = analyse_index(start_date)

    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 设置图片大小，宽高
    plt.rcParams['figure.figsize'] = (30.0, 6.0)

    draw_index_history(sh_index_code)
    draw_index_history(sz_index_code)
    draw_trade_point(buy_date, buy_index, sell_date, sell_index)

    plt.legend(loc='upper left')
    plt.show()


# draw()