"""io module of the screamlab package."""

import copy
import csv
import math
import os

import numpy as np
import matplotlib.pyplot as plt
import nmrglue as ng
import lmfit
import screamlab


class TopspinImporter:
    """Class for importing NMR data from Bruker's TopSpin software."""

    def __init__(self, ds):
        """Initialize the TopspinImporter."""
        self._dataset = ds
        self.file = None
        self._current_path_to_exp = None
        self._nmr_data = None

    def _set_values(self):
        """Set internal values including scans, buildup time, x and y data."""
        self._set_number_of_scans()
        self._set_buildup_time()
        self._set_y_data()
        self._normalize_y_values_to_number_of_scans()
        if len(self._dataset.props.subspec) == 2:
            self._gen_subspectrum()

    def _sort_xy_lists(self):
        t_pol_list = []
        for spectrum in self._dataset.spectra:
            t_pol_list.append(spectrum.tpol)
        sorted_lists = sorted(
            zip(t_pol_list, self._dataset.spectra)
        )  # sortiert nach den Werten in liste1
        _, self._dataset.spectra = zip(*sorted_lists)

    def _add_spectrum(self):
        """Add a new spectrum to the ds."""
        self._dataset.spectra.append(screamlab.dataset.Spectra())

    def _get_physical_range(self):
        """
        Retrieve the physical range of the spectrum.

        :return: The physical range of the spectrum.
        :rtype: dict
        """
        ranges = {}
        with open(
            rf"{self.file}/pdata/{self._dataset.props.procno}/procs",
            "r",
            encoding="utf-8",
        ) as procs_file:
            for procs_line in procs_file:
                if "##$ABSF1=" in procs_line:
                    ranges["start"] = float(procs_line.strip().split(" ")[-1])
                if "##$ABSF2=" in procs_line:
                    ranges["end"] = float(procs_line.strip().split(" ")[-1])
        return ranges

    def _get_num_of_datapoints(self):
        """
        Retrieve the number of data points in the spectrum.

        :return: Number of data points.
        :rtype: int
        """
        datapoints = None
        with open(
            rf"{self.file}/pdata/{self._dataset.props.procno}/procs",
            "r",
            encoding="utf-8",
        ) as procs_file:
            for procs_line in procs_file:
                if "##$FTSIZE=" in procs_line:
                    datapoints = int(procs_line.strip().split(" ")[-1])
        return datapoints

    def _calc_x_axis(self, physical_range, number_of_datapoints):
        """
        Calculate the x-axis values based on the physical range and number of data points.

        :param physical_range: The physical range of the spectrum.
        :type physical_range: dict
        :param number_of_datapoints: Number of data points in the spectrum.
        :type number_of_datapoints: int
        :return: Calculated x-axis values.
        :rtype: numpy.ndarray
        """
        return np.linspace(
            float(physical_range["start"]),
            float(physical_range["end"]),
            number_of_datapoints,
        )

    def _generate_path_to_experiment(self):
        """
        Generate file paths for all experiment numbers.

        :return: List of file paths to experiment data.
        :rtype: list
        """
        base_path = self._dataset.props.path_to_experiment
        path_list = [
            os.path.join(base_path, str(expno))
            for expno in self._dataset.props.expno
        ]
        return path_list


