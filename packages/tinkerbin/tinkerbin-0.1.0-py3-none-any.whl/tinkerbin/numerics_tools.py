#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tools for numerical integrations, Fourier transforms, etc.
"""

################################### Import #####################################
# ---- Internal ---------------
import numpy as np
import numpy.typing
from typing import Optional, Callable

# ---- Custom -----------------
from .attr_class import AttrClass


################################### Math functions #############################


def linear_ramp_func(x_onset: float) -> Callable[[np.ndarray], np.ndarray]:
    """
    Linear ramp function.

    Args:
        x_onset: Point where ramp reaches 1

    Returns:
        Lambda function that applies linear ramp: 0 for x<0, x/x_onset for 0<=x<x_onset, 1 for x>=x_onset
    """
    return lambda x: np.where(x < 0, 0, np.where(x >= x_onset, 1, x / x_onset))


def bump_func_func(x_onset: float) -> Callable[[np.ndarray], np.ndarray]:
    """
    Bump function ramp.

    Args:
        x_onset: Point where bump function reaches 1

    Returns:
        Lambda function that applies smooth bump function transition
    """
    return lambda x: np.where(
        x < 0,
        0,
        np.where(x >= x_onset, 1, np.exp(1 - x_onset**2 / (x * (2 * x_onset - x)))),
    )


################################### Numerical integration ######################


class Discretization(AttrClass, internal_attrs=['var_name']):
    """
    Discretization class for numerical computations.

    Stores discretization parameters for a variable including linear array,
    bounds, step size, and zero positions.
    """

    var_name: str
    x_lin: numpy.typing.NDArray
    N_x: int
    x_min: float
    x_max: float
    dx: float
    x_0pos: float
    x_0neg: float

    def __init__(
        self,
        x_lin: numpy.typing.NDArray,
        N_x: int,
        x_min: float,
        x_max: float,
        dx: float,
        x_0pos: float,
        x_0neg: float,
        var_name: str = 'x',
    ) -> None:
        """
        Initialize discretization.

        Args:
            x_lin: Linear array of discretized values
            N_x: Number of discretization points
            x_min: Minimum value
            x_max: Maximum value
            dx: Step size
            x_0pos: Positive zero position
            x_0neg: Negative zero position
            var_name: Name of the variable being discretized
        """
        (
            self.x_lin,
            self.N_x,
            self.x_min,
            self.x_max,
            self.dx,
            self.x_0pos,
            self.x_0neg,
            self.var_name,
        ) = x_lin, N_x, x_min, x_max, dx, x_0pos, x_0neg, var_name

    def param_dic(self) -> dict[str, any]:
        """
        Get parameter dictionary with variable-specific naming.

        Returns:
            Dictionary of parameters with variable name substituted in keys
        """
        param_dic = {}
        for attr_name, attr_val in self.to_dic().items():
            if attr_name != 'x_lin':
                sub_attr_name = attr_name.replace('x_', self.var_name + '_')
                sub_attr_name = sub_attr_name.replace('_x', '_' + self.var_name)
                sub_attr_name = sub_attr_name.replace('dx', 'd' + self.var_name)
                param_dic[sub_attr_name] = attr_val
        return param_dic


def discretize_func(
    func: Callable[[numpy.typing.NDArray], numpy.typing.NDArray], disc: Discretization
) -> numpy.typing.NDArray:
    """
    Compute function over discretization array.

    Args:
        func: Function to evaluate
        disc: Discretization object

    Returns:
        Function evaluated over the discretization array
    """
    return func(disc.x_lin)


def integral_inner(
    f1: numpy.typing.NDArray,
    f2: numpy.typing.NDArray,
    disc: Discretization,
    x_lower: Optional[float] = None,
    x_upper: Optional[float] = None,
) -> complex:
    """
    Numerical integral inner product, without complex conjugation over specified range.

    Args:
        f1: First function array
        f2: Second function array
        disc: Discretization object
        x_lower: Lower integration bound (default: x_min)
        x_upper: Upper integration bound (default: x_max)

    Returns:
        Inner product integral
    """
    x_lin, x_min, x_max, dx = disc.x_lin, disc.x_min, disc.x_max, disc.dx

    if x_lower is None:
        x_lower = x_min
    if x_upper is None:
        x_upper = x_max

    mask = np.bitwise_and(x_lin >= x_lower, x_lin <= x_upper)
    return np.inner(f1[mask], f2[mask]) * dx


def integral_inner_pos(
    f1: numpy.typing.NDArray, f2: numpy.typing.NDArray, disc: Discretization
) -> complex:
    """
    Numerical integral inner product, without complex conjugation over positive x.

    Args:
        f1: First function array
        f2: Second function array
        disc: Discretization object

    Returns:
        Inner product integral over positive domain
    """
    return integral_inner(f1, f2, disc, x_lower=disc.x_0pos)


def integral_inner_neg(
    f1: numpy.typing.NDArray, f2: numpy.typing.NDArray, disc: Discretization
) -> complex:
    """
    Numerical integral inner product, without complex conjugation over negative x.

    Args:
        f1: First function array
        f2: Second function array
        disc: Discretization object

    Returns:
        Inner product integral over negative domain
    """
    return integral_inner(f1, f2, disc, x_upper=disc.x_0neg)


def integral_norm(
    f: numpy.typing.NDArray,
    disc: Discretization,
    x_lower: Optional[float] = None,
    x_upper: Optional[float] = None,
) -> float:
    """
    Numerical integral norm over specified range.

    Args:
        f: Function array
        disc: Discretization object
        x_lower: Lower integration bound (default: x_min)
        x_upper: Upper integration bound (default: x_max)

    Returns:
        L2 norm of the function
    """
    return np.sqrt(np.abs(integral_inner(np.conj(f), f, disc, x_lower, x_upper)))


def integral_norm_pos(f: numpy.typing.NDArray, disc: Discretization) -> float:
    """
    Numerical integral norm over positive x.

    Args:
        f: Function array
        disc: Discretization object

    Returns:
        L2 norm over positive domain
    """
    return np.sqrt(np.abs(integral_inner_pos(np.conj(f), f, disc)))


def integral_norm_neg(f: numpy.typing.NDArray, disc: Discretization) -> float:
    """
    Numerical integral norm over negative x.

    Args:
        f: Function array
        disc: Discretization object

    Returns:
        L2 norm over negative domain
    """
    return np.sqrt(np.abs(integral_inner_neg(np.conj(f), f, disc)))


def normalized(
    f: numpy.typing.NDArray,
    disc: Discretization,
    x_lower: Optional[float] = None,
    x_upper: Optional[float] = None,
) -> numpy.typing.NDArray:
    """
    Normalize function to have integral norm over specified range equal to 1.

    Args:
        f: Function array to normalize
        disc: Discretization object
        x_lower: Lower integration bound (default: x_min)
        x_upper: Upper integration bound (default: x_max)

    Returns:
        Normalized function array
    """
    norm = integral_norm(f, disc, x_lower, x_upper)
    f_normed = 1 / norm * f
    return f_normed


def normalized_pos(
    f: numpy.typing.NDArray, disc: Discretization
) -> numpy.typing.NDArray:
    """
    Normalize function to have integral norm over positive x equal to 1.

    Args:
        f: Function array to normalize
        disc: Discretization object

    Returns:
        Normalized function array
    """
    norm = integral_norm_pos(f, disc)
    f_normed = 1 / norm * f
    return f_normed


def normalized_neg(
    f: numpy.typing.NDArray, disc: Discretization
) -> numpy.typing.NDArray:
    """
    Normalize function to have integral norm over negative x equal to 1.

    Args:
        f: Function array to normalize
        disc: Discretization object

    Returns:
        Normalized function array
    """
    norm = integral_norm_neg(f, disc)
    f_normed = 1 / norm * f
    return f_normed


################################### Fourier transforms #########################


def fft(
    f_lin: numpy.typing.NDArray,
    dt: float,
    dw: float,
    N: int,
    hanning_window: bool = True,
    input_is_shifted: bool = False,
) -> numpy.typing.NDArray:
    """
    Compute FFT. Unitary, plus sign in exponent.

    Hanning window (if chosen) to reduce ripple effects due to numerical truncation.

    Args:
        f_lin: Input function array
        dt: Time step
        dw: Frequency step
        N: Number of points
        hanning_window: Whether to apply Hanning window
        input_is_shifted: Whether input array is already with 0-component first

    Returns:
        Fourier transform of the input
    """
    if input_is_shifted:
        if hanning_window:
            f_shift_lin = f_lin * np.fft.fftshift(np.hanning(N))
        else:
            f_shift_lin = f_lin
    else:
        if hanning_window:
            f_shift_lin = np.fft.fftshift(f_lin * np.hanning(N))
        else:
            f_shift_lin = np.fft.fftshift(f_lin)
    F_shift_lin = np.sqrt(dt / dw) * np.fft.ifft(
        f_shift_lin, norm='ortho'
    )  # sqrt(dt / dw) for normalization.
    F_lin = np.fft.ifftshift(F_shift_lin)
    return F_lin


def ifft(
    F_lin: numpy.typing.NDArray,
    dt: float,
    dw: float,
    N: int,
    hanning_window: bool = True,
    input_is_shifted: bool = False,
) -> numpy.typing.NDArray:
    """
    Compute inverse FFT. Unitary, minus sign in exponent.

    Hanning window (if chosen) to reduce ripple effects due to numerical truncation.

    Args:
        F_lin: Input frequency domain array
        dt: Time step
        dw: Frequency step
        N: Number of points
        hanning_window: Whether to apply Hanning window
        input_is_shifted: Whether input array is already with 0-component first

    Returns:
        Inverse Fourier transform of the input
    """
    if input_is_shifted:
        if hanning_window:
            F_shift_lin = F_lin * np.fft.fftshift(np.hanning(N))
        else:
            F_shift_lin = F_lin
    else:
        if hanning_window:
            F_shift_lin = np.fft.fftshift(F_lin * np.hanning(N))
        else:
            F_shift_lin = np.fft.fftshift(F_lin)
    f_shift_lin = np.sqrt(dw / dt) * np.fft.fft(
        F_shift_lin, norm='ortho'
    )  # sqrt(dw / dt) for normalization.
    f_lin = np.fft.ifftshift(f_shift_lin)
    return f_lin


def time_shift(
    f_lin: numpy.typing.NDArray,
    w_lin: numpy.typing.NDArray,
    t_shift: float,
    dt: float,
    dw: float,
    N: int,
    hanning_window: bool = True,
) -> numpy.typing.NDArray:
    """
    Compute f(t - t_shift) by FFT.

    Args:
        f_lin: Input time domain function
        w_lin: Frequency array
        t_shift: Time shift amount
        dt: Time step
        dw: Frequency step
        N: Number of points
        hanning_window: Whether to apply Hanning window

    Returns:
        Time-shifted function
    """
    F = fft(f_lin, dt, dw, N, hanning_window)
    f_shift_lin = ifft(F * np.exp(1j * w_lin * t_shift), dt, dw, N, hanning_window)
    return f_shift_lin
