#!/usr/bin/python3

# 因为使用后复权数据，允许买入小数个股票

from stock import Stock


# 初始资金
class Account:
    cash = 10000
    suggest_buy_times = 0
    suggest_sell_times = 0
    stock = {}

    # 全部现金买入股票
    def buy(self, stock_code, price):
        self.suggest_sell_times = 0
        self.suggest_buy_times += 1
        # 计算可用金钱
        if self.suggest_buy_times == 1:
            can_use_cash = self.cash
        else:
            can_use_cash = 0
        # 可买入数量
        pre_vol = can_use_cash / price
        # 如果股票已经存在
        if stock_code in self.stock:
            stock = self.stock[stock_code]
            stock.vol = stock.vol + pre_vol
        else:
            stock = Stock()
            stock.vol = pre_vol

        self.cash = self.cash - can_use_cash
        self.stock[stock_code] = stock

        return pre_vol

    # 卖出所有股票
    def sell(self, stock_code, price):
        self.suggest_buy_times = 0
        self.suggest_sell_times += 1

        # 计算可卖出数量
        if self.suggest_sell_times == 1:
            can_sell_vol = self.stock[stock_code].vol
        else:
            can_sell_vol = 0

        # 卖出
        if stock_code in self.stock:
            money = price * can_sell_vol
            self.cash += money

            self.stock[stock_code].vol -= can_sell_vol

            return can_sell_vol
        else:
            return 0




# account = Account()
#
# account.buy('000848.SH', 100)
# print( account.cash, ("%0.2f" % account.stock['000848.SH'].val))
# #
# account.sell("000848.SH", 50)
# print( account.cash, ": ", '000848.SH' in account.stock)