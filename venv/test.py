import datetime, time
import pandas as pd

text = "600690.SH"
tmp = text.split(".")
print(tmp[1]+tmp[0])

delta_year = 5

today = datetime.datetime.today().date()

print(today.strftime('%Y%m%d'))

start_date = datetime.date(today.year - delta_year, today.month, today.day)
start_date_formatted = start_date.strftime('%Y%m%d')

day_delta = datetime.timedelta(days=-7)

today = datetime.datetime.today().date()

start_date = today + day_delta
start_date = start_date.strftime('%Y%m%d')

date = '20190101'
date = datetime.datetime.strptime(str(date), '%Y%m%d')
print(date)

date = '20190101'
date = pd.to_datetime(str(date), format='%Y%m%d')
print(date)

# 转为字符串
price = 12
price = str(12)
# 转为int
price = int(price)


# 转为字符串
price = 12
price = str(12)

# 转为int
price = int(price)

# 分割
text = "600690.SH"
tmp = text.split(".")
print(tmp[1]+tmp[0])

# 大小写
text = text.lower()
print( text )
text = text.upper()
print( text)

from pandas.tseries.offsets import *
today = '20190101'
today = pd.Timestamp(today)
this_quarter = (today - QuarterEnd(n=0))
print(this_quarter.strftime("%Y%m%d"))
last_quarter = (today - QuarterEnd(n=1))
print(last_quarter.strftime("%Y%m%d"))