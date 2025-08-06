"""
Provides general-purpose utility functions used across various models.

Functions are independent and stateless, designed to be reusable throughout the codebase.
"""

import re
import numpy as np
from scipy.special import wofz


def voigt_profile(x, center, sigma, gamma, amplitude):
    """
    Compute the Voigt profile, a convolution of a Gaussian and Lorentzian function.

    :param x: Array of x values.
    :param center: Center of the peak.
    :param sigma: Standard deviation of the Gaussian component.
    :param gamma: Half-width at half-maximum (HWHM) of the Lorentzian component.
    :param amplitude: Peak amplitude.
    :return: Voigt profile evaluated at x.
    """
    z = ((x - center) + 1j * gamma) / (sigma * np.sqrt(2))
    return amplitude * np.real(wofz(z)) / (sigma * np.sqrt(2 * np.pi))


def gauss_profile(x, center, sigma, amplitude):
    """
    Compute a Gaussian profile.

    :param x: Array of x values.
    :param center: Center of the peak.
    :param sigma: Standard deviation of the Gaussian distribution.
    :param amplitude: Peak amplitude.
    :return: Gaussian profile evaluated at x.
    """
    return (
        amplitude
        * np.exp(-0.5 * ((x - center) / sigma) ** 2)
        / (sigma * np.sqrt(2 * np.pi))
    )


def lorentz_profile(x, center, gamma, amplitude):
    """
    Compute a Lorentzian profile.

    :param x: Array of x values.
    :param center: Center of the peak.
    :param gamma: Half-width at half-maximum (HWHM) of the Lorentzian function.
    :param amplitude: Peak amplitude.
    :return: Lorentzian profile evaluated at x.
    """
    return (
        amplitude
        * (gamma**2 / ((x - center) ** 2 + gamma**2))
        / (np.pi * gamma)
    )


def fwhm_gaussian(sigma):
    """
    Compute the Full Width at Half Maximum (FWHM) of a Gaussian function.

    It is calculated using the formula:
        FWHM = 2 * sqrt(2 * ln(2)) * sigma

    Parameters
    ----------
    sigma : float
        The standard deviation of the Gaussian function.

    Returns
    -------
    float
        The full width at half maximum (FWHM) of the Gaussian.

    """
    return 2 * np.sqrt(2 * np.log(2)) * sigma


def fwhm_lorentzian(gamma):
    """
    Compute the Full Width at Half Maximum (FWHM) of a Lorentzian function.

    For a Lorentzian distribution, the FWHM is:
        FWHM = 2 * gamma

    Parameters
    ----------
    gamma : float
        The half-width at half-maximum (HWHM) parameter of the Lorentzian function.

    Returns
    -------
    float
        The full width at half maximum (FWHM) of the Lorentzian.

    """
    return 2 * gamma


def fwhm_voigt(sigma, gamma):
    """
    Compute the full width at half maximum (FWHM) of a Voigt profile.

    The Voigt profile is a convolution of a Gaussian and a Lorentzian function:
        FWHM ≈ 0.5346 * (2 * gamma) + sqrt(0.2166 * (2 * gamma)^2 + 4 * ln(2) * sigma^2)

    Parameters
    ----------
    sigma : float
        Standard deviation of the Gaussian component.
    gamma : float
        Half-width at half-maximum (HWHM) of the Lorentzian component.

    Returns
    -------
    float
        The approximate FWHM of the Voigt profile.

    """
    return 0.5346 * (2 * gamma) + np.sqrt(
        0.2166 * (2 * gamma) ** 2 + 4 * np.log(2) * sigma**2
    )


def calc_exponential(time_vals, param):
    """
    Compute values of an exponential growth function over time.

    The function models the equation:
        I(t) = A * (1 - exp(-t / tf))

    where:
        - I(t)  : The output value at time t
        - A     : Amplitude (maximum value the function approaches)
        - tf    : Time constant (controls the rate of growth)

    Returns
    -------
        list: Exponential profile evaluated at t.

    """
    return list(param[0] * (1 - np.exp(-np.asarray(time_vals) / param[1])))


def calc_stretched_exponential(time_vals, param):
    """
    Compute values of a stretched exponential growth function over time.

    The function models the equation:
        I(t) = A * (1 - exp(-t / tf)^beta)

    where:
        - I(t)  : The output value at time t
        - A     : Amplitude (maximum value the function approaches)
        - tf    : Time constant (controls the rate of growth)
        - beta  : stretching exponent

    Returns
    -------
        list: Stretched exponential profile evaluated at t.

    """
    return list(
        param[0]
        * (1 - np.exp(-((np.asarray(time_vals) / param[1]) ** param[2])))
    )


def calc_biexponential(time_vals, param):
    """
    Compute values of a biexponential growth function over time.

    The function models the equation:
        I(t) = Af * (1 - exp(-t / tf)) + As * (1 - exp(-t / ts))

    where:
        - I(t)  : The output value at time t
        - Af, As: Amplitudes (maximum value the function approaches)
        - tf, ts: Time constants (controls the rate of growth)


    Returns
    -------
        list: Biexponential profile evaluated at t.

    """
    return list(
        param[0] * (1 - np.exp(-np.asarray(time_vals) / param[2]))
        + param[1] * (1 - np.exp(-np.asarray(time_vals) / param[3]))
    )


