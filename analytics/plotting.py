import utils
import timeseries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from functools import wraps
from .utils import APPROX_BDAYS_PER_MONTH

def plotting_context(func):
    """Decorator to set plotting context during function call."""
    @wraps(func)
    def call_w_context(*args, **kwargs):
        set_context = kwargs.pop('set_context', True)
        if set_context:
            with context():
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return call_w_context

def plot_rolling_returns(returns, factor_returns=None, live_start_date=None, cone_std=None, legend_loc='best',
                         volatility_match=False, cone_function=timeseries.forecast_cone_bootstrap, ax=None, **kwargs):
    """
    Plots cumulative rolling returns versus some benchmarks'.

    Backtest returns are in green, and out-of-sample (live trading)
    returns are in red.

    Additionally, a non-parametric cone plot may be added to the
    out-of-sample returns region.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series, optional
        Daily noncumulative returns of a risk factor.
         - This is in the same style as returns.
    live_start_date : datetime, optional
        The date when the strategy began live trading, after
        its backtest period. This date should be normalized.
    cone_std : float, or tuple, optional
        If float, The standard deviation to use for the cone plots.
        If tuple, Tuple of standard deviation values to use for the cone plots
         - See timeseries.forecast_cone_bounds for more details.
    legend_loc : matplotlib.loc, optional
        The location of the legend on the plot.
    volatility_match : bool, optional
        Whether to normalize the volatility of the returns to those of the
        benchmark returns. This helps compare strategies with different
        volatilities. Requires passing of benchmark_rets.
    cone_function : function, optional
        Function to use when generating forecast probability cone.
        The function signiture must follow the form:
        def cone(in_sample_returns (pd.Series),
                 days_to_project_forward (int),
                 cone_std= (float, or tuple),
                 starting_value= (int, or float))
        See timeseries.forecast_cone_bootstrap for an example.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.
    **kwargs, optional
        Passed to plotting function.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.

"""
    if ax is None:
        ax = plt.gca()

    ax.set_ylabel('Cumulative returns')
    ax.set_xlabel('')

    benchmark_rets = utils.get_symbol_rets('SPY')
    benchmark_rets.index = pd.DatetimeIndex([i.replace(tzinfo=None) for i in benchmark_rets.index])
    # If the strategy's history is longer than the benchmark's, limit the strategy
    if returns.index[0] < benchmark_rets.index[0]:
        returns = returns[returns.index > benchmark_rets.index[0]]

    if volatility_match and factor_returns is None:
        raise ValueError('volatility_match requires passing of'
                         'factor_returns.')
    elif volatility_match and factor_returns is not None:
        bmark_vol = factor_returns.loc[returns.index].std()
        returns = (returns / returns.std()) * bmark_vol

    cum_rets = timeseries.cum_returns(returns, 1.0)
    # y_axis_formatter = FuncFormatter(utils.percentage)
    # ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    if factor_returns is None:
        factor_returns = benchmark_rets
    # if factor_returns is not None:
    cum_factor_returns = timeseries.cum_returns(factor_returns[cum_rets.index], 1.0)
    cum_factor_returns.plot(lw=2, color='gray',label=factor_returns.name, alpha=0.60,
                            ax=ax, **kwargs)
    if live_start_date is not None:
        live_start_date = utils.get_utc_timestamp(live_start_date)
        is_cum_returns = cum_rets.loc[cum_rets.index < live_start_date]
        oos_cum_returns = cum_rets.loc[cum_rets.index >= live_start_date]
    else:
        is_cum_returns = cum_rets
        oos_cum_returns = pd.Series([])
    is_cum_returns.plot(lw=3, color='forestgreen', alpha=0.6, label='Backtest', ax=ax, **kwargs)
    if len(oos_cum_returns) > 0:
        oos_cum_returns.plot(lw=4, color='red', alpha=0.6, label='Live', ax=ax, **kwargs)
        if cone_std is not None:
            if isinstance(cone_std, (float, int)):
                cone_std = [cone_std]
            is_returns = returns.loc[returns.index < live_start_date]
            cone_bounds = cone_function(
                is_returns,
                len(oos_cum_returns),
                cone_std=cone_std,
                starting_value=is_cum_returns[-1])
            cone_bounds = cone_bounds.set_index(oos_cum_returns.index)
            for std in cone_std:
                ax.fill_between(cone_bounds.index,
                                cone_bounds[float(std)],
                                cone_bounds[float(-std)],
                                color='steelblue', alpha=0.5)
    if legend_loc is not None:
        ax.legend(loc=legend_loc)
    ax.axhline(1.0, linestyle='--', color='black', lw=2)
    return ax

def plot_holdings(returns, positions, legend_loc='best', ax=None, **kwargs):
    """Plots total amount of stocks with an active position, either short
    or long (for ONE symbol).

    Displays daily total, daily average per month, and all-time daily
    average.

    Parameters
    ----------
     returns : pd.Series
            Daily returns of the strategy, noncumulative.
             - Time series with decimal returns.
             - Example:
                2015-07-16    -0.012143
                2015-07-17    0.045350
                2015-07-20    0.030957
                2015-07-21    0.004902
    positions : pd.DataFrame, optional
        Daily net position values (for ONE symbol).
         - Time series of dollar amount invested in each position and cash.
         - Days where stocks are not held can be represented by 0 or NaN.
         - Non-working capital is labelled 'cash'
         - Example:
            index         'AAPL'          cash
            2004-01-09    13939.3800      711.5585
            2004-01-12    14492.6300      27.1821
            2004-01-13    -13853.2800     -43.6375
    legend_loc : matplotlib.loc, optional
        The location of the legend on the plot.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.
    **kwargs, optional
        Passed to plotting function.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.

    """
    if ax is None:
        ax = plt.gca()
    df_holdings = positions.copy().drop('cash', axis='columns')
    symbol = df_holdings.keys()[0]
    df_holdings_by_month = df_holdings.resample('1M', how='mean')
    df_holdings.plot(color='steelblue', alpha=0.6, lw=0.5, ax=ax, **kwargs)
    df_holdings_by_month.plot(
        color='orangered',
        alpha=0.5,
        lw=2,
        ax=ax,
        **kwargs)
    ax.axhline(
        df_holdings.values.mean(),
        color='steelblue',
        ls='--',
        lw=3,
        alpha=1.0)
    ax.set_xlim((returns.index[0], returns.index[-1]))
    ax.legend(['{} Daily holdings'.format(symbol),
               '{} Average daily holdings, by month'.format(symbol),
               '{} Average daily holdings, net'.format(symbol)],
              loc=legend_loc)
    ax.set_title('{} Holdings per Day'.format(symbol))
    ax.set_ylabel('{} Amount of holdings per day'.format(symbol))
    ax.set_xlabel('')
    return ax

def show_perf_stats(returns, factor_returns, live_start_date=None,
                    bootstrap=False):
    """Prints some performance metrics of the strategy.

    - Shows amount of time the strategy has been run in backtest and
      out-of-sample (in live trading).

    - Shows Omega ratio, max drawdown, Calmar ratio, annual return,
      stability, Sharpe ratio, annual volatility, alpha, and beta.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    live_start_date : datetime, optional
        The point in time when the strategy began live trading, after
        its backtest period.
    factor_returns : pd.Series
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
    bootstrap : boolean (optional)
        Whether to perform bootstrap analysis for the performance
        metrics.
         - For more information, see timeseries.perf_stats_bootstrap

    """

    if bootstrap:
        perf_func = timeseries.perf_stats_bootstrap
    else:
        perf_func = timeseries.perf_stats

    if live_start_date is not None:
        live_start_date = utils.get_utc_timestamp(live_start_date)
        returns_backtest = returns[returns.index < live_start_date]
        returns_live = returns[returns.index > live_start_date]

        perf_stats_live = perf_func(
            returns_live,
            factor_returns=factor_returns)

        perf_stats_all = perf_func(
            returns,
            factor_returns=factor_returns)

        print('Out-of-Sample Months: ' +
              str(int(len(returns_live) / APPROX_BDAYS_PER_MONTH)))
    else:
        returns_backtest = returns

    print('Backtest Months: ' +
          str(int(len(returns_backtest) / APPROX_BDAYS_PER_MONTH)))

    perf_stats = perf_func(
        returns_backtest,
        factor_returns=factor_returns)

    if live_start_date is not None:
        perf_stats = pd.concat(OrderedDict([
            ('Backtest', perf_stats),
            ('Out of sample', perf_stats_live),
            ('All history', perf_stats_all),
        ]), axis=1)
    else:
        perf_stats = pd.DataFrame(perf_stats, columns=['Backtest'])

    utils.print_table(perf_stats, name='Performance statistics',
                      fmt='{0:.2f}')

def context(context='notebook', font_scale=1.5, rc=None):
    """Create pyfolio default plotting style context.

    Under the hood, calls and returns seaborn.plotting_context() with
    some custom settings. Usually you would use in a with-context.

    Parameters
    ----------
    context : str, optional
        Name of seaborn context.
    font_scale : float, optional
        Scale font by factor font_scale.
    rc : dict, optional
        Config flags.
        By default, {'lines.linewidth': 1.5,
                     'axes.facecolor': '0.995',
                     'figure.facecolor': '0.97'}
        is being used and will be added to any
        rc passed in, unless explicitly overriden.

    Returns
    -------
    seaborn plotting context

    Example
    -------
    >>> with pyfolio.plotting.context(font_scale=2):
    >>>    pyfolio.create_full_tear_sheet()

    See also
    --------
    For more information, see seaborn.plotting_context().

"""
    if rc is None:
        rc = {}

    rc_default = {'lines.linewidth': 1.5,
                  'axes.facecolor': '0.995',
                  'figure.facecolor': '0.97'}

    # Add defaults if they do not exist
    for name, val in rc_default.items():
        rc.setdefault(name, val)

    return sns.plotting_context(context=context, font_scale=font_scale,
                                rc=rc)
