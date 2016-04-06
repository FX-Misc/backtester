import unittest
from data.data_utils import future_utils as fut

class TestFutureUtils(unittest.TestCase):
    def test_get_month_code(self):
        months = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
        for i in range(12):
            self.assertTrue(fut.get_contract_month_code(i + 1), months[i])