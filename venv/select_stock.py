#!/usr/bin/python3
# 根据财务筛选股票

import time

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import *
import json
from finance_analysis import add_quarter_data, compute_yoy

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')


# 最近四个季度营收、利润增速>10%
def select_by_quarter():
    df = api.stock_basic(exchange='', list_status='L', fields='ts_code,name,industry')

    # 获取近两年的数据
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 2)
    start_date = start_year + '0101'

    good_stocks = []

#     遍历每一个股票（即：每一行）
    for index, line in df.iterrows():
        ts_code = line['ts_code']
        try:
            time.sleep(1)
            income_df = analyse_income_df(ts_code, start_date)
            cashflow_df = analyse_cashflow(ts_code, start_date)

            # 判断前四条数据（即最近四个季度）：季度营收同比、季度利润增速都>10
            for income_df_index, income_df_line in income_df.iterrows():
                if income_df_line['yoy_quarter_total_revenue'] < 10 \
                        or income_df_line['yoy_quarter_total_profit'] < 10 \
                        or income_df_line['yoy_quarter_n_income'] < 10 \
                        or cashflow_df.loc[income_df_index, 'n_cashflow_act'] < 0:    # 经营现金流现金流为正
                    print("bad stock[%s]" % ts_code)
                    break
                if income_df_index == 3:
                    print("good stock[%s]" % ts_code)
                    with open('/tmp/select_by_quarter_good_stock_code.txt', mode='a+') as file:
                        file.write("%s\n" % ts_code)

                    stock_info = {}
                    stock_info['ts_code'] = ts_code
                    stock_info['name'] = line['name']
                    stock_info['industry'] = line['industry']
                    first_index = income_df.index[0]
                    second_index = income_df.index[1]
                    third_index = income_df.index[2]
                    date = income_df.loc[first_index, 'end_date']
                    stock_info[date] = "%0.1f%%" % income_df.loc[first_index, 'yoy_quarter_total_revenue']
                    date = income_df.loc[second_index, 'end_date']
                    stock_info[date] = "%0.1f%%" % income_df.loc[second_index, 'yoy_quarter_total_revenue']
                    date = income_df.loc[third_index, 'end_date']
                    stock_info[date] = "%0.1f%%" % income_df.loc[third_index, 'yoy_quarter_total_revenue']

                    # 获取pe
                    this_year = int(time.strftime("%Y"))
                    pe_start_date = str(this_year) + '0101'
                    pe_df = api.daily_basic(ts_code=ts_code, start_date=pe_start_date)
                    stock_info['pe'] = "%0.1f" % pe_df.loc[0, 'pe']

                    good_stocks.append(stock_info)

                    break
        except Exception as e:
            print("analyse stock[%s] failed" % ts_code)
            print("Unexpected error:", e)

    df = pd.DataFrame(good_stocks)

    df.to_csv("/tmp/good_stocks", index=False)

    return good_stocks


# 分析股票
def analyse_income_df(stock_code, start_date):
    income_df = api.income(ts_code=stock_code, start_date=start_date)
    income_df.drop_duplicates(subset='end_date', keep='first', inplace=True)

    # 补充单季度数据
    add_quarter_data(income_df, 'total_revenue')  # 营业总收入
    add_quarter_data(income_df, 'total_profit')  # 营业总利润
    add_quarter_data(income_df, 'n_income')  # 净利润

    compute_yoy(income_df, 'quarter_total_revenue')
    compute_yoy(income_df, 'quarter_total_profit')
    compute_yoy(income_df, 'quarter_n_income')

    return income_df


# 分析现金流
def analyse_cashflow(stock_code, start_date):
    cashflow_df = api.cashflow(ts_code=stock_code, start_date=start_date)
    cashflow_df.drop_duplicates(subset='end_date', keep='first', inplace=True)
    return cashflow_df


# 加载分析完成的股票
def load_good_stock_by_quarter():
    file_path = '/tmp/good_stocks'
    df = pd.read_csv(file_path)
    latest_quarter_label = df.columns[2]  # 最近一个季度
    df['latest_quarter_float'] = df[latest_quarter_label].apply(lambda value: float(value[:-2]))
    df = df.sort_values(by='latest_quarter_float', ascending=False)
    return df


good_stock = select_by_quarter()