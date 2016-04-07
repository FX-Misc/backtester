import utils.data_utils.yahoo_finance as yf
from trading.data_handler import DataHandler


class StockBacktestDataHandler(DataHandler):
    def __init__(self, events, symbols, start_date, end_date):
        """
        Handles data for (one) stock using pandas/yahoo finance API.
        :param events: (Queue)
        :param symbols: (list)
        :param start_date: (datetime)
        :param end_date: (datetime)
        :return:
        """
        super(StockBacktestDataHandler, self).__init__(events)
        self.symbol_data = self.load_all_symbol_data()

    def load_all_symbol_data(self):
        """
        On init, load all the data for the provided symbols.
        :return: (dict) of (DataFrame)
        """
        raise NotImplementedError("Daniel, implement this")

    def get_latest(self, n=1):
        """
        Get the latest data (called from a Strategy)
        :param n:
        :return: (DataFrame) the last n rows of data from the symbol data-structure.
        """
        pass

    def update(self):
        """
        Push the next-tick to the symbol data-structure.
        :return:
        """
        pass
