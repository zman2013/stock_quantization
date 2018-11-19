import requests

import time

import tushare as ts
import pandas as pd
import numpy as np
import json


# 从国家统计局数据库获取m0 m1 m2的dataframe格式数据
def fetch_m2_df():
    df = pd.DataFrame({'A1B0101_sj': [],
                       'A1B0102_sj': [],
                       'A1B0103_sj': [],
                       'A1B0104_sj': [],
                       'A1B0105_sj': [],
                       'A1B0106_sj': [],
                       })

    url = "http://data.stats.gov.cn/easyquery.htm"
    para = {'m': 'QueryData',
            'dbcode': 'hgyd',
            'rowcode': 'zb',
            'colcode': 'sj',
            'wds': '[]',
            'dfwds': '[{"wdcode":"sj","valuecode":"LAST160"}]',
            'k1': 1542116142076}
    # cookie可能过期导致获取的数据不正确，此时重新在浏览器中获取新的cookie
    header = {
            'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
            'Accept - Encoding': 'gzip, deflate',
            'Accept - Language': 'zh - CN, zh;q = 0.9, en;q = 0.8, zh - TW;q = 0.7',
            'Cache - Control': 'max - age = 0',
            'Connection': 'keep - alive',
            'Cookie': 'u = 1;_trs_uv = jnltr7sr_6_i0kb;JSESSIONID = 25EA1139EFDEBD9007F38038B96C231F',
            'Host': 'data.stats.gov.cn',
            'Upgrade - Insecure - Requests': '1',
            'User - Agent': 'Mozilla / 5.0(Macintosh'
    }

    r = requests.get(url, params=para, headers=header)
    print(r.cookies.get_dict())

    A1B0101_sj = {}
    A1B0102_sj = {}
    A1B0103_sj = {}
    A1B0104_sj = {}
    A1B0105_sj = {}
    A1B0106_sj = {}

    for data in r.json()['returndata']['datanodes']:
        code = data['code']
        value = data['data']['data']

        [item, code, date] = code.split(".")

        if code == 'A1B0101_sj':
            A1B0101_sj[date] = value
        elif code == 'A1B0102_sj':
            A1B0102_sj[date] = value
        elif code == 'A1B0103_sj':
            A1B0103_sj[date] = value
        elif code == 'A1B0104_sj':
            A1B0104_sj[date] = value
        elif code == 'A1B0105_sj':
            A1B0105_sj[date] = value
        elif code == 'A1B0106_sj':
            A1B0106_sj[date] = value

    s1 = pd.Series(A1B0101_sj)
    s2 = pd.Series(A1B0102_sj)
    s3 = pd.Series(A1B0103_sj)
    s4 = pd.Series(A1B0104_sj)
    s5 = pd.Series(A1B0105_sj)
    s6 = pd.Series(A1B0106_sj)

    df1 = pd.DataFrame(s1, columns=['A1B0101_sj'])  # 货币和准货币(M2)供应量_期末值(亿元)
    df1 = df1.rename(columns={'A1B0101_sj': 'M2'})
    df2 = pd.DataFrame(s2, columns=['A1B0102_sj'])  # 货币和准货币(M2)供应量_同比增长(%)
    df2 = df2.rename(columns={'A1B0102_sj': 'M2同比'})
    df3 = pd.DataFrame(s3, columns=['A1B0103_sj'])  # 货币(M1)供应量_期末值(亿元)
    df3 = df3.rename(columns={'A1B0103_sj': 'M1'})
    df4 = pd.DataFrame(s4, columns=['A1B0104_sj'])  # 货币(M1)供应量_同比增长(%)
    df4 = df4.rename(columns={'A1B0104_sj': 'M1同比'})
    df5 = pd.DataFrame(s5, columns=['A1B0105_sj'])  # 流通中现金(M0)供应量_期末值(亿元)
    df5 = df5.rename(columns={'A1B0105_sj': 'M0'})
    df6 = pd.DataFrame(s6, columns=['A1B0106_sj'])  # 流通中现金(M0)供应量_同比增长(%)
    df6 = df6.rename(columns={'A1B0106_sj': 'M0同比'})

    df = pd.merge(df1, df2, left_index=True, right_index=True)
    df = pd.merge(df, df3, left_index=True, right_index=True)
    df = pd.merge(df, df4, left_index=True, right_index=True)
    df = pd.merge(df, df5, left_index=True, right_index=True)
    df = pd.merge(df, df6, left_index=True, right_index=True)

    return df



fetch_m2_df()
