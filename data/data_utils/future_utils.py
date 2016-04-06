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
    12: 'Z'
}


def build_contract(symbol, exp_year, exp_month):
    """

    :param symbol:
    :param exp_year:
    :param exp_month:
    :return:
    """


def get_contract_month_code(month):
    """
    Get the CME contract month code.
    :param month: (int)
    :return: (char)
    """
    return MONTH_CODES[month]


def get_highest_volume_contract(year, month):
    raise NotImplementedError