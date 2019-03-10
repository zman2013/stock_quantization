import time
import sys

from flask import Flask
from flask import render_template
from flask import jsonify

import pandas as pd

import json

from web import app
from flask import Blueprint

from web.service import hold_stock_service


hold_stock_blueprint = Blueprint('hold_stock', __name__, url_prefix='/hold_stock')


@hold_stock_blueprint.route('/view')
def view():
    return render_template("hold_stock/view.html")


@hold_stock_blueprint.route('/info')
def info():
    hold_stock_info_json = hold_stock_service.fetch_hold_stock_info()
    json_data = {
        'data': hold_stock_info_json
    }
    return jsonify(json_data)


@hold_stock_blueprint.route('/download')
def download():
    result = hold_stock_service.download_hold_stock_info()
    json_data = {
        'data': result
    }
    return jsonify(json_data)