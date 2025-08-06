import screamlab.settings
import lmfit
from screamlab import dataset, settings, functions
import unittest
import matplotlib.pyplot as plt
import numpy as np


class TestDataset(unittest.TestCase):

    def setUp(self):
        self.ds = dataset.Dataset()
        self.peak = dataset.Peak()

    def add_n_spectra(self, number_of_spectra, type=["voigt"]):
        for spec in range(0, number_of_spectra):
            self.ds.spectra.append(screamlab.dataset.Spectra())
        self.add_x_axis()
        self.add_y_axix(type)

    def add_x_axis(self):
        for spec in self.ds.spectra:
            spec.x_axis = np.linspace(100, 350, 1000)

    def add_y_axix(self, type_list):
        for spec_nr, spec in enumerate(self.ds.spectra):
            y_axis = np.zeros(len(spec.x_axis))
            for type in type_list:
                if type == "voigt":
                    y_axis = y_axis + functions.voigt_profile(
                        spec.x_axis, 250, 2, 2, (spec_nr + 1) * 200
                    )
                if type == "gauss":
                    y_axis = y_axis + functions.gauss_profile(
                        spec.x_axis, 150, 3, (spec_nr + 1) * 200
                    )
                if type == "lorentz":
                    y_axis = y_axis + functions.lorentz_profile(
                        spec.x_axis, 200, 4, (spec_nr + 1) * 200
                    )
            spec.y_axis = y_axis

    def start_buildup_fitting(self, fitting_type):
        self.ds.props.buildup_types = [fitting_type]
        self.ds.peak_list.append(dataset.Peak())
        self.ds.peak_list[0].peak_sign = "+"
        buidlup_list = dataset.BuildupList()
        buidlup_list.tpol = [1, 2, 4, 8, 16, 32, 64, 128, 256]
        buidlup_list.intensity = list(
            400 * (1 - np.exp(-np.asarray(buidlup_list.tpol) / 30))
        )
        buidlup_list.intensity = buidlup_list.intensity + np.random.normal(
            0, 10, size=len(buidlup_list.intensity)
        )
        self.ds.peak_list[0]._buildup_vals = buidlup_list
        self.ds._start_buildup_fit()

    def test_dataset_init_has_none_type_importer(self):
        self.assertIsNone(self.ds.importer)

    def test_dataset_init_properties(self):
        self.assertEqual(type(self.ds.props), screamlab.settings.Properties)

    def test_dataset_init_has_none_type_spectra(self):
        self.assertListEqual(self.ds.spectra, [])

    def test_dataset_init_has_none_type_fitter(self):
        self.assertIsNone(self.ds.fitter)

    def test_setup_correct_topspin_importer_default_properties(self):
        self.ds._setup_correct_topspin_importer()
        self.assertEqual(
            type(self.ds.importer), screamlab.io.Pseudo2DImporter
        )

    def test_setup_correct_topspin_importer_set_properties_pseudo2D(self):
        self.ds.props.expno = [2]
        self.ds._setup_correct_topspin_importer()
        self.assertEqual(
            type(self.ds.importer), screamlab.io.Pseudo2DImporter
        )

    def test_setup_correct_topspin_importer_set_properties_SCREAM(self):
        self.ds.props.expno = [2, 3, 4, 5, 6]
        self.ds._setup_correct_topspin_importer()
        self.assertEqual(type(self.ds.importer), screamlab.io.ScreamImporter)

    def test_read_in_data_from_topspin_pseudo2D(self):
        # TODO add some real parameters or fake spectrum
        self.ds._read_in_data_from_topspin
        self.assertIsNotNone(self.ds.spectra)

    def test_spectra_init_number_of_scans_is_None(self):
        spectrum = screamlab.dataset.Spectra()
        self.assertIsNone(spectrum.number_of_scans)

    def test_spectra_init_tdel_None(self):
        spectrum = screamlab.dataset.Spectra()
        self.assertIsNone(spectrum.tpol)

    def test_spectra_init_x_axis_is_None(self):
        spectrum = screamlab.dataset.Spectra()
        self.assertIsNone(spectrum.x_axis)

    def test_spectra_init_y_axis_is_None(self):
        spectrum = screamlab.dataset.Spectra()
        self.assertIsNone(spectrum.y_axis)

    def test_ds_init_peak_list_is_empty_list(self):
        self.assertListEqual(self.ds.peak_list, [])

    def test_peak_init_center_is_none(self):
        self.assertIsNone(self.peak._peak_center)

    def test_peak_init_label_is_none(self):
        self.assertIsNone(self.peak._peak_label)

    def test_peak_init_fitting_type_is_none(self):
        self.assertIsNone(self.peak._fitting_type)

    def test_peak_init_fitting_type_is_none(self):
        self.assertIsNone(self.peak._fitting_type)

    def test_peak_init_peak_sing_is_none(self):
        self.assertIsNone(self.peak._peak_sign)

    def test_peak_init_line_broadening_is_none(self):
        self.assertIsNone(self.peak._line_broadening)

    def test_peak_center_set_to_int(self):
        self.peak.peak_center = 1
        self.assertEqual(self.peak.peak_center, 1.0)

    def test_peak_center_set_to_float(self):
        self.peak.peak_center = 1.0
        self.assertEqual(self.peak.peak_center, 1.0)

    def test_peak_center_set_to_invalid_type(self):
        with self.assertRaises(TypeError) as context:
            self.peak.peak_center = "str"
        self.assertEqual(
            str(context.exception),
            "'peak_center' must be of type 'int' or 'float', but got <class 'str'>.",
        )

    def test_peak_center_private_variable(self):
        self.peak.peak_center = 1
        self.assertEqual(self.peak._peak_center, 1.0)

    def test_dataset_add_one_peak(self):
        self.ds.add_peak(12)
        self.assertEqual(len(self.ds.peak_list), 1)

    def test_dataset_add_two_peaks(self):
        self.ds.add_peak(12)
        self.ds.add_peak(13)
        self.assertEqual(len(self.ds.peak_list), 2)

    def test_dataset_add_one_peak_check_correct_peak_center(self):
        self.ds.add_peak(12)
        self.assertEqual(self.ds.peak_list[0].peak_center, 12.0)

    def test_dataset_add_two_peaks_check_correct_peak_center(self):
        self.ds.add_peak(12)
        self.ds.add_peak(14.1)
        peaks = []
        for peak_center in self.ds.peak_list:
            peaks.append(peak_center.peak_center)
        self.assertListEqual(peaks, [12.0, 14.1])

    def test_peak_label_default(self):
        self.peak.peak_center = 1
        self.peak.peak_label = ""
        self.assertEqual(self.peak.peak_label, "Peak_at_1_ppm")

    def test_peak_label_own_label(self):
        self.peak.peak_label = "C_alpha"
        self.assertEqual(self.peak.peak_label, "C_alpha")

    def test_peak_label_set_to_invalid_type(self):
        with self.assertRaises(TypeError) as context:
            self.peak.peak_label = ["invalid"]
        self.assertEqual(
            str(context.exception),
            "'peak_label' must be of type 'str', but got <class 'list'>.",
        )

    def test_peak_label_private_variable(self):
        self.peak.peak_label = "C_alpha"
        self.assertEqual(self.peak._peak_label, "C_alpha")

    def test_dataset_add_two_peaks_check_correct_peak_labels(self):
        self.ds.add_peak(12.3)
        self.ds.add_peak(14.1, peak_label="C_alpha")
        peaks = []
        for peak_label in self.ds.peak_list:
            peaks.append(peak_label.peak_label)
        self.assertListEqual(peaks, ["Peak_at_12_ppm", "C_alpha"])

    def test_fitting_type_default(self):
        self.peak.fitting_type = "voigt"
        self.assertEqual(self.peak.fitting_type, "voigt")

    def test_fitting_type_gauss(self):
        self.peak.fitting_type = "gauss"
        self.assertEqual(self.peak.fitting_type, "gauss")

    def test_fitting_type(self):
        with self.assertRaises(TypeError) as context:
            self.peak.fitting_type = 12
        self.assertEqual(
            str(context.exception),
            "'fitting_type' must be of type 'str', but got <class 'int'>.",
        )

    def test_fitting_type_isinstance_of_gauss_lorentz_voigt(self):
        with self.assertRaises(ValueError) as context:
            self.peak.fitting_type = "weibull"
        self.assertEqual(
            str(context.exception),
            "'fitting_type' must be one of ['gauss', 'lorentz', 'voigt'].",
        )

    def test_fitting_type_private_variable(self):
        self.peak.fitting_type = "gauss"
        self.assertEqual(self.peak._fitting_type, "gauss")

    def test_dataset_add_two_peaks_check_correct_fitting_types(self):
        self.ds.add_peak(12.3)
        self.ds.add_peak(14.1, fitting_type="gauss")
        peaks = []
        for fitting_type in self.ds.peak_list:
            peaks.append(fitting_type.fitting_type)
        self.assertListEqual(peaks, ["voigt", "gauss"])

    def test_peak_sign_plus(self):
        self.peak.peak_sign = "+"
        self.assertEqual(self.peak.peak_sign, "+")

    def test_peak_sign_minus(self):
        self.peak.peak_sign = "-"
        self.assertEqual(self.peak.peak_sign, "-")

    def test_peak_sign_invalid_type(self):
        with self.assertRaises(TypeError) as context:
            self.peak.peak_sign = 12
        self.assertEqual(
            str(context.exception),
            "'peak_sign' must be of type 'str', but got <class 'int'>.",
        )

    def test_peak_sign_invalid_value(self):
        with self.assertRaises(ValueError) as context:
            self.peak.peak_sign = "12"
        self.assertEqual(
            str(context.exception),
            "'peak_sign' must be one of ['+', '-'].",
        )

    def test_peak_sign_private_variable(self):
        self.peak.peak_sign = "-"
        self.assertEqual(self.peak._peak_sign, "-")

    def test_dataset_add_two_peaks_check_correct_signs(self):
        self.ds.add_peak(12.3)
        self.ds.add_peak(14.1, peak_sign="-")
        peaks = []
        for peak_sign in self.ds.peak_list:
            peaks.append(peak_sign.peak_sign)
        self.assertListEqual(peaks, ["+", "-"])

    def test_line_broadening_default_gauss(self):
        self.peak.fitting_type = "gauss"
        self.peak.line_broadening = dict()
        self.assertDictEqual(
            self.peak.line_broadening, {"sigma": {"min": 0, "max": 3}}
        )

    def test_line_broadening_default_lorentz(self):
        self.peak.fitting_type = "lorentz"
        self.peak.line_broadening = dict()
        self.assertDictEqual(
            self.peak.line_broadening, {"gamma": {"min": 0, "max": 3}}
        )

    def test_line_broadening_default_lorentz(self):
        self.peak.fitting_type = "voigt"
        self.peak.line_broadening = dict()
        self.assertDictEqual(
            self.peak.line_broadening,
            {"sigma": {"min": 0, "max": 3}, "gamma": {"min": 0, "max": 3}},
        )

    def test_line_broadening_invalid_type(self):
        with self.assertRaises(TypeError) as context:
            self.peak.line_broadening = "12"
        self.assertEqual(
            str(context.exception),
            "'line_broadening' must be a 'dict', but got <class 'str'>.",
        )

    def test_line_broadening_allowed_keys(self):
        with self.assertRaises(ValueError) as context:
            self.peak.line_broadening = {"test": {"min": 0, "max": 20}}
        self.assertEqual(
            str(context.exception),
            "Invalid keys found in the dictionary: ['test']. Allowed keys are: ['sigma', 'gamma'].",
        )

    def test_line_broadening_dict_of_dicts(self):
        with self.assertRaises(TypeError) as context:
            self.peak.line_broadening = {"sigma": "min"}
        self.assertEqual(
            str(context.exception),
            "Each value in the 'line_broadening' dictionary must be of type 'dict'.",
        )

    def test_line_broadening_allowed_keys_of_dict_of_dicts(self):
        with self.assertRaises(ValueError) as context:
            self.peak.line_broadening = {"sigma": {"min": 20, "invalid": 30}}
        self.assertEqual(
            str(context.exception),
            "Invalid inner keys for 'sigma': ['invalid']. Allowed inner keys are: ['min', 'max'].",
        )

    def test_line_broadening_with_new_params_gauss(self):
        self.peak.fitting_type = "gauss"
        self.peak.line_broadening = {"sigma": {"min": 20, "max": 30}}
        self.assertDictEqual(
            self.peak.line_broadening, {"sigma": {"min": 20, "max": 30}}
        )

    def test_line_broadening_with_new_params_gauss(self):
        self.peak.fitting_type = "lorentz"
        self.peak.line_broadening = {"gamma": {"min": 20, "max": 30}}
        self.assertDictEqual(
            self.peak.line_broadening, {"gamma": {"min": 20, "max": 30}}
        )

    def test_line_broadening_with_new_params_voigt(self):
        self.peak.fitting_type = "voigt"
        self.peak.line_broadening = {"gamma": {"min": 20, "max": 30}}
        self.assertDictEqual(
            self.peak.line_broadening,
            {"gamma": {"min": 20, "max": 30}, "sigma": {"max": 3, "min": 0}},
        )

    def test_line_broadening_with_new_params_and_wrong_input(self):
        self.peak.fitting_type = "voigt"
        with self.assertRaises(TypeError) as context:
            self.peak.line_broadening = {"gamma": {"min": 20, "max": "20"}}
        self.assertEqual(
            str(context.exception),
            "'max' value must be an 'int' or 'float', but got <class 'str'>.",
        )

    def test_line_broadening_with_new_params_voigt_private_variable(self):
        self.peak.fitting_type = "voigt"
        self.peak.line_broadening = {"gamma": {"min": 20, "max": 30}}
        self.assertDictEqual(
            self.peak._line_broadening,
            {"gamma": {"min": 20, "max": 30}, "sigma": {"max": 3, "min": 0}},
        )

    def test_dataset_add_two_peaks_check_correct_signs(self):
        # Next Test
        self.ds.add_peak(12.3)
        self.ds.add_peak(
            14.1,
            line_broadening={
                "gamma": {"min": 20, "max": 30},
                "sigma": {"max": 20, "min": 0},
            },
        )
        peaks = []
        for line_broadening in self.ds.peak_list:
            peaks.append(line_broadening.line_broadening)
        self.assertListEqual(
            peaks,
            [
                {
                    "gamma": {"max": 3, "min": 0},
                    "sigma": {"max": 3, "min": 0},
                },
                {
                    "gamma": {"max": 30.0, "min": 20.0},
                    "sigma": {"max": 20.0, "min": 0.0},
                },
            ],
        )

    def test_dataset_correct_peak_list_length(self):
        # Next Test
        self.ds.add_peak(12.3)
        self.ds.add_peak(
            14.1,
            line_broadening={
                "gamma": {"min": 20, "max": 30},
                "sigma": {"max": 20, "min": 0},
            },
        )
        self.assertEqual(len(self.ds.peak_list), 2)

    def test_return_default_dict(self):
        self.assertDictEqual(
            self.peak._return_default_dict(),
            {"sigma": {"min": 0, "max": 3}, "gamma": {"min": 0, "max": 3}},
        )

    def test_dataset_perform_global_spectrum_fit_set_correct_fitter(self):
        self.ds._set_global_fitter()
        self.assertEqual(type(self.ds.fitter), screamlab.utils.GlobalFitter)

    def test_dataset_perform_single_spectrum_fit_set_correct_fitter(self):
        self.ds._set_single_fitter()
        self.assertEqual(
            type(self.ds.fitter), screamlab.utils.IndependentFitter
        )

    def test_dataset_perform_single_spectrum_fit_set_correct_fitter(self):
        self.ds._set_prefitter()
        self.assertEqual(type(self.ds.fitter), screamlab.utils.Prefitter)

    def test_init_dataset_lmfit_result_handler(self):
        self.assertEqual(
            type(self.ds.lmfit_result_handler),
            screamlab.io.LmfitResultHandler,
        )

    def test_calculate_peak_intensities_prefit_result_setter(self):
        self.ds.props.prefit = True
        self.add_n_spectra(1)
        self.ds.add_peak(250)
        self.ds._calculate_peak_intensities()
        self.assertEqual(
            type(self.ds.lmfit_result_handler.prefit),
            lmfit.minimizer.MinimizerResult,
        )

    def test_update_line_broadening(self):
        self.ds.props.prefit = True
        self.add_n_spectra(1)
        self.ds.add_peak(250, peak_sign="+")
        self.ds._set_prefitter()
        result = self.ds.fitter.fit()
        self.ds._update_line_broadening(result)
        self.ds.peak_list[-1].line_broadening["gamma"]["max"] = round(
            self.ds.peak_list[-1].line_broadening["gamma"]["max"], 1
        )
        self.ds.peak_list[-1].line_broadening["gamma"]["min"] = round(
            self.ds.peak_list[-1].line_broadening["gamma"]["min"], 1
        )
        self.ds.peak_list[-1].line_broadening["sigma"]["max"] = round(
            self.ds.peak_list[-1].line_broadening["sigma"]["max"], 1
        )
        self.ds.peak_list[-1].line_broadening["sigma"]["min"] = round(
            self.ds.peak_list[-1].line_broadening["sigma"]["min"], 1
        )
        self.assertDictEqual(
            self.ds.peak_list[-1].line_broadening,
            {
                "sigma": {"min": 1.8, "max": 2.2},
                "gamma": {"min": 1.8, "max": 2.2},
            },
        )

    def test_update_line_broadening_gauss(self):
        self.ds.props.prefit = True
        self.add_n_spectra(1, type=["gauss"])
        self.ds.add_peak(150, peak_sign="+")
        self.ds.peak_list[0].fitting_type = "gauss"
        self.ds._set_prefitter()
        result = self.ds.fitter.fit()
        self.ds._update_line_broadening(result)
        self.ds.peak_list[-1].line_broadening["sigma"]["max"] = round(
            self.ds.peak_list[-1].line_broadening["sigma"]["max"], 3
        )
        self.ds.peak_list[-1].line_broadening["sigma"]["min"] = round(
            self.ds.peak_list[-1].line_broadening["sigma"]["min"], 3
        )
        self.assertDictEqual(
            self.ds.peak_list[-1].line_broadening,
            {"sigma": {"min": 2.7, "max": 3.3}},
        )

    def test_update_line_broadening_lorentz(self):
        self.ds.props.prefit = True
        self.add_n_spectra(1, type=["lorentz"])
        self.ds.add_peak(200, peak_sign="+")
        self.ds.peak_list[0].fitting_type = "lorentz"
        self.ds._set_prefitter()
        result = self.ds.fitter.fit()
        self.ds._update_line_broadening(result)
        self.ds.peak_list[-1].line_broadening["gamma"]["max"] = round(
            self.ds.peak_list[-1].line_broadening["gamma"]["max"], 3
        )
        self.ds.peak_list[-1].line_broadening["gamma"]["min"] = round(
            self.ds.peak_list[-1].line_broadening["gamma"]["min"], 3
        )
        self.assertDictEqual(
            self.ds.peak_list[-1].line_broadening,
            {"gamma": {"min": 2.7, "max": 3.3}},
        )

    def test_calculate_peak_intensities_global_fit_result_setter_without_prefit(
        self,
    ):
        self.add_n_spectra(3)
        self.ds.add_peak(250)
        self.ds._calculate_peak_intensities()
        self.assertEqual(
            type(self.ds.lmfit_result_handler.global_fit),
            lmfit.minimizer.MinimizerResult,
        )

    def test_calculate_peak_intensities_global_fit_result_setter_with_prefit(
        self,
    ):
        self.ds.props.prefit = True
        self.add_n_spectra(3)
        self.ds.add_peak(250)
        self.ds._calculate_peak_intensities()
        self.assertEqual(
            type(self.ds.lmfit_result_handler.global_fit),
            lmfit.minimizer.MinimizerResult,
        )

    def test_buildup_list_init_tdel(self):
        tbup = dataset.BuildupList()
        self.assertEqual(tbup.tpol, None)

    def test_buildup_list_init_intensity(self):
        tbup = dataset.BuildupList()
        self.assertEqual(tbup.intensity, None)

    def test_buidlup_list_set_tdel(self):
        self.add_n_spectra(5)
        for nr, spectrum in enumerate(self.ds.spectra):
            spectrum.tpol = nr * 2
        b_list = screamlab.dataset.BuildupList()
        b_list._set_tpol(self.ds.spectra)
        self.assertListEqual(b_list.tpol, [0, 2, 4, 6, 8])

    def test_buildup_list_set_intensity_one_peak_voigt(self):
        self.add_n_spectra(5)
        self.ds.add_peak(250, peak_sign="+")
        b_list = screamlab.dataset.BuildupList()
        b_list._set_tpol(self.ds.spectra)
        self.ds._set_single_fitter()
        result = self.ds.fitter.fit()
        b_list._set_intensity(
            result, self.ds.peak_list[0].peak_label, self.ds.spectra
        )
        for val_nr, val in enumerate(b_list.intensity):
            b_list.intensity[val_nr] = round(val)

        result_list = [
            791,
            1581,
            2372,
            3163,
            3954,
        ]
        self.assertListEqual(b_list.intensity, result_list)

    def test_sort_lists(self):
        b_list = screamlab.dataset.BuildupList()
        b_list.tpol = [1, 2, 4, 8, 16, 128, 256, 32, 64]
        b_list.intensity = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        b_list._sort_lists()
        result_list = [2**i for i in range(9)] + [1, 2, 3, 4, 5, 8, 9, 6, 7]
        self.assertListEqual(b_list.tpol + b_list.intensity, result_list)

    def test_monoexp_fitting(self):
        fitting_type = "exponential"
        self.start_buildup_fitting(fitting_type)
        self.assertEqual(
            type(self.ds.lmfit_result_handler.buildup_fit[fitting_type][0]),
            lmfit.minimizer.MinimizerResult,
        )

    def test_biexp_fitting(self):
        fitting_type = "biexponential"
        self.start_buildup_fitting(fitting_type)
        self.assertEqual(
            type(self.ds.lmfit_result_handler.buildup_fit[fitting_type][0]),
            lmfit.minimizer.MinimizerResult,
        )

    def test_biexp_offset_fitting(self):
        fitting_type = "biexponential_with_offset"
        self.start_buildup_fitting(fitting_type)
        self.assertEqual(
            type(self.ds.lmfit_result_handler.buildup_fit[fitting_type][0]),
            lmfit.minimizer.MinimizerResult,
        )

    def test_exp_offset_fitting(self):
        fitting_type = "exponential_with_offset"
        self.start_buildup_fitting(fitting_type)
        self.assertEqual(
            type(self.ds.lmfit_result_handler.buildup_fit[fitting_type][0]),
            lmfit.minimizer.MinimizerResult,
        )
