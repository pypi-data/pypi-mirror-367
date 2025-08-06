import unittest
import screamlab.dataset
from screamlab import io, dataset
from pathlib import Path
import os


class TestDataset(unittest.TestCase):

    def setUp(self):
        self.scream_importer = io.ScreamImporter(dataset.Dataset())
        self.pseudo_importer = io.Pseudo2DImporter(dataset.Dataset())
        self.lmfit_result = io.LmfitResultHandler()

    def set_up_one_real_spectrum(self):
        self.scream_importer._dataset.spectra.append(
            screamlab.dataset.Spectra()
        )

        test_dir = Path(__file__).parent
        self.scream_importer.file = rf"{test_dir}/SCREAM_Test_Files/Alanin/8"

    def set_up_real_dataset(self):
        test_dir = Path(__file__).parent
        self.scream_importer._dataset.props.procno = 103
        self.scream_importer._dataset.props.expno = [1, 8]
        self.scream_importer._dataset.props.path_to_experiment = (
            rf"{test_dir}/SCREAM_Test_Files/Alanin"
        )

    def test_scream_init_set_dataset(self):
        self.assertEqual(
            type(self.scream_importer._dataset), screamlab.dataset.Dataset
        )

    def test_scream_init_path_is_none(self):
        self.assertIsNone(self.scream_importer._current_path_to_exp)

    def test_scream_init_nmr_data_is_none(self):
        self.assertIsNone(self.scream_importer._nmr_data)

    def test_add_one_spectrum(self):
        self.scream_importer._add_spectrum()
        self.assertEqual(len(self.scream_importer._dataset.spectra), 1)

    def test_add_spectrum_is_list(self):
        self.scream_importer._add_spectrum()
        self.assertEqual(type(self.scream_importer._dataset.spectra), list)

    def test_add_spectrum_is_list_of_Spectra(self):
        self.scream_importer._add_spectrum()
        self.assertEqual(
            type(self.scream_importer._dataset.spectra[0]),
            screamlab.dataset.Spectra,
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_number_of_scans_2(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_number_of_scans()
        self.assertEqual(
            self.scream_importer._dataset.spectra[-1].number_of_scans, 16
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_buildup_time(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_buildup_time()
        self.assertEqual(self.scream_importer._dataset.spectra[-1].tpol, 32)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_buildup_time_is_float(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_buildup_time()
        self.assertEqual(
            type(self.scream_importer._dataset.spectra[-1].tpol), float
        )

    def test_set_get_physical_range(self):
        self.set_up_one_real_spectrum()
        range = self.scream_importer._get_physical_range()
        self.assertDictEqual(range, {"start": 169.4191, "end": -244.3311})

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_get_number_of_datapoints(self):
        self.set_up_one_real_spectrum()
        points = self.scream_importer._get_num_of_datapoints()
        self.assertEqual(points, 16384)

    def test_calc_x_axis_correct_length(self):
        self.set_up_one_real_spectrum()
        physical_range = {"start": 150, "end": -200}
        axis_length = len(
            self.scream_importer._calc_x_axis(physical_range, 350)
        )
        self.assertEqual(axis_length, 350)

    def test_calc_x_axis_correct_start_value(self):
        self.set_up_one_real_spectrum()
        physical_range = {"start": 150, "end": -200}
        axis = self.scream_importer._calc_x_axis(physical_range, 350)
        self.assertEqual(axis[0], 150)

    def test_calc_x_axis_correct_end_value(self):
        self.set_up_one_real_spectrum()
        physical_range = {"start": 150, "end": -200}
        axis = self.scream_importer._calc_x_axis(physical_range, 350)
        self.assertEqual(axis[-1], -200)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_y_data(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_y_data()
        self.assertEqual(
            len(self.scream_importer._dataset.spectra[0].y_axis), 16384
        )

    def test_set_values(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_values()
        norm_maximum = max(self.scream_importer._dataset.spectra[0].y_axis)
        self.assertEqual(norm_maximum, 5693.3125)

    def test_scream_import_topspin_correct_number_of_data(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        self.assertEqual(len(self.scream_importer._dataset.spectra), 8)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_delay_times(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(spectrum.tpol)
        self.assertListEqual(
            delay_times, [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_number_of_scans(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(spectrum.number_of_scans)
        self.assertListEqual(delay_times, [128, 128, 128, 64, 64, 32, 32, 16])

    def test_scream_import_topspin_correct_size_of_x_axis(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(len(spectrum.x_axis))
        self.assertListEqual(delay_times, [16384] * 8)

    def test_scream_import_topspin_correct_size_of_y_axis(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(len(spectrum.y_axis))
        self.assertListEqual(delay_times, [16384] * 8)

    def test_init_lmfit_result_handler_prefit(self):
        self.assertEqual(self.lmfit_result.prefit, None)

    def test_init_lmfit_result_handler_single_fit(self):
        self.assertEqual(self.lmfit_result.single_fit, None)

    def test_init_lmfit_result_handler_sglobal_fit(self):
        self.assertEqual(self.lmfit_result.global_fit, None)

    def test_init_lmfit_result_handler_buidlup_fit(self):
        self.assertEqual(self.lmfit_result.buildup_fit, {})

    def test_pseudo2dimporter_init_set_dataset(self):
        self.assertEqual(
            type(self.pseudo_importer._dataset), screamlab.dataset.Dataset
        )

    def test_pseudo2dimporter_init_path_is_none(self):
        self.assertIsNone(self.pseudo_importer._current_path_to_exp)

    def test_add_one_spectrump_seudo2dimporter(self):
        self.pseudo_importer._add_spectrum()
        self.assertEqual(len(self.pseudo_importer._dataset.spectra), 1)

    def test_add_spectrum_is_list_pseudo2dimporter(self):
        self.pseudo_importer._add_spectrum()
        self.assertEqual(type(self.pseudo_importer._dataset.spectra), list)

    def test_add_spectrum_is_list_of_spectra_pseudo2dimporter(self):
        self.pseudo_importer._add_spectrum()
        self.assertEqual(
            type(self.pseudo_importer._dataset.spectra[0]),
            screamlab.dataset.Spectra,
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_buildup_time_2(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_buildup_time()
        self.assertEqual(self.scream_importer._dataset.spectra[-1].tpol, 32)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_buildup_time_is_float_2(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_buildup_time()
        self.assertEqual(
            type(self.scream_importer._dataset.spectra[-1].tpol), float
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_get_physical_range(self):
        self.set_up_one_real_spectrum()
        range = self.scream_importer._get_physical_range()
        self.assertDictEqual(range, {"start": 169.4191, "end": -244.3311})

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_get_number_of_datapoints(self):
        self.set_up_one_real_spectrum()
        points = self.scream_importer._get_num_of_datapoints()
        self.assertEqual(points, 16384)

    def test_calc_x_axis_correct_length(self):
        self.set_up_one_real_spectrum()
        physical_range = {"start": 150, "end": -200}
        axis_length = len(
            self.scream_importer._calc_x_axis(physical_range, 350)
        )
        self.assertEqual(axis_length, 350)

    def test_calc_x_axis_correct_start_value(self):
        self.set_up_one_real_spectrum()
        physical_range = {"start": 150, "end": -200}
        axis = self.scream_importer._calc_x_axis(physical_range, 350)
        self.assertEqual(axis[0], 150)

    def test_calc_x_axis_correct_end_value(self):
        self.set_up_one_real_spectrum()
        physical_range = {"start": 150, "end": -200}
        axis = self.scream_importer._calc_x_axis(physical_range, 350)
        self.assertEqual(axis[-1], -200)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_y_data(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_y_data()
        self.assertEqual(
            len(self.scream_importer._dataset.spectra[0].y_axis), 16384
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_set_values(self):
        self.set_up_one_real_spectrum()
        self.scream_importer._set_values()
        norm_maximum = max(self.scream_importer._dataset.spectra[0].y_axis)
        self.assertEqual(norm_maximum, 5693.3125)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_number_of_data(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        self.assertEqual(len(self.scream_importer._dataset.spectra), 8)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_delay_times_2(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(spectrum.tpol)
        self.assertListEqual(
            delay_times, [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
        )

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_number_of_scans(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(spectrum.number_of_scans)
        self.assertListEqual(delay_times, [128, 128, 128, 64, 64, 32, 32, 16])

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_size_of_x_axis(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(len(spectrum.x_axis))
        self.assertListEqual(delay_times, [16384] * 8)

    @unittest.skipIf(
        os.getenv("CI") == "true", "Skipping test in CI/CD environment"
    )
    def test_scream_import_topspin_correct_size_of_y_axis(self):
        self.set_up_real_dataset()
        self.scream_importer.import_topspin_data()
        delay_times = []
        for spectrum in self.scream_importer._dataset.spectra:
            delay_times.append(len(spectrum.y_axis))
        self.assertListEqual(delay_times, [16384] * 8)
