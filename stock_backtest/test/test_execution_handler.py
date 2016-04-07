import unittest
import datetime as dt
from Queue import Queue
from stock_backtest.events import StockBacktestOrderEvent
from stock_backtest.execution_handler import StockBacktestExecutionHandler

class TestStockBacktestExecutionHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.execution = StockBacktestExecutionHandler(cls.events)
        cls.symbol = 'AAPL'

    def test_process_order(self):
        # test market order
        order_dt = dt.datetime(year=2016, month=4, day=6)
        order = StockBacktestOrderEvent(order_dt, self.symbol, 'MARKET', 10)
        self.execution.process_order(order)
        raise NotImplementedError("Arvind, implement this")
        # test limit order

    def test_process_resting_orders(self):
        raise NotImplementedError("Arvind, implement this")