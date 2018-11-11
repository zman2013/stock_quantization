import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from trade import Account

print(ts.__version__)

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')


# 指数分析
def index_analyse(stock_code, download=False):

    filePath = '/tmp/'+stock_code+'.csv'

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
    if download:
        df = ts.pro_bar(pro_api=api, ts_code=stock_code, asset='I', start_date='20120101')
        df2 = ts.pro_bar(pro_api=api, ts_code=stock_code, asset='I', start_date='20060101', end_date='20120101')

        df = df.append(df2, ignore_index=True)
        df.to_csv(filePath, index=False)

    df = pd.read_csv( filePath )

    trigger_date = set([])
    min_data = pd.DataFrame(columns=['trade_date', 'close'])

    # 寻找在20个交易日内，跌幅超过6%的点位
    for index in range( len(df)-20, 0, -1):
        data = df[index : index+20]
        pct_change = data['pct_change']

        max_line = data.loc[data['close'].idxmax()]
        min_line = data.loc[data['close'].idxmin()]

        delta = ( max_line['close'] - min_line['close'] ) / max_line['close']
        if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
            if delta > 0.06:                                    # 跌幅 > 6%
                if min_line['trade_date'] not in trigger_date:  # 之前没出现这个最低点
                    print( max_line['trade_date'], "%0.2f" % max_line['close'],
                           min_line['trade_date'], "%0.2f" % min_line['close'],
                           "   delta ", "%0.2f" % delta,
                           "  today pct_change ", "%0.2f" % min_line['pct_change'])

                    trigger_date.add( min_line['trade_date'] )

                    tmp = pd.DataFrame({ 'trade_date':[min_line['trade_date']],
                                       'close':[min_line['close']]})
                    min_data = min_data.append( tmp, ignore_index=True)

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    plot = df['close']
    plot.plot(zorder=1, c='gray')

    # 画点 卖出点
    min_data_date_index = [ pd.to_datetime(d, format='%Y%m%d') for d in min_data['trade_date'] ]
    plt.scatter(min_data_date_index, min_data['close'], s=3, c='g', label='sell', zorder=2)

    df = pd.read_csv(filePath)
    max_data = pd.DataFrame(columns=['trade_date', 'close'])
    # 寻找在70个交易日内，点位从最高点降到最低点后又回到最高点的的点位
    for index in range(len(df) - 80, 0, -1):
        data = df[index: index + 80]

        max_line = data.loc[data['close'].idxmax()]
        min_line = data.loc[data['close'].idxmin()]

        delta = (max_line['close'] - min_line['close']) / max_line['close']

        if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
            if max_line['trade_date'] == data.iloc[0]['trade_date']:    # 最高点就是今天
                print(max_line['trade_date'], "%0.2f" % max_line['close'],
                      min_line['trade_date'], "%0.2f" % min_line['close'],
                      "   delta ", "%0.2f" % delta,
                      "  today pct_change ", "%0.2f" % min_line['pct_change'])

                tmp = pd.DataFrame({'trade_date': [max_line['trade_date']],
                                    'close': [max_line['close']]})
                max_data = max_data.append(tmp, ignore_index=True)

    # 画点 买入点
    min_data_date_index = [pd.to_datetime(d, format='%Y%m%d') for d in max_data['trade_date']]
    plt.scatter(min_data_date_index, max_data['close'], s=3, c="r", marker='+', label="buy", zorder=3)


# 股价分析
def stock_analyse(stock_code, download=False):

    filePath = '/tmp/'+stock_code+'.csv'

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
    if download:
        df = ts.pro_bar(pro_api=api, ts_code=stock_code, asset='E', adj='hfq', start_date='20120101')
        df2 = ts.pro_bar(pro_api=api, ts_code=stock_code, asset='E', adj='hfq', start_date='20060101', end_date='20120101')

        df = df.append(df2, ignore_index=True)
        df.to_csv(filePath, index=False)

    df = pd.read_csv( filePath )

    trigger_date = set([])
    min_data = pd.DataFrame(columns=['trade_date', 'close'])

    # 寻找在20个交易日内，跌幅超过6%的点位
    for index in range( len(df)-20, 0, -1):
        data = df[index : index+20]
        pct_change = data['pct_change']

        max_line = data.loc[data['close'].idxmax()]
        min_line = data.loc[data['close'].idxmin()]

        delta = ( max_line['close'] - min_line['close'] ) / max_line['close']
        if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
            if delta > 0.06:                                    # 跌幅 > 6%
                if min_line['trade_date'] not in trigger_date:  # 之前没出现这个最低点
                    print( max_line['trade_date'], "%0.2f" % max_line['close'],
                           min_line['trade_date'], "%0.2f" % min_line['close'],
                           "   delta ", "%0.2f" % delta,
                           "  today pct_change ", "%0.2f" % min_line['pct_change'])

                    trigger_date.add( min_line['trade_date'] )

                    tmp = pd.DataFrame({ 'trade_date':[min_line['trade_date']],
                                       'close':[min_line['close']]})
                    min_data = min_data.append( tmp, ignore_index=True)

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    plot = df['close']
    plot.plot(zorder=1, c='gray')

    # 画点 卖出点
    min_data_date_index = [ pd.to_datetime(d, format='%Y%m%d') for d in min_data['trade_date'] ]
    plt.scatter(min_data_date_index, min_data['close'], s=3, c='g', label='sell', zorder=2)

    df = pd.read_csv(filePath)
    max_data = pd.DataFrame(columns=['trade_date', 'close'])
    # 寻找在70个交易日内，点位从最高点降到最低点后又回到最高点的的点位
    for index in range(len(df) - 80, 0, -1):
        data = df[index: index + 80]

        max_line = data.loc[data['close'].idxmax()]
        min_line = data.loc[data['close'].idxmin()]

        delta = (max_line['close'] - min_line['close']) / max_line['close']

        if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
            if max_line['trade_date'] == data.iloc[0]['trade_date']:    # 最高点就是今天
                print(max_line['trade_date'], "%0.2f" % max_line['close'],
                      min_line['trade_date'], "%0.2f" % min_line['close'],
                      "   delta ", "%0.2f" % delta,
                      "  today pct_change ", "%0.2f" % min_line['pct_change'])

                tmp = pd.DataFrame({'trade_date': [max_line['trade_date']],
                                    'close': [max_line['close']]})
                max_data = max_data.append(tmp, ignore_index=True)

    # 画点 买入点
    min_data_date_index = [pd.to_datetime(d, format='%Y%m%d') for d in max_data['trade_date']]
    plt.scatter(min_data_date_index, max_data['close'], s=3, c="r", marker='+', label="buy", zorder=3)


# 成交额曲线
def amount_line(stock_code):
    filePath = '/tmp/' + stock_code + '.csv'
    df = pd.read_csv(filePath)

    # 划线
    date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(date_index, inplace=True)
    df = df.sort_index(ascending=True)
    amount_plot = df['close']
    amount_plot.plot(label='close price', legend=True)

    vol_plot = df['amount']
    vol_plot.plot(secondary_y=True, label='trade amount', legend=True)


plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
# 设置图片大小，宽高
plt.rcParams['figure.figsize'] = (30.0, 6.0)

# stock_analyse('000848.SZ', False)
index_analyse('000001.SH', True)
# amount_line(stock_code='000001.SH')

plt.legend(loc='upper left')
plt.show()

account = Account()
print( account.cash )


