"""
LensMC - a Python package for weak lensing shear measurements.
Workhorse module of the LensMC package used for the shear measurement.

Copyright 2015 Giuseppe Congedo
"""

import multiprocessing as mp
import numpy as np
import tempfile
from collections.abc import Callable
from traceback import format_tb
from typing import Any, List, Tuple, Type, TypeVar, Union

from lensmc import measure_shear
from lensmc.flags import flag_failure
# noinspection PyUnresolvedReferences
from lensmc.galaxy_model import alloc_working_arrays
from lensmc.image import Image
from lensmc.psf import PSF
from lensmc.utils import friend_of_friend_neighbour, LensMCError, logger


# generic array like data type
T = TypeVar('T')
ArrayLike = Union[T, List[T], np.ndarray]

# catalogue data types
det_cat_dtype = [('id', np.uint), ('ra', float), ('dec', float)]  # optionally also ('seg_id', np.uint)
meas_cat_dtype = [('id', np.uint), ('group', np.uint), ('e1', np.float32), ('e2', np.float32), ('re', np.float32),
                  ('ra', float), ('dec', float), ('flux', np.float32), ('flux_bulge', np.float32), ('flux_disc', np.float32),
                  ('bulgefrac', np.float32), ('snr', np.float32),
                  ('mag', np.float32), ('zp', np.float32), ('hlr', np.float32),
                  ('chi2', np.float32), ('dof', np.uint32),
                  ('flag', np.uint32), ('e1_err', np.float32), ('e2_err', np.float32), ('e_var', np.float32),
                  ('w', np.float32), ('re_err', np.float32), ('ra_err', np.float64), ('dec_err', np.float64),
                  ('flux_err', np.float32), ('flux_bulge_err', np.float32), ('flux_disc_err', np.float32),
                  ('bulgefrac_err', np.float32), ('snr_err', np.float32),
                  ('mag_err', np.float32), ('hlr_err', np.float32), ('acc', np.float32),
                  ('psf_e1', np.float32), ('psf_e2', np.float32), ('psf_r2', np.float32), ('psf_fwhm', np.float32),
                  ('distortion_matrix', (np.float32, (2, 2))),
                  ('pvalue_bkg', np.float32), ('likl_calls_optim', np.uint32), ('likl_calls_mcmc', np.uint32)]
DetCatType = np.ndarray[Any, det_cat_dtype]
MeasCatType = np.ndarray[Any, meas_cat_dtype]

# column descritions
column_descriptions = {'id': 'Object ID.',
                       'group': 'Group ID the object belongs to.',
                       'e1': 'First component of ellipticity in (-RA, DEC) world coordinates. ' \
                             'Defined on the tangent plane at the object position.',
                       'e2': 'Second component of ellipticity in (-RA, DEC) world coordinates. ' \
                             'Defined on the tangent plane at the object position.',
                       're': 'Exponential scale length of the disc (arcsec).',
                       'ra': 'Right ascension (degree).',
                       'dec': 'Declination (degree).',
                       'flux': 'Total flux in top-of-the-telescope counts per second.',
                       'flux_bulge': 'Bulge flux in top-of-the-telescope counts per second.',
                       'flux_disc': 'Disc flux in top-of-the-telescope counts per second.',
                       'bulgefrac': 'Bulge to total flux fraction.',
                       'snr': 'Signal-to-noise ratio.',
                       'mag': 'Magnitude.',
                       'zp': 'Magnitude zero-point.',
                       'hlr': 'Total flux-averaged half-light radius (arcsec).',
                       'chi2': 'Reduced chi-squared at the mean value.',
                       'dof': 'Number of degrees of freedom.',
                       'flag': 'Success flag (0 meaning good,' \
                               'see https://gitlab.com/lensmc/LensMC/-/blob/main/lensmc/flags.py ).',
                       'e1_err': '1-sigma statistical error on e1.',
                       'e2_err': '1-sigma statistical error on e2.',
                       'e_var': 'Per-component ellipticity variance.',
                       'w': 'Shear weight.',
                       're_err': '1-sigma statistical error on re.',
                       'ra_err': '1-sigma statistical error on ra.',
                       'dec_err': '1-sigma statistical error on dec.',
                       'flux_err': '1-sigma statistical error on flux.',
                       'flux_bulge_err': '1-sigma statistical error on flux_bulge.',
                       'flux_disc_err': '1-sigma statistical error on flux_disc.',
                       'bulgefrac_err': '1-sigma statistical error on bulgefrac.',
                       'snr_err': '1-sigma statistical error on snr.',
                       'mag_err': '1-sigma statistical error on mag.',
                       'hlr_err': '1-sigma statistical error on hlr.',
                       'acc': 'MCMC acceptance rate.',
                       'psf_e1': 'Moments-based first component of PSF ellipticity.',
                       'psf_e2': 'Moments-based second component of PSF ellipticity.',
                       'psf_r2': 'Moments-based R2 PSF size (arcsec^2).',
                       'psf_fwhm': 'PSF full width at half maximum (arcsec).',
                       'distortion_matrix': 'Astrometric distortion matrix at the object position (arcsec/pixel).',
                       'pvalue_bkg': 'P-value of good background.',
                       'likl_calls_optim': 'Number of likelihood evaluations in the optimisation.',
                       'likl_calls_mcmc': 'Number of likelihood evaluations in the MCMC.'}


