import time
import json
from queue import Queue
from ib_trade import IBTrade
from strategies.paper_strategy import ClassifierStrategy
from strategies.buy_strategy_stock import BuyStrategy
from ib_live.ib_data_handler import IBDataHandler
from ib_live.ib_execution_handler import IBExecutionHandler
from trading.stock import Stock

IB_CONFIG = json.load(open('test_ib_config.json', 'r'))
events = Queue()
# products = [FuturesContract('GC', exp_year=2016, exp_month=6)]
products = [Stock('MSFT'), Stock('ORCL')]
data = IBDataHandler(events, products, IB_CONFIG)
execution = IBExecutionHandler(events, IB_CONFIG)
strategy = BuyStrategy(events, data, products=products)
ib_trade = IBTrade(events, strategy, data, execution)
time.sleep(5)
ib_trade.run()