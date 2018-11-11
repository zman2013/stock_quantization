#!/usr/bin/python3
# 财务分析

import time

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import *
import json

api = ts.pro_api('0a2415da6321725dec885fc0a46975dd3009c45ee1870e072c8d1865')


# 添加季度数据
def add_quarter_data(df, label):
    quarter_label = 'quarter_'+label
    df[quarter_label] = None
    for index, line in df.iterrows():
        # 计算每个季度的总收入
        if '0331' == line['end_date'][4:]:
            df.loc[index, quarter_label] = line[label]
        else:
            this_quarter = pd.Timestamp(line['end_date'])
            last_quarter = (this_quarter - QuarterEnd(n=1)).strftime("%Y%m%d")
            last_quarter_line = df[df.end_date == last_quarter].iloc[-1]
            df.loc[index, quarter_label] = line[label] - last_quarter_line[label]

        # print(line['end_date'], income_df.loc[index, quarter_label])


# 计算同比增长
def compute_yoy(df, label):
    start_year = df.iloc[-1]['end_date'][:4]
    yoy_label = 'yoy_' + label
    df[yoy_label] = None
    for index, line in df.iterrows():
        # 计算每个季度的总收入
        if start_year != line['end_date'][:4]:
            this_year = pd.Timestamp(line['end_date'])
            last_year = (this_year - DateOffset(years=1)).strftime("%Y%m%d")
            last_year_line = df[df.end_date == last_year].iloc[-1]
            df.loc[index, yoy_label] = (line[label] - last_year_line[label]) / last_year_line[label] * 100

            print(line['end_date'], "%0.2f%%" % df.loc[index, yoy_label] )


# 分析股票
def analyse(stock_code):

    this_year = int( time.strftime("%Y") )
    this_month = int( time.strftime("%M") )
    start_year = str(this_year-6)
    start_date = start_year + '0101'

    income_df = api.income(ts_code=stock_code, start_date=start_date)
    income_df.drop_duplicates(subset='end_date', keep = 'first', inplace = True)
    # balancesheet_df = api.balancesheet(ts_code=stock_code, start_date=start_date)
    # balancesheet_df.drop_duplicates(subset='end_date',keep = 'first', inplace = True)
    # cashflow_df = api.cashflow(ts_code=stock_code, start_date=start_date)
    # cashflow_df.drop_duplicates(subset='end_date',keep = 'first', inplace = True)

    # 补充单季度数据
    add_quarter_data(income_df, 'total_revenue')    # 营业总收入
    add_quarter_data(income_df, 'total_profit')     # 营业总利润
    add_quarter_data(income_df, 'n_income')         # 净利润

    print( 'quarter_total_revenue')
    compute_yoy(income_df, 'quarter_total_revenue')
    print( 'quarter_total_profit')
    compute_yoy(income_df, 'quarter_total_profit')
    print( 'quarter_n_income')
    compute_yoy(income_df, 'quarter_n_income')

    # 格式化数据
    income_df['end_date'] = income_df['end_date'].apply(lambda x: x[2:6])


    income_df.set_index(income_df['end_date'], inplace=True)
    income_df = income_df[['total_revenue', 'total_profit', 'n_income', 'yoy_quarter_total_revenue', 'yoy_quarter_total_profit', 'yoy_quarter_n_income']]
    income_df[['total_revenue', 'total_profit', 'n_income']] = income_df[['total_revenue', 'total_profit', 'n_income']] / 100000000
    income_df = income_df.fillna(value=0)
    income_df = income_df.round(2)
    income_df = income_df.rename(columns={'n_income': '净利润',
                                          'total_revenue':'营业总收入',
                                          'total_profit':'营业总利润',
                                          'yoy_quarter_total_revenue':'总收入季度增长率',
                                          'yoy_quarter_total_profit':'总利润季度增长率',
                                          'yoy_quarter_n_income':'净利润季度增长率'})
    income_df = income_df.transpose()
    income_df.insert(0, '类目', income_df.index)

    jsonData = {}
    jsonData['data'] = json.loads( income_df.to_json(orient="records") )
    jsonData['dates'] = income_df.columns.values.tolist()
    # for date in income_df.columns.values.tolist():
    #     jsonData['dates'].append(date[2:6])

    return jsonData


