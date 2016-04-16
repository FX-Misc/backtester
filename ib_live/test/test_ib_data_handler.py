import json
import time
import unittest
from queue import Queue
from trading.futures_contract import FuturesContract
from ib_live.ib_utils import create_ib_futures_contract
from ib_live.ib_data_handler import IBDataHandler

CONFIG = json.load(open('test_ib_config.json', 'r'))

class TestIBDataHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.products = [FuturesContract('GC', exp_year=2016, exp_month=6)]
        cls.data = IBDataHandler(cls.events, cls.products, CONFIG)
        while(cls.data.next_valid_order_id is -1):
            time.sleep(.1)

    def test_data_stream(self):
        time.sleep(1)
        last_tick = self.data.last_tick
        print last_tick
        self.assertGreaterEqual(last_tick['ask_price'], last_tick['bid_price'])
        self.assertLessEqual(last_tick['bid_price'], last_tick['ask_price'])
        for i in range(100):
            self.assertGreater(last_tick['ask_price'], last_tick['bid_price'])
            time.sleep(1)

if __name__ == "__main__":
    unittest.main()
