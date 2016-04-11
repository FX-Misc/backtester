import utils
import timeseries
import plotting
import pos
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
from plotting import plotting_context

@plotting_context
def create_returns_tear_sheet(returns, live_start_date=None, cone_std=(1.0, 1.5, 2.0), benchmark_rets=None,
                              bootstrap=False, return_fig=False):
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
    matplotlib.rc('font', size=6)
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
    plotting.show_perf_stats(returns, benchmark_rets, bootstrap=bootstrap, live_start_date=live_start_date)
    fig = plt.figure(figsize=(16, 12))
    ax_rolling_returns = plt.subplot(4, 1, 1, label='small')
    ax_rolling_returns_vol_match = plt.subplot(4,1,2, sharex=ax_rolling_returns)
    ax_drawdown = plt.subplot(4, 1, 3, sharex=ax_rolling_returns)
    ax_underwater = plt.subplot(4, 1, 4, sharex=ax_rolling_returns)
    # ax_rolling_beta = plt.subplot(4, 1, 3, sharex=ax_rolling_returns)
    # ax_rolling_sharpe = plt.subplot(4, 1, 4, sharex=ax_rolling_returns)
    # ax_rolling_risk = plt.subplot(gs[5, :], sharex=ax_rolling_returns)
    # ax_monthly_heatmap = plt.subplot(gs[8, 0])
    # ax_annual_returns = plt.subplot(gs[8, 1])
    # ax_monthly_dist = plt.subplot(gs[8, 2])
    # ax_return_quantiles = plt.subplot(gs[9, :])

    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=cone_std,
        ax=ax_rolling_returns)
    ax_rolling_returns.set_title(
        'cum Returns')

    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=None,
        volatility_match=True,
        legend_loc=None,
        ax=ax_rolling_returns_vol_match)
    ax_rolling_returns_vol_match.set_title(
        'cum returns, vol matched to benchmark.')

    # plotting.plot_rolling_beta(
    #     returns, benchmark_rets, ax=ax_rolling_beta)
    #
    # plotting.plot_rolling_sharpe(
    #     returns, ax=ax_rolling_sharpe)

    # plotting.plot_rolling_fama_french(
    #     returns, ax=ax_rolling_risk)

    # Drawdowns
    plotting.plot_drawdown_periods(returns, top=5, ax=ax_drawdown)
    plotting.plot_drawdown_underwater(returns=returns, ax=ax_underwater)
    plotting.show_worst_drawdown_periods(returns)

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

@plotting_context
def create_position_tear_sheet(returns, positions, gross_lev=None,
                               show_and_plot_top_pos=2, hide_positions=False,
                               return_fig=False, sector_mappings=None):
    """
    Generate a number of plots for analyzing a
    strategy's positions and holdings.

    - Plots: gross leverage, exposures, top positions, and holdings.
    - Will also print the top positions held.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in create_full_tear_sheet.
    positions : pd.DataFrame
        Daily net position values.
         - See full explanation in create_full_tear_sheet.
    gross_lev : pd.Series, optional
        The leverage of a strategy.
         - See full explanation in create_full_tear_sheet.
    show_and_plot_top_pos : int, optional
        By default, this is 2, and both prints and plots the
        top 10 positions.
        If this is 0, it will only plot; if 1, it will only print.
    hide_positions : bool, optional
        If True, will not output any symbol names.
        Overrides show_and_plot_top_pos to 0 to suppress text output.
    return_fig : boolean, optional
        If True, returns the figure that was plotted on.
    set_context : boolean, optional
        If True, set default plotting style context.
    sector_mappings : dict or pd.Series, optional
        Security identifier to sector mapping.
        Security ids as keys, sectors as values.
    """
    matplotlib.rc('font', size=6)
    if hide_positions:
        show_and_plot_top_pos = 0

    fig = plt.figure(figsize=(16,12))
    ax_gross_leverage = plt.subplot(5,1,5)
    ax_exposures = plt.subplot(5,1,2, sharex=ax_gross_leverage)
    ax_top_positions = plt.subplot(5, 1, 4, sharex=ax_gross_leverage)
    ax_max_median_pos = plt.subplot(5, 1, 3, sharex=ax_gross_leverage)
    ax_holdings = plt.subplot(5, 1, 1, sharex=ax_gross_leverage)

    positions_alloc = pos.get_percent_alloc(positions)
    if gross_lev is not None:
        plotting.plot_gross_leverage(returns, gross_lev, ax=ax_gross_leverage)

    plotting.plot_exposures(returns, positions_alloc, ax=ax_exposures)

    plotting.show_and_plot_top_positions(
        returns,
        positions_alloc,
        show_and_plot=show_and_plot_top_pos,
        hide_positions=hide_positions,
        ax=ax_top_positions)

    plotting.plot_max_median_position_concentration(positions,ax=ax_max_median_pos)
    plotting.plot_holdings(returns, positions_alloc, ax=ax_holdings)

    # if sector_mappings is not None:
    #     sector_exposures = pos.get_sector_exposures(positions, sector_mappings)
    #     if len(sector_exposures.columns) > 1:
    #         sector_alloc = pos.get_percent_alloc(sector_exposures)
    #         sector_alloc = sector_alloc.drop('cash', axis='columns')
    #         ax_sector_alloc = plt.subplot(gs[5, :], sharex=ax_gross_leverage)
    #         plotting.plot_sector_allocations(returns, sector_alloc,
    #                                          ax=ax_sector_alloc)
    for ax in fig.axes:
        plt.setp(ax.get_xticklabels(), visible=True)

    plt.show()
    if return_fig:
        return fig
