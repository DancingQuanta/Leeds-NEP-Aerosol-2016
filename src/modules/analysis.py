#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Plotting helper functions

"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

def figsize(scale):
    fig_width_pt = 483.69687                          # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0 / 72.27                       # Convert pt to inch
    golden_mean = (np.sqrt(5.0)-1.0) / 2.0            # Aesthetic ratio (you could change this)
    fig_width = fig_width_pt * inches_per_pt*scale    # width in inches
    fig_height = fig_width * 0.80              # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size


def saveplot(path, name, kind, fig, **kwargs):
    filename = name + "-" + kind + ".png"
    path1 = os.path.join(path, filename)
    print("Plotting: %s" % (path1))
    fig.savefig(path1)
    filename = name + "-" + kind + ".pgf"
    path2 = os.path.join(path, filename)
    fig.savefig(path2, **kwargs)
    return path2.replace("\\\\", "/")


def save_latex(df, path, name, kind, **kwargs):
    """Save a DataFrame to latex table via to_latex()

    Args:
        df: Pandas.DataFrame
        path: str
            where outputfile will be saved to
        name: str
            part of filename
        kind: str
            part of filename, could be a histogram or statistics
        kwargs: **
            pass keywords unto pd.to_latex()
    Returns:
        path: str
            location and filename of saved latex file which can used to input
            into a latex document with \input(path)

    """
    latex = df.to_latex(**kwargs)
    filename = name + "-" + kind +  ".tex"
    path = os.path.join(path, filename)
    with open(path, 'w') as f:
        f.write(latex)
    return path.replace("\\\\", "/")


def nmoment(x, counts, c, n):
    return np.sum(((x-c)**n)*counts) / np.sum(counts)


def statistics(midpoints, counts):
    """Statistics for binned data

    Args:
        counts: ndarray
        midpoints: adarray

    Returns:

    """
    totalCounts = np.sum(counts)
    # Mean
    mean = nmoment(midpoints, counts, 0, 1)

    # Standard deviation
    std = nmoment(midpoints, counts, mean, 2)**0.5

    # Lower 95% bounds
    lower = mean - 2 * std

    # Upper 95% bounds
    upper = mean + 2 * std

    return mean, std, lower, upper


def geometricStd(data, bounds, gmd):
    """Calculate geometric standard deviation of a lognormal distribution
    Args:
        data : list
            list of counts per bin
        bins : list
            list of bin boundaries, with length one element longer than data
        gmd : float
            Geometric mean diameter

    Returns:
        gsd : float
            Geometric standard deviation
    """
    # Geometric standard deviation
    numerator = 0
    totalCounts = 0
    for ix, key in enumerate(data):
        counts = data[ix]
        lower = bounds[ix]
        upper = bounds[ix+1]
        difference = upper-lower
        midpoint = lower + difference/2
        logmidpoint = np.log10(midpoint)  # Is this correct? todo
        totalCounts = totalCounts + counts
        numerator = counts * ((logmidpoint - np.log10(gmd)) ** 2) + numerator

    denominator = totalCounts - 1
    loggsd = np.sqrt(numerator / denominator)
    gsd = np.exp(loggsd)

    # Lower 95% bounds
    lower = gmd / (gsd ** 2)

    # Upper 95% bounds
    upper = gmd * (gsd ** 2)

    return gsd, lower, upper


def plot(data, path, name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    data.plot(ax=ax)
    plt.ylabel('Particle count')
    plt.xlabel('Time')
    # custom_tick_labels = data.index.map(lambda t: t.strftime('%H'))
    # ax.set_xticklabels(custom_tick_labels)

    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc='upper center', mode='expand')
    art = []
    lgd = ax.legend(lines, labels, loc=9, bbox_to_anchor=(0.5, -0.2), ncol=2)
    art.append(lgd)
    kwargs = {"additional_artists": art,
              "bbox_inches": "tight"}

    plt.tight_layout()
    path = saveplot(path, name, "plot", fig, **kwargs)
    plt.close()
    return path.replace("\\\\", "/")


def twoplot(df, df1, path, name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    df.plot(ax=ax)
    df1.plot(ax=ax)
    plt.ylabel('Particle count')
    plt.xlabel('Time')
    # custom_tick_labels = data.index.map(lambda t: t.strftime('%H'))
    # ax.set_xticklabels(custom_tick_labels)

    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc='upper center', mode='expand')
    art = []
    lgd = ax.legend(lines, labels, loc=9, bbox_to_anchor=(0.5, -0.2), ncol=2)
    art.append(lgd)
    kwargs = {"additional_artists": art,
              "bbox_inches": "tight"}

    # plt.tight_layout()
    path = saveplot(path, name, "twoplot", fig, **kwargs)
    plt.close()
    return path.replace("\\\\", "/")


def histogram(data, plotspath, statspath, name):
    """Plot a histogram of a binned data with defined bin boundaries.
    Args:
        df : Pandas.DataFrame
            Input dataframe with index of datetime object and each column is a
            bin od data
        bounds : list of floats
            List of bins boundaries.
        path : str
            Path for saved plots

    Returns:
        dataDict: dict
            dictionary of plots paths, statistics
    """

    # Load data
    df = data['data']
    bounds = data['bounds']

    # Initialise new dict for data output
    dataDict = {}
    dataDict['histplot'] = {}

    # Initialise new series
    columns = ["lower", "upper", "width", "midpoint",
               "loglower", "logupper", "logwidth", "logmidpoint",
               'Counts', 'Cum Counts', 'Density', "dN/logD"]
    df1 = pd.DataFrame(columns=columns)

    # Take a mean of the input dataframe which becomes a series with column
    df1['Counts'] = df.mean(axis=0)
    totalCounts = df1['Counts'].sum()

    df1["lower"] = bounds[:-1]
    df1["upper"] = bounds[1:]
    df1["width"] = df1["upper"] - df1["lower"]
    df1["midpoint"] = df1["width"]/2 + df1["lower"]
    df1["loglower"] = np.log10(df1["lower"])
    df1["logupper"] = np.log10(df1["upper"])
    df1["logwidth"] = df1["logupper"] - df1["loglower"]
    df1["logmidpoint"] = np.log10(df1["midpoint"])
    df1["Density"] = df1["Counts"] / df1["width"]
    df1["dN/logD"] = df1["Counts"] / df1["logwidth"]

    # Iterate through the bins
    bins = df1.index
    cumCounts = 0
    for ix, key in enumerate(bins):
        counts = df1['Counts'].iloc[ix]
        lower = df1['lower'].iloc[ix]
        width = df1["width"].iloc[ix]

        # Cumulative frequency
        lowerCumCounts = cumCounts
        cumCounts += counts
        upperCumCounts = cumCounts
        df1['Cum Counts'].iloc[ix] = cumCounts

        # Median
        if lowerCumCounts < totalCounts/2 < upperCumCounts:
            median = lower + ((totalCounts/2 - lowerCumCounts)/counts) * width

    # Statistics
    counts = df1['Counts'].values
    midpoints = df1["midpoint"].values
    # logmidpoints = np.log10(midpoints)

    # Normal distribution
    mean, std, lower, upper = statistics(midpoints, counts)

    # Log normal distribution
    gm, gstd, glower, gupper = np.exp(statistics(np.log(midpoints), counts))

    # Sometimes a median is not found and so need to be excluded from display
    if 'median' in locals():
        index = ['Median',
                 'Mean Diameter', 'Std', '95% lower', '95% upper',
                 'Geometric mean diameter', 'Geometric standard deviation',
                 'Geometric 95% lower', 'Geometric 95% upper']
        statsdata = [median,
                     mean, std, lower, upper,
                     gm, std, glower, gupper]
    else:
        index = ['Mean Diameter', 'Std', '95% lower', '95% upper',
                 'Geometric mean diameter', 'Geometric standard deviation',
                 'Geometric 95% lower', 'Geometric 95% upper']
        statsdata = [mean, std, lower, upper,
                     gm, std, glower, gupper]

    statsdf = pd.DataFrame(statsdata, index=index)
    columns = ['Counts', 'Cum Counts', 'Density']

    dataDict['histstats'] = save_latex(statsdf, statspath,
                                       name, "histstats", header=False)
    dataDict['histdata'] = save_latex(df1[columns], statspath,
                                      name, "histdata")

    # Plots
    x1 = df1["lower"].tolist()  # left edge
    x2 = df1["upper"].tolist()  # right edge
    w = np.array(x2)-np.array(x1)  # variable width
    y = df1['Density'].tolist()

    # plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x1, y, width=w)

    # # find minimum and maximum of xticks, so we know
    # # where we should compute theoretical distribution
    # xt = plt.xticks()[0]
    # xmin, xmax = min(xt), max(xt)
    # lnspc = np.linspace(xmin, xmax, len(y))
    # pdf_g = stats.norm.pdf(lnspc, mean, std)
    # ax.plot(lnspc, pdf_g, label="Norm")

    plt.ylabel(r'Frequency per $\mu$')
    plt.xlabel(r'\textbf{Diameter} / $\mu$')
    path1 = saveplot(plotspath, name, "hist", fig)
    dataDict['histplot']["hist"] = path1
    plt.close()

    # Cumulative distribution
    y = df1['Cum Counts'].tolist()

    fig = plt.figure()
    plt.plot(x1, y)
    plt.ylabel(r'Cumulative frequency')
    plt.xlabel(r'\textbf{Diameter} / $\mu$')
    path1 = saveplot(plotspath, name, "cumFreq", fig)
    dataDict['histplot']["cumFreq"] = path1
    plt.close()

    # x1 = df1["loglower"].tolist() # left edge
    # x2 = df1["logupper"].tolist() # right edge
    # w = np.array(x2)-np.array(x1) # variable width
    y = df1["dN/logD"].tolist()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x1, y, width=w)
    ax.set_xscale('log')

    # # find minimum and maximum of xticks, so we know
    # # where we should compute theoretical distribution
    # xt = plt.xticks()[0]
    # xmin, xmax = min(xt), max(xt)
    # lnspc = np.linspace(xmin, xmax, len(y))
    # pdf_g = stats.norm.pdf(lnspc, gm, gstd)
    # ax.plot(lnspc, pdf_g, label="Norm")

    plt.ylabel(r'Frequency per $\log \mu$')
    plt.xlabel(r'$\log \mathbf{Diameter}$ / $\mu$')
    path1 = saveplot(plotspath, name, "histlog", fig)
    dataDict['histplot']["histlog"] = path1
    # plt.clf()
    plt.close()
    return dataDict


def plot_corr(df, plotspath, statspath, name, size=14):
    """Function plots a graphical correlation matrix for each pair
    of columns in the dataframe.

    Args:
        df (Pandas.DataFrame):
        path (str): Path for figure to be saved to.
        size (int): vertical and horizontal size of the plot
    """
    # Correlation analysis
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(corr)
    locs, labels = plt.xticks(range(len(corr.columns)), corr.columns)
    plt.setp(labels, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    path1 = saveplot(plotspath, name, "corr", fig)
    print("Saved correlations graph")
    plt.clf()

    # corr[corr<threshold] = np.nan
    # corr.fillna(0, inplace = True)
    filename = name + "-corr.csv"
    path = os.path.join(statspath, filename)
    corr.to_csv(path)

    # Covariance analysis
    cov = df.cov()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(cov)
    locs, labels = plt.xticks(range(len(cov.columns)), cov.columns)
    plt.setp(labels, rotation=90)
    plt.yticks(range(len(cov.columns)), cov.columns)
    path1 = saveplot(plotspath, name, "cov", fig)
    print("Saved covariations graph")


def make_scatter_plot(df, path, name):
    """
    Make scatterplot of a dataframe

    Args:
        df (Pandas.DataFrame):
        path (str): Path for figure to be saved to.

    """
    plt.clf()
    fig = plt.figure()
    axs = pd.scatter_matrix(df, alpha=0.2)
    for ax in axs[:, 0]:  # the left boundary
        ax.grid('off', axis='both')
        # ax.set_yticks([0, .5])

    for ax in axs[-1, :]:  # the lower boundary
        ax.grid('off', axis='both')
        # ax.set_xticks([0, .5])
    path1 = saveplot(path, name, "scatter-matrix", fig)


def scatter_matrix(df, path, name):
    fig, axarr = plt.subplots(4, 4, sharex=True)

    x = df.columns[0]
    print(x)
    for i, ax in enumerate(fig.axes):
        y = df.columns[i + 2]
        print(y)
        df.plot(x=x, y=y, ax=ax, kind='scatter')

    # # the left boundary
    # axarr[:, 0].grid('off', axis='both')
    # axarr[:, 0].set_yticks([0, .5])

    # # the lower boundary
    # axarr[-1, :].grid('off', axis='both')
    # axarr[-1, :].set_xticks([0,  .5])
    path1 = saveplot(path, name, "scatter-matrix", fig)


def scatter_plot(df, path, name):
    filename = name + "-scatter.pdf"
    path = os.path.join(path, filename)
    for x in df.columns:
        for y in df.columns:
            df.plot(x=x, y=y, kind='scatter')
            filename = "%s_%s_%s" % (x, y, name)
            plt.savefig(os.path.join(path, filename))


def compare(data, path):
    plot_corr(data, path)
    # scatter_plot(data, path)


def calibrate(df):
    """Calibrate a dataset by other dataset.
    Each dataset is a time series histogram with defined bin boundaries.
    Both datasets must share same bin boundaries.
    The value of a bin of a dataset is divided by a value of same bin of
    different dataset to find a multiplicative calibration factor between two
    dataset for that bin.

    Args:
        df: Pandas.DataFrame
            Input dataframe consisting of two datasets, where each column is a
            bin. For two bins dataset, the dataframe will have four columns, of
            which two belonged to one dataset and other two belonged to another
            dataset.
            The leftmost dataset will be divided by the rightmost dataset.
    Returns:
        df: Pandas.DataFrame
            Output DataFrame is a superset of input dataframe with additional
            columns which are calibration factors for each bin over time.
    """
    columns = df.columns
    for i, a in enumerate(columns):
        for j, b in enumerate(columns[i:]):
            sensor1, bin1 = a.split('-')
            sensor2, bin2 = b.split('-')
            if bin1 == bin2 and sensor1 != sensor2:
                # Ensure the bins are same but sensors are different
                c = "%s/%s-%s" % (sensor1, sensor2, bin1)
                df[c] = df[a] / df[b]

    # Sometimes there are zero counts so will yield NaN or Inf
    df = df.fillna(0)
    df = df.replace(np.inf, 0)
    return df
