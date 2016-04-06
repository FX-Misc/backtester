from backtest import Backtest
from data.futures_data_handler import FuturesDataHandler

class FuturesBacktest(Backtest):
    def __init__(self, events, strategy, data, execution, start_date, end_date,
                 start_time=None, end_time=None):

        assert isinstance(data, FuturesDataHandler)
        super(FuturesBacktest, self).__init__(events, strategy, data, execution, start_date, end_date)
