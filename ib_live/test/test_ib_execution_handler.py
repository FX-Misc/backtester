import json
import time
import unittest

from production.IB.ib_execution_handler import IBExecutionHandler
from production.IB.ib_utils import create_futures_contract
from queue import Queue

from ib_live.ib_events import IBOrderEvent, IBFillEvent

CONFIG = json.load(open('test_ib_config.json', 'r'))

class TestIBExecutionHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.execution = IBExecutionHandler(cls.events, CONFIG)
        while(cls.execution.next_valid_order_id is -1):
            time.sleep(.1)

    def test_process_order(self):
        contract = create_futures_contract('GC', exp_month=4, exp_year=2016)
        order_event = IBOrderEvent('GC', 'MARKET', 1, price=None)
        self.execution.process_order(order_event, contract)
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

if __name__ == "__main__":
    unittest.main()

