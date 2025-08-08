"""
LensMC - a Python package for weak lensing shear measurements.
Log-likelihood and goodness-of-fit for the bulge+disc images testing.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from scipy.optimize import nnls
# noinspection PyUnresolvedReferences
from lensmc.cross_product import cross_product_float as cross_product


def log_likl(data, p, bulge_model_fcn, disc_model_fcn, weights, log_likl_const=0.):
    """
    Log-likelihood for bulge+disc galaxy model and multiple exposures.

    :type data: list of ndarray
    :type p: ndarray
    :type bulge_model_fcn: list of lambda
    :type disc_model_fcn: list of lambda
    :type weights: list of ndarray
    :type log_likl_const: float
    :rtype: float
    """

    # get models
    n = len(data)
    w_size = weights[0].shape[0]
    bulge = [None] * n
    disc = [None] * n
    bulge_w = [None] * n
    disc_w = [None] * n
    for ii in range(n):
        bulge[ii] = np.copy(bulge_model_fcn[ii](p))
        size = bulge[ii].shape[0]
        ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
        bulge_w[ii] = bulge[ii] * weights[ii][ix0: ix1, ix0: ix1]
    for ii in range(n):
        disc[ii] = np.copy(disc_model_fcn[ii](p))
        size = disc[ii].shape[0]
        ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
        disc_w[ii] = disc[ii] * weights[ii][ix0: ix1, ix0: ix1]

    # get cross products
    bulge_bulge = cross_product(bulge, bulge_w)
    bulge_disc = cross_product(disc, bulge_w)
    disc_disc = cross_product(disc, disc_w)
    bulge_data = cross_product(data, bulge_w)
    disc_data = cross_product(data, disc_w)

    # Fisher matrix and data vector
    F = np.array([[bulge_bulge, bulge_disc], [bulge_disc, disc_disc]])
    X = np.array([bulge_data, disc_data])

    # compute log-likelihood
    return _log_likl(F, X, log_likl_const)


def log_likl_1component(data, p, model_fcn, weights, logl_likl_const=0.):
    """
    Log-likelihood for disc-only galaxy model.

    :type data: list of ndarray
    :type p: ndarray
    :type model_fcn: list of lambda
    :type weights: list of ndarray
    :type logl_likl_const: float
    :rtype: float
    """

    # get model
    n = len(data)
    w_size = weights[0].shape[0]
    model = [None] * n
    model_w = [None] * n
    for ii in range(n):
        model[ii] = np.copy(model_fcn[ii](p))
        size = model[ii].shape[0]
        ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
        model_w[ii] = model[ii] * weights[ii][ix0: ix1, ix0: ix1]

    # get cross products
    model_model = cross_product(model, model_w)
    model_data = cross_product(data, model_w)

    # compute log-likelihood
    if model_data > 0 and model_model > 0:
        logl = .5 * model_data ** 2 / model_model
    else:
        logl = 0.

    return logl_likl_const + logl


def log_likl_joint(data, p, bulge_model_fcns, disc_model_fcns, weights):
    """
    Log-likelihood for bulge+disc galaxy model and multiple exposures.

    :type data: list of ndarray
    :type p: ndarray
    :type bulge_model_fcns: list of lambda
    :type disc_model_fcns: list of lambda
    :type weights: list of ndarray
    :rtype: float
    """

    # calculate models, residuals, and log-likelihood
    n, o = len(data), len(disc_model_fcns)
    data_size = data[0].shape[0]
    logl = 0
    for jj in range(n):
        # residuals
        r = np.copy(data[jj])
        for ii in range(o):
            # parameters
            ip0 = 7 * ii
            ip1 = ip0 + 5
            p_in_model = p[ip0: ip1]
            flux_bulge, flux_disc = p[ip1], p[ip1 + 1]

            # bulge
            bulge = bulge_model_fcns[ii][jj](p_in_model)
            bulge_size = bulge.shape[0]
            ix0, ix1 = (data_size - bulge_size) // 2, (data_size + bulge_size) // 2
            r[ix0: ix1, ix0: ix1] -= flux_bulge * bulge

            # disc
            disc = disc_model_fcns[ii][jj](p_in_model)
            disc_size = disc.shape[0]
            ix0, ix1 = (data_size - disc_size) // 2, (data_size + disc_size) // 2
            r[ix0: ix1, ix0: ix1] -= flux_disc * disc
        # residuals by weights
        r_w = np.multiply(r, weights[jj], dtype=np.float64)
        # log-likelihood
        logl -= .5 * np.multiply(r_w, r, dtype=np.float64).sum()

    return logl


def marginal_model(p, bulge_model_fcn, disc_model_fcn, data, weights, return_coeff=False):
    """
    Bulge+disc galaxy model marginalised over data.
    It returns the marginalised model, and the two linear coefficients.

    :type p: ndarray
    :type bulge_model_fcn: list of lambda
    :type disc_model_fcn: list of lambda
    :type data: list of ndarray
    :type weights: list of ndarray
    :rtype: float
    """

    # get models
    n = len(data)
    w_size = weights[0].shape[0]
    bulge = [None] * n
    disc = [None] * n
    bulge_w = [None] * n
    disc_w = [None] * n
    for ii in range(n):
        bulge[ii] = np.copy(bulge_model_fcn[ii](p))
        size = bulge[ii].shape[0]
        ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
        bulge_w[ii] = bulge[ii] * weights[ii][ix0: ix1, ix0: ix1]
    for ii in range(n):
        disc[ii] = np.copy(disc_model_fcn[ii](p))
        size = disc[ii].shape[0]
        ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
        disc_w[ii] = disc[ii] * weights[ii][ix0: ix1, ix0: ix1]

    # get cross products
    bulge_bulge = cross_product(bulge, bulge_w)
    bulge_disc = cross_product(disc, bulge_w)
    disc_disc = cross_product(disc, disc_w)
    bulge_data = cross_product(data, bulge_w)
    disc_data = cross_product(data, disc_w)

    # Fisher matrix and data vector
    F = np.array([[bulge_bulge, bulge_disc], [bulge_disc, disc_disc]])
    X = np.array([bulge_data, disc_data])

    # coefficients
    (a_bulge, a_disc), _ = nnls(F, X)

    # model = a_bulge * bulge + a_disc * disc
    n = len(data)
    data_size = data[0].shape[0]
    model = [np.zeros(data[0].shape, dtype=np.float32)] * n
    for ii in range(n):
        bulge_size = bulge[ii].shape[0]
        ix0, ix1 = (data_size - bulge_size) // 2, (data_size + bulge_size) // 2
        model[ii][ix0: ix1, ix0: ix1] = a_bulge * bulge[ii].astype(np.float64)
        disc_size = disc[ii].shape[0]
        ix0, ix1 = (data_size - disc_size) // 2, (data_size + disc_size) // 2
        model[ii][ix0: ix1, ix0: ix1] += a_disc * disc[ii].astype(np.float64)

    if return_coeff:
        return model, a_bulge, a_disc
    else:
        return model


def marginal_model_1component(p, model_fcn, data, weights, return_coeff=False):
    """
    Disc-only galaxy model marginalised over data.
    It returns the marginalised model.

    :type p: ndarray
    :type model_fcn: list of lambda
    :type data: list of ndarray
    :type weights: list of ndarray
    :rtype: float
    """

    # get model
    n = len(data)
    w_size = weights[0].shape[0]
    model = [None] * n
    model_w = [None] * n
    for ii in range(n):
        model[ii] = np.copy(model_fcn[ii](p))
        size = model[ii].shape[0]
        ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
        model_w[ii] = model[ii] * weights[ii][ix0: ix1, ix0: ix1]

    # get cross products
    model_model = cross_product(model, model_w)
    model_data = cross_product(data, model_w)

    # check on linear coefficient
    if model_data > 0 and model_model > 0:
        a = model_data / model_model
    else:
        a = 0.

    # model = a * disc
    n = len(data)
    data_size = data[0].shape[0]
    out_model = [np.zeros(data[0].shape, dtype=np.float32)] * n
    for ii in range(n):
        model_size = model[ii].shape[0]
        ix0, ix1 = (data_size - model_size) // 2, (data_size + model_size) // 2
        out_model[ii][ix0: ix1, ix0: ix1] = a * model[ii].astype(np.float64)

    if return_coeff:
        return out_model, a
    else:
        return out_model


def marginal_model_joint(p, bulge_model_fcns, disc_model_fcns, data, weights, return_coeff=False, return_models=False):
    """
    Bulge+disc galaxy model marginalised over data.
    It returns the marginalised model, and the two linear coefficients.

    :type p: ndarray
    :type bulge_model_fcns: list of lambda
    :type disc_model_fcns: list of lambda
    :type data: list of ndarray
    :type weights: list of ndarray
    :rtype: float
    """

    # get models
    n, o = len(data), len(disc_model_fcns)
    w_size = weights[0].shape[0]
    bulge = [None] * o
    disc = [None] * o
    bulge_w = [None] * o
    disc_w = [None] * o
    for ii in range(o):
        bulge[ii] = [None] * n
        disc[ii] = [None] * n
        bulge_w[ii] = [None] * n
        disc_w[ii] = [None] * n
        for jj in range(n):
            ip0 = 5 * ii
            p_in_model = p[ip0: 5 * (ii + 1)]
            bulge[ii][jj] = np.copy(bulge_model_fcns[ii][jj](p_in_model))
            disc[ii][jj] = np.copy(disc_model_fcns[ii][jj](p_in_model))
            size = bulge[ii][jj].shape[0]
            ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
            bulge_w[ii][jj] = bulge[ii][jj] * weights[jj][ix0: ix1, ix0: ix1]
            size = disc[ii][jj].shape[0]
            ix0, ix1 = (w_size - size) // 2, (w_size + size) // 2
            disc_w[ii][jj] = disc[ii][jj] * weights[jj][ix0: ix1, ix0: ix1]

    # get cross products
    bulge_bulge = np.empty((o, o))
    disc_disc = np.empty((o, o))
    bulge_disc = np.empty((o, o))
    bulge_data = np.empty((o,))
    disc_data = np.empty((o,))
    for ii in range(o):
        for jj in range(o):
            if jj >= ii:
                bulge_bulge[ii, jj] = cross_product(bulge[ii], bulge_w[jj])
                bulge_disc[ii, jj] = cross_product(disc[ii], bulge_w[jj])
                disc_disc[ii, jj] = cross_product(disc[ii], disc_w[jj])
            else:
                bulge_bulge[ii, jj] = bulge_bulge[jj, ii]
                bulge_disc[ii, jj] = bulge_disc[jj, ii]
                disc_disc[ii, jj] = disc_disc[jj, ii]
        bulge_data[ii] = cross_product(data, bulge_w[ii])
        disc_data[ii] = cross_product(data, disc_w[ii])

    # Fisher matrix and data vector
    # axis order: bulge of object 0, disc of object 0, bulge of object 1, disc of object 1, ...
    o2 = 2 * o
    X = np.empty(o2)
    F = np.empty((o2, o2))
    for ii in range(o):
        ix0, ix1 = 2 * ii, 2 * (ii + 1)
        X[ix0: ix1] = [bulge_data[ii], disc_data[ii]]
        for jj in range(o):
            iy0, iy1 = 2 * jj, 2 * (jj + 1)
            F[ix0: ix1, iy0: iy1] = [[bulge_bulge[ii, jj], bulge_disc[ii, jj]], [bulge_disc[ii, jj], disc_disc[ii, jj]]]

    # coefficients
    Y, _ = nnls(F, X)

    # model = a_bulge * bulge + a_disc * disc
    data_size = data[0].shape[0]
    model = [np.zeros(data[0].shape, dtype=np.float64)] * n
    models = [None] * o
    a_bulge = Y[::2]
    a_disc = Y[1::2]
    for ii in range(o):
        models[ii] = [np.zeros(data[0].shape, dtype=np.float64)] * n
        for jj in range(n):
            # bulge
            bulge_size = bulge[ii][jj].shape[0]
            ix0, ix1 = (data_size - bulge_size) // 2, (data_size + bulge_size) // 2
            models[ii][jj][ix0: ix1, ix0: ix1] = a_bulge[ii] * bulge[ii][jj]
            # disc
            disc_size = disc[ii][jj].shape[0]
            ix0, ix1 = (data_size - disc_size) // 2, (data_size + disc_size) // 2
            models[ii][jj][ix0: ix1, ix0: ix1] += a_disc[ii] * disc[ii][jj]
            # sum
            model[jj] += models[ii][jj]

    if return_coeff and return_models:
        return model, models, a_bulge, a_disc
    elif return_coeff and not return_models:
        return model, a_bulge, a_disc,
    elif not return_coeff and return_models:
        return model, models
    else:
        return model


def model_joint(p, bulge_model_fcns, disc_model_fcns, image_size, return_models=False):
    """
    Bulge+disc galaxy model.

    :type p: ndarray
    :type bulge_model_fcns: list of lambda
    :type disc_model_fcns: list of lambda
    :type image_size: int
    :rtype: float
    """

    # calculate models
    n, o = len(bulge_model_fcns[0]), len(disc_model_fcns)
    model = [None] * n
    for jj in range(n):
        model[jj] = np.zeros((image_size, image_size))
    if return_models:
        models = [None] * o
        for ii in range(o):
            models[ii] = [None] * n
            for jj in range(n):
                models[ii][jj] = np.zeros((image_size, image_size))
    for ii in range(o):
        # parameters
        ip0 = 7 * ii
        ip1 = ip0 + 5
        p_in_model = p[ip0: ip1]
        flux_bulge, flux_disc = p[ip1], p[ip1 + 1]

        for jj in range(n):
            # bulge
            bulge = flux_bulge * bulge_model_fcns[ii][jj](p_in_model)
            size = bulge.shape[0]
            ix0, ix1 = (image_size - size) // 2, (image_size + size) // 2
            model[jj][ix0: ix1, ix0: ix1] += bulge
            if return_models:
                models[ii][jj][ix0: ix1, ix0: ix1] += bulge

            # disc
            disc = flux_disc * disc_model_fcns[ii][jj](p_in_model)
            size = disc.shape[0]
            ix0, ix1 = (image_size - size) // 2, (image_size + size) // 2
            model[jj][ix0: ix1, ix0: ix1] += disc
            if return_models:
                models[ii][jj][ix0: ix1, ix0: ix1] += disc

    if return_models:
        return model, models
    else:
        return model


def _log_likl(F, X, log_likl_const):
    Y, _ = nnls(F, X)
    return .5 * X.T @ Y + log_likl_const
