import time
import sys

from flask import Flask
from flask import render_template
from flask import jsonify

import json

from flask import Blueprint

from web.service import margin_service


margin_blueprint = Blueprint('margin', __name__, url_prefix='/margin')


@margin_blueprint.route('/view')
def view():
    return render_template("margin/view.html")


@margin_blueprint.route('/chart_json')
def info():
    margin_df = margin_service.load()

    margin_df.set_index(margin_df['trade_date'], inplace=True)

    jsonData = {'index': {}}
    jsonData['index']['data'] = []

    # 格式化指数数据
    index_df = margin_df[['close']]
    index_df = index_df.transpose()
    index_df = index_df.sort_index(axis=1, ascending=False)

    jsonData['index']['dates'] = index_df.columns.values.tolist()

    data = json.loads(index_df.to_json(orient="values"))
    tmp = {'name': '上证指数', 'data': data[0], 'type': 'line'}

    jsonData['index']['data'].append(tmp)

    # 格式融资融券数据
    margin_df = margin_df[['rzye', 'rqye', 'rzmre']]
    margin_df = margin_df.rename(columns={
        'rzye': '融资余额',
        'rqye': '融券余额',
        'rzmre': '融资买入额'
                            })
    margin_df = margin_df.transpose()
    margin_df = margin_df.sort_index(axis=1, ascending=False)
    # 添加标头:rzye/rqye/rzmre到第一列
    margin_df.insert(0, '类目', margin_df.index)

    data = json.loads(margin_df.to_json(orient="values"))
    for d in data:
        title = d[0]
        tmp = {'name': title, 'data': d[1:-1], 'type': 'line', 'yAxisIndex': 1}
        jsonData[title] = {'data': []}
        jsonData[title]['data'].append(tmp)

    return jsonify(jsonData)


@margin_blueprint.route('/download')
def download():
    result = margin_service.download()
    json_data = {
        'data': result
    }
    return jsonify(json_data)