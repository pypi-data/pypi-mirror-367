import unittest
import os
from screamlab.settings import Properties


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.props = Properties()
        self.props.path_to_experiment = r"..\tests\Pseud2DTestFiles"
        self.props.output_folder = r"\Pseud2DTestFiles"

    def test_prefit_default_value(self):
        self.assertFalse(self.props.prefit)

    def test_prefit_initial_value(self):
        props = Properties(prefit=True)
        self.assertTrue(props.prefit)

    def test_prefit_set_valid_value(self):
        props = Properties()
        props.prefit = True
        self.assertTrue(props.prefit)

    def test_prefit_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.prefit = "invalid"
        self.assertEqual(
            str(context.exception),
            "Expected 'prefit' to be of type 'bool', got str.",
        )

    def test_prefit_change_value(self):
        props = Properties(prefit=False)
        props.prefit = True
        self.assertTrue(props.prefit)

    def test_prefit_private_variable(self):
        props = Properties(prefit=True)
        self.assertTrue(props._prefit)

    def test_buildup_types_default_value(self):
        props = Properties()
        self.assertListEqual(props.buildup_types, ["exponential"])

    def test_buildup_types_initial_value(self):
        props = Properties(buildup_types=["exponential"])
        self.assertListEqual(props.buildup_types, ["exponential"])

    def test_buildup_types_set_valid_value(self):
        props = Properties()
        props.buildup_types = ["exponential", "biexponential"]
        self.assertListEqual(
            props.buildup_types, ["exponential", "biexponential"]
        )

    def test_buildup_types_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.buildup_types = "invalid"
        self.assertEqual(
            str(context.exception),
            "Expected 'buildup_types' to be of type 'list', got str.",
        )

    def test_buildup_types_change_value(self):
        props = Properties(buildup_types=["biexponential"])
        props.buildup_types = ["exponential", "biexponential"]
        self.assertListEqual(
            props.buildup_types, ["exponential", "biexponential"]
        )

    def test_buildup_types_private_variable(self):
        props = Properties(buildup_types=["biexponential"])
        self.assertListEqual(props._buildup_types, ["biexponential"])

    def test_buildup_types_empty_buildup_types(self):
        props = Properties()
        empty_list = []
        with self.assertRaises(ValueError) as context:
            props.buildup_types = empty_list

    def test_buildup_types_invalid_buildup_types_contains_non_strings(self):
        props = Properties()
        with self.assertRaises(ValueError):
            props.buildup_types = ["exponential", 42, "constant"]

    def test_buildup_types_valid_in_possibilities(self):
        props = Properties()
        props.buildup_types = ["exponential", "biexponential"]
        self.assertEqual(
            props.buildup_types, ["exponential", "biexponential"]
        )

    def test_buildup_types_invalid(self):
        props = Properties()
        with self.assertRaises(ValueError) as context:
            props.buildup_types = "invalid"
            self.assertIn("must be one of", str(context.exception))

    def test_spectrum_for_prefit_default_value(self):
        props = Properties()
        self.assertEqual(props.spectrum_for_prefit, -1)

    def test_spectrum_for_prefit_initial_value(self):
        props = Properties(spectrum_for_prefit=1)
        self.assertEqual(props.spectrum_for_prefit, 1)

    def test_spectrum_for_prefit_set_valid_value(self):
        props = Properties()
        props.spectrum_for_prefit = 2
        self.assertEqual(props.spectrum_for_prefit, 2)

    def test_spectrum_for_prefit_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.spectrum_for_prefit = "invalid"
        self.assertEqual(
            str(context.exception),
            "Expected 'spectrum_for_prefit' to be of type 'int', got str.",
        )

    def test_spectrum_for_prefit_change_value(self):
        props = Properties(spectrum_for_prefit=1)
        props.spectrum_for_prefit = 2
        self.assertEqual(props.spectrum_for_prefit, 2)

    def test_spectrum_for_prefitt_private_variable(self):
        props = Properties(spectrum_for_prefit=2)
        self.assertTrue(props._spectrum_for_prefit)

    def test_spectrum_fit_type_default_value(self):
        props = Properties()
        self.assertEqual(props.spectrum_fit_type, "global")

    def test_spectrum_fit_type_initial_value(self):
        props = Properties(spectrum_fit_type="global")
        self.assertEqual(props.spectrum_fit_type, "global")

    def test_spectrum_fit_type_set_valid_value(self):
        props = Properties()
        props.spectrum_fit_type = "global"
        self.assertEqual(props.spectrum_fit_type, "global")

    def test_spectrum_fit_type_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.spectrum_fit_type = ["invalid"]
        self.assertEqual(
            str(context.exception),
            "Expected 'spectrum_fit_type' to be of type 'str', got list.",
        )

    def test_spectrum_fit_type_change_value(self):
        props = Properties(spectrum_fit_type="global")
        props.spectrum_fit_type = "global"
        self.assertEqual(props.spectrum_fit_type, "global")

    def test_spectrum_fit_type_private_variable(self):
        props = Properties(spectrum_fit_type="global")
        self.assertEqual(props._spectrum_fit_type, "global")

    def test_spectrum_fit_type_empty_buildup_types(self):
        props = Properties()
        empty_str = ""
        with self.assertRaises(ValueError) as context:
            props.spectrum_fit_type = empty_str

    def test_spectrum_fit_type_invalid_buildup_types_contains_non_strings(
        self,
    ):
        props = Properties()
        with self.assertRaises(ValueError):
            props.buildup_types = ["exponential", 42, "constant"]

    def test_spectrum_fit_type_valid_in_possibilitys(self):
        props = Properties()
        try:
            props.spectrum_fit_type = "global"
            self.assertEqual(props.spectrum_fit_type, "global")
        except Exception as e:
            self.fail(f"Valid values raised an exception: {e}")

    def test_buildup_types_invalid(self):
        props = Properties()
        with self.assertRaises(ValueError) as context:
            props.spectrum_fit_type = "invalid_type"
        self.assertIn("must be one of", str(context.exception))

    def test_path_to_experiment_initial_value(self):
        props = Properties(path_to_experiment="/testfolder/test/test")
        self.assertEqual(props.path_to_experiment, "/testfolder/test/test")

    def test_path_to_experiment_set_valid_value(self):
        props = Properties()
        props.path_to_experiment = "/testfolder/test/test"
        self.assertEqual(props.path_to_experiment, "/testfolder/test/test")

    def test_path_to_experiment_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.path_to_experiment = 12
        self.assertEqual(
            str(context.exception),
            "Expected 'path_to_experiment' to be of type 'str', got int.",
        )

    def test_path_to_experiment_change_value(self):
        props = Properties(path_to_experiment="/testfolder/test")
        props.path_to_experiment = "/testfolder/test/test"
        self.assertTrue(props.path_to_experiment, "/testfolder/test/test")

    def test_path_to_experiment_private_variable(self):
        props = Properties(path_to_experiment="/testfolder/test/test")
        self.assertEqual(props._path_to_experiment, "/testfolder/test/test")

    def test_procno_default_value(self):
        props = Properties()
        self.assertEqual(props.procno, "103")

    def test_procno_initial_value(self):
        props = Properties(procno=102)
        self.assertEqual(props.procno, "102")

    def test_procno_set_valid_value(self):
        props = Properties()
        props.procno = 111
        self.assertEqual(props.procno, "111")

    def test_procno_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.procno = "12"
        self.assertEqual(
            str(context.exception),
            "Expected 'procno' to be of type 'int', got str.",
        )

    def test_procno_change_value(self):
        props = Properties(procno=111)
        props.procno = 2
        self.assertTrue(props.procno, "2")

    def test_procno_private_variable(self):
        props = Properties(procno=2)
        self.assertEqual(props._procno, "2")

    def test_expno_default_value(self):
        props = Properties()
        self.assertListEqual(props.expno, ["1"])

    def test_expno_initial_value(self):
        props = Properties(expno=[23, 50])
        self.assertListEqual(
            props.expno, [str(item) for item in list(range(23, 51))]
        )

    def test_expno_set_valid_value(self):
        props = Properties()
        props.expno = [111]
        self.assertListEqual(props.expno, ["111"])

    def test_expno_set_invalid_value(self):
        props = Properties()
        with self.assertRaises(TypeError) as context:
            props.expno = "12"
        self.assertEqual(
            str(context.exception),
            "Expected 'expno' to be of type 'list', got str.",
        )

    def test_expno_set_not_int_value(self):
        props = Properties()
        with self.assertRaises(ValueError) as context:
            props.expno = [1, "12"]
        self.assertEqual(
            str(context.exception),
            "All elements in the 'expno' list must be of type 'int'.",
        )

    def test_expno_change_value(self):
        props = Properties(expno=[111])
        props.expno = [111, 112]
        self.assertListEqual(props.expno, ["111", "112"])

    def test_expno_private_variable(self):
        props = Properties(expno=[2])
        self.assertListEqual(props._expno, ["2"])
