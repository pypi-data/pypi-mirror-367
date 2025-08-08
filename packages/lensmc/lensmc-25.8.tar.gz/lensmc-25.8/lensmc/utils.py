"""
LensMC - a Python package for weak lensing shear measurements.
Module containing utility functions for lensmc.

Copyright 2015 Giuseppe Congedo
"""

import logging
import multiprocessing as mp
import numpy as np
from astropy.coordinates import angular_separation
from scipy.optimize import brenth


_deg_to_rad = np.pi / 180.


# define basic logger
logging.basicConfig(level=logging.INFO, format='%(name)s %(levelname)s: %(message)s')
logger = logging.getLogger('LensMC')


class LensMCError(RuntimeError):
    """Base error class"""
    pass


class Counter:

    def __init__(self, fcn):

        self.calls = 0
        self._fcn = fcn

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self._fcn(*args, **kwargs)

    def reset_calls(self):
        self.calls = 0


def moments(f, sigma=2.5, rtol=1e-5, atol=1e-8, maxiter=100):

    # cut-off point in weighting function
    # rsq_max = (3. * sigma) ** 2

    # pixel grid
    x = np.arange(f.shape[0], dtype=float)
    y = np.arange(f.shape[1], dtype=float)
    x, y = np.meshgrid(x, y)

    # starting point
    e1, e2, r2 = 0., 0., 0.
    x0, y0 = np.average(x, weights=f), np.average(y, weights=f)

    # iterate
    for ii in range(maxiter):
        # keep old values
        e1old, e2old, r2old, x0old, y0old = e1, e2, r2, x0, y0
        # shift by centroid
        xx = x - x0
        yy = y - y0
        # squared quantities
        xsq = xx ** 2
        ysq = yy ** 2
        rsq = xsq + ysq
        # weight function
        w = np.exp(-.5 * rsq / sigma ** 2)
        fw = f * w
        # moments
        qxx = np.sum(xsq * fw)
        qyy = np.sum(ysq * fw)
        qxy = np.sum(xx * yy * fw)
        qq = qxx + qyy
        # estimates
        e1 = (qxx - qyy) / qq
        e2 = (2 * qxy) / qq
        sumw = np.sum(fw)
        r2 = qq / sumw
        x0, y0 = np.sum(x * fw) / sumw, np.sum(y * fw) / sumw
        # check for convergence
        if np.isclose(e1, e1old, rtol=rtol, atol=atol) and np.isclose(e2, e2old, rtol=rtol, atol=atol) \
           and np.isclose(r2, r2old, rtol=rtol, atol=atol) \
           and np.isclose(x0, x0old, rtol=rtol, atol=atol) and np.isclose(y0, y0old, rtol=rtol, atol=atol):
            break
    else:
        logger.warning(f'Did not converge within {maxiter} iterations and the desired tolerance.')

    return e1, e2, r2, x0, y0


def fwhm(f, axis=0):
    """
    Measure the FWHM of an input image along axis 0 or 1. It returns the width in units of pixel.

    :type f: ndarray
    :type axis: int
    :rtype: float
    """

    # maximum flux and half flux
    fmax = np.max(f)
    half_flux = .5 * fmax

    # peak position
    x0 = np.unravel_index(np.argmax(f), f.shape)

    # pixel grid
    x = np.arange(f.shape[axis-1]) - x0[axis]

    # interpolated flux
    if axis == 0:
        f_fcn = lambda p: np.interp(p, x, f[x0[0], :])
    else:
        f_fcn = lambda p: np.interp(p, x, f[:, x0[1]])

    # error function
    err_fcn = lambda x: f_fcn(x) - half_flux

    # find zeros
    try:
        xl = brenth(err_fcn, np.min(x), 0.)
        xu = brenth(err_fcn, 0., np.max(x))
        return xu - xl
    except:
        return np.nan


def ra_dec_area(ra0, ra1, dec0, dec1):
    ra1_flt = np.atleast_1d(ra1).astype(float)
    ra0_flt = np.atleast_1d(ra0).astype(float)
    dec1_flt = np.atleast_1d(dec1).astype(float)
    dec0_flt = np.atleast_1d(dec0).astype(float)
    area = (ra1_flt - ra0_flt) * \
           (np.sin(_deg_to_rad * dec1_flt) - np.sin(_deg_to_rad * dec0_flt))
    if area.size == 1:
        return area[0] / _deg_to_rad
    else:
        return area / _deg_to_rad


def friend_of_friend_neighbour(id_, x, y, r, blends=None, processes=None):
    """
    Make a list of groups of objects based on a friend-of-friend neighbour algorithm.
    x, y, and r in degree.
    """

    # define number of objects
    n = len(id_)

    # check dimensions
    if len(id_) != len(x) or len(id_) != len(y):
        raise LensMCError('ID, x, and y must have the same length.')

    # to radians
    pi_180 = np.pi / 180
    x_rad, y_rad, r_rad = x * pi_180, y * pi_180, r * pi_180

    # by default use all cores
    if processes is None:
        processes = mp.cpu_count()

    # start initialisation of groups in parallel
    # select all objects closer than the distance threshold
    # (distance neighbour)
    # fork the requested number of processes and get results from queue
    def worker(n_list, x_rad, y_rad, id_, queue):
        groups = []
        for n in n_list:
            rr = angular_separation(x_rad[n], y_rad[n], x_rad, y_rad)
            groups += [id_[rr <= r_rad].tolist()]
        queue.put(groups)
        return

    # begin parallel loop
    chunk_size = n // processes
    n_list = list(range(n))
    chunks = [n_list[ii * chunk_size: (ii + 1) * chunk_size] for ii in range(0, processes)]
    for ii in range(n % processes):
        chunks[ii] += [n_list[processes * chunk_size + ii]]
    groups = [None] * processes
    queue = mp.Queue()
    procs = [mp.Process(target=worker, args=(n_list, x_rad, y_rad, id_, queue)) for n_list in chunks]
    [p.start() for p in procs]
    for ii in range(processes):
        groups[ii] = queue.get()
    [p.join() for p in procs]
    groups = [item for sublist in groups for item in sublist]

    # merge groups with blends
    if blends:
        for gg, group in enumerate(groups):
            for bb, blend in enumerate(blends):
                if any(np.isin(group, blend)):
                    groups[gg] += blend
                    groups[gg] = list(set(group))

    # merge groups
    # (friend of friend)
    groups = [set(g) for g in groups]
    for ii in range(n):
        for jj in range(ii, n):
            if any(groups[jj] & groups[ii]):
                groups[ii] = groups[ii].union(groups[jj])
                groups[jj] = groups[jj].union(groups[ii])

    # ensure unique groups
    for ii in range(n):
        groups[ii] = frozenset(groups[ii])
    groups = list(set(groups))
    for ii in range(len(groups)):
        groups[ii] = list(groups[ii])

    return groups