def calc_exponential_with_offset(time_vals, param):
    """
    Compute values of an exponential growth function with time offset over time.

    The function models the equation:
        I(t) = Af * (1 - exp(-(t-t0) / tf))

    where:
        - I(t)  : The output value at time t
        - Af    : Amplitudes (maximum value the function approaches)
        - tf    : Time constants (controls the rate of growth)
        - t0    : Time offset


    Returns
    -------
        list: Exponential profile with time offset evaluated at t.

    """
    return list(
        param[0]
        * (1 - np.exp(-(np.asarray(time_vals) - param[2]) / param[1]))
    )


def calc_biexponential_with_offset(time_vals, param):
    """
    Compute values of a biexponential growth function with time offset over time.

    The function models the equation:
        I(t) = Af * (1 - exp(-(t - t0) / tf)) + As * (1 - exp(-(t - t0) / ts))

    where:
        - I(t)  : The output value at time t
        - Af, As: Amplitudes (maximum value the function approaches)
        - tf, ts: Time constants (controls the rate of growth)
        - t0    : Time offset


    Returns
    -------
        list: Biexponential profile with time offset evaluated at t.

    """
    return list(
        param[0]
        * (1 - np.exp(-(np.asarray(time_vals) - param[4]) / param[2]))
        + param[1]
        * (1 - np.exp(-(np.asarray(time_vals) - param[4]) / param[3]))
    )


def generate_spectra_param_dict(params):
    """
    Generate a dictionary of spectral parameters from a list of parameter names.

    :param params: Dictionary of parameter names and values.
    :return: Dictionary of structured parameter values.
    """
    param_dict = {}
    prefix, lastfix = None, None
    dict_index = -1
    param_value_list = []
    for param in params:
        parts = re.split(r"_(cen|amp|sigma|gamma)_", param)
        if prefix != parts[0]:
            if param_value_list:
                param_dict[dict_index].append(param_value_list)
            prefix = parts[0]
            param_value_list = []
        if lastfix != parts[2]:
            if param_value_list:
                param_dict[dict_index].append(param_value_list)
                param_value_list = []
            lastfix = parts[2]
            dict_index += 1
        if dict_index not in param_dict:
            param_dict[dict_index] = []
        param_value_list.append(float(params[param].value))
        if parts[1] == "gamma":
            param_value_list.append("gam")
    param_dict[dict_index].append(param_value_list)
    return param_dict


def calc_peak(x_axis, simspec, val):
    """Simulates spectra based on given parameters."""
    if len(val) == 5:
        simspec += voigt_profile(x_axis, val[1], val[2], val[3], val[0])
    if len(val) == 3:
        simspec += gauss_profile(x_axis, val[1], val[2], val[0])
    if len(val) == 4:
        simspec += lorentz_profile(x_axis, val[1], val[2], val[0])
    return simspec


def format_mapping():
    """Maps each buildup function type to its parameter names."""
    return {
        "exponential": [
            "Af",
            "tf",
            "---",
            "---",
            "---",
            "Rf",
            "---",
            "Sf",
            "---",
            "---",
        ],
        "streched_exponential": [
            "Af",
            "tf",
            "---",
            "---",
            "---",
            "Rf",
            "---",
            "Sf",
            "---",
            "beta",
        ],
        "exponential_with_offset": [
            "Af",
            "tf",
            "---",
            "---",
            "t_off",
            "Rf",
            "---",
            "Sf",
            "---",
            "---",
        ],
        "biexponential": [
            "Af",
            "tf",
            "As",
            "ts",
            "---",
            "Rf",
            "Rs",
            "Sf",
            "Ss",
            "---",
        ],
        "biexponential_with_offset": [
            "Af",
            "tf",
            "As",
            "ts",
            "t_off",
            "Rf",
            "Rs",
            "Sf",
            "Ss",
            "---",
        ],
    }


def buildup_header():
    """Returns a list of headers for the buildup analysis table."""
    return [
        "Label",
        "Af / a.u.",
        "tf / s",
        "As / a.u.",
        "ts / s",
        "t_off / s",
        "Rf / 1/s",
        "Rs / 1/s",
        "Sensitivity1 (Af/sqrt(tf))",
        "Sensitivity2 (As/sqrt(ts))",
        "beta",
    ]


def spectrum_fit_header():
    """Returns a list of headers for the spectrum fitting results table."""
    return [
        "Label",
        "Time / s",
        "Center / ppm",
        "Amplitude / a.u.",
        "Sigma / ppm",
        "Gamma / ppm",
        "FWHM Lorentz / ppm",
        "FWHM Gauss / ppm",
        "FWHM Voigt / ppm",
        "Integral / a.u.",
    ]


def return_func_map():
    """Returns a dictionary mapping function types to their corresponding fitting functions."""
    return {
        "exponential": calc_exponential,
        "biexponential": calc_biexponential,
        "exponential_with_offset": calc_exponential_with_offset,
        "biexponential_with_offset": calc_biexponential_with_offset,
        "streched_exponential": calc_stretched_exponential,
    }


def generate_subspec(spectrum, subspec):
    """
    Extract a subspectrum of a spectrum based on a given x-axis range.

    Returns
    -------
    tuple of ndarray
        A tuple containing two arrays:
        The sliced x- and y-axis values specified range.

    """
    start = np.argmax(spectrum.x_axis < max(subspec))
    stop = np.argmax(spectrum.x_axis < min(subspec))
    return spectrum.x_axis[start:stop], spectrum.y_axis[start:stop]
