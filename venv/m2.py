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

    # 必须分三步才能获取长时间的数据
    # 请求主页，获取JSESSIONID和u
    url = "http://data.stats.gov.cn/easyquery.htm"
    para = {'cn':'A01'}
    header = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'data.stats.gov.cn',
            'Upgrade-Insecure-Requests': '1',
            # 'Referer': 'http://data.stats.gov.cn/easyquery.htm?cn=A01',
            'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            # 'X-Requested-With': 'XMLHttpRequest'
    }
    print(url)
    print(header)
    print(para)
    r = requests.get(url, params=para, headers=header)
    print(r.status_code)
    print(r.headers)
    print(r.content)

    # 请求m2主页
    header['Cookie'] = 'JSESSIONID=' + r.cookies.get_dict()['JSESSIONID']+';u='+r.cookies.get_dict()['u']
    para = {'m': 'QueryData',
            'dbcode': 'hgyd',
            'rowcode': 'zb',
            'colcode': 'sj',
            'wds': '[]',
            'dfwds': '[{"wdcode":"zb","valuecode":"A0D01"}]',
            'k1': int(time.time()) * 1000}
    print(url)
    print(header)
    print(para)
    r = requests.post(url, params=para, headers=header)
    print(r.status_code)
    print(r.headers)
    print(r.content)

    # 请求长期的m2数据
    para = {'m': 'QueryData',
            'dbcode': 'hgyd',
            'rowcode': 'zb',
            'colcode': 'sj',
            'wds': '[]',
            'dfwds': '[{"wdcode":"sj","valuecode":"LAST160"}]',
            'k1': int(time.time()) * 1000}
    print(url)
    print(header)
    print(para)
    r = requests.get(url, params=para, headers=header)
    print(r.status_code)
    print(r.headers)
    print(r.content)

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

        if code == 'A0D0101_sj':    # 货币和准货币(M2)供应量_期末值(亿元)
            A1B0101_sj[date] = value
        elif code == 'A0D0102_sj':  # 货币和准货币(M2)供应量_同比增长(%)
            A1B0102_sj[date] = value
        elif code == 'A0D0103_sj':  # 货币(M1)供应量_期末值(亿元)
            A1B0103_sj[date] = value
        elif code == 'A0D0104_sj':  # 货币(M1)供应量_同比增长(%)
            A1B0104_sj[date] = value
        elif code == 'A0D0105_sj':  # 流通中现金(M0)供应量_期末值(亿元)
            A1B0105_sj[date] = value
        elif code == 'A0D0106_sj':  # 流通中现金(M0)供应量_同比增长(%)
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



# df = fetch_m2_df()
# print( df )
