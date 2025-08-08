"""
LensMC - a Python package for weak lensing shear measurements.
Log-prior for the bulge+disc images testing.

Copyright 2015 Giuseppe Congedo
"""

from math import sqrt
from numpy import inf


def log_prior_unif(p, emax=0.99, smax=20., deltamax=3.):
    """
    Uniform hard bound log-prior for the bulge+disc galaxy model.
    It can be either in pixel or sky coordinates depending on the optional parameters.

    :type p: ndarray
    :type emax: float
    :type smax: float
    :type deltamax: float
    :rtype float
    """

    # ellipticity
    if abs(p[0]) > emax or abs(p[1]) > emax or sqrt(p[0] ** 2 + p[1] ** 2) > emax:
        return -inf

    # size
    if p[2] < 0 or p[2] > smax:
        return -inf

    # position
    if abs(p[3]) > deltamax or abs(p[4]) > deltamax or sqrt(p[3] ** 2 + p[4] ** 2) > deltamax:
        return -inf

    return 0.
