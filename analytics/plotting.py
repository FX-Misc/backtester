import matplotlib.pyplot as plt

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
