import cProfile
import numpy as np
import os
import pytest
import time
import unittest
from astropy.convolution import AiryDisk2DKernel
from astropy.wcs import WCS
from scipy.ndimage import affine_transform
from scipy.stats import truncnorm

from lensmc import measure_shear_all
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


class TestMeasureAll(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def setup(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # image properties
        dim = 2048
        dim2 = dim // 2
        dtype = np.float32

        # choose a random seed
        self.seed = 67794

        # define a PSF with an Airy profile
        # AiryDisk2DKernel centres it at size/2 - 1, but we want to have it at size/2, consistent with FFTW
        pdim = 128
        pdim2 = pdim // 2
        e1, e2, r = -0.01, 0., 7.
        psf = AiryDisk2DKernel(r, x_size=pdim + 1, y_size=pdim + 1, model='oversample').array[:-1, :-1]
        A = np.array([[1 + e1, -e2], [-e2, 1 - e1]]) / (1 - np.sqrt(e1 ** 2 - e2 ** 2))
        half_arr = np.array([pdim2, pdim2])
        psf = affine_transform(psf, A, offset=half_arr - A @ half_arr)
        self.psf = PSF(psf / psf.sum(), oversampling=3)

        # choose some galaxy parameters
        n = 200
        id_ = np.arange(n)
        np.random.seed(self.seed)
        e = truncnorm.rvs(0, 0.5, size=n)
        phi = np.random.uniform(0, 2 * np.pi, size=n)
        e1, e2 = e * np.cos(phi), e * np.sin(phi)
        re = np.random.uniform(0.05, 0.5, n)
        ra0, dec0 = 10.0, -20.0
        cos_dec0 = np.cos(dec0 * np.pi / 180)
        ra = np.random.uniform(ra0 - 0.01 / cos_dec0, ra0 + 0.02 / cos_dec0, n)
        dec = np.random.uniform(dec0 - 0.01, dec0 + 0.02, n)
        flux = np.random.uniform(100, 1000, n)
        bulgefrac = np.random.uniform(0, 1, n)
        hl_to_exp = 0.15
        n_bulge, n_disc = 1.0, 1.0

        # define a WCS
        wcs = WCS(naxis=2)
        wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        wcs.wcs.cd = 0.1 * np.diag([-1, 1]) / 3600
        wcs.wcs.crpix = [dim2, dim2]
        wcs.wcs.crval = [ra0, dec0]

        # make an image of two galaxies for joint measurement
        image = make_image(dim, dim, e1, e2, re, ra, dec, flux, bulgefrac,
                           psf_disc=self.psf[0], psf_bulge=self.psf[0], w=wcs,
                           oversampling=self.psf.oversampling,
                           hl_to_exp=hl_to_exp, n_bulge=n_bulge, n_disc=n_disc,
                           dtype=dtype)
        self.image = Image(image, wcs=wcs)

        # define detection catalogue
        cat = np.zeros((n,), dtype=[('id', int), ('e1', float), ('e2', float), ('ra', float), ('dec', float)])
        cat['id'], cat['e1'], cat['e2'], cat['ra'], cat['dec'] = id_, e1, e2, ra, dec
        self.cat = cat

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

        t0 = time.time()

        # run lensmc
        meas_cat = measure_shear_all(self.image, cat=self.cat, psf=self.psf, seed=self.seed)

        logger.info(f'Runtime = {(time.time() - t0) / self.cat.size:.3f} secs / galaxy')

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
