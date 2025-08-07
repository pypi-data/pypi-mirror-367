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
def geodetic_distance_fast(double[::1]lons1, double[::1]lats1,
                           double[::1]lons2, double[::1]lats2,
                           double[:, ::1]result):
    cdef double EARTH_RADIUS = 6371.
    cdef Py_ssize_t nx = lons1.shape[0]
    cdef Py_ssize_t ny = lons2.shape[0]

    cdef double lon2, lat2
    cdef double *res
    cdef Py_ssize_t x, y

    if &lons1[0] == &lons2[0] and &lats1[0] == &lats2[0]:
        #for y in range(ny, nogil=True, schedule='guided'):
        for y in range(ny):
            lon2 = lons2[y]
            lat2 = lats2[y]
            for x in range(y+1):
                result[y, x] = result[x, y] = (
                    EARTH_RADIUS *
                    sqrt(((lons1[x] - lon2) *
                        cos(0.5 * (lats1[x] + lat2)))**2 +
                        (lats1[x] - lat2)**2))
    else:
        #for y in range(ny, nogil=True, schedule=dynamic):
        for y in range(ny):
            res = &result[y, 0]
            lon2 = lons2[y]
            lat2 = lats2[y]
            for x in range(nx):
                res[x] = (
                    EARTH_RADIUS *
                    sqrt(((lons1[x] - lon2) *
                        cos(0.5 * (lats1[x] + lat2)))**2 +
                        (lats1[x] - lat2)**2))
    return


@cython.boundscheck(False)
@cython.wraparound(False)
def geodetic_distance_haversine(double[::1]lons1, double[::1]lats1,
                                double[::1]lons2, double[::1]lats2,
                                double[:, ::1]result):
    cdef double EARTH_RADIUS = 6371.
    cdef Py_ssize_t nx = lons1.shape[0]
    cdef Py_ssize_t ny = lons2.shape[0]

    cdef Py_ssize_t x, y
    cdef double diameter = 2.0 * EARTH_RADIUS

    if &lons1[0] == &lons2[0] and &lats1[0] == &lats2[0]:
        #for y in range(ny, nogil=True, schedule='guided'):
        for y in range(ny):
            for x in range(y+1):
                result[y, x] = result[x, y] = (
                    diameter * asin(sqrt(
                        sin((lats1[x] - lats2[y]) / 2.0)**2 +
                        cos(lats1[x]) * cos(lats2[y]) *
                        sin((lons1[x] - lons2[y]) / 2.0)**2)))
    else:
        #for y in range(ny, nogil=True, schedule=dynamic):
        for y in range(ny):
            for x in range(nx):
                result[y, x] = (
                    diameter * asin(sqrt(
                        sin((lats1[x] - lats2[y]) / 2.0)**2 +
                        cos(lats1[x]) * cos(lats2[y]) *
                        sin((lons1[x] - lons2[y]) / 2.0)**2)))
    return

