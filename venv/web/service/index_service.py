import datetime

import tushare as ts

from web.persistence import index_repo

from setting import ts_api


# 获取sh index df
def load_sh_index_df(start_date):
    df = index_repo.load_daily('000001.SH', start_date)
    return df


# 获取sz index df
def load_sz_index_df(start_date):
    df = index_repo.load_daily('399001.SZ', start_date)
    return df


# 下载sh index并保存到本地
def download_sh_index(start_date=None):
    index_code = '000001.SH'
    df = download(index_code, start_date, asset='I')
    # df['trade_date'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))
    index_repo.save_daily(index_code, df)


# 下载sz index并保存到本地
def download_sz_index(start_date=None):
    index_code = '399001.SZ'
    df = download(index_code, start_date, asset='I')
    # df['trade_date'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))
    index_repo.save_daily(index_code, df)


# load_available_dates
def load_available_dates():
    index_df = load_sh_index_df(start_date=None)
    dates = []
    for date in index_df['trade_date']:
        date = datetime.datetime.strptime(str(date), '%Y%m%d').date()
        dates.append(date)
    return dates


# 下载tu_share日线数据
def download(code, start_date=None, asset='E', adj=None):

    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

    if start_date is None:
        start_date = datetime.date(today.year - delta_year, today.month, today.day)
        start_date_formatted = start_date.strftime('%Y%m%d')
        df = ts.pro_bar(pro_api=ts_api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        while today > start_date:
            start_date_formatted = start_date.strftime('%Y%m%d')
            end_date = datetime.date(start_date.year + delta_year, start_date.month, start_date.day)
            end_date_formatted = end_date.strftime('%Y%m%d')

            df2 = ts.pro_bar(pro_api=ts_api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted,
                             end_date=end_date_formatted)
            if df is not None:
                df = df2.append(df, ignore_index=True)
            else:
                df = df2

            start_date = end_date

    return df




# print( download_pe_df(stock_code='600690.SH', start_date='20190101'))