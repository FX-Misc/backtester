import utils.data_utils.yahoo_finance as yf
from trading.execution_handler import ExecutionHandler

class StockBacktestExecutionHandler(ExecutionHandler):

    def __init__(self, events):
        """
        Handles simulated execution using inter-day data.
        :param events:
        :return:
        """
        # add any other parameters you might find useful for this subclass
        super(StockBacktestExecutionHandler, self).__init__(events)