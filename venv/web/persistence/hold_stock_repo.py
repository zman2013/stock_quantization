import time

import pandas as pd

import json
import os
import sys

sys.path.append("../..")
import setting


dir_path = setting.root_dir + '/hold_stock'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)
file_path = setting.root_dir + '/hold_stock/list.csv'


# 加载持有的股票列表
def find():
    df = None
    try:
        df = pd.read_csv(file_path)
    except:
        print( 'load hold stock list from file failed')
    return df


# 输出持有的股票
def save(df):
    df.to_csv(file_path)