# 分析股票
def analyse_chart(stock_code):

    this_year = int( time.strftime("%Y") )
    this_month = int( time.strftime("%M") )
    start_year = str(this_year-6)
    start_date = start_year + '0101'

    income_df = api.income(ts_code=stock_code, start_date=start_date)
    income_df.drop_duplicates(subset='end_date', keep = 'first', inplace = True)
    balancesheet_df = api.balancesheet(ts_code=stock_code, start_date=start_date)
    balancesheet_df.drop_duplicates(subset='end_date',keep = 'first', inplace = True)
    cashflow_df = api.cashflow(ts_code=stock_code, start_date=start_date)
    cashflow_df.drop_duplicates(subset='end_date',keep = 'first', inplace = True)
    fina_indicator_df = api.fina_indicator(ts_code=stock_code, start_date=start_date)
    fina_indicator_df.drop_duplicates(subset='end_date', keep='first', inplace = True)

    df = pd.merge(income_df, balancesheet_df, on='end_date')
    df = pd.merge(df, cashflow_df, on='end_date')
    df = pd.merge(df, fina_indicator_df, on='end_date')

    # 格式化数据
    df['end_date'] = income_df['end_date'].apply(lambda x: x[2:6])
    df.set_index(income_df['end_date'], inplace=True)

    # 提取关注的财务信息
    # 'total_revenue':'营业总收入'
    # 'total_profit':'营业总利润'
    # 'n_income': '净利润'
    # q_gr_yoy : 营业总收入同比增长（单季）
    # q_op_yoy : 营业利润同比增长率
    # q_profit_yoy : 净利润同比增长率
    # roe : 净资产收益率
    # roe_dt : 净资产收益率(扣除非经常损益)
    # grossprofit_margin : 销售毛利率
    # debt_to_assets : 资产负债率
    # accounts_receiv : 应收账款
    # adv_receipts : 预收款项
    # inventories : 存货
    # n_cashflow_act : 经营活动产生的现金流量净额
    # n_cashflow_inv_act : 投资活动产生的现金流量净额
    # n_cash_flows_fnc_act : 筹资活动产生的现金流量净额
    # free_cashflow : 企业自由现金流量
    # rd_exp : 研发费用
    # rd_exp_per : 研发收入比

    df = df[['total_revenue', 'total_profit', 'n_income', 'q_gr_yoy', 'q_op_yoy', 'q_profit_yoy',
                           'roe', 'roe_dt', 'grossprofit_margin', 'debt_to_assets', 'accounts_receiv', 'adv_receipts',
                           'inventories', 'n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act', 'free_cashflow',
                           'rd_exp', ''
                           ]]
    df['rd_exp_per'] = df['rd_exp'] / df['total_revenue']
    df = df.fillna(value=0)
    df = df.round(2)
    df = df.rename(columns={'n_income': '净利润',
                            'total_revenue': '营业总收入',
                            'total_profit': '营业总利润',
                            'q_gr_yoy': '总收入季度增长率',
                            'q_op_yoy': '总利润季度增长率',
                            'q_profit_yoy': '净利润季度增长率',
    roe : 净资产收益率
    roe_dt : 净资产收益率(扣除非经常损益)
    grossprofit_margin : 销售毛利率
    debt_to_assets : 资产负债率
    accounts_receiv : 应收账款
    adv_receipts : 预收款项
    inventories : 存货
    n_cashflow_act : 经营活动产生的现金流量净额
    n_cashflow_inv_act : 投资活动产生的现金流量净额
    n_cash_flows_fnc_act : 筹资活动产生的现金流量净额
    free_cashflow : 企业自由现金流量
    rd_exp : 研发费用
    rd_exp_per : 研发收入比



                            })
    income_df = income_df.transpose()
    income_df.insert(0, '类目', income_df.index)

    jsonData = {}

    income_df = income_df['总收入季度增长率':'净利润季度增长率']
    jsonData['dates'] = income_df.columns.values.tolist()[1:-1]
    jsonData['data'] = []
    data = json.loads(income_df.to_json(orient="values"))

    for d in data:
        tmp = {}
        tmp['name'] = d[0]
        tmp['data'] = d[1:-1]
        tmp['type'] = 'line'
        jsonData['data'].append( tmp )

    return jsonData