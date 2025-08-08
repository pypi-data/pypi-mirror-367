"""
LensMC - a Python package for weak lensing shear measurements.
Python wrapper of fast model generation C library.

Copyright 2015 Giuseppe Congedo
"""

cimport cython
cimport numpy as np
import numpy as np
from numpy.fft import ifftshift

cimport star_model


eye = np.eye(2, dtype=np.float64)


@cython.boundscheck(False)
@cython.wraparound(False)
def generate_model(double delta_x, double delta_y,
                   tuple psf_ft,
                   working_arrays,
                   np.ndarray[np.float64_t, ndim=2, mode="c"] astrometric_distortion=None,
                   double x_offset=0., double y_offset=0.,
                   bint psf_centring=False, unsigned int odim_min=32):
    """
    Fast galaxy model generation function - wrapper of C source file.
    This wrapper function chooses between different input galaxy sizes, and between different output array sizes
    depending on the required galaxy size. It is fast as all arrays are pre-allocated in the outer scope.
    """

    # extract working arrays
    cdef tuple odim = working_arrays.odim
    cdef int oversampling = working_arrays.oversampling
    cdef tuple dsmodel_plan = working_arrays.dsmodel_plan

    # all input sizes are in units of detector pixels

    if astrometric_distortion is None:
        astrometric_distortion = eye

    # check minimum model array size
    for ii in range(len(odim)):
        if odim[ii] >= odim_min:
            oo = ii
            break
    else:
        raise Exception('Cannot allocate the desired model array size.')

    cdef np.ndarray[np.complex64_t, ndim=2, mode="c"] psf_ft_at_o = psf_ft[oo]
    cdef np.ndarray[np.complex64_t, ndim=1, mode="c"] xshift_ft = working_arrays.xshift_ft
    cdef np.ndarray[np.complex64_t, ndim=1, mode="c"] yshift_ft = working_arrays.yshift_ft
    cdef np.ndarray[np.complex64_t, ndim=2, mode="c"] convmodel_ft = working_arrays.convmodel_ft[oo]
    cdef np.ndarray[np.complex64_t, ndim=2, mode="c"] dsmodel_ft = working_arrays.dsmodel_plan[oo].input_array

    # call the module for model generation
    star_model.generate_star_model(
        delta_x, delta_y,
        &astrometric_distortion[0, 0], x_offset, y_offset,
        odim[oo], oversampling,
        &psf_ft_at_o[0, 0],
        &xshift_ft[0], &yshift_ft[0],
        &convmodel_ft[0, 0], &dsmodel_ft[0, 0])

    # ifft to real space
    dsmodel_plan[oo]()
    model = dsmodel_plan[oo].output_array.real
    model[model < 0] = 0

    # if psf has zero frequency in the corner, then swap quadrants
    if psf_centring:
        model = ifftshift(model)

    return model
