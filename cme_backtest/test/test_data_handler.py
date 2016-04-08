import unittest
from Queue import Queue

class TestCMEBacktest(unittest.TestCase):

    @classmethod
    def setUpCls(cls):
        cls.events = Queue()

