import json
import time
import unittest
import datetime as dt
from queue import Queue
from trading.futures_contract import FuturesContract
from ib_live.ib_execution_handler import IBExecutionHandler
from ib_live.ib_utils import create_ib_futures_contract
from ib_live.ib_events import IBOrderEvent, IBFillEvent

CONFIG = json.load(open('test_ib_config.json', 'r'))

class TestIBExecutionHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.execution = IBExecutionHandler(cls.events, CONFIG)
        cls.contract = FuturesContract('GC', exp_year=2016, exp_month=6)
        while(cls.execution.next_valid_order_id is -1):
            time.sleep(.1)

    def test_process_order(self):
        contract = self.contract.ib_contract
        order_event = IBOrderEvent('GC', 1, 'MARKET', price=None, order_time=None)
        self.execution.process_new_order(order_event, contract)
        time.sleep(.5)
        fill = self.execution.fills.popleft()
        self.assertIsInstance(fill, IBFillEvent)
        self.assertIsNotNone(fill)
        self.assertEqual(fill.exchange, 'NYMEX')
        self.assertEqual(fill.symbol, 'GC')
        self.assertEqual(fill.quantity, 1)
        time.sleep(.5)

    def test_create_order(self):
        pass
