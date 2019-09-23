#!/usr/bin/python3

import requests
import json
import traceback

import datetime

from pandas.io.json import json_normalize


# 获取基金数据
def download_fund_data():
    # 数据集合
    df = None

    try:
        # 转换格式
        # 沪深300
        url = "https://stock.pingan.com/omm/http/pss/searchByKey?key=沪深300&curPage=0&pageSize=100"
        # 中证500
        url = "https://stock.pingan.com/omm/http/pss/searchByKey?key=中证500&curPage=0&pageSize=100"
        # qdii
        url = "https://stock.pingan.com/omm/http/pss/searchByKey?key=qdii&curPage=0&pageSize=100"
        # 国债
        url = "https://stock.pingan.com/omm/http/pss/searchByKey?key=国债&curPage=0&pageSize=100"
        # 全部
        url = "https://stock.pingan.com/omm/http/pss/queryShelfPublic?curPage=1&pageSize=900"
        para = {}
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

        data = json.loads(r.text)['data']

        index = 0
        for fund in data:
            if index % 100 == 0:
                print("index: " + str(index))
            index = index + 1

            fund_code = fund['fundInfo']['code']
            fund_df = download_fund_detail(fund_code)

            if df is None:
                df = fund_df
            else:
                df = df.append(fund_df, ignore_index=True)

        df = df[['benchMark', 'name', 'purchaseFeeRule', 'redeemFeeRule', 'rebatePurchaseFee',
                 'managementfeeRatio', 'custodianfeeRatio', 'unitTotal', 'avgreturnYear', 'setupDate',
                 'firstInvestType']]
        # 重命名列名
        df = df.rename(columns={'benchMark': '基准比较',
                                'name': 'name',
                                'purchaseFeeRule': '购买费用',
                                'redeemFeeRule': '赎回费用',
                                'rebatePurchaseFee': '折扣购买费用',
                                'managementfeeRatio': '管理费率',
                                'custodianfeeRatio': '托管费率',
                                'unitTotal': '规模',
                                'avgreturnYear': '平均年收益',
                                'setupDate': '成立日期',
                                'firstInvestType': '类型'
                                })
    except Exception as e:
        print(e)
        traceback.print_exc()

    df.to_csv("~/Downloads/fund_data_all_2.csv", index=False)


# 获取基金详细数据
def download_fund_detail(fund_code):
    # 数据集合
    pe_df = None

    try:
        # 转换格式
        url = "https://stock.pingan.com/omm/http/pss/queryPublicDetail?code="+fund_code
        para = {}
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

        data = json.loads(r.text)

        df = json_normalize(data)

        return df
    except Exception as e:
        print('', e)
        traceback.print_exc()
        return None


download_fund_data()