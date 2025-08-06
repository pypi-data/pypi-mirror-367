"""The `settings` module is responsible for managing configuration options."""

from typing import Any
import os


class Properties:
    """A class to manage and validate properties related to spectral fitting and buildup types."""

    def __init__(
        self,
        prefit: bool = False,
        buildup_types: list = None,
        spectrum_fit_type: str = None,
        spectrum_for_prefit: int = -1,
        path_to_experiment: str = "",
        procno: int = 103,
        expno: list = None,
        output_folder: str = "",
        subspec=None,
    ):
        self.init_call = True
        if buildup_types is None:
            buildup_types = ["exponential"]
        if spectrum_fit_type is None:
            spectrum_fit_type = "global"
        if expno is None:
            expno = [1]
        self._path_to_experiment = None
        self.path_to_experiment = path_to_experiment
        self._procno = None
        self.procno = procno
        self._expno = None
        self.expno = expno
        self._prefit = None
        self.prefit = prefit
        self._buildup_types = None
        self.buildup_types = buildup_types
        self._spectrum_for_prefit = None
        self.spectrum_for_prefit = spectrum_for_prefit
        self._spectrum_fit_type = None
        self.spectrum_fit_type = spectrum_fit_type
        self.loop20 = "L 20"
        self.delay20 = "D 20"

        self._output_folder = None
        self.output_folder = output_folder
        self._subspec = None
        self.subspec = subspec
        self.init_call = False

    def __str__(self):
        """Returns string representation of Properties class"""
        sub = (
            f"A subspectrum ranging from {self.subspec[0]} to {self.subspec[1]} "
            f"ppm has been extracted."
            if self.subspec
            else "No subspectrum has been extracted."
        )
        return (
            f"[[Settings]]\n"
            f"Experiment folder: {self.path_to_experiment}\n"
            f"Expno: {self.expno}\n"
            f"Procno: {self.procno}\n"
            f"Prefit: {self.prefit}\n"
            f"Spectrum for prefit: {self.spectrum_for_prefit}\n"
            f"Spectrum fitting type: {self.spectrum_fit_type}\n"
            f"Buildup evaluation: {self.buildup_types}\n"
            f"Wrote output to: {self.output_folder}\n"
            f"{sub}"
        )

    @property
    def subspec(self) -> list:
        """
        List of int, optional: Specifies region of subspectrum.

        Default is None.
        """
        return self._subspec

    @subspec.setter
    def subspec(self, value: Any):
        """Sets list for subspectrum"""
        if value is not None:
            self._subspec = value
        else:
            self._subspec = []

    @property
    def output_folder(self) -> str:
        """
        str: The current folder path where the output is being saved.

        Folder path for saving output.

        Default is an empty string ("").
        """
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: Any):
        """Set the folder path for saving output."""
        if not isinstance(value, str):
            raise TypeError(
                f"Expected 'output_folder' to be of type 'str', got {type(value).__name__}."
            )
        if not os.path.exists(f"{value}") and not self.init_call:
            os.makedirs(f"{value}")

        self._output_folder = value

    @property
    def expno(self) -> list:
        """
        List of int: List of experiment numbers (expno; TopSpin) that should be used for analysis.

        Two different input formats are allowed. [1, 8] means using all experiment numbers
        between 1 and 8, while [1, 3, 5, 7, 8] allows for a specific selection.

        Default is None.
        """
        return self._expno

    @expno.setter
    def expno(self, value: Any):
        """Set the expno list."""
        if not isinstance(value, list):
            raise TypeError(
                f"Expected 'expno' to be of type 'list', got {type(value).__name__}."
            )
        if not all(isinstance(item, int) for item in value):
            raise ValueError(
                "All elements in the 'expno' list must be of type 'int'."
            )
        if len(value) == 2:
            value = list(range(value[0], value[-1] + 1))
        self._expno = [str(item) for item in value]

    @property
    def procno(self) -> int:
        """
        int, optional: Processing number according to Bruker's TopSpin

        Default is 103 (standard in SCREAM-DNP experiments).
        """
        return self._procno

    @procno.setter
    def procno(self, value: Any):
        """Set the procno"""
        if not isinstance(value, int):
            raise TypeError(
                f"Expected 'procno' to be of type 'int', got {type(value).__name__}."
            )
        self._procno = str(value)

    @property
    def path_to_experiment(self) -> str:
        """
        str: Path to the experiment data.

        Returns the path where experiment-related data is stored.
        This is typically a directory path in string format.

        Default is an empty string ("").
        """
        return self._path_to_experiment

    @path_to_experiment.setter
    def path_to_experiment(self, value: Any):
        """Sets the path to the experiment data."""
        if not isinstance(value, str):
            raise TypeError(
                f"Expected 'path_to_experiment' to be of type 'str', got {type(value).__name__}."
            )
        self._path_to_experiment = value

    @property
    def spectrum_fit_type(self) -> list:
        """
        str, optional: A list specifying the spectrum fit type

        Options supporded: "global","independent".

        """
        return self._spectrum_fit_type

    @spectrum_fit_type.setter
    def spectrum_fit_type(self, value: Any):
        """Sets the spectrum fit type"""
        allowed_values = {
            "global",
            "individual",
        }
        if not isinstance(value, str):
            raise TypeError(
                f"Expected 'spectrum_fit_type' to be of type 'str', got"
                f" {type(value).__name__}."
            )
        if value not in allowed_values:
            raise ValueError(
                f"'spectrum_fit_type' must be one of {allowed_values}."
            )
        if not value:
            raise ValueError("'spectrum_fit_type' cannot be an empty str.")
        self._spectrum_fit_type = value

    @property
    def buildup_types(self) -> list:
        """
        List of str, optional: A list of buildup function types

        Options supporded: "exponential","biexponential", "exponential_with_offset",
        "biexponential_with_offset", "stretched_exponential".

        Default is ["exponential"].

        """
        return self._buildup_types

    @buildup_types.setter
    def buildup_types(self, value: Any):
        """Sets buildup type list"""
        allowed_values = {
            "exponential",
            "biexponential",
            "biexponential_with_offset",
            "exponential_with_offset",
            "streched_exponential",
        }
        if not isinstance(value, list):
            raise TypeError(
                f"Expected 'buildup_types' to be of type 'list', got {type(value).__name__}."
            )
        if not all(item in allowed_values for item in value):
            raise ValueError(
                f"All elements in 'buildup_types' must be one of {allowed_values}."
            )
        if not value:
            raise ValueError("'buildup_types' cannot be an empty list.")
        self._buildup_types = value

    @property
    def prefit(self) -> bool:
        """
        bool, optional: Indicates whether a prefit should be performed or not.

        Default is False.

        """
        return self._prefit

    @prefit.setter
    def prefit(self, value: Any):
        """Sets prefit to True or False"""
        if not isinstance(value, bool):
            raise TypeError(
                f"Expected 'prefit' to be of type 'bool', got {type(value).__name__}."
            )
        self._prefit = value

    @property
    def spectrum_for_prefit(self) -> int:
        """
        int, optional: Specifies the spectrum used for prefit.

        Default is -1, meaning the last spectrum in
        :obj:`screamlab.settings.Spectra`.

        """
        return self._spectrum_for_prefit

    @spectrum_for_prefit.setter
    def spectrum_for_prefit(self, value: Any):
        """Sets spectrum for prefit."""
        if not isinstance(value, int):
            raise TypeError(
                f"Expected 'spectrum_for_prefit' to be of type 'int', got {type(value).__name__}."
            )
        self._spectrum_for_prefit = value
