import datetime as dt

class FuturesContract(object):
    def __init__(self, symbol, exp_year=None, exp_month=None, continuous=False):
        self.symbol = symbol
        self.exp_year = exp_year if exp_year is not None else dt.datetime.now().year
        self.exp_month = exp_month if exp_month is not None else dt.datetime.now().month