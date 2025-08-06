"""
Spectral and Peak information containing module.

This moduel provides classes for handling and processing of spectral/peak information as well as
results from spectral fitting.

Classes:
    Dataset: Represents the hole dataset and provides all functions needed to start analysis.
    Spectra: Represents spectral data from NMR (Nuclear Magnetic Resonance) experiments.
    Peak: Represents a peak with its properties.
    BuildupList: Represents a list of buildup values used for fitting delay times and intensities.

"""

from datetime import datetime
import numpy as np
from screamlab import io, utils, settings, functions


class Dataset:
    """Represents a dataset containing NMR spectra, peak fitting, and buildup fitting."""

    def __init__(self, props=settings.Properties()):
        """
        Initialize the Dataset with default or specified properties.

        Parameters
        ----------
        props : settings.Properties, optional
            Experiment properties used to configure the ds.
            Defaults to settings.Properties().

        """
        self.importer = None
        self.props = props
        self.spectra = []
        self.fitter = None
        self.peak_list = []
        self.lmfit_result_handler = io.LmfitResultHandler()

    def __str__(self):
        """Returns a string representation of the ds."""
        return (
            f"[[Dataset]]\n"
            f"Fitted {len(self.peak_list)} peaks per spectrum in {len(self.spectra)} spectra."
        )

    def start_analysis(self):
        """
        Starting the analysis process.

        The analysis is carried out in three stages: first, the spectral data are imported
        from the Topspin file format; second, spectral deconvolution is performed; and finally,
        a buildup fit is applied.

        """
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "
            f"Start loading data from topspin: {self.props.path_to_experiment}"
        )
        self._read_in_data_from_topspin()
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start fitting."
        )
        self._calculate_peak_intensities()
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start buildup fit."
        )
        self._start_buildup_fit()
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "
            f"Start generating result files. ({self.props.output_folder})"
        )
        self._print_all()

    def _start_buildup_fit_from_spectra(self):
        """Starts buildup fitting using data imported from spectra CSV files."""

    def _start_buildup_from_intensitys(self):
        """Placeholder for starting buildup fitting from intensity values."""

    def add_peak(
        self,
        center_of_peak,
        peak_label="",
        fitting_type="voigt",
        peak_sign="-",
        line_broadening=None,
    ):
        """
        Adds a peak to the ds.

        Attributes
        ----------
            center_of_peak (float): Peak position in ppm (chemical shift).
            peak_label (str, optional): Custom label. Defaults to "Peak_at_<ppm>_ppm".
            fitting_type (str, optional): Peak shape: "gauss", "lorentz", or "voigt" (default).
            peak_sign (str, optional): "+" for upward, "-" for downward peaks. Defaults to "+".
            line_broadening (dict, optional): Dict with "sigma" and "gamma" keys for line width.
                Defaults to {"sigma": {"min": 0, "max": 3}, "gamma": {"min": 0, "max": 3}}.

        """
        if line_broadening is None:
            line_broadening = {}
        self.peak_list.append(Peak())
        peak = self.peak_list[-1]
        peak.peak_center = center_of_peak
        peak.peak_label = peak_label
        peak.fitting_type = fitting_type
        peak.peak_sign = peak_sign
        peak.line_broadening = line_broadening

    def _read_in_data_from_topspin(self):
        """Reads and imports data from TopSpin."""
        self._setup_correct_topspin_importer()
        self.importer.import_topspin_data()

    def _setup_correct_topspin_importer(self):
        """Sets up the appropriate TopSpin importer based on experiment properties."""
        if len(self.props.expno) == 1:
            self.importer = io.Pseudo2DImporter(self)
        else:
            self.importer = io.ScreamImporter(self)

    def _print_all(self):
        """Prints all results using an exporter."""
        exporter = io.Exporter(self)
        exporter.print()

    def _read_in_data_from_csv(self):
        """Placeholder function for reading data from CSV files."""

    def _calculate_peak_intensities(self):
        """Calculates peak intensities based on fitting methods."""
        if self.props.prefit:
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start prefit."
            )
            self._set_prefitter()
            result = self.fitter.fit()
            self.lmfit_result_handler.prefit = result
            self._update_line_broadening(result)
        if "individual" == self.props.spectrum_fit_type:
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start individual fit."
            )
            self._set_single_fitter()
            result = self.fitter.fit()
            self.lmfit_result_handler.global_fit = result
            self._get_intensities(result)
        if "global" == self.props.spectrum_fit_type:
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start global fit."
            )
            self._set_global_fitter()
            result = self.fitter.fit()
            self.lmfit_result_handler.global_fit = result
            self._get_intensities(result)

    def _start_buildup_fit(self):
        """Performs buildup fitting using the appropriate fitter classes."""
        fitter_classes = {
            "biexponential": utils.BiexpFitter,
            "biexponential_with_offset": utils.BiexpFitterWithOffset,
            "exponential": utils.ExpFitter,
            "exponential_with_offset": utils.ExpFitterWithOffset,
            "streched_exponential": utils.StrechedExponentialFitter,
        }

        for b_type in self.props.buildup_types:
            fitter_class = fitter_classes.get(b_type)
            if fitter_class:
                fitter = fitter_class(self)
                self.lmfit_result_handler.buildup_fit[b_type] = (
                    fitter.perform_fit()
                )

    def _set_prefitter(self):
        """Sets up a pre-fitter."""
        self.fitter = utils.Prefitter(self)

    def _set_single_fitter(self):
        """Sets up a single-spectrum fitter."""
        self.fitter = utils.IndependentFitter(self)

    def _set_global_fitter(self):
        """Sets up a global fitter for all spectra."""
        self.fitter = utils.GlobalFitter(self)

    def _get_intensities(self, result):
        """Extracts intensity values from the fitting results."""
        if isinstance(
            self.fitter, (utils.IndependentFitter, utils.GlobalFitter)
        ):
            for peak in self.peak_list:
                peak.buildup_vals = (result, self.spectra)

    def _update_line_broadening(self, result):
        """Updates line broadening values based on fitting results."""
        for peak in self.peak_list:
            peak.line_broadening = {
                lw: {
                    "min": result.params.get(
                        f"{peak.peak_label}_{lw}_0"
                    ).value
                    * 0.9,
                    "max": result.params.get(
                        f"{peak.peak_label}_{lw}_0"
                    ).value
                    * 1.1,
                }
                for lw in ["sigma", "gamma"]
                if f"{peak.peak_label}_{lw}_0" in result.params
            }


