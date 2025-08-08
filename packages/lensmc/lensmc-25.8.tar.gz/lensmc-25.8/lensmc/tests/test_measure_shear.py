import cProfile
import numpy as np
import os
import pytest
import time
import unittest
from astropy.wcs import WCS
from pkg_resources import resource_filename

from lensmc import measure_shear, __path__ as lensmc_path
# noinspection PyUnresolvedReferences
from lensmc.galaxy_model import alloc_working_arrays
from lensmc.image import Image, make as make_image
from lensmc.psf import PSF
from lensmc.utils import logger

# If the LENSMC_PROFILING environment variable is set, enable profiling for each test
if "LENSMC_PROFILING" in os.environ and os.environ["LENSMC_PROFILING"] == "1":
    profiling = True

    # needed to get the function name for the profiling output filename
    import inspect

    # basename of the profiling output name
    profiling_basename = os.path.splitext(__file__)[0] + "."
else:
    profiling = False


class TestFitPostageStamp(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def setup(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # image properties
        self.dim = 384
        dtype = np.float32

        # choose a random seed
        self.seed = 67794

        # draw dummy PSFs
        hdim = self.dim // 2
        psf = np.zeros((self.dim, self.dim), dtype=dtype)
        psf[hdim + 1, hdim + 1] = 1.0
        self.psf = [psf] * 2
        self.oversampling = 3

        # access the LensMC cache file for fast model generation
        cache_fname = f'cache_{self.oversampling}x.bin'
        cache_files = [os.path.join(lensmc_path[0], f'aux/{cache_fname}'), resource_filename('lensmc', cache_fname)]
        for f in cache_files:
            if f is not None and os.path.isfile(f):
                cache_file = f
                break

        # choose some galaxy parameters
        id_ = (0, 1)
        e1 = (0.3, 0.0)
        e2 = (0.0, -0.3)
        re = (0.3, 0.5)
        ra0, dec0 = 10.0, -20.0
        ra = (ra0, ra0 + 1.39e-4)
        dec = (dec0, dec0 + 5.56e-5)
        flux = (1e4,) * 2
        bulgefrac = (0.3,) * 2
        hl_to_exp = 0.15
        n_bulge, n_disc = 1.0, 1.0

        # working arrays
        self.working_arrays = alloc_working_arrays(n_bulge, n_disc, cache_file=cache_file, oversampling=self.oversampling)

        # define a WCS
        self.wcs = WCS(naxis=2)
        self.wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        self.wcs.wcs.cd = 0.1 * np.diag([-1, 1]) / 3600
        self.wcs.wcs.crpix = [self.dim // 2, self.dim // 2 + 5]
        self.wcs.wcs.crval = [ra0, dec0]

        # make an image of a galaxy
        self.image = make_image(self.dim, self.dim, e1[0], e2[0], re[0], ra[0], dec[0], flux[0], bulgefrac[0],
                                psf_disc=self.psf[0], psf_bulge=self.psf[0], w=self.wcs,
                                oversampling=self.oversampling,
                                hl_to_exp=hl_to_exp, n_bulge=n_bulge, n_disc=n_disc,
                                dtype=dtype)

        # make an image of two galaxies for joint measurement
        self.crowded_image = make_image(self.dim, self.dim, e1, e2, re, ra, dec, flux, bulgefrac,
                                        psf_disc=self.psf, psf_bulge=self.psf, w=self.wcs,
                                        oversampling=self.oversampling,
                                        hl_to_exp=hl_to_exp, n_bulge=n_bulge, n_disc=n_disc,
                                        dtype=dtype)

        self.ra = ra
        self.dec = dec
        self.id_ = id_

        if profiling:
            profiler.disable()
            filename = profiling_basename + str(inspect.currentframe().f_code.co_name) + ".profile"
            print(f"Writing profiling results to '{filename}'")
            profiler.dump_stats(filename)

    def test_single_exposure(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # make sure we seed the random number generator to produce consistent results
        np.random.seed(self.seed)

        # put psf in PSF class
        psf = PSF(self.psf[0], oversampling=self.oversampling)

        # put image in Image class
        image = Image(self.image, wcs=self.wcs)

        t0 = time.time()

        # run lensmc
        results = measure_shear(image, id_=self.id_[0], ra=self.ra[0], dec=self.dec[0], psf=psf,
                                working_arrays=self.working_arrays, seed=self.seed)

        logger.info('Runtime = {:.3f}'.format(time.time() - t0))

        logger.info('Individual galaxy, single exposure: chi2 = {:.3f}'.format(results.chi2))

        if profiling:
            profiler.disable()
            filename = profiling_basename + str(inspect.currentframe().f_code.co_name) + ".profile"
            print(f"Writing profiling results to '{filename}'")
            profiler.dump_stats(filename)

        pass

    def test_multiple_exposures(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # make sure we seed the random number generator to produce consistent results
        np.random.seed(self.seed)

        n_exposures = 4

        # put psf in PSF class
        psf = PSF([self.psf[0]] * n_exposures, oversampling=self.oversampling)

        # put image in Image class
        image = Image([self.image] * n_exposures, wcs=[self.wcs] * n_exposures)

        t0 = time.time()

        # run lensmc
        results = measure_shear(image, id_=self.id_[0], ra=self.ra[0], dec=self.dec[0], psf=psf,
                                working_arrays=self.working_arrays, seed=self.seed)

        logger.info('Runtime = {:.3f}'.format(time.time() - t0))

        logger.info('Individual galaxy, multiple exposures: chi2 = {:.3f}'.format(results.chi2))

        if profiling:
            profiler.disable()
            filename = profiling_basename + str(inspect.currentframe().f_code.co_name) + ".profile"
            print(f"Writing profiling results to '{filename}'")
            profiler.dump_stats(filename)

        pass

    def test_joint_single_exposure(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # make sure we seed the random number generator to produce consistent results
        np.random.seed(self.seed)

        # put psf in PSF class
        psf = [PSF(self.psf[0], oversampling=self.oversampling),
               PSF(self.psf[1], oversampling=self.oversampling)]

        # put image in Image class
        image = Image(self.crowded_image, wcs=self.wcs)

        t0 = time.time()

        # run lensmc
        results = measure_shear(image, id_=self.id_, ra=self.ra, dec=self.dec, psf=psf,
                                working_arrays=self.working_arrays, seed=self.seed)

        logger.info('Runtime = {:.3f}'.format(time.time() - t0))

        logger.info('Joint measurement of two galaxies, single exposure: chi2 = {:.3f}'.format(results.chi2))

        if profiling:
            profiler.disable()
            filename = profiling_basename + str(inspect.currentframe().f_code.co_name) + ".profile"
            print(f"Writing profiling results to '{filename}'")
            profiler.dump_stats(filename)

        pass

    def test_joint_multiple_exposures(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # make sure we seed the random number generator to produce consistent results
        np.random.seed(self.seed)

        n_exposures = 4

        # put psf in PSF class
        psf = [PSF([self.psf[0]] * n_exposures, oversampling=self.oversampling),
               PSF([self.psf[1]] * n_exposures, oversampling=self.oversampling)]

        # put image in Image class
        image = Image([self.crowded_image] * n_exposures, wcs=[self.wcs] * n_exposures)

        t0 = time.time()

        # run lensmc
        results = measure_shear(image, id_=self.id_, ra=self.ra, dec=self.dec, psf=psf,
                                working_arrays=self.working_arrays, seed=self.seed)

        logger.info('Runtime = {:.3f}'.format(time.time() - t0))

        logger.info('Joint measurement of two galaxies, multiple exposures: chi2 = {:.3f}'.format(results.chi2))

        if profiling:
            profiler.disable()
            filename = profiling_basename + str(inspect.currentframe().f_code.co_name) + ".profile"
            print(f"Writing profiling results to '{filename}'")
            profiler.dump_stats(filename)

        pass


if __name__ == '__main__':
    print("Running tests with profiling...")

    # set this environment variable which tells this script (when loaded again by pytest) to enable profiling
    os.environ["LENSMC_PROFILING"] = "1"

    pytest.main(["-s", __file__])