class ScreamImporter(TopspinImporter):
    """
    Class for importing and processing SCREAM DNP data.

    Automatically reads information about x- and y-axis (chemical shift and intensitys),
    polarization times (t_pol) and the number of scans used for the respective experiment.
    Automatically normalizes the  intensitys to the number of scans.

    """

    def _set_number_of_scans(self):
        """Set the number of scans for the last spectrum in the ds."""
        with open(rf"{self.file}/acqu", "r", encoding="utf-8") as acqu_file:
            for acqu_line in acqu_file:
                if "##$NS=" in acqu_line:
                    self._dataset.spectra[-1].number_of_scans = int(
                        acqu_line.strip().split(" ")[-1]
                    )

    def import_topspin_data(self):
        """Import NMR data from TopSpin and process it."""
        files = self._generate_path_to_experiment()
        for file in files:
            self.file = file
            self._add_spectrum()
            self._set_values()
        self._sort_xy_lists()

    def _set_buildup_time(self):
        """Set the buildup time for the last spectrum in the ds."""
        delay = self._extract_params_from_acqus("##$D= (0..63)", 64)
        loop = self._extract_params_from_acqus("##$L= (0..31)", 32)
        self._dataset.spectra[-1].tpol = loop * delay

    def _extract_params_from_acqus(self, param_list_name, param_count):
        flag = False
        param_line = ""
        param = None
        with open(rf"{self.file}/acqus", "r", encoding="utf-8") as acqus_file:
            for acqus_line in acqus_file:
                if "##" in acqus_line:
                    flag = False
                if flag:
                    param_line = param_line + " " + acqus_line.strip()
                    if (
                        len(
                            [
                                element
                                for element in param_line.split(" ")
                                if element != ""
                            ]
                        )
                        == param_count
                    ):
                        param_line = [
                            float(delay_time)
                            for delay_time in param_line.split(" ")
                            if delay_time != ""
                        ]
                        if param_list_name == "##$D= (0..63)":
                            param = param_line[
                                int(
                                    self._dataset.props.delay20.split(" ")[-1]
                                )
                            ]
                        elif param_list_name == "##$L= (0..31)":
                            param = param_line[
                                int(self._dataset.props.loop20.split(" ")[-1])
                            ]
                if param_list_name in acqus_line:
                    flag = True
        return param

    def _set_y_data(self):
        """Set the y-axis data for the last spectrum in the ds."""
        dic, y_data = ng.bruker.read_pdata(
            rf"{self.file}/pdata/" f"{self._dataset.props.procno}"
        )
        udic = ng.bruker.guess_udic(dic, y_data)
        uc = ng.fileiobase.uc_from_udic(udic)
        self._dataset.spectra[-1].x_axis = uc.ppm_scale()
        self._dataset.spectra[-1].y_axis = y_data

    def _normalize_y_values_to_number_of_scans(self):
        """Normalize the y-axis values to the number of scans."""
        self._dataset.spectra[-1].y_axis = np.divide(
            self._dataset.spectra[-1].y_axis,
            self._dataset.spectra[-1].number_of_scans,
        )

    def _gen_subspectrum(self):
        self._dataset.spectra[-1].x_axis, self._dataset.spectra[-1].y_axis = (
            screamlab.functions.generate_subspec(
                self._dataset.spectra[-1], self._dataset.props.subspec
            )
        )


class Pseudo2DImporter(TopspinImporter):
    """Not implemented yet."""


