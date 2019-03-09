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
from simulation import repair_stock_data, fetch_stock_daily_price_df, fetch_index_daily_df

from index_data import load_sh_index_pe, load_sz_index_pe, calculate_warning_point

from service import hold_stock_service

from web import app
from flask import Blueprint

hold_stock_blueprint = Blueprint('hold_stock', __name__, url_prefix='/hold_stock')


@hold_stock_blueprint.route('/')
def home():
    return render_template("home.html")