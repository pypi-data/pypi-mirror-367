import cProfile
import numpy as np
import os
import time
import unittest
import pytest
# noinspection PyUnresolvedReferences
from lensmc.galaxy_model import alloc_working_arrays, generate_model as generate_galaxy_model
from lensmc.psf import initialise_pixelavg_ft, calculate_psf_ft
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


class TestGalaxyRuntime(unittest.TestCase):

    def test_core_runtime(self):

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        # some hard coded values
        oversampling = 3
        n_bulge, n_disc = 1.0, 1.0

        # draw a dummy PSF
        dim = 512
        hdim = dim // 2
        psf = np.zeros((dim, dim), dtype=np.float32)
        psf[hdim + 1, hdim + 1] = 1.0

        # allocate working arrays dictionary for fast model generation
        working_arrays = alloc_working_arrays(n_bulge, n_disc, oversampling=oversampling, dtype=np.float32)

        # pre-process PSF
        psf_ft = calculate_psf_ft(psf, oversampling=oversampling, dtype=np.float32)

        disc_ht = working_arrays.disc_ht

        # dummy astrometric distorion
        astrometric_distortion = np.eye(2, dtype=np.float64)

        logger.info('Galaxy model runtime:')

        # measure runtime
        n = 100
        re = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]

        for jj in range(len(re)):

            t = np.zeros((n + 1,))
            t[0] = time.time()
            for ii in range(n):
                generate_galaxy_model(0.3, 0., re[jj], 0.1, 0.,
                                      disc_ht, psf_ft, working_arrays,
                                      astrometric_distortion=astrometric_distortion,
                                      x_offset=0, y_offset=0,
                                      pixel_scale=1,
                                      do_hankel_resample=True)

                t[ii] = time.time()
            t = (t[1:] - t[:-1]) * n
            t *= 1000.0 / n

            tmed = np.median(t)
            dtplus, dtminus = np.percentile(t, 75) - tmed, tmed - np.percentile(t, 25)

            logger.info(f'(size {re[jj]:.1f}) = ({tmed:.2f} +{dtplus:.2f} -{dtminus:.2f}) ms')

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
