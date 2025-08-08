"""
LensMC - a Python package for weak lensing shear measurements.
Module implementing segmentation utility functions for lensmc.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from copy import deepcopy
from scipy.ndimage import gaussian_filter, binary_dilation, label

from lensmc.flags import flag_seg_false, flag_seg_masked, flag_seg_unassigned
from lensmc.utils import LensMCError


def make_obj_detection(image, sigma=1., truncate=4., threshold=4., dc=True, mask=None):
    """
    Make an object detection map through Gaussian filtering and rms thresholding.
    Optional (bool) mask: 1 for good pixel, 0 otherwise.
    Detection (bool) map: 1 for a detection, 0 otherwise.

    :type image: ndarray
    :type sigma: float
    :type truncate: float
    :type threshold: float
    :type dc: bool
    :type mask: ndarray
    :rtype: ndarray
    """

    # whether we subtract the DC offset
    image = deepcopy(image)
    if dc:
        if mask is not None:
            image[mask] -= np.median(image[mask])
        else:
            image -= np.median(image)

    # smooth with a truncated gaussian filter
    image_flt = gaussian_filter(image, sigma, order=0, mode='constant', cval=0., truncate=truncate)

    # estimate robust rms through mean absolute deviation
    image_flt = np.abs(image_flt)
    # rms = np.median(image_flt) / 0.67449
    if mask is not None:
        rms = np.median(image_flt[mask])
    else:
        rms = np.median(image_flt)
    rms /= 0.67449

    # define pixel belonging to an object as 1, otherwise set it to 0
    detection = np.empty(image_flt.shape, dtype=bool)
    ix = image_flt > threshold * rms
    detection[ix] = 1
    detection[~ix] = 0

    # combine with provided mask
    if mask is not None:
        detection += ~ mask

    return detection


def make_obj_segm(image, id, x, y, sigma=1., truncate=4., threshold=4., mask=None, deblend=False, dtype=np.int32):
    """
    Make an object segmentation map via catalogue matching, and optionally de-blend the map.
    Also returns a list of blends by object IDs.
    Algorithm:
    1. Make a (bool) detection map (1 for detection, 0 otherwise) via detection_map().
    2. Cross-match with catalogue entries, and associate detections with object IDs.
    3. (Optional) Make a list of blended objects.
    3. (Optional) Deblend neighbouring objects.
    Optional (bool) mask: 1 for good pixel, 0 otherwise.
    Segmentation map: ID for matched detection, -2 for spurious unmatched detections, -1 otherwise.

    :type image: ndarray
    :type sigma: float
    :type truncate: float
    :type threshold: float
    :type id: ndarray
    :type x: ndarray
    :type y: ndarray
    :type mask: ndarray
    :type deblend: bool
    :type dtype: dtype
    :rtype: ndarray or tuple
    """

    if np.isscalar(id):
        id = [id]
        x = [x]
        y = [y]
    assert len(id) == len(x) == len(y)

    # define number of catalogue objects
    n_objs = len(id)

    # make detection map
    # will be the segmentation map later on
    det_map = make_obj_detection(image, sigma=sigma, truncate=truncate, threshold=threshold, mask=mask)

    # get array indices from rounded catalogue positions
    # but avoid edges
    xr, yr = np.round(x).astype(int), np.round(y).astype(int)
    xr[xr < 0] = 0
    yr[yr < 0] = 0
    xr[xr >= image.shape[1]] = image.shape[1] - 1
    yr[yr >= image.shape[0]] = image.shape[0] - 1

    # merge with provided detections
    det_map[yr, xr] = 1

    # define structuring element for dilation and labelling
    s = np.ones((3, 3), dtype=dtype)

    # apply dilation
    det_map = binary_dilation(det_map, structure=s)

    # set data type to provided one (integer as a default)
    det_map = det_map.astype(dtype)

    # label detection map
    label_map, n_features = label(det_map, structure=s)

    # cross match labelled detections with catalogue entries
    # 1) loop through the labelled features identified in the labelled detection map
    # 2) scan through catalogue entries and try to match positions
    # 3) if matched, associate segmentation map with that ID
    # 4) otherwise define it as a spurious detection (flag_seg_false)
    segm_map = np.full_like(det_map, flag_seg_masked)
    segm_map[det_map == 1] = flag_seg_false   # presume all detections are unmatched, before matching with catalogue
    segm_map[det_map == 0] = flag_seg_unassigned
    for jjj in range(n_objs):
        # get array indices from catalogue positions
        jj, ii = xr[jjj], yr[jjj]
        # check if it hasn't been matched already, if not check whether it does now
        if label_map[ii, jj] > 0:
            segm_map[label_map == label_map[ii, jj]] = id[jjj]
        else:
            segm_map[ii, jj] = id[jjj]

    # now try to make a list of blends
    # 1) scan again through catalogue entries
    # 2) go back checking the segmentation map
    # 3) if IDs don't match, both objects are classified as 'blended'
    # 4) make a list of blended objects in pairs
    # 5) merge pairs to clusters if required
    # 6) now deblend: assign individual pixels in blended objects to individual objects
    blends = []
    for jjj in range(n_objs):
        # get array indices from catalogue positions
        jj, ii = xr[jjj], yr[jjj]
        # check segmentation map
        segm_id = segm_map[ii, jj]
        if segm_id != id[jjj] and segm_id >= 0 and id[jjj] > 0:
            blends += [[segm_id, id[jjj]]]

    # cluster blend pairs together, if required
    for ii in range(len(blends)):
        for jj in range(ii + 1, len(blends)):
            for bb in blends[ii]:
                for bbb in blends[jj]:
                    if bb == bbb:
                        # join blends
                        joined_blends = blends[ii] + blends[jj]
                        # cluster together (uniquely)
                        blends[ii] = [*{*joined_blends}]
                        blends[jj] = []
    blends = [x for x in blends if x != []]

    # sort blends such that the first object in every cluster is classified as the "parent"
    # parent is the object that identifies the whole cluster with its ID
    n_blends = len(blends)
    parents = [None] * n_blends
    for bb in range(n_blends):
        for iii in blends[bb]:
            if np.sum(segm_map == iii) > 0:
                parents[bb] = iii
    # sort the list of blends such that the parent is always the first element
    for bb in range(n_blends):
        blends[bb].remove(parents[bb])
        blends[bb] = [parents[bb]] + blends[bb]

    # try to deblend
    if deblend:
        for bb in blends:
            # identify "parent" and "children"
            # this is just nominal as it has nothing to do with the object itself
            parent = -1
            children = []
            for iii in bb:
                if np.sum(segm_map == iii) > 0:
                    parent = iii
                else:
                    children.append(iii)
            # get object positions and calculate distance weights based on central flux
            n_blended_objs = len(bb)
            jj, ii = [None] * n_blended_objs, [None] * n_blended_objs
            # w = [None] * n_blended_objs
            for cc in range(n_blended_objs):
                jj[cc], ii[cc] = xr[id == bb[cc]], yr[id == bb[cc]]
                # w[cc] = image[ii[cc], jj[cc]]
            # get coordinates of blended objects
            ix, iy = np.where(segm_map == parent)
            # compute weighted squared distance from pixel to individual objects
            for iiii in range(len(ix)):
                d = np.zeros((n_blended_objs,))
                for cc in range(n_blended_objs):
                    d[cc] = (ix[iiii] - ii[cc]) ** 2 + (iy[iiii] - jj[cc]) ** 2
                    # d[cc] = w[cc] * ((ix[iiii] - ii[cc]) ** 2 + (iy[iiii] - jj[cc]) ** 2)
                # make a decision based on minimum distance to object
                mm = np.argmin(d)
                segm_map[ix[iiii], iy[iiii]] = bb[mm]

    # scan catalogue entries and check segmentation at central pixel for missed detections
    flat_blends = [item for sublist in blends for item in sublist]
    for jjj in range(n_objs):
        # get array indices from catalogue positions if not a blended object
        if id[jjj] not in flat_blends:
            jj, ii = xr[jjj], yr[jjj]
            if segm_map[ii, jj] != id[jjj]:
                segm_map[ii, jj] = id[jjj]

    # combine with provided mask
    if mask is not None:
        segm_map[~mask] = flag_seg_masked

    return segm_map, blends


def make_image_segm(segm_map, id, x, y, r=200, blends=None, mask=None):
    """
    Make an image segmentation map as Voronoi tesselation from an input object segmentation map and objects catalogue.
    Optional list of clustered blended objects by their IDs.
    Optional (bool) mask: 1 for good pixel, 0 otherwise.
    Segmentation map: ID for matched cell, -2 for spurious unmatched detections, -1 otherwise.

    :type segm_map: ndarray
    :type id: ndarray
    :type x: ndarray
    :type y: ndarray
    :type r: float
    :type blends: list of list
    :type mask: ndarray
    :rtype: ndarray
    """

    assert len(id) == len(x) == len(y) > 0

    # define number of catalogue objects
    n_objs = len(id)

    # whether we check for blends
    check_blends = bool(blends)

    # flatten input blends list for quick check
    if check_blends:
        flat_blends = [item for sublist in blends for item in sublist]
    else:
        flat_blends = blends

    # estimate distance weights based on input segmentation map
    w = np.empty((n_objs,))
    for ii in range(n_objs):
        # count number of pixels associated to object ID
        n_px = np.sum(segm_map == id[ii])
        # if zero pixels are found, look at whether it's actually blended
        if n_px == 0 and check_blends:
            if id[ii] in flat_blends:
                for bb in range(len(blends)):
                    if id[ii] in blends[bb]:
                        n_px = np.sum(segm_map == blends[bb][0])
                        break
            else:
                raise LensMCError('Problem with input segmentation map. Object ID not found.')
        w[ii] = 1. / n_px

    # make a circular mask around every nominal position
    # r should allow room for the biggest galaxies (e.g. 2" x 4.5 x 2 x 0.1"/px)
    r2 = 2 * r + 1
    sy, sx = segm_map.shape
    yc, xc = np.ogrid[-r: r + 1, -r: r + 1]
    csmallmask = xc ** 2 + yc ** 2 < r ** 2
    cmask = np.zeros_like(segm_map, dtype=bool)
    for ii in range(n_objs):
        xr, yr = int(round(x[ii])), int(round(y[ii]))
        xr_m, xr_p = xr - r, xr + r + 1
        yr_m, yr_p = yr - r, yr + r + 1
        xx0, xx1 = max(xr_m, 0), min(xr_p, sx)
        yy0, yy1 = max(yr_m, 0), min(yr_p, sy)
        xxx0, xxx1 = 0, r2
        yyy0, yyy1 = 0, r2
        if xr_m < 0:
            xxx0 += abs(xr_m)
        if yr_m < 0:
            yyy0 += abs(yr_m)
        if xr_p > sx:
            xxx1 -= xr_p - sx
        if yr_p > sy:
            yyy1 -= yr_p - sy
        cmask[yy0:yy1, xx0:xx1] = cmask[yy0:yy1, xx0:xx1] + csmallmask[yyy0:yyy1, xxx0:xxx1]

    # iterate over pixels in the mask defined above and associate pixels to catalogue objects
    img_segm_map = np.copy(segm_map)
    for yy in range(img_segm_map.shape[0]):
        for xx in range(img_segm_map.shape[1]):
            if cmask[yy, xx] and segm_map[yy, xx] == -1:
                # compute distances to reference position
                d = w * ((xx - x) ** 2 + (yy - y) ** 2)
                # find the minimum distance
                ix = np.argmin(d)
                # assign to object
                if not id[ix] in flat_blends:
                    img_segm_map[yy, xx] = id[ix]
                else:
                    for bb in range(len(blends)):
                        if id[ix] in blends[bb]:
                            img_segm_map[yy, xx] = blends[bb][0]
                            break

    # combine with provided mask
    if mask is not None:
        img_segm_map[~mask] = -2

    return img_segm_map
