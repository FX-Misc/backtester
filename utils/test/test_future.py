import unittest

from trading.futures_contract import FuturesContract


class TestFuture(unittest.TestCase):
    def test_future(self):
        future = FuturesContract('GC')
        pass
