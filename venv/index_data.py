#!/usr/bin/python3

import requests
import json

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from trade import Account
from stock import Stock

import time
import datetime
from pandas.tseries.offsets import *
import pandas as pd

from pandas.io.json import json_normalize


api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')

dir_path = '/Users/zman/PycharmProjects/tushare/venv/data/index/'


# 下载股票数据
def download(code, start_date=None, asset='E', adj=None):

    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

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

    file_path = dir_path+code+'.csv'
    df.to_csv(file_path, index=False)


# 加载上证pe信息
def load_sh_index_pe():
    file_path = dir_path + 'sh_pe.csv'
    return pd.read_csv(file_path)


# 加载深成pe信息
def load_sz_index_pe():
    file_path = dir_path + 'sz_pe.csv'
    return pd.read_csv(file_path)


def download_index(index_code, start_date=None):
    download(index_code, start_date, asset='I')


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


# 读取指数数据
def load_index_from_file(stock_code):
    file_path = '/tmp/' + stock_code + '.csv'
    stock_df = pd.read_csv(file_path)
    return stock_df


# 读取上证指数数据
def load_sh_index_from_file():
    index_df = load_index_from_file('000001.SH')
    return index_df


# 读取深成指数数据
def load_sz_index_from_file():
    index_df = load_index_from_file('399001.SZ')
    return index_df


# 获取有效的交易日期列表
def load_available_dates():
    index_df = load_sh_index_from_file()
    dates = []
    for date in index_df['trade_date']:
        date = datetime.datetime.strptime(str(date), '%Y%m%d').date()
        dates.append(date)
    return dates


# 获取指数数据
def fetch_index_df(index_code, start_date):
    download_index(index_code, start_date)
    index_df = read_data_frame(index_code)

    return index_df


# 获取上证pe数据
def download_sh_pe_data(start_date):
    # 起始日志
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    # 有效日志
    dates = load_available_dates()
    # 数据集合
    pe_df = None

    for date in dates:
        # 小于起始日志 => 忽略
        if date < start_date:
            continue

        # 转换格式
        searchDate = date.strftime('%Y-%m-%d')

        url = "http://query.sse.com.cn/marketdata/tradedata/queryTradingByProdTypeData.do"
        # jsonCallBack=jsonpCallback69044&searchDate=2019-03-01&prodType=gp
        para = {'jsonCallBack': 'jsonpCallback23675',
                'prodType': 'gp',
                'searchDate': searchDate,
                '_': 1552589155411}
        header = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'query.sse.com.cn',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://www.sse.com.cn/market/stockdata/overview/day/',
            'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

        r = requests.get(url, params=para, headers=header)

        jsonStr = r.text.replace("jsonpCallback23675", "").replace('(', '').replace(')', '')
        data = json.loads(jsonStr)
        df = json_normalize(data['result'][0])

        if pe_df is None:
            pe_df = df
        else:
            pe_df = pe_df.append(df)

    # 写入文件
    file_path = dir_path + 'sh_pe.csv'
    pe_df.to_csv(file_path)


# 获取深成pe数据
def download_sz_pe_data(start_date):
    # 起始日志
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    # 有效日志
    dates = load_available_dates()
    # 数据集合
    pe_df = None

    for date in dates:
        # 小于起始日志 => 忽略
        if date < start_date:
            continue

        # 转换格式
        searchDate = date.strftime('%Y-%m-%d')

        url = "http://www.szse.cn/api/report/ShowReport/data"
        # SHOWTYPE=JSON&CATALOGID=1803&TABKEY=tab1&txtQueryDate=2017-02-03&random=0.1924540432483206
        para = {'SHOWTYPE': 'JSON',
                'CATALOGID': '1803',
                'TABKEY': 'tab1',
                'txtQueryDate': searchDate,
                'random': 0.1924540432483206}
        header = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.szse.cn',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://www.szse.cn/market/stock/indicator/index.html',
            'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

        r = requests.get(url, params=para, headers=header)
        # 提取数据
        result = r.json()
        tradeAmount = result[0]['data'][11]['brsz'].replace(',', '')
        pe = result[0]['data'][13]['brsz']
        exchangeRate = result[0]['data'][14]['brsz']

        # 拼装数据
        data = {}
        data['trdAmt'] = tradeAmount
        data['profitRate'] = pe
        data['exchangeRate'] = exchangeRate
        data['searchDate'] = searchDate

        # 转换格式
        df = json_normalize(data)

        if pe_df is None:
            pe_df = df
        else:
            pe_df = pe_df.append(df)

    # 写入文件
    file_path = dir_path + 'sz_pe.csv'
    pe_df.to_csv(file_path)


# 计算卖出买入警告
def calculate_warning_point(pe_df):
    # 买入日期、价格
    buy_date = []
    buy_index = []
    # 卖出日期、价格
    sell_date = []
    sell_index = []

    # 从最早时间点向后遍历股票，遇到关键点位就进行操作
    for index in range(len(pe_df) - 480, 0, -1):
        data = pe_df.iloc[index]
        result = check_point(index, pe_df)
        if result == 'buy':
            buy_date.append(data['searchDate'])
            buy_index.append(0)
        elif result == 'sell':
            sell_date.append(data['searchDate'])
            sell_index.append(0)

    return [buy_date, buy_index, sell_date, sell_index]


# 计算卖出买入警告
def check_point(index, pe_df):

    # 判断卖出
    data = pe_df[index: index + 480]

    max_line = data.loc[data['profitRate'].idxmax()]
    min_line = data.loc[data['profitRate'].idxmin()]

    todayPE = data.iloc[0]

    maxMinDelta = max_line['profitRate'] - min_line['profitRate']
    todayMinDelta = todayPE['profitRate'] - min_line['profitRate']

    # 如果pe临近最高点的90%
    if todayMinDelta / maxMinDelta > 0.9:
        return 'sell'
    # 如果pe临近最低点的10%
    elif todayMinDelta / maxMinDelta < 0.1:
        return 'buy'
    else:
        return 'hold'


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


# 画上证pe
def draw_sh_pe():
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 设置图片大小，宽高
    plt.rcParams['figure.figsize'] = (30.0, 6.0)

    sh_pe_df = load_sh_index_pe()

    date_index = pd.to_datetime(sh_pe_df['searchDate'], format='%Y-%m-%d')
    sh_pe_df.set_index(date_index, inplace=True)
    sh_pe_df = sh_pe_df.sort_index(ascending=True)
    # pe
    plot = sh_pe_df['profitRate']
    plot.plot(zorder=1, c='y', label='pe', legend=True)
    # 换手率
    # plot = sh_pe_df['exchangeRate']
    # plot.plot(zorder=1, c='r', label='exchangeRate', legend=True)
    # 成交金额
    # plot = sh_pe_df['trdAmt']
    # plot.plot(zorder=1, c='b', label='tradeAmount', legend=True)

    plt.legend(loc='upper left')
    plt.show()

# download_sh_pe_data('20160101')
# draw()
# download_index(index_code='000001.SH', start_date='20190301')
# dates = load_available_dates()
# draw_sh_pe()
# download_sz_pe_data('20160101')

calculate_warning_point(load_sh_index_pe())