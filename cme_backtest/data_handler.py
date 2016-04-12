import logging
import datetime as dt
from events import CMEBacktestMarketEvent
from trading.data_handler import BacktestDataHandler
from cme_backtest.data_utils.quantgo_utils import get_data, get_data_multi
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('Backtest')


class CMEBacktestDataHandler(BacktestDataHandler):
    def __init__(self, events, symbols, start_date, end_date,
                 start_time=dt.timedelta(hours=3), end_time=dt.timedelta(hours=20, minutes=59),
                 second_bars=True):

        super(CMEBacktestDataHandler, self).__init__(events, symbols, start_date, end_date,
                                                     start_time=start_time, end_time=end_time)
        self.second_bars = second_bars
        self.latest_data = None
        self.curr_day = dt.datetime(year=start_date.year, month=start_date.month, day=start_date.day)
        self.curr_day_data = None
        self.curr_day_index = 0
        self.symbol = self.symbols[0]
        self._load_day_data()

    def _load_day_data(self):
        """
        Updates the current_day_data.
        """
        # log.info("Loading data for " + self.symbol + " " + str(self.curr_day))
        try:
            if len(self.symbols) > 1:
                self.curr_day_data = get_data_multi(self.symbols, self.curr_day, second_bars=self.second_bars,
                                                    start_time=self.start_time, end_time=self.end_time)
            else:
                self.curr_day_data = get_data(self.symbol, self.curr_day, download=False, second_bars=True)
        except ValueError:
            pass

    def get_latest(self, n=1):
        """
        Return latest data.
        """
        latest_data = self.latest_data
        self.latest_data = None
        return latest_data

    def update(self):
        if self.curr_day > self.end_date:
            self.continue_backtest = False
            return
        try:
            self._push_next_data()
        except IndexError:
            self.curr_day += dt.timedelta(days=1)
            self._load_day_data()
            self.update()

    def _push_next_data(self):
        """
        Push the next tick from curr_day_data to latest_data (for all symbols).
        """
        self.latest_data = self.curr_day_data.ix[self.curr_day_index]
        self.curr_day_index += 1
        self.events.put(CMEBacktestMarketEvent(self.latest_data['datetime']))