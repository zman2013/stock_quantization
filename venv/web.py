import time

from flask import Flask
from flask import render_template
from flask import jsonify

import json

from finance_analysis import finance_analyse, analyse_chart, fetch_finance_data, fetch_pe_df, fetch_stock_price_df

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


if __name__ == '__main__':
    app.run()