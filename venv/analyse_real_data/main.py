#!/usr/bin/python3
# 股票历史分析

import time
import datetime
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tseries.offsets import *
import json
import matplotlib.dates as mdate

from china_stock_data_download import download_stock, download_index
from simulate import simulate

sys.path.append("..")
from trade import Account
from stock import Stock


# 格力电器
stock_code = "000651.SZ"
download_stock(stock_code=stock_code, start_date="19960101")
simulate(stock_code)