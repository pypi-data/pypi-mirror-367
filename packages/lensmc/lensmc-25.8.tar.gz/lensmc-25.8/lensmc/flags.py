"""
Lensmc - a Python package for weak lensing shear measurements.
Module for flag definition for lensmc.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from collections import defaultdict


n_bits = 20

flag_galaxy = 0
flag_star = 2 ** 0
flag_unknown = 2 ** 1
flag_blended = 2 ** 2
flag_bad_residuals = 2 ** 3
flag_undetected = 2 ** 4
flag_insufficient_data = 2 ** 5
flag_corrupt_data = 2 ** 6

flag_failure = 2 ** n_bits

flag_to_str_dict = defaultdict(lambda: '')
flag_to_str_dict[flag_galaxy] = 'Galaxy'
flag_to_str_dict[flag_star] = 'Star'
flag_to_str_dict[flag_unknown] = 'Unknown'
flag_to_str_dict[flag_blended] = 'Blended'
flag_to_str_dict[flag_bad_residuals] = 'Bad residuals'
flag_to_str_dict[flag_undetected] = 'Undetected'
flag_to_str_dict[flag_insufficient_data] = 'Insufficient data'
flag_to_str_dict[flag_corrupt_data] = 'Corrupted data'
flag_to_str_dict[flag_failure] = 'Failure'

# values of the segmentation map for unassigned pixels, false detections, or masked pixels
# any value > 0 is a detection
flag_seg_unassigned = 0
flag_seg_false = -1
flag_seg_masked = -2

# values for the binary mask
# 1 is good
flag_mask_bad = 0


def int2flags(n):
    if n == 0:
        return [0]
    flags = []
    while n > 0:
        nearpow2 = 2 ** int(np.log2(n))
        flags += [nearpow2]
        n = n % nearpow2
    return flags


def flags2str(flags):
    return [flag_to_str_dict[f] for f in flags]


def int2str(n):
    flags = int2flags(n)
    return flags2str(flags)
