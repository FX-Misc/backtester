import unittest
from data.stock import Stock


class TestStock(unittest.TestCase):
    def test_stock(self):
        stock = Stock('AAPL')
        self.assertEqual('AAPL', stock.symbol)
        self.assertEqual('Apple Inc.', stock.name)
        self.assertEqual('Consumer Goods', stock.sector)
