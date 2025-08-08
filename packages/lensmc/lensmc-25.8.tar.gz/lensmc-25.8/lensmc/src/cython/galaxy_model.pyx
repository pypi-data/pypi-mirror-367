"""
LensMC - a Python package for weak lensing shear measurements.
Fast galaxy model generation interfacing with C library.

Copyright 2015 Giuseppe Congedo
"""

cimport cython
cimport numpy as np
import numpy as np
import os
import pickle
import pyfftw
from numpy.fft import ifftshift
from pkg_resources import resource_filename

cimport galaxy_model
from lensmc import __path__ as lensmc_path
from lensmc.utils import LensMCError, logger


n_disc = (1.,)
n_bulge = (0.5, 1., 1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5., 5.5, 6.)
odim = (32, 48, 64, 96, 128, 192, 256, 384)
rfiducial = (2., 4., 8., 16., 32.)
oversampling = 1
mdim = 16384
n_odim, n_rfiducial = len(odim), len(rfiducial)

sqrt2 = 1.4142135623730951
s_cutoff = 18.  # 2 x 2 x 4.5 x exponential scalelength
delta_max_pix = 10  # pixels away from the centre

eye = np.eye(2, dtype=np.float64)

failure_array = np.zeros((odim[0], odim[0]), dtype=np.float32)


cdef class WorkingArrays:

    __slots__ = ('rfiducial', 'odim', 'mdim', 'oversampling', 'n_bulge', 'n_disc',
                 'bulge_ht', 'disc_ht', 'dsmodel_plan',
                 'resampled_model_ft', 'xshift_ft', 'yshift_ft',
                 'convmodel_ft')

    cdef readonly tuple rfiducial
    cdef readonly tuple odim
    cdef readonly int mdim
    cdef readonly int oversampling
    cdef readonly float n_bulge
    cdef readonly float n_disc
    cdef readonly tuple bulge_ht
    cdef readonly tuple disc_ht
    cdef readonly tuple dsmodel_plan
    cdef readonly object resampled_model_ft
    cdef readonly object xshift_ft
    cdef readonly object yshift_ft
    cdef readonly tuple convmodel_ft
    cdef readonly int oo
    cdef readonly int rr


    def __init__(self, tuple rfiducial, tuple odim, int mdim, int oversampling, float n_bulge, float n_disc,
        tuple bulge_ht, tuple disc_ht, tuple dsmodel_plan,
        np.ndarray[np.float32_t, ndim=2, mode="c"] resampled_model_ft,
        np.ndarray[np.complex64_t, ndim=1, mode="c"] xshift_ft,
        np.ndarray[np.complex64_t, ndim=1, mode="c"] yshift_ft,
        tuple convmodel_ft, int oo=0, int rr=0):

        self.rfiducial = rfiducial
        self.odim = odim
        self.mdim = mdim
        self.oversampling = oversampling
        self.n_bulge = n_bulge
        self.n_disc = n_disc
        self.bulge_ht = bulge_ht
        self.disc_ht = disc_ht
        self.dsmodel_plan = dsmodel_plan
        self.resampled_model_ft = resampled_model_ft
        self.xshift_ft = xshift_ft
        self.yshift_ft = yshift_ft
        self.convmodel_ft = convmodel_ft
        self.oo = oo
        self.rr = rr


