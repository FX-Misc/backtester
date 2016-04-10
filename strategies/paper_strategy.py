import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('Portfolio')

from queue import Queue
import json
import datetime as dt
import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.externals import joblib
from hashlib import md5
import time
import prediction.features as feats
from cme_backtest.data_handler import CMEBacktestDataHandler
from trading.strategy import Strategy
from cme_backtest.execution_handler import CMEBacktestExecutionHandler
from cme_backtest.backtest import CMEBacktest
from cme_backtest.data_utils.quantgo_utils import get_data_furdays
import prediction.featutils as featutils
from plotting.plot import plot_backtest, FIGS_DIR

NOT_UPDATING_FEATURES = False
BACKTEST_NAME = None
RUN_TIME = dt.datetime.now()

granularity = 5
hl = int(3840 / granularity)
window = int(7680 / granularity)

x_feats = [
    feats.mean_reversion_signal(hl, window),
    feats.ema_diff(window/2)
]
drop_cols = featutils.drop_orderbook(min_keep_level=1, depth=5)

class ClassifierStrategy(Strategy):

    def initialize(self, contract_multiplier={}, transaction_costs={}, slippage=0, starting_cash=100000,
                   min_hold_time=dt.timedelta(minutes=15), max_hold_time=dt.timedelta(hours=2), start_date=None, end_date=None,
                   start_time=dt.time(hour=0), closing_time=dt.time(hour=23, minute=59), standardize=False, take_profit_threshold=None,
                   take_profit_down_only=False, order_qty=1):

        self.symbols = self.bars.symbols
        self.contract_multiplier = contract_multiplier
        self.transaction_costs = transaction_costs
        self.slippage = slippage
        self.starting_cash = starting_cash
        self.min_hold_time = min_hold_time
        self.max_hold_time = max_hold_time
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.closing_time = closing_time
        self.standardize = standardize
        self.take_profit_threshold = take_profit_threshold
        self.take_profit_down_only = take_profit_down_only
        self.order_qty = order_qty

        self.retrain_period = 0
        self.last_order_time = {sym: None for sym in self.symbols}
        self.pos = {sym: 0 for sym in self.symbols}
        self.implied_pos = {sym: 0 for sym in self.symbols}
        self.entry_price = {sym: None for sym in self.symbols}
        self.cash = self.starting_cash
        self.pnl = []
        self.daily_pnl = [self.starting_cash]
        self.price_series = {sym: [] for sym in self.symbols}
        self.spread = {sym: [] for sym in self.symbols}
        self.time_series = []
        self.orders = {sym: [] for sym in self.symbols}
        self.kill_till = {sym: None for sym in self.symbols}
        self.total_signals = {sym: [] for sym in self.symbols}
        self.total_probs = {sym: [] for sym in self.symbols}
        self.total_pnl = []
        self.total_price_series = {sym: [] for sym in self.symbols}
        self.total_spread = {sym: [] for sym in self.symbols}
        self.total_time_series = []
        self.total_orders = {sym: [] for sym in self.symbols}
        self.kill_till = {sym: None for sym in self.symbols}
        self.signals = {sym: [] for sym in self.symbols}
        self.probs = {sym: [] for sym in self.symbols}
        self.true_probs = {sym: [] for sym in self.symbols}
        self.cur_time = None

    def add_features(self, bars):
        for feat in x_feats:
            feat(bars)

    def new_tick(self, market_event):

        self.cur_time = market_event.datetime

        bars = self.bars.get_latest_bars(n=window)

        self.add_features(bars)

        bar = bars.iloc[-1]

        self.update_metrics()

        for sym in self.symbols:
            try:
                pos = self.implied_pos[sym]
                prob = bar['mean_reversion_signal_3840_7680']
                ema_diff = bar['ema_diff_3840']

                signal = int(-prob)

                if abs(signal) > 3:
                    signal = 3 * np.sign(signal)

                # close out
                if self.cur_time.time() >= self.closing_time and pos != 0:
                    print pos
                    self.order(sym, -pos)
                    self.implied_pos[sym] += -pos
                    self.last_order_time[sym] = self.cur_time

                elif self.cur_time.time() >= self.start_time and self.cur_time.time() < self.closing_time:

                    if self.cur_time.time() >= self.closing_time and pos == 0:
                        pass

                    # increase position
                    elif self.order_qty*abs(signal) > abs(pos):
                        self.order(sym, signal*self.order_qty - pos)
                        self.implied_pos[sym] += signal*self.order_qty - pos
                        if np.sign(pos) != np.sign(signal):
                            self.last_order_time[sym] = self.cur_time

                    elif pos != 0 and np.sign(ema_diff) != -np.sign(pos):
                        self.order(sym, -pos)
                        self.implied_pos[sym] += -pos
                        self.last_order_time[sym] = None

                    elif pos != 0:
                        self.check_stop_loss(sym)

                self.signals[sym].append(0)
                self.probs[sym].append(prob)
                self.positions[sym].append(pos)

            except Exception as e:
                self.signals[sym].append(0)
                self.probs[sym].append(0)
                self.positions[sym].append(0)
                print e

        if len(self.signals[self.symbols[0]]) != len(self.time_series):
            raise Exception("FUCK YOU")

    def new_day(self, newday_event):
        print "new day", newday_event.next_date

        if len(self.time_series) == 0:
            return

        self.daily_pnl.append(self.pnl[-1])

        self.total_time_series += self.time_series
        self.total_pnl += self.pnl
        for sym in self.symbols:
            self.total_price_series[sym] += self.price_series[sym]
            self.total_orders[sym] += self.orders[sym]
            self.total_signals[sym] += self.signals[sym]
            self.total_probs[sym] += self.probs[sym]

        backtest_dir = os.path.join('forwardtests',
                            "_".join(self.symbols),
                            "{}_{}".format(self.start_date.strftime("%Y_%m_%d"), self.end_date.strftime("%Y_%m_%d")),
                            RUN_TIME.strftime("%Y_%m_%d_%h_%M_%s")
                            if BACKTEST_NAME is None else BACKTEST_NAME)

        plot_backtest(os.path.join(backtest_dir,
                                   'forwardtest_results_{}'.format(
                                       (dt.datetime.utcfromtimestamp(newday_event.prev_date.tolist()/1e9)).strftime("%Y_%m_%d"))),
                      self.time_series,
                      self.price_series[self.symbols[0]],
                      self.pnl,
                      self.orders[self.symbols[0]],
                      self.signals[self.symbols[0]],
                      self.probs[self.symbols[0]])

        self.time_series = []
        self.pnl = []
        for sym in self.symbols:
            self.price_series[sym] = []
            self.orders[sym] = []
            self.signals[sym] = []
            self.probs[sym] = []
            self.true_probs[sym] = []

    def new_fill(self, fill_event):
        sym = fill_event.symbol
        self.pos[sym] += fill_event.quantity
        if self.pos[sym] == 0:
            self.entry_price[sym] = None
        else:
            self.entry_price[sym] = fill_event.fill_cost / float(fill_event.quantity)
        self.cash -= self.contract_multiplier[sym] * fill_event.fill_cost - \
                     self.transaction_costs[sym] * abs(fill_event.quantity) - \
                     self.contract_multiplier[sym] * abs(fill_event.quantity) * self.slippage
        self.orders[sym].append((self.cur_time, fill_event.quantity, self.pos[sym], abs(fill_event.fill_cost / float(fill_event.quantity))))

    def finished(self):

        log_returns = np.diff(np.log(self.daily_pnl))
        sharpe = np.sqrt(252) * (np.mean(log_returns) / np.std(log_returns))
        max_drawdown = np.min(
            [np.min(np.array(self.daily_pnl)[i:] - np.array(self.daily_pnl)[:-i])
             for i in xrange(1, len(self.daily_pnl))])
        print "Sharpe ratio = {}".format(sharpe)
        print "Max drawdown = {}".format(max_drawdown)

        info_fpath = self._build_forwardtest_fpath('info.json')

        with open(info_fpath, 'w') as f:
            info = {
                'closing_time': str(self.closing_time),
                'min_hold': str(self.min_hold_time),
                'max_hold': str(self.max_hold_time),
                'slippage': self.slippage,
                'standardize': self.standardize,
                'starting_cash': self.starting_cash,
                'sharpe': sharpe,
                'pnl': self.total_pnl[-1],
                'daily_pnl': self.daily_pnl,
                'max_drawdown': max_drawdown,
                'orders': sum([len(self.total_orders[s]) for s in self.symbols]),
                'longs': sum([len(filter(lambda x: (x[1] > 0) and (x[2] != 0), self.total_orders[s])) for s in self.symbols]),
                'shorts': sum([len(filter(lambda x: (x[1] < 0) and (x[2] != 0), self.total_orders[s])) for s in self.symbols])
            }
            f.write(json.dumps(info))

        backtest_dir = os.path.join('forwardtests',
                                    "_".join(self.symbols),
                                    "{}_{}".format(self.start_date.strftime("%Y_%m_%d"), self.end_date.strftime("%Y_%m_%d")),
                                    RUN_TIME.strftime("%Y_%m_%d_%h_%M_%s")
                                    if BACKTEST_NAME is None else BACKTEST_NAME)

        plot_backtest(os.path.join(backtest_dir, 'forwardtest_results_full'),
                      self.total_time_series,
                      self.total_price_series[self.symbols[0]],
                      self.total_pnl,
                      self.total_orders[self.symbols[0]],
                      self.total_signals[self.symbols[0]],
                      self.total_probs[self.symbols[0]])

    def update_metrics(self):
        last_bar = self.bars.get_latest_bars(n=1)
        pnl_ = self.cash + sum([self.pos[sym] * self.contract_multiplier[sym] *
                                (last_bar['level_1_price_buy']
                                 if self.pos[sym] < 0 else
                                 last_bar['level_1_price_sell']) for sym in self.symbols])
        self.pnl.append(pnl_)
        self.time_series.append(self.cur_time)
        for sym in self.symbols:
            self.price_series[sym].append((last_bar['level_1_price_buy'] + last_bar['level_1_price_sell']) / 2.)
            self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])

    def check_stop_loss(self, sym):
        pos = self.implied_pos[sym]
        # TODO - improve stop-loss handling
        """
        if (pos != 0 and len(self.pnl) > 600 and self.pnl[-600] - self.pnl[-1] > 250) and \
                (self.kill_till[sym] is None or self.kill_till[sym] <= self.cur_time):
            self.order(sym, -pos)
            self.order(sym, -pos)
            self.implied_pos[sym] += -2*pos
            self.kill_till[sym] = self.cur_time + dt.timedelta(minutes=15)
            self.last_order_time[sym] = self.cur_time
        """

    def _build_forwardtest_fpath(self, fname):
        backtest_dir = os.path.join('forwardtests',
                                    "_".join(self.symbols),
                                    "{}_{}".format(self.start_date.strftime("%Y_%m_%d"), self.end_date.strftime("%Y_%m_%d")),
                                    RUN_TIME.strftime("%Y_%m_%d_%h_%M_%s")
                                    if BACKTEST_NAME is None else BACKTEST_NAME)

        fpath = os.path.join(FIGS_DIR, backtest_dir, fname)

        if not os.path.exists(os.path.dirname(fpath)):
            os.makedirs(os.path.dirname(fpath))

        return fpath

