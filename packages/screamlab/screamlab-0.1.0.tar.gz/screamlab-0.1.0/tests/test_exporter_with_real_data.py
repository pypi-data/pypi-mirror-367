import unittest
import os
import lmfit
import shutil
from pathlib import Path
from screamlab import settings, dataset


@unittest.skipIf(
    os.getenv("CI") == "true", "Skipping test in CI/CD environment"
)
class TestDataset(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = Path(__file__).parent
        output_folder = rf"{test_dir}\SCREAM_Test_Files\Alanin\result"
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        self.props = settings.Properties()
        self.props.prefit = True
        self.props.spectrum_for_prefit = -2
        self.props.buildup_types = [
            "exponential",
            "exponential_with_offset",
            "biexponential",
            "streched_exponential",
            "biexponential_with_offset",
        ]
        self.props.spectrum_fit_type = "global"
        self.props.expno = [1, 8]
        self.props.procno = 103
        self.props.path_to_experiment = (
            rf"{test_dir}/SCREAM_Test_Files/Alanin"
        )
        self.props.output_folder = (
            rf"{test_dir}/SCREAM_Test_Files/Alanin/result"
        )
        self.ds = dataset.Dataset()
        self.ds.props = self.props
        self.ds.add_peak(-16.5, peak_sign="+", fitting_type="lorentz")
        self.ds.start_analysis()

    def test_results_folder_exists(self):
        self.assertTrue(os.path.exists(self.props.output_folder))

    def test_buildup_plot_exists(self):
        self.assertTrue(
            os.path.exists(rf"{self.props.output_folder}/buildup_plots")
        )

    def test_lmfit_reports_exists(self):
        self.assertTrue(
            os.path.exists(rf"{self.props.output_folder}/lmfit_reports")
        )

    def test_spectra_exists(self):
        self.assertTrue(
            os.path.exists(rf"{self.props.output_folder}/spectra")
        )

    def test_spec_deconv_exists(self):
        self.assertTrue(
            os.path.exists(
                rf"{self.props.output_folder}/spectral_deconvolution_plots"
            )
        )

    def test_tabular_results_exists(self):
        self.assertTrue(
            os.path.exists(rf"{self.props.output_folder}/tabular_results")
        )

    def test_buildup_plots_contains_correct_number_of_files(self):
        self.assertEqual(
            len(os.listdir(rf"{self.props.output_folder}/buildup_plots")), 10
        )

    def test_lmfit_reports_contains_correct_number_of_files(self):
        self.assertEqual(
            len(os.listdir(rf"{self.props.output_folder}/lmfit_reports")), 6
        )

    def test_spectra_contains_correct_number_of_files(self):
        self.assertEqual(
            len(os.listdir(rf"{self.props.output_folder}/spectra")), 3
        )

    def test_spec_deconv_contains_correct_number_of_files(self):
        self.assertEqual(
            len(
                os.listdir(
                    rf"{self.props.output_folder}/spectral_deconvolution_plots"
                )
            ),
            19,
        )

    def test_spec_deconv_contains_correct_number_of_files(self):
        self.assertEqual(
            len(os.listdir(rf"{self.props.output_folder}/tabular_results")), 6
        )
