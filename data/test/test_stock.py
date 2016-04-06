import unittest
from data.stock import Stock


class TestStock(unittest.TestCase):
    def test_stock(self):
        stock = Stock('AAPL')
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(stock.name, 'Apple Inc.')
        self.assertEqual(stock.sector, 'Consumer Goods')