def run_forwardtest():
    # parameters
    #global BACKTEST_NAME
    #if len(sys.argv) > 1:
    #    BACKTEST_NAME = sys.argv[1]
    start_time = dt.time(hour=3)
    closing_time = dt.time(hour=20)
    standardize = False
    take_profit_threshold = None
    #start_date = dt.datetime(year=2015, month=11, day=1)
    #end_date = dt.datetime(year=2015, month=11, day=30)
    #symbols = ['GCZ5']
    start_date = dt.datetime.strptime(sys.argv[2], "%Y-%m-%d")
    end_date = dt.datetime.strptime(sys.argv[3], "%Y-%m-%d")
    symbols = [sys.argv[1]]
    contract_multiplier = {
        symbols[0]: 1000
    }
    transaction_costs = {
        symbols[0]: 1.45
    }

    events = Queue()

    bars = CMEDataHandlerHistorical(events, symbols, start_date, end_date,
                                    second_bars=True,
                                    add_features=False,
                                    standardize=standardize,
                                    start_time=dt.timedelta(hours=3),
                                    end_time=dt.timedelta(hours=22))

    strategy = ClassifierStrategy(bars, events,
                                  load_classifier=True,
                                  contract_multiplier=contract_multiplier,
                                  transaction_costs=transaction_costs,
                                  slippage=0.01,
                                  min_hold_time=dt.timedelta(minutes=5),
                                  max_hold_time=dt.timedelta(hours=12),
                                  start_date=start_date,
                                  end_date=end_date,
                                  start_time=start_time,
                                  closing_time=closing_time,
                                  standardize=standardize)

    execution = CMEBacktestExecutionHandler(symbols, events, second_bars=True)
    backtest = Backtest(events, bars, strategy, execution, start_date, end_date)
    backtest.run()

if __name__ == "__main__":
    run_forwardtest()