"""
Lensmc - a Python package for weak lensing shear measurements.
This is a module containing models for lensmc.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from numpy import exp, inf, log, sqrt


log10_e = np.log10(np.e)


def shear_ellipticity(e1, e2, g1, g2):
    """
    Shear a set of ellipticity values ('e1' and 'e2') with a set of shear values ('g1' and 'g2').
    To get the inverse transformation, negate the input shear.

    :type e1: ndarray
    :type e2: ndarray
    :type g1: ndarray
    :type g2: ndarray
    :rtype: ndarray
    :rtype: ndarray
    """

    emod2 = e1 ** 2 + e2 ** 2
    e1g1, e2g2 = e1 * g1, e2 * g2
    g12, g22 = g1 ** 2, g2 ** 2
    denom = (e2 * g1 - e1 * g2) ** 2 + (1 + e1g1 + e2g2) ** 2
    e1 = (e1 * (1 + g12 - g22) + g1 * (1 + emod2 + 2 * e2g2)) / denom
    e2 = (e2 * (1 + g22 - g12) + g2 * (1 + emod2 + 2 * e1g1)) / denom

    return e1, e2


def ellipticity_logprior(e, e0=0.0256, emax=0.804, a=0.2539, components=False):
    """
    Intrinsic elliptiticty prior. Default values for circularity ('e0'), cut-off point ('emax'),
    and dispersion ('a') are set according to Miller et al (2013).

    :type e: ndarray
    :type e0: float
    :type emax: float
    :type a: float
    :rtype: ndarray
    """

    if not components:
        if 0 < e < emax:
            return log(e) + log(1. - exp((e-emax) / a)) - log(1. + e) - log(sqrt(e**2 + e0**2))
        else:
            return -inf
    else:
        if 0 <= e < emax:
            return log(1. - exp((e-emax) / a)) - log(1. + e) - log(sqrt(e**2 + e0**2))
        else:
            return -inf


def mag_logprior(mag, mag_min=20., mag_max=27.5, c=(-0.01410823, 0.97602646, -10.62538433)):
    """
    Joint polynomial fit to VIS magnitudes in the GOODS-S (mag < 26) and UDF (mag > 26) regions.
    A colour correction has already been applied to convert to VIS.

    :type mag: array_like
    :type mag_min: float
    :type mag_max: float
    :type c: tuple
    :rtype: array_like
    """

    mag = np.atleast_1d(mag)
    logp = np.empty_like(mag)
    ix = (mag >= mag_min) & (mag <= mag_max)
    logp[ix] = np.polyval(c, mag[ix]) / log10_e
    logp[~ix] = -inf

    return logp


def star_mag_logprior(mag, mag_min=17., mag_max=26., c=(-9.99806520e-4, 4.66799298e-2, -0.558829047, 3.84945781),
                      i_to_v=0.3):
    """
    Polynomial fit to i magnitudes generated with the Besancon model in the North Ecliptic Pole region (10 sq.deg.).
    A global colour correction is applied to convert to VIS magnitude.

    :type mag: array_like
    :type mag_min: float
    :type mag_max: float
    :type c: tuple
    :type i_to_v: object
    :rtype: array_like
    """

    mag = np.atleast_1d(mag)
    mag = mag - i_to_v
    logp = np.empty_like(mag)
    ix = (mag >= mag_min) & (mag <= mag_max)
    logp[ix] = np.polyval(c, mag[ix]) / log10_e
    logp[~ix] = -inf

    return logp


def size_mag_cond_logprior(s, mag, defaults='HST',
                           s_min=0., s_max=2.,
                           alpha=1.3333333333333333, rd0=1.134,
                           mag0=22.33, rd_const0=-1.092, rd_const1=-0.2154):
    """
    Size prior conditional to magnitude.
    Default values can be chosen from either 'HST' or 'CFHTLenS' [Miller et al (2013)].
    Size is measured in arcsec.

    :type s: ndarray
    :type mag: ndarray
    :type defaults: str
    :type s_min: float
    :type s_max: float
    :type alpha: float
    :type rd0: float
    :type mag0: float
    :type rd_const0: float
    :type rd_const1: float
    :rtype: ndarray
    """

    # default parameters
    if defaults == 'CFHTLenS':
        rd_const0, rd_const1, mag0 = -1.145, -0.269, 23.

    if s_min < s < s_max:
        # median major-axis scalelength VS magnitude
        rd = exp(rd_const0 + rd_const1 * (mag - mag0))
        # exponential scalelength
        a = rd / rd0
        return log(s) - (s / a) ** alpha
    else:
        return -inf


def size_mag_joint_logprior(s, mag, defaults='HST',
                            s_min=0., s_max=2., mag_min=20., mag_max=25.5,
                            alpha=1.3333333333333333, rd0=1.134,
                            mag0=22.33, rd_const0=-1.092, rd_const1=-0.2154):
    """
    Size-magnitude joint prior.
    Default values can be chosen from either 'HST' or 'CFHTLenS' [Miller et al (2013)].
    Size is measured in arcsec.
    p(s,m) = p(s|m) * p(m)

    :type mag: ndarray
    :type s: ndarray
    :type defaults: str
    :type s_min: float
    :type s_max: float
    :type mag_min: float
    :type mag_max: float
    :type alpha: float
    :type rd0: float
    :type mag0: float
    :type rd_const0: float
    :type rd_const1: float
    :rtype: ndarray
    """

    # default parameters
    if defaults == 'CFHTLenS':
        rd_const0, rd_const1, mag0 = -1.145, -0.269, 23.

    # p(m)
    logp_m = mag_logprior(mag, mag_min=mag_min, mag_max=mag_max)

    # p(s|a)
    logp_s_a = size_mag_cond_logprior(s, mag, defaults=defaults,
                                      s_min=s_min, s_max=s_max,
                                      alpha=alpha, rd0=rd0,
                                      mag0=mag0, rd_const0=rd_const0, rd_const1=rd_const1)

    return logp_s_a + logp_m


def bulgefrac_logprior(b, disc_n=1., disc_scale=.07, bulge_mean=1., bulge_std=0.05, bulge_to_disc_scale=0.15, offset=0.03):
    """
    Bulge fraction prior.

    :type b: ndarray
    :type disc_n: float
    :type disc_scale: float
    :type bulge_mean: float
    :type bulge_std: float
    :type bulge_to_disc_scale: float
    :type offset: float
    :rtype: float
    """

    p0 = (b >= 0.) * (b <= 1.) * exp(- (b / disc_scale) ** (1. / disc_n))
    p1 = (b >= 0.) * (b <= 1.) * exp(- .5 * ((b - bulge_mean) / bulge_std) ** 2)

    p = p0 + bulge_to_disc_scale * p1 + offset
    if p > 0:
        return log(p)
    else:
        return - inf


def magnitude2count(mag, zero_point=25.719, count_rate=1., exposure_time=565.):
    """
    Convert magnitude to photoelectron count in the Euclid VIS-band.

    :type mag: ndarray
    :type zero_point: float
    :type count_rate: float
    :type exposure_time: float
    :rtype: ndarray
    """

    count0 = count_rate * exposure_time
    return count0 * 10 ** ((zero_point - mag) / 2.5)


def count2magnitude(count, zero_point=25.719, count_rate=1., exposure_time=565.):
    """
    Convert photoelectron count to magnitude in the Euclid VIS-band.

    :type count: ndarray
    :type zero_point: float
    :type count_rate: float
    :type exposure_time: float
    :rtype: ndarray
    """

    count0 = count_rate * exposure_time
    return -2.5 * np.log10(count / count0) + zero_point


def background_noise(exposure_time=565., bkg_rate=0.225, dark_current=0.001, read_noise=4.5):
    """
    Nominal background noise calculation for Euclid. It returns the noise variance measured in count.

    :rtype: float
    """

    # set observation exposure duration (sec)

    # zodiacal light background count rate per sec (zodiacal and dark current)
    # for nominal bandpass 550-900 nm
    # from https://irsa.ipac.caltech.edu/cgi-bin/BackgroundModel/nph-bgmodel?locstr=0.%20+30.%20ecl&wavelength=0.658&obslocin=0&ido_viewin=1
    # we get about flux = 0.26 MJy/sr
    # flux = 0.26e6 / (180 / np.pi) ** 2 / 3600 ** 2 * 0.1 ** 2 = 0.061 uJy/px
    # AB = 23.9 - 2.5 * np.log10(flux * 1e6) = 26.94
    # count = 10 ** (12.881 - 0.4 * AB) = 127.74
    # rate = count / exp.time = 0.22609
    # at the NEP, the flux is 0.11-0.16 MJy/sr, which ballpark gives 0.138-0.201 count/s
    # but integrated over VIS passband and spectrum gives 0.225

    # dark current count/sec

    # read noise

    # effective background with nominal zodiacal light
    return (bkg_rate + dark_current) * exposure_time + read_noise ** 2