def measure_shear_all(image: Image, cat: DetCatType, psf: Union[PSF, List[PSF], Callable[[float, float], PSF]],
                      e1: float = 0., e2: float = 0., re: float = 0.3, delta_ra: float = 0., delta_dec: float = 0.,
                      postage_stamp: int = 512, x_buffer: int = 3, y_buffer: int = 3,
                      dilate_mask: bool = True, dilate_segmentation: bool = True,
                      hl_to_exp: float = 0.15, n_bulge: float = 1., n_disc: float = 1.,
                      e_max: float = 0.99, re_max: float = 2., delta_max: float = 0.3,
                      disc_only: bool = False,
                      intcal: bool = True, cal: bool = False,
                      return_model: bool = False,
                      significance: float = 0.01,
                      maximisation: bool = True, sampling: bool = True,
                      mode: str = None,
                      n_samples: int = 200, n_burnin: int = 500,
                      seed: int = None, fftw_flags: Tuple = ('FFTW_MEASURE',),
                      shape_noise: float = 0.3, r_sg: float = 0.15,
                      copy: bool = True, dtype: Type = np.float32,
                      log_level: str = 'info',
                      r_friend: float = 1,
                      processes: int = None, traceback: bool = False) -> MeasCatType:

    # check detection catalogue
    if cat.size == 0:
        raise LensMCError('Detection catalogue can not have zero size.')
    if not set([t[0] for t in det_cat_dtype]).issubset(set(cat.dtype.names)):
        raise LensMCError(f'Detection catalogue should be of type: {det_cat_dtype}.')

    # check PSFs
    if isinstance(psf, PSF):
        psf = [psf] * cat.size
    elif isinstance(psf, list):
        if len(psf) != cat.size:
            raise LensMCError('PSF must be a list of PSF objects of the same size of the detection catalogue.')
        for p in psf:
            if not isinstance(p, PSF):
                raise LensMCError('PSF must be a list of PSF objects.')
    elif callable(psf):
        psf_ = psf(cat[0]['ra'], cat[0]['dec'])
    else:
        raise LensMCError('PSF must be a PSF object, list of PSF objects, or a callable(RA, DEC)-> PSF.')

    if not callable(psf) and len(psf) > 1 and len(psf) != cat.size:
        raise LensMCError('The PSF array should have the same length of the detection catalogue.')

    # by default use all cores
    if processes is None:
        processes = mp.cpu_count()

    logger.debug('Allocate working arrays.')

    if callable(psf):
        oversampling = psf_.oversampling
    else:
        oversampling = psf[0].oversampling

    working_arrays = alloc_working_arrays(n_bulge, n_disc, oversampling=oversampling,
                                          dtype=dtype, fftw_flags=fftw_flags)

    logger.info(f'Make groups of detected objects within a friend-of-friend separation of {r_friend:.1f}".')

    groups = friend_of_friend_neighbour(cat['id'], cat['ra'], cat['dec'], r_friend / 3600, processes=processes)
    chunk_size = len(groups) // processes
    chunks = [groups[ii * chunk_size: (ii + 1) * chunk_size] for ii in range(0, processes)]
    for ii in range(len(groups) % processes):
        chunks[ii] += [groups[processes * chunk_size + ii]]
    max_group_size = np.max([len(group) for group in groups])

    logger.info(f'Found {len(groups)} groups for {cat.size} detected objects.')

    logger.debug('Initialise measurement catalogue')

    # augment data type if necessary
    # safer to copy the dtype tuple for repeated calls to the main function in the same script
    out_meas_cat_dtype = meas_cat_dtype.copy()
    for ii in range(len(out_meas_cat_dtype)):
        n = out_meas_cat_dtype[ii][0]
        if n == 'group' and max_group_size > 1:
            out_meas_cat_dtype[ii] += (max_group_size,)
        elif n == 'psf_e1' and image.n_exp > 1:
            out_meas_cat_dtype[ii] += (image.n_exp,)
        elif n == 'psf_e2' and image.n_exp > 1:
            out_meas_cat_dtype[ii] += (image.n_exp,)
        elif n == 'psf_r2' and image.n_exp > 1:
            out_meas_cat_dtype[ii] += (image.n_exp,)
        elif n == 'psf_fwhm' and image.n_exp > 1:
            out_meas_cat_dtype[ii] += (image.n_exp,)
        elif n == 'distortion_matrix' and image.n_exp > 1:
            out_meas_cat_dtype[ii] = (n, out_meas_cat_dtype[ii][1][0], (image.n_exp, 2, 2))

    # memory map array to temporary file, which will be removed upon exit
    fp = tempfile.NamedTemporaryFile()
    meas_cat = np.memmap(fp, dtype=out_meas_cat_dtype, mode='w+', shape=(cat.size,))

    # set some default values
    for col in meas_cat.dtype.descr:
        if np.issubdtype(col[1], np.floating):
            meas_cat[col[0]] = np.nan
        else:
            meas_cat[col[0]] = 0
    meas_cat['id'] = cat['id']
    meas_cat['group'] = 0
    meas_cat['w'] = 0

    logger.debug('Start main loop')

    # store progress counter
    lock = mp.Lock()
    counter = mp.Value('i', 0)

    # progress logging
    msg = f"{'Progress':8s}{'ID':>13s}{'chi2':>9s}{'SNR':>9s}"
    if mode != 'fast':
        msg += f"{'accept':>9s}"
    logger.info(msg)

    # define worker executing shear measurement on a target object or set of objects for neighbours
    def worker(chunk, image, psf, cat, meas_cat, e1=e1, e2=e2, re=re):

        # loop over groups in a chunk
        for group in chunk:

            # find objects in detection catalogue
            ix = _match(cat['id'], group)
            id_, ra_, dec_ = cat['id'][ix], cat['ra'][ix], cat['dec'][ix]

            # find segmentation map ID if present
            if 'seg_id' in cat.dtype.names:
                seg_id = cat['seg_id'][ix]
            else:
                seg_id = None

            # save measurement
            ix = _match(meas_cat['id'], group)
            # meas_cat['id'][ix] = id_
            for _ in ix:
                group_size = len(group)
                if group_size == 1:
                    meas_cat['group'][_] = group[0]
                else:
                    meas_cat['group'][_][:len(group)] = group

            # extract postage stamp
            # a bit larger than the default in measure_shear()
            # mainly to ease processing
            image_stamp = image.extract_postage_stamp(np.mean(ra_), np.mean(dec_), dim=postage_stamp,
                                                      x_buffer=x_buffer, y_buffer=y_buffer, return_removed_exposures=False)

            # model PSF at the nominal positions
            if callable(psf):
                psf_ = [psf(r, d) for r in ra_ for d in dec_]
            else:
                psf_ = [psf[_] for _ in ix]

            # call core measurement function
            try:
                results = measure_shear(image_stamp,
                                        e1=e1, e2=e2, re=re, delta_ra=delta_ra, delta_dec=delta_dec,
                                        id_=id_, ra=ra_, dec=dec_,
                                        postage_stamp=postage_stamp, x_buffer=x_buffer, y_buffer=y_buffer,
                                        dilate_mask=dilate_mask, dilate_segmentation=dilate_segmentation,
                                        seg_id=seg_id,
                                        psf=psf_,
                                        hl_to_exp=hl_to_exp, n_bulge=n_bulge, n_disc=n_disc,
                                        e_max=e_max, re_max=re_max, delta_max=delta_max,
                                        disc_only=disc_only, working_arrays=working_arrays,
                                        intcal=intcal, cal=cal,
                                        return_model=return_model,
                                        significance=significance,
                                        maximisation=maximisation, sampling=sampling,
                                        mode=mode,
                                        n_samples=n_samples, n_burnin=n_burnin,
                                        seed=seed, fftw_flags=fftw_flags,
                                        shape_noise=shape_noise, r_sg=r_sg,
                                        copy=copy, dtype=dtype,
                                        log_level=log_level)
                is_success = True
            except Exception as e:
                meas_cat['flag'][ix] += flag_failure
                msg = f'LensMC did not run on object(s) {group}. Exception: {e}'
                if traceback:
                    msg += f"\nTraceback: {''.join(format_tb(e.__traceback__))}"
                logger.warning(msg)
                is_success = False

            # save info
            if is_success:
                if mode != 'fast':
                    e1_meas, e2_meas = results.e1, results.e2
                else:
                    e1_meas, e2_meas = results.e1_max, results.e2_max
                meas_cat['e1'][ix] = e1_meas
                meas_cat['e2'][ix] = e2_meas
                meas_cat['re'][ix] = results.re
                meas_cat['ra'][ix] = results.ra
                meas_cat['dec'][ix] = results.dec
                meas_cat['flux'][ix] = results.flux
                meas_cat['flux_bulge'][ix] = results.flux_bulge
                meas_cat['flux_disc'][ix] = results.flux_disc
                meas_cat['bulgefrac'][ix] = results.bulgefrac
                meas_cat['snr'][ix] = results.snr
                meas_cat['mag'][ix] = results.magnitude
                meas_cat['zp'][ix] = results.zero_point
                meas_cat['hlr'][ix] = results.hlr
                meas_cat['chi2'][ix] = results.chi2
                meas_cat['dof'][ix] = results.dof
                meas_cat['flag'][ix] = results.flag
                meas_cat['e1_err'][ix] = results.e1_err
                meas_cat['e2_err'][ix] = results.e2_err
                meas_cat['e_var'][ix] = results.e_var
                meas_cat['w'][ix] = results.w
                meas_cat['re_err'][ix] = results.re_err
                meas_cat['ra_err'][ix] = results.ra_err
                meas_cat['dec_err'][ix] = results.dec_err
                meas_cat['flux_err'][ix] = results.flux_err
                meas_cat['flux_bulge_err'][ix] = results.flux_bulge_err
                meas_cat['flux_disc_err'][ix] = results.flux_disc_err
                meas_cat['bulgefrac_err'][ix] = results.bulgefrac_err
                meas_cat['snr_err'][ix] = results.snr_err
                meas_cat['mag_err'][ix] = results.magnitude_err
                meas_cat['hlr_err'][ix] = results.hlr_err
                meas_cat['acc'][ix] = results.acc
                if len(ix) == 1:
                    meas_cat['psf_e1'][ix] = results.psf_e1
                    meas_cat['psf_e2'][ix] = results.psf_e2
                    meas_cat['psf_r2'][ix] = results.psf_r2
                    meas_cat['psf_fwhm'][ix] = results.psf_fwhm
                    meas_cat['distortion_matrix'][ix] = results.distortion_matrix
                else:
                    meas_cat['psf_e1'][ix] = results.psf_e1.ravel()
                    meas_cat['psf_e2'][ix] = results.psf_e2.ravel()
                    meas_cat['psf_r2'][ix] = results.psf_r2.ravel()
                    meas_cat['psf_fwhm'][ix] = results.psf_fwhm.ravel()
                    for oo, _ in enumerate(ix):
                        meas_cat['distortion_matrix'][_] = results.distortion_matrix[oo]
                meas_cat['pvalue_bkg'][ix] = results.pvalue_bkg
                meas_cat['likl_calls_optim'][ix] = results.likl_calls_optim
                meas_cat['likl_calls_mcmc'][ix] = results.likl_calls_mcmc

            # set the progress counter
            with lock:
                # update counter
                counter.value += id_.size
                progress = counter.value * 100 / cat.size

                # log info
                if is_success:
                    snr = np.atleast_1d(results.snr)
                    for ii in range(id_.size):
                        msg = f'{progress:7.1f}%{id_[ii]:13d}{results.chi2:9.3g}{snr[ii]:9.3g}'
                        if mode != 'fast':
                            msg += f'{results.acc:9.2g}'
                        logger.info(msg)

        return

    # run measurement in parallel
    # fork the requested number of processes and save results to memory map
    if processes > 1:
        procs = [mp.Process(target=worker, args=(chunk, image, psf, cat, meas_cat)) for chunk in chunks]
        [p.start() for p in procs]
        [p.join() for p in procs]
    else:
        worker(chunks[0], image, psf, cat, meas_cat)

    # copy array to memory before returning
    meas_cat = meas_cat.copy()

    return meas_cat


def _flatten(x):
    return [item for sublist in x for item in sublist]


def _match(x, y):
    """
    Match x to y, i.e. find indices of y in x.
    """
    return _flatten([np.where(x == _)[0].tolist() for _ in y])

