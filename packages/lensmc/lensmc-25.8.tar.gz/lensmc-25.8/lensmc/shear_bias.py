"""
LensMC - a Python package for weak lensing shear measurements.
Shear bias estimation and calibration.

Copyright 2015-22 Giuseppe Congedo
"""

import numpy as np
from dask import compute, delayed


def get_bias2(g, g0, weights, g_bin_edges,
             param=None, param_bin_edges=None, return_bin_centres=False, return_bin_sizes=False,
             g_aux=None,
             g_calset=None, g0_calset=None, weights_calset=None, g_aux_calset=None, param_calset=None,
             m_cal=None, c_cal=None,
             analytic=False, n_bootstrap=1000):

    # what calibration strategies should be carried out
    do_int_cal = g_aux is not None
    do_ext_cal = g_calset is not None and g0_calset is not None
    do_int_ext_cal = do_int_cal and do_ext_cal and g_aux_calset is not None
    do_cal = m_cal is not None

    # whether selection should be applied
    do_parametric = param is not None
    if do_parametric:
        assert ((param_bin_edges is not None) and (len(param_bin_edges) >= 2))

    # return bin centres and sizes only when applying selection
    return_bin_centres = do_parametric and return_bin_centres
    return_bin_sizes = do_parametric and return_bin_sizes

    # shear bins
    n_g_bins = len(g_bin_edges) - 1

    # number of selection bins
    if do_parametric:
        n_bins = len(param_bin_edges) - 1
    else:
        n_bins = 1

    # loop over bins
    m, c, dm, dc, \
    m_ical, c_ical, dm_ical, dc_ical, \
    m_calset, c_calset, dm_calset, dc_calset, \
    m_ical_calset, c_ical_calset, dm_ical_calset, dc_ical_calset, \
    m_mcal, c_mcal, dm_mcal, dm_mcal = ([np.nan] * n_bins for _ in range(20))
    if return_bin_centres:
        bin_centres = [0] * n_bins
    if return_bin_sizes:
        bin_sizes = [0] * n_bins
    for ii in range(n_bins):

        # selection indices
        if do_parametric:
            ix = (param >= param_bin_edges[ii]) & (param < param_bin_edges[ii + 1])
            if do_ext_cal:
                ix_calset = (param_calset >= param_bin_edges[ii]) & (param_calset < param_bin_edges[ii + 1])
        else:
            ix = np.ones(g.shape, dtype=bool)
            if do_ext_cal:
                ix_calset = np.ones(g_calset.shape, dtype=bool)

        # get bin centre
        if return_bin_centres:
            bin_centres[ii] = np.median(param[ix])

        # get bin size
        if return_bin_sizes:
            bin_sizes[ii] = ix.sum()

        # check whether the selection leaves enough dataset samples
        if ix.sum() > 3:

            # internal calibration for calibration set
            if do_int_ext_cal and ix_calset.sum() > 3:
                 m_ical_calset[ii], c_ical_calset[ii], dm_ical_calset[ii], dc_ical_calset[ii] = \
                    linear_fit(g_aux_calset[ix_calset], g_calset[ix_calset],
                               weights=weights_calset[ix_calset], analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                m_ical_calset[ii], c_ical_calset[ii], dm_ical_calset[ii], dc_ical_calset[ii] = 0, 0, 0, 0

            # external calibration
            if do_ext_cal and ix_calset.sum() > 3:
                # new_weights_calset = 1 / (1 / weights_calset[ix_calset] +
                #                           g_calset[ix_calset] ** 2 * dm_ical_calset[ii] ** 2 + dc_ical_calset[ii] ** 2)
                new_g_calset = (g_calset[ix_calset] - c_ical_calset[ii]) / (1 + m_ical_calset[ii])
                x, y, icov = np.empty((3, n_g_bins,))
                for gg in range(n_g_bins):
                    ix_g = (g0_calset[ix] >= g_bin_edges[gg]) * (g0_calset[ix] < g_bin_edges[gg + 1])
                    w_g = weights_calset[ix][ix_g]
                    w_g[w_g < 0] = 0
                    y[gg] = np.average(new_g_calset[ix_g], weights=w_g)
                    icov[gg] = 1 / np.cov(new_g_calset[ix_g], aweights=w_g)
                    x[gg] = np.mean(g0_calset[ix][ix_g])
                m_calset[ii], c_calset[ii], dm_calset[ii], dc_calset[ii] = linear_fit(y, x, weights=icov, analytic=analytic, n_bootstrap=n_bootstrap)
                # m_calset[ii], c_calset[ii], dm_calset[ii], dc_calset[ii] = \
                #     linear_fit(new_g_calset, g0_calset[ix_calset],
                #                weights=new_weights_calset, analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                m_calset[ii], c_calset[ii], dm_calset[ii], dc_calset[ii] = 0, 0, 0, 0

            # internal calibration for data set
            if do_int_cal:
                # m_ical[ii], c_ical[ii], dm_ical[ii], dc_ical[ii] = \
                #     linear_fit(g_aux[ix], g[ix],
                #                weights=weights[ix], analytic=analytic, n_bootstrap=n_bootstrap)
                x, y, icov = np.empty((3, n_g_bins,))
                for gg in range(n_g_bins):
                    ix_g = (g0[ix] >= g_bin_edges[gg]) * (g0[ix] < g_bin_edges[gg + 1])
                    w_g = weights[ix][ix_g]
                    w_g[w_g < 0] = 0
                    y[gg] = np.average(g[ix][ix_g], weights=w_g)
                    icov[gg] = 1 / np.cov(g[ix][ix_g], aweights=w_g)
                    x[gg] = np.mean(g0[ix][ix_g])
                m_ical[ii], c_ical[ii], dm_ical[ii], dc_ical[ii] = linear_fit(y, x, weights=icov, analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                m_ical[ii], c_ical[ii], dm_ical[ii], dc_ical[ii] = 0, 0, 0, 0

            # final bias
            if not do_cal:
                # new_weights = 1 / (1 / weights[ix] +
                #                    g[ix] ** 2 * (dm_ical[ii] ** 2 + dm_calset[ii] ** 2) + dc_ical[ii] ** 2 + dc_calset[ii] ** 2)
                new_g = ((g[ix] - c_ical[ii]) / (1 + m_ical[ii]) - c_calset[ii]) / (1 + m_calset[ii])
                x, y, icov = np.empty((3, n_g_bins,))
                for gg in range(n_g_bins):
                    ix_g = (g0[ix] >= g_bin_edges[gg]) * (g0[ix] < g_bin_edges[gg + 1])
                    w_g = weights[ix][ix_g]
                    w_g[w_g < 0] = 0
                    y[gg] = np.average(new_g[ix_g], weights=w_g)
                    icov[gg] = 1 / np.cov(new_g[ix_g], aweights=w_g)
                    x[gg] = np.mean(g0[ix][ix_g])
                m[ii], c[ii], dm[ii], dc[ii] = linear_fit(y, x, weights=icov, analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                # calibration with provided m & c
                new_g = np.copy(g[ix])
                if c_cal is not None:
                    new_g -= np.median(c_cal[ix])
                new_g /= m_cal[ix]
                m[ii], c[ii], dm[ii], dc[ii] = linear_fit(new_g, g0[ix],
                                                          weights=weights[ix], analytic=analytic, n_bootstrap=n_bootstrap)

    # just return scalar values for trivial selection
    if n_bins == 1:
        m = m[0]
        c = c[0]
        dm = dm[0]
        dc = dc[0]
        if return_bin_centres:
            bin_centres = bin_centres[0]
        if return_bin_sizes:
            bin_sizes = bin_sizes[0]

    if return_bin_sizes and not return_bin_centres:
        return m, c, dm, dc, bin_sizes
    elif not return_bin_sizes and return_bin_centres:
        return m, c, dm, dc, bin_centres
    elif return_bin_sizes and return_bin_centres:
        return m, c, dm, dc, bin_centres, bin_sizes
    else:
        return m, c, dm, dc


def get_bias(g, g0, weights,
             param=None, param_bin_edges=None, return_bin_centres=False, return_bin_sizes=False,
             g_aux=None,
             g_calset=None, g0_calset=None, weights_calset=None, g_aux_calset=None, param_calset=None,
             m_cal=None, c_cal=None,
             analytic=False, n_bootstrap=1000):

    # what calibration strategies should be carried out
    do_int_cal = g_aux is not None
    do_ext_cal = g_calset is not None and g0_calset is not None
    do_int_ext_cal = do_int_cal and do_ext_cal and g_aux_calset is not None
    do_cal = m_cal is not None

    # whether selection should be applied
    do_parametric = param is not None
    if do_parametric:
        assert ((param_bin_edges is not None) and (len(param_bin_edges) >= 2))

    # return bin centres and sizes only when applying selection
    return_bin_centres = do_parametric and return_bin_centres
    return_bin_sizes = do_parametric and return_bin_sizes

    # number of selection bins
    if do_parametric:
        n_bins = len(param_bin_edges) - 1
    else:
        n_bins = 1

    # loop over bins
    m, c, dm, dc, \
    m_ical, c_ical, dm_ical, dc_ical, \
    m_calset, c_calset, dm_calset, dc_calset, \
    m_ical_calset, c_ical_calset, dm_ical_calset, dc_ical_calset, \
    m_mcal, c_mcal, dm_mcal, dm_mcal = ([np.nan] * n_bins for _ in range(20))
    if return_bin_centres:
        bin_centres = [0] * n_bins
    if return_bin_sizes:
        bin_sizes = [0] * n_bins
    for ii in range(n_bins):

        # selection indices
        if do_parametric:
            ix = (param >= param_bin_edges[ii]) & (param < param_bin_edges[ii + 1])
            if do_ext_cal:
                ix_calset = (param_calset >= param_bin_edges[ii]) & (param_calset < param_bin_edges[ii + 1])
        else:
            ix = np.ones(g.shape, dtype=bool)
            if do_ext_cal:
                ix_calset = np.ones(g_calset.shape, dtype=bool)

        # get bin centre
        if return_bin_centres:
            bin_centres[ii] = np.median(param[ix])

        # get bin size
        if return_bin_sizes:
            bin_sizes[ii] = ix.sum()

        # check whether the selection leaves enough dataset samples
        if ix.sum() > 3:

            # internal calibration for calibration set
            if do_int_ext_cal and ix_calset.sum() > 3:
                m_ical_calset[ii], c_ical_calset[ii], dm_ical_calset[ii], dc_ical_calset[ii] = \
                    linear_fit(g_aux_calset[ix_calset], g_calset[ix_calset],
                               weights=weights_calset[ix_calset], analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                m_ical_calset[ii], c_ical_calset[ii], dm_ical_calset[ii], dc_ical_calset[ii] = 0, 0, 0, 0

            # external calibration
            if do_ext_cal and ix_calset.sum() > 3:
                new_weights_calset = 1 / (1 / weights_calset[ix_calset] +
                                          g_calset[ix_calset] ** 2 * dm_ical_calset[ii] ** 2 + dc_ical_calset[ii] ** 2)
                new_g_calset = (g_calset[ix_calset] - c_ical_calset[ii]) / (1 + m_ical_calset[ii])
                m_calset[ii], c_calset[ii], dm_calset[ii], dc_calset[ii] = \
                    linear_fit(new_g_calset, g0_calset[ix_calset],
                               weights=new_weights_calset, analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                m_calset[ii], c_calset[ii], dm_calset[ii], dc_calset[ii] = 0, 0, 0, 0

            # internal calibration for data set
            if do_int_cal:
                m_ical[ii], c_ical[ii], dm_ical[ii], dc_ical[ii] = \
                    linear_fit(g_aux[ix], g[ix],
                               weights=weights[ix], analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                m_ical[ii], c_ical[ii], dm_ical[ii], dc_ical[ii] = 0, 0, 0, 0

            # final bias
            if not do_cal:
                new_weights = 1 / (1 / weights[ix] +
                                   g[ix] ** 2 * (dm_ical[ii] ** 2 + dm_calset[ii] ** 2) + dc_ical[ii] ** 2 + dc_calset[ii] ** 2)
                new_g = ((g[ix] - c_ical[ii]) / (1 + m_ical[ii]) - c_calset[ii]) / (1 + m_calset[ii])
                m[ii], c[ii], dm[ii], dc[ii] = linear_fit(new_g, g0[ix],
                                                          weights=new_weights, analytic=analytic, n_bootstrap=n_bootstrap)
            else:
                # calibration with provided m & c
                new_g = np.copy(g[ix])
                if c_cal is not None:
                    new_g -= np.mean(c_cal[ix])
                new_g /= np.mean(m_cal[ix])
                m[ii], c[ii], dm[ii], dc[ii] = linear_fit(new_g, g0[ix],
                                                          weights=weights[ix], analytic=analytic, n_bootstrap=n_bootstrap)

    # just return scalar values for trivial selection
    if n_bins == 1:
        m = m[0]
        c = c[0]
        dm = dm[0]
        dc = dc[0]
        if return_bin_centres:
            bin_centres = bin_centres[0]
        if return_bin_sizes:
            bin_sizes = bin_sizes[0]

    if return_bin_sizes and not return_bin_centres:
        return m, c, dm, dc, bin_sizes
    elif not return_bin_sizes and return_bin_centres:
        return m, c, dm, dc, bin_centres
    elif return_bin_sizes and return_bin_centres:
        return m, c, dm, dc, bin_centres, bin_sizes
    else:
        return m, c, dm, dc


def linear_fit(g, g0, analytic=False, n_bootstrap=1000, weights=None, slope_plus_one=True):
    """
    Weighted linear fit bias of measured values ('g') against true values ('g0').
    Modelled bias is: g = (1 + m) * g0 + c.
    Best-fit shear bias ('m' and 'c') are returned along with statistical 1-sigma uncertainties via bootstrap.

    :type g: ndarray
    :type g0: ndarray
    :type n_bootstrap: int
    :type weights: ndarray or None
    :rtype m: float
    :rtype c: float
    :rtype dm: float
    :rtype dc: float
    """

    assert len(g) == len(g0)

    # define combine weights
    if weights is not None:
        assert len(weights) == len(g)
    else:
        weights = np.ones(g.shape)

    # measure bias
    if analytic:
        m, c, dm, dc = _linfit_fcn(g, g0, weights, return_errors=True, slope_plus_one=slope_plus_one)
        return m, c, dm, dc
    else:
        m, c = _linfit_fcn(g, g0, weights, return_errors=False, slope_plus_one=slope_plus_one)

    # number of samples
    n_samples = len(g)

    # bootstrap uncertainties
    if not analytic and n_bootstrap > 0:

        # run bootstrap resampling
        vals = [delayed(_bootstrap_fcn)(n_samples, g, g0, weights, slope_plus_one) for _ in range(n_bootstrap)]
        bs = np.asarray(compute(*vals, scheduler='threads'))

        # get errors
        dm, dc = bs[:, 0].std(), bs[:, 1].std()

        return m, c, dm, dc
    else:
        return m, c


def _linfit_fcn(y, x, w, return_errors=False, slope_plus_one=True):

    # intermediate arrays and inner products
    dy = y - x
    xw = x * w
    xx, xdy = (x * xw).sum(), (dy * xw).sum()
    sx, sdy = xw.sum(), (dy * w).sum()
    n = w.sum()
    d = n * xx - sx ** 2

    # multiplicative and additive bias
    m = (n * xdy - sx * sdy) / d
    c = (-sx * xdy + xx * sdy) / d

    # fix (1+m) slope [user requests m, not (1+m)]
    if not slope_plus_one:
        m += 1

    if return_errors:
        r = y - (1 + m) * x - c
        chi2 = (r ** 2 * w).sum() / (r.size - 2)
        # C = chi2 * np.linalg.inv(np.array([[xx, sx], [sx, n]]))
        dm = np.sqrt(chi2 * n / d)
        dc = np.sqrt(chi2 * xx / d)
        return m, c, dm, dc
    else:
        return m, c


def _bootstrap_fcn(n_samples, g, g0, weights, slope_plus_one=True):

    # draw samples with replacement
    u = np.random.random_integers(0, n_samples - 1, n_samples)

    # measure bias
    m, c = _linfit_fcn(g[u], g0[u], weights[u], slope_plus_one=slope_plus_one)

    return m, c
