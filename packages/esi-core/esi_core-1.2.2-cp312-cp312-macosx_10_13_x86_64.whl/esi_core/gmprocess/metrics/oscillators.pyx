#cython: language_level=3
# third party imports
import numpy as np
from numpy cimport ndarray
cimport numpy as np
cimport cython


cdef extern from "cfuncs.h":
    void calculate_spectrals_c(double *acc, int npoints, double dt,
                               double period, double damping, double *sacc,
                               double *svel, double *sdis);

cpdef list calculate_spectrals(data, new_np, new_dt, new_sample_rate, period, damping):
    """
    Returns a list of spectral responses for acceleration, velocity,
            and displacement.
    Args:
        data (ndarray):
            Acceleration data array.
        new_np (int):
            New number of points.
        new_dt (float):
            New delta t.
        new_sample_rate (float):
            New sample rate.
        period (float):
            Period in seconds.
        damping (float):
            Fraction of critical damping.
    Returns:
        list: List of spectral responses (np.ndarray).
    """

    cdef ndarray[double, ndim=1] spectral_acc = np.zeros(new_np)
    cdef ndarray[double, ndim=1] spectral_vel = np.zeros(new_np)
    cdef ndarray[double, ndim=1] spectral_dis = np.zeros(new_np)
    cdef ndarray[double, ndim=1] acc = data

    calculate_spectrals_c(<double *>acc.data, new_np, new_dt,
                          period, damping,
                          <double *>spectral_acc.data,
                          <double *>spectral_vel.data,
                          <double *>spectral_dis.data)
    return [spectral_acc, spectral_vel, spectral_dis, new_np, new_dt, new_sample_rate]


