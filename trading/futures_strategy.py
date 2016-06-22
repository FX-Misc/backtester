import numpy as np
import pandas as pd
import datetime as dt
from trading.strategy import Strategy
from cme_backtest.data_utils.quantgo_utils import _reindex_data
from futures_utils import get_base_symbol_from_symbol

BUFFER_SIZE = 100000

class FuturesStrategy(Strategy):

    def __init__(self, events, data, products, initial_cash=0, continuous=True, live=False):
        super(FuturesStrategy, self).__init__(events, data, products, initial_cash)

        self.ticker_prods = {product.symbol: product for product in self.products}
        self.pnl_series = []
        self.transactions_series = []  #(fill_time, quantity, fill_price, ticker)
        # self.cash_series = pd.Series(data=None)
        # self.positions_series = {product.symbol: pd.Series(data=None) for product in self.products}
        # self.transactions_series = {product.symbol: pd.DataFrame(data=None, columns=['dt', 'amount', 'price', 'symbol']) for product in self.products}
        # self.time_series = self._make_time_series_df(0, columns=['dt', 'level_1_price_buy', 'level_1_price_sell'])
        # self.time_series_index = 0
        self.live = live

    def _new_tick_update_backtest(self, market_event):
        """
        Take the data directly from the data handler (for historical data)
        :param market_event:
        :return:
        """

    def _new_tick_update_live(self, market_event):
        """
        Stream the data into a buffer.
        :param market_event:
        :return:
        """
        pass


    def get_latest_bars(self, symbol, window, start=None):
        """
        Get data for a symbol from [start-window, start]
        :param symbol:
        :param window: (pd.Timedelta)
        :param start: (pd.Timestamp / DateTime) defaults to self.curr_dt
        :return:
        """
        start = start if start is not None else self.curr_dt
        if self.live is False:
            return self._get_latest_bars_backtest(symbol, window, start)
        else:
            return self._get_latest_bars_live()





    def finished(self):
        pass
        # for symbol_time_series in self.time_series.values():
        #     symbol_time_series.set_index('dt', inplace=True)
