#cython: language_level=3
import numpy as np
cimport cython
#from cython.parallel import prange
from libc.math cimport (sqrt,
                        cos,
                        sin,
                        asin,
                        exp)

@cython.boundscheck(False)
@cython.wraparound(False)
def make_sigma_matrix(double[:, ::1]corr12, double[:]sdsta, double[:]sdarr):
    cdef Py_ssize_t ny = corr12.shape[0]
    cdef Py_ssize_t nx = corr12.shape[1]

    cdef double *c12p
    cdef double sdval
    cdef double tmp
    cdef Py_ssize_t x, y

    #for y in range(ny, nogil=True, schedule=dynamic):
    for y in range(ny):
        c12p = &corr12[y, 0]
        sdval = sdarr[y]
        for x in range(nx):
            # Putting these operations all on one line seems to
            # allow the compiler to do things that result in the
            # output matrix being very slightly asymmetric.
            tmp = sdsta[x] * sdval
            c12p[x] = c12p[x] * tmp
    return


@cython.boundscheck(False)
@cython.wraparound(False)
def eval_lb_correlation(double[:, ::1]b1, double[:, ::1]b2, double[:, ::1]b3,
                        long[:, ::1]ix1, long[:, ::1]ix2, double[:, ::1]h):
    cdef Py_ssize_t nx = ix1.shape[1]
    cdef Py_ssize_t ny = ix1.shape[0]

    cdef Py_ssize_t x, y, i, j
    cdef double hval
    cdef long *ix1p
    cdef long *ix2p
    cdef double *hp
    cdef double afact = -3.0 / 20.0
    cdef double bfact = -3.0 / 70.0

    #for y in range(ny, nogil=True, schedule=dynamic):
    for y in range(ny):
        hp = &h[y, 0]
        ix1p = &ix1[y, 0]
        ix2p = &ix2[y, 0]
        for x in range(nx):
            hval = hp[x]
            i = ix1p[x]
            j = ix2p[x]
            hp[x] = (b1[i, j] * exp(hval * afact) +
                     b2[i, j] * exp(hval * bfact))
            if hval == 0:
                hp[x] += b3[i, j]

    return h


@cython.boundscheck(False)
@cython.wraparound(False)
def make_sd_array(double[:, ::1]sdgrid, double[:, ::1]pout_sd2, long iy,
                  double[:, ::1]rcmatrix, double[:, ::1]sigma12):
    cdef Py_ssize_t nx = rcmatrix.shape[1]
    cdef Py_ssize_t ny = rcmatrix.shape[0]

    cdef double tmp
    cdef double *sdg = &sdgrid[iy, 0]
    cdef double *pop = &pout_sd2[iy, 0]
    cdef double *rcp
    cdef double *sgp
    cdef Py_ssize_t x, y

    #for y in range(ny, nogil=True):
    for y in range(ny):
        rcp = &rcmatrix[y, 0]
        sgp = &sigma12[y, 0]
        tmp = 0
        for x in range(nx):
            tmp = tmp + rcp[x] * sgp[x]
        sdg[y] = pop[y] - tmp
        if sdg[y] < 0:
            sdg[y] = 0
        # sdg[y] = sqrt(sdg[y])
    return
