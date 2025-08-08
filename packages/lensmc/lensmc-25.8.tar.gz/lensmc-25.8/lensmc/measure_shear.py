"""
LensMC - a Python package for weak lensing shear measurements.
Workhorse module of the LensMC package used for the shear measurement.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from astropy.coordinates import angular_separation
from copy import deepcopy
from scipy.stats import f
from typing import List, Tuple, Type, TypeVar, Union

from lensmc.flags import flag_galaxy, flag_bad_residuals, flag_failure
# noinspection PyUnresolvedReferences
from lensmc.galaxy_model import alloc_working_arrays, generate_model as generate_galaxy_model, WorkingArrays
from lensmc.image import Image
from lensmc.likelihood import log_likl, log_likl_1component, log_likl_joint, marginal_model, \
    marginal_model_1component, model_joint
from lensmc.optimise import importance_sampling, sampler, Results
from lensmc.prior import log_prior_unif
from lensmc.psf import PSF
from lensmc.utils import LensMCError, logger


# generic array like data type
T = TypeVar('T')
ArrayLike = Union[T, List[T], np.ndarray]


def measure_shear(image: Image,
                  e1: float = 0., e2: float = 0., re: float = 0.3, delta_ra: float = 0., delta_dec: float = 0.,
                  id_: ArrayLike[int] = None, ra: ArrayLike[float] = None, dec: ArrayLike[float] = None,
                  postage_stamp: int = None, x_buffer: int = 3, y_buffer: int = 3,
                  dilate_mask: bool = True, dilate_segmentation: bool = True, seg_id: ArrayLike[int] = None,
                  psf: Union[PSF, List[PSF]] = None,
                  psf_bulge: Union[PSF, List[PSF]] = None, psf_disc: Union[PSF, List[PSF]] = None,
                  hl_to_exp: float = 0.15, n_bulge: float = 1., n_disc: float = 1.,
                  e_max: float = 0.99, re_max: float = 2., delta_max: float = 0.3,
                  disc_only: bool = False, working_arrays: WorkingArrays = None, cache_file: str = None,
                  intcal: bool = False, cal: bool = False,
                  return_model: bool = False,
                  significance: float = 0.01,
                  maximisation: bool = True, sampling: bool = True,
                  mode: str = None,
                  n_samples: int = 200, n_burnin: int = 500, n_chains: int = 1, n_swap: int = 100,
                  affine_invariant: bool = False, n_ai_samples: int = 20, n_ai_burnin: int = 50, n_ai_chains: int = 10,
                  seed: int = None, fftw_flags: Tuple = ('FFTW_MEASURE',),
                  shape_noise: float = 0.3, r_sg: float = 0.15,
                  copy: bool = True, dtype: Type = np.float32,
                  log_level: str = 'info') -> 'LensMCResults':
    """
    Workhorse of the LensMC package.
    Fit multiple exposure image data and get an estimate of shear for a given target galaxy object.
    Functionality:
    - take care of astrometric distortion(s) and offset(s) if fit is done in world coordinates;
    - accurate PSF convolution(s) for individual galaxy components;
    - estimate RMS and DC level(s) from data if not already provided;
    - combine good pixel mask(s) with segmentation map(s), if provided.
    - fast MCMC sampling and marginalisation of ellipticity posterior
    Returns LensMC analysis object with the shear estimate and extra information such as
    nuisance parameters, Markov chains, etc.

    :param image: Multiple exposure pixel data.
    :param e1: Initial guess for first component of ellipticity.
    :param e2: Initial guess for second component of ellipticity.
    :param re: Initial guess for effective radius, i.e. exp. scalelength of the disc (default: 0.3 arcsec).
    :param delta_ra: Initial guess for RA offset from nominal value.
    :param delta_dec: Initial guess for DEC offset from nominal value.
    :param id_: Object ID(s).
    :param ra: Nominal RA(s).
    :param dec: Nominal DEC(s).
    :param postage_stamp: Size of the square postage stamp that will be extracted internally.
    :param x_buffer: Buffer size along x in pixel to avoid edges of the image.
    :param y_buffer: Buffer size along y in pixel to avoid edges of the image.
    :param dilate_mask: Dilate mask by one pixel.
    :param dilate_segmentation: Dilate segmentation map by one pixel.
    :param seg_id: Segmentation map ID(s).
    :param psf: PSF image(s), before pixel average convolution.
    :param psf_bulge: PSF image(s) of the bulge component, before pixel average convolution.
    :param psf_disc: PSF image(s) of the disc component, before pixel average convolution.
    :param hl_to_exp: Half-light radius of the bulge to exponential scalelength of the disc.
    :param n_bulge: Bulge Sersic index; available: n=(1., 1.5, 2., 2.5, 3., 3.5, 4.).
    :param n_disc: Disc Sersic index; available: n=1.
    :param e_max: Hard upper bound on ellipticity (default: 0.99).
    :param re_max: Hard upper bound on effective radius (default: 2 arcsec).
    :param delta_max: Hard upper bound on position offset (default: 0.3 arcsec).
    :param disc_only: Whether to fit only for a disc component.
    :param working_arrays: Dictionary of various working arrays for model generation.
    :param cache_file: Cache file where to save and load working arrays for model generation.
    :param intcal: Derive internally-calibrated estimator.
    :param cal: Derive calibration estimator (in development).
    :param return_model: Whether to return best-fit model(s), input image data, and residuals.
    :param significance: Significance level for object classification.
    :param maximisation: Maximise posterior before sampling.
    :param sampling: Sample posterior via MCMC.
    :param mode: If set to 'fast', override any sampling settings and produce MAP estimate (without MCMC/errors/intcal).
    :param n_samples: Number of samples per chain.
    :param n_burnin: Number of burnin samples that will be discarded.
    :param n_chains: Number of parallel chains.
    :param n_swap: Number of samples after which samples will be swapped between parallel chains (only if n_chains > 1).
    :param affine_invariant: Sample via affine invariant (AI) MCMC.
    :param n_ai_samples: Number of samples per (AI) chain.
    :param n_ai_burnin: Number of burnin AI samples that will be discarded.
    :param n_ai_chains: Number of parallel (AI) chains.
    :param seed: Seed for the random sampler; see https://numpy.org/doc/stable/reference/random/generator.html
    :param fftw_flags: FFTW flags; choose ('FFTW_ESTIMATE',) for completely deterministic output; see https://www.fftw.org/faq/section3.html#nondeterministic
    :param shape_noise: Standard deviation of the 1d distribution of ellipticity.
    :param r_sg: Threshold on re for star-galaxy separation (default: 0.15 arcsec).
    :param copy: Make a deep copy of some of the input data to make sure they're not modified.
    :param dtype: Pixel data type.
    :param log_level: Set log level (default: info).
    :return: Shear measurement results.
    """

    # set log level
    if log_level != 'info':
        logger.setLevel(log_level.upper())

    logger.debug('Enter measure_shear().')

    # make a deep copy of input data
    if copy:
        logger.debug('Make a deep copy of data.')
        image = deepcopy(image)
        psf = deepcopy(psf)
        psf_bulge = deepcopy(psf_bulge)
        psf_disc = deepcopy(psf_disc)

    logger.debug('Initial checks.')

    # fix data type
    for ii in range(image.n_exp):
        if image[ii].dtype != dtype:
            image[ii] = image[ii].astype(dtype)

    # check postage stamp size
    if postage_stamp is None:
        postage_stamp = np.min([min(image[ii].shape) for ii in range(image.n_exp)]).item() // 2 * 2
    if not isinstance(postage_stamp, int) or postage_stamp % 2:
        raise LensMCError('Postage stamp size must be an even integer.')

    # check minimum image/postage stamp size
    if np.min([min(image[ii].shape) for ii in range(image.n_exp)]) < 384 or postage_stamp < 384:
        raise LensMCError('Image size or required postage stamp size must be >= 384 pixels.')

    # check x and y buffers
    if not isinstance(x_buffer, int) or x_buffer < 0:
        raise LensMCError('x buffer must be a positive integer.')
    if not isinstance(y_buffer, int) or y_buffer < 0:
        raise LensMCError('y buffer must be a positive integer.')

    # check galaxy nominal position
    ra, dec = np.atleast_1d(ra), np.atleast_1d(dec)

    # check object ID
    n_objects = 1
    if id_ is None:
        id_ = 0
        if not np.isscalar(ra) or not np.isscalar(dec):
            raise LensMCError('ID, RA, and DEC must be scalars.')
    elif type(id_) in (list, tuple, np.ndarray):
        if type(ra) not in (list, tuple, np.ndarray) or type(dec) not in (list, tuple, np.ndarray):
            raise LensMCError('ID, RA, and DEC must be array-like.')
        n_objects = len(id_)
        if len(ra) != n_objects or len(dec) != n_objects:
            raise LensMCError('ID, RA, and DEC must have the same length.')
        if len(set(id_)) < n_objects:
            raise LensMCError('Duplicate IDs found.')

    # check PSF
    if psf is not None:
        if not type(psf) in (list, tuple):
            psf = [deepcopy(psf) for _ in range(n_objects)]
        for p in psf:
            if not isinstance(p, PSF):
                raise LensMCError('PSF must be a PSF instance or a list of PSF instances.')
        if n_objects > 1:
            for ii in range(1, n_objects):
                if psf[ii].oversampling != psf[0].oversampling:
                    raise LensMCError('PSFs must have the same oversampling factor.')
                if psf[ii].dtype != psf[0].dtype:
                    raise LensMCError('PSFs must be of the same data type.')
    elif psf_disc is not None and psf_bulge is not None:
        if not type(psf_disc) in (list, tuple):
            psf_disc = [deepcopy(psf_disc) for _ in range(n_objects)]
        for p in psf_disc:
            if not isinstance(p, PSF):
                raise LensMCError('Disc PSF must be a PSF instance or a list of PSF instances.')
        if not type(psf_bulge) in (list, tuple):
            psf_bulge = [deepcopy(psf_bulge) for _ in range(n_objects)]
        for p in psf_bulge:
            if not isinstance(p, PSF):
                raise LensMCError('Bulge PSF must be a PSF instance or a list of PSF instances.')
        if psf_disc[0].oversampling != psf_bulge[0].oversampling:
            raise LensMCError('Disc and bulge PSFs must have the same oversampling factor.')
        if psf_disc[0].dtype != psf_bulge[0].dtype:
            raise LensMCError('Disc and bulge PSFs must be of the same data type.')
        if n_objects > 1:
            for ii in range(1, n_objects):
                if psf_disc[ii].oversampling != psf_disc[0].oversampling:
                    raise LensMCError('Disc PSFs must have the same oversampling factor.')
                if psf_disc[ii].dtype != psf_disc[0].dtype:
                    raise LensMCError('Disc PSFs must be of the same data type.')
                if psf_bulge[ii].oversampling != psf_disc[0].oversampling:
                    raise LensMCError('Disc PSFs must have the same oversampling factor.')
                if psf_bulge[ii].dtype != psf_disc[0].dtype:
                    raise LensMCError('Disc PSFs must be of the same data type.')
    else:
        raise LensMCError('Please check PSF.')
    oversampling = psf[0].oversampling if psf is not None else psf_disc[0].oversampling

    # check if we have the working arrays preallocated
    if working_arrays is not None:
        logger.debug('Check working arrays.')
        if working_arrays.oversampling != oversampling:
            raise Exception('Working arrays oversampling factor does not match with PSF.')
    else:
        logger.debug('Allocate working arrays.')
        working_arrays = alloc_working_arrays(n_bulge, n_disc, oversampling=oversampling, cache_file=cache_file,
                                              dtype=dtype, fftw_flags=fftw_flags)
    odim = working_arrays.odim

    # extract a square postage stamp from image of a given size around nominal position
    # if fitting multiple objects, take the centroid
    logger.debug('Extract postage stamp.')
    image, removed_exps = image.extract_postage_stamp(np.mean(ra), np.mean(dec), dim=postage_stamp,
                                                      x_buffer=x_buffer, y_buffer=y_buffer,
                                                      return_removed_exposures=True)

    # define trivial PSFs if not provided, and compute FTs
    logger.debug('Process PSF.')
    if psf is not None:
        psf_bulge = [None] * n_objects
        psf_disc = [None] * n_objects
        for ii in range(n_objects):
            psf[ii].drop_exposures(removed_exps)
            if psf[ii].n_exp != image.n_exp:
                raise LensMCError('Number of exposures for PSF and image must match.')
            psf[ii].calculate_ft(odim=odim, oversampling=oversampling, dtype=dtype, fftw_flags=fftw_flags)
            psf_bulge[ii] = deepcopy(psf[ii])
            psf_disc[ii] = deepcopy(psf[ii])
    elif psf_bulge is not None and psf_disc is not None:
        for ii in range(n_objects):
            psf_bulge[ii].drop_exposures(removed_exps)
            psf_disc[ii].drop_exposures(removed_exps)
            if psf_bulge[ii].n_exp != psf_disc[ii].n_exp or psf_bulge[ii].n_exp != image.n_exp:
                raise LensMCError('Number of exposures for bulge/disc PSF and image must match.')
            psf_bulge[ii].calculate_ft(odim=odim, oversampling=oversampling, dtype=dtype, fftw_flags=fftw_flags)
            psf_disc[ii].calculate_ft(odim=odim, oversampling=oversampling, dtype=dtype, fftw_flags=fftw_flags)
    else:
        odim_max = max(odim)
        psf = np.zeros((odim_max, odim_max), dtype=dtype)
        psf[odim_max // 2, odim_max // 2] = 1.
        psf = PSF([psf] * image.n_exp)
        psf.calculate_ft(odim=odim, oversampling=oversampling, dtype=dtype, fftw_flags=fftw_flags)
        psf_bulge = psf_disc = psf
        psf_bulge = [psf_bulge]
        psf_disc = [psf_disc]

    # make segmentation map if not provided and auto-segmentation is requested
    if image.seg is None:
        logger.debug('Make segmentation map.')
        image.make_segmentation(id_, ra, dec)

    # dilate the mask by one pixel if required
    if dilate_mask:
        logger.debug('Dilate mask.')
        image.dilate_mask()

    # dilate the mask by one pixel if required
    if dilate_segmentation:
        logger.debug('Dilate segmentation map.')
        image.dilate_segmentation()

    # check if object is still valid, i.e. it hasn't been masked out after dilating and merging
    logger.debug('Verify mask.')
    bad_exposures = image.verify_mask(id_, ra, dec)

    # drop bad exposures
    if bad_exposures:
        logger.debug('Drop bad image exposures.')
        image.drop_exposures(bad_exposures)
        if image.n_exp == 0:
            raise LensMCError('Left no exposures. Please check object IDs, maps, or masks.')
        logger.debug('Drop corresponding PSF exposures.')
        if psf is not None:
            [p.drop_exposures(bad_exposures) for p in psf]
        elif psf_bulge is not None and psf_disc is not None:
            [p.drop_exposures(bad_exposures) for p in psf_bulge]
            [p.drop_exposures(bad_exposures) for p in psf_disc]

    # check consistency of segmentation
    # then merge mask with segmentation map:
    # - make a new mask that combines the original mask with segmentation
    # - mask out any other object or spurious detections
    # i.e. keep only those pixels that are either associated to an object ID or noise
    logger.debug('Merge mask with segmentation map.')
    image.merge_mask_with_segmentation(id_, ra, dec, seg_id=seg_id)

    # sigma clipping for unmasked bad pixel rejection
    image.sigma_clip()

    # DC estimation
    if image.dc is None:
        logger.debug('Estimate DC.')
        image.estimate_dc()

    # DC subtraction (after masking out)
    logger.debug('Subtract DC.')
    image.subtract_dc()

    # RMS estimation (after masking out)
    if image.rms is None:
        logger.debug('Estimate RMS.')
        image.estimate_rms()

    # convert to normalised count rate
    if image.exposure_time is not None and image.gain is not None and image.zero_point is not None:
        image.to_normalised_count_rate()

    # work out inverse-variance weights for likelihood, given mask and segmentation
    logger.debug('Define weight map.')
    image.set_weight()

    # fit in celestial coordinates
    # user must have supplied the WCSs in the image class
    logger.debug('Get astrometry.')
    astrometry = [image.get_astrometry(ra[ii], dec[ii]) for ii in range(n_objects)]

    # initial guess
    # common for all exposures
    logger.debug('Define starting parameters.')
    e1 = np.atleast_1d(e1)
    e2 = np.atleast_1d(e2)
    re = np.atleast_1d(re)
    delta_ra = np.atleast_1d(delta_ra)
    delta_dec = np.atleast_1d(delta_dec)
    if e1.size == 1 and n_objects > 1:
        e1 = np.repeat(e1, n_objects)
    if e2.size == 1 and n_objects > 1:
        e2 = np.repeat(e2, n_objects)
    if re.size == 1 and n_objects > 1:
        re = np.repeat(re, n_objects)
    if delta_ra.size == 1 and n_objects > 1:
        delta_ra = np.repeat(delta_ra, n_objects)
    if delta_dec.size == 1 and n_objects > 1:
        delta_dec = np.repeat(delta_dec, n_objects)
    x = []
    for ii in range(n_objects):
        x += [e1[ii], e2[ii], re[ii], delta_ra[ii], delta_dec[ii]]
        if n_objects > 1:
            x += [0., 0.]

    # define galaxy model functions
    logger.debug('Define galaxy models.')
    bulge_model_fcns, disc_model_fcns, model_fcns = define_model_functions(working_arrays, disc_only, hl_to_exp, image,
                                                                           psf_bulge, psf_disc, astrometry)

    # define total model
    # sum over objects
    if n_objects == 1:
        model_fcn = model_fcns[0]
    else:
        def fcn(x):
            return model_joint(x, bulge_model_fcns, disc_model_fcns, postage_stamp, return_models=False)
        model_fcn = deepcopy(fcn)

    # define likelihood function
    logger.debug('Define galaxy likelihood.')
    log_likl_fcn, chi2_fcn, log_likl_const = define_likelihood_function(bulge_model_fcns, disc_model_fcns, image,
                                                                        return_log_likl_const=True)
    # log-prior function
    logger.debug('Define hard-bound prior.')
    if n_objects == 1:
        def log_prior_fcn(x):
            return log_prior_unif(x, emax=e_max, smax=re_max, deltamax=delta_max)
    else:
        # for joint fitting of multiple objects workout deltamax per object
        # that's to avoid swapping the role of the two objects in the fit if the position offsets start diverging
        delta_max_per_obj = [None] * n_objects
        pi_180 = np.pi / 180
        ra_rad, dec_rad = ra * pi_180, dec * pi_180
        for ii in range(n_objects):
            d = angular_separation(ra_rad[ii], dec_rad[ii], np.delete(ra_rad, ii), np.delete(dec_rad, ii))
            d *= 3600 / pi_180
            delta_max_per_obj[ii] = min(delta_max, 0.5 * np.min(d))

        def log_prior_fcn(x):
            l = 0
            for ii in range(n_objects):
                ix0 = 7 * ii
                ix1 = ix0 + 5
                if x[ix1] < 0 or x[ix1 + 1] < 0:
                    return -np.inf
                l += log_prior_unif(x[ix0: ix1], emax=e_max, smax=re_max, deltamax=delta_max_per_obj[ii])
            return l

    # override options to default to fast mode
    if mode == 'fast':
        maximisation = True
        sampling = False

    # define wrapper functions for likelihood and prior so we can first fit for position offsets and fluxes
    if n_objects > 1:

        # set the free parameters in the fit
        ix_fit = np.tile(np.array([0, 0, 0, 1, 1, 1, 1], dtype=bool), n_objects)

        def log_likl_wrap_fcn(image, xx, x0=x):

            x1 = np.copy(x0)
            x1[ix_fit] = xx
            return log_likl_fcn(image, x1)

        def log_prior_wrap_fcn(xx, x0=x):

            x1 = np.copy(x0)
            x1[ix_fit] = xx
            return log_prior_fcn(x1)

        # define new initial guess for those free parameters
        xx = [x[ii] for ii in range(len(x)) if ix_fit[ii]]

        # run core LensMC maximisation/sampling function
        logger.debug('Sample joint posterior for position offsets and fluxes.')
        results = sampler(image.exp, log_likl_wrap_fcn, xx,
                          log_prior_fcn=log_prior_wrap_fcn,
                          maximisation=True, sampling=False,
                          n_burnin=n_burnin, n_samples=n_samples, n_chains=n_chains, n_swap=n_swap,
                          affine_invariant=affine_invariant,
                          n_ai_samples=n_ai_samples, n_ai_burnin=n_ai_burnin, n_ai_chains=n_ai_chains,
                          seed=seed,
                          intcal=False)

        # set estimates to original initial guess
        x = np.array(x)
        x[ix_fit] = results.x
        x = x.tolist()

    # run core LensMC maximisation/sampling function
    logger.debug('Sample galaxy posterior.')
    results = sampler(image.exp, log_likl_fcn, x,
                      log_prior_fcn=log_prior_fcn,
                      maximisation=maximisation, sampling=sampling,
                      n_burnin=n_burnin, n_samples=n_samples, n_chains=n_chains, n_swap=n_swap,
                      affine_invariant=affine_invariant,
                      n_ai_samples=n_ai_samples, n_ai_burnin=n_ai_burnin, n_ai_chains=n_ai_chains,
                      seed=seed,
                      intcal=intcal, model_fcn=model_fcn)

    # set flag
    flag = flag_galaxy

    # take care of possible failures and report no results
    if results.x is None:
        results.flag += flag_failure
        return LensMCResults()

    # test goodness of fit
    logger.debug('Test goodness of fit.')
    chi2, dof, chi2_bkg, dof_bkg = goodness_of_fit(image, results.x_max, chi2_fcn, test_background=True)

    # do an F test between chi2 with model and chi2 without model
    # (assuming perfect masking, if at least a segmentation map has been provided)
    # H0: variance after the fit is consistent with the background variance after masking object
    # H1: variance is significantly greater otherwise
    if dof_bkg < 0:
        flag += flag_bad_residuals
        pvalue_bkg = np.nan
    else:
        F = (chi2 / dof) / (chi2_bkg / dof_bkg)
        pvalue_bkg = f.sf(F, dof, dof_bkg)
        if pvalue_bkg < significance:
            flag += flag_bad_residuals

    # calibration
    if cal:

        logger.debug('M-calibration.')

        # define 4 shear values on a circle
        # with modulus capped to 0.05
        gmod = 0.01
        g1 = [gmod, 0, -gmod, 0]
        g2 = [0, gmod, 0, -gmod]

        # define centre of shearing (for multiple objects)
        ra0, dec0 = ra.mean(), dec.mean()

        # loop over shears
        ng = len(g1)
        e1_sheared = np.zeros((ng, n_objects))
        e2_sheared = np.zeros((ng, n_objects))
        for ii in range(ng):

            # make (sheared) image proxies
            image_proxy = image.shear(g1[ii], g2[ii], ra0, dec0)

            # define likelihood function
            log_likl_aux_fcn, _ = define_likelihood_function(bulge_model_fcns, disc_model_fcns, image_proxy)

            # define auxiliary posterior
            log_post_aux_fcn = lambda x: log_likl_fcn(image_proxy.exp, x) + log_prior_fcn(x)

            # run importance sampling
            likl_ratio, ess, has_succedeed = importance_sampling(results.x_samples, results.logp_samples,
                                                                 log_post_aux_fcn)

            # derive autocal estimator
            if has_succedeed and ess > n_samples / 2:
                x_sheared = np.average(results.x_samples, axis=0, weights=likl_ratio)
                e1_sheared[ii] = x_sheared[0] if n_objects == 1 else x_sheared[0::7]
                e2_sheared[ii] = x_sheared[1] if n_objects == 1 else x_sheared[1::7]

        # measure responses
        m1 = 0.5 * (e1_sheared[0] - e1_sheared[2]) / gmod
        m2 = 0.5 * (e2_sheared[1] - e2_sheared[3]) / gmod
        m12 = 0.5 * (e1_sheared[1] - e1_sheared[3]) / gmod
        m21 = 0.5 * (e2_sheared[0] - e2_sheared[2]) / gmod
        n = 5 if n_objects == 1 else 7
        c1 = 0.5 * (e1_sheared[0] + e1_sheared[2]) - results.x[::n]
        c2 = 0.5 * (e2_sheared[1] + e2_sheared[3]) - results.x[1::n]

    logger.debug('Calculate extra parameters.')

    # define function to get snr, flux, and B/T
    def get_extra_params(model_fcns, x):
        snr = np.zeros((n_objects, ))
        flux = np.zeros((n_objects, ))
        for oo, model_fcn in enumerate(model_fcns):
            if n_objects == 1:
                model, a0 = model_fcn(x, return_coeff=True)[:2]
            else:
                model = model_fcn(x)
            for ii in range(image.n_exp):
                snr[oo] += np.sum(model[ii] * model[ii] * image.weight[ii])
                if n_objects:
                    flux[oo] += np.sum(model[ii]) / image.n_exp
        snr = np.sqrt(snr)
        if n_objects == 1:
            if not disc_only:
                flux_bulge = a0
                flux_disc = flux - a0
            else:
                flux_bulge = 0
                flux_disc = a0
        else:
            flux_bulge = x[5::7]
            flux_disc = x[6::7]
            flux[:] = flux_bulge + flux_disc
        return snr, flux, flux_bulge, flux_disc

    # extract chain values
    if sampling:
        x_samples = results.x_samples
    else:
        n_samples = 1
        x_samples = results.x.reshape((1, len(x)))

    # calculate snr, fluxes, and magnitude
    snr = np.empty((n_objects, n_samples))
    flux = np.empty((n_objects, n_samples))
    flux_bulge = np.empty((n_objects, n_samples))
    flux_disc = np.empty((n_objects, n_samples))
    snr[:, 0], flux[:, 0], flux_bulge[:, 0], flux_disc[:, 0] = get_extra_params(model_fcns, x_samples[0])
    for ii in range(1, n_samples):
        if not all(x_samples[ii] == x_samples[ii - 1]):
            snr[:, ii], flux[:, ii], flux_bulge[:, ii], flux_disc[:, ii] = get_extra_params(model_fcns, x_samples[ii])
        else:
            snr[:, ii], flux[:, ii], flux_bulge[:, ii], flux_disc[:, ii] = \
                snr[:, ii - 1], flux[:, ii - 1], flux_bulge[:, ii - 1], flux_disc[:, ii - 1]

    # make LensMC results object and set attributes
    lensmc_results = LensMCResults(results)
    if sampling:
        lensmc_results.set_weight(shape_noise, r_sg=r_sg)
    lensmc_results.set_ra_dec(ra, dec)
    lensmc_results.set_fluxes(snr, flux, flux_bulge, flux_disc, image.normalised_zero_point)
    lensmc_results.set_half_light_radius(flux, flux_bulge, flux_disc, hl_to_exp)
    lensmc_results.set_image_props(image)
    lensmc_results.set_other_props(id_, chi2 / dof, dof, pvalue_bkg, flag, seed)
    if cal:
        lensmc_results.set_cal_props(gmod, m1, m2, m12, m21, c1, c2)
    if return_model:
        lensmc_results.set_data(image)
        lensmc_results.set_model(model_fcn(lensmc_results._results.x))
        lensmc_results.set_residuals()
    lensmc_results.set_psf_metrics(psf_disc, astrometry)
    lensmc_results.set_distortion_matrix(astrometry)

    logger.debug('Exit measure_shear().')

    return lensmc_results


class LensMCResults:

    __slots__ = ('e1', 'e2', 're', 'ra', 'dec', 'e1_err', 'e2_err', 'e_var', 'w', 're_err', 'ra_err', 'dec_err',
                 'e1_ical', 'e2_ical', 'e1_max', 'e2_max', 'id_', 'chi2', 'dof', 'acc', 'n_eff', 'flag',
                 'e1_samples', 'e2_samples', 're_samples', 'ra_samples', 'dec_samples',
                 'g_cal', 'm1_cal', 'm2_cal', 'm12_cal', 'm21_cal', 'c1_cal', 'c2_cal',
                 'model', 'pvalue_bkg', 'snr', 'flux', 'flux_bulge', 'flux_disc', 'magnitude', 'bulgefrac',
                 'snr_err', 'bulgefrac_err', 'flux_err', 'flux_bulge_err', 'flux_disc_err', 'magnitude_err',
                 'snr_samples', 'flux_samples', 'flux_bulge_samples', 'flux_disc_samples', 'magnitude_samples',
                 'hlr', 'hlr_err',
                 'acc_samples', 'logp_samples', 'likl_ratio_samples', 'acc', 'flag',
                 'likl_calls_intcal', 'likl_calls_mcmc', 'likl_calls_optim', 'seed',
                 'psf_e1', 'psf_e2', 'psf_r2', 'psf_fwhm', 'distortion_matrix',
                 'n_exposures', 'bad_exposures', 'zero_point', 'model', 'data', 'residuals',
                 '_results', '_n', '_nx', '_no', '_has_samples', 'has_values')

    def __init__(self, results: Results = None):

        self.has_values = hasattr(results, 'x') and results.x is not None
        if not self.has_values:
            return

        self._results = results

        n = len(results.x)
        nx = 7 if n > 5 else 5
        self._n = n  # length of parameter array
        self._nx = nx  # number of parameters being fitted for each object
        self._no = self._n // self._nx  # number of objects
        self._has_samples = results.x_samples is not None

        self.e1 = results.x[0::nx]
        self.e2 = results.x[1::nx]
        self.re = results.x[2::nx]
        self.ra = results.x[3::nx] / 3600  # degree
        self.dec = results.x[4::nx] / 3600  # degree
        if results.dx is not None:
            self.e1_err = results.dx[0::nx]
            self.e2_err = results.dx[1::nx]
            self.e_var = 0.5 * (self.e1_err ** 2 + self.e2_err ** 2)
            self.re_err = results.dx[2::nx]  # arcsec
            self.ra_err = results.dx[3::nx] / 3600  # degree
            self.dec_err = results.dx[4::nx] / 3600  # degree
        if self._has_samples:
            results.x_samples[:, 3::self._nx] /= 3600  # arcsec
            results.x_samples[:, 4::self._nx] /= 3600  # arcsec
        if results.x_ical is not None:
            self.e1_ical = results.x_ical[0::nx]
            self.e2_ical = results.x_ical[1::nx]
        if results.x_max is not None:
            self.e1_max = results.x_max[0::nx]
            self.e2_max = results.x_max[1::nx]
        if self._has_samples:
            self.e1_samples = self._results.x_samples[:, 0::self._nx].T
            self.e2_samples = self._results.x_samples[:, 1::self._nx].T
            self.re_samples = self._results.x_samples[:, 2::self._nx].T
            self.ra_samples = self._results.x_samples[:, 3::self._nx].T
            self.dec_samples = self._results.x_samples[:, 4::self._nx].T
            self.acc_samples = self._results.acc_samples
            self.logp_samples = self._results.logp_samples
            self.likl_ratio_samples = self._results.likl_ratio_samples
            self.acc = self._results.acc
            self.n_eff = self._results.n_eff
        self.likl_calls_optim = self._results.likl_calls_optim
        self.likl_calls_mcmc = self._results.likl_calls_mcmc
        self.likl_calls_intcal = self._results.likl_calls_intcal

        self.id_ = None
        self.chi2 = None
        self.dof = None
        self.w = None
        self.e1_ical = None
        self.e2_ical = None
        self.g_cal = None
        self.m1_cal = None
        self.m2_cal = None
        self.model = None
        self.data = None
        self.residuals = None
        self.pvalue_bkg = None
        self.snr = None
        self.flux = None
        self.flux_bulge = None
        self.flux_disc = None
        self.magnitude = None
        self.bulgefrac = None
        self.snr_err = None
        self.bulgefrac_err = None
        self.flux_err = None
        self.flux_bulge_err = None
        self.flux_disc_err = None
        self.magnitude_err = None
        self.snr_samples = None
        self.flux_samples = None
        self.flux_bulge_samples = None
        self.flux_disc_samples = None
        self.magnitude_samples = None
        self.hlr = None
        self.hlr_err = None
        self.n_exposures = None
        self.bad_exposures = None
        self.zero_point = None
        self.model = None
        self.flag = None
        self.seed = None
        self.psf_e1 = None
        self.psf_e2 = None
        self.psf_r2 = None
        self.psf_fwhm = None
        self.distortion_matrix = None

        if self._no == 1:
            self.__flatten__()

    def set_weight(self, shape_noise, r_sg=None):

        if self.e_var is not None:
            self.w = 1. / (self.e_var + shape_noise ** 2)
            if r_sg is not None:
                self.w *= self.re > r_sg

    def set_ra_dec(self, ra, dec):

        self.ra += ra
        self.dec += dec
        if self._has_samples:
            if self._no == 1:
                self.ra_samples += ra
                self.dec_samples += dec
            else:
                for ii in range(self._no):
                    self.ra_samples[ii] += ra[ii]
                    self.dec_samples[ii] += dec[ii]

    def set_fluxes(self, snr, flux, flux_bulge, flux_disc, normalised_zero_point=None):
        """
        Method that calculates ancillary information about fluxes and set the derived estimates as attributes
        of the object.
        It computes the mean of the chains while excluding invalid numbers that may arise in the measurement.
        For instance, while a flux sample can be nominally zero, the calculation of the magnitude will be ill-defined.
        """
        mag = -2.5 * np.log10(flux, where=flux > 0, out=np.full_like(flux, -np.inf))
        if normalised_zero_point is not None:
            mag += np.full_like(flux, normalised_zero_point)
        self.snr = np.mean(snr, axis=1)
        self.flux = np.mean(flux, axis=1)
        self.flux_bulge = np.mean(flux_bulge, axis=1)
        self.flux_disc = np.mean(flux_disc, axis=1)
        # take care of NaN/infs in magnitude samples
        self.magnitude = np.full_like(self.flux, np.inf)
        self.magnitude_err = np.full_like(self.flux, np.nan)
        for ii in range(self._no):
            ix = np.isfinite(mag[ii])
            if np.any(ix):
                x = mag[ii][ix]
                self.magnitude[ii] = np.mean(x)
                self.magnitude_err[ii] = np.std(x)
        is_flux_positive = self.flux > 0
        self.bulgefrac = np.divide(self.flux_bulge, self.flux, where=is_flux_positive, out=np.full((self._no,), np.nan))
        if self._has_samples:
            self.snr_err = np.std(snr, axis=1)
            self.bulgefrac_err = np.sqrt(
                np.divide(np.var(flux_bulge, axis=1), self.flux ** 2, where=is_flux_positive,
                          out=np.full((self._no,), np.nan)) +
                np.var(flux, axis=1) * np.divide(self.bulgefrac ** 2, self.flux ** 4, where=is_flux_positive,
                                                 out=np.full(self._no, np.nan)))
            self.flux_err = np.std(flux, axis=1)
            self.flux_bulge_err = np.std(flux_bulge, axis=1)
            self.flux_disc_err = np.std(flux_disc, axis=1)
            self.snr_samples = snr if self._n > 1 else snr.ravel()
            self.flux_samples = flux if self._n > 1 else flux.ravel()
            self.flux_bulge_samples = flux_bulge if self._n > 1 else flux_bulge.ravel()
            self.flux_disc_samples = flux_disc if self._n > 1 else flux_disc.ravel()
            self.magnitude_samples = mag if self._n > 1 else mag.ravel()

        if self._no == 1:
            self.__flatten__()

    def set_half_light_radius(self, flux, flux_bulge, flux_disc, hl_to_exp):
        """
        Calculate a flux-weighted total half-light radius from the available Re and flux samples.
        1.1678 converts disc scale length to HLR.
        hl_to_exp converts disc scale length to bulge HLR.
        """
        if self._has_samples:
            hlr = self.re_samples * np.divide(flux_disc * 1.678 + flux_bulge * hl_to_exp, flux,
                                              where=flux > 0, out=np.zeros_like(flux))
            self.hlr = np.mean(hlr, axis=1)
            self.hlr_err = np.std(hlr, axis=1)

        if self._no == 1:
            self.__flatten__()

    def set_image_props(self, image):

        self.n_exposures = image.n_exp
        self.bad_exposures = image.bad_exp
        self.zero_point = image.normalised_zero_point

    def set_other_props(self, id_, chi2, dof, pvalue_bkg, flag, seed):

        self.id_ = id_
        self.chi2 = chi2
        self.dof = dof
        self.pvalue_bkg = pvalue_bkg
        self.flag = flag
        self.seed = seed

        if self._no == 1:
            self.__flatten__()

    def set_cal_props(self, gmod, m1, m2, m12, m21, c1, c2):

        self.g_cal = gmod
        self.m1_cal = m1
        self.m2_cal = m2
        self.m12_cal = m12
        self.m21_cal = m21
        self.c1_cal = c1
        self.c2_cal = c2

    def set_data(self, data):

        if not isinstance(data, Image):
            data = Image(data)
        self.data = data

    def set_model(self, model):

        if not isinstance(model, Image):
            model = Image(model, wcs=self.data.wcs if self.data is not None else None)
        self.model = model

    def set_residuals(self):

        if self.data is None or self.model is None:
            raise Exception('Can only calculate residuals if both data and model have been set.')
        self.residuals = Image([self.data[ii] - self.model[ii] for ii in range(self.data.n_exp)],
                               wcs=self.data.wcs if self.data is not None else None)

    def __flatten__(self):

        for attr in self.__slots__:
            if hasattr(self, attr):
                val = self.__getattribute__(attr)
                if isinstance(val, np.ndarray):
                    if val.size == 1:
                        self.__setattr__(attr, val.item())
                    elif val.ndim == 2 and val.shape[0] == 1:
                        self.__setattr__(attr, val.ravel())
                elif isinstance(val, list) and len(val) == 1:
                    self.__setattr__(attr, val[0])

    def set_psf_metrics(self, psf, astrometry, sigma=2.5):

        n_objects = len(psf)
        n_exposures = psf[0].n_exp

        # loop over objects
        e1_w, e2_w, r2_w, fwhm_w = np.empty((4, n_objects, n_exposures))
        for ii in range(n_objects):
            # get measurements
            e1, e2, r2, *_ = psf[ii].get_moments(sigma=sigma)
            # get astrometry
            A = astrometry[ii].distortion_matrix
            pixel_scale = astrometry[ii].pixel_scale
            # loop over exposures
            for jj in range(len(e1)):
                # transform to world coordinates
                e = np.array([[1 + e1[jj], e2[jj]], [e2[jj], 1 - e1[jj]]])
                e = A[jj] @ e @ A[jj].T
                tr = e[0, 0] + e[1, 1]
                e1[jj] = (e[0, 0] - e[1, 1]) / tr
                e2[jj] = 2 * e[0, 1] / tr
            # take mean over exposures
            e1_w[ii] = e1
            e2_w[ii] = e2
            r2_w[ii] = r2 * pixel_scale ** 2
            fwhm_w[ii] = psf[ii].get_fwhm() * pixel_scale

        self.psf_e1 = e1_w
        self.psf_e2 = e2_w
        self.psf_r2 = r2_w
        self.psf_fwhm = fwhm_w

        if self._no == 1:
            self.__flatten__()

    def set_distortion_matrix(self, astrometry):

        distortion_matrix = np.array([a.distortion_matrix for a in astrometry])

        # flatten twice until we get a numpy object
        # there shouldn't be any worry about the shape as it's always (n_obj x n_exp x 2 x 2)
        # so we're flattening along the first two axes and n_obj and n_exp are known in advance
        if distortion_matrix.shape[1] == 1:
            distortion_matrix = np.squeeze(distortion_matrix, axis=1)
        if distortion_matrix.shape[0] == 1:
            distortion_matrix = np.squeeze(distortion_matrix, axis=0)
        self.distortion_matrix = distortion_matrix


def define_model_functions(working_arrays, disc_only, hl_to_exp, image, psf_bulge, psf_disc, astrometry,
                           fixed_astrometry=False):

    # Hankel resample model only for the first exposure
    # we'll reuse this for all other exposures
    # this saves ~2X computational time, but assumes the astrometric distortion is fixed across exposures
    do_hankel_resample = np.zeros((image.n_exp, ), dtype=bool)
    do_hankel_resample[0] = 1
    if not fixed_astrometry:
        do_hankel_resample[1:] = 1

    # choose model array size only for first exposure
    # allowing full freedom for all exposures complicates the analysis
    # that also leads to overflows in the Cython implementation of cross product
    # which assumes all model arrays have the same size
    do_choose_model_size = np.zeros((image.n_exp, ), dtype=bool)
    do_choose_model_size[0] = 1

    # extract working arrays
    bulge_ht = working_arrays.bulge_ht
    disc_ht = working_arrays.disc_ht

    # define galaxy model functions for every object and exposure
    o = len(astrometry)
    bulge_model_fcn = [None] * o
    disc_model_fcn = [None] * o
    model_fcn = [None] * o
    for oo in range(o):

        bulge_model_fcn[oo] = [None] * image.n_exp
        disc_model_fcn[oo] = [None] * image.n_exp

        for ii in range(image.n_exp):

            # bulge model
            # note that the templates already contain the correct size definition (Peng relation)
            if not disc_only:
                def fcn(x, psf_bulge_ft=psf_bulge[oo].ft[ii],
                        astrometric_distortion=astrometry[oo].distortion_matrix[ii],
                        pixel_scale=astrometry[oo].pixel_scale[ii],
                        x_offset=astrometry[oo].x_offset[ii],
                        y_offset=astrometry[oo].y_offset[ii],
                        do_hankel_resample=do_hankel_resample[ii], do_choose_model_size=do_choose_model_size[ii]):
                    return generate_galaxy_model(x[0], x[1], hl_to_exp * x[2], x[3], x[4],
                                                 bulge_ht, psf_bulge_ft, working_arrays,
                                                 astrometric_distortion=astrometric_distortion,
                                                 x_offset=x_offset, y_offset=y_offset,
                                                 pixel_scale=pixel_scale,
                                                 do_hankel_resample=do_hankel_resample,
                                                 do_choose_model_size=do_choose_model_size)
                bulge_model_fcn[oo][ii] = deepcopy(fcn)

            # disc model
            def fcn(x, psf_disc_ft=psf_disc[oo].ft[ii],
                    astrometric_distortion=astrometry[oo].distortion_matrix[ii],
                    pixel_scale=astrometry[oo].pixel_scale[ii],
                    x_offset=astrometry[oo].x_offset[ii],
                    y_offset=astrometry[oo].y_offset[ii],
                    do_hankel_resample=do_hankel_resample[ii], do_choose_model_size=do_choose_model_size[ii]):
                return generate_galaxy_model(x[0], x[1], x[2], x[3], x[4],
                                             disc_ht, psf_disc_ft, working_arrays,
                                             astrometric_distortion=astrometric_distortion,
                                             x_offset=x_offset, y_offset=y_offset,
                                             pixel_scale=pixel_scale,
                                             do_hankel_resample=do_hankel_resample,
                                             do_choose_model_size=do_choose_model_size)
            disc_model_fcn[oo][ii] = deepcopy(fcn)

        # bulge+disc model marginalised over linear parameters
        if o == 1:
            if not disc_only:
                def fcn(x, return_coeff=False):
                    return marginal_model(x, bulge_model_fcn[oo], disc_model_fcn[oo], image.exp, image.weight,
                                          return_coeff=return_coeff)
            else:
                def fcn(x, return_coeff=False):
                    return marginal_model_1component(x, disc_model_fcn[oo], image.exp, image.weight,
                                                     return_coeff=return_coeff)
        else:

            def fcn(x, oo=oo):
                _ = model_joint(x, bulge_model_fcn, disc_model_fcn, image[0].shape[0], return_models=True)
                return _[1][oo]

        model_fcn[oo] = deepcopy(fcn)

    return bulge_model_fcn, disc_model_fcn, model_fcn


def define_likelihood_function(bulge_model_fcn, disc_model_fcn, image,
                               single_component=False, return_log_likl_const=False):

    # log-likelihood offset (required for proper normalisation)
    log_likl_const = 0.
    for ii in range(image.n_exp):
        log_likl_const += -.5 * np.sum(image[ii] * image[ii] * image.weight[ii])

    # number of objects
    # determine if joint fitting or not
    n = len(disc_model_fcn)

    # log-likelihood function
    if not single_component:
        if n == 1:
            def log_likl_fcn(data, x, weight=image.weight, log_likl_const=log_likl_const):
                return log_likl(data, x, bulge_model_fcn[0], disc_model_fcn[0], weight, log_likl_const)
        else:
            def log_likl_fcn(data, x, weight=image.weight, **kwargs):
                return log_likl_joint(data, x, bulge_model_fcn, disc_model_fcn, weight)
    else:
        if n == 1:
            def log_likl_fcn(data, x, weight=image.weight, log_likl_const=log_likl_const):
                return log_likl_1component(data, x, disc_model_fcn[0], weight, log_likl_const)
        else:
            raise LensMCError('Single component not implemented with joint fitting.')

    # chi2 function
    def chi2_fcn(data, x, weight=image.weight, log_likl_const=log_likl_const):
        return -2. * log_likl_fcn(data, x, weight=weight, log_likl_const=log_likl_const)

    if return_log_likl_const:
        return log_likl_fcn, chi2_fcn, log_likl_const
    else:
        return log_likl_fcn, chi2_fcn


def goodness_of_fit(image, x, chi2_fcn, test_background=True):

    # first measure the fit chi2
    chi2 = chi2_fcn(image.exp, x)
    dof = 0
    for ii in range(image.n_exp):
        dof += np.sum(image.weight[ii] > 0)
    dof -= len(x)

    # now let's measure the background chi2, excluding the object
    if test_background:

        # make sure background mask is defined
        if image.bkg_mask is None:
            image.set_background_mask()

        # re-estimate likelihood weights and normalisation, excluding the object (via background mask)
        logl_likl_const_new = 0.
        weight_new = [0] * image.n_exp
        for ii in range(image.n_exp):
            weight_new[ii] = image.weight[ii] * image.bkg_mask[ii]
            logl_likl_const_new += -.5 * np.sum(image[ii] * image[ii] * weight_new[ii])

        # calculate baseline chi2 excluding the identified object
        chi2_bkg = chi2_fcn(image.exp, x, weight=weight_new, log_likl_const=logl_likl_const_new)
        dof_bkg = 0
        for ii in range(image.n_exp):
            dof_bkg += np.sum(weight_new[ii] > 0)
        dof_bkg -= len(x)

        return chi2, dof, chi2_bkg, dof_bkg
    else:
        return chi2, dof


def test_for_contaminated_image(image, model_fcn, x, weights, n_exposures, sigmas=3):

    assert n_exposures >= 3

    # calculate overlap between model and data for every images
    overlap = np.empty((n_exposures,))
    sigma_overlap = np.empty((n_exposures,))
    var_overlap = np.empty((n_exposures,))
    _ = model_fcn(x)
    for ii in range(n_exposures):
        # compute overlap = (m|d) / (m|m)
        _weights = _[ii] * weights[ii]
        snr2 = np.sum(_[ii] * _weights)
        overlap[ii] = np.sum(image[ii] * _weights) / snr2
        sigma_overlap[ii] = 1. / np.sqrt(snr2)
        # var_overlap[ii] = np.sum(_[ii])
        var_overlap[ii] = np.sum(_[ii] ** 2) / snr2 ** 2

    # take the maximum
    max = np.max(overlap)
    ix = np.argmax(overlap)

    # take the mean and std of the remaining samples
    mask = np.ones((n_exposures, ), dtype=bool)
    mask[ix] = 0
    overlap_masked = overlap[mask]
    mean = np.mean(overlap_masked)
    std = np.std(overlap_masked)

    # # 2nd version
    # mean = np.mean(overlap)
    # std = np.std(overlap)
    #
    # # 3rd version
    # w = 1. / sigma_overlap ** 2
    # mean = np.average(overlap, weights=w)
    # std = np.sqrt(np.average((overlap - mean) ** 2, weights=w))

    # # 4th version
    # std = np.sqrt(np.sum(sigma_overlap[mask] * 2) / (n_exposures - 1))
    # cdf_value = np.empty((n_exposures,))
    # for ii in range(n_exposures):
    #     cdf_value[ii] = norm.cdf(max, loc=1, scale=np.sqrt(var_overlap[ii]))
    # p_value_max = 1 - np.prod(cdf_value)
    #
    # # # 5th version
    # std = np.std(overlap_masked)
    # p_value_max = norm.sf(max, loc=1, scale=std)

    # test statistic
    # H0: the image with the maximum model overlap is consistent with the sample distribution
    # H1: the image with the maximum model overlap is not consistent with the sample distribution
    t = np.abs(max - mean) / std
    # t = np.abs(max - 1) / sigma_overlap[ix]
    if t > sigmas:
    # if p_value_max < 0.01:
        # test does pass and H0 is rejected
        test_result, image_index = True, ix
    else:
        # test doesn't pass and H0 is not rejected
        test_result, image_index = False, None

    return test_result, image_index
