import tabulate
import pandas as pd
from random import randint
from collections import OrderedDict
from trading.events import OrderEvent
from trading.strategy import StockStrategy

PRICE_FIELD = 'Open'

class BuyStrategy(StockStrategy):
    def __init__(self, events, data, initial_capital=1000000):
        super(BuyStrategy, self).__init__(events, data)
        self.curr_dt = None
        self.initial_capital = initial_capital
        self.capital = initial_capital

        self.sym1 = 'AAPL'
        self.sym2 = 'MSFT'

        self.positions = {'AAPL': 0,
                          'MSFT': 0
                          }


        self.latest_data = None

        self.fills = []
        self.positions_series = OrderedDict()
        self.cash_series = OrderedDict()

    def new_tick(self, market_event):
        self.curr_dt = market_event.dt
        self.latest_data = self.data.get_latest()
        aapl_order_qty = randint(-4,4)
        msft_order_qty = randint(-12,12)
        temp_capital = self.capital
        if self._check_order(temp_capital, self.sym1, aapl_order_qty):
            self.order(self.sym1, aapl_order_qty)
            temp_capital -= self.latest_data[self.sym1][PRICE_FIELD] * aapl_order_qty

        if self._check_order(temp_capital, self.sym2, msft_order_qty):
            self.order(self.sym2, msft_order_qty)
            temp_capital -= self.latest_data[self.sym2][PRICE_FIELD] * msft_order_qty

    def _check_order(self, capital, symbol, quantity):
        if self.latest_data[symbol][PRICE_FIELD] * quantity < capital:
            return True
        return False

    def new_fill(self, fill_event):
        self.fills.append(fill_event)
        self._update_positions(fill_event)

    def _update_positions(self, fill_event):
        self.capital -= fill_event.fill_cost
        self.positions_series[fill_event.fill_time] = self.positions.copy()
        self.cash_series[fill_event.fill_time] = self.capital

    def finished(self):
        symbols = ['AAPL', 'MSFT']
        all_data = self.data.all_symbol_data
        results = pd.DataFrame(data=self.positions_series.values(), index=self.positions_series.keys())
        results['cash'] = self.cash_series.values()
        results['AAPL_mkt'] = all_data['AAPL']['Open']
        results['AAPL_value'] = results['AAPL_mkt']*results['AAPL']
        results['value'] = results['cash'] + results['AAPL_value']
        results['pnl'] = 100*results['value'].pct_change().fillna(0)
        results['pnl_total'] = 1-results['value']/self.initial_capital
        return results

    def order(self, symbol, quantity, order_type='MARKET', price=None,):
        order = OrderEvent(self.curr_dt, symbol, quantity, order_type, price)
        self.events.put(order)