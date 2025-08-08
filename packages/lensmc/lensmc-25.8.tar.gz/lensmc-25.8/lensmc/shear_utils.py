"""
LensMC - a Python package for weak lensing shear measurements.
This is a module containing utility functions for shear bias measurement.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np


def get_bias(g, g0, parameter=None, bin_edges=None, n_bootstrap=1000, weights=None, masks=None,
             return_bin_centres=False, return_bin_sizes=False,
             m_cal=0., c_cal=0., g_cal=None, g0_cal=None, parameter_cal=None, weights_cal=None, masks_cal=None):
    """
    Weighted masked linear bias estimation of measured values ('g') against true values ('g0').
    Modelled bias is: g = (1 + m) * g0 + c, as a function of a possible parameter in bins defined by their edges.
    Best-fit shear bias ('m' and 'c') are returned along with statistical 1-sigma uncertainties via bootstrap,
    and also bin centres.

    :type g: ndarray
    :type g0: ndarray
    :type parameter: ndarray
    :type bin_edges: ndarray
    :type n_bootstrap: int
    :type weights: ndarray or None
    :type masks: ndarray or None
    :type return_bin_centres: bool
    :rtype m: ndarray
    :rtype c: ndarray
    :rtype dm: ndarray
    :rtype dc: ndarray
    :rtype bin_centres: ndarray
    """

    do_calibration = g_cal is not None and g0_cal is not None

    # either choose a nn-parametric or a parametric bias estimation
    if parameter is None:

        # go for total bias

        if do_calibration:
            m_cal, c_cal, dm_cal, dc_cal = linear_fit(g_cal, g0_cal,
                                                      n_bootstrap=n_bootstrap, weights=weights_cal)[0:4]

        # measure shear bias
        m, c, dm, dc = linear_fit((g - c_cal) / (1 + m_cal), g0, n_bootstrap=n_bootstrap, weights=weights)[0:4]

        # add up calibration noise in quadrature
        if do_calibration:
            dm = np.sqrt(dm ** 2 + dm_cal ** 2)
            dc = np.sqrt(dc ** 2 + dc_cal ** 2)

        return m, c, dm, dc

    else:

        # go for bias as a function of parameter

        m_cal_sel = c_cal_sel = 0.

        if masks is None:
            parameter_masked = parameter
            if parameter_cal is not None:
                parameter_cal_masked = parameter_cal
        else:
            parameter_masked = parameter[masks]
            if parameter_cal is not None:
                parameter_cal_masked = parameter_cal[masks_cal]

        # measure bias per parameter bin
        n_bins = len(bin_edges) - 1
        bin_centres = np. empty((n_bins,))
        bin_sizes = np.empty((n_bins,))
        shape = parameter.shape
        m, c, dm, dc = np.full((4, n_bins), np.nan)
        for ii in range(n_bins):
            # bin index
            if masks is None:
                ix = (parameter_masked >= bin_edges[ii]) & (parameter_masked < bin_edges[ii + 1])
                if parameter_cal is not None:
                    ix_cal = (parameter_cal_masked >= bin_edges[ii]) & (parameter_cal_masked < bin_edges[ii + 1])
            else:
                ix = np.zeros(shape, dtype=bool)
                ix[masks] = (parameter_masked >= bin_edges[ii]) & (parameter_masked < bin_edges[ii + 1])
                if parameter_cal is not None:
                    ix_cal = np.zeros(parameter_cal.shape, dtype=bool)
                    ix_cal[masks_cal] = (parameter_cal_masked >= bin_edges[ii]) & (parameter_cal_masked < bin_edges[ii + 1])

            # measure shear bias
            bin_sizes[ii] = np.sum(ix)
            if bin_sizes[ii] > 3:

                # set the weights
                if weights is None:
                    w = None
                else:
                    w = weights[ix]

                # set calibration coefficients
                if m_cal is not None:
                    if np.isscalar(m_cal):
                        m_cal_sel = m_cal
                    else:
                        m_cal_sel = np.mean(m_cal[ix_cal])
                if c_cal is not None:
                    if np.isscalar(m_cal):
                        c_cal_sel = c_cal
                    else:
                        c_cal_sel = np.mean(c_cal[ix_cal])

                if do_calibration:
                    if weights is not None:
                        assert weights_cal is not None
                        w_cal = weights_cal[ix_cal]

                    m_cal_sel, c_cal_sel, dm_cal_sel, dc_cal_sel = linear_fit(g_cal[ix_cal], g0_cal[ix_cal],
                                                                              n_bootstrap=n_bootstrap, weights=w_cal)[0:4]

                # fit bias
                m[ii], c[ii], dm[ii], dc[ii] = linear_fit((g[ix] - c_cal_sel) / (1 + m_cal_sel), g0[ix],
                                                          n_bootstrap=n_bootstrap, weights=w)[0:4]

                # add up calibration noise in quadrature
                if do_calibration:
                    dm[ii] = np.sqrt(dm[ii] ** 2 + dm_cal_sel ** 2)
                    dc[ii] = np.sqrt(dc[ii] ** 2 + dc_cal_sel ** 2)

            # compute bin centres
            if return_bin_centres:
                bin_centres[ii] = np.median(parameter_masked[ix])

        if return_bin_centres and not return_bin_sizes:
            return m, c, dm, dc, bin_centres
        elif return_bin_centres and return_bin_sizes:
            return m, c, dm, dc, bin_centres, bin_sizes
        else:
            return m, c, dm, dc


def linear_fit(g, g0, n_bootstrap=1000, weights=None, masks=None, errors_on_errors=False, n_bootstrap_errors=100):
    """
    Weighted masked linear fit bias of measured values ('g') against true values ('g0').
    Modelled bias is: g = (1 + m) * g0 + c.
    Best-fit shear bias ('m' and 'c') are returned along with statistical 1-sigma uncertainties via bootstrap,
    and possibly errors on errors.

    :type g: ndarray
    :type g0: ndarray
    :type n_bootstrap: int
    :type weights: ndarray or None
    :type masks: ndarray or None
    :type errors_on_errors: bool
    :type n_bootstrap_errors: int
    :rtype m: float
    :rtype c: float
    :rtype dm: float
    :rtype dc: float
    :rtype ddm: float
    :rtype ddc: float
    """

    assert len(g) == len(g0)

    # define combine weights
    if weights is not None:
        assert len(weights) == len(g)
    else:
        weights = np.ones(g.shape)
    if masks is not None:
        assert len(masks) == len(g)
    else:
        masks = np.ones(g.shape)
    w = weights * masks

    def fcn(y, x, w):

        # intermediate arrays and inner products
        xw = x * w
        xx, xy = np.sum(x * xw), np.sum(y * xw)
        sx, sy = np.sum(xw), np.sum(y * w)
        n = np.sum(w)
        d = n * xx - sx ** 2

        # additive bias
        c = (sy * xx - sx * xy) / d

        # multiplicative bias
        m = (n * xy - sx * sy) / d - 1

        return m, c

    # measure bias
    m, c = fcn(g, g0, w)

    # number of samples
    n_samples = len(g)

    # bootstrap uncertainties
    if n_bootstrap > 0:
        m_bs = np.empty((n_bootstrap,))
        c_bs = np.empty((n_bootstrap,))
        for ii in range(n_bootstrap):
            # draw samples with replacement
            u = np.random.random_integers(0, n_samples - 1, n_samples)
            # measure bias
            m_bs[ii], c_bs[ii] = fcn(g[u], g0[u], w[u])
        dm = np.std(m_bs)
        dc = np.std(c_bs)
        if errors_on_errors:
            n_bs_samples = len(m_bs)
            dm_bs = np.empty((n_bootstrap_errors,))
            dc_bs = np.empty((n_bootstrap_errors,))
            for ii in range(n_bootstrap_errors):
                # draw samples with replacement
                u = np.random.random_integers(0, n_bs_samples - 1, n_bs_samples)
                # measure bias
                dm_bs[ii] = np.std(m_bs[u])
                dc_bs[ii] = np.std(c_bs[u])
            ddm = np.std(dm_bs)
            ddc = np.std(dc_bs)
            return m, c, dm, dc, ddm, ddc
        else:
            return m, c, dm, dc
    else:
        return m, c


# def measure_bias(g, g0, n_bootstrap=1000, weights=None, masks=None, errors_on_errors=False, n_bootstrap_errors=100):
#     """
#     Measure linear bias of given measured shear values ('g') against true shear values ('g0').
#     The bias is modelled as g = (1 + m) * g0 + c. Best-fit shear bias ('m' and 'c') are output together with
#     their statistical uncertainty estimated via bootstrap, with optional number of bootstrap samples ('n_bootstrap').
#
#     :type g: ndarray
#     :type g0: ndarray
#     :type n_bootstrap: int
#     :type weights: ndarray or None
#     :type masks: ndarray or None
#     :type errors_on_errors: bool
#     :type n_bootstrap_errors: int
#     :rtype m: float
#     :rtype c: float
#     :rtype dm: float
#     :rtype dc: float
#     :rtype ddm: float
#     :rtype ddc: float
#     """
#
#     # difference between measured and true values
#     delta_g = g - g0
#
#     # deal with masks
#     if masks is None:
#         g0_masked = g0
#         delta_g_masked = delta_g
#         weights_masked = weights
#     else:
#         g0_masked = g0[masks]
#         delta_g_masked = delta_g[masks]
#         weights_masked = weights[masks]
#
#     # define weighted or unweighted fitting
#     if weights is None:
#         fcn = lambda x, y: np.polyfit(x, y, 1)
#     else:
#         fcn = lambda x, y: np.polyfit(x, y, 1, w=np.sqrt(weights_masked))
#
#     # measure bias
#     m, c = fcn(g0_masked, delta_g_masked)[0:2]
#
#     # number of samples
#     n_samples = len(g0_masked)
#
#     # bootstrap uncertainties
#     if n_bootstrap > 0:
#         m_bs = np.empty((n_bootstrap,))
#         c_bs = np.empty((n_bootstrap,))
#         for ii in range(n_bootstrap):
#             # draw samples with replacement
#             u = np.random.random_integers(0, n_samples - 1, n_samples)
#             # measure bias
#             m_bs[ii], c_bs[ii] = fcn(g0_masked[u], delta_g_masked[u])[0:2]
#         dm = np.std(m_bs)
#         dc = np.std(c_bs)
#         if errors_on_errors:
#             n_bs_samples = len(m_bs)
#             dm_bs = np.empty((n_bootstrap_errors,))
#             dc_bs = np.empty((n_bootstrap_errors,))
#             for ii in range(n_bootstrap_errors):
#                 # draw samples with replacement
#                 u = np.random.random_integers(0, n_bs_samples - 1, n_bs_samples)
#                 # measure bias
#                 dm_bs[ii] = np.std(m_bs[u])
#                 dc_bs[ii] = np.std(c_bs[u])
#             ddm = np.std(dm_bs)
#             ddc = np.std(dc_bs)
#             return m, c, dm, dc, ddm, ddc
#         else:
#             return m, c, dm, dc
#     else:
#         return m, c
#
#
# def measure_bias_parametric(g, g0, p, bin_edges, n_bootstrap=1000, weights=None, masks=None, return_bin_centres=True):
#     """
#     Measure linear bias of given measured shear values ('g') against true shear values ('g0'),
#     as a function of a parameter ('p'). It requires also the edges of parameter bins ('bin_edges').
#     The bias is modelled as g = (1 + m) * g0 + c. Best-fit shear bias ('m' and 'c') are output together with
#     their statistical uncertainty estimated via bootstrap, with optional number of bootstrap samples ('n_bootstrap').
#
#     :type g: ndarray
#     :type g0: ndarray
#     :type p: ndarray
#     :type bin_edges: ndarray
#     :type n_bootstrap: int
#     :type weights: ndarray or None
#     :type masks: ndarray or None
#     :type return_bin_centres: bool
#     :rtype m: ndarray
#     :rtype c: ndarray
#     :rtype dm: ndarray
#     :rtype dc: ndarray
#     :rtype bin_centres: ndarray
#     """
#
#     # compute bin centres
#     n_bins = len(bin_edges) - 1
#     bin_centres = np.zeros((n_bins,))
#     for ii in range(n_bins):
#         bin_centres[ii] = 0.5 * (bin_edges[ii] + bin_edges[ii+1])
#
#     if masks is None:
#         p_masked = p
#     else:
#         p_masked = p[masks]
#
#     # measure bias per parameter bin
#     m, c, dm, dc = np.empty((4, n_bins)) * np.nan
#     for ii in range(n_bins):
#         # bin index
#         if masks is None:
#             ix = (p_masked >= bin_edges[ii]) & (p_masked < bin_edges[ii + 1])
#         else:
#             ix = np.zeros(p.shape, dtype=bool)
#             ix[masks] = (p_masked >= bin_edges[ii]) & (p_masked < bin_edges[ii + 1])
#
#         # measure shear bias
#         if np.sum(ix) > 1:
#             if weights is None:
#                 m[ii], c[ii], dm[ii], dc[ii] = measure_bias(g[ix], g0[ix], n_bootstrap=n_bootstrap)[0:4]
#             else:
#                 m[ii], c[ii], dm[ii], dc[ii] = measure_bias(g[ix], g0[ix], n_bootstrap=n_bootstrap,
#                                                             weights=weights[ix])[0:4]
#
#     if return_bin_centres:
#         return m, c, dm, dc, bin_centres
#     else:
#         return m, c, dm, dc


