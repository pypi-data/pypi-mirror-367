cimport cython
cimport numpy as np
from math import sqrt
from numpy import asarray, copy, float64


@cython.boundscheck(False)
@cython.wraparound(False)
def linear_fit(x, y, w=None):
    """
    Weighted linear least square fit. Fit the model (1+m)+c.
    Return m, c and their errors scaled by the rms of the residuals assuming that in general
    the weights may not accurately reproduce the underlying statistical scatter.
    """

    cdef bint weighted = w is not None

    x = asarray(x)
    y = asarray(y)
    if weighted:
        w = asarray(w)

    cdef int n = x.size

    if y.size != n or (weighted and w.size != n):
        raise Exception('Inputs must all have the same size')

    dtype = x.dtype
    if (y.dtype != dtype) or (weighted and w.dtype != dtype):
        raise Exception('Inputs must be of the same type')

    if x.base is not None:
        x = copy(x)
    if y.base is not None:
        y = copy(y)
    if weighted and w.base is not None:
        w = copy(w)

    if weighted:
        if dtype == float64:
            sxx, sxdy, sx, sdy, s, d = _get_weighted_coefficients_double(x, y, w, n)
        else:
            sxx, sxdy, sx, sdy, s, d = _get_weighted_coefficients_single(x, y, w, n)
    else:
        if dtype == float64:
            sxx, sxdy, sx, sdy, s, d = _get_unweighted_coefficients_double(x, y, n)
        else:
            sxx, sxdy, sx, sdy, s, d = _get_unweighted_coefficients_single(x, y, n)

    cdef double m = (s * sxdy - sx * sdy) / d
    cdef double c = (-sx * sxdy + sxx * sdy) / d

    if weighted:
        if dtype == float64:
            chi2 = _get_weighted_chi2_double(x, y, w, n, m, c)
        else:
            chi2 = _get_weighted_chi2_single(x, y, w, n, m, c)
    else:
        if dtype == float64:
            chi2 = _get_unweighted_chi2_double(x, y, n, m, c)
        else:
            chi2 = _get_unweighted_chi2_single(x, y, n, m, c)

    cdef double norm = chi2 / d
    cdef double dm = sqrt(s * norm)
    cdef double dc = sqrt(sxx * norm)

    return m, c, dm, dc


@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple _get_weighted_coefficients_double(np.float64_t[:] x, np.float64_t[:] y, np.float64_t[:] w, int n):

    cdef double sxx = 0
    cdef double sxdy = 0
    cdef double sx = 0
    cdef double sdy = 0
    cdef double s = 0
    cdef double xi, wi, xwi, xyi
    cdef int ii
    for ii in range(n):
        xi = x[ii]
        wi = w[ii]
        xwi = xi * wi
        xyi = y[ii] - xi
        sxx += xi * xwi
        sxdy += xyi * xwi
        sx += xwi
        sdy += xyi * wi
        s += wi
    cdef double d = s * sxx - sx * sx

    return sxx, sxdy, sx, sdy, s, d


@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple _get_unweighted_coefficients_double(np.float64_t[:] x, np.float64_t[:] y, int n):

    cdef double sxx = 0
    cdef double sxdy = 0
    cdef double sx = 0
    cdef double sdy = 0
    cdef double xi, xyi
    cdef int ii
    for ii in range(n):
        xi = x[ii]
        xyi = y[ii] - xi
        sxx += xi * xi
        sxdy += xyi * xi
        sx += xi
        sdy += xyi
    cdef double d = n * sxx - sx * sx

    return sxx, sxdy, sx, sdy, n, d


@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _get_weighted_chi2_double(np.float64_t[:] x, np.float64_t[:] y, np.float64_t[:] w, int n, double m, double c):

    cdef double r
    cdef double chi2 = 0
    for ii in range(n):
        r = y[ii] - (1 + m) * x[ii] - c
        chi2 += r * r * w[ii]
    chi2 /= (n - 2)

    return chi2


@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _get_unweighted_chi2_double(np.float64_t[:] x, np.float64_t[:] y, int n, double m, double c):

    cdef double r
    cdef double chi2 = 0
    for ii in range(n):
        r = y[ii] - (1 + m) * x[ii] - c
        chi2 += r * r
    chi2 /= (n - 2)

    return chi2


@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple _get_weighted_coefficients_single(np.float32_t[:] x, np.float32_t[:] y, np.float32_t[:] w, int n):

    cdef double sxx = 0
    cdef double sxdy = 0
    cdef double sx = 0
    cdef double sdy = 0
    cdef double s = 0
    cdef double xi, wi, xwi, xyi
    cdef int ii
    for ii in range(n):
        xi = x[ii]
        wi = w[ii]
        xwi = xi * wi
        xyi = y[ii] - xi
        sxx += xi * xwi
        sxdy += xyi * xwi
        sx += xwi
        sdy += xyi * wi
        s += wi
    cdef double d = s * sxx - sx * sx

    return sxx, sxdy, sx, sdy, s, d


@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple _get_unweighted_coefficients_single(np.float32_t[:] x, np.float32_t[:] y, int n):

    cdef double sxx = 0
    cdef double sxdy = 0
    cdef double sx = 0
    cdef double sdy = 0
    cdef double xi, xyi
    cdef int ii
    for ii in range(n):
        xi = x[ii]
        xyi = y[ii] - xi
        sxx += xi * xi
        sxdy += xyi * xi
        sx += xi
        sdy += xyi
    cdef double d = n * sxx - sx * sx

    return sxx, sxdy, sx, sdy, n, d


@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _get_weighted_chi2_single(np.float32_t[:] x, np.float32_t[:] y, np.float32_t[:] w, int n, double m, double c):

    cdef double r
    cdef double chi2 = 0
    for ii in range(n):
        r = y[ii] - (1 + m) * x[ii] - c
        chi2 += r * r * w[ii]
    chi2 /= (n - 2)

    return chi2


@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _get_unweighted_chi2_single(np.float32_t[:] x, np.float32_t[:] y, int n, double m, double c):

    cdef double r
    cdef double chi2 = 0
    for ii in range(n):
        r = y[ii] - (1 + m) * x[ii] - c
        chi2 += r * r
    chi2 /= (n - 2)

    return chi2
