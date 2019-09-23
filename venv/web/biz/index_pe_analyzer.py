

# 计算卖出买入警告
def calculate_warning_point(pe_df):
    # 买入日期、价格
    buy_date = []
    buy_index = []
    # 卖出日期、价格
    sell_date = []
    sell_index = []

    # 从最早时间点向后遍历股票，遇到关键点位就进行操作
    for index in range(len(pe_df) - 480, -1, -1):
        data = pe_df.iloc[index]
        result = check_point(index, pe_df)
        if result == 'buy':
            buy_date.append(data['searchDate'])
            buy_index.append(0)
        elif result == 'sell':
            sell_date.append(data['searchDate'])
            sell_index.append(0)

    return [buy_date, buy_index, sell_date, sell_index]


# 计算卖出买入警告
def check_point(index, pe_df):

    # 判断卖出
    data = pe_df[index: index + 480]

    max_line = data.loc[data['profitRate'].idxmax()]
    min_line = data.loc[data['profitRate'].idxmin()]

    todayPE = data.iloc[0]

    maxMinDelta = max_line['profitRate'] - min_line['profitRate']
    todayMinDelta = todayPE['profitRate'] - min_line['profitRate']

    # 如果pe临近最高点的90%
    if todayMinDelta / maxMinDelta > 0.9:
        return 'sell'
    # 如果pe临近最低点的10%
    elif todayMinDelta / maxMinDelta < 0.1:
        return 'buy'
    else:
        return 'hold'
