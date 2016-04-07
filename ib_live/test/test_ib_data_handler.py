import json
import time
import unittest

from production.IB.ib_utils import create_futures_contract
from queue import Queue

from ib_live.ib_data_handler import IBDataHandler

CONFIG = json.load(open('test_ib_config.json', 'r'))

class TestIBDataHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = Queue()
        cls.data = IBDataHandler(cls.events, CONFIG)
        while(cls.data.next_valid_order_id is -1):
            time.sleep(.1)

    def test_data_stream(self):
        contract = create_futures_contract('GC', exp_month=4, exp_year=2016)
        self.data.connection.reqMarketDataType(3)
        self.data.connection.reqMktData(123456, contract, "", False)
        time.sleep(1)

        last_tick = self.data.last_tick
        self.assertGreater(last_tick['ask_price'], last_tick['bid_price'])

        for i in range(100):
            self.assertGreater(last_tick['ask_price'], last_tick['bid_price'])
            time.sleep(1)

if __name__ == "__main__":
    unittest.main()
