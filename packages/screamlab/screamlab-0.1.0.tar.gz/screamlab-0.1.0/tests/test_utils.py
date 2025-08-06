import unittest
import lmfit
import numpy as np
import matplotlib.pyplot as plt
from screamlab import dataset, settings, utils, functions


class TestDataset(unittest.TestCase):

    def setUp(self):
        self.ds = dataset.Dataset()
        self.peak = dataset.Peak()
        self.fitter = utils.Fitter(self.ds)
        self.prefitter = utils.Prefitter(self.ds)
        self.globalfitter = utils.GlobalFitter(self.ds)
        self.singlefitter = utils.IndependentFitter(self.ds)

    def assertListAlmostEqual(self, list1, list2, delta=1e-6):
        self.assertEqual(
            len(list1), len(list2), "Lists are of different lengths"
        )
        for i, (a, b) in enumerate(zip(list1, list2)):
            self.assertAlmostEqual(
                a, b, delta=delta, msg=f"Mismatch at index {i}: {a} != {b}"
            )

    def add_n_spectra(self, number_of_spectra, type=["voigt"]):
        self.ds.spectra = []
        for spec in range(0, number_of_spectra):
            self.ds.spectra.append(dataset.Spectra())
            self.ds.add_peak(150)
        self.add_x_axis()
        self.add_y_axix(type)

    def add_one_peak(self):
        self.ds.peak_list.append(dataset.Peak())
        self.ds.peak_list[0]._buildup_vals = dataset.BuildupList()
        self.ds.peak_list[0]._buildup_vals.tpol = [2**i for i in range(7)]
        self.ds.peak_list[0]._buildup_vals.intensity = [
            12000 * (1 + np.exp(-3 / (2**i))) for i in range(7)
        ]
        self.ds.peak_list[0].peak_sign = "+"

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

    def add_noise(self, y_axis):
        y_axis = np.array(y_axis)
        noise = np.random.normal(0, 1, size=y_axis.shape)
        return y_axis + noise

    def calc_params(self, fitter):
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        samples = fitter._get_lhs_init_params(param_dict, 2)
        return fitter._set_params(param_dict, samples[0])

    def calc_lhs_init_params(self, fitter):
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        return fitter._get_lhs_init_params(param_dict, 2)

    def check_dict(self, param_dict, a_dict):
        t_dict = {"value": 5, "min": 0, "max": 192}
        x_dict = {"value": 0, "min": -5, "max": 192}
        for key in param_dict:
            if "A" in key:
                self.assertDictEqual(param_dict[key], a_dict)
            if "t" in key:
                if "t_off" in key:
                    self.assertDictEqual(
                        param_dict[key], {"value": 0, "min": -5, "max": 5}
                    )
                else:
                    self.assertDictEqual(param_dict[key], t_dict)
            if "x" in key:
                self.assertDictEqual(param_dict[key], x_dict)

    def test_fitter_init_dataset(self):
        self.assertEqual(type(self.fitter.dataset), dataset.Dataset)

    def test_prefitter_init_dataset(self):
        self.assertEqual(type(self.prefitter.dataset), dataset.Dataset)

    def test_globalfitter_init_dataset(self):
        self.assertEqual(type(self.globalfitter.dataset), dataset.Dataset)

    def test_singlefitter_init_dataset(self):
        self.assertEqual(type(self.singlefitter.dataset), dataset.Dataset)

    def test_generate_x_axis_list_prefitter(self):
        self.add_n_spectra(1)
        x_axis, y_axis = self.prefitter._generate_axis_list()
        self.assertTrue(
            np.array_equal(x_axis[0], np.linspace(100, 350, 1000))
        )

    def test_generate_axis_list_same_lenght_prefitter(self):
        self.add_n_spectra(1)
        x_axis, y_axis = self.prefitter._generate_axis_list()
        self.assertEqual(len(x_axis[0]), len(y_axis[0]))

    def test_generate_x_axis_has_one_element_prefitter(self):
        self.add_n_spectra(1)
        x_axis, y_axis = self.prefitter._generate_axis_list()
        self.assertEqual(len(x_axis), 1)

    def test_generate_y_axis_has_one_element_prefitter(self):
        self.add_n_spectra(1)
        x_axis, y_axis = self.prefitter._generate_axis_list()
        self.assertEqual(len(y_axis), 1)

    def test_generate_y_axis_correct_spectrum_prefitter(self):
        self.add_n_spectra(1)
        x_axis, y_axis = self.prefitter._generate_axis_list()
        self.assertEqual(
            max(y_axis[0]),
            max(
                functions.voigt_profile(
                    self.ds.spectra[0].x_axis, 250, 2, 2, 200
                )
            ),
        )

    def test_generate_y_axis_correct_spectrum_prefitter_with_more_spectra(
        self,
    ):
        self.add_n_spectra(7)

        self.prefitter.dataset.props.spectrum_for_prefit = 6
        x_axis, y_axis = self.prefitter._generate_axis_list()
        self.prefitter.dataset.props.spectrum_for_prefit = -1
        self.assertEqual(
            max(y_axis[0]),
            max(
                functions.voigt_profile(
                    self.ds.spectra[0].x_axis, 250, 2, 2, 7 * 200
                )
            ),
        )

    def test_generate_x_axis_global_fitter(self):
        self.add_n_spectra(7)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        self.assertEqual(len(x_axis), 7)

    def test_generate_y_axis_global_fitter(self):
        self.add_n_spectra(7)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        self.assertEqual(len(y_axis), 7)

    def test_generate_y_axis_global_fitter(self):
        self.add_n_spectra(7)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        maxima = []
        sim_maxima = []
        for nr, axis in enumerate(y_axis):
            maxima.append(max(axis))
            sim_maxima.append(
                max(
                    functions.voigt_profile(
                        self.ds.spectra[0].x_axis, 250, 2, 2, (nr + 1) * 200
                    )
                )
            )
        self.assertListEqual(maxima, sim_maxima)

    def test_generate_x_axis_single_fitter(self):
        self.add_n_spectra(7)
        x_axis, y_axis = self.singlefitter._generate_axis_list()
        self.assertEqual(len(x_axis), 7)

    def test_generate_y_axis_single_fitter(self):
        self.add_n_spectra(6)
        x_axis, y_axis = self.singlefitter._generate_axis_list()
        self.assertEqual(len(y_axis), 6)

    def test_generate_y_axis_single_fitter(self):
        self.add_n_spectra(6)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        maxima = []
        sim_maxima = []
        for nr, axis in enumerate(y_axis):
            maxima.append(max(axis))
            sim_maxima.append(
                max(
                    functions.voigt_profile(
                        self.ds.spectra[0].x_axis, 250, 2, 2, (nr + 1) * 200
                    )
                )
            )
        self.assertListEqual(maxima, sim_maxima)

    def test_get_amplitude_dict_negative_sign_prefitter(self):
        self.add_n_spectra(1)
        value = self.prefitter._get_amplitude_dict(self.ds.peak_list[0], 0)
        self.assertDictEqual(
            value,
            {
                "name": "Peak_at_150_ppm_amp_0",
                "value": -200,
                "min": -np.inf,
                "max": 0,
            },
        )

    def test_get_amplitude_dict_positive_sign_prefitter(self):
        self.add_n_spectra(1)
        self.ds.peak_list[0].peak_sign = "+"
        value = self.prefitter._get_amplitude_dict(self.ds.peak_list[0], 0)
        self.assertDictEqual(
            value,
            {
                "name": "Peak_at_150_ppm_amp_0",
                "value": 200,
                "min": 0,
                "max": np.inf,
            },
        )

    def test_get_lw_dict_sigma_prefitter(self):
        self.add_n_spectra(1)
        value = self.prefitter._get_lw_dict(self.ds.peak_list[0], 0, "sigma")
        self.assertDictEqual(
            value,
            {
                "name": "Peak_at_150_ppm_sigma_0",
                "value": 1.5,
                "min": 0,
                "max": 3,
            },
        )

    def test_get_lw_dict_gamma_prefitter(self):
        self.add_n_spectra(1)
        value = self.prefitter._get_lw_dict(self.ds.peak_list[0], 0, "gamma")
        self.assertDictEqual(
            value,
            {
                "name": "Peak_at_150_ppm_gamma_0",
                "value": 1.5,
                "min": 0,
                "max": 3,
            },
        )

    def test_get_lw_dict_gamma_non_default_values_prefitter(self):
        self.add_n_spectra(1)
        self.ds.peak_list[0].line_broadening["gamma"]["max"] = 5
        value = self.prefitter._get_lw_dict(self.ds.peak_list[0], 0, "gamma")
        self.assertDictEqual(
            value,
            {
                "name": "Peak_at_150_ppm_gamma_0",
                "value": 2.5,
                "min": 0,
                "max": 5,
            },
        )

    def test_generate_params_list_one_voigt_prefitter(self):
        self.add_n_spectra(1)
        params = self.prefitter._generate_params_list()
        self.assertListEqual(
            list(params.keys()),
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
            ],
        )

    def test_generate_params_list_one_gauss_prefitter(self):
        self.add_n_spectra(1)
        self.ds.peak_list[0].fitting_type = "gauss"
        params = self.prefitter._generate_params_list()
        self.assertListEqual(
            list(params.keys()),
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
            ],
        )

    def test_generate_params_list_one_lorentz_prefitter(self):
        self.add_n_spectra(1)
        self.ds.peak_list[0].fitting_type = "lorentz"
        params = self.prefitter._generate_params_list()
        self.assertListEqual(
            list(params.keys()),
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_gamma_0",
            ],
        )

    def test_generate_params_list_two_voigt_prefitter(self):
        self.add_n_spectra(1)
        self.ds.add_peak(120)
        params = self.prefitter._generate_params_list()
        self.assertListEqual(
            list(params.keys()),
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
                "Peak_at_120_ppm_amp_0",
                "Peak_at_120_ppm_cen_0",
                "Peak_at_120_ppm_sigma_0",
                "Peak_at_120_ppm_gamma_0",
            ],
        )

    def test_generate_params_list_voigt_gauss_lorentz_prefitter(self):
        self.add_n_spectra(1)
        self.ds.add_peak(120, fitting_type="gauss")
        self.ds.add_peak(100, fitting_type="lorentz")
        params = self.prefitter._generate_params_list()
        self.assertListEqual(
            list(params.keys()),
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
                "Peak_at_120_ppm_amp_0",
                "Peak_at_120_ppm_cen_0",
                "Peak_at_120_ppm_sigma_0",
                "Peak_at_100_ppm_amp_0",
                "Peak_at_100_ppm_cen_0",
                "Peak_at_100_ppm_gamma_0",
            ],
        )

    def test_sort_params_one_voigt_one_spectrum(self):
        self.add_n_spectra(1)
        params = self.prefitter._generate_params_list()
        param_dict_list = functions.generate_spectra_param_dict(params)
        self.assertDictEqual(
            param_dict_list, {0: [[-200.0, 150.0, 1.5, 1.5, "gam"]]}
        )

    def test_sort_params_two_voigt_one_spectrum_user_def_sigma_max(self):
        self.add_n_spectra(1)
        self.ds.add_peak(120, line_broadening={"sigma": {"max": 2}})
        params = self.prefitter._generate_params_list()
        param_dict_list = functions.generate_spectra_param_dict(params)
        self.assertDictEqual(
            param_dict_list,
            {
                0: [
                    [-200.0, 150.0, 1.5, 1.5, "gam"],
                    [-200.0, 120.0, 1.0, 1.5, "gam"],
                ]
            },
        )

    def test_sort_params_voigt_gauss_lorentz_one_spectrum(self):
        self.add_n_spectra(1)
        self.ds.add_peak(120, fitting_type="gauss")
        self.ds.add_peak(100, fitting_type="lorentz")
        params = self.prefitter._generate_params_list()
        param_dict_list = functions.generate_spectra_param_dict(params)
        self.assertDictEqual(
            param_dict_list,
            {
                0: [
                    [-200.0, 150.0, 1.5, 1.5, "gam"],
                    [-200.0, 120.0, 1.5],
                    [-200.0, 100.0, 1.5, "gam"],
                ]
            },
        )

    def test_spectral_fitting_one_gauss_prefit(self):
        self.add_n_spectra(1, type=["gauss"])
        self.ds.peak_list[0].fitting_type = "gauss"
        self.ds.peak_list[0].peak_sign = "+"
        x_axis, y_axis = self.prefitter._generate_axis_list()
        params = self.prefitter._generate_params_list()
        params["Peak_at_150_ppm_sigma_0"].value = 3

        residual = self.prefitter._spectral_fitting(params, x_axis, y_axis)
        self.assertEqual(sum(residual), 0)

    def test_spectral_fitting_one_lorentz_prefit(self):
        self.add_n_spectra(1, type=["lorentz"])
        self.ds.peak_list[0].fitting_type = "lorentz"
        self.ds.peak_list[0].peak_sign = "+"
        x_axis, y_axis = self.prefitter._generate_axis_list()
        params = self.prefitter._generate_params_list()
        params["Peak_at_150_ppm_gamma_0"].value = 4
        params["Peak_at_150_ppm_cen_0"].max = 200
        params["Peak_at_150_ppm_cen_0"].value = 200
        residual = self.prefitter._spectral_fitting(params, x_axis, y_axis)
        self.assertAlmostEqual(sum(residual), 0, delta=5)

    def test_prefiter_fit_one_voigt(self):
        self.add_n_spectra(1)
        self.prefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        result = self.prefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListEqual(value_list, [200, 250, 2, 2])

    def test_prefiter_fit_voigt_gauss(self):
        self.add_n_spectra(1, type=["voigt", "gauss"])
        self.ds.add_peak(210, fitting_type="gauss")
        self.prefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        self.prefitter.dataset.peak_list[1].peak_center = 150
        self.prefitter.dataset.peak_list[1].peak_sign = "+"
        result = self.prefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListEqual(value_list, [200, 250, 2, 2, 200, 150, 3])

    def test_prefitter_fit_voigt_gauss(self):
        self.add_n_spectra(1, type=["voigt", "gauss", "lorentz"])
        self.ds.add_peak(210, fitting_type="gauss", peak_sign="+")
        self.ds.add_peak(200, fitting_type="lorentz", peak_sign="+")
        self.prefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        self.prefitter.dataset.peak_list[1].peak_center = 150
        self.prefitter.dataset.peak_list[1].peak_sign = "+"
        result = self.prefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListEqual(
            value_list, [204, 250, 2, 2, 200, 150, 3, 171, 200, 3]
        )

    def test_prefiter_fit_one_voigt_add_noise_test_amop_cen(self):
        self.add_n_spectra(1)
        self.ds.spectra[0].y_axis = self.add_noise(self.ds.spectra[0].y_axis)
        self.prefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        result = self.prefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListAlmostEqual(value_list[:2], [200, 250], delta=10)

    def test_prefiter_fit_one_voigt_add_noise_test_lw(self):
        self.add_n_spectra(1)
        self.ds.spectra[0].y_axis = self.add_noise(self.ds.spectra[0].y_axis)
        self.prefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        result = self.prefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListAlmostEqual(value_list[2:], [2, 2], delta=0.01)

    def test_prefiter_fit_voigt_gauss_with_noise(self):
        self.add_n_spectra(1, type=["voigt", "gauss", "lorentz"])
        self.ds.add_peak(210, fitting_type="gauss", peak_sign="+")
        self.ds.add_peak(200, fitting_type="lorentz", peak_sign="+")
        self.ds.spectra[0].y_axis = self.add_noise(self.ds.spectra[0].y_axis)
        self.prefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        self.prefitter.dataset.peak_list[1].peak_center = 150
        self.prefitter.dataset.peak_list[1].peak_sign = "+"
        result = self.prefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListAlmostEqual(
            value_list, [200, 250, 2, 2, 200, 150, 3, 200, 200, 4], delta=40
        )

    def test_generate_axis_list_global_fitter_nr_elements_x(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        self.assertEqual(len(x_axis), 3)

    def test_generate_axis_list_global_fitter_nr_elements_y(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        self.assertEqual(len(y_axis), 3)

    def test_generate_axis_list_global_fitter_corect_x_val(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        self.assertTrue(
            np.array_equal(x_axis[1], np.linspace(100, 350, 1000))
        )

    def test_generate_axis_list_global_fitter_corect_y_val(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        max_list = []
        for vals in y_axis:
            max_list.append(int(max(vals)))
        self.assertListEqual(max_list, [20, 41, 62])

    def test_generate_axis_list_single_fitter_nr_elements_x(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.singlefitter._generate_axis_list()
        self.assertEqual(len(x_axis), 3)

    def test_generate_axis_list_single_fitter_nr_elements_y(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.singlefitter._generate_axis_list()
        self.assertEqual(len(y_axis), 3)

    def test_generate_axis_list_single_fitter_corect_x_val(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.singlefitter._generate_axis_list()
        self.assertTrue(
            np.array_equal(x_axis[1], np.linspace(100, 350, 1000))
        )

    def test_generate_axis_list_single_fitter_corect_y_val(self):
        self.add_n_spectra(3)
        x_axis, y_axis = self.globalfitter._generate_axis_list()
        max_list = []
        for vals in y_axis:
            max_list.append(int(max(vals)))
        self.assertListEqual(max_list, [20, 41, 62])

    def test_generate_param_list_two_spectra_global_fitter(self):
        self.add_n_spectra(2)
        params = self.globalfitter._generate_params_list()
        keylist = []
        for keys in params.keys():
            keylist.append(keys)
        self.assertListEqual(
            keylist,
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
                "Peak_at_150_ppm_amp_1",
                "Peak_at_150_ppm_cen_1",
                "Peak_at_150_ppm_sigma_1",
                "Peak_at_150_ppm_gamma_1",
            ],
        )

    def test_generate_param_list_two_spectra_single_fitter(self):
        self.add_n_spectra(2)
        params = self.singlefitter._generate_params_list()
        keylist = []
        for keys in params.keys():
            keylist.append(keys)
        self.assertListEqual(
            keylist,
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
                "Peak_at_150_ppm_amp_1",
                "Peak_at_150_ppm_cen_1",
                "Peak_at_150_ppm_sigma_1",
                "Peak_at_150_ppm_gamma_1",
            ],
        )

    def test_generate_param_list_two_spectra_two_peaks_single_fitter(self):
        self.add_n_spectra(2)
        self.ds.add_peak(120, fitting_type="gauss")
        params = self.singlefitter._generate_params_list()
        keylist = []
        for keys in params.keys():
            keylist.append(keys)
        self.assertListEqual(
            keylist,
            [
                "Peak_at_150_ppm_amp_0",
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
                "Peak_at_120_ppm_amp_0",
                "Peak_at_120_ppm_cen_0",
                "Peak_at_120_ppm_sigma_0",
                "Peak_at_150_ppm_amp_1",
                "Peak_at_150_ppm_cen_1",
                "Peak_at_150_ppm_sigma_1",
                "Peak_at_150_ppm_gamma_1",
                "Peak_at_120_ppm_amp_1",
                "Peak_at_120_ppm_cen_1",
                "Peak_at_120_ppm_sigma_1",
            ],
        )

    def test_singlefitter_fit_one_voigt_three_spectra(self):
        self.add_n_spectra(3)
        self.singlefitter.dataset.peak_list[0].peak_center = 250
        self.prefitter.dataset.peak_list[0].peak_sign = "+"
        self.singlefitter.dataset.peak_list[1].peak_center = 250
        self.prefitter.dataset.peak_list[1].peak_sign = "+"
        self.singlefitter.dataset.peak_list[2].peak_center = 250
        self.prefitter.dataset.peak_list[2].peak_sign = "+"
        result = self.singlefitter.fit()
        value_list = []
        for key in result.params:
            value_list.append(round(result.params[key].value))
        self.assertListEqual(
            value_list, [200, 250, 2, 2, 400, 250, 2, 2, 600, 250, 2, 2]
        )

    def test_set_param_expr_global_fitter(self):
        self.add_n_spectra(2)
        params = self.globalfitter._generate_params_list()
        params = self.globalfitter._set_param_expr(params)
        keylist = []
        for key in params.keys():
            keylist.append(params[key].expr)
        self.assertListEqual(
            keylist,
            [
                None,
                None,
                None,
                None,
                None,
                "Peak_at_150_ppm_cen_0",
                "Peak_at_150_ppm_sigma_0",
                "Peak_at_150_ppm_gamma_0",
            ],
        )

    def test_buildup_fitter_init_type_exp(self):
        self.add_one_peak()
        fitter = utils.ExpFitter(self.ds)
        self.assertEqual(type(fitter), utils.ExpFitter)

    def test_buildup_fitter_init_ds_exp(self):
        self.add_one_peak()
        fitter = utils.ExpFitter(self.ds)
        self.assertEqual(type(fitter.dataset), dataset.Dataset)

    def test_buildup_fitter_init_type_biexp(self):
        self.add_one_peak()
        fitter = utils.BiexpFitter(self.ds)
        self.assertEqual(type(fitter), utils.BiexpFitter)

    def test_buildup_fitter_init_ds_biexp(self):
        self.add_one_peak()
        fitter = utils.BiexpFitter(self.ds)
        self.assertEqual(type(fitter.dataset), dataset.Dataset)

    def test_buildup_fitter_init_type_biexpoff(self):
        self.add_one_peak()
        fitter = utils.BiexpFitterWithOffset(self.ds)
        self.assertEqual(type(fitter), utils.BiexpFitterWithOffset)

    def test_buildup_fitter_init_ds_bieexpoff(self):
        self.add_one_peak()
        fitter = utils.BiexpFitterWithOffset(self.ds)
        self.assertEqual(type(fitter.dataset), dataset.Dataset)

    def test_buildup_fitter_init_type_expoff(self):
        self.add_one_peak()
        fitter = utils.ExpFitterWithOffset(self.ds)
        self.assertEqual(type(fitter), utils.ExpFitterWithOffset)

    def test_biexp_fitter_get_default_param_dict(self):
        self.add_one_peak()
        fitter = utils.BiexpFitter(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": 0, "max": 70351.43997489079}
        self.check_dict(param_dict, a_dict)

    def test_biexp_fitter_get_default_param_dict_correct_number_of_keys(self):
        self.add_one_peak()
        fitter = utils.BiexpFitter(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        self.assertEqual(len(param_dict.keys()), 4)

    def test_biexp_fitter_get_default_param_dict_negative(self):
        self.add_one_peak()
        fitter = utils.BiexpFitter(self.ds)
        self.ds.peak_list[0].peak_sign = "-"
        self.ds.peak_list[0].buildup_vals.intensity = [
            -x for x in self.ds.peak_list[0].buildup_vals.intensity
        ]
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": -70351.43997489079, "max": 0}
        self.check_dict(param_dict, a_dict)

    def test_exp_fitter_get_default_param_dict(self):
        self.add_one_peak()
        fitter = utils.ExpFitter(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": 0, "max": 70351.43997489079}
        self.check_dict(param_dict, a_dict)

    def test_exp_fitter_get_default_param_dict_correct_number_of_keys(self):
        self.add_one_peak()
        fitter = utils.ExpFitter(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        self.assertEqual(len(param_dict.keys()), 2)

    def test_exp_fitter_get_default_param_dict_negative(self):
        self.add_one_peak()
        fitter = utils.ExpFitter(self.ds)
        self.ds.peak_list[0].peak_sign = "-"
        self.ds.peak_list[0].buildup_vals.intensity = [
            -x for x in self.ds.peak_list[0].buildup_vals.intensity
        ]
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": -70351.43997489079, "max": 0}
        self.check_dict(param_dict, a_dict)

    def test_biexp_offset_fitter_get_default_param_dict(self):
        self.add_one_peak()
        fitter = utils.BiexpFitterWithOffset(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": 0, "max": 70351.43997489079}
        self.check_dict(param_dict, a_dict)

    def test_biexp_fitter_get_default_param_dict_correct_number_of_keys(self):
        self.add_one_peak()
        fitter = utils.BiexpFitterWithOffset(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        self.assertEqual(len(param_dict.keys()), 5)

    def test_biexp_fitter_get_default_param_dict_negative(self):
        self.add_one_peak()
        fitter = utils.BiexpFitterWithOffset(self.ds)
        self.ds.peak_list[0].peak_sign = "-"
        self.ds.peak_list[0].buildup_vals.intensity = [
            -x for x in self.ds.peak_list[0].buildup_vals.intensity
        ]
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": -70351.43997489079, "max": 0}
        self.check_dict(param_dict, a_dict)

    def test_exp_offset_fitter_get_default_param_dict(self):
        self.add_one_peak()
        fitter = utils.ExpFitterWithOffset(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": 0, "max": 70351.43997489079}
        self.check_dict(param_dict, a_dict)

    def test_exp_fitter_get_default_param_dict_correct_number_of_keys(self):
        self.add_one_peak()
        fitter = utils.ExpFitterWithOffset(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        self.assertEqual(len(param_dict.keys()), 3)

    def test_exp_fitter_get_default_param_dict_negative(self):
        self.add_one_peak()
        fitter = utils.ExpFitterWithOffset(self.ds)
        self.ds.peak_list[0].peak_sign = "-"
        self.ds.peak_list[0].buildup_vals.intensity = [
            -x for x in self.ds.peak_list[0].buildup_vals.intensity
        ]
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        a_dict = {"value": 10, "min": -70351.43997489079, "max": 0}
        self.check_dict(param_dict, a_dict)

    def test_buidlup_fitter_get_param_bounds(self):
        self.add_one_peak()
        fitter = utils.ExpFitterWithOffset(self.ds)
        param_dict = fitter._get_default_param_dict(self.ds.peak_list[0])
        result = fitter._get_param_bounds({"value": 5, "min": 0, "max": 5})
        self.assertEqual(result, (0, 5))

    def test_buildup_fitter_get_init_params_list(self):
        self.add_one_peak()
        result = self.calc_lhs_init_params(utils.ExpFitterWithOffset(self.ds))
        self.assertEqual(type(result), list)

    def test_buildup_fitter_get_init_params_list_of_lists(self):
        self.add_one_peak()
        result = self.calc_lhs_init_params(utils.ExpFitterWithOffset(self.ds))
        for lists in result:
            self.assertEqual(type(lists), list)

    def test_buildup_fitter_get_init_params_list_two_items(self):
        self.add_one_peak()
        result = self.calc_lhs_init_params(utils.ExpFitterWithOffset(self.ds))
        self.assertEqual(len(result), 2)

    def test_buildup_fitter_get_init_params_list_of_lists(self):
        self.add_one_peak()
        result = self.calc_lhs_init_params(utils.ExpFitterWithOffset(self.ds))
        for lists in result:
            self.assertEqual(len(lists), 3)

    def test_buildup_fitter_get_init_params_lists_correct_len(self):
        self.add_one_peak()
        result = self.calc_lhs_init_params(
            utils.BiexpFitterWithOffset(self.ds)
        )
        for lists in result:
            self.assertEqual(len(lists), 5)

    def test_set_params_is_lmfit_params(self):
        self.add_one_peak()
        params = self.calc_params(utils.ExpFitter(self.ds))
        self.assertEqual(type(params), lmfit.Parameters)

    def test_set_params_exp(self):
        self.add_one_peak()
        params = self.calc_params(utils.ExpFitter(self.ds))
        self.assertEqual(list(params.keys()), ["Af", "tf"])

    def test_set_params_biexp(self):
        self.add_one_peak()
        params = self.calc_params(utils.BiexpFitter(self.ds))
        self.assertEqual(list(params.keys()), ["Af", "As", "tf", "ts"])

    def test_set_params_biexp_offset(self):
        self.add_one_peak()
        params = self.calc_params(utils.BiexpFitterWithOffset(self.ds))
        self.assertEqual(
            list(params.keys()), ["Af", "As", "tf", "ts", "t_off"]
        )

    def test_set_params_exp_offset(self):
        self.add_one_peak()
        params = self.calc_params(utils.ExpFitterWithOffset(self.ds))
        self.assertEqual(list(params.keys()), ["Af", "tf", "t_off"])

    def test_set_params_biexp_offset(self):
        self.add_one_peak()
        fitter = utils.BiexpFitterWithOffset(self.ds)
        params = self.calc_params(fitter)
        param_list = fitter._generate_param_list(params)
        self.assertEqual(len(param_list), 5)

    def test_biexp_fitter_calc_intensity(self):
        fitter = utils.BiexpFitter(self.ds)
        result = fitter._calc_intensity([1, 2, 3], [20, 10, 2, 8])
        result = [int(val) for val in result]
        expected_vals = [9, 14, 18]
        self.assertListEqual(result, expected_vals)

    def test_exp_fitter_calc_intensity(self):
        fitter = utils.ExpFitter(self.ds)
        result = fitter._calc_intensity(
            [1, 2, 3],
            [
                20,
                2,
            ],
        )
        expected_vals = [
            7.8693868057473315,
            12.642411176571153,
            15.537396797031404,
        ]
        self.assertListEqual(result, expected_vals)

    def test_exp_offset_fitter_calc_intensity(self):
        fitter = utils.ExpFitterWithOffset(self.ds)
        result = fitter._calc_intensity([1, 2, 3], [20, 2, -2])
        expected_vals = [
            15.537396797031404,
            17.293294335267746,
            18.358300027522024,
        ]
        self.assertListEqual(result, expected_vals)

    def test_biexp_offset_fitter_calc_intensity(self):
        fitter = utils.BiexpFitterWithOffset(self.ds)
        result = fitter._calc_intensity([1, 2, 3], [20, 10, 2, 8, -2])
        expected_vals = [
            18.664504009121682,
            21.22798773814141,
            23.00568574233212,
        ]
        self.assertListEqual(result, expected_vals)
