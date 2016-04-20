import json
import time
import unittest
import datetime as dt
from queue import Queue
from trading.events import OrderEvent
from trading.stock import Stock
from trading.futures_contract import FuturesContract
from ib_live.ib_execution_handler import IBExecutionHandler
from ib_live.ib_events import IBFillEvent

CONFIG = json.load(open('test_ib_config.json', 'r'))

class TestIBExecutionHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.execution = IBExecutionHandler(cls.events, CONFIG)
        cls.future = FuturesContract('GC', exp_year=2016, exp_month=6)
        cls.stock = Stock('AAPL')
        while cls.execution.next_valid_order_id is -1:
            time.sleep(.1)

    def test_process_new_order_future(self):
        order_event = OrderEvent(self.future , 1, 'MARKET', price=None, order_time=None)
        self.execution.process_new_order(order_event)
        time.sleep(.5)
        fill = self.execution.fills.popleft()
        self.assertIsInstance(fill, IBFillEvent)
        self.assertIsNotNone(fill)
        self.assertEqual(fill.exchange, 'NYMEX')
        self.assertEqual(fill.symbol, 'GC')
        self.assertEqual(fill.quantity, 1)
        time.sleep(.5)

    def test_process_new_order_stock(self):
        pass
        # order_event = OrderEvent('GC', 1, 'MARKET', price=None, order_time=None)
        # self.execution.process_new_order(order_event)
        # time.sleep(.5)
        # fill = self.execution.fills.popleft()
        # self.assertIsInstance(fill, IBFillEvent)
        # self.assertIsNotNone(fill)
        # self.assertEqual(fill.exchange, 'NYMEX')
        # self.assertEqual(fill.symbol, 'GC')
        # self.assertEqual(fill.quantity, 1)
        # time.sleep(.5)

    def test_create_order(self):
        pass