@cython.boundscheck(False)
@cython.wraparound(False)
def generate_model(double e1, double e2, double s, double delta_x, double delta_y, tuple model_ht,
                   tuple psf_ft, WorkingArrays working_arrays,
                   np.ndarray[np.float64_t, ndim=2, mode="c"] astrometric_distortion=None,
                   double x_offset=0., double y_offset=0.,
                   double pixel_scale=1.,
                   bint semimajor=1, bint psf_centring=0,
                   bint do_hankel_resample=True, bint do_choose_model_size=True, unsigned int odim_min=32):
    """
    Fast galaxy model generation function - wrapper of C source file.
    This wrapper function chooses between different input galaxy sizes, and between different output array sizes
    depending on the required galaxy size. It is fast as all arrays are pre-allocated in the outer scope.
    """

    # extract working arrays
    cdef tuple rfiducial = working_arrays.rfiducial
    cdef tuple odim = working_arrays.odim
    cdef int mdim = working_arrays.mdim
    cdef int oversampling = working_arrays.oversampling
    cdef tuple dsmodel_plan = working_arrays.dsmodel_plan

    # all input sizes are in units of detector pixels

    if astrometric_distortion is None:
        astrometric_distortion = eye

    if do_choose_model_size:

        # size in pixels
        s_pix = s / pixel_scale

        # to determine the output dimension,
        # find index of first occurrence of 2*2*4.5 * galsize < odim_templates
        # also accounts for any large offset that may have been applied
        s_cutoff_by_s_pix = s_cutoff * s_pix
        s_cutoff_by_s_pix += 4 * max(abs(x_offset), abs(y_offset))
        s_cutoff_by_s_pix = max(s_cutoff_by_s_pix, odim_min)
        for ii in range(n_odim):
            if odim[ii] >= s_cutoff_by_s_pix:
                oo = ii
                working_arrays.oo = oo
                break
        else:
            logger.debug('Galaxy size too big. Increase max dimension of output array.')
            return failure_array

        # to determine the input galaxy size,
        # find index of first occurrence of galsize < galsize_templates
        sqrt2_by_s_pix = sqrt2 * s_pix
        for ii in range(n_rfiducial):
            if rfiducial[ii] > sqrt2_by_s_pix:
                rr = ii
                break
        else:
            logger.debug('Galaxy size too big. Increase max fiducial radius of input galaxy.')
            return failure_array
        working_arrays.rr = rr

    else:
        oo = working_arrays.oo
        rr = working_arrays.rr

    # max position shift
    delta_max = delta_max_pix * pixel_scale

    # check position offsets
    if abs(delta_x) > delta_max:
        logger.debug('Galaxy x offset too big.')
        return failure_array
    if abs(delta_y) > delta_max:
        logger.debug('Galaxy y offset too big.')
        return failure_array

    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] model_ht_at_r = model_ht[rr]
    cdef np.ndarray[np.float32_t, ndim=2, mode="c"] resampledmodel_ft = working_arrays.resampled_model_ft
    cdef np.ndarray[np.complex64_t, ndim=2, mode="c"] psf_ft_at_o = psf_ft[oo]
    cdef np.ndarray[np.complex64_t, ndim=1, mode="c"] xshift_ft = working_arrays.xshift_ft
    cdef np.ndarray[np.complex64_t, ndim=1, mode="c"] yshift_ft = working_arrays.yshift_ft
    cdef np.ndarray[np.complex64_t, ndim=2, mode="c"] convmodel_ft = working_arrays.convmodel_ft[oo]
    cdef np.ndarray[np.complex64_t, ndim=2, mode="c"] dsmodel_ft = working_arrays.dsmodel_plan[oo].input_array

    # call the module for model generation
    galaxy_model.generate_galaxy_model(
        e1, e2, s, delta_x, delta_y, semimajor, rfiducial[rr],
        &astrometric_distortion[0, 0], x_offset, y_offset,
        odim[oo], mdim, oversampling,
        &model_ht_at_r[0], &resampledmodel_ft[0, 0],
        &psf_ft_at_o[0, 0],
        &xshift_ft[0], &yshift_ft[0],
        &convmodel_ft[0, 0], &dsmodel_ft[0, 0],
        do_hankel_resample)

    # ifft to real space
    dsmodel_plan[oo]()
    model = dsmodel_plan[oo].output_array.real
    model[model < 0] = 0

    # if psf has zero frequency in the corner, then swap quadrants
    if psf_centring:
        model = ifftshift(model)

    return model


