import logging
from abc import ABCMeta, abstractmethod
from trading.position import Position
from trading.events import OrderEvent


class Strategy(object):

    __metaclass__ = ABCMeta

    def __init__(self, events, data, products, initial_cash, live=False, *args, **kwargs):
        """
        The Strategy is an ABC that presents an interface for taking market data and
        generating corresponding OrderEvents which are sent to the ExecutionHandler.

        :param events: (Queue)
        :param data: (DataHandler)
        :param products: (list) (FuturesContract)
        :param initial_cash: (float)
        :param args:
        :param kwargs:
        """
        self.live = live

        self.events = events
        self.data = data
        self.products = products
        self.symbols = [product.symbol for product in self.products]

        self.initialize(*args, **kwargs)

        # current internals
        self.curr_dt = None
        self.last_bar = None
        self.positions = {product.symbol: Position(product.symbol) for product in self.products}
        self.cash = initial_cash
        self.pnl_realized = 0

        # store for analysis
        self.price_series = {product.symbol: [] for product in self.products}
        self.positions_series = {product.symbol: [] for product in self.products}
        self.transactions_series = []
        self.pnl_series = []
        self.cash_series = []

        # logging
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger(__name__)

    @abstractmethod
    def new_tick(self):
        """
        Call back for when the strategy receives a new tick.
        self.last_bar is automatically updated before this.
        """
        raise NotImplementedError('Strategy.new_tick()')

    @abstractmethod
    def new_fill(self, fill_event):
        """
        Call back for when an order placed by the strategy is filled.
        This should be implemented by the strategy.

        new_fill_update is called prior to this callback.
        Updated before this callback:
            self.positions
            self.cash
            self.transactions_series

        :param fill_event: (FillEvent)
        """
        raise NotImplementedError("Strategy.new_fill()")

    def new_day(self):
        pass

    @abstractmethod
    def finished(self):
        """
        Call back for when a backtest (or live-trading) is finished.
        Creates the time_series (DataFrame)
        """
        raise NotImplementedError("Strategy.finished()")


    def order(self, product, quantity, order_type='MARKET', price=None, order_time=None):
        """
        Generate and send an order to be executed.

        :param product: (Product) FuturesContract or Stock
        :param order_type: (str) 'MARKET' or 'LIMIT'
        :param quantity: (int)
        :param price: (float)
        :param order_time: (DateTime)
        """
        order_time = order_time if order_time is not None else self.curr_dt
        order = OrderEvent(product, quantity, order_type, price, order_time)
        self.log.info(str(order))
        self.events.put(order)

    def new_tick_update(self, market_event):
        """
            Update:
            - pnl series
            - price_series (last_bar)
            - returns (series of decimal of cumulative PnL)
            - transactions (basically the fills)
            - positions series
        :param market_event:
        :return:
        """
        self.curr_dt = market_event.dt
        self.last_bar = market_event.data

    def new_fill_update(self, fill_event):
        """
        Internal update on new fill.
        Updates:
            - current positions
            - current cash
            - transactions log
            - pnl_realized

        :param fill_event: (FillEvent))
        """
        self.positions[fill_event.symbol].update(fill_event)
        self.cash -= fill_event.fill_cost
        self.transactions_series.append(fill_event)
        self.pnl_realized = sum(position.pnl_realized for position in self.positions.values())

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

    def _get_latest_bars_backtest(self, symbol, window, start):
        before = start - window
        return self.data.curr_day_data[symbol].truncate(before, start)

    def _get_latest_bars_live(self):
        pass

    def initialize(self, *args, **kwargs):
        """
        Initialize the strategy
        """
        pass