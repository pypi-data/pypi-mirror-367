import cython
cimport numpy as np


# The kernel that does the calculation (double precision version)
@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
cdef np.float64_t _cross_prod_double(np.float64_t[:, ::1] a, np.float64_t[:, ::1] b, int ix0, int ix1):
    cdef np.float64_t p
    cdef int i, j
    p = 0.
    cdef int ix10 = ix1 - ix0
    for i in range(ix10):
        for j in range(ix10):
            p += a[i + ix0, j + ix0] * b[i,j]
    return p


# The kernel that does the calculation (float version)
@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
cdef np.float32_t _cross_prod_float(np.float32_t[:, ::1] a, np.float32_t[:, ::1] b, int ix0, int ix1):
    cdef np.float32_t p
    cdef int i, j
    p = 0.
    cdef int ix10 = ix1 - ix0
    for i in range(ix10):
        for j in range(ix10):
            p += a[i + ix0, j + ix0] * b[i, j]
    return p


# Entry point into cross_product (double precision version)
def cross_product_double(list a, list b):
    cdef int a_size, b_size
    a_size = a[0].shape[0]
    b_size = b[0].shape[0]

    cdef int ix0, ix1
    ix0 = (a_size - b_size) // 2
    ix1 = (a_size + b_size) // 2
    cdef int n = len(a)
    cdef np.float64_t p = 0.

    cdef int ii
    if ix0 < 0:
        ix0 *= -1
        a, b = b, a
    for ii in range(n):
        p += _cross_prod_double(a[ii], b[ii], ix0, ix1)

    return p


# Entry point into cross_product (float version)
def cross_product_float(list a, list b):
    cdef int a_size, b_size
    a_size = a[0].shape[0]
    b_size = b[0].shape[0]

    cdef int ix0, ix1
    ix0 = (a_size - b_size) // 2
    ix1 = (a_size + b_size) // 2
    cdef int n = len(a)
    cdef np.float32_t p = 0.

    cdef int ii
    if ix0 < 0:
        ix0 *= -1
        a, b = b, a
    for ii in range(n):
        p += _cross_prod_float(a[ii], b[ii], ix0, ix1)

    return p