class Spectra:
    """
    Represents spectral data for NMR (Nuclear Magnetic Resonance) experiments.

    Attributes
    ----------
    number_of_scans : list of int or None
        The number of scans performed in the NMR experiment.
    tpol : float or None
        The polarization time used in the experiment.
    x_axis : array-like or None
        The x-axis values representing frequency domain data data.
    y_axis : array-like or None
        The y-axis values representing intensity or amplitude data.

    """

    def __init__(self):
        """Initializes Spectra attributes."""
        self.number_of_scans = None
        self.tpol = None
        self.x_axis = None
        self.y_axis = None


class Peak:
    """
    Represents a peak with its properties.

    Such as peak center, peak label, fitting group, fitting type,
    peak sign, line broadening, and buildup values.

    """

    def __init__(self):
        """Initializes a Peak object with default values set to None."""
        self._peak_center = None
        self._peak_label = None
        self._fitting_type = None
        self._peak_sign = None
        self._line_broadening = None
        self._line_broadening_init = None
        self._buildup_vals = None

    def __str__(self):
        """
        Returns a formatted string representation of the peak.

        :return: A string describing the peak's attributes.
        """
        return (
            f"Peak center: {self.peak_center}\n"
            f"Peak label: {self.peak_label}\n"
            f"Peak shape: {self.fitting_type}\n"
            f"Peak sign: {self.peak_sign}\n"
            f"During the prefit stage, variables are permitted to vary within "
            f"the following ranges:\n"
            f" {self._format_fitting_range('prefit')}"
            f"During the main analysis stage, variables are permitted to vary "
            f"within the following ranges:\n"
            f" {self._format_fitting_range('')}"
        )

    def _format_fitting_range(self, fit_type):
        a_max = "0 and inf" if self.peak_sign == "+" else "-inf and 0"
        lb = ""
        line_broadening = (
            self._line_broadening_init
            if fit_type == "prefit"
            else self._line_broadening
        )
        for keys in line_broadening:
            lb += (
                f"\t{keys}:\t\t\tBetween {line_broadening[keys]['min']} ppm"
                f" and {line_broadening[keys]['max']} ppm.\n"
            )
        return (
            f"\tCenter (µ):\t\tBetween {self.peak_center-1} ppm and"
            f" {self.peak_center+1} ppm.\n"
            f"\tAmplitude (A):\tBetween {a_max}.\n"
            f"{lb}"
        )

    @property
    def buildup_vals(self) -> list:
        """
        Gets the buildup values.

        :return: A list of buildup values.
        """
        return self._buildup_vals

    @buildup_vals.setter
    def buildup_vals(self, args):
        """
        Sets the buildup values.

        :param args: Tuple containing result and spectra.
        """
        result, spectra = args
        self._buildup_vals = BuildupList()
        self._buildup_vals.set_vals(result, spectra, self.peak_label)

    @property
    def line_broadening(self) -> str:
        """
        Gets the line broadening parameters.

        :return: A dictionary representing line broadening values.
        """
        return self._line_broadening

    @line_broadening.setter
    def line_broadening(self, value):
        """
        Sets the line broadening parameters after validation.

        :param value: Dictionary containing line broadening parameters.
        """
        allowed_values = ["sigma", "gamma"]
        inner_allowed_values = ["min", "max"]
        self._check_if_value_is_dict(value)
        self._check_for_invalid_keys(value, allowed_values)
        self._check_for_invalid_dict(value)
        self._check_for_invalid_inner_keys(value, inner_allowed_values)
        params = self._set_init_params()
        self._overwrite_init_params(
            value, allowed_values, inner_allowed_values, params
        )

        self._line_broadening = params
        if self._line_broadening_init is None:
            self._line_broadening_init = params

    @property
    def peak_sign(self) -> str:
        """
        Gets the peak sign.

        :return: The peak sign ('+' or '-').
        """
        return self._peak_sign

    @peak_sign.setter
    def peak_sign(self, value):
        """
        Sets the peak sign after validation.

        :param value: A string representing the peak sign ('+' or '-').
        """
        allowed_values = {"+", "-"}
        if not isinstance(value, str):
            raise TypeError(
                f"'peak_sign' must be of type 'str', but got {type(value)}."
            )
        if value not in allowed_values:
            raise ValueError(
                f"'peak_sign' must be one of {sorted(allowed_values)}."
            )
        self._peak_sign = value

    @property
    def fitting_type(self) -> str:
        """
        Gets the peak fitting type.

        :return: The fitting type as a string.
        """
        return self._fitting_type

    @fitting_type.setter
    def fitting_type(self, value):
        """
        Sets the peak fitting type after validation.

        :param value: A string representing the fitting type.
        """
        allowed_values = {"voigt", "lorentz", "gauss"}
        if not isinstance(value, str):
            raise TypeError(
                f"'fitting_type' must be of type 'str', but got {type(value)}."
            )
        if value not in allowed_values:
            raise ValueError(
                f"'fitting_type' must be one of {sorted(allowed_values)}."
            )
        self._fitting_type = value

    @property
    def peak_center(self) -> (int, float):
        """
        Gets the peak center.

        :return: The peak center as an integer or float.
        """
        return self._peak_center

    @peak_center.setter
    def peak_center(self, value):
        """
        Sets the peak center after validation.

        :param value: An integer or float representing the peak center.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"'peak_center' must be of type 'int' or 'float', but got {type(value)}."
            )
        self._peak_center = float(value)

    @property
    def peak_label(self) -> str:
        """
        Get or set the label for a peak.

        Returns
        -------
            str: The current peak label.

        """
        return self._peak_label

    @peak_label.setter
    def peak_label(self, value):
        """
        Set the label for a peak.

        If an empty string is provided, a default label in the format
        'Peak_at_<center>_ppm' is generated, where <center> is the integer
        value of `self.peak_center` (with '-' replaced by 'm').

        Args
        ----
            value (str): The label to assign to the peak.

        Raises
        ------
            TypeError: If the provided value is not a string.

        """
        if not isinstance(value, str):
            raise TypeError(
                f"'peak_label' must be of type 'str', but got {type(value)}."
            )
        if value == "":
            name = str(int(self.peak_center)).replace("-", "m")
            value = f"Peak_at_{name}_ppm"
        self._peak_label = value

    def _return_default_dict(self):
        """
        Returns the default dictionary for line broadening values.

        :return: A dictionary with default values for 'sigma' and 'gamma'.
        """
        return {
            "sigma": {"min": 0, "max": 3},
            "gamma": {"min": 0, "max": 3},
        }

    def _check_if_value_is_dict(self, value):
        """
        Checks if the given value is a dictionary.

        :param value: The value to check.
        """
        if not isinstance(value, dict):
            raise TypeError(
                f"'line_broadening' must be a 'dict', but got {type(value)}."
            )

    def _check_for_invalid_keys(self, value, allowed_values):
        invalid_keys = [
            key for key in value.keys() if key not in allowed_values
        ]
        if invalid_keys:
            raise ValueError(
                f"Invalid keys found in the dictionary: {invalid_keys}. "
                f"Allowed keys are: {allowed_values}."
            )

    def _check_for_invalid_dict(self, value):
        if not all(isinstance(v, dict) for v in value.values()):
            raise TypeError(
                "Each value in the 'line_broadening' dictionary must be of type 'dict'."
            )

    def _check_for_invalid_inner_keys(self, value, inner_allowed_values):
        for key, inner_dict in value.items():
            invalid_inner_keys = [
                inner_key
                for inner_key in inner_dict.keys()
                if inner_key not in inner_allowed_values
            ]
            if invalid_inner_keys:
                raise ValueError(
                    f"Invalid inner keys for '{key}': {invalid_inner_keys}. "
                    f"Allowed inner keys are: {inner_allowed_values}."
                )

    def _set_init_params(self):
        """
        Sets initial parameters based on fitting type.

        :return: A dictionary of initial parameters.
        """
        params = self._return_default_dict()
        if self.fitting_type == "gauss":
            params = {"sigma": params["sigma"]}
        elif self.fitting_type == "lorentz":
            params = {"gamma": params["gamma"]}
        return params

    def _overwrite_init_params(
        self, value, allowed_values, inner_allowed_values, params
    ):
        """
        Overwrites initial parameters with provided values.

        :param value: Dictionary containing new parameter values.
        :param allowed_values: List of allowed outer dictionary keys.
        :param inner_allowed_values: List of allowed inner dictionary keys.
        :param params: Dictionary of existing parameters to be updated.

        """
        for key in allowed_values:
            if key in value:
                for inner_key in inner_allowed_values:
                    inner_value = value[key].get(inner_key)
                    if inner_value is not None:
                        if not isinstance(inner_value, (int, float)):
                            raise TypeError(
                                f"'{inner_key}' value must be an 'int' or 'float', "
                                f"but got {type(inner_value)}."
                            )
                        params[key][inner_key] = float(inner_value)
        return params


class BuildupList:
    """
    Represents a list of buildup values used for fitting delay times and intensities.

    Attributes
    ----------
        tpol (list): List of delay times.
        intensity (list): List of intensity values.

    """

    def __init__(self):
        """Initializes an empty BuildupList with None values for attributes."""
        self.tpol = None
        self.intensity = None

    def __str__(self):
        """
        Returns a formatted string representation of the buildup values.

        Returns
        -------
            str: A formatted string listing delay times and intensities.

        """
        return (
            "Parameters for buildup fitting:\nDelay times:\t"
            + "\t\t\t".join(str(x) for x in self.tpol)
            + "\nIntegral:\t"
            + "\t".join(str(x) for x in self.intensity)
        )

    def set_vals(self, result, spectra, label):
        """
        Sets buildup values using the result parameters and spectra.

        Attributes
        ----------
            result (object): Fitted parameter values used for calculating buildup.
            spectra (list): Spectrum objects used with result to compute buildup.
            label (str): Peak label used to filter relevant parameters in result.

        """
        self._set_tpol(spectra)
        self._set_intensity(result, label, spectra)
        self._sort_lists()

    def _set_tpol(self, spectra):
        self.tpol = [s.tpol for s in spectra]

    def _set_intensity(self, result, label, spectra):
        last_digid = None
        self.intensity = []
        val_list = []
        for param in result.params:
            if label in param:
                if last_digid != param.split("_")[-1]:
                    if val_list:
                        self.intensity.append(
                            self._calc_integral(
                                val_list, spectra[int(last_digid)]
                            )
                        )
                    last_digid = param.split("_")[-1]
                    val_list = []
                val_list.append(float(result.params[param].value))
                if param.split("_")[-2] == "gamma":
                    val_list.append("gamma")
        self.intensity.append(
            self._calc_integral(val_list, spectra[int(last_digid)])
        )

    def _calc_integral(self, val_list, spectrum):
        """
        Computes the numerical integral of the simulated spectrum.

        Args
        ----
            val_list (list): List of values used for peak calculation.
            spectrum (object): Spectrum object containing x-axis data.

        Returns
        -------
            float: The computed integral of the spectrum.

        """
        simspec = [0 for _ in range(len(spectrum.x_axis))]
        simspec = functions.calc_peak(spectrum.x_axis, simspec, val_list)
        return np.trapz(simspec)

    def _sort_lists(self):
        """
        Sorting method.

        Sorts the delay times and corresponding intensity values in
        ascending order of delay times.
        """
        self.tpol, self.intensity = map(
            list, zip(*sorted(zip(self.tpol, self.intensity)))
        )
