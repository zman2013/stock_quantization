#!/usr/bin/python3
# 模拟一支股票交易，看最终剩余多少资金

import time
import datetime
import os

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from trade import Account
from stock import Stock

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')

dir_path = '/Users/zman/PycharmProjects/tushare/venv/data/index/'

# 下载股票数据
def download(code, start_date=None, asset='E', adj=None):
    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

    # mock一个时间
    # today = datetime.datetime.strptime("20000101", "%Y%m%d").date()

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

    df.set_index(df['trade_date'], inplace=True)
    df = df.sort_index(ascending=True)
    df.to_csv(file_path, index=False)


def download_stock(stock_code, start_date=None):
    download(stock_code, start_date, asset='E', adj='hfq')


def download_index(index_code, start_date=None):
    download(index_code, start_date, asset='I')


# 分析股票，并进行交易
def analyse(stock_code, sh_index_code, sz_index_code, stock_df, sh_index_df, sz_index_df):
    stock_df['zichan'] = 0
    account = Account()
    account.stock[stock_code] = Stock()
    account.cash = stock_df.iloc[-1]['close']

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
        stock_check_result = check_stock_point( index, stock_df)
        if sh_index_check_result != 'hold':
            account.stock[stock_code].sh_index_point = sh_index_check_result
        else:
            account.stock[stock_code].sh_index_point = 'hold'
        if sz_index_check_result != 'hold':
            account.stock[stock_code].sz_index_point = sz_index_check_result
        else:
            account.stock[stock_code].sz_index_point = 'hold'
        if stock_check_result != 'hold':
            account.stock[stock_code].stock_point = stock_check_result
        else:
            account.stock[stock_code].stock_point = stock_check_result

        stock = account.stock[stock_code]

        if (stock.sh_index_point == 'buy' and stock.sz_index_point == 'buy') :
            vol = account.buy(stock_code, data['close'])
            if vol != 0:
                buy_date.append(data['trade_date'])
                buy_price.append(data['close'])
                print("%s %s buy %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash + account.stock[stock_code].vol * data['close']))
        # elif (stock.sh_index_point == 'sell' and stock.sz_index_point == 'sell') or stock.stock_point == 'sell':
        elif stock.stock_point == 'sell' or stock.sh_index_point == 'sell':
            vol = account.sell(stock_code, data['close'])
            if vol != 0:
                sell_date.append(data['trade_date'])
                sell_price.append(data['close'])
                if account.stock[stock_code] != 0:
                    print("%s %s sel %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash + account.stock[stock_code].vol * data['close']))
                else:
                    print("%s %s sel %0.2f on price %0.2f, zichan %0.2f" % (data['trade_date'], stock_code, vol, data['close'], account.cash ))


        # 给资产赋值
        stock_df.iloc[index, -1] = account.cash + account.stock[stock_code].vol * data['close']
    return [account, buy_date, buy_price, sell_date, sell_price, stock_df]


# 可以动态调整买入卖出的时间间隔吗
# 判断是否为关键点位：'buy' 'sell' 'hold'
def check_point(index, index_df):
    data = index_df[index: index + 18]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
        if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最高点就是今天
            # print( "max date %s price %0.2f, min date %s price %0.2f" % (max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close']))
            return 'buy'    # 买入

    # 判断卖出 单日跌幅 > 3%
    if data.iloc[0]['pct_chg'] <= -6:
        return 'sell'

    # 判断卖出
    data = index_df[index : index+20]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
        if delta > 0.091:                                    # 跌幅 > 6%
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


# 检查股票是否卖出买入点位
# 判断是否为关键点位：'buy' 'sell' 'hold'
def check_stock_point(index, index_df):
    # data = index_df[index: index + 18]
    #
    # max_line = data.loc[data['close'].idxmax()]
    # min_line = data.loc[data['close'].idxmin()]
    #
    # if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
    #     if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最高点就是今天
    #         # print( "max date %s price %0.2f, min date %s price %0.2f" % (max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close']))
    #         return 'buy'    # 买入
    #
    # # 判断卖出 单日跌幅 > 3%
    # # if data.iloc[0]['pct_chg'] <= -9:
    # #     return 'sell'
    #
    # # 判断卖出
    # data = index_df[index : index+20]
    #
    # max_line = data.loc[data['close'].idxmax()]
    # min_line = data.loc[data['close'].idxmin()]
    #
    # delta = (max_line['close'] - min_line['close']) / max_line['close']
    # if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
    #     if delta > 0.09:                                    # 跌幅 > 6%
    #         if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
    #             return 'sell'

    # 判断卖出
    data = index_df[index: index + 120]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:  # 最高点在最低点之前
        if delta > 0.20:  # 跌幅 > 6%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                print("max date %s price %0.2f, min date %s price %0.2f, delta %0.2f" % ( max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close'], delta))
                return 'sell'

    # 不操作
    return 'hold'


# 画出指数历史曲线
def draw_index_history(stock_code, label, color):
    file_path = '/tmp/' + stock_code + '.csv'
    df = pd.read_csv(file_path)

    df['close'] = df['close'] / df['close'].max() * 100

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    plot = df['close']
    plot.plot(zorder=1, c=color, label=label, legend=True)


# 画出股票历史曲线
def draw_stock_price_history(stock_code):
    file_path = '/tmp/' + stock_code + '.csv'
    df = pd.read_csv(file_path)

    df['close'] = df['close'] / df['close'].max() * 100

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    plot = df['close']
    plot.plot(zorder=2, c='gray', secondary_y=False, label='stock', legend=True)


# 画出资产历史曲线
def draw_zichan(zichan_df):
    # 划线
    date_index = pd.to_datetime(zichan_df['trade_date'], format='%Y%m%d')
    zichan_df.set_index(date_index, inplace=True)
    zichan_df = zichan_df.sort_index(ascending=True)
    plot = zichan_df['zichan']
    plot.plot(zorder=2, c='y', label='zichan', legend=True)


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


# 获取股票日线
def fetch_stock_daily_price_df(stock_code, start_date):
    download_stock(stock_code, start_date)
    stock_df = read_data_frame(stock_code)
    return stock_df


# 获取股票日线
def fetch_index_daily_df(index_code, start_date):
    download_index(index_code, start_date)
    index_df = read_data_frame(index_code)
    return index_df


def simulate():
    # 下载股票数据SH
    # stock_code = '000651.SZ'    #格力
    stock_code = '600066.SH'    #宇通
    # stock_code = '601398.SH'    #工行
    # stock_code = '600104.SH'    #上汽
    # stock_code = '002624.SZ'
    # stock_code = '000905.SH'
    # stock_code = '000848.SZ'  #露露
    # stock_code = '300296.SZ'  #利亚德
    # stock_code = '000001.SH'
    # stock_code = '399001.SZ'
    # stock_code = '000100.SZ'  #TCL
    # stock_code = '600030.SH'   #中证
    # index_code = '000001.SH'
    sh_index_code = '000001.SH' #上证
    # sh_index_code = '399001.SZ' #深指
    # sz_index_code = '399001.SZ' #深指
    sz_index_code = '000001.SH' #上证
    # index_code = '399102.SZ' #创业板
    # start_date = '20060101'
    start_date = '20110101'
    download_stock(stock_code, start_date)
    download_index(sh_index_code, start_date)
    download_index(sz_index_code, start_date)

    # is_point = check_point('000001.SH', 80)
    stock_df = read_data_frame(stock_code)
    stock_df['close'] = stock_df['close']/stock_df['close'].max()*100
    sh_index_df = read_data_frame(sh_index_code)
    sh_index_df['close'] = sh_index_df['close'] / sh_index_df['close'].max() * 100
    sz_index_df = read_data_frame(sz_index_code)
    sz_index_df['close'] = sz_index_df['close'] / sz_index_df['close'].max() * 100
    # 补全由于停牌引起的数据缺失
    stock_df = repair_stock_data(stock_df, sh_index_df)
    # 排序
    stock_df = stock_df.sort_index(axis=0, ascending=False)
    sh_index_df = sh_index_df.sort_index(axis=0, ascending=False)
    sz_index_df = sz_index_df.sort_index(axis=0, ascending=False)

    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    # 设置图片大小，宽高
    plt.rcParams['figure.figsize'] = (30.0, 6.0)

    [account, buy_date, buy_price, sell_date, sell_price, zichan_df] = analyse(stock_code, sh_index_code, sz_index_code, stock_df, sh_index_df, sz_index_df)

    draw_index_history(sh_index_code, 'sh_index', '000')
    draw_index_history(sz_index_code, 'sz_index', '999')
    draw_stock_price_history(stock_code)
    draw_trade_point(buy_date, buy_price, sell_date, sell_price)
    draw_zichan(zichan_df)

    print( account.cash )

    plt.legend(loc='upper left')
    plt.show()

    print("shown")


# 画出开户历史数据：周级数据
def draw_stock_open_count():
    df = api.stk_account(start_date='20150101')
    print(df)
    date_index = pd.to_datetime(df['date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)


# 获取指数数据：天级数据
def fetch_index_sorted_history(start_date):
    index_code = "000001.SH"
    index_df = fetch_index_daily_df(index_code, start_date)
    index_df['close'] = index_df['close']/index_df['close'].max()*100
    date_index = pd.to_datetime(index_df['trade_date'], format='%Y%m%d')
    index_df.set_index(date_index, inplace=True)
    index_df = index_df.sort_index(ascending=True)
    return index_df


# 获取指数数据：周级数据
def extract_index_weekly_history(index_df, stock_open_count_df):
    df = pd.merge( stock_open_count_df, index_df, how='inner',
                   left_index=True, right_index=True)
    return df


def draw_account_open():
    # 获取旧数据
    account_old_df = api.stk_account_old(start_date='20080101', end_date='20150529')
    account_old_df['weekly_new'] = (account_old_df['new_sh'] + account_old_df['new_sz'])/10000
    for index, line in account_old_df.iterrows():
        # 20141229~0102
        account_old_df.loc[index, 'date'] = line['date'][0:4] + line['date'][9:]

    # 获取新数据
    stock_open_count_df = api.stk_account(start_date='20150101')

    # 拼接新旧数据
    # stock_open_count_df = stock_open_count_df.append(account_old_df, ignore_index=True)

    stock_open_count_df['weekly_new'] = stock_open_count_df['weekly_new']/stock_open_count_df['weekly_new'].max()*100
    date_index = pd.to_datetime(stock_open_count_df['date'], format='%Y%m%d')
    stock_open_count_df.set_index(date_index, inplace=True)
    stock_open_count_df = stock_open_count_df.sort_index(ascending=True)

    for index, line in stock_open_count_df.iterrows():
        print( line['date'], ' ', line['weekly_new'] )

    index_df = fetch_index_sorted_history(start_date='20080101')
    df = extract_index_weekly_history(index_df, stock_open_count_df)

    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    # 设置图片大小，宽高
    plt.rcParams['figure.figsize'] = (30.0, 6.0)
    # 画开户数
    plot = df['weekly_new']
    plot.plot(zorder=2, c='y', label='weekly_new', legend=True)
    # 画指数
    plot = df['close']
    plot.plot(zorder=2, c='r', label='index', legend=True)

    plt.legend(loc='upper left')
    plt.show()


# 北向、南向资金
def cash_flow():
    start_date = '20150101'
    # 获取资金数据
    df = None
    today = datetime.datetime.today().date()
    delta_year = 1

    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    while today > start_date:
        start_date_formatted = start_date.strftime('%Y%m%d')
        end_date = datetime.date(start_date.year + delta_year, start_date.month, start_date.day)
        end_date_formatted = end_date.strftime('%Y%m%d')

        df2 = api.moneyflow_hsgt(start_date=start_date_formatted, end_date=end_date_formatted)
        if df is not None:
            df = df2.append(df, ignore_index=True)
        else:
            df = df2

        start_date = end_date

    cash_df = df
    date_index = pd.to_datetime(cash_df['trade_date'], format='%Y%m%d')
    cash_df.set_index(date_index, inplace=True)
    cash_df = cash_df.sort_index(ascending=True)

    # 按周统计数据
    i = 0
    south_money = 0
    north_money = 0
    for index, line in cash_df.iterrows():
        south_money = south_money + line['south_money']
        north_money = north_money + line['north_money']
        if i < 4:
            cash_df.loc[index,'south_money'] = 0
            cash_df.loc[index, 'north_money'] = 0
            i = i+1
        else:
            i = 0
            cash_df.loc[index, 'south_money'] = south_money
            cash_df.loc[index, 'north_money'] = north_money
            south_money = 0
            north_money = 0

    # 标准化
    cash_df['north_money'] = cash_df['north_money'] / cash_df['north_money'].max() * 100
    cash_df['south_money'] = cash_df['south_money'] / cash_df['south_money'].max() * 100

    # 指数数据
    index_df = fetch_index_sorted_history(start_date='20150101')
    index_df['close'] = index_df['close'] / index_df['close'].max() * 100

    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 设置图片大小，宽高
    plt.rcParams['figure.figsize'] = (30.0, 6.0)
    # 画北向资金数
    # plot = cash_df['north_money']
    # plot.plot(zorder=2, c='y', label='north_money', legend=True)
    # 画南向资金
    plot = cash_df['south_money'] - cash_df['north_money']
    plot.plot(zorder=2, c='r', label='south_money', legend=True)
    # 画出指数
    plot = index_df['close']
    plot.plot(zorder=2, c='b', label='close', legend=True)

    plt.legend(loc='upper left')
    plt.show()


# 融资融券数据
def draw_margin():
    index_df = fetch_index_sorted_history(start_date='20190101')
    index_df['close'] = index_df['close'] / index_df['close'].max() * 100



    # download margin data
    margin_df = None
    for index, line in index_df.iterrows():
        trade_date = line['trade_date']
        tmp_df = api.query('margin', trade_date=trade_date, exchange_id='SSE')
        print( tmp_df )
        if margin_df is None:
            margin_df = tmp_df
        else:
            margin_df = margin_df.append( tmp_df, ignore_index=True)
        # sleep 1秒
        time.sleep(1)
    #

    file_path = dir_path + "/margin_df.csv"

    # 如果文件已经存在就加载旧数据，并和新数据合并去重后，再写入文件
    if os.path.exists(file_path):
        # 加载已有数据
        df = pd.read_csv(file_path)
        # 新旧数据拼接
        margin_df = df.append(margin_df)
        # 去重
        margin_df = margin_df.drop_duplicates(subset='trade_date')
        # 排序
        date_index = pd.to_datetime(margin_df['trade_date'], format='%Y-%m-%d')
        margin_df.set_index(date_index, inplace=True)
        margin_df = margin_df.sort_index(ascending=False)

    # 写入文件
    margin_df.to_csv(file_path, index=False)

    # 从文件读取融资数据
    margin_df = pd.read_csv(file_path)
    date_index = pd.to_datetime(margin_df['trade_date'], format='%Y%m%d')
    margin_df.set_index(date_index, inplace=True)
    margin_df = margin_df.sort_index(ascending=True)

    # 标准化
    margin_df['rzye'] = margin_df['rzye'] / margin_df['rzye'].max() * 100
    margin_df['rqye'] = margin_df['rqye'] / margin_df['rqye'].max() * 100
    margin_df['rzmre'] = margin_df['rzmre'] / margin_df['rzmre'].max() * 100

    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 设置图片大小，宽高
    plt.rcParams['figure.figsize'] = (30.0, 6.0)
    # 画融资余额
    plot = margin_df['rzye']
    plot.plot(zorder=2, c='y', label='rzye', legend=True)
    # 画融资买入额
    plot = margin_df['rzmre']
    plot.plot(zorder=2, c='g', label='rzmre', legend=True)
    # 画融券余额
    plot = margin_df['rqye']
    plot.plot(zorder=2, c='r', label='rqye', legend=True)
    # 画出指数
    plot = index_df['close']
    plot.plot(zorder=2, c='b', label='index', legend=True)

    plt.legend(loc='upper left')
    plt.show()

# 南向资金>北向资金，说明资金一直在流出A股，从15~17年可以看出，之前经历了暴跌，这种情形是慢牛
# 南向资金-北向资金 连续>4周资金量较以往凸起，并且跟随两周资金量暴跌，说明资金流出的差不多了，A股活跃度接下来会凉，从18年可以看出，这种情形是慢熊
# 牛熊转换比较明显，就看资金流向即可：
#     1. 第一阶段：资金一直净流向A股，这时A股是一个下跌的过程，等资金积累到一定量，A股活跃度上来，必定上涨。
#     2. 第二阶段：资金净流向A股降低，A股继续上涨
#     3. 第三阶段：资金净流向反转，开始撤离A股，此时A股活跃度开始下降，如果之前进入了疯牛，将进入疯熊市
#     4. 第四阶段：资金净持续流出，连续>4周资金量较以往凸起，并且跟随两周资金量暴跌，说明资金流出的差不多了，A股活跃度接下来会凉
#     5. goto 第一阶段，如此循环
# cash_flow()


# draw_account_open()


# 分为短期、长期
# 短期对应疯牛，主要关注什么时机卖出
# 1. 融资余额暴跌，牛转熊的信号，卖出
# 长期对应普通情况 m
# 1. 以半年期为时间单位，如果上升即为慢牛
# 2. 以半年期为时间单位，如果下降即为慢熊
draw_margin()