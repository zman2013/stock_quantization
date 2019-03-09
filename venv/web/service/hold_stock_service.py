import sys

sys.path.append("..")
from persistence import hold_stock_repo


def get_hold_stock():
    return hold_stock_repo.find()


def save_hold_stock(df):
    hold_stock_repo.save(df)


def fetch_stock_info(stock_code, buy_date):
    start_date = '最近3年'
    stock_df = load_stock_df(stock_code, start_date)

    stock_pe_df = load_stock_pe_df(stock_code, start_date)

    