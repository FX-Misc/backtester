import os
import json
import pandas as pd
import numpy as np
import datetime as dt
from Queue import Queue
from backtest.backtest import Backtest
from backtest.data import BacktestData
from backtest.execution import BacktestExecution
from trading.strategy import Strategy
from trading.futures_contract import FuturesContract
from plotting.plot import plot_backtest, FIGS_DIR

# Params
NOT_UPDATING_FEATURES = False
BACKTEST_NAME = None
RUN_TIME = dt.datetime.now()

# TODO - plot the entry and exit thresholds plus the true_price vs mid_price


class MeanrevertStrategy(Strategy):

    def initialize(self,  contract_multiplier=None, transaction_costs=None, slippage=0, starting_cash=100000, granularity=1,
                   min_hold_time=dt.timedelta(minutes=15), max_hold_time=dt.timedelta(hours=2), start_date=None, end_date=None,
                   start_time=dt.time(hour=0), closing_time=dt.time(hour=23, minute=59), order_qty=1):

        self.prod = self.products[0]
        # self.symbols = self.data.symbols

        self.contract_multiplier = contract_multiplier if contract_multiplier is not None else {}
        self.transaction_costs = transaction_costs if transaction_costs is not None else {}

        self.slippage = slippage
        self.starting_cash = starting_cash
        self.min_hold_time = min_hold_time
        self.max_hold_time = max_hold_time
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.closing_time = closing_time
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
        self.total_signals2 = {sym: [] for sym in self.symbols}
        self.total_probs = {sym: [] for sym in self.symbols}
        self.total_pnl = []
        self.total_price_series = {sym: [] for sym in self.symbols}
        self.total_spread = {sym: [] for sym in self.symbols}
        self.total_time_series = []
        self.total_orders = {sym: [] for sym in self.symbols}
        self.total_positions = {sym: [] for sym in self.symbols}
        self.kill_till = {sym: None for sym in self.symbols}
        self.signals = {sym: [] for sym in self.symbols}
        self.signals2 = {sym: [] for sym in self.symbols}
        self.probs = {sym: [] for sym in self.symbols}
        self.true_probs = {sym: [] for sym in self.symbols}
        # self.positions = {sym: [] for sym in self.symbols}
        self.curr_dt = None
        self.granularity = granularity

        self.alphas = []
        self.thetas = {sym: [0] for sym in self.symbols}
        self.thetas_ps = {sym: [0] for sym in self.symbols}

        self.theta_lockdown = 0
        self.jump_lockdown = 0
        self.stoploss_lockdown = 0

        self.HL = int(7680/2 / self.granularity)
        self.alpha = 1-np.exp(np.log(0.5)/self.HL)
        self.std_window = 4*self.HL

        self.true_price = {sym: [] for sym in self.symbols}
        self.true_price_ps = {sym: [] for sym in self.symbols}
        self.uthreshs = {sym: [] for sym in self.symbols}
        self.dthreshs = {sym: [] for sym in self.symbols}
        self.uexthreshs = {sym: [] for sym in self.symbols}
        self.dexthreshs = {sym: [] for sym in self.symbols}

        self.total_true_price = {sym: [] for sym in self.symbols}
        self.total_true_price_ps = {sym: [] for sym in self.symbols}
        self.total_uthreshs = {sym: [] for sym in self.symbols}
        self.total_dthreshs = {sym: [] for sym in self.symbols}
        self.total_uexthreshs = {sym: [] for sym in self.symbols}
        self.total_dexthreshs = {sym: [] for sym in self.symbols}

        self.stds = {sym: [] for sym in self.symbols}

        self.lockdown = [0]

        self.std_queue = {sym: [] for sym in self.symbols}

        self.pos_entry_index = None

        self.trade_pnls = {
            'pnl': [],
            'theta': [],
            'stopped': []
        }

    def new_tick(self):


        '''
        last bar is automatically updated, also no need to update self.curr_dt as it is also automatically updated
        prior to new_tick()
        '''
        bar = self.data.last_bar[self.products[0].symbol]
        mid_price = (bar['level_1_price_buy'] + bar['level_1_price_sell']) / 2.
        self.update_metrics()  #TODO: abstractions

        slope = 0

        for sym in self.symbols:
            #try:
            if True:
                if len(self.true_price[sym]) > 0:
                    py = self.true_price[sym][-1]
                    py_ps = self.true_price_ps[sym][-1]
                    pt = self.thetas[sym][-1]
                    pt_ps = self.thetas_ps[sym][-1]
                    x = mid_price
                    self.lockdown.append(0)
                    if self.theta_lockdown > 0:
                        self.theta_lockdown -= 1
                        self.lockdown[-1] = 1
                    if self.jump_lockdown > 0:
                        self.jump_lockdown -= 1
                        self.lockdown[-1] = 1
                        a = 1
                        aps = 1
                        self.thetas[sym].append(0)
                        self.thetas_ps[sym].append(0)
                    else:
                        slope = 10 * (self.true_price_ps[sym][-1] - self.true_price_ps[sym][-2]) \
                            if len(self.true_price_ps[sym]) > 2 else 0
                        self.thetas[sym].append(4*self.alpha * (self.true_price[sym][-1]-x) + (1-4*self.alpha) * pt)
                        self.thetas_ps[sym].append(4 * self.alpha * (self.true_price_ps[sym][-1] - x) + (1 - 4 * self.alpha) * pt_ps)
                        a = min(1, self.alpha + max(0, abs(self.thetas[sym][-1]) - 0.1) + abs(slope))
                        #a = min(1, self.alpha + max(0, abs(slope)))
                        aps = min(1, self.alpha + max(0, abs(self.thetas_ps[sym][-1]) - 0.1))
                    self.true_price[sym].append(a * x + (1-a) * py)
                    self.true_price_ps[sym].append(aps * x + (1 - aps) * py_ps)
                    if abs(self.true_price[sym][-1]-x) > 1.5 and self.jump_lockdown == 0:
                        self.jump_lockdown = int(60 * 60 / self.granularity)
                    if abs(self.thetas_ps[sym][-1] - slope) > 0.15 and self.theta_lockdown == 0:
                        self.theta_lockdown = int(60 * 60 / self.granularity)
                else:
                    self.true_price[sym].append(mid_price)
                    self.true_price_ps[sym].append(mid_price)
                    self.signals[sym].append(0)
                    self.signals2[sym].append(0)
                    self.probs[sym].append(0)
                    # self.positions[sym].append(0)
                    self.uthreshs[sym].append(None)
                    self.dthreshs[sym].append(None)
                    self.uexthreshs[sym].append(None)
                    self.dexthreshs[sym].append(None)
                    continue

                # omit jump lockdowns from the std measurement
                if a != 1:
                    self.std_queue[sym].append(mid_price)
                    if len(self.std_queue[sym]) > self.std_window:
                        self.std_queue[sym] = self.std_queue[sym][1:]

                self.stds[sym].append(np.std(np.diff(self.std_queue[sym])))

                pos = self.implied_pos[sym]

                # close out
                if self.curr_dt.time() >= self.closing_time and pos != 0:
                    self.order(self.prod, -pos)
                    self.implied_pos[sym] += -pos
                    self.last_order_time[sym] = self.curr_dt
                    self.signals[sym].append(0)
                    self.signals2[sym].append(0)
                    self.probs[sym].append(0)
                    # self.positions[sym].append(0)
                    self.uthreshs[sym].append(None)
                    self.dthreshs[sym].append(None)
                    self.uexthreshs[sym].append(None)
                    self.dexthreshs[sym].append(None)
                    continue

                # do not trade before start time or after close
                if self.curr_dt.time() < self.start_time or self.curr_dt.time() > self.closing_time:
                    self.signals[sym].append(0)
                    self.signals2[sym].append(0)
                    self.probs[sym].append(0)
                    # self.positions[sym].append(0)
                    self.uthreshs[sym].append(None)
                    self.dthreshs[sym].append(None)
                    self.uexthreshs[sym].append(None)
                    self.dexthreshs[sym].append(None)
                    continue

                uthresh = self.true_price[sym][-1] + max(0.15/2, self.stds[sym][-1])
                dthresh = self.true_price[sym][-1] - max(0.15/2, self.stds[sym][-1])

                uexthresh = self.true_price[sym][-1] #+ max(0.075/4, self.stds[sym][-1]/4.)
                dexthresh = self.true_price[sym][-1] #- max(0.075/4, self.stds[sym][-1]/4.)

                #signal = mid_price - self.true_price[sym][-1]
                signal = abs(self.true_price[sym][-1] - self.true_price[sym][-2])
                signal2 = self.thetas_ps[sym][-1] - slope

                if (self.jump_lockdown > 0 or self.theta_lockdown > 0 or self.stoploss_lockdown > 0) and pos != 0:
                    self.order(self.prod, -pos)
                    self.implied_pos[sym] += -pos
                    trade_pnl = self.pnl[-1] - self.pnl[self.pos_entry_index]
                    self.trade_pnls['pnl'].append(trade_pnl)
                    self.trade_pnls['theta'].append(signal2)
                    self.trade_pnls['stopped'].append(1)
                elif mid_price > uthresh:
                    #qty = -1*(1 + abs(mid_price-uthresh)/0.1/self.stds[sym][-1])
                    qty = -1
                    if (abs(qty) > abs(pos) and np.sign(qty) == np.sign(pos)) or (np.sign(qty) != np.sign(pos)):
                        self.order(self.prod, qty-pos)
                        self.implied_pos[sym] += qty-pos
                        self.pos_entry_index = len(self.pnl) - 1
                elif mid_price < dthresh:
                    #qty = (1 + abs(dthresh-mid_price)/0.1/self.stds[sym][-1])
                    qty = 1
                    if (abs(qty) > abs(pos) and np.sign(qty) == np.sign(pos)) or (np.sign(qty) != np.sign(pos)):
                        self.order(self.prod, qty-pos)
                        self.implied_pos[sym] += qty-pos
                        self.pos_entry_index = len(self.pnl) - 1
                elif pos < 0 and mid_price <= uexthresh:
                    self.order(self.prod, -pos)
                    self.implied_pos[sym] += -pos
                    trade_pnl = self.pnl[-1] - self.pnl[self.pos_entry_index]
                    self.trade_pnls['pnl'].append(trade_pnl)
                    self.trade_pnls['theta'].append(signal2)
                    self.trade_pnls['stopped'].append(0)
                    self.pos_entry_index = None
                elif pos > 0 and mid_price >= dexthresh:
                    self.order(self.prod, -pos)
                    self.implied_pos[sym] += -pos
                    trade_pnl = self.pnl[-1] - self.pnl[self.pos_entry_index]
                    self.trade_pnls['pnl'].append(trade_pnl)
                    self.trade_pnls['theta'].append(signal2)
                    self.trade_pnls['stopped'].append(0)
                    self.pos_entry_index = None

                if self.stoploss_lockdown > 0:
                    self.stoploss_lockdown -= 1

                self.signals[sym].append(signal)
                self.signals2[sym].append(signal2)
                self.probs[sym].append(self.thetas_ps[sym][-1])
                # self.positions[sym].append(pos)
                self.uthreshs[sym].append(uthresh)
                self.dthreshs[sym].append(dthresh)
                self.uexthreshs[sym].append(uexthresh)
                self.dexthreshs[sym].append(dexthresh)

                if pos != 0:
                    self.check_stop_loss(self.prod)

            #except Exception as e:
            #    self.true_price[sym].append(mid_price)
            #    self.true_price_preslope[sym].append(mid_price)
            #    self.signals[sym].append(0)
            #    self.signals2[sym].append(0)
            #    self.probs[sym].append(0)
            #    self.positions[sym].append(0)
            #    self.uthreshs[sym].append(None)
            #    self.dthreshs[sym].append(None)
            #    self.uexthreshs[sym].append(None)
            #    self.dexthreshs[sym].append(None)
            #    print e

        if len(self.true_price[self.symbols[0]]) != len(self.time_series):
            print len(self.true_price[self.symbols[0]]), len(self.time_series)
            raise Exception("FUCK YOU")

    def new_day(self):
        print "new day", self.curr_dt

        if len(self.time_series) == 0:
            return

        self.daily_pnl.append(self.pnl[-1])

        self.total_time_series += self.time_series
        self.total_pnl += self.pnl
        for sym in self.symbols:
            self.total_price_series[sym] += self.price_series[sym]
            self.total_orders[sym] += self.orders[sym]
            self.total_signals[sym] += self.signals[sym]
            self.total_signals2[sym] += self.signals2[sym]
            self.total_probs[sym] += self.probs[sym]
            # self.total_positions[sym] += self.positions[sym]
            self.total_true_price[sym] += self.true_price[sym]
            self.total_true_price_ps[sym] += self.true_price_ps[sym]
            self.total_uthreshs[sym] += self.uthreshs[sym]
            self.total_dthreshs[sym] += self.dthreshs[sym]
            self.total_uexthreshs[sym] += self.uexthreshs[sym]
            self.total_dexthreshs[sym] += self.dexthreshs[sym]

        backtest_dir = os.path.join('backtests',
                            "_".join(self.symbols),
                            "{}_{}".format(self.start_date.strftime("%Y_%m_%d"), self.end_date.strftime("%Y_%m_%d")),
                            RUN_TIME.strftime("%Y_%m_%d_%h_%M_%s")
                            if BACKTEST_NAME is None else BACKTEST_NAME)

        path = os.path.join(backtest_dir,'backtest_results_{}'.
                            format((dt.datetime.utcfromtimestamp(self.data.prev_day.tolist()/1e9)).strftime("%Y_%m_%d")))
        plot_backtest(path,
                      self.time_series,
                      self.price_series[self.symbols[0]],
                      self.true_price[self.symbols[0]],
                      self.true_price_ps[self.symbols[0]],
                      self.uthreshs[self.symbols[0]],
                      self.dthreshs[self.symbols[0]],
                      self.uexthreshs[self.symbols[0]],
                      self.dexthreshs[self.symbols[0]],
                      self.pnl,
                      self.orders[self.symbols[0]],
                      self.signals[self.symbols[0]],
                      self.signals2[self.symbols[0]],
                      self.probs[self.symbols[0]],
                      # self.positions[self.symbols[0]]
                      )

        self.time_series = []
        self.pnl = []
        for sym in self.symbols:
            self.price_series[sym] = []
            self.orders[sym] = []
            self.signals[sym] = []
            self.signals2[sym] = []
            self.probs[sym] = []
            self.true_probs[sym] = []
            # self.positions[sym] = []
            self.true_price[sym] = []
            self.true_price_ps[sym] = []
            self.uthreshs[sym] = []
            self.dthreshs[sym] = []
            self.uexthreshs[sym] = []
            self.dexthreshs[sym] = []

    def new_fill(self, fill_event):
        pass
        # sym = fill_event.symbol
        # self.pos[sym] += fill_event.quantity
        # if self.pos[sym] == 0:
        #     self.entry_price[sym] = None
        # else:
        #     self.entry_price[sym] = fill_event.fill_cost / float(fill_event.quantity)
        # self.cash -= self.contract_multiplier[sym] * fill_event.fill_cost + \
        #              self.transaction_costs[sym] * abs(fill_event.quantity) + \
        #              self.contract_multiplier[sym] * abs(fill_event.quantity) * self.slippage
        # self.orders[sym].append((self.curr_dt, fill_event.quantity, self.pos[sym], abs(fill_event.fill_cost / float(fill_event.quantity))))

    def finished(self):

        log_returns = np.diff(np.log(self.daily_pnl))
        sharpe = np.sqrt(252) * (np.mean(log_returns) / np.std(log_returns))
        max_drawdown = np.min(
            [np.min(np.array(self.daily_pnl)[i:] - np.array(self.daily_pnl)[:-i])
             for i in xrange(1, len(self.daily_pnl))])
        print "Sharpe ratio = {}".format(sharpe)
        print "Max drawdown = {}".format(max_drawdown)

        info_fpath = self._build_backtest_fpath('info.json')

        with open(info_fpath, 'w') as f:
            info = {
                'min_hold': str(self.min_hold_time),
                'max_hold': str(self.max_hold_time),
                'slippage': self.slippage,
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

        backtest_dir = os.path.join('backtests',
                                    "_".join(self.symbols),
                                    "{}_{}".format(self.start_date.strftime("%Y_%m_%d"), self.end_date.strftime("%Y_%m_%d")),
                                    RUN_TIME.strftime("%Y_%m_%d_%h_%M_%s")
                                    if BACKTEST_NAME is None else BACKTEST_NAME)

        pd.DataFrame(data=self.trade_pnls).to_csv(self._build_backtest_fpath('trade_info.csv'))

        plot_backtest(os.path.join(backtest_dir, 'backtest_results_full'),
                      self.total_time_series,
                      self.total_price_series[self.symbols[0]],
                      self.total_true_price[self.symbols[0]],
                      self.total_true_price_ps[self.symbols[0]],
                      self.total_uthreshs[self.symbols[0]],
                      self.total_dthreshs[self.symbols[0]],
                      self.total_uexthreshs[self.symbols[0]],
                      self.total_dexthreshs[self.symbols[0]],
                      self.total_pnl,
                      self.total_orders[self.symbols[0]],
                      self.total_signals[self.symbols[0]],
                      self.total_signals2[self.symbols[0]],
                      self.total_probs[self.symbols[0]],
                      self.total_positions[self.symbols[0]])

    def update_metrics(self):
        # last_bar = self.bars.get_latest_bars(n=1)
        last_bar = self.data.last_bar[self.products[0].symbol]
        last_bar_mid_price = (last_bar['level_1_price_sell'] + last_bar['level_1_price_buy']) / 2.
        # pnl_ = self.cash + sum([self.pos[sym] * self.contract_multiplier[sym] * last_bar_mid_price for sym in self.symbols])
        # print self.pos
        pnl_ = self.cash + sum([self.pos[sym] * 1000 * last_bar_mid_price for sym in self.symbols])
        self.pnl.append(pnl_)
        self.time_series.append(self.curr_dt)
        # for sym in self.symbols:
        #     self.price_series[sym].append(last_bar_mid_price)
        #     self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])

    def check_stop_loss(self, sym):
        if self.pos_entry_index is not None:
            pos_pnl = self.pnl[-1] - self.pnl[self.pos_entry_index]
            if pos_pnl < -200:
                pos = self.implied_pos[sym]
                self.order(self.prod, -pos)
                self.implied_pos[sym] += -pos
                trade_pnl = self.pnl[-1] - self.pnl[self.pos_entry_index]
                self.trade_pnls['pnl'].append(trade_pnl)
                self.trade_pnls['theta'].append(self.thetas_ps[sym][-1] - self.signals2[sym][-1])
                self.trade_pnls['stopped'].append(1)
                self.pos_entry_index = None
                self.stoploss_lockdown = 10

        # TODO - improve stop-loss handling
        """
        if (pos != 0 and len(self.pnl) > 600 and self.pnl[-600] - self.pnl[-1] > 250) and \
                (self.kill_till[sym] is None or self.kill_till[sym] <= self.cur_time):
            self.order(self.prod, -pos)
            self.order(self.prod, -pos)
            self.implied_pos[sym] += -2*pos
            self.kill_till[sym] = self.cur_time + dt.timedelta(minutes=15)
            self.last_order_time[sym] = self.cur_time
        """

    def _build_backtest_fpath(self, fname):
        backtest_dir = os.path.join('backtests',
                                    "_".join(self.symbols),
                                    "{}_{}".format(self.start_date.strftime("%Y_%m_%d"), self.end_date.strftime("%Y_%m_%d")),
                                    RUN_TIME.strftime("%Y_%m_%d_%h_%M_%s")
                                    if BACKTEST_NAME is None else BACKTEST_NAME)

        fpath = os.path.join(FIGS_DIR, backtest_dir, fname)

        if not os.path.exists(os.path.dirname(fpath)):
            os.makedirs(os.path.dirname(fpath))

        return fpath


def run_backtest():
    order_qty = 1
    start_time = dt.time(hour=5)
    closing_time = dt.time(hour=18)
    standardize = False
    start_date = dt.datetime(year=2015, month=12, day=1)
    end_date = dt.datetime(year=2015, month=12, day=2)

    # contract_multiplier = {
    #     symbols[0]: 1000
    # }
    # transaction_costs = {
    #     symbols[0]: 1.45
    # }

    events = Queue()
    products = [FuturesContract('GC', continuous=True)]
    data = BacktestData(events, products, start_date, end_date, start_time=start_time, end_time=closing_time)
    execution = BacktestExecution(events, products)
    strategy = MeanrevertStrategy(events, data, products,
                                  initial_cash=100000,
                                  # contract_multiplier=contract_multiplier,
                                  # transaction_costs=transaction_costs,
                                  slippage=0.00,
                                  granularity=60,
                                  order_qty=order_qty,
                                  min_hold_time=dt.timedelta(minutes=5),
                                  max_hold_time=dt.timedelta(hours=12),
                                  start_date=start_date,
                                  end_date=end_date,
                                  start_time=start_time,
                                  closing_time=closing_time)

    backtest = Backtest(events, strategy, data, execution, start_date, end_date)
    backtest.run()


if __name__ == "__main__":
    run_backtest()