def generate_templates(rfiducial=rfiducial, oversampling=oversampling, cache_file=None, mdim=mdim,
                       n_bulge=n_bulge, n_disc=n_disc, dtype=np.float32, fftw_flags=('FFTW_MEASURE',)):
    """
    Make a set of isotropic model templates (i.e. circular galaxies) for fast model generation.
    It returns a dictionary of templates for every Sersic indices, and for every fiducial galaxy sizes.
    As this is heavy duty calculation, the templates are actually generated only if the cache file doesn't exist.

    :param rfiducial: Fiducial galaxy sizes [pixel]
    :type rfiducial: tuple of float
    :param oversampling: Oversampling factor of the model wrt to actual sampling.
    :type oversampling: int
    :param cache_file: File containing the model templates cache
    :type cache_file: str
    :param mdim: Dimension of isotropic galaxy model for Hankel transform
    :type mdim: int
    :param n_bulge: Bulge Sersic index; available: n=(1., 1.5, 2., 2.5, 3., 3.5, 4.)
    :type n_bulge: float
    :param n_disc: Disc Sersic index; available: n=1
    :type n_disc: float
    :param dtype: Output model's data type
    :type dtype: type
    :param fftw_flags: FFTW flags; choose ('FFTW_ESTIMATE',) for completely deterministic output; see https://www.fftw.org/faq/section3.html#nondeterministic
    :type fftw_flags: Tuple
    :return: templates: Model templates
    :rtype templates: dict
    """

    # load templates from cache file
    # check all filenames, provided or standard paths
    # otherwise generate and save it to provided filename or aux directory (as a default)
    if cache_file is not None:
        if os.path.isfile(cache_file):
            with open(cache_file, 'rb') as fo:
                return pickle.load(fo)
    else:
        cache_files = [os.path.join(lensmc_path[0], f'aux/cache_{oversampling}x.bin'), resource_filename('lensmc', 'cache.bin')]
        for f in cache_files:
            if f is not None and os.path.isfile(f):
                with open(f, 'rb') as fo:
                    return pickle.load(fo)
    cache_file = cache_file if cache_file is not None else cache_files[0]

    cdef np.ndarray[np.float64_t, ndim=2, mode="c"] model = np.zeros((mdim, mdim), dtype=np.float64)
    cdef np.ndarray[np.complex128_t, ndim=2, mode="c"] model_ft = np.zeros((mdim, mdim // 2 + 1), dtype=np.complex128)

    print('Generating model templates cache, this may take a while...')

    # FFTW plan
    fftw_plan = pyfftw.FFTW(model, model_ft, axes=(0, 1), threads=1, flags=fftw_flags)
    fftw_plan()

    # galaxy model internal oversampling - not to confuse with the external oversampling
    # a ~ 2*n - 0.331, for half-light radius [S. Bridle et al MNRAS 405, 2044 (2010)]
    # in generating the circular models, we choose the oversampling factor such that the relative difference
    # from the analytical calculation is <0.1%;
    # for n=1,2,4 (a=1,3.669,7.669) the oversampling factors are 5, 29, 285;
    # so we get this interpolating function osampl = 8.08333 n - 9.375 n^2 + 6.29167 n^3

    def model_oversampling_fcn(n):
        return int(8.08333 * n - 9.375 * n ** 2 + 6.29167 * n ** 3)

    # define length of bulge and disc Sersic indices tuple
    n_n_bulge = len(n_bulge)
    n_n_disc = len(n_disc)

    # calculate the correct normalisation
    # make sure the bulge effective radius is half-light
    # whereas the disc effective radius is always exponential
    a_bulge = tuple(2 * n - 0.331 for n in n_bulge)
    a_disc = (1,) * n_n_disc

    # initialise output dictionary
    templates = {'rfiducial': tuple(rfiducial),
                 'mdim': mdim,
                 'oversampling': oversampling,
                 'n_bulge': tuple(n_bulge),
                 'n_disc': tuple(n_disc),
                 'a_bulge': a_bulge,
                 'a_disc': a_disc,
                 'bulge_ht': [None] * n_n_bulge,
                 'disc_ht': [None] * n_n_disc}

    # bulge: loop over Sersic indices and fiducial sizes
    for jj in range(n_n_bulge):

        print(f'Bulge Sersic index n={n_bulge[jj]}...')

        model_ht = [0] * n_rfiducial
        model_oversampling = model_oversampling_fcn(n_bulge[jj])
        for ii in range(n_rfiducial):
            # generate circular galaxy template
            galaxy_model.make_circular_galaxy(n_bulge[jj], a_bulge[jj], rfiducial[ii] * oversampling, mdim,
                                              model_oversampling, &model[0, 0])
            # inverse swap quadrants
            model[:, :] = np.fft.ifftshift(model)
            # calculate fft
            fftw_plan()
            # take the Hankel transform and store
            model_ht[ii] = (model_ft[0].real / model_ft[0, 0].real).astype(dtype)
        templates['bulge_ht'][jj] = tuple(model_ht)
    templates['bulge_ht'] = tuple(templates['bulge_ht'])

    # disc: loop over Sersic indices and fiducial sizes
    for jj in range(n_n_disc):

        print(f'Disc Sersic index n={n_disc[jj]}...')

        model_ht = [0] * n_rfiducial
        model_oversampling = model_oversampling_fcn(n_disc[jj])
        for ii in range(n_rfiducial):
            # generate circular galaxy template
            galaxy_model.make_circular_galaxy(n_disc[jj], a_disc[jj], rfiducial[ii] * oversampling, mdim,
                                              model_oversampling, &model[0, 0])
            # inverse swap quadrants
            model[:, :] = np.fft.ifftshift(model)
            # calculate fft
            fftw_plan()
            # take the Hankel transform and store
            model_ht[ii] = (model_ft[0].real / model_ft[0, 0].real).astype(dtype)
        templates['disc_ht'][jj] = tuple(model_ht)
    templates['disc_ht'] = tuple(templates['disc_ht'])

    # save to cache
    with open(cache_file, 'wb') as fo:
        pickle.dump(templates, fo)

    print('Model templates cache saved to ' + cache_file)

    return templates


def alloc_working_arrays(n_bulge, n_disc, rfiducial=rfiducial, odim=odim, oversampling=oversampling, cache_file=None, mdim=mdim,
                         dtype=np.float32, fftw_flags=('FFTW_MEASURE',)):
    """
    Allocate the dictionary of working arrays for fast model generation.

    :param n_bulge: Bulge Sersic index; available: n=(1., 1.5, 2., 2.5, 3., 3.5, 4.)
    :type n_bulge: float
    :param n_disc: Disc Sersic index; available: n=1
    :type n_disc: float
    :param rfiducial: Fiducial galaxy sizes [pixel]
    :type rfiducial: tuple of float
    :param odim: Dimensions of output model array
    :type odim: tuple of int
    :param oversampling: Oversampling factor of the model wrt to actual sampling.
    :type oversampling: int
    :param cache_file: File containing the model templates cache.
    :type cache_file: str
    :param mdim: Dimension of isotropic galaxy model for Hankel transform.
    :type mdim: int
    :param dtype: Output model's data type
    :type dtype: type
    :param fftw_flags: FFTW flags; choose ('FFTW_ESTIMATE',) for completely deterministic output; see https://www.fftw.org/faq/section3.html#nondeterministic
    :type fftw_flags: Tuple
    :return working_arrays: All working arrays
    :rtype working_arrays: WorkingArrays
    """

    # to tuple
    rfiducial = tuple(rfiducial)
    odim = tuple(odim)

    # define complex type for fftw
    if np.issubdtype(dtype, np.float32):
        dtype_ft = np.complex64
    else:
        dtype_ft = np.complex128

    # loop through all output array sizes
    convmodel_ft = [0] * n_odim
    dsmodel_plan = [0] * n_odim
    for ii in range(n_odim):

        # get oversampled array size
        arr_size = oversampling * odim[ii]
        arr_h_size = arr_size // 2 + 1

        # convolved model
        convmodel_ft[ii] = np.empty((arr_size, arr_h_size), dtype=dtype_ft)

        # output galaxy model array, and its Fourier transform
        dsmodel = pyfftw.zeros_aligned((odim[ii], odim[ii]), dtype=dtype_ft)
        dsmodel_ft = pyfftw.zeros_aligned((odim[ii], odim[ii]), dtype=dtype_ft)

        # model FFTW plan
        plan = pyfftw.FFTW(dsmodel_ft, dsmodel, axes=(0, 1), threads=1,
                           flags=fftw_flags, direction='FFTW_BACKWARD')
        plan()
        dsmodel_plan[ii] = plan

    convmodel_ft = tuple(convmodel_ft)
    dsmodel_plan = tuple(dsmodel_plan)

    # get oversampled array max size
    arr_size = oversampling * odim[-1]
    arr_h_size = arr_size // 2 + 1

    # resampled input galaxy model (bulge and disc) arrays
    resampled_model_ft = np.empty((arr_size, arr_h_size), dtype=dtype)

    # Fourier transforms of x/y shift and convolved model
    xshift_ft = np.empty((arr_h_size,), dtype=dtype_ft)
    yshift_ft = np.empty((arr_size,), dtype=dtype_ft)

    # load or generate isotropic input galaxy model arrays
    templates_cache = generate_templates(rfiducial=rfiducial, oversampling=oversampling, cache_file=cache_file,
                                         mdim=mdim, dtype=dtype)

    # check consistency of parameters
    if n_bulge not in templates_cache['n_bulge']:
        raise LensMCError('The requested \'n_bulge\' does not match with the ones stored in cache.')
    if rfiducial != templates_cache['rfiducial']:
        raise LensMCError('The requested \'rfiducial\' does not match with the ones stored in cache.')
    if oversampling != templates_cache['oversampling']:
        raise LensMCError('The requested \'oversampling\' does not match with the one stored in cache.')
    if mdim != templates_cache['mdim']:
        raise LensMCError('The requested \'mdim\' does not match with the one stored in cache.')

    # load isotropic galaxy model templates from cache
    disc_model_ht = tuple(templates_cache['disc_ht'][templates_cache['n_disc'].index(n_disc)])
    bulge_model_ht = tuple(templates_cache['bulge_ht'][templates_cache['n_bulge'].index(n_bulge)])

    # working arrays
    working_arrays = WorkingArrays(
        rfiducial, odim, mdim, oversampling, n_bulge, n_disc,
        bulge_model_ht, disc_model_ht, dsmodel_plan,
        resampled_model_ft, xshift_ft, yshift_ft,
        convmodel_ft)

    return working_arrays