class Exporter:
    """
    A class to handle exporting and printing ds information.

    Attributes
    ----------
        dataset:  :obj:`screamlab.ds.Dataset` with all information aquired during fitting.

    """

    def __init__(self, ds):
        """
        Initializes the Exporter with a ds.

        :param ds: The ds to be processed.
        :type ds: object
        """
        self.dataset = ds

    def print(self):
        """
        Executes the complete visualization and export pipeline for the ds.

        This method performs the following actions:

        1. Plots TopSpin raw data after identifying sub-spectra (if the option is selected)
           and normalizing by the number of scans. Additionally, outputs them in CSV format.
        2. If prefit is enabled in the ds properties:
            - Plots prefit results.
            - Prints the lmfit prefit report.
        3. If the spectrum fit type includes "global" or "individual":
            - Plots the combined fit.
            - Plots each individual component of the global fit.
        4. For each buildup type defined in the ds properties:
            - Plots the corresponding buildup data.
        5. Prints a summary report of the fitting and analysis.
        6. Exports results:
            - Writes global/individual fit results to a semicolon-separated file.
            - Writes buildup fit results to a semicolon-separated file.
        """
        self._print_report()
        self._plot_topspin_data()
        self._plot_global_all_together()
        if self.dataset.props.prefit:
            self._plot_prefit()
            self._print_lmfit_prefit_report()
        if "global" in self.dataset.props.spectrum_fit_type:
            self._plot_global_each_individual()
        if "individual" in self.dataset.props.spectrum_fit_type:
            self._plot_global_each_individual()
        for buildup_type in self.dataset.props.buildup_types:
            self._plot_buildup(buildup_type)
        self._write_global_fit_results_to_semicolon_separated_file()
        self._write_buildup_fit_to_semicolon_separated_file()
        self._csv_output()

    def _plot_topspin_data(self):
        """
        Plots the spectral data from the ds

        Displays time delays (t_del) on the x-axis and intensity values on the y-axis.

        """
        colormap = plt.cm.Blues
        colors = [
            colormap(i / len(self.dataset.spectra))
            for i in range(len(self.dataset.spectra) + 2)
        ]
        for idx, spectrum in enumerate(self.dataset.spectra):
            plt.plot(
                spectrum.x_axis,
                spectrum.y_axis,
                label=f"$t_{{\\mathrm{{pol}}}}$ = {spectrum.tpol} s",
                color=colors[idx + 2],
            )
        plt.gca().invert_xaxis()
        plt.xlabel("$\\delta$ / ppm", fontsize=16)
        plt.ylabel("$I$ / a.u.", fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)
        output_dir = self._generate_output_dir("spectra")
        plt.savefig(
            f"{output_dir}/spectra.pdf",
            dpi=400,
            bbox_inches="tight",
        )
        plt.savefig(
            f"{output_dir}/spectra.png",
            dpi=400,
            bbox_inches="tight",
        )
        plt.close()

    def _plot_prefit(self):
        """
        Plots experimental data, simulation results, and residuals for the prefit analysis.

        The plot contains two subplots: the first shows the experimental data and simulation,
        while the second displays the residuals. The plot is saved as a high-resolution PDF.
        """
        spectrum = self.dataset.spectra[
            self.dataset.props.spectrum_for_prefit
        ]
        x_axis, y_axis = spectrum.x_axis, spectrum.y_axis
        valdict = screamlab.functions.generate_spectra_param_dict(
            self.dataset.lmfit_result_handler.prefit.params
        )
        simspec = [0] * len(y_axis)
        for values in valdict.values():
            for val in values:
                simspec = screamlab.functions.calc_peak(x_axis, simspec, val)
        _, axs = plt.subplots(
            2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1]}
        )
        axs[0].plot(x_axis, y_axis, color="black", label="Experiment")
        axs[0].plot(x_axis, simspec, "r--", label="Simulation")
        axs[0].legend(fontsize=14)
        axs[0].set_ylabel("$I$ / a.u.", fontsize=16)
        axs[0].tick_params(axis="both", labelsize=14)

        residual = y_axis - simspec
        axs[1].plot(x_axis, residual, color="grey", label="Residual")
        axs[1].set_xlabel("$\\delta$ / ppm", fontsize=16)
        axs[1].set_ylabel(r"$I_{\mathrm{resid}}$ / a.u.", fontsize=16)
        axs[0].set_xlim(max(x_axis), min(x_axis))
        axs[1].set_xlim(max(x_axis), min(x_axis))
        axs[1].legend(fontsize=14)
        axs[1].tick_params(axis="both", labelsize=14)
        plt.tight_layout()
        output_dir = self._generate_output_dir("spectral_deconvolution_plots")
        plt.savefig(
            f"{output_dir}/Prefit_plot.pdf",
            dpi=400,
            bbox_inches="tight",
        )
        output_dir = self._generate_output_dir("spectral_deconvolution_plots")
        plt.savefig(
            f"{output_dir}/Prefit_plot.png",
            dpi=400,
            bbox_inches="tight",
        )
        plt.close()

    def _print_lmfit_prefit_report(self):
        output_dir = self._generate_output_dir("lmfit_reports")
        lmfit_report = (
            f"{output_dir}/" f"spectral_decomposition_result_prefit.txt"
        )

        with open(lmfit_report, "w", encoding="utf-8") as a:
            a.write(
                lmfit.fit_report(
                    self.dataset.lmfit_result_handler.prefit, min_correl=0.25
                )
            )
        a.close()

    def _plot_buildup(self, buildup_type):
        """
        Plots the buildup data and corresponding model fits for a specified buildup type.

        The plot includes experimental data and simulations (exponential, biexponential, etc.)
        for each peak. The resulting plot is saved as a high-resolution PDF.

        :param buildup_type: The type of buildup function to fit
        (e.g., 'exponential', 'biexponential').
        :type buildup_type: str
        """
        output_dir = self._generate_output_dir("buildup_plots")
        colors = plt.get_cmap("viridis")
        norm = plt.Normalize(vmin=0, vmax=len(self.dataset.peak_list))

        func_map = screamlab.functions.return_func_map()

        for peak_nr, peak in enumerate(self.dataset.peak_list):
            peak_result = self.dataset.lmfit_result_handler.buildup_fit[
                buildup_type
            ][peak_nr]
            color = colors(norm(peak_nr))
            plt.plot(
                peak.buildup_vals.tpol,
                peak.buildup_vals.intensity,
                "o",
                color=color,
                label=f"{peak.peak_label}",
            )
            sim_tdel = np.linspace(0, peak.buildup_vals.tpol[-1], 1024)
            val_list = [param.value for param in peak_result.params.values()]
            plt.plot(
                sim_tdel,
                func_map[buildup_type](sim_tdel, val_list),
                "-",
                color=color,
            )
        plt.xlabel(r"$t_{\mathrm{pol}}$ / s", fontsize=16)
        plt.ylabel("$I$ / a.u.", fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)
        plt.savefig(
            f"{output_dir}/buildup_fit_{buildup_type}.pdf",
            dpi=400,
            bbox_inches="tight",
        )
        plt.savefig(
            f"{output_dir}/buildup_fit_{buildup_type}.png",
            dpi=400,
            bbox_inches="tight",
        )
        plt.close()

    def _plot_global_each_individual(self):
        output_dir = self._generate_output_dir("spectral_deconvolution_plots")
        param_dict = screamlab.functions.generate_spectra_param_dict(
            self.dataset.lmfit_result_handler.global_fit.params
        )

        for key, param_list in param_dict.items():
            spectrum = self.dataset.spectra[key]
            x_axis, y_axis = spectrum.x_axis, spectrum.y_axis

            simspec = [0] * len(y_axis)
            residual = copy.deepcopy(y_axis)

            fig, axs = plt.subplots(
                2,
                1,
                sharex=True,
                sharey=True,
                gridspec_kw={"height_ratios": [3, 1]},
            )

            for params in param_list:
                simspec = screamlab.functions.calc_peak(
                    x_axis, simspec, params
                )

            axs[0].plot(x_axis, y_axis, color="black", label="Experiment")
            axs[0].plot(x_axis, simspec, "r--", label="Simulation", alpha=0.8)

            residual -= simspec
            axs[1].plot(x_axis, residual, color="grey", label="Residual")

            axs[0].set_ylabel("$I$ / a.u.", fontsize=16)
            axs[1].set_xlabel("$\\delta$ / ppm", fontsize=16)
            axs[1].set_ylabel(r"$I_{\mathrm{resid}}$ / a.u.", fontsize=16)
            axs[0].tick_params(axis="both", labelsize=14)
            axs[1].tick_params(axis="both", labelsize=14)

            for ax in axs:
                ax.set_xlim(max(x_axis), min(x_axis))
                ax.legend(fontsize=14)

            plt.tight_layout()
            plot_filename = os.path.join(
                output_dir, f"{spectrum.tpol}_s_polarization_time.pdf"
            )
            plt.savefig(plot_filename, dpi=400, bbox_inches="tight")
            plot_filename = os.path.join(
                output_dir, f"{spectrum.tpol}_s_polarization_time.png"
            )
            plt.savefig(plot_filename, dpi=400, bbox_inches="tight")

            plt.close(fig)

    def _plot_global_all_together(self):
        output_dir = self._generate_output_dir("spectral_deconvolution_plots")

        param_dict = screamlab.functions.generate_spectra_param_dict(
            self.dataset.lmfit_result_handler.global_fit.params
        )

        num_spectra = len(param_dict)
        cols = 3
        rows = math.ceil(num_spectra / cols)

        fig, axs = plt.subplots(
            rows * 2,
            cols,
            sharex=True,
            sharey=False,
            figsize=(cols * 4, rows * 4),
            gridspec_kw={"height_ratios": [3, 1] * rows},
        )

        if rows == 1:
            axs = [axs]

        for i, (key, param_list) in enumerate(param_dict.items()):
            row, col = divmod(i, cols)
            ax_spectrum = axs[row * 2][col]
            ax_residual = axs[row * 2 + 1][col]

            spectrum = self.dataset.spectra[key]
            x_axis, y_axis = spectrum.x_axis, spectrum.y_axis
            simspec = [0] * len(y_axis)
            residual = copy.deepcopy(y_axis)

            for params in param_list:
                simspec = screamlab.functions.calc_peak(
                    x_axis, simspec, params
                )

            ax_spectrum.plot(
                x_axis, y_axis, color="black", label="Experiment"
            )
            ax_spectrum.plot(
                x_axis, simspec, "r--", label="Simulation", alpha=0.8
            )
            residual -= simspec
            ax_residual.plot(x_axis, residual, color="grey", label="Residual")

            ax_spectrum.set_ylabel("$I$ / a.u.", fontsize=14)
            ax_residual.set_xlabel("$\\delta$ / ppm", fontsize=14)
            ax_residual.set_ylabel(
                r"$I_{\mathrm{resid}}$ / a.u.", fontsize=14
            )
            ax_residual.tick_params(axis="both", labelsize=14)
            ax_spectrum.set_xlim(max(x_axis), min(x_axis))
            ax_spectrum.legend(loc="upper right", fontsize=10)
            ax_spectrum.tick_params(axis="both", labelsize=14)
            ax_residual.legend(loc="upper right", fontsize=10)
            ax_residual.set_ylim(
                -1 * max(abs(y_axis)) / 2, max(abs(y_axis)) / 2
            )

            ax_spectrum.text(
                0.05,
                0.85,
                rf"$t_{{pol}}$ = {spectrum.tpol:.2f} s",
                transform=ax_spectrum.transAxes,
                fontsize=10,
                bbox={"facecolor": "white", "alpha": 0.5},
            )

        plot_filename_pdf = os.path.join(output_dir, "All_Spectra.pdf")
        plot_filename_png = os.path.join(output_dir, "All_Spectra.png")

        plt.tight_layout()
        plt.savefig(plot_filename_png, dpi=400, bbox_inches="tight")
        plt.savefig(plot_filename_pdf, dpi=400, bbox_inches="tight")
        plt.close(fig)

    def _print_report(self):
        with open(
            f"{self.dataset.props.output_folder}/analysis_result.txt",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(str(self.dataset.props) + "\n")
            f.write(str(self.dataset) + "\n")

            f.write("[[Peaks]]\n")
            for peak_nr, peak in enumerate(self.dataset.peak_list):
                f.write(f"[Peak {peak_nr + 1}]\n")
                f.write(str(peak))
            f.write("[[Prefit]]\n")
            if self.dataset.props.prefit:
                self._get_prefit_string(f)
            else:
                f.write("No prefit performed.\n")

            f.write("[[Global fit results]]\n")
            self._print_global_fit_results(f)
            f.write("[[Buildup fit results]]\n")
            self._print_buildup(f)

    def _print_buildup(self, f):
        for buildup_type in self.dataset.props.buildup_types:
            f.write(f"[{buildup_type}]\n")
            header = screamlab.functions.buildup_header()
            column_widths = [20, 15, 10, 15, 10, 15, 15, 15, 35, 35, 10]
            f.write(
                "".join(h.ljust(w) for h, w in zip(header, column_widths))
                + "\n"
            )
            format_mappings = screamlab.functions.format_mapping()
            type_format = format_mappings.get(buildup_type, [])
            for result_nr, result in enumerate(
                self.dataset.lmfit_result_handler.buildup_fit[buildup_type]
            ):
                row_data = [self.dataset.peak_list[result_nr].peak_label]

                for param in type_format:
                    value = self._set_value(param, result, row_data)
                    value, row_data = self._sort_value_list(
                        param, value, row_data, result
                    )
                    row_data.append(value)

                f.write(
                    "".join(
                        h.ljust(w) for h, w in zip(row_data, column_widths)
                    )
                    + "\n"
                )

    def _print_global_fit_results(self, f):
        valdict = screamlab.functions.generate_spectra_param_dict(
            self.dataset.lmfit_result_handler.global_fit.params
        )
        header = screamlab.functions.spectrum_fit_header()
        column_widths = [25, 12, 15, 20, 15, 15, 22, 20, 20, 10]
        f.write(
            "".join(f"{h:<{w}}" for h, w in zip(header, column_widths)) + "\n"
        )

        for delay_time in range(0, len(valdict[0])):
            for val_nr, (_, values) in enumerate(valdict.items()):
                row = self._generate_fit_param_row(values, delay_time, val_nr)
                f.write(
                    "".join(f"{h:<{w}}" for h, w in zip(row, column_widths))
                    + "\n"
                )

    def _get_prefit_string(self, f):
        valdict = screamlab.functions.generate_spectra_param_dict(
            self.dataset.lmfit_result_handler.prefit.params
        )
        widths = [25, 18, 20, 15, 15]
        header = [
            "Label",
            "Center / ppm,",
            "Amplitude / a.u.",
            "Sigma / ppm",
            "Gamma / ppm",
        ]
        f.write("".join(h.ljust(w) for h, w in zip(header, widths)) + "\n")

        for _, keys in enumerate(valdict):
            for val_nr, val in enumerate(valdict[keys]):
                pars = []
                if len(val) == 5:
                    pars.append(self.dataset.peak_list[val_nr].peak_label)
                    pars.extend(
                        [
                            round(val[1], 3),
                            round(val[0], 3),
                            round(val[2], 3),
                            round(val[3], 3),
                        ]
                    )
                    f.write(
                        "".join(str(h).ljust(w) for h, w in zip(pars, widths))
                        + "\n"
                    )
                elif len(val) == 3:
                    pars.append(self.dataset.peak_list[val_nr].peak_label)
                    pars.extend(
                        [
                            round(val[1], 3),
                            round(val[0], 3),
                            round(val[2], 3),
                            "---",
                        ]
                    )
                    f.write(
                        "".join(str(h).ljust(w) for h, w in zip(pars, widths))
                        + "\n"
                    )
                elif len(val) == 4:
                    pars.append(self.dataset.peak_list[val_nr].peak_label)
                    pars.extend(
                        [
                            round(val[1], 3),
                            round(val[0], 3),
                            "---",
                            round(val[2], 3),
                        ]
                    )
                    f.write(
                        "".join(str(h).ljust(w) for h, w in zip(pars, widths))
                        + "\n"
                    )

    def _write_buildup_fit_to_semicolon_separated_file(self):
        """
        Writes the buildup fit results to semicolon-separated text files for each buildup type.

        This method iterates over the different buildup types, retrieves the corresponding
        buildup fit results, formats them using a predefined header and value mapping, and
        writes the results into individual text files.

        Each file is named as 'buildup_fit_result_<buildup_type>.txt' and
        includes
        a header row followed by the formatted data rows for each result.
        """
        for buildup_type in self.dataset.props.buildup_types:
            output_folder = self._generate_output_dir("tabular_results")
            output_file_path = (
                f"{output_folder}/buildup_fit_result_{buildup_type}.txt"
            )
            with open(output_file_path, "w", encoding="utf-8") as f:
                header = screamlab.functions.buildup_header()
                f.write(";".join(header) + "\n")
                format_mappings = screamlab.functions.format_mapping()
                type_format = format_mappings.get(buildup_type, [])
                for result_nr, result in enumerate(
                    self.dataset.lmfit_result_handler.buildup_fit[
                        buildup_type
                    ]
                ):
                    self._save_lmfit_report_buildup(
                        buildup_type, result, result_nr
                    )
                    peak_label = self.dataset.peak_list[result_nr].peak_label
                    row_data = [peak_label]
                    for param in type_format:
                        value = self._set_value(param, result, row_data)
                        value, row_data = self._sort_value_list(
                            param, value, row_data, result
                        )
                        row_data.append(value)
                    f.write(";".join(row_data) + "\n")

    def _save_lmfit_report_buildup(self, buildup_type, result, result_nr):
        output_dir = self._generate_output_dir("lmfit_reports")
        lmfit_report = (
            f"{output_dir}/"
            f"buildup_fit_result_{buildup_type}_{self.dataset.peak_list[result_nr].peak_label}.txt"
        )
        with open(lmfit_report, "w", encoding="utf-8") as a:
            a.write(lmfit.fit_report(result, min_correl=0.25))
        a.close()

    def _generate_output_dir(self, new_dir):
        output_dir = os.path.join(self.dataset.props.output_folder, new_dir)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _write_global_fit_results_to_semicolon_separated_file(self):
        """
        Writes the global fit results to a semicolon-separated text file.

        This method retrieves the global fit parameters, generates a dictionary of spectra
        parameters, formats the data into rows, and writes the results to a file named
        'Global_fit_result.txt'. The file includes a header row followed by the formatted
        data rows for each delay time and parameter value.

        The output file is stored in the specified output folder.
        """
        output_folder = self._generate_output_dir("tabular_results")
        output_file_path = (
            f"{output_folder}/spectral_decomposition_result.txt"
        )

        with open(output_file_path, "w", encoding="utf-8") as f:
            valdict = screamlab.functions.generate_spectra_param_dict(
                self.dataset.lmfit_result_handler.global_fit.params
            )
            header = screamlab.functions.spectrum_fit_header()
            f.write(";".join(str(item) for item in header) + "\n")
            for delay_time in range(0, len(valdict[0])):
                for val_nr, (_, values) in enumerate(valdict.items()):
                    row = self._generate_fit_param_row(
                        values, delay_time, val_nr
                    )
                    f.write(";".join(str(item) for item in row) + "\n")

    def _csv_output(self):
        """
        Writes spectral data to a CSV file with semicolon-separated values.

        This method extracts the x-axis and y-axis data from each spectrum in the ds,
        and writes the data to a CSV file named 'spectra.csv' in the specified
        output folder. The file is structured such that each row contains the corresponding
        values for the x-axis and y-axis.
        """
        spectral_data = []
        output_dir = self._generate_output_dir("spectra")
        with open(
            f"{output_dir}\\spectra.csv", "w", newline="", encoding="utf-8"
        ) as file:
            for spectrum in self.dataset.spectra:
                spectral_data.append(spectrum.x_axis)
                spectral_data.append(spectrum.y_axis)
            writer = csv.writer(file, delimiter=";")
            for row in zip(*spectral_data):
                writer.writerow(row)

    def _set_value(self, param, result, row_data):
        param_calc = {
            "Rf": lambda: str(round(1 / float(row_data[2]), 5)),
            "Rs": lambda: str(round(1 / float(row_data[4]), 5)),
            "Sf": lambda: str(
                round(
                    float(row_data[1]) / math.sqrt(float(row_data[2])),
                    3,
                )
            ),
            "Ss": lambda: str(
                round(
                    float(row_data[3]) / math.sqrt(float(row_data[4])),
                    3,
                )
            ),
        }
        if param == "---":
            value = "---"
        elif param in param_calc:
            value = param_calc[param]()
        else:
            value = str(round(result.params[param].value, 3))
        return value

    def _sort_value_list(self, param, value, row_data, result):
        if param != "ts":
            return value, row_data
        param_value = float(result.params[param].value)
        if param_value < float(row_data[2]):
            row_data[1], row_data[3] = row_data[3], row_data[1]
            value, row_data[2] = row_data[2], str(value)
        return value, row_data

    def _generate_fit_param_row(self, values, delay_time, val_nr):
        """
        Generates a row of fit parameters for a given delay time and spectrum index.

        This function extracts and formats the fitting parameters, including peak label,
        delay time, center, amplitude, sigma, gamma, and full-width at half maximum (FWHM)
        or Lorentzian, Gaussian, and Voigt line shapes. It also includes the corresponding
         intensity value.

        :param values: Dictionary containing fitting parameters for each delay time.
        :type values: dict
        :param delay_time: The index of the delay time corresponding to the fit parameters.
        :type delay_time: int
        :param val_nr: The index of the spectrum being processed.
        :type val_nr: int
        :return: A list with the formatted fit parameter row, or None if the format is invalid.
        :rtype: list or None
        """
        row = None
        if len(values[delay_time]) == 5:
            row = self._gen_voigt_output(values, delay_time, val_nr)
        if len(values[delay_time]) == 3:
            row = self._gen_gauss_output(values, delay_time, val_nr)
        if len(values[delay_time]) == 4:
            row = self._gen_lorentz_output(values, delay_time, val_nr)
        return row

    def _gen_voigt_output(self, values, delay_time, val_nr):
        return [
            (
                self.dataset.peak_list[delay_time].peak_label
                if val_nr == 0
                else ""
            ),
            self.dataset.spectra[val_nr].tpol,
            round(values[delay_time][1], 3),
            round(values[delay_time][0], 3),
            round(values[delay_time][2], 3),
            round(values[delay_time][3], 3),
            round(
                screamlab.functions.fwhm_lorentzian(values[delay_time][3]),
                3,
            ),
            round(
                screamlab.functions.fwhm_gaussian(values[delay_time][2]),
                3,
            ),
            round(
                screamlab.functions.fwhm_voigt(
                    values[delay_time][2], values[delay_time][3]
                ),
                3,
            ),
            round(
                self.dataset.peak_list[delay_time].buildup_vals.intensity[
                    val_nr
                ],
                3,
            ),
        ]

    def _gen_gauss_output(self, values, delay_time, val_nr):
        return [
            (
                self.dataset.peak_list[delay_time].peak_label
                if val_nr == 0
                else ""
            ),
            self.dataset.spectra[val_nr].tpol,
            round(values[delay_time][1], 3),
            round(values[delay_time][0], 3),
            round(values[delay_time][2], 3),
            "---",
            "---",
            round(
                screamlab.functions.fwhm_gaussian(values[delay_time][2]),
                3,
            ),
            "---",
            round(
                self.dataset.peak_list[delay_time].buildup_vals.intensity[
                    val_nr
                ],
                3,
            ),
        ]

    def _gen_lorentz_output(self, values, delay_time, val_nr):
        return [
            (
                self.dataset.peak_list[delay_time].peak_label
                if val_nr == 0
                else ""
            ),
            self.dataset.spectra[val_nr].tpol,
            round(values[delay_time][1], 3),
            round(values[delay_time][0], 3),
            "---",
            round(values[delay_time][2], 3),
            round(
                screamlab.functions.fwhm_lorentzian(values[delay_time][2]),
                3,
            ),
            "---",
            "---",
            round(
                self.dataset.peak_list[delay_time].buildup_vals.intensity[
                    val_nr
                ],
                3,
            ),
        ]


class LmfitResultHandler:
    """
    A class to store the results of fitting operations.

    This class stores and manages the results from different types of fits:
    prefit, individual fit, global fit, and buildup fit. It provides a container
    for the various fit results to facilitate later analysis and processing.

    Attributes
    ----------
        prefit (object | None): Stores the prefit result, which may be an object or None.
        individual_fit (object | None): Result of an individual fit, or None if unavailable.
        global_fit (object | None): Result of a global fit, or None if unavailable.
        buildup_fit (dict): Stores buildup fit results, keyed by fit ID.

    """

    def __init__(self):
        """
        Initializes the LmfitResultHandler with default values.

        The prefit, single_fit, and global_fit attributes are set to None,
        indicating that no fit results have been stored yet. The buildup_fit
        attribute is initialized as an empty dictionary to store multiple buildup fit results.

        Attributes
        ----------
            prefit (None): Default value for the prefit result.
            individual_fit (None): Default value for the single fit result.
            global_fit (None): Default value for the global fit result.
            buildup_fit (dict): Default empty dictionary for storing buildup fit results.

        """
        self.prefit = None
        self.single_fit = None
        self.global_fit = None
        self.buildup_fit = {}
