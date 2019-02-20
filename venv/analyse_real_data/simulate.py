#!/usr/bin/python3
# 股票历史分析

import time
import datetime
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import *
import json
import matplotlib.dates as mdate

sys.path.append("..")
from trade import Account
from stock import Stock


# 分析股票，并进行交易
# index_df 需要按时间正排序
def analyse( index_df, buy_analyse_interval):
    stock = Stock()
    account = Account()
    stock_code = 'america'
    account.stock[stock_code] = stock

    # 买入日期、价格
    buy_date = []
    buy_index = []
    # 卖出日期、价格
    sell_date = []
    sell_index = []

    # 从最早时间点向后遍历股票，遇到关键点位就进行操作
    for index in range(len(index_df)-80, -1, -1):
        data = index_df.iloc[index]

        index_check_result = check_point(index, index_df, buy_analyse_interval)

        if index_check_result != 'hold':
            stock.sh_index_point = index_check_result

        if stock.sh_index_point == 'buy':
            # if vol != 0:
            buy_date.append(data['trade_date'])
            buy_index.append(data['close'])
            # 既然买入了就重置状态
            stock.sh_index_point = 'hold'
            # simulation
            vol = account.buy(stock_code, data['close'])
            if vol > 0:
                print("%s %s buy %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'],
                                                                    account.cash + account.stock[stock_code].vol * data[
                                                                        'close']))
        elif stock.sh_index_point == 'sell':
            # if vol != 0:
            sell_date.append(data['trade_date'])
            sell_index.append(data['close'])
            # 既然卖出了就重置状态
            stock.sh_index_point = 'hold'
            # simulation
            vol = account.sell(stock_code, data['close'])
            if vol > 0:
                if account.stock[stock_code].vol > 0:
                    print("%s %s sel %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash + account.stock[stock_code].vol * data['close']))
                else:
                    print("%s %s sel %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash ))
        # 给资产赋值
        index_df.iloc[index, -1] = account.cash + account.stock[stock_code].vol * data['close']

    return [buy_date, buy_index, sell_date, sell_index]


# 判断是否为关键点位：'buy' 'sell' 'hold'
def check_point(index, index_df, buy_analyse_interval):
    data = index_df[index: index + buy_analyse_interval]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    # 判断买入 1
    if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
        if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最高点就是今天
            # print( "max date %s price %0.2f, min date %s price %0.2f" % (max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close']))
            return 'buy'    # 买入

    # 判断买入 2
    # data = index_df[index: index + 20]
    #
    # max_line = data.loc[data['close'].idxmax()]
    # min_line = data.loc[data['close'].idxmin()]
    #
    # delta = (max_line['close'] - min_line['close']) / min_line['close']
    # if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
    #     if delta > 0.10:  # 20个交易日内，涨幅 > 10%
    #         if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
    #             return 'buy'

    # 判断卖出
    data = index_df[index : index+20]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
        if delta > 0.091:                                    # 20个交易日内，跌幅 > 7%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                return 'sell'

    # 判断卖出
    data = index_df[index: index + 120]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:  # 最高点在最低点之前
        if delta > 0.15:  # 120个交易日内，跌幅 > 15%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                return 'sell'

    # 不操作
    return 'hold'


def simulate(code):

    for buy_analyse_interval in range(18, 80):

        file_path = "/tmp/"+code

        index_df = pd.read_csv(filepath_or_buffer=file_path + ".csv")

        start_price = index_df.loc[0, 'close']
        end_price = index_df.loc[len(index_df)-1, 'close']

        index_df['zichan'] = 0
        index_df = index_df.sort_index(axis=0, ascending=False)
        analyse(index_df, buy_analyse_interval)

        index_df.to_csv(path_or_buf=file_path+"_calculated.csv")

        index_df = pd.read_csv(filepath_or_buffer=file_path+"_calculated.csv" )

        date_index = pd.to_datetime(index_df['trade_date'], format='%Y%m%d')
        index_df.set_index(date_index, inplace=True)

        index_df['close'] = index_df['close'] / start_price
        index_df['zichan'] = index_df['zichan'] / 1000

        print("buy_analyse_interval %d, stock increase: %0.2f, final shouyi: %0.2f" % (buy_analyse_interval, end_price/start_price, index_df['zichan'][0] ))

        # plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
        # # 设置图片大小，宽高
        # plt.rcParams['figure.figsize'] = (100.0, 6.0)
        #
        # fig1 = plt.figure(figsize=(100, 6))
        # ax1 = fig1.add_subplot(1, 1, 1)
        # ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d')) #设置时间标签显示格式
        #
        # plt.xticks(pd.date_range('1896-05-26', '2016-01-07', freq='5Y'))
        #
        # plot = index_df['close']
        # plot.plot(zorder=0, c='r', secondary_y=False, label='index', legend=True)
        # plot = index_df['zichan']
        # plot.plot(zorder=1, c='g', secondary_y=False, label='zichan', legend=True)
        #
        # plt.grid(linestyle='-.')
        # plt.legend(loc='upper left')
        # plt.show()

# simulate()
