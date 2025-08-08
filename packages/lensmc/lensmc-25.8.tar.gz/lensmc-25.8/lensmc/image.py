"""
LensMC - a Python package for weak lensing shear measurements.
Image module.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
import astropy.io.fits as fits
import pickle
from astropy.io.fits import ImageHDU
from astropy.stats import sigma_clip
from astropy.wcs import WCS
from copy import deepcopy
from scipy.ndimage import affine_transform, binary_dilation, grey_dilation
from typing import List, Type, TypeVar, Union

from lensmc.flags import flag_mask_bad, flag_seg_unassigned
# noinspection PyUnresolvedReferences
from lensmc.galaxy_model import alloc_working_arrays, generate_model as generate_galaxy_model, odim, oversampling,\
    rfiducial, oversampling, mdim
from lensmc.models import background_noise
from lensmc.segmentation import make_obj_segm
# noinspection PyUnresolvedReferences
from lensmc.star_model import generate_model as generate_star_model
from lensmc.utils import logger, LensMCError


# generic array like data type
T = TypeVar('T')
ArrayLike = Union[List[np.ndarray], np.ndarray]
ScalarOrArrayLike = Union[Union[List[np.ndarray], List[T]], np.ndarray, float]
ListLike = Union[T, List[T]]


class Image:
    """
    Image class used as data container for LensMC.

    :param image: Multiple exposure pixel data
    :param mask: Good pixel mask(s): 1 if pixel is good, 0 otherwise
    :param seg: Segmentation map(s): ID if pixel is associated to ID>0 galaxy; 'flag_seg_unassigned' otherwise
    :param dc: DC level(s); otherwise estimated from masked data
    :param rms: RMS of background noise; otherwise estimated from masked data
    :param wcs: WCS(s) astrometric solution
    :param x_origin: x-coordinate(s) of the origin of the image in the reference frame of the image the WCS refers to
    :param y_origin: y-coordinate(s) of the origin of the image in the reference frame of the image the WCS refers to
    :param exposure_time: Exposure time [s]
    :param gain: Gain for digital units to photo-electrons [e-/ADU]
    :param read_noise: RMS of read noise [ADU]
    :param zero_point: Magnitude zero-point
    :param order: Axis order: yx for y along axis 0 (default); xy for x along axis 0, if so transpose.
    :param dtype: Pixel data type
    """

    __slots__ = ('exp', 'n_exp', 'mask', 'bkg_mask', 'seg', 'dc', 'rms', 'weight',
                 'wcs', 'x_origin', 'y_origin',
                 'exposure_time', 'gain', 'read_noise', 'zero_point', 'normalised_zero_point',
                 'order', 'dtype', 'bad_exp', '_is_count_rate')

    def __init__(self, image: ArrayLike, mask: ArrayLike = None, seg: ArrayLike = None,
                 dc: ScalarOrArrayLike = None, rms: ScalarOrArrayLike = None, wcs: ListLike[WCS] = None,
                 x_origin: ListLike[float] = None, y_origin: ListLike[float] = None,
                 exposure_time: ListLike[float] = None, gain: ListLike[float] = None,
                 read_noise: ListLike[float] = None, zero_point: ListLike[float] = None,
                 order: str = 'yx', dtype: Type = np.float32):

        # basic checks
        if isinstance(image, np.ndarray):
            image = [image]
        n = len(image)
        if not isinstance(image, list) or n == 0:
            raise LensMCError('Image must be a list of ndarray, of length > 1.')
        if mask is not None:
            if isinstance(mask, np.ndarray):
                mask = [mask]
            if not isinstance(mask, list):
                raise LensMCError('Mask must be a list of ndarray.')
            if len(mask) != n:
                raise LensMCError('Mask must have the same length of image.')
        if seg is not None:
            if isinstance(seg, np.ndarray):
                seg = [seg]
            if not isinstance(seg, list):
                raise LensMCError('Segmentation map must be a list of ndarray.')
            if len(seg) != n:
                raise LensMCError('Segmentation map must have the same length of image.')
        if dc is not None:
            if isinstance(dc, np.ndarray) or np.isscalar(dc):
                dc = [dc]
            if not isinstance(dc, list):
                raise LensMCError('DC must be a list of ndarray or scalar.')
            if len(dc) != n:
                raise LensMCError('DC must have the same length of image.')
        if rms is not None:
            if isinstance(rms, np.ndarray) or np.isscalar(rms):
                rms = [rms]
            if not isinstance(rms, list):
                raise LensMCError('RMS must be a list of ndarray or scalar.')
            if len(rms) != n:
                raise LensMCError('RMS must have the same length of image.')
        if wcs is not None:
            if isinstance(wcs, WCS):
                wcs = [wcs]
            if not isinstance(wcs, list):
                raise LensMCError('WCS must be a list of astropy.wcs.WCS.')
            if len(wcs) != n:
                raise LensMCError('WCS must have the same length of image.')
        else:
            wcs = [_get_linear_wcs() for _ in range(n)]
        if x_origin is not None:
            x_origin = np.atleast_1d(x_origin)
            if x_origin.size != n:
                raise LensMCError('X origin must have the same length of image.')
        else:
            x_origin = np.zeros(n)
        if y_origin is not None:
            y_origin = np.atleast_1d(y_origin)
            if y_origin.size != n:
                raise LensMCError('Y origin must have the same length of image.')
        else:
            y_origin = np.zeros(n)
        if exposure_time is not None:
            exposure_time = np.atleast_1d(exposure_time)
            if exposure_time.size != n:
                raise LensMCError('Exposure time must have the same length of image.')
        if gain is not None:
            gain = np.atleast_1d(gain)
            if gain.size != n:
                raise LensMCError('Gain must have the same length of image.')
        if read_noise is not None:
            read_noise = np.atleast_1d(read_noise)
            if read_noise.size != n:
                raise LensMCError('Read noise must have the same length of image.')
        if zero_point is not None:
            zero_point = np.atleast_1d(zero_point)
            if zero_point.size != n:
                raise LensMCError('Zero point must have the same length of image.')

        # remove bad exposures with None
        exps = [ii for ii in range(len(image)) if image[ii] is None]
        if exps:
            image = _drop(image, exps)
            if mask is not None:
                mask = _drop(mask, exps)
            if seg is not None:
                seg = _drop(seg, exps)
            if dc is not None:
                dc = _drop(dc, exps)
            if rms is not None:
                rms = _drop(rms, exps)
            if wcs is not None:
                wcs = _drop(wcs, exps)
            x_origin = _drop(x_origin, exps)
            y_origin = _drop(y_origin, exps)
            exposure_time = _drop(exposure_time, exps)
            gain = _drop(exposure_time, exps)
            read_noise = _drop(exposure_time, exps)
            zero_point = _drop(exposure_time, exps)

        # further checks
        n = len(image)
        for ii in range(n):
            if not isinstance(image[ii], np.ndarray):
                raise LensMCError('Image must be an array, or an iterator of arrays.')
            shape = image[ii].shape
            if shape[0] % 2:
                raise LensMCError('Image size along axis 0 must be even.')
            if shape[1] % 2:
                raise LensMCError('Image size along axis 1 must be even.')
            if image[ii].dtype != dtype:
                image[ii] = image[ii].astype(dtype)
            if mask and mask[ii] is not None:
                if not isinstance(mask[ii], np.ndarray):
                    raise LensMCError('Mask must be an array, or an iterator of arrays (including None).')
                if mask[ii].shape[0] != shape[0] or mask[ii].shape[1] != shape[1]:
                    raise LensMCError('Mask must have the same shape of image.')
                if not mask[ii].dtype == bool:
                    raise LensMCError('Mask must be of type bool.')
            if seg and seg[ii] is not None:
                if not isinstance(seg[ii], np.ndarray):
                    raise LensMCError('Segmentation map must be an array, or an iterator of arrays.')
                if seg[ii].shape[0] != shape[0] or seg[ii].shape[1] != shape[1]:
                    raise LensMCError('Segmentation map must have the same shape of image.')
                if not np.issubdtype(seg[ii].dtype, np.integer):
                    raise LensMCError('Segmentation map must be of type integer.')
            if dc and dc[ii] is not None:
                if not (isinstance(dc[ii], np.ndarray) or np.isscalar(dc[ii])):
                    raise LensMCError('DC must be an array/scalar, or an iterator of arrays/scalars.')
                if isinstance(dc[ii], np.ndarray) and (dc[ii].shape[0] != shape[0] or dc[ii].shape[1] != shape[1]):
                    raise LensMCError('DC must have the same shape of image.')
            if rms and rms[ii] is not None:
                if not (isinstance(rms[ii], np.ndarray) or np.isscalar(rms[ii])):
                    raise LensMCError('RMS must be an array/scalar, or an iterator of arrays/scalars.')
                if isinstance(rms[ii], np.ndarray) and (rms[ii].shape[0] != shape[0] or rms[ii].shape[1] != shape[1]):
                    raise LensMCError('RMS must have the same shape of image.')
            if wcs and wcs[ii] is not None:
                if not isinstance(wcs[ii], WCS):
                    raise LensMCError('WCS must be an astropy.wcs.WCS.')
            if x_origin.size != n:
                raise LensMCError('X origin must have the same length of image.')
            if y_origin.size != n:
                raise LensMCError('Y origin must have the same length of image.')
            if exposure_time is not None and exposure_time.size != n:
                raise LensMCError('Exposure time must have the same length of image.')
            if gain is not None and gain.size != n:
                raise LensMCError('Gain must have the same length of image.')
            if read_noise is not None and read_noise.size != n:
                raise LensMCError('Read noise must have the same length of image.')
            if zero_point is not None and zero_point.size != n:
                raise LensMCError('Zero point must have the same length of image.')

        # check order
        if order not in ('yx', 'xy'):
            raise LensMCError('Order must be either yx or xy.')
        if order == 'xy':
            for ii in range(n):
                image[ii] = image[ii].T
                if mask and mask[ii] is not None:
                    mask[ii] = mask[ii].T
                if seg and seg[ii] is not None:
                    seg[ii] = seg[ii].T
                if dc and dc[ii] is not None and not np.isscalar(dc[ii]):
                    dc[ii] = dc[ii].T
                if rms and rms[ii] is not None and not np.isscalar(rms[ii]):
                    rms[ii] = rms[ii].T

        # set attributes
        # including placeholders for background mask and weights, which will be set if needed
        self.exp = image
        self.n_exp = n
        self.mask = mask
        self.seg = seg
        self.dc = dc
        self.rms = rms
        self.wcs = wcs
        self.x_origin = x_origin
        self.y_origin = y_origin
        self.exposure_time = exposure_time
        self.gain = gain
        self.read_noise = read_noise
        self.zero_point = zero_point
        self.normalised_zero_point = zero_point.mean() if zero_point is not None else None
        self.bkg_mask = None
        self.weight = None
        self.order = order
        self.dtype = dtype
        self.bad_exp = None
        self._is_count_rate = False

    def __getitem__(self, ii):
        return self.exp[ii]

    def __setitem__(self, ii, val):
        self.exp[ii] = val

    def world2pix(self, ra, dec, origin=0):
        ra, dec = np.atleast_1d(ra), np.atleast_1d(dec)
        n = len(ra)
        if n != len(dec):
            raise LensMCError('ra and dec must have the same length.')
        x = np.empty((self.n_exp, n))
        y = np.empty((self.n_exp, n))
        for ii in range(self.n_exp):
            x[ii], y[ii] = self.wcs[ii].all_world2pix(ra, dec, origin)
        x -= self.x_origin[:, np.newaxis]
        y -= self.y_origin[:, np.newaxis]
        return x, y

    def pix2world(self, x, y, origin=0):
        x, y = np.atleast_1d(x), np.atleast_1d(y)
        if x.shape != y.shape:
            raise LensMCError('x and y must have the same shape.')
        if x.ndim == 1:
            x = x[np.newaxis, :]
            y = y[np.newaxis, :]
        if x.shape[0] != self.n_exp:
            raise LensMCError('Axis 0 of x and y must have the same size of n_exp.')
        n = x.shape[1]
        ra = np.empty((self.n_exp, n))
        dec = np.empty((self.n_exp, n))
        x = x + self.x_origin[:, np.newaxis]
        y = y + self.y_origin[:, np.newaxis]
        for ii in range(self.n_exp):
            ra[ii], dec[ii] = self.wcs[ii].all_pix2world(x[ii], y[ii], origin)
        return ra, dec

    def extract_postage_stamp(self, x, y, dim=384, x_buffer=3, y_buffer=3,
                              return_position_in_stamps=False, return_removed_exposures=False):

        if (not np.isscalar(x) and len(x) > 1) or (not np.isscalar(y) and len(y) > 1):
            raise LensMCError('x and y position must be scalars.')
        x, y = self.world2pix(x, y)

        image = [None] * self.n_exp
        mask = [None] * self.n_exp
        if self.mask is not None:
            is_mask = True
        else:
            is_mask = False
        if self.seg is not None:
            is_seg = True
            seg = [None] * self.n_exp
        else:
            is_seg = False
            seg = None
        if self.dc is not None:
            is_dc = True
            dc = [None] * self.n_exp
        else:
            is_dc = False
            dc = None
        if self.rms is not None:
            is_rms = True
            rms = [None] * self.n_exp
        else:
            is_rms = False
            rms = None
        stamp_x_origin = np.empty(self.n_exp)
        stamp_y_origin = np.empty(self.n_exp)
        for ii in range(self.n_exp):
            if x_buffer < x[ii] < self[ii].shape[1] and y_buffer < y[ii] < self[ii].shape[0]:
                image[ii], stamp_mask, stamp_x_origin[ii], stamp_y_origin[ii] = \
                    extract_postage_stamp(self[ii], x[ii], y[ii], dim=dim, return_mask=True, return_corner=True)
                if is_mask:
                    mask[ii] = extract_postage_stamp(self.mask[ii], x[ii], y[ii], dim=dim)
                else:
                    mask[ii] = np.ones_like(image[ii], dtype=bool)
                mask[ii] *= stamp_mask
                if is_seg:
                    seg[ii] = extract_postage_stamp(self.seg[ii], x[ii], y[ii], dim=dim)
                    seg[ii][stamp_mask == 0] = flag_seg_unassigned
                if is_dc:
                    if np.isscalar(self.dc[ii]):
                        dc[ii] = self.dc[ii]
                    else:
                        dc[ii] = extract_postage_stamp(self.dc[ii], x[ii], y[ii], dim=dim)
                if is_rms:
                    if np.isscalar(self.rms[ii]):
                        rms[ii] = self.rms[ii]
                    else:
                        rms[ii] = extract_postage_stamp(self.rms[ii], x[ii], y[ii], dim=dim)
            else:
                logger.debug(f'No postage stamp extracted for exposure {ii}.')
        x_origin = self.x_origin + stamp_x_origin
        y_origin = self.y_origin + stamp_y_origin
        wcs = deepcopy(self.wcs)
        exposure_time = self.exposure_time
        gain = self.gain
        read_noise = self.read_noise
        zero_point = self.zero_point

        # remove bad exposures
        exps = [ii for ii in range(len(image)) if image[ii] is None]
        if exps:
            image = _drop(image, exps)
            mask = _drop(mask, exps)
            seg = _drop(seg, exps)
            dc = _drop(dc, exps)
            rms = _drop(rms, exps)
            wcs = _drop(wcs, exps)
            x_origin = _drop(x_origin, exps)
            y_origin = _drop(y_origin, exps)
            exposure_time = _drop(exposure_time, exps)
            gain = _drop(gain, exps)
            read_noise = _drop(read_noise, exps)
            zero_point = _drop(zero_point, exps)

        # initialise stamp image
        if len(image) > 0:
            stamp = Image(image, mask=mask, seg=seg, dc=dc, rms=rms, wcs=wcs, x_origin=x_origin, y_origin=y_origin,
                          exposure_time=exposure_time, gain=gain, read_noise=read_noise, zero_point=zero_point)
        else:
            raise LensMCError(f'No postage stamp extracted.')

        for ii in range(self.n_exp):
            x[ii] -= stamp_x_origin[ii]
            y[ii] -= stamp_y_origin[ii]

        if return_position_in_stamps and return_removed_exposures:
            return stamp, x, y, exps
        elif return_position_in_stamps and not return_removed_exposures:
            return stamp, x, y
        elif not return_position_in_stamps and return_removed_exposures:
            return stamp, exps
        else:
            return stamp

    def make_segmentation(self, id_, x, y, sigma=1., truncate=4., threshold=4., deblend=False):

        x, y = self.world2pix(x, y)

        self.seg = [None] * self.n_exp
        blends = [None] * self.n_exp
        for ii in range(self.n_exp):
            if self.mask is not None:
                mask = self.mask[ii]
            else:
                mask = None
            self.seg[ii], blends[ii] = make_obj_segm(self[ii], id_, x[ii], y[ii], sigma=sigma, truncate=truncate,
                                                     threshold=threshold, mask=mask, deblend=deblend)
        merged_blends = blends[0]
        if self.n_exp == 1:
            for ii, b in enumerate(blends[0]):
                for jj in range(1, self.n_exp):
                    for bb in blends[jj]:
                        if any(item in b for item in bb):
                            merged_blends[ii] += bb
                            merged_blends[ii] = list(set(merged_blends[ii]))
        return merged_blends

    def to_normalised_count_rate(self):
        if self._is_count_rate:
            raise LensMCError('Data has already been converted to normalised count rate')
        if self.exposure_time is None and self.gain is None and self.zero_point is None:
            return
        norm = 1
        if self.gain is not None:
            norm *= self.gain
        if self.exposure_time is not None:
            norm /= self.exposure_time
        if self.zero_point is not None:
            norm /= 10 ** ((self.zero_point - self.normalised_zero_point) / 2.5)
        for ii in range(self.n_exp):
            self[ii] *= norm[ii]
            if self.rms is not None:
                self.rms[ii] *= norm[ii]
            if self.dc is not None:
                self.dc[ii] *= norm[ii]

    def dilate_mask(self):
        if self.mask is None:
            raise LensMCError('Please set mask.')
        s = np.ones((3, 3), dtype=bool)
        for ii in range(self.n_exp):
            self.mask[ii] = ~binary_dilation(~self.mask[ii], structure=s)

    def dilate_segmentation(self):
        if self.seg is None:
            raise LensMCError('Please set segmentation map.')
        s = np.zeros((3, 3), dtype=bool)
        for ii in range(self.n_exp):
            self.seg[ii] = grey_dilation(self.seg[ii], structure=s)

    def merge_mask_with_segmentation(self, id_, x, y, seg_id=None):

        x, y = self.world2pix(x, y)

        if self.mask is None:
            raise LensMCError('Please provide mask.')
        if self.seg is None:
            raise LensMCError('Please provide seg.')

        # get the segmentation map ID at the right position, and merge
        id_ = np.atleast_1d(id_)
        if seg_id is not None:
            seg_id = np.atleast_1d(seg_id)
        for ii in range(self.n_exp):
            if seg_id is None:
                xi, yi = np.round(x[ii]).astype(int), np.round(y[ii]).astype(int)
                seg_id = np.atleast_1d(self.seg[ii][yi, xi])
            if not set(seg_id).issubset(id_):
                raise LensMCError(f'Segmentation ID {seg_id} does not match with object ID {id_}.')
            is_target = np.zeros_like(self.seg[ii], dtype=bool)
            for ss in seg_id:
                is_target += self.seg[ii] == ss
            is_noise = self.seg[ii] == flag_seg_unassigned
            self.mask[ii] *= is_target + is_noise

    def verify_mask(self, id_, x, y):

        x, y = self.world2pix(x, y)

        if self.mask is None:
            raise LensMCError('Please provide mask.')

        # get the mask at the right position, check it, and return indices of bad exposures
        exps = []
        for ii in range(self.n_exp):
            xi, yi = np.round(x[ii]).astype(int), np.round(y[ii]).astype(int)
            if not all(np.atleast_1d(self.mask[ii][yi, xi])):
                exps += [ii]
        self.bad_exp = exps

        return exps

    def drop_exposures(self, exp):

        if self.n_exp == 0:
            raise LensMCError('No exposures to drop.')

        if not isinstance(exp, (list, tuple, np.ndarray)):
            exp = [exp]

        if self.exp is not None:
            self.exp = _drop(self.exp, exp)
        self.n_exp = len(self.exp)
        if self.mask is not None:
            self.mask = _drop(self.mask, exp)
        if self.bkg_mask is not None:
            self.bkg_mask = _drop(self.bkg_mask, exp)
        if self.seg is not None:
            self.seg = _drop(self.seg, exp)
        if self.dc is not None:
            self.dc = _drop(self.dc, exp)
        if self.rms is not None:
            self.rms = _drop(self.rms, exp)
        if self.weight is not None:
            self.weight = _drop(self.weight, exp)
        if self.wcs is not None:
            self.wcs = _drop(self.wcs, exp)
        if self.x_origin is not None:
            self.x_origin = _drop(self.x_origin, exp)
        if self.y_origin is not None:
            self.y_origin = _drop(self.y_origin, exp)

    def set_background_mask(self):
        if self.seg is None:
            raise LensMCError('Please set segmentation map')
        if self.mask is None:
            raise LensMCError('Please set mask.')
        self.bkg_mask = [None] * self.n_exp
        for ii in range(self.n_exp):
            self.bkg_mask[ii] = np.copy(self.mask[ii])
            self.bkg_mask[ii] *= self.seg[ii] == flag_seg_unassigned

    def sigma_clip(self, clip=3, method='astropy'):
        if self.bkg_mask is None:
            self.set_background_mask()
        for ii in range(self.n_exp):
            x = self[ii][self.bkg_mask[ii]]
            med = np.median(x)
            if method == 'astropy':
                x = sigma_clip(x - med, sigma=clip)
                ix = np.copy(self.bkg_mask[ii])  # original indices to map back into masks
                not_masked = ~x.mask
                self.bkg_mask[ii][ix] *= not_masked
                self.mask[ii][ix] *= not_masked
            else:
                # 1.4826 ensures the estimator corresponds to standard deviation for Gaussian data
                sigma = 1.4826 * np.median(np.abs(x - med))
                ix = self.bkg_mask[ii] * (np.abs(self[ii] - med) > clip * sigma)
                self.bkg_mask[ii][ix] = flag_mask_bad
                self.mask[ii][ix] = flag_mask_bad

    def estimate_dc(self, gradient=True):
        if self.bkg_mask is None:
            self.set_background_mask()
        self.dc = [None] * self.n_exp
        for ii in range(self.n_exp):
            self.dc[ii] = np.median(self[ii][self.bkg_mask[ii]])
            if gradient:
                x, y = np.arange(self[ii].shape[1]), np.arange(self[ii].shape[0])
                xx, yy = np.meshgrid(x, y)
                ix = self.bkg_mask[ii]
                xx_ix, yy_ix = xx[ix].ravel(), yy[ix].ravel()
                X = np.vstack((xx_ix, yy_ix, np.ones(ix.sum()))).T
                p = np.linalg.lstsq(X, (self[ii][yy_ix, xx_ix] - self.dc[ii]).ravel(), rcond=-1)[0]
                self.dc[ii] += p[0] * xx + p[1] * yy + p[2]

    def subtract_dc(self):
        if self.dc is None:
            raise LensMCError('Please set DC.')
        for ii in range(self.n_exp):
            self[ii] -= self.dc[ii]

    def estimate_rms(self, robust=False):
        if self.bkg_mask is None:
            self.set_background_mask()
        self.rms = [None] * self.n_exp
        for ii in range(self.n_exp):
            x = self[ii][self.bkg_mask[ii]]
            if robust:
                # 1.4826 ensures the estimator corresponds to standard deviation for Gaussian data
                self.rms[ii] = 1.4826 * np.median(np.abs(x - np.median(x)))
            else:
                self.rms[ii] = np.std(x)

    def set_weight(self):
        if self.mask is None:
            raise LensMCError('Please set mask.')
        if self.rms is None:
            raise LensMCError('Please set RMS.')
        self.weight = [None] * self.n_exp
        for ii in range(self.n_exp):
            self.weight[ii] = np.empty(self[ii].shape)
            if type(self.rms[ii]) is np.ndarray:
                self.weight[ii][self.mask[ii]] = 1 / self.rms[ii][self.mask[ii]] ** 2
            else:
                self.weight[ii][self.mask[ii]] = 1 / self.rms[ii] ** 2
            self.weight[ii][~self.mask[ii]] = 0
            self.weight[ii] = self.weight[ii].astype(self.dtype)

    def get_astrometry(self, ra, dec, fixed_astrometry=False, grid_size=3):

        if not np.isscalar(ra) or not np.isscalar(dec):
            raise LensMCError('x and y position must be scalars.')

        x, y = self.world2pix(ra, dec)

        # make a square grid of three pixels
        dx = grid_size * np.array([0, 1, 1, 0, -1, -1, -1, 0, 1], dtype=float)
        dy = grid_size * np.array([0, 0, 1, 1, 1, 0, -1, -1, -1], dtype=float)
        X = np.array([dx, dy])

        # define a grid of pixel coordinates around x, y
        # also add the origin to shift coordinates in the WCS reference frame
        x_grid = x + dx[np.newaxis, :]
        y_grid = y + dy[np.newaxis, :]

        # transform to world coordinates
        ra_grid, dec_grid = self.pix2world(x_grid, y_grid)

        # define a WCS object for the (flipped-RA) tangent plane projection at the centre of the grid
        tanw = _get_tan_plane_proj_wcs(ra, dec)

        # Fisher matrix
        F = X @ X.T
        inv_F = np.linalg.inv(F)

        # loop over exposures
        A = [None] * self.n_exp
        pixel_scale = np.empty(self.n_exp)
        for ii in range(self.n_exp):

            # tangent plane projection at the centre of the grid
            U = tanw.wcs_world2pix(ra_grid[ii], dec_grid[ii], 0)

            # measure local distortion matrix
            # from pixels to local tangent projection [arcsec / pixel]
            A[ii] = 3600 * (U @ X.T) @ inv_F

            # get nominal pixel scale
            # (only used for correct change of units in nominal galaxy sizes for fast model generation)
            pixel_scale[ii] = np.sqrt(np.abs(np.linalg.det(A[ii])))

        # assumes the astrometric distortion is fixed across exposures
        # this saves ~2X computational time
        if fixed_astrometry:
            # take the mean distortion from all exposures
            sum_A = np.zeros((2, 2))
            for ee in range(self.n_exp):
                sum_A += A[ee]
            A = [sum_A / self.n_exp] * self.n_exp
            pixel_scale = np.full(self.n_exp, pixel_scale.mean())

        # get registration offsets in pixel units
        x_centre = np.array([self[ii].shape[1] // 2 for ii in range(self.n_exp)])
        y_centre = np.array([self[ii].shape[0] // 2 for ii in range(self.n_exp)])
        x_offset = (x - x_centre[:, np.newaxis]).ravel()
        y_offset = (y - y_centre[:, np.newaxis]).ravel()

        return Astrometry(A, x_offset, y_offset, pixel_scale)

    def plot(self, exp=0, data='image', lim=None, xlim=None, ylim=None, extent=False, vmin='auto', vmax='auto', perc=99,
             nticks=None, nxticks=None, nyticks=None, scale=None, cmap='Greys_r', show=True, newfig=True):

        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import LogNorm
            from matplotlib.ticker import MaxNLocator
        except ModuleNotFoundError:
            logger.error('plot() requires matplotlib. Please install it before calling this method again.')
            return

        attr = 'exp' if data in ('image', 'exp', None) else data
        data = self.__getattribute__(attr)

        if exp >= self.n_exp:
            raise LensMCError(f'Not enough number of exposures to access image with index {exp}.')

        if np.isscalar(data[exp]):
            raise LensMCError(f'Could not plot image. Requested data is the scalar {data[exp]}.')

        if data[exp] is None:
            raise LensMCError('Could not plot image. Requested data is None.')

        if lim is not None:
            xlim = ylim = lim

        if nticks is not None:
            nxticks = nyticks = nticks

        if scale is None or scale == 'lin':
            norm = None
        elif scale == 'log':
            norm = LogNorm()
        else:
            raise LensMCError(f'Scale parameter not understood: {scale}.')

        if vmin == 'auto' and attr not in ('seg', 'mask', 'bkg_mask'):
            vmin = np.nanpercentile(data[exp], 100 - perc)
        else:
            vmin = None
        if vmax == 'auto' and attr not in ('seg', 'mask', 'bkg_mask'):
            vmax = np.nanpercentile(data[exp], perc)
        else:
            vmax = None

        if extent and self.wcs is not None:
            x0, y0 = self.pix2world(-0.5, 0.5)
            x1, y1 = self.pix2world(self[exp].shape[1] + 0.5, self[exp].shape[0] + 0.5)
            extent = (x0, x1, y0, y1)
        else:
            extent = None

        if newfig:
            plt.figure()
        plt.imshow(data[exp], origin='lower', aspect='equal', vmin=vmin, vmax=vmax,
                   extent=extent, norm=norm, cmap=cmap)
        plt.xlim(xlim)
        plt.ylim(ylim)
        ax = plt.gca()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        if nxticks is not None:
            plt.locator_params(axis='x', nbins=nxticks - 1)
        if nyticks is not None:
            plt.locator_params(axis='y', nbins=nyticks - 1)
        plt.minorticks_on()
        fig = plt.gcf()
        if show:
            fig.show()

        return fig

    def shear(self, g1, g2, ra, dec):

        # shear matrix
        # (g1 needs to be flipped in order for affine_transform to work)
        S = np.array([[1 + g1, -g2], [-g2, 1 - g1]])

        # estimate local distortion matrices (for every exposure) at provided position (in units of arcsec/pixel)
        # we want the shear applied in world coordinates
        astrometry = self.get_astrometry(ra, dec)
        A = [astrometry.distortion_matrix[ii] / astrometry.pixel_scale[ii] for ii in range(self.n_exp)]

        # combine shear and astrometric distortion matrices and provide the inverse
        # [ A^-T * S * (A^-1) ]^-1 = A * S^-1 * A^T
        AS = [A[ii] @ S @ A[ii].T for ii in range(self.n_exp)]

        # calculate offset in sheared coordinates
        offset = [None] * self.n_exp
        for ii in range(self.n_exp):
            in_offset = 0.5 * np.array(self[ii].shape)
            offset[ii] = in_offset - AS[ii] @ in_offset

        # calculate sheared exposures
        exps = [affine_transform(self[ii], AS[ii], offset=offset[ii]) for ii in range(self.n_exp)]

        # make a copy of the image and set appropriate attribute
        sheared_image = deepcopy(self)
        sheared_image.exp = exps

        return sheared_image

    def to_hdu_list(self, data='image', transform=None):
        from lensmc import __author__, __email__, __version__, __status__, __copyright__
        pri_hdu = fits.PrimaryHDU()
        pri_hdu.header['AUTHOR'] = __author__
        pri_hdu.header['EMAIL'] = __email__
        pri_hdu.header['VERSION'] = __version__
        pri_hdu.header['STATUS'] = __status__
        pri_hdu.header['CPRGHT'] = __copyright__
        if data == 'image':
            data = 'exp'
        data = self.__getattribute__(data)
        if data is None:
            raise LensMCError(f'\'{data}\' attribute is None.')
        for ii, d in enumerate(data):
            if np.isscalar(d):
                data[ii] = np.full_like(self.exp[ii], data[ii])
        if transform is None:
            def transform(x):
                return x
        if not callable(transform):
            raise LensMCError('\'transform\' must be a callable function.')
        hdu_list = [None] * self.n_exp
        for ii, d in enumerate(data):
            hdr = self.wcs[ii].to_fits()[0].header
            hdu_list[ii] = ImageHDU(transform(d), header=hdr)
        return fits.HDUList([pri_hdu] + hdu_list)

    def to_fits(self, data='image', fname='', transform=None, overwrite=False):
        hdul = self.to_hdu_list(data=data, transform=transform)
        hdul.writeto(fname, overwrite=overwrite)

    def from_fits(self, image, mask=None, seg=None, dc=None, rms=None, wcs=None,
                  exposure_time=None, gain=None, read_noise=None, zero_point=None):
        image = [hdu.data for hdu in fits.open(image) if hdu.data is not None and hdu.data.ndim == 2]
        if mask is not None:
            mask = [hdu.data for hdu in fits.open(mask) if hdu.data is not None and hdu.data.ndim == 2]
        if seg is not None:
            seg = [hdu.data for hdu in fits.open(seg) if hdu.data is not None and hdu.data.ndim == 2]
        if dc is not None:
            dc = [hdu.data for hdu in fits.open(dc) if hdu.data is not None and hdu.data.ndim == 2]
        if rms is not None:
            rms = [hdu.data for hdu in fits.open(rms) if hdu.data is not None and hdu.data.ndim == 2]
        if wcs is not None:
            wcs = [WCS(hdu.header) for hdu in fits.open(image) if hdu.header is not None]
        return self.__init__(image, mask=mask, seg=seg, dc=dc, rms=rms, wcs=wcs,
                             exposure_time=exposure_time, gain=gain, read_noise=read_noise, zero_point=zero_point)

    def to_pickle(self, fname):
        with open(fname, 'wb') as fo:
            pickle.dump(self, fo)

    @staticmethod
    def from_pickle(fname):
        with open(fname, 'rb') as fo:
            data = pickle.load(fo)
        return data


class Astrometry:

    __slots__ = ('distortion_matrix', 'x_offset', 'y_offset', 'pixel_scale')

    def __init__(self, distortion_matrix, x_offset, y_offset, pixel_scale):
        self.distortion_matrix = distortion_matrix
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.pixel_scale = pixel_scale


def extract_postage_stamp(image, x, y, dim=384, return_mask=False, return_corner=False):

    # define constants
    hdim = dim // 2
    ydim, xdim = image.shape

    # calculate coordinates of postage stamp's corners
    # the postage stamp is centred around nominal galaxy position
    x, y = int(np.round(x)), int(np.round(y))
    ix0, ix1 = x - hdim, x + hdim
    iy0, iy1 = y - hdim, y + hdim

    # determine allowable indices for image slice
    ix0_image, ix1_image = max(ix0, 0), min(ix1, xdim)
    iy0_image, iy1_image = max(iy0, 0), min(iy1, ydim)

    # and corresponding indices for postage stamp
    ix0_stamp, ix1_stamp = ix0_image - ix0, dim + ix1_image - ix1
    iy0_stamp, iy1_stamp = iy0_image - iy0, dim + iy1_image - iy1

    # initialise stamp array
    stamp = np.zeros((dim, dim), dtype=image.dtype)

    # set values that are present in the image
    stamp[iy0_stamp:iy1_stamp, ix0_stamp:ix1_stamp] = image[iy0_image:iy1_image, ix0_image:ix1_image]

    # define array to mask out outer regions
    if return_mask:
        mask = stamp != 0

    if return_mask and return_corner:
        return stamp, mask, ix0, iy0
    elif return_mask and not return_corner:
        return stamp, mask
    elif not return_mask and return_corner:
        return stamp, ix0, iy0
    elif not return_mask and not return_corner:
        return stamp


def make(xdim, ydim, e1, e2, s, x, y, flux, bulgefrac,
         psf_disc=None, psf_bulge=None, psf_disc_ft=None, psf_bulge_ft=None,
         pixelavg_ft=None, working_arrays=None,
         rfiducial=rfiducial, odim=odim,
         oversampling=oversampling, cache_file=None, mdim=mdim, n_bulge=1, n_disc=1,
         hl_to_exp=0.15, r50_bulge=None, stamp_dim=384, disc_only=False, is_star=None,
         w=None,
         add_noise=True, poisson_noise=True, exposure_time=565., background_rate=0.225,
         dark_current=0.001, readout_noise=4.5, bias_level=2000., digitalisation=1, gain=3.1,
         seed=None, return_rms_dc=False, return_models=False, dtype=np.float32, fftw_flags=('FFTW_MEASURE',)):
    """
    Make bulge+disc galaxy models on an image of given dimensions.
    Note about pixel convention: the x-axis is along the 2nd array axis, whereas the y-axis is along the 1st array axis.

    :param xdim: Dimension of output image along x
    :type xdim: int
    :param ydim: Dimension of output image along y
    :type ydim: int
    :param e1: First ellipticity components
    :type e1: ndarray
    :param e2: Second ellipticity components
    :type e2: ndarray
    :param s: Galaxy sizes [pixel]
    :type s: ndarray
    :param x: Positions along x [pixel]
    :type x: ndarray
    :param y: Positions along y [pixel]
    :type y: ndarray
    :param flux: Total fluxes
    :type flux: ndarray
    :param bulgefrac: Bulge-to-total ratios
    :type bulgefrac: ndarray
    :param psf_disc: Disc PSFs
    :type psf_disc: tuple of ndarray
    :param psf_bulge:  Bulge PSFs
    :type psf_bulge: tuple of ndarray
    :param pixelavg_ft: Sequence of pre-allocated pixel average Fourier transforms required for the different model array sizes
    :type pixelavg_ft: tuple of ndarray
    :param working_arrays: Dictionary of all working arrays
    :type working_arrays: dict
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
    :param n_bulge: Bulge Sersic index; available: n=(1., 1.5, 2., 2.5, 3., 3.5, 4.)
    :type n_bulge: float
    :param n_disc: Disc Sersic index; available: n=1
    :type n_disc: float
    :param hl_to_exp: Half-ligh-to-exponential-scalength ratio
    :type hl_to_exp: float
    :param stamp_dim: Dimension of square stamp array
    :type stamp_dim: int
    :param disc_only: Whether assume a disc only model
    :type disc_only: bool
    :param w: Astrometric solution
    :type w: astropy.wcs.WCS
    :param dtype: Output model's data type
    :type dtype: type
    :param fftw_flags: FFTW flags; choose ('FFTW_ESTIMATE',) for completely deterministic output;
                       see https://www.fftw.org/faq/section3.html#nondeterministic
    :type fftw_flags: tuple
    :return: Galaxy model on a square array stamp
    :rtype: ndarray
    """

    # check inputs
    e1, e2, s, x, y, flux, bulgefrac = np.atleast_1d(e1, e2, s, x, y, flux, bulgefrac)
    n_bulge = np.atleast_1d(n_bulge)
    if r50_bulge is not None:
        r50_bulge = np.atleast_1d(r50_bulge)
    if is_star is not None:
        is_star = np.atleast_1d(is_star)
    else:
        is_star = np.zeros_like(e1, dtype=bool)
    if type(psf_disc) is np.ndarray:
        psf_disc = [psf_disc] * len(e1)
    if type(psf_bulge) is np.ndarray:
        psf_bulge = [psf_bulge] * len(e1)

    if not (len(e1) == len(e2) == len(s) == len(x) == len(y) == len(flux) == len(bulgefrac)):
        raise LensMCError('All input parameters must have the same length.')

    # define number of galaxies
    n_gal = len(e1)

    # allocate image
    noise_free_image = np.zeros((ydim, xdim))

    # make a linear WCS if not provided
    if w is None:
        w = _get_linear_wcs()

    # check wcs
    x_world, y_world = deepcopy(x), deepcopy(y)
    dummy_image = Image(noise_free_image, wcs=w)
    astrometry = [dummy_image.get_astrometry(x_world[ii], y_world[ii]) for ii in range(n_gal)]
    x, y = dummy_image.world2pix(x_world, y_world)
    x, y = x.ravel(), y.ravel()

    # background noise [count]
    # do not include read noise just now
    background = background_noise(exposure_time=exposure_time, bkg_rate=background_rate,
                                  dark_current=dark_current, read_noise=0)

    # calculate RMS
    # (bkg_rate + dark_current) * exposure_time + read_noise ** 2
    rms = np.sqrt(background + readout_noise ** 2)

    # correct RMS and DC for bias and digitalisation
    quant_var, quant_dc = 1. / 12, 0.5
    dc = float(bias_level)
    if poisson_noise:
        dc += background
    if digitalisation:
        rms /= gain
        dc /= gain
        rms = np.sqrt(rms ** 2 + quant_var)
        dc -= quant_dc

    # render objects that fall within the image
    ix = (x > 0.5) * (x < xdim - 0.5) * (y > 0.5) * (y < ydim - 0.5)
    if ix.sum() > 0:
        x_world = x_world[ix]
        y_world = y_world[ix]
        x = x[ix]
        y = y[ix]
        e1 = e1[ix]
        e2 = e2[ix]
        s = s[ix]
        flux = flux[ix]
        bulgefrac = bulgefrac[ix]
        psf_disc = [psf_disc[ii] for ii, ixx in enumerate(ix) if ixx]
        psf_bulge = [psf_bulge[ii] for ii, ixx in enumerate(ix) if ixx]
        astrometry = [astrometry[ii] for ii, ixx in enumerate(ix) if ixx]
        is_star = is_star[ix]
        n_gal = e1.size
    else:
        zeros = np.zeros((ydim, xdim), dtype=dtype)
        if return_rms_dc and not return_models:
            return zeros, (rms, dc)
        elif return_rms_dc and return_models:
            return zeros, (rms, dc, zeros, [zeros] * n_gal)
        else:
            return zeros

    # allocate working arrays dictionary for fast model generation
    # if variables bulges are required, working arrays will be allocated by the model stamp generator
    if working_arrays is None and n_bulge.size == 1:
        working_arrays = alloc_working_arrays(rfiducial=rfiducial, odim=odim, oversampling=oversampling,
                                              cache_file=cache_file, mdim=mdim, n_bulge=n_bulge, n_disc=n_disc,
                                              dtype=dtype, fftw_flags=fftw_flags)

    # check the PSF
    if psf_disc is None and psf_disc_ft is None:
        odim_max = max(odim)
        psf_disc = np.zeros((odim_max, odim_max), dtype=dtype)
        psf_disc[odim_max // 2, odim_max // 2] = 1.
        psf_disc = (psf_disc, ) * n_gal
    if not disc_only and psf_bulge is None:
        psf_bulge = psf_disc

    if is_star is None:
        is_star = np.zeros((n_gal,), dtype=bool)
    if np.isscalar(is_star):
        is_star = np.atleast_1d(is_star)
    if len(is_star) != n_gal:
        raise LensMCError('is_star should have the same length of the other parameters.')

    # allocate list of models
    if return_models:
        models = [None] * n_gal

    # set the dimension of the postage stamp
    # if the required image is too small for the galaxies being simulated, it will raise an error
    stamp_dim = min(stamp_dim, min(xdim, ydim))
    half_stamp_dim = stamp_dim // 2

    # define centre of stamp in image frame
    xc, yc = np.round(x).astype(int), np.round(y).astype(int)

    # get position offsets wrt to centre of stamp
    # can be positive or negative, but always smaller than half a pixel
    if w is None:
        x0, y0 = x - xc, y - yc
    else:
        # we use a tangent plane projection to calculate the coordinate offsets.
        # note the RA sign is flipped: this is needed because all models are rendered in -ra,dec tangent coordinates
        # alternatives:
        # 1. flat-sky approximation (as the distance between the two positions is less than a pixel)
        #    with a -cos(dec) correction factor
        # 2. use astropy's SkyCoord to calculate angular separation and position angle,
        #    convert that angle to pos->-pos+pi/2 (i.e. from North->East to East->North),
        #    and calculate the offset in RA and DEC
        xc_world, yc_world = dummy_image.pix2world(xc, yc)
        xc_world, yc_world = xc_world.ravel(), yc_world.ravel()
        x0, y0 = np.empty_like(xc_world), np.empty_like(yc_world)
        for ii in range(n_gal):
            tanw = _get_tan_plane_proj_wcs(xc_world[ii], yc_world[ii])
            uc = tanw.wcs_world2pix(xc_world[ii], yc_world[ii], 0)
            u = tanw.wcs_world2pix(x_world[ii], y_world[ii], 0)
            x0[ii] = (u[0] - uc[0]) * 3600
            y0[ii] = (u[1] - uc[1]) * 3600

    # iterate through galaxies
    for iii in range(n_gal):

        # pre-process PSF of disc and bulge
        from lensmc.psf import calculate_psf_ft  # avoid the circular import between image and psf modules
        if psf_disc_ft is None:
            psf_disc_ft_iii = calculate_psf_ft(psf_disc[iii], pixelavg_ft=pixelavg_ft, oversampling=oversampling,
                                               dtype=dtype, fftw_flags=fftw_flags)
        else:
            psf_disc_ft_iii = psf_disc_ft[iii]
        if not disc_only:
            if psf_bulge_ft is None:
                psf_bulge_ft_iii = calculate_psf_ft(psf_bulge[iii], pixelavg_ft=pixelavg_ft, oversampling=oversampling,
                                                    dtype=dtype, fftw_flags=fftw_flags)
            else:
                psf_bulge_ft_iii = psf_bulge_ft[iii]
        else:
            psf_bulge_ft_iii = None

        # take care of variable bulges if necessary
        n_bulge_iii = n_bulge[iii] if n_bulge.size > 1 else n_bulge[0]
        r50_bulge_iii = r50_bulge[iii] if r50_bulge is not None else None

        # make the stamp
        model = make_model_on_stamp(stamp_dim, e1[iii], e2[iii], s[iii], x0[iii], y0[iii], flux[iii], bulgefrac[iii],
                                    psf_disc_ft_iii, psf_bulge_ft=psf_bulge_ft_iii,
                                    working_arrays=working_arrays,
                                    rfiducial=rfiducial, odim=odim,
                                    oversampling=oversampling, cache_file=cache_file, mdim=mdim,
                                    n_bulge=n_bulge_iii, n_disc=n_disc,
                                    hl_to_exp=hl_to_exp, r50_bulge=r50_bulge_iii,
                                    disc_only=disc_only, is_star=is_star[iii],
                                    astrometry=astrometry[iii], dtype=dtype, fftw_flags=fftw_flags)

        # get nominal (left and right) stamp array corners in the image frame
        ii0, ii1 = yc[iii] - half_stamp_dim, yc[iii] + half_stamp_dim
        jj0, jj1 = xc[iii] - half_stamp_dim, xc[iii] + half_stamp_dim

        # define (left and right) stamp array corners and deal with edge effects
        mdl_ii0, mdl_ii1 = 0, stamp_dim
        mdl_jj0, mdl_jj1 = 0, stamp_dim
        if ii0 < 0:
            mdl_ii0 = abs(ii0)
            ii0 = 0
        if jj0 < 0:
            mdl_jj0 = abs(jj0)
            jj0 = 0
        if ii1 > ydim:
            mdl_ii1 = stamp_dim - (ii1 - ydim)
            ii1 = ydim
        if jj1 > xdim:
            mdl_jj1 = stamp_dim - (jj1 - xdim)
            jj1 = xdim

        # add up model to image at the right coordinates
        noise_free_image[ii0: ii1, jj0: jj1] += model[mdl_ii0: mdl_ii1, mdl_jj0: mdl_jj1]

        # save individual models
        if return_models:
            models[iii] = model.copy()

    # add pixel noise if required
    if add_noise:

        # initialise the RNG
        rng = np.random.default_rng(seed)

        # add noise, including read noise
        if poisson_noise:
            poisson_mean = background + noise_free_image
            image = rng.poisson(poisson_mean, size=(ydim, xdim)) + readout_noise * rng.standard_normal((ydim, xdim))
        else:
            image = noise_free_image + rms * rng.standard_normal((ydim, xdim))

    else:
        image = noise_free_image.copy()

    # apply bias and digitalisation
    if bias_level > 0:
        image += bias_level
        if poisson_noise:
            ix = image < 0
            if ix.any():
                image[ix] = 0
    if digitalisation:
        image /= gain
        image = np.trunc(image)
        noise_free_image /= gain
        if return_models:
            models = [models[ii] / gain for ii in range(n_gal)]

    # cast to output data type
    image = image.astype(dtype)

    if return_rms_dc and not return_models:
        return image, (rms, dc)
    elif return_rms_dc and return_models:
        return image, (rms, dc, noise_free_image, models)
    else:
        return image


def make_model_on_stamp(dim, e1, e2, s, x0, y0, flux, bulgefrac, psf_disc_ft=None, psf_bulge_ft=None, working_arrays=None,
                        rfiducial=rfiducial, odim=odim,
                        oversampling=oversampling, cache_file=None, mdim=mdim, n_bulge=1, n_disc=1,
                        hl_to_exp=0.15, r50_bulge=None, disc_only=False, is_star=False,
                        astrometry=None, dtype=np.float32, fftw_flags=('FFTW_MEASURE',)):
    """
    Make a bulge+disc galaxy model on a square image stamp.

    :param dim: Dimension of output model array
    :type dim: int
    :param e1: First ellipticity component
    :type e1: float
    :param e2: Second ellipticity component
    :type e2: float
    :param s: Galaxy size [pixel]
    :type s: float
    :param x0: Position x offset wrt to the centre of the array [pixel]
    :type x0: float
    :param y0: Position x offset wrt to the centre of the array [pixel]
    :type y0: float
    :param flux: Total flux
    :type flux: float
    :param bulgefrac: Bulge-to-total ratio
    :type bulgefrac: float
    :param psf_disc_ft: Disc PSF for different array sizes
    :type psf_disc_ft: tuple of ndarray
    :param psf_bulge_ft:  Bulge PSF for different array sizes
    :type psf_bulge_ft: tuple of ndarray
    :param working_arrays: Dictionary of all working arrays
    :type working_arrays: dict
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
    :param n_bulge: Bulge Sersic index; available: n=(1., 1.5, 2., 2.5, 3., 3.5, 4.)
    :type n_bulge: float
    :param n_disc: Disc Sersic index; available: n=1
    :type n_disc: float
    :param hl_to_exp: Half-ligh-to-exponential-scalength ratio
    :type hl_to_exp: float
    :param disc_only: Whether assume a disc only model
    :type disc_only: bool
    :param dtype: Output model's data type
    :type dtype: type
    :param fftw_flags: FFTW flags; choose ('FFTW_ESTIMATE',) for completely deterministic output;
                       see https://www.fftw.org/faq/section3.html#nondeterministic
    :type fftw_flags: tuple
    :return: Galaxy model on a square array stamp
    :rtype: ndarray
    """

    if np.sqrt(e1 ** 2 + e2 ** 2) < 0 or np.sqrt(e1 ** 2 + e2 ** 2) >= 1 or \
            s < 0 or flux < 0 or bulgefrac < 0 or bulgefrac > 1:
        raise LensMCError('Out of galaxy parameter bounds.')

    if working_arrays is None:
        working_arrays = alloc_working_arrays(n_bulge, n_disc, rfiducial=rfiducial, odim=odim,
                                              oversampling=oversampling, cache_file=cache_file, mdim=mdim, dtype=dtype,
                                              fftw_flags=fftw_flags)
    if oversampling != working_arrays.oversampling:
        raise LensMCError('working_arrays does not match oversampling.')
    bulge_ht = working_arrays.bulge_ht
    disc_ht = working_arrays.disc_ht

    # total model
    model = np.zeros((dim, dim), dtype=dtype)

    if not is_star:

        # disc model
        disc = generate_galaxy_model(e1, e2, s, x0, y0, disc_ht, psf_disc_ft, working_arrays,
                                     astrometric_distortion=astrometry.distortion_matrix[0],
                                     pixel_scale=astrometry.pixel_scale[0], odim_min=192)
        disc *= flux * (1 - bulgefrac)

        # add disc model
        disc_size = disc.shape[0]
        ix0, ix1 = (dim - disc_size) // 2, (dim + disc_size) // 2
        if ix0 >= 0 and ix1 <= dim:
            model[ix0:ix1, ix0:ix1] += disc
        else:
            raise LensMCError('Increase model array dimension.')

        # bulge model
        # note that the templates already contain the correct size definition (Peng relation)
        if not disc_only:
            if r50_bulge is None:
                r50_bulge = hl_to_exp * s
            bulge = generate_galaxy_model(e1, e2, r50_bulge, x0, y0, bulge_ht, psf_bulge_ft, working_arrays,
                                          astrometric_distortion=astrometry.distortion_matrix[0],
                                          pixel_scale=astrometry.pixel_scale[0], odim_min=192)
            bulge *= flux * bulgefrac

            # add bulge model
            bulge_size = bulge.shape[0]
            ix0, ix1 = (dim - bulge_size) // 2, (dim + bulge_size) // 2
            model[ix0:ix1, ix0:ix1] += bulge

    else:

        # star model
        star = generate_star_model(x0, y0, psf_disc_ft, working_arrays,
                                   astrometric_distortion=astrometry.distortion_matrix[0], odim_min=192)
        star *= flux

        # add star model
        star_size = star.shape[0]
        ix0, ix1 = (dim - star_size) // 2, (dim + star_size) // 2
        if ix0 >= 0 and ix1 <= dim:
            model[ix0:ix1, ix0:ix1] += star
        else:
            raise LensMCError('Increase model array dimension.')

    return model


def _drop(target, indices):
    if isinstance(target, list):
        return [i for j, i in enumerate(target) if j not in indices]
    elif isinstance(target, np.ndarray):
        return np.delete(target, indices)
    elif target is None:
        return target
    else:
        raise LensMCError('Target must be list, ndarray or None.')


def _get_linear_wcs():
    wcs = WCS(naxis=2)
    wcs.wcs.ctype = ['LINEAR', 'LINEAR']
    wcs.wcs.crpix = [1., 1.]
    wcs.wcs.cdelt = [1., 1.]
    return wcs


def _get_tan_plane_proj_wcs(ra, dec, flip_ra=True):
    wcs = WCS(naxis=2)
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    wcs.wcs.crval = [ra, dec]
    wcs.wcs.crpix = [1., 1.]  # FITS convention
    wcs.wcs.cdelt = [(-1.) ** flip_ra, 1.]  # project onto flipped RA coordinate
    return wcs
