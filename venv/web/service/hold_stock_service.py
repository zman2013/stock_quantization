import sys
import datetime
import traceback

from web.persistence import hold_stock_repo

from web.service import stock_service


# 获取持有的股票信息df
def get_hold_stock():
    return hold_stock_repo.load()


# 保存持有的股票df
def save_hold_stock(df):
    hold_stock_repo.save(df)


# 下载持有的股票信息
def download_hold_stock_info():
    hold_stock_df = get_hold_stock()

    download_info = []

    for index in range(0, len(hold_stock_df), 1):
        stock_code = hold_stock_df.iloc[index]['stock_code']
        try:
            stock_service.download_daily_df(stock_code)
            stock_service.download_pe_df(stock_code)
            download_info.append(stock_code + ' succeed')
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            download_info.append(stock_code + ' fail')

    return download_info

# 获取持有的所有股票的指标信息
def fetch_hold_stock_info():
    hold_stock_df = get_hold_stock()
    hold_stock_df['buy_date'] = hold_stock_df['buy_date'].apply(str)

    hold_stock_info = []

    for index in range(0, len(hold_stock_df), 1):
        line = hold_stock_df.iloc[index]
        try:
            stock_code = line['stock_code']
            stock_name = line['stock_name']
            buy_date = line['buy_date']

            [buy_price, pe_label, raise_percent, fall_percent, daily_label, buy_profit, today_price] = fetch_stock_info(stock_code, buy_date)

            tmp = stock_code.split('.')
            sina_code = tmp[1].lower()+tmp[0]

            stock_info = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'buy_date': buy_date,
                'buy_price': buy_price,
                'pe_label': pe_label,
                'raise_percent': raise_percent,
                'fall_percent': fall_percent,
                'daily_label': daily_label,
                'buy_profit': buy_profit,
                'today_price': today_price,
                'sina_code':sina_code
            }

            hold_stock_info.append(stock_info)
        except Exception as e:
            print(e)

    return hold_stock_info


# 获取单支股票的：pe警告、涨跌幅警告
def fetch_stock_info(stock_code, buy_date):
    # 最近三年
    delta_year = 3
    today = datetime.datetime.today().date()
    start_date = datetime.date(today.year - delta_year, today.month, today.day)
    start_date = start_date.strftime('%Y%m%d')

    # 买入日期
    buy_date = datetime.datetime.strptime(buy_date, '%Y%m%d').date()

    # pe
    stock_pe_df = stock_service.find_pe_df(stock_code, start_date)
    # 买入时pe
    buy_pe = stock_pe_df.loc[buy_date, 'pe']
    # 日线
    stock_daily_df = stock_service.find_stock_daily_price_df(stock_code, start_date)
    # 买入价
    buy_price = stock_daily_df.loc[buy_date, 'close']
    # 今日价格
    today_price = stock_daily_df.iloc[0]['close']

    # pe指标
    pe_label = compute_pe_label(stock_pe_df)

    # 股价120天涨跌幅
    # 从最低点涨多少，最低点日期
    [raise_percent, min_trade_date] = compute_raise_percent(stock_daily_df)

    # 从最高点跌多少，最高点日期
    [fall_percent, max_trade_date] = compute_fall_percent(stock_daily_df)

    # 日线指标
    daily_label = 'hold'
    if fall_percent < -20 and max_trade_date > min_trade_date:
        daily_label = 'sell'
    if raise_percent > 20 and max_trade_date < min_trade_date:
        daily_label = 'buy'

    # 买入后收益
    buy_profit = (today_price - buy_price) / buy_price * 100
    buy_profit = round(buy_profit, 2)

    return [buy_price, pe_label, raise_percent, fall_percent, daily_label, buy_profit, today_price]


# 计算pe指标
def compute_pe_label(stock_pe_df):
    data = stock_pe_df[0: 480]

    max_line = data.loc[data['pe'].idxmax()]
    min_line = data.loc[data['pe'].idxmin()]

    todayPE = data.iloc[0]

    maxMinDelta = max_line['pe'] - min_line['pe']
    todayMinDelta = todayPE['pe'] - min_line['pe']

    # 如果pe临近最高点的90%
    if todayMinDelta / maxMinDelta > 0.9:
        return 'sell'
    # 如果pe临近最低点的10%
    elif todayMinDelta / maxMinDelta < 0.1:
        return 'buy'
    else:
        return 'hold'


# 股价120天涨跌幅, 从最低点涨多少，返回日期
def compute_raise_percent(stock_daily_df):
    data = stock_daily_df[0: 120]

    min_line = data.loc[data['close'].idxmin()]

    trade_date = min_line['trade_date']
    trade_date = datetime.datetime.strptime(str(trade_date), '%Y%m%d').date()

    today_daily = data.iloc[0]['close']

    percent = (today_daily - min_line['close']) / min_line['close'] * 100
    return [round(percent, 2), trade_date]


# 股价120天涨跌幅, 从最高点降多少, 返回日期
def compute_fall_percent(stock_daily_df):
    data = stock_daily_df[0: 120]

    max_line = data.loc[data['close'].idxmax()]

    trade_date = max_line['trade_date']
    trade_date = datetime.datetime.strptime(str(trade_date), '%Y%m%d').date()

    today_daily = data.iloc[0]['close']

    percent = (today_daily - max_line['close']) / max_line['close'] * 100
    return [round(percent, 2), trade_date]


# stock_code = '600690.SH'
# buy_date = '20190104'
# stock_service.download_daily_df(stock_code)
# stock_service.download_pe_df(stock_code)
# fetch_stock_info(stock_code, buy_date)