# def measure_bias_shear_pdf(g_grid, logp_g_coeffs, A_g, g0, n_bootstrap=1000, weights=None):
#     """
#     Measure linear bias of given measured shear values ('g') against true shear values ('g0').
#     The bias is modelled as g = (1 + m) * g0 + c. Best-fit shear bias ('m' and 'c') are output together with
#     their statistical uncertainty estimated via bootstrap, with optional number of bootstrap samples ('n_bootstrap').
#
#     :type g: ndarray
#     :type g0: ndarray
#     :type n_bootstrap: int
#     :type weights: ndarray or None
#     :rtype m: float
#     :rtype c: float
#     :rtype dm: float
#     :rtype dc: float
#     """
#
#     # number of samples
#     n_samples = logp_g_coeffs.shape[0]
#
#     # measure shear
#     g = np.empty((n_samples, ))
#     for ii in range(n_samples):
#         logp_g = np.dot(A_g, logp_g_coeffs[ii, :])
#         p_g = np.exp(logp_g - np.max(logp_g))
#         g[ii] = np.average(g_grid, weights=p_g)
#
#     # difference between measured and true values
#     delta_g = g - g0
#
#     # define weighted or unweighted fitting
#     fcn = lambda x, y: np.polyfit(x, y, 1, w=weights)
#
#     # measure bias
#     # res = scipy.stats.linregress(g0, delta_g)
#     # m, c = res[0:2]
#     m, c = fcn(g0, delta_g)[0:2]
#
#     # bootstrap uncertainties
#     if n_bootstrap > 0:
#         m_bs = np.zeros((n_bootstrap,))
#         c_bs = np.zeros((n_bootstrap,))
#         for ii in range(n_bootstrap):
#             # draw samples with replacement
#             u = np.random.random_integers(0, n_samples - 1, n_samples)
#             # measure bias
#             # res = scipy.stats.linregress(g0[u], delta_g[u])
#             # m_bs[ii], c_bs[ii] = res[0:2]
#             for kk in range(n_samples):
#                 logp_g = np.dot(A_g, logp_g_coeffs[u, :][kk, :])
#                 p_g = np.exp(logp_g - np.max(logp_g))
#                 g[kk] = np.average(g_grid, weights=p_g)
#             delta_g = g - g0
#             m_bs[ii], c_bs[ii] = fcn(g0[u], delta_g)[0:2]
#         dm = np.std(m_bs)
#         dc = np.std(c_bs)
#         return m, c, dm, dc
#     else:
#         return m, c
#
#
# def measure_bias_shear_pdf_parametric(g_grid, logp_g_coeffs, A_g, g0, p, bin_edges, n_bootstrap=1000, weights=None, return_bin_centres=True):
#     """
#     Measure linear bias of given measured shear values ('g') against true shear values ('g0'),
#     as a function of a parameter ('p'). It requires also the edges of parameter bins ('bin_edges').
#     The bias is modelled as g = (1 + m) * g0 + c. Best-fit shear bias ('m' and 'c') are output together with
#     their statistical uncertainty estimated via bootstrap, with optional number of bootstrap samples ('n_bootstrap').
#
#     :type g: ndarray
#     :type g0: ndarray
#     :type p: ndarray
#     :type bin_edges: ndarray
#     :type n_bootstrap: int
#     :type weights: ndarray or None
#     :type return_bin_centres: bool
#     :rtype m: ndarray
#     :rtype c: ndarray
#     :rtype dm: ndarray
#     :rtype dc: ndarray
#     :rtype bin_centres: ndarray
#     """
#
#     # compute bin centres
#     n_bins = len(bin_edges) - 1
#     bin_centres = np.zeros((n_bins,))
#     for ii in range(n_bins):
#         bin_centres[ii] = 0.5 * (bin_edges[ii] + bin_edges[ii+1])
#
#     # measure bias per parameter bin
#     m, c, dm, dc = np.zeros((4, n_bins)) * np.nan
#     for ii in range(n_bins):
#         # bin index
#         ix = (p >= bin_edges[ii]) & (p < bin_edges[ii+1])
#         # measure shear bias
#         if np.sum(ix):
#             if weights is None:
#                 m[ii], c[ii], dm[ii], dc[ii] = measure_bias_shear_pdf(g_grid, logp_g_coeffs[ix, :], A_g, g0[ix], n_bootstrap=n_bootstrap)[0:4]
#             else:
#                 m[ii], c[ii], dm[ii], dc[ii] = measure_bias_shear_pdf(g_grid, logp_g_coeffs[ix, :], A_g, g0[ix], n_bootstrap=n_bootstrap,
#                                                             weights=weights[ix])[0:4]
#
#     if return_bin_centres:
#         return m, c, dm, dc, bin_centres
#     else:
#         return m, c, dm, dc


def calculate_weights(dg1, dg2, shape_noise_std=0.3, emax=0.804, average=False,
                      snr=None, s=None, snr_bins_edges=None, s_bins_edges=None):
    """
    It returns weights calculated by summing up in quadrature measurement errors and shape noise.
    These weights can optionally be averaged in bins of snr, |e|, and s.
    """

    # sum up in quadrature measurement errors and shape noise
    w = 1. / (dg1 ** 2 + dg2 ** 2 + shape_noise_std ** 2)
    # var_g = dg1 ** 2 + dg2 ** 2
    # emax2 = emax ** 2
    # w = 1. / ((var_g * emax2) / (emax2 - 2 * var_g) + shape_noise_std ** 2)

    # # average in bins of snr, |e|, and s
    # if average:
    #     w_binned = np.full((len(snr_bins_edges) - 1, len(e_bins_edges) - 1, len(s_bins_edges) - 1), fill_value=np.nan)
    #     for ii in range(len(snr_bins_edges) - 1):
    #         for jj in range(len(e_bins_edges) - 1):
    #             for kk in range(len(s_bins_edges) - 1):
    #                 ix_bin = (snr >= snr_bins_edges[ii]) * (snr < snr_bins_edges[ii + 1]) * \
    #                          (e >= e_bins_edges[jj]) * (e < e_bins_edges[jj + 1]) * \
    #                          (s >= s_bins_edges[kk]) * (s < s_bins_edges[kk + 1])
    #                 if np.sum(ix_bin) > 1:
    #                     w_binned[ii, jj, kk] = np.mean(w[ix_bin])
    #     for iii in range(len(w)):
    #         ii, jj, kk = np.nan, np.nan, np.nan
    #         for ii in range(len(snr_bins_edges) - 1):
    #             if (snr[iii] >= snr_bins_edges[ii]) * (snr[iii] < snr_bins_edges[ii + 1]):
    #                 break
    #         for jj in range(len(e_bins_edges) - 1):
    #             if (e[iii] >= e_bins_edges[jj]) * (e[iii] < e_bins_edges[jj + 1]):
    #                 break
    #         for kk in range(len(s_bins_edges) - 1):
    #             if (s[iii] >= s_bins_edges[kk]) * (s[iii] < s_bins_edges[kk + 1]):
    #                 break
    #         if np.isfinite(w_binned[ii, jj, kk]):
    #             w[iii] = w_binned[ii, jj, kk]

    # average in bins of snr and s
    if average:
        w_binned = np.zeros((len(snr_bins_edges) - 1, len(s_bins_edges) - 1)) * np.nan
        for ii in range(len(snr_bins_edges) - 1):
            for kk in range(len(s_bins_edges) - 1):
                ix_bin = (snr >= snr_bins_edges[ii]) * (snr < snr_bins_edges[ii + 1]) * \
                         (s >= s_bins_edges[kk]) * (s < s_bins_edges[kk + 1])
                if np.sum(ix_bin) > 1:
                    w_binned[ii, kk] = np.mean(w[ix_bin])
        for iii in range(len(w)):
            ii, kk = np.nan, np.nan
            for ii in range(len(snr_bins_edges) - 1):
                if (snr[iii] >= snr_bins_edges[ii]) * (snr[iii] < snr_bins_edges[ii + 1]):
                    break
            for kk in range(len(s_bins_edges) - 1):
                if (s[iii] >= s_bins_edges[kk]) * (s[iii] < s_bins_edges[kk + 1]):
                    break
            if np.isfinite(w_binned[ii, kk]):
                w[iii] = w_binned[ii, kk]

    return w


