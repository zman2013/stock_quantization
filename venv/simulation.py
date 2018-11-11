#!/usr/bin/python3
# 模拟一支股票交易，看最终剩余多少资金

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from trade import Account
from stock import Stock

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')

# 下载股票数据
def download(code, start_date=None, asset='E', adj=None):

    file_path = '/tmp/' + code + '.csv'

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
    if start_date is None:
        df = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date='20120101')
        df2 = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date='20060101', end_date='20120101')
        df = df.append(df2, ignore_index=True)
    else:
        if start_date > '20120101':
            df = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date=start_date)
        else:
            df = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date='20120101')
            df2 = ts.pro_bar(pro_api=api, ts_code=code, asset=asset, adj=adj, start_date=start_date, end_date='20120101')
            df = df.append(df2, ignore_index=True)

    df.to_csv(file_path, index=False)


def download_stock(stock_code, start_date=None):
    download(stock_code, start_date, asset='E', adj='hfq')


def download_index(index_code, start_date=None):
    download(index_code, start_date, asset='I')


# 分析股票，并进行交易
def analyse(stock_code, sh_index_code, sz_index_code, stock_df, sh_index_df, sz_index_df):
    account = Account()
    account.stock[stock_code] = Stock()

    # 买入日期、价格
    buy_date = []
    buy_price = []
    # 卖出日期、价格
    sell_date = []
    sell_price = []

    # 从最早时间点向后遍历股票，遇到关键点位就进行操作
    for index in range(len(stock_df)-80, 0, -1):
        data = stock_df.iloc[index]
        sh_index_check_result = check_point( index, sh_index_df)
        sz_index_check_result = check_point( index, sz_index_df)
        stock_check_result = check_point( index, stock_df)
        if sh_index_check_result != 'hold':
            account.stock[stock_code].sh_index_point = sh_index_check_result
        if sz_index_check_result != 'hold':
            account.stock[stock_code].sz_index_point = sz_index_check_result
        if stock_check_result != 'hold':
            account.stock[stock_code].stock_point = stock_check_result

        stock = account.stock[stock_code]

        if stock.sh_index_point == 'buy' and stock.sz_index_point == 'buy':
            vol = account.buy(stock_code, data['close'])
            # if vol != 0:
            buy_date.append(data['trade_date'])
            buy_price.append(data['close'])
            print("%s %s buy %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash + account.stock[stock_code].vol * data['close']))
        elif stock.sh_index_point == 'sell' and stock.sz_index_point == 'sell':
            vol = account.sell(stock_code, data['close'])
            # if vol != 0:
            sell_date.append(data['trade_date'])
            sell_price.append(data['close'])
            if account.stock[stock_code] != 0:
                print("%s %s sel %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash + account.stock[stock_code].vol * data['close']))
            else:
                print("%s %s sel %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash ))

    return [account, buy_date, buy_price, sell_date, sell_price]


# 判断是否为关键点位：'buy' 'sell' 'hold'
def check_point(index, index_df):
    data = index_df[index: index + 60]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
        if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最高点就是今天
            # print( "max date %s price %0.2f, min date %s price %0.2f" % (max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close']))
            return 'buy'    # 买入

    # 判断卖出
    data = index_df[index : index+20]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
        if delta > 0.07:                                    # 跌幅 > 6%
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


# 下载股票数据SH
stock_code = '600066.SH'    #宇通
# stock_code = '601398.SH'    #工行
# stock_code = '600104.SH'    #上汽
# stock_code = '002624.SZ'
# stock_code = '000905.SH'
# stock_code = '000848.SZ'
# stock_code = '300296.SZ'
# stock_code = '000001.SH'
# stock_code = '399001.SZ'
# index_code = '000001.SH'
sh_index_code = '000001.SH' #上证
# sh_index_code = '399001.SZ' #深指
sz_index_code = '399001.SZ' #深指
# sz_index_code = '000001.SH' #上证
# index_code = '399102.SZ' #创业板
# start_date = '20060101'
start_date = '20170601'
download_stock(stock_code, start_date)
download_index(sh_index_code, start_date)
download_index(sz_index_code, start_date)

# is_point = check_point('000001.SH', 80)
stock_df = read_data_frame(stock_code)
sh_index_df = read_data_frame(sh_index_code)
sz_index_df = read_data_frame(sz_index_code)
# 补全由于停牌引起的数据缺失
stock_df = repair_stock_data(stock_df, sh_index_df)

plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
# 设置图片大小，宽高
plt.rcParams['figure.figsize'] = (30.0, 6.0)

[account, buy_date, buy_price, sell_date, sell_price] = analyse(stock_code, sh_index_code, sz_index_code, stock_df, sh_index_df, sz_index_df)

draw_index_history(sh_index_code)
draw_index_history(sz_index_code)
draw_stock_price_history(stock_code)
draw_trade_point(buy_date, buy_price, sell_date, sell_price)

print( account.cash )

plt.legend(loc='upper left')
plt.show()