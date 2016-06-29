import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import prediction.featutils as featutils


apply_n_times = lambda f, n, x: reduce(lambda x, y: f(x), range(n), x)
ROOT_DIR = apply_n_times(os.path.dirname, 3, os.path.realpath(__file__))
FIGS_DIR = os.path.join(ROOT_DIR, 'figs')


def _get_file_path(title, overwrite):
    i = 1
    fpath = os.path.join(FIGS_DIR, "{}.png".format(title))

    while os.path.exists(fpath) and not overwrite:
        fpath = os.path.join(FIGS_DIR, "{} ({}).png".format(title, i))
        i += 1

    return fpath


def plot(title, labels, *args, **kwargs):
    """
    :param title: plot filename
    :param labels: list of lists, each sublist is a list of label names for the corresponding subplot, of None if no label
    :param args: variable args are list of series to plot.  Each list corresponds to a subplot
    :param kwargs:
        overwrite - if true overwrite, else append integer to filename
    :return:
    """
    overwrite = kwargs.get('overwrite', False)
    plot_type = kwargs.get('type', 'line')
    x = kwargs.get('x', [])
    rows = len(args)
    fig, axes = plt.subplots(nrows=rows, figsize=(15.0, 10.0))
    fig.suptitle(title)
    if rows == 1:
        axes = [axes]

    for i, Y in enumerate(args):
        Y = Y if type(Y) is list else [Y]
        if labels[i] is not None:
            L = labels[i] if type(labels[i]) is list else [labels[i]]
            yes_labels = True
        else:
            L = [''] * len(Y)
            yes_labels = False
        for j, y in enumerate(Y):
            if plot_type == 'line':
                if len(x) > 0:
                    axes[i].plot(x, y, label=L[j])
                else:
                    axes[i].plot(y, label=L[j])
            else:
                raise NotImplementedError("plot_type {} not supported".format(plot_type))
        #if i == 2:
        #    ymin = np.min([np.min(y) for y in Y])
        #    ymax = np.max([np.max(y) for y in Y])
        #    axes[i].set_ylim([-0.03, 0.03])
        if yes_labels:
            h, l = axes[i].get_legend_handles_labels()
            axes[i].legend(h, l)

    fpath = _get_file_path(title, overwrite)

    if not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.dirname(fpath))

    fig.savefig(fpath)

    return fpath


def scatter(title, x, y, **kwargs):
    overwrite = kwargs.get('overwrite', False)

    fig, ax = plt.subplots(nrows=1)
    fig.suptitle(title)
    ax.scatter(x, y)

    axis_dims = kwargs.get('axis_dims', None)
    if axis_dims:
        plt.axis(axis_dims)

    fpath = _get_file_path(title, overwrite)

    if not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.dirname(fpath))

    fig.savefig(fpath)

    return fpath



def plot_backtest(title, time_series, price_series, pnl_series, orders, signals, probs, positions, overwrite=False):
    """
    Plot a backtest
    :param title:
    :param time_series:
    :param price_series:
    :param pnl_series:
    :param orders:
    :param signals:
    :param probs:
    :param overwrite:
    :return:
    """
    fig, axes = plt.subplots(nrows=5, figsize=(12.0, 10.0))

    long_orders = filter(lambda x: (x[1] > 0) and (x[2] != 0), orders)
    short_orders = filter(lambda x: (x[1] < 0) and (x[2] != 0), orders)
    flat_orders = filter(lambda x: x[2] == 0, orders)
    long_order_times = map(lambda x: x[0], long_orders)
    short_order_times = map(lambda x: x[0], short_orders)
    flat_order_times = map(lambda x: x[0], flat_orders)
    long_order_prices = map(lambda x: x[3], long_orders)
    short_order_prices = map(lambda x: x[3], short_orders)
    flat_order_prices = map(lambda x: x[3], flat_orders)

    axes[0].plot(time_series, price_series)
    axes[0].plot(long_order_times, long_order_prices, '^', ms=8, color='g')
    axes[0].plot(short_order_times, short_order_prices, 'v', ms=8, color='r')
    axes[0].plot(flat_order_times, flat_order_prices, 'x', ms=8, color='m')
    axes[0].set_title("Price and Orders")

    axes[1].plot(time_series, pnl_series, label='pnl')
    axes[1].set_title("PnL")

    axes[2].plot(time_series, signals)
    axes[2].set_title("Signals & Position")

    axes[3].plot(time_series, probs)
    axes[3].set_title("Probs")

    axes[4].plot(time_series, positions)

    fpath = _get_file_path(title, overwrite)

    if not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.dirname(fpath))

    fig.savefig(fpath)

    print "saved to {}".format(fpath)

# plt.axis([xmin,xmax,ymin,ymax])
