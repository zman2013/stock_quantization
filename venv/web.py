import time

from flask import Flask
from flask import render_template
from flask import jsonify

import pandas as pd

import json

from finance_analysis import finance_analyse, analyse_chart, fetch_finance_data, \
    fetch_pe_df, fetch_stock_price_df
from analyse_index import analyse_index, fetch_index_df
from m2 import fetch_m2_df
from select_stock import load_good_stock_by_quarter

app = Flask(__name__)


# @app.route('/')
# def hello_world():
#     return 'Hello World!'

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/m2')
def m2Page():
    return render_template("m2.html")


@app.route('/select_by_quarter_inc_view')
def select_by_quarter_inc_view():
    return render_template("select_by_quarter_inc.html")


@app.route('/select_by_quarter_inc')
def select_by_quarter_inc():
    df = load_good_stock_by_quarter()

    jsonData = {}
    jsonData['data'] = json.loads(df.to_json(orient="records"))
    jsonData['dates'] = df.columns.values.tolist()[0:3]
    jsonData['dates'].reverse()

    return jsonify(jsonData)


@app.route('/stock_finance/<stock_code>')
def stock_finance(stock_code):

    context = {
        'stock_code': stock_code
    }

    return render_template("stock_finance.html", **context)


@app.route('/stock_analysis/<stock_code>')
def stock_analysis(stock_code):
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    df = finance_analyse(stock_code, start_date)
    json = fetch_finance_data(stock_code, df)

    return jsonify(json)


@app.route('/stock_analysis_chart/<stock_code>')
def stock_analysis_chart(stock_code):
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    df = finance_analyse(stock_code, start_date)
    pe_df = fetch_pe_df(stock_code, start_date)
    [stock_price_max_min_df, stock_price_df] = fetch_stock_price_df(stock_code, start_date)

    json = analyse_chart(df, pe_df, stock_price_df, stock_price_max_min_df)
    return jsonify(json)


@app.route('/stock_pe_chart/<stock_code>')
def stock_pe_chart(stock_code):
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    pe_df = fetch_pe_df(stock_code, start_date)

    pe_df.set_index(pe_df['trade_date'], inplace=True)
    pe_df = pe_df.transpose()
    pe_df = pe_df.sort_index(axis=1, ascending=False)
    pe_df = pe_df.loc['pe_ttm':'pe_ttm', :]

    jsonData = {'pe': {} }
    jsonData['pe']['dates'] = pe_df.columns.values.tolist()
    jsonData['pe']['data'] = []

    data = json.loads(pe_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = 'pe'
        tmp['data'] = d
        tmp['type'] = 'line'
        jsonData['pe']['data'].append( tmp )

    return jsonify(jsonData)


# m0 m1 m2 同比数据
@app.route('/m2_analyse_chart')
def m2_analyse_chart():
    m2_df = fetch_m2_df()

    # 指数数据
    index_df = fetch_index_df('000001.SH', '20060101')
    index_df['trade_date'] = index_df['trade_date'].apply(lambda x: str(x)[:6])
    index_df = index_df.groupby('trade_date').max().rename(columns={'close': 'max'})
    index_df = index_df.rename(columns={'max': '上证'})

    # 合并数据
    df = pd.merge(m2_df, index_df, left_index=True, right_index=True)
    df['M1同比-M2同比'] = df['M1同比'] - df['M2同比']

    df = df.transpose()
    df = df.sort_index(axis=1, ascending=False)

    if df.iloc[0, 0] == 0 and df.iloc[1, 0] == 0 and df.iloc[2, 0] == 0:
        df = df.drop(labels=df.columns[0], axis=1)

    # m2数据
    m2_df = df.loc[['M0同比', 'M1同比', 'M2同比', 'M1同比-M2同比'], :]

    jsonData = {'mx': {}, 'index': {}}
    jsonData['mx']['dates'] = m2_df.columns.values.tolist()
    jsonData['mx']['data'] = []

    m2_df.insert(0, '类目', m2_df.index)
    data = json.loads(m2_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = d[0]
        tmp['data'] = d[1:-1]
        tmp['type'] = 'line'
        jsonData['mx']['data'].append(tmp)

    # 指数数据
    index_df = df.loc[['上证'], :]

    jsonData['index']['dates'] = index_df.columns.values.tolist()
    jsonData['index']['data'] = []

    index_df.insert(0, '类目', index_df.index)
    data = json.loads(index_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = d[0]
        tmp['data'] = d[1:-1]
        tmp['type'] = 'line'
        tmp['yAxisIndex'] = 1
        jsonData['index']['data'].append(tmp)

    return jsonify(jsonData)


@app.route('/index_analyse_chart')
def index_analyse_chart():
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 1)
    start_date = start_year + '0101'
    [buy_date, buy_index, sell_date, sell_index, sh_index_df, sz_index_df] = analyse_index(start_date)

    sh_index_df.set_index(sh_index_df['trade_date'], inplace=True)
    sh_index_df = sh_index_df[['close']]
    sh_index_df = sh_index_df.transpose()
    sh_index_df = sh_index_df.sort_index(axis=1, ascending=False)

    sz_index_df.set_index(sz_index_df['trade_date'], inplace=True)
    sz_index_df = sz_index_df[['close']]
    sz_index_df = sz_index_df.transpose()
    sz_index_df = sz_index_df.sort_index(axis=1, ascending=False)

    jsonData = {'sh_index_history': {},
                'sz_index_history':{},
                'buy_point':{},
                'sell_point': {}}
    jsonData['sh_index_history']['dates'] = sh_index_df.columns.values.tolist()
    jsonData['sh_index_history']['data'] = []
    jsonData['sz_index_history']['data'] = []
    jsonData['buy_point']['data'] = []
    jsonData['sell_point']['data'] = []

    # 上证指数
    data = json.loads(sh_index_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '上证'
        tmp['data'] = d
        tmp['type'] = 'line'
        jsonData['sh_index_history']['data'].append( tmp )

    # 深成指数
    data = json.loads(sz_index_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '深成'
        tmp['data'] = d
        tmp['type'] = 'line'
        tmp['yAxisIndex'] = 1
        jsonData['sz_index_history']['data'].append(tmp)

    # 画点（买入、卖出）
    tmp = {}
    tmp['name'] = '买入'
    tmp['data'] = []
    for i in range(0, len(buy_date)):
        tmp['data'].append([str(buy_date[i]), buy_index[i]])
    tmp['type'] = 'scatter'
    tmp['itemStyle'] = {'normal': {'color': '#f00'}}
    tmp['symbolSize'] = 10
    jsonData['buy_point']['data'].append(tmp)
    # 画点（买入、卖出）
    tmp = {}
    tmp['name'] = '卖出'
    tmp['data'] = []
    for i in range(0, len(sell_date)):
        tmp['data'].append([str(sell_date[i]), sell_index[i]])
    tmp['type'] = 'scatter'
    tmp['itemStyle'] = {'normal': {'color': '#080'}}
    tmp['symbolSize'] = 10
    jsonData['sell_point']['data'].append(tmp)

    return jsonify(jsonData)


if __name__ == '__main__':
    app.run()