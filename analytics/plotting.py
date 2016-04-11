import pos
import utils
import timeseries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from functools import wraps
from collections import OrderedDict
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
        raise ValueError('volatility_match requires passing of factor_returns.')
    elif volatility_match and factor_returns is not None:
        bmark_vol = factor_returns.loc[returns.index].std()
        returns = (returns / returns.std()) * bmark_vol
    cum_rets = timeseries.cum_returns(returns, 1.0)
    if factor_returns is None:
        factor_returns = benchmark_rets
    cum_factor_returns = timeseries.cum_returns(factor_returns[cum_rets.index], 1.0)
    cum_factor_returns.plot(lw=2, color='gray',label=factor_returns.name, alpha=0.60, ax=ax, **kwargs)
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


def plot_rolling_beta(returns, factor_returns, legend_loc='best', ax=None, **kwargs):
    """
    Plots the rolling 6-month and 12-month beta versus date.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series, optional
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
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

    y_axis_formatter = FuncFormatter(utils.one_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    ax.set_title("Rolling Portfolio Beta to " + str(factor_returns.name))
    ax.set_ylabel('Beta')
    rb_1 = timeseries.rolling_beta(
        returns, factor_returns, rolling_window=APPROX_BDAYS_PER_MONTH * 6)
    rb_1.plot(color='steelblue', lw=3, alpha=0.6, ax=ax, **kwargs)
    rb_2 = timeseries.rolling_beta(
        returns, factor_returns, rolling_window=APPROX_BDAYS_PER_MONTH * 12)
    rb_2.plot(color='grey', lw=3, alpha=0.4, ax=ax, **kwargs)
    ax.set_ylim((-2.5, 2.5))
    ax.axhline(rb_1.mean(), color='steelblue', linestyle='--', lw=3)
    ax.axhline(0.0, color='black', linestyle='-', lw=2)

    ax.set_xlabel('')
    ax.legend(['6-mo',
               '12-mo'],
              loc=legend_loc)
    return ax


def plot_rolling_sharpe(returns, rolling_window=APPROX_BDAYS_PER_MONTH * 6, legend_loc='best', ax=None, **kwargs):
    """
    Plots the rolling Sharpe ratio versus date.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    rolling_window : int, optional
        The days window over which to compute the sharpe ratio.
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

    y_axis_formatter = FuncFormatter(utils.one_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    rolling_sharpe_ts = timeseries.rolling_sharpe(
        returns, rolling_window)
    rolling_sharpe_ts.plot(alpha=.7, lw=3, color='orangered', ax=ax,
                           **kwargs)

    ax.set_title('Rolling Sharpe ratio (6-month)')
    ax.axhline(
        rolling_sharpe_ts.mean(),
        color='steelblue',
        linestyle='--',
        lw=3)
    ax.axhline(0.0, color='black', linestyle='-', lw=3)

    ax.set_ylim((-3.0, 6.0))
    ax.set_ylabel('Sharpe ratio')
    ax.set_xlabel('')
    ax.legend(['Sharpe', 'Average'],
              loc=legend_loc)
    return ax


def plot_drawdown_periods(returns, top=10, ax=None, **kwargs):
    """
    Plots cumulative returns highlighting top drawdown periods.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    top : int, optional
        Amount of top drawdowns periods to plot (default 10).
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

    y_axis_formatter = FuncFormatter(utils.one_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    df_cum_rets = timeseries.cum_returns(returns, starting_value=1.0)
    df_drawdowns = timeseries.gen_drawdown_table(returns, top=top)

    df_cum_rets.plot(ax=ax, **kwargs)

    lim = ax.get_ylim()
    colors = sns.cubehelix_palette(len(df_drawdowns))[::-1]
    for i, (peak, recovery) in df_drawdowns[
            ['peak date', 'recovery date']].iterrows():
        if pd.isnull(recovery):
            recovery = returns.index[-1]
        ax.fill_between((peak, recovery),
                        lim[0],
                        lim[1],
                        alpha=.4,
                        color=colors[i])

    ax.set_title('Top %i Drawdown Periods' % top)
    ax.set_ylabel('Cumulative returns')
    ax.legend(['Portfolio'], loc='upper left')
    ax.set_xlabel('')
    return ax


def plot_drawdown_underwater(returns, ax=None, **kwargs):
    """Plots how far underwaterr returns are over time, or plots current
    drawdown vs. date.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
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

    y_axis_formatter = FuncFormatter(utils.percentage)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    df_cum_rets = timeseries.cum_returns(returns, starting_value=1.0)
    running_max = np.maximum.accumulate(df_cum_rets)
    underwater = -100 * ((running_max - df_cum_rets) / running_max)
    (underwater).plot(ax=ax, kind='area', color='coral', alpha=0.7, **kwargs)
    ax.set_ylabel('Drawdown')
    ax.set_title('Underwater Plot')
    ax.set_xlabel('')
    return ax


def show_worst_drawdown_periods(returns, top=5):
    """Prints information about the worst drawdown periods.

    Prints peak dates, valley dates, recovery dates, and net
    drawdowns.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    top : int, optional
        Amount of top drawdowns periods to plot (default 5).

    """

    drawdown_df = timeseries.gen_drawdown_table(returns, top=top)
    utils.print_table(drawdown_df.sort('net drawdown in %', ascending=False),
                      name='Worst Drawdown Periods', fmt='{0:.2f}')


def plot_gross_leverage(returns, gross_lev, ax=None, **kwargs):
    """Plots gross leverage versus date.

    Gross leverage is the sum of long and short exposure per share
    divided by net asset value.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    gross_lev : pd.Series, optional
        The leverage of a strategy.
         - See full explanation in tears.create_full_tear_sheet.
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

    gross_lev.plot(alpha=0.8, lw=0.5, color='g', legend=False, ax=ax,
                   **kwargs)

    ax.axhline(gross_lev.mean(), color='g', linestyle='--', lw=3,
               alpha=1.0)

    ax.set_title('Gross Leverage')
    ax.set_ylabel('Gross Leverage')
    ax.set_xlabel('')
    return ax


def plot_exposures(returns, positions_alloc, ax=None, **kwargs):
    """Plots a cake chart of the long and short exposure.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    positions_alloc : pd.DataFrame
        Portfolio allocation of positions. See
        pos.get_percent_alloc.
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

    df_long_short = pos.get_long_short_pos(positions_alloc)

    df_long_short.plot(
        kind='area', color=['lightblue', 'green'], alpha=1.0,
        ax=ax, **kwargs)
    df_cum_rets = timeseries.cum_returns(returns, starting_value=1)
    ax.set_xlim((df_cum_rets.index[0], df_cum_rets.index[-1]))
    ax.set_title("Long/Short Exposure")
    ax.set_ylabel('Exposure')
    ax.set_xlabel('')
    return ax


def show_and_plot_top_positions(returns, positions_alloc,show_and_plot=2, hide_positions=False, legend_loc='real_best',
                                ax=None, **kwargs):
    """Prints and/or plots the exposures of the top 10 held positions of
    all time.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    positions_alloc : pd.DataFrame
        Portfolio allocation of positions. See pos.get_percent_alloc.
    show_and_plot : int, optional
        By default, this is 2, and both prints and plots.
        If this is 0, it will only plot; if 1, it will only print.
    hide_positions : bool, optional
        If True, will not output any symbol names.
    legend_loc : matplotlib.loc, optional
        The location of the legend on the plot.
        By default, the legend will display below the plot.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.
    **kwargs, optional
        Passed to plotting function.

    Returns
    -------
    ax : matplotlib.Axes, conditional
        The axes that were plotted on.

    """

    df_top_long, df_top_short, df_top_abs = pos.get_top_long_short_abs(
        positions_alloc)

    if show_and_plot == 1 or show_and_plot == 2:
        utils.print_table(pd.DataFrame(df_top_long * 100, columns=['max']),
                          fmt='{0:.2f}%',
                          name='Top 10 long positions of all time')

        utils.print_table(pd.DataFrame(df_top_short * 100, columns=['max']),
                          fmt='{0:.2f}%',
                          name='Top 10 short positions of all time')

        utils.print_table(pd.DataFrame(df_top_abs * 100, columns=['max']),
                          fmt='{0:.2f}%',
                          name='Top 10 positions of all time')

        _, _, df_top_abs_all = pos.get_top_long_short_abs(
            positions_alloc, top=9999)
        utils.print_table(pd.DataFrame(df_top_abs_all * 100, columns=['max']),
                          fmt='{0:.2f}%',
                          name='All positions ever held')

    if show_and_plot == 0 or show_and_plot == 2:

        if ax is None:
            ax = plt.gca()

        positions_alloc[df_top_abs.index].plot(
            title='Portfolio Allocation Over Time, Only Top 10 Holdings',
            alpha=0.4, ax=ax, **kwargs)

        # Place legend below plot, shrink plot by 20%
        if legend_loc == 'real_best':
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

            # Put a legend below current axis
            ax.legend(
                loc='upper center', frameon=True, bbox_to_anchor=(
                    0.5, -0.14), ncol=5)
        else:
            ax.legend(loc=legend_loc)

        df_cum_rets = timeseries.cum_returns(returns, starting_value=1)
        ax.set_xlim((df_cum_rets.index[0], df_cum_rets.index[-1]))
        ax.set_ylabel('Exposure by stock')

        if hide_positions:
            ax.legend_.remove()

        return ax


def plot_max_median_position_concentration(positions, ax=None, **kwargs):
    """
    Plots the max and median of long and short position concentrations
    over the time.

    Parameters
    ----------
    positions : pd.DataFrame
        The positions that the strategy takes over time.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.
    """
    if ax is None:
        ax = plt.gcf()

    alloc_summary = pos.get_max_median_position_concentration(positions)
    colors = ['mediumblue', 'steelblue', 'tomato', 'firebrick']
    alloc_summary.plot(linewidth=1, color=colors, alpha=0.6, ax=ax)

    ax.legend(loc='center left')
    ax.set_ylabel('Exposure')
    ax.set_title('Long/Short Max and Median Position Concentration')

    return ax


def show_perf_stats(returns, factor_returns, live_start_date=None, bootstrap=False):
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


def context(context='notebook', font_scale=1.0, rc=None):
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

    rc_default = {'lines.linewidth': 1.0,
                  'axes.facecolor': '0.995',
                  'figure.facecolor': '0.97',}

    # Add defaults if they do not exist
    print rc_default.items()
    for name, val in rc_default.items():
        rc.setdefault(name, val)
    return sns.plotting_context(context=context, font_scale=font_scale, rc=rc)
