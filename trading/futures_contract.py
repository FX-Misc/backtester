import os
import csv
import datetime as dt
import Quandl as qd
from dateutil.tz import tzlocal
from dateutil.relativedelta import relativedelta
from ib_live.ib_utils import create_ib_futures_contract
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class FuturesContract(object):
    def __init__(self, base_symbol, exp_year=None, exp_month=None, continuous=False):
        self.base_symbol = base_symbol
        self.symbol = build_contract(base_symbol, exp_year, exp_month)
        self.exp_year = exp_year if exp_year is not None else dt.datetime.now().year
        self.exp_month = exp_month if exp_month is not None else dt.datetime.now().month

        specs = get_contract_specs(self.base_symbol)
        self.name = specs['Name']
        self.exchange = specs['Exchange']
        self.tick_value = specs['Tick Value']
        self.contract_size = specs['Contract Size']
        self.active = specs['Active']
        self.deliver_months = specs['Delivery Months']
        self.units = specs['Units']
        self.currency = specs['Currency']
        self.trading_times = specs['Trading Times']
        self.min_tick_value =  specs['Minimum Tick Value']
        self.full_point_value = specs['Full Point Value']
        self.terminal_point_value = ['Terminal Point Value']

        self.mkt_open, self.mkt_close = get_mkt_times(self.trading_times)

        self.ib_contract = create_ib_futures_contract(self.base_symbol,
                                                      exp_month=self.exp_month,
                                                      exp_year=self.exp_year,
                                                      exchange=self.exchange,
                                                      currency=self.currency)


def get_contract_month_code(exp_month):
    """
    Get the CME contract month code.
    :param exp_month: (int)
    :return: (char)
    """
    return MONTH_CODES[exp_month]


def build_contract(symbol, exp_year, exp_month):
    """
    Build the contract ticker.
    :param symbol: (str)
    :param exp_year: (int)
    :param exp_month: (int)
    :return: (str) e.g. 'GCM6'
    """
    year = str(exp_year)[-1]
    month = get_contract_month_code(exp_month)
    return symbol + month + year


def get_exp_year_from_symbol(symbol):
    return int('201'+symbol[-1])


def get_exp_month_from_symbol(symbol):
    return MONTH_CODES[symbol[-2]]


def get_base_symbol_from_symbol(symbol):
    return symbol[:-2]


def get_quandl_future_code(symbol, exp_year, exp_month):
    """
    Builds the quandl database code for the requested future contract.
    :param symbol:
    :param exp_year:
    :param exp_month:
    :return:
    """
    return 'CME/' + symbol + get_contract_month_code(exp_month) + str(exp_year)


def get_futures_data(symbol, exp_year, exp_month):
    """
    Get's inter-day futures data from Quandl.
    :param symbol: (str)
    :param exp_year: (int)
    :param exp_month: (int)
    :return: (DataFrame)
    |                     |   Open |   High |    Low |   Last |   Change |   Settle |   Volume |   Open Interest |
    |:--------------------|-------:|-------:|-------:|-------:|---------:|---------:|---------:|----------------:|
    | 2016-02-26 00:00:00 |  nan   |  nan   |  nan   |  nan   |      0   |   1220.7 |        0 |               0 |
    | 2016-02-29 00:00:00 | 1220.2 | 1241.4 | 1220.2 | 1241.4 |     14   |   1234.7 |       49 |               0 |
    | 2016-03-01 00:00:00 | 1245.3 | 1247   | 1229.7 | 1232.4 |      3.6 |   1231.1 |       42 |              32 |
    | 2016-03-02 00:00:00 | 1227.8 | 1241.1 | 1227.8 | 1240.9 |     11   |   1242.1 |       42 |              33 |
    | 2016-03-03 00:00:00 | 1243.8 | 1268.1 | 1243.2 | 1268.1 |     16.5 |   1258.6 |       36 |              32 |
    | 2016-03-04 00:00:00 | 1265   | 1279.6 | 1253.5 | 1259.8 |     12.5 |   1271.1 |      113 |              37 |
    | 2016-03-07 00:00:00 | 1267.2 | 1270   | 1260.2 | 1263.8 |      6.6 |   1264.5 |       37 |              98 |
    | 2016-03-08 00:00:00 | 1269.5 | 1279.2 | 1261.4 | 1262.4 |      1.1 |   1263.4 |       69 |             118 |
    | 2016-03-09 00:00:00 | 1262.6 | 1263.1 | 1245   | 1252.2 |      5.5 |   1257.9 |      227 |             157 |
    | 2016-03-10 00:00:00 | 1250.6 | 1274.5 | 1240.1 | 1274   |     15.4 |   1273.3 |      249 |             309 |
    """
    quandl_future_code = get_quandl_future_code(symbol, exp_year, exp_month)
    return qd.get(dataset=quandl_future_code, authtoken=QUANDL_KEY)


def get_highest_volume_contract(symbol, year, month, day):
    """
    Get the highest-volume contract for the symbol for a given date.
    :param symbol: (int)
    :param year: (int)
    :param month: (int)
    :param day: (int)
    :return: (str) e.g. 'GCM6'
    """
    highest_volume_contract = build_contract(symbol, year, month)
    max_volume = 0
    start_date = dt.datetime(year, month, day)
    for i in range(8):
        date = start_date + relativedelta(months=i)
        try:
            data = get_futures_data(symbol, date.year, date.month)
            volume = data.ix[start_date]['Volume']
            if volume >= max_volume:
                highest_volume_contract = build_contract(symbol, date.year, date.month)
                max_volume = volume
        except qd.DatasetNotFound:
            pass

    return highest_volume_contract


def get_contract_specs(symbol):
    """

    :param symbol:
    :return:
    """
    reader = csv.DictReader(open(os.path.join(__location__, 'contract_specs.csv')))
    contracts = {}
    for row in reader:
        k = row['Symbol']
        contracts[k] = row
    specs = contracts[symbol]
    return specs


def get_mkt_times(trading_times_str):
    mkt_open_str = trading_times_str.split('-')[0].rstrip()
    mkt_close_str = trading_times_str.split('-')[1].lstrip()
    mkt_open = dt.datetime.strptime(mkt_open_str, '%H:%M').replace(tzinfo=tzlocal()).time()
    mkt_close = dt.datetime.strptime(mkt_close_str, '%H:%M').replace(tzinfo=tzlocal()).time()
    return mkt_open, mkt_close


QUANDL_KEY = "SyH7V4ywJGho77EC6W7C"

MONTH_CODES = {
    1: 'F',
    2: 'G',
    3: 'H',
    4: 'J',
    5: 'K',
    6: 'M',
    7: 'N',
    8: 'Q',
    9: 'U',
    10: 'V',
    11: 'X',
    12: 'Z',
    'F': 1,
    'G': 2,
    'H': 3,
    'J': 4,
    'K': 5,
    'M': 6,
    'N': 7,
    'Q': 8,
    'U': 9,
    'V': 10,
    'X': 11,
    'Z': 12
}
