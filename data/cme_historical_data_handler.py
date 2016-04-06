import logging
import datetime as dt
from data_handler import DataHandler
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('Backtest')


class CMEDataHandlerHistorical(DataHandler):
    def __init__(self, events, symbols, start_date, end_date, start_time=dt.timedelta(hours=3),
                 end_time=dt.timedelta(hours=20, minutes=59), second_bars=True,
                 add_features=True, standardize=False, bar_length=1, preprocess_function=None, x_feats=[], y_feats=[]):

        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.second_bars = second_bars
        self.add_features = add_features
        self.standardize = standardize
        self.bar_length = bar_length
        self.x_feats = x_feats
        self.y_feats = y_feats

        self.continue_backtest = True
        self.events = events

        self.latest_data = pd.DataFrame()
        self.symbol_data = {}
        self.current_day = start_date
        self.current_day_data = None
        self.current_day_data_iter = None

        self.symbol = self.symbols[0]

        self.current_day_index = 0
        self._load_day_data()

        self.xfeatures = None


    def _load_day_data(self):
        """
        Updates the current_day_data
        """
        log.info("Loading data for " + self.symbol + " " + str(self.current_day))

        self.current_day_index = 0

        if self.current_day_data is not None:
            self.events.put(NewDayEvent(self.current_day_data, self.current_day))

        try:
            if len(self.symbols) > 1:
                self.current_day_data = get_data_multi(self.symbols, self.current_day, second_bars=self.second_bars,
                                                   start_time=self.start_time, end_time=self.end_time)
            else:
                self.current_day_data = get_data(self.symbol, self.current_day, download=False, second_bars=True)

            if self.add_features:
                windows = [30, 60, 120, 240, 480, 960, 1920, 3840, 7680, 15360, 2*15360, 4*15360]

                x_feats = self.x_feats

                y_feats = self.y_feats

                self.current_day_data, xfeatures, yfeatures = feats.add_features([self.current_day_data],
                                                                  standardize=self.standardize,
                                                                  inplace=False,
                                                                  load_if_exists=False,
                                                                  start_time=self.start_time,
                                                                  end_time=self.end_time,
                                                                  x_feats=x_feats,
                                                                  y_feats=y_feats)

        except ValueError:
            self._increment_day_and_load_data()  # current day does not exist, try the next day

    def _increment_day_and_load_data(self):
        """
        Increment the day before updating the current_day_data
        """
        if self.current_day >= self.end_date:
            self.continue_backtest = False  # end the backtest
        else:
            self.current_day = self.current_day + dt.timedelta(days=1)
            self._load_day_data()

    def get_latest(self, n=1):
        """
        Returns the last N bars from the lastest_data list,
        or fewer if less bars are available.
        """
        i = self.current_day_index
        n = min(i, n)
        if n == 1:
            return self.current_day_data.ix[i]
        else:
            return self.current_day_data.ix[(i-n):(i+1)]

    def update(self):
        try:
            self.current_day_index += self.bar_length
            i = self.current_day_index
            bar = self.current_day_data.ix[i]
        except IndexError:
            self._increment_day_and_load_data()  # reached the last bar of the current day data
        else:
            if bar is not None:
                self.events.put(MarketEvent(bar['datetime']))
