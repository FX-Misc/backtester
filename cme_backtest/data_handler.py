import logging
import datetime as dt
from trading.events import MarketEvent
from trading.data_handler import BacktestDataHandler
from cme_backtest.data_utils.quantgo_utils import get_data_multi
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('Backtest')


class CMEBacktestDataHandler(BacktestDataHandler):
    def __init__(self, events, products, start_date, end_date,
                 start_time=dt.time(hour=3),
                 end_time=dt.time(hour=20),
                 second_bars=True):

        super(CMEBacktestDataHandler, self).__init__(events, products, start_date, end_date,
                                                     start_time=start_time,
                                                     end_time=end_time)
        self.second_bars = second_bars
        self.symbols = [product.symbol for product in self.products]
        self.curr_day = dt.datetime(year=start_date.year, month=start_date.month, day=start_date.day)
        self.curr_day_data = None
        self.curr_day_index = 0
        self.curr_dt = None
        self.symbol = self.symbols[0]
        self.last_bar = {}
        self._load_day_data()


    def _load_day_data(self):
        """
        Updates the current_day_data.
        """
        self.curr_day_data = get_data_multi(self.symbols, self.curr_day,
                                            download=False,
                                            second_bars=True,
                                            start_time=self.start_time,
                                            end_time=self.end_time)
        self.curr_day_data_it = self.curr_day_data.iterrows()

    def update(self):
        if self.curr_day >= self.end_date:
            self.continue_backtest = False
            return
        try:
            self._push_next_data()
        except (StopIteration, AttributeError, ValueError):
            self.curr_day += dt.timedelta(days=1)
            self._load_day_data()
            self.update()

    def _push_next_data(self):
        """
        Push the next tick from curr_day_data to latest_data (for all symbols).
        """
        timestamp, self.last_bar = next(self.curr_day_data_it)
        self.curr_dt = timestamp.to_datetime()
        self.events.put(MarketEvent(self.curr_dt, self.last_bar))