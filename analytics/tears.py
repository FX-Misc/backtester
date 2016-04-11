import utils
import timeseries
import plotting
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from plotting import plotting_context

@plotting_context
def create_returns_tear_sheet(returns, live_start_date=None,
                              cone_std=(1.0, 1.5, 2.0),
                              benchmark_rets=None,
                              bootstrap=False,
                              return_fig=False):
    """
    Generate a number of plots for analyzing a strategy's returns.

    - Fetches benchmarks, then creates the plots on a single figure.
    - Plots: rolling returns (with cone), rolling beta, rolling sharpe,
        rolling Fama-French risk factors, drawdowns, underwater plot, monthly
        and annual return plots, daily similarity plots,
        and return quantile box plot.
    - Will also print the start and end dates of the strategy,
        performance statistics, drawdown periods, and the return range.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in create_full_tear_sheet.
    live_start_date : datetime, optional
        The point in time when the strategy began live trading,
        after its backtest period.
    cone_std : float, or tuple, optional
        If float, The standard deviation to use for the cone plots.
        If tuple, Tuple of standard deviation values to use for the cone plots
         - The cone is a normal distribution with this standard deviation
             centered around a linear regression.
    benchmark_rets : pd.Series, optional
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
    bootstrap : boolean (optional)
        Whether to perform bootstrap analysis for the performance
        metrics. Takes a few minutes longer.
    return_fig : boolean, optional
        If True, returns the figure that was plotted on.
    set_context : boolean, optional
        If True, set default plotting style context.
    """
    if benchmark_rets is None:
        benchmark_rets = utils.get_symbol_rets('SPY')
        benchmark_rets.index = pd.DatetimeIndex([i.replace(tzinfo=None) for i in benchmark_rets.index])
        # If the strategy's history is longer than the benchmark's, limit the strategy
        if returns.index[0] < benchmark_rets.index[0]:
            returns = returns[returns.index > benchmark_rets.index[0]]

    df_cum_rets = timeseries.cum_returns(returns, starting_value=1)
    print("Entire data start date: " + str(df_cum_rets.index[0].strftime('%Y-%m-%d')))
    print("Entire data end date: " + str(df_cum_rets.index[-1].strftime('%Y-%m-%d')))
    print('\n')

    plotting.show_perf_stats(returns, benchmark_rets,
                             bootstrap=bootstrap,
                             live_start_date=live_start_date)

    if live_start_date is not None:
        vertical_sections = 11
        live_start_date = utils.get_utc_timestamp(live_start_date)
    else:
        vertical_sections = 10

    if bootstrap:
        vertical_sections += 1

    fig = plt.figure(figsize=(14, vertical_sections * 6))
    gs = gridspec.GridSpec(vertical_sections, 3, wspace=0.5, hspace=0.5)
    ax_rolling_returns = plt.subplot(gs[:2, :])
    ax_rolling_returns_vol_match = plt.subplot(gs[2, :], sharex=ax_rolling_returns)
    ax_rolling_beta = plt.subplot(gs[3, :], sharex=ax_rolling_returns)
    ax_rolling_sharpe = plt.subplot(gs[4, :], sharex=ax_rolling_returns)
    ax_rolling_risk = plt.subplot(gs[5, :], sharex=ax_rolling_returns)
    ax_drawdown = plt.subplot(gs[6, :], sharex=ax_rolling_returns)
    ax_underwater = plt.subplot(gs[7, :], sharex=ax_rolling_returns)
    ax_monthly_heatmap = plt.subplot(gs[8, 0])
    ax_annual_returns = plt.subplot(gs[8, 1])
    ax_monthly_dist = plt.subplot(gs[8, 2])
    ax_return_quantiles = plt.subplot(gs[9, :])

    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=cone_std,
        ax=ax_rolling_returns)
    ax_rolling_returns.set_title(
        'Cumulative Returns')

    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=None,
        volatility_match=True,
        legend_loc=None,
        ax=ax_rolling_returns_vol_match)
    ax_rolling_returns_vol_match.set_title(
        'Cumulative returns volatility matched to benchmark.')

    # plotting.plot_rolling_beta(
    #     returns, benchmark_rets, ax=ax_rolling_beta)
    #
    # plotting.plot_rolling_sharpe(
    #     returns, ax=ax_rolling_sharpe)
    #
    # plotting.plot_rolling_fama_french(
    #     returns, ax=ax_rolling_risk)
    #
    # # Drawdowns
    # plotting.plot_drawdown_periods(
    #     returns, top=5, ax=ax_drawdown)
    #
    # plotting.plot_drawdown_underwater(
    #     returns=returns, ax=ax_underwater)
    #
    # plotting.show_worst_drawdown_periods(returns)
    #
    # df_weekly = timeseries.aggregate_returns(returns, 'weekly')
    # df_monthly = timeseries.aggregate_returns(returns, 'monthly')
    #
    # print('\n')
    # plotting.show_return_range(returns, df_weekly)
    #
    # plotting.plot_monthly_returns_heatmap(returns, ax=ax_monthly_heatmap)
    # plotting.plot_annual_returns(returns, ax=ax_annual_returns)
    # plotting.plot_monthly_returns_dist(returns, ax=ax_monthly_dist)
    #
    # plotting.plot_return_quantiles(
    #     returns,
    #     df_weekly,
    #     df_monthly,
    #     ax=ax_return_quantiles)
    #
    # if bootstrap:
    #     ax_bootstrap = plt.subplot(gs[10, :])
    #     plotting.plot_perf_stats(returns, benchmark_rets,
    #                              ax=ax_bootstrap)

    for ax in fig.axes:
        plt.setp(ax.get_xticklabels(), visible=True)

    plt.show()
    if return_fig:
        return fig