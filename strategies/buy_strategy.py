import tabulate
import pandas as pd
from collections import OrderedDict
from trading.events import OrderEvent
from trading.strategy import Strategy

PRICE_FIELD = 'Open'

class BuyStrategy(Strategy):
    def __init__(self, events, data, initial_capital=1000000):
        super(BuyStrategy, self).__init__(events, data)
        self.curr_dt = None
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

        aapl_order_qty = 10
        msft_order_qty = 50
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
        self.positions[fill_event.symbol] += fill_event.quantity
        self.capital -= fill_event.fill_cost
        self.positions_series[fill_event.fill_time] = self.positions.copy()
        self.cash_series[fill_event.fill_time] = self.capital

    def finished(self):
        symbols = ['AAPL', 'MSFT']
        all_data = self.data.all_symbol_data
        results = pd.DataFrame(data=self.positions_series.values(), index=self.positions_series.keys())
        results['cash'] = self.cash_series.values()
        results['position_value'] = all_data['AAPL']['Open']*results['AAPL']
        results['value'] = results['cash'] + results['position_value']
        print tabulate.tabulate(results, headers='keys', tablefmt='pipe')


    def order(self, symbol, quantity, order_type='MARKET', price=None,):
        order = OrderEvent(self.curr_dt, symbol, quantity, order_type, price)
        self.events.put(order)