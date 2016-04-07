import unittest
from stock_backtest.data_handler import StockBacktestDataHandler

class TestStockDataHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        raise NotImplementedError("Daniel, implement this")

    def test_load_all_symbol_data(self):
        raise NotImplementedError("Daniel, implement this")

    def test_get_latest_data(self):
        raise NotImplementedError("Daniel, implement this")

    def test_update(self):
        raise NotImplementedError("Daniel, implement this")

    def test_update_edge_case_1(self):
        pass

    def test_get_latest_edge_case_1(self):
        pass

import datetime as dt
from Queue import Queue

if __name__ == "__main__":
    events = Queue()
    symbols = ['AAPL', 'FB']
    start_date = dt.datetime(year=2012, month=1, day=1)
    end_date = dt.datetime(year=2016, month=4, day=1)
    data_handler = StockBacktestDataHandler(events, symbols, start_date, end_date)

    data_handler.update()
    data_handler.update()

    foo = data_handler.get_latest()