def get_calibration(g, g0, weights=None, snr=None, s=None, snr_bins_edges=None, s_bins_edges=None, n_bootstrap=100):

    # manage unweighted analysis
    if weights is None:
        weights = np.ones(g.shape)

    # number of bins
    n_snr_bins = len(snr_bins_edges) - 1
    n_s_bins = len(s_bins_edges) - 1

    # measure bias in bins
    m_binned, c_binned, dm_binned, dc_binned = np.zeros((4, len(snr_bins_edges) - 1, len(s_bins_edges) - 1))
    for ii in range(n_snr_bins):
        for kk in range(n_s_bins):
            ix_bin = (snr >= snr_bins_edges[ii]) * (snr < snr_bins_edges[ii + 1]) * \
                     (s >= s_bins_edges[kk]) * (s < s_bins_edges[kk + 1])
            if np.sum(ix_bin) >= 10:  # requires a minum of 10 values in the bin to proceed with calibration
                m_binned[ii, kk], c_binned[ii, kk], dm_binned[ii, kk], dc_binned[ii, kk] = \
                    get_bias(g[ix_bin], g0[ix_bin], weights=weights[ix_bin], n_bootstrap=n_bootstrap)

    # calibration function
    def calibration_fcn(snr, s):

        ix_snr = (snr >= snr_bins_edges[:-1]) * (snr < snr_bins_edges[1:])
        ix_s = (s >= s_bins_edges[:-1]) * (s < s_bins_edges[1:])

        if any(ix_snr) and any(ix_s):
            ix_snr, ix_s = np.where(ix_snr), np.where(ix_s)
            return m_binned[ix_snr, ix_s], c_binned[ix_snr, ix_s], dm_binned[ix_snr, ix_s], dc_binned[ix_snr, ix_s]
        else:
            return np.zeros((4, ))

    return calibration_fcn


