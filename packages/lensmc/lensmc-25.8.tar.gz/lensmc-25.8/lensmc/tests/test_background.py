import numpy as np
import pytest
import unittest

from lensmc.image import Image, make as make_image


class Background(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup(self):

        # image properties
        dim = 384
        dtype = np.float32

        # make a list of dummy image containing a deterministic background + gradient, and a bright blob that should be masked out
        xxx = np.arange(dim, dtype=dtype)
        XXX, YYY = np.meshgrid(xxx, xxx)
        image = [-0.09 * XXX + 0.05 * YYY + 100,
                 0.02 * XXX - 0.06 * YYY + 200]
        image[0][20: 30, 20: 30] = 10_000
        image[1][200: 230, 200: 230] = 10_000
        mask = [np.ones((dim, dim), dtype=bool),
                np.ones((dim, dim), dtype=bool)]
        mask[0][20: 30, 20: 30] = 0
        mask[1][200: 230, 200: 230] = 0
        seg = [np.full((dim, dim), fill_value=-1, dtype=int)] * 2
        self.image = Image(image, mask=mask, seg=seg)

    def test_background(self):

        self.image.estimate_dc()

        image = self.image
        assert np.all(np.isclose(image.dc[0][image.bkg_mask[0]], image[0][image.bkg_mask[0]]))
        assert np.all(np.isclose(image.dc[1][image.bkg_mask[1]], image[1][image.bkg_mask[1]]))

        pass

