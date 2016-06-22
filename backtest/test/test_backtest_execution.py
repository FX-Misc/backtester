import unittest
import datetime as dt
from Queue import Queue
from trading.futures_contract import FuturesContract
from trading.events import OrderEvent
from backtest.execution_handler import CMEBacktestExecutionHandler


class TestCMEBacktestExecutionHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.products = [FuturesContract('GC', exp_year=2016, exp_month=2)]
        cls.execution = CMEBacktestExecutionHandler()

    def test_compare_dates(self):
        dt1 = dt.datetime(year=2015, month=10, day=10)
        dt2 = dt.datetime(year=2015, month=10, day=10)
        dt3 = dt.datetime(year=2015, month=9, day=10)
        self.assertTrue(CMEBacktestExecutionHandler.compare_dates(dt1, dt2))
        self.assertFalse(CMEBacktestExecutionHandler.compare_dates(dt1, dt3))

    def test_check_day_data(self):
        events = Queue()

        execution_handler = CMEBacktestExecutionHandler(events, self.products)
        order_dt = dt.datetime(year=2015, month=12, day=1, hour=8)
        execution_handler._check_day_data(order_dt)
        self.assertIsNotNone(execution_handler.curr_day_data)

        # test a new date for order
        order_dt = dt.datetime(year=2015, month=12, day=2, hour=8)
        execution_handler._check_day_data(order_dt)
        self.assertEqual(execution_handler.curr_day_data.iloc[0]['level_1_price_buy'], 45.02)

    def test_execute_order(self):
        symbols = ['CLF6', 'GCZ5']
        events = Queue()
        execution_handler = CMEBacktestExecutionHandler(events, symbols)
        order_dt = dt.datetime(year=2015, month=11, day=18)
        execution_handler._check_day_data(order_dt)
        order_event = OrderEvent('GCG6', order_dt, 'MARKET', 1)
        execution_handler.place_order(order_event)