def apply_calibration(g, dg, calibration_fcn, snr=None, s=None):

    n_g = len(g)
    m, c, dm, dc = np.empty((4, n_g))
    for ii in range(n_g):
        m[ii], c[ii], dm[ii], dc[ii] = calibration_fcn(snr[ii], s[ii])
    g_cal = (g - c) / (1. + m)
    # g_cal = (1. - m) * g - c
    dg_cal = np.sqrt((1 + m) ** (-2) * dg ** 2 + (g - c) ** 2 * dm ** 2 + (1 + m) ** (-2) * dc ** 2)
    # dg_cal = np.sqrt(g ** 2 * dm ** 2 + dc ** 2)

    return g_cal, dg_cal


# def measure_shear_BA(P, Q, R):
#     """
#     Implements formulae:
#     C^(-1) = sum( Q Q^T / P^2 - R / P)
#     g = C * sum( Q / P )
#     Assumes flat arrays.
#     """
#
#     # normalise by P
#     ix = np.where(P != 0)
#     q = np.zeros(Q.shape)
#     for ii in range(Q.shape[1]):
#         q[ix, ii] = Q[ix, ii] / P[ix]
#     r = np.zeros(R.shape)
#     for ii in range(R.shape[1]):
#         r[ix, ii] = R[ix, ii] / P[ix]
#
#     # compute outer product
#     qq = np.empty(r.shape)
#     for ii in range(P.size):
#         qq[ii, :] = np.outer(q[ii, :], q[ii, :]).ravel()
#
#     # covariance
#     iC = np.sum(qq - r, axis=0).reshape((2, 2))
#     C = np.linalg.pinv(iC)
#     dg = np.sqrt(np.diag(C))
#
#     # mean
#     q = np.sum(q, axis=0)
#     g = np.dot(C, q)
#
#     return g, dg
