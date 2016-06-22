import unittest
import datetime as dt
from queue import Queue
from trading.futures_contract import FuturesContract
from backtest.backtest import CMEBacktest
from backtest.data_handler import CMEBacktestDataHandler
from backtest.execution_handler import CMEBacktestExecutionHandler
from strategies.buy_strategy_futures import BuyStrategy


class TestCMEBacktestDataHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.start_date = dt.datetime(year=2015, month=12, day=1)
        cls.end_date = dt.datetime(year=2015, month=12, day=2)
        cls.products = [FuturesContract('GC', exp_year=2016, exp_month=2)]
        cls.data = CMEBacktestDataHandler(cls.events, cls.products, cls.start_date, cls.end_date)
        cls.execution = CMEBacktestExecutionHandler(cls.events, cls.products)
        cls.strategy = BuyStrategy(cls.events, cls.data, cls.products)
        cls.backtest = CMEBacktest(cls.events, cls.strategy, cls.data, cls.execution, cls.start_date, cls.end_date)


    def test_run_backtest(self):
        self.backtest.run()
