#!/usr/bin/python3

import requests
import json

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from trade import Account
from stock import Stock

import time
import datetime
from pandas.tseries.offsets import *
import pandas as pd

from pandas.io.json import json_normalize

from web.persistence import index_repo
from web.service import index_service


# 获取sh index df
def load_sh_pe_df(start_date=None):
    df = index_repo.load_pe('000001.SH', start_date)
    return df


# 获取sz index df
def load_sz_pe_df(start_date=None):
    df = index_repo.load_pe('399001.SZ', start_date)
    return df


# 获取上证pe数据
def download_sh_pe(start_date):
    # 起始日期
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    # 有效日期
    dates = index_service.load_available_dates()
    # 数据集合
    pe_df = None

    for date in dates:
        # 小于起始日志 => 忽略
        if date < start_date:
            continue

        try:
            # 转换格式
            searchDate = date.strftime('%Y-%m-%d')

            url = "http://query.sse.com.cn/marketdata/tradedata/queryTradingByProdTypeData.do"
            # jsonCallBack=jsonpCallback69044&searchDate=2019-03-01&prodType=gp
            para = {'jsonCallBack': 'jsonpCallback23675',
                    'prodType': 'gp',
                    'searchDate': searchDate,
                    '_': 1552589155411}
            header = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'query.sse.com.cn',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'http://www.sse.com.cn/market/stockdata/overview/day/',
                'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            }

            r = requests.get(url, params=para, headers=header)

            jsonStr = r.text.replace("jsonpCallback23675", "").replace('(', '').replace(')', '')
            data = json.loads(jsonStr)
            df = json_normalize(data['result'][0])

            if pe_df is None:
                pe_df = df
            else:
                pe_df = pe_df.append(df)
        except Exception as e:
            print(date, e)

    index_repo.save_pe('000001.SH', pe_df)


# 获取深成pe数据
def download_sz_pe(start_date):
    # 起始日志
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    # 有效日志
    dates = index_service.load_available_dates()
    # 数据集合
    pe_df = None

    for date in dates:
        # 小于起始日志 => 忽略
        if date < start_date:
            continue

        try:
            # 转换格式
            searchDate = date.strftime('%Y-%m-%d')

            url = "http://www.szse.cn/api/report/ShowReport/data"
            # SHOWTYPE=JSON&CATALOGID=1803&TABKEY=tab1&txtQueryDate=2017-02-03&random=0.1924540432483206
            para = {'SHOWTYPE': 'JSON',
                    'CATALOGID': '1803',
                    'TABKEY': 'tab1',
                    'txtQueryDate': searchDate,
                    'random': 0.1924540432483206}
            header = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'www.szse.cn',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'http://www.szse.cn/market/stock/indicator/index.html',
                'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            }

            r = requests.get(url, params=para, headers=header)
            # 提取数据
            result = r.json()
            tradeAmount = result[0]['data'][11]['brsz'].replace(',', '')
            pe = result[0]['data'][13]['brsz']
            exchangeRate = result[0]['data'][14]['brsz']

            # 拼装数据
            data = {}
            data['trdAmt'] = tradeAmount
            data['profitRate'] = pe
            data['exchangeRate'] = exchangeRate
            data['searchDate'] = searchDate

            # 转换格式
            df = json_normalize(data)

            if pe_df is None:
                pe_df = df
            else:
                pe_df = pe_df.append(df)
        except Exception as e:
            print(date, e)

    index_repo.save_pe('399001.SZ', pe_df)
