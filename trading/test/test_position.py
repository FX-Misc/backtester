import unittest
from trading.position import Position
from trading.events import FillEvent

class TestPosition(unittest.TestCase):

    @classmethod
    def setUp(self):
        # initial fills
        self.position = Position('test')
        initial_fill = FillEvent(None, 'test', 19, 99.75, 19*99.75, 'test')
        self.position.update(initial_fill)
        assert self.position.symbol is 'test'
        assert self.position.quantity == 19
        assert self.position.avg_cost == 99.75

    def test_update_increase(self):
        new_fill = FillEvent(None, 'test', 10, 100, 10*100, 'test')
        self.position.update(new_fill)
        self.assertEqual(self.position.quantity, 29)
        self.assertAlmostEquals(self.position.avg_cost, 99.83620, places=3)

    def test_update_partial_decrease(self):
        new_fill = FillEvent(None, 'test', -12, 101, -12*101, 'test')
        self.position.update(new_fill)
        self.assertEqual(self.position.quantity, 7)
        self.assertAlmostEquals(self.position.avg_cost, 99.75, places=3)
        self.assertEqual(self.position.pnl_realized, 15)