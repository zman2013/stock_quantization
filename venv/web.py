import time

from flask import Flask
from flask import render_template
from flask import jsonify

import json

from finance_analysis import finance_analyse, analyse_chart, fetch_finance_data, fetch_pe_df, fetch_stock_price_df
from analyse_index import analyse_index

app = Flask(__name__)


# @app.route('/')
# def hello_world():
#     return 'Hello World!'

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/stock_analysis')
def stock_analysis():
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    df = finance_analyse('000100.SZ', start_date)
    json = fetch_finance_data(df)

    return jsonify(json)


@app.route('/stock_analysis_chart')
def stock_analysis_chart():
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    df = finance_analyse('000100.SZ', start_date)
    pe_df = fetch_pe_df('000100.SZ', start_date)
    stock_price_df = fetch_stock_price_df('000100.SZ', start_date)

    json = analyse_chart(df, pe_df, stock_price_df)
    return jsonify(json)


@app.route('/stock_pe_chart')
def stock_pe_chart():
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    pe_df = fetch_pe_df('000100.SZ', start_date)

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
    jsonData['buy_point']['data'].append(tmp)
    # 画点（买入、卖出）
    tmp = {}
    tmp['name'] = '卖出'
    tmp['data'] = []
    for i in range(0, len(sell_date)):
        tmp['data'].append([str(sell_date[i]), sell_index[i]])
    tmp['type'] = 'scatter'
    jsonData['sell_point']['data'].append(tmp)

    return jsonify(jsonData)



if __name__ == '__main__':
    app.run()