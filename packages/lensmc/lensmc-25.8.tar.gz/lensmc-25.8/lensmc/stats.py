"""
LensMC - a Python package for weak lensing shear measurements.
This is a module containing stats functions for lensmc.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.stats import binned_statistic, mstats


def draw_samples_from_cdf(cdf, x, n, seed=None):
    """
    Draw samples from a 1d empirical cumulative distribution function using the inverse transform method.

    :type cdf: ndarray
    :type x: ndarray
    :type n: float
    :type seed: see https://numpy.org/doc/stable/reference/random/generator.html
    :rtype: ndarray
    """

    # check for invertibility
    # cdf_unique, ix = np.unique(cdf, return_index=True)

    # inverse cdf as a function of uniform variable
    # icdf_fcn = lambda u: np.interp(u, cdf_unique, x[ix])
    icdf_fcn = interp1d(cdf, x)

    # initialise the RNG
    rng = np.random.default_rng(seed)

    # generate samples
    u = rng.random(n)

    return icdf_fcn(u)


def binned_scatter(x, y, statistic='mean', bins=10):
    """
    Make a binned scatter between variable x and y, with edges in xbins and ybins.
    :type x: ndarray
    :type y: ndarray
    :type statistic: str
    :type bins: int or list
    :rtype: ndarray
    """

    # counts
    nx, _, _ = binned_statistic(x, x, statistic='count', bins=bins)
    ny, _, _ = binned_statistic(x, y, statistic='count', bins=bins)

    # means
    xmean, _, _ = binned_statistic(x, x, statistic=statistic, bins=bins)
    ymean, _, _ = binned_statistic(x, y, statistic=statistic, bins=bins)

    # errors
    if statistic == 'median':
        err_fcn = lambda x: 1.4826 * np.median(np.abs(x - np.median(x)))
    else:
        err_fcn = 'std'
    xerr, _, _ = binned_statistic(x, x, statistic=err_fcn, bins=bins)
    yerr, _, _ = binned_statistic(x, y, statistic=err_fcn, bins=bins)

    # xerr[nx != 0] /= np.sqrt(nx[nx != 0])
    # yerr[ny != 0] /= np.sqrt(ny[ny != 0])
    xerr[nx == 0] = np.nan
    yerr[ny == 0] = np.nan

    return xmean, ymean, xerr, yerr


def binned_quantiles(x, y, bins=10, q=[0.25, 0.5, 0.75]):

    if np.isscalar(bins):
        nbins = int(bins)
        bins = np.linspace(x.min(), x.max(), nbins + 1)
    else:
        nbins = len(bins) - 1

    x_centres = np.full((nbins,), np.nan)
    y_quantiles = np.full((3, nbins), np.nan)
    for ii in range(nbins):
        bin = (x >= bins[ii]) * (x < bins[ii + 1])
        if bin.sum() >=5:
            x_centres[ii] = np.median(x[bin])
            y_quantiles[:, ii] = mstats.mquantiles(y[bin], q)

    return y_quantiles, x_centres


def batch_mean(a, segment=1, weights=None):
    """
    Calculate mean of a 1-d array over batches of length 'segment'.
    If weights are provided, these must be the same size of the input array.

    :type a: ndarray
    :type segment: int
    :type weights: ndarray
    :rtype a: ndarray
    """

    if segment > 1:
        n = a.size // segment
        a_spl = np.split(a, n)
        if weights is None:
            a = np.array([a_spl[ii].mean() for ii in range(n)])
        else:
            w_spl = np.split(weights, n)
            a = np.array([(w_spl[ii] * a_spl[ii]).sum() / w_spl[ii].sum() for ii in range(n)])

    return a
