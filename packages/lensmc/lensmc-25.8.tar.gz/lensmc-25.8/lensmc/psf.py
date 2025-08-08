"""
LensMC - a Python package for weak lensing shear measurements.
Process input PSF into a format that is usable by the images simulation and shear measurement.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
import pyfftw
from typing import List, Type, TypeVar, Union

from lensmc.image import Image
# noinspection PyUnresolvedReferences
from lensmc.galaxy_model import odim, oversampling
from lensmc.utils import fwhm as fwhm_fcn, moments as moments_fcn


# generic array like data type
T = TypeVar('T')
ArrayLike = Union[List[np.ndarray], np.ndarray]


class PSF(Image):

    """
    PSF image class used as data container for LensMC.

    :param image: Multiple exposure pixel data
    :param oversampling: Oversampling factor
    :param pixelavg_ft: Pixel average Fourier transforms
    :param order: Axes order
    :param dtype: Pixel data type
    """

    __slots__ = ('exp', 'n_exp', 'oversampling', 'ft', 'pixelavg_ft', 'order', 'dtype')

    def __init__(self, image: ArrayLike, oversampling: int = 1,
                 order: str = 'yx', dtype: Type = np.float32):

        # inherit from image class
        super().__init__(image, order=order, dtype=dtype)

        # set additional attributes
        # including placeholders for oversampling and Fourier transform
        self.oversampling = oversampling
        self.ft = None
        self.pixelavg_ft = None

    def initialise_pixelavg_ft(self, odim=odim, oversampling=oversampling, dtype=np.float32,
                               fftw_flags=('FFTW_MEASURE',)):
        self.pixelavg_ft = initialise_pixelavg_ft(odim=odim, oversampling=oversampling, dtype=dtype,
                                                  fftw_flags=fftw_flags)

    def calculate_ft(self, odim=odim, oversampling=oversampling, dtype=np.float32, fftw_flags=('FFTW_MEASURE',)):
        self.ft = [None] * self.n_exp
        for ii in range(self.n_exp):
            self.ft[ii] = calculate_psf_ft(self[ii], pixelavg_ft=self.pixelavg_ft, odim=odim, oversampling=oversampling,
                                           dtype=dtype, fftw_flags=fftw_flags)

    def get_fwhm(self):
        fwhm = np.empty(self.n_exp)
        for ii in range(self.n_exp):
            fwhm[ii] = 0.5 * (fwhm_fcn(self[ii], axis=0) + fwhm_fcn(self[ii], axis=1))
        fwhm /= self.oversampling
        return fwhm

    def get_moments(self, sigma=2.5):
        e1 = np.empty(self.n_exp)
        e2 = np.empty(self.n_exp)
        r2 = np.empty(self.n_exp)
        x_offset = np.empty(self.n_exp)
        y_offset = np.empty(self.n_exp)
        for ii in range(self.n_exp):
            e1[ii], e2[ii], r2[ii], x, y = moments_fcn(self[ii], sigma * self.oversampling)
            x_offset[ii], y_offset[ii] = x - self[ii].shape[1] // 2, y - self[ii].shape[0] // 2
        r2 /= self.oversampling ** 2
        x_offset /= self.oversampling
        y_offset /= self.oversampling
        return e1, e2, r2, x_offset, y_offset


def calculate_psf_ft(psf, pixelavg_ft=None, odim=odim, oversampling=oversampling, dtype=np.float32,
                     fftw_flags=('FFTW_MEASURE',)):

    # define complex type for fftw
    if np.issubdtype(dtype, np.float32):
        dtype, dtype_ft = np.float32, np.complex64
    elif np.issubdtype(dtype, np.float64):
        dtype, dtype_ft = np.float64, np.complex128

    # check if odim is an iterable
    if not type(odim) in (tuple, list):
        odim = [odim]

    # check pixel average FT
    if pixelavg_ft is not None and type(pixelavg_ft) not in (tuple, list):
        pixelavg_ft = [pixelavg_ft]

    # plan fft before allocating values
    n_out_sizes = len(odim)
    psf_list = [0] * n_out_sizes
    psf_ft_list = [0] * n_out_sizes
    psf_plan_list = [0] * n_out_sizes
    for ii in range(n_out_sizes):

        # get oversampled array size
        arr_size = oversampling * odim[ii]
        arr_h_size = arr_size // 2 + 1

        psf_list[ii] = pyfftw.empty_aligned((arr_size, arr_size), dtype=dtype)
        psf_ft_list[ii] = pyfftw.empty_aligned((arr_size, arr_h_size), dtype=dtype_ft)
        psf_plan_list[ii] = pyfftw.FFTW(psf_list[ii], psf_ft_list[ii], axes=(0, 1), direction='FFTW_FORWARD',
                                        flags=fftw_flags)

    # chop/pad psf to fit the input image size, then copy into psf_list[ii]
    for ii in range(n_out_sizes):
        img_size = odim[ii] * oversampling
        psf_size = psf.shape[0]
        if psf_size > img_size:
            # chop the PSF down to size if it's too large
            chop = (psf.shape[0] - img_size) // 2
            p = np.copy(psf[chop: -chop, chop: -chop])
            p /= p.sum()  # normalise
        elif psf_size == img_size:
            # the psf is the correct size, do nothing
            p = psf
        else:
            # pad the psf with zeros to make it the correct size
            pad = (img_size - psf_size) // 2
            p = np.pad(psf, pad, mode='constant', constant_values=0)
        psf_list[ii][:] = p

    # multiply psf and pixel average together in fourier space
    for ii in range(n_out_sizes):
        # do the FFT of psf_list[ii] to psf_ft_list[ii]
        psf_plan_list[ii]()
        if pixelavg_ft is not None:
            psf_ft_list[ii] *= pixelavg_ft[ii]

    if n_out_sizes > 1:
        return tuple(psf_ft_list)
    else:
        return psf_ft_list[0]


def initialise_pixelavg_ft(odim=odim, oversampling=oversampling, dtype=np.float32, fftw_flags=('FFTW_MEASURE',)):

    # define complex type for fftw
    if np.issubdtype(dtype, np.float32):
        dtype_ft = np.complex64
    else:
        dtype_ft = np.complex128

    # plan fft before allocating values
    oversampling2 = oversampling ** 2
    n_out_sizes = len(odim)
    pixelavg = [0] * n_out_sizes
    pixelavg_ft = [0] * n_out_sizes
    pixelavg_plan = [0] * n_out_sizes
    for ii in range(n_out_sizes):

        # get oversampled array size
        arr_size = oversampling * odim[ii]
        arr_h_size = arr_size // 2 + 1

        # preallocate arrays
        pixelavg[ii] = pyfftw.zeros_aligned((arr_size, arr_size), dtype=dtype)
        pixelavg_ft[ii] = pyfftw.empty_aligned((arr_size, arr_h_size), dtype=dtype_ft)

        # plan the fft
        pixelavg_plan[ii] = pyfftw.FFTW(pixelavg[ii], pixelavg_ft[ii], axes=(0, 1), direction='FFTW_FORWARD',
                                        flags=fftw_flags)

        # allocate pixel average array
        ix0, ix1 = arr_size // 2 - oversampling // 2, arr_size // 2 + oversampling // 2 + 1
        pixelavg[ii][ix0:ix1, ix0:ix1] = 1. / oversampling2

        # swap quadrants
        pixelavg[ii][:] = np.fft.ifftshift(pixelavg[ii])

        # calculate the fft
        pixelavg_plan[ii]()

    return tuple(pixelavg_ft)
