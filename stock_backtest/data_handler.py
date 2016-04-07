import datetime as dt
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
        self.start_date = start_date
        self.end_date = end_date
        self.symbols = symbols
        self.all_symbol_data = yf.get_stock_data_multiple(symbols, start_date=start_date, end_date=end_date)
        self.curr_data = {}
        self.curr_date = start_date

        self.continue_backtest = True

    def get_latest(self):
        """
        Get the latest data (called from a Strategy)
        :return: (Series)
        """
        latest_data = self.curr_data
        self.curr_data = {}
        return latest_data

    def update(self):
        """
        Push the next-tick to the symbol data-structure (one day/line at a time)
        :return:
        """
        if self.curr_date == self.end_date:
            self.continue_backtest = False
            return
        try:
            self._push_next_data()
        except KeyError:
            self.curr_date += dt.timedelta(days=1)
            self.update()

    def _push_next_data(self):
        """
        Push the next tick for all symbols.
        """
        for symbol in self.symbols:
            if symbol not in self.curr_data:
                self.curr_data[symbol] = self.all_symbol_data[symbol].ix[self.curr_date]
            else:
                self.curr_data[symbol].append(self.all_symbol_data[symbol].ix[self.curr_date])
