import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind

from . import read_excel_imfcs_saved as imfcsread


class Psf:

    PANEL_PARAM: list[str] = [
        "Frame time",
        "Bleach Correction",
        "Polynomial Order",
        "Image width",
        "Image height",
        "Overlap",
    ]
    RSD_t: float  # Exclude points where std dev / mean ratio goes beyond 100%.

    input_path: str
    filename: str

    slopes: list
    intercepts: list
    correct_psf_param: float
    min_slope_index: int
    arr: np.array

    def __init__(self, input_path: str, filename: str, RSD_t: float = 1.0):
        self.input_path = input_path
        self.filename = filename
        self.RSD_t = RSD_t

    def get_file_path(self):
        return os.path.join(self.input_path, self.filename)

    def plot_psf_calib_all(
        self, param: dict, arr: np.array, subptitle: str, RSD_tres: float
    ):

        a_size, b_size, c_size = arr.shape

        # Create the plot.
        fig, axs = plt.subplots(1, 3, figsize=(18, 5))

        ## Plot 1 - D values at different combiantion of binning and PSF.
        for a in range(a_size):
            x_values = np.arange(param["bin start"], param["bin end"] + 1)
            # Mask invalid points based on RSD_tres.
            y_values = arr[a, :, 0]
            y_ratios = arr[a, :, 1] / y_values
            y_mask = y_ratios > RSD_tres
            y_errors = arr[a, :, 1]
            y_values[y_mask] = np.nan
            y_errors[y_mask] = np.nan

            psf_label = param["psf start"] + (a * param["psf step"])
            axs[0].errorbar(
                x_values,
                y_values,
                yerr=y_errors,
                label=f"{psf_label:.1f}",
                fmt="-",
                capsize=3,
            )

            axs[0].set_title("PSF calibration")
            axs[0].set_xlabel("Pixel binning")
            axs[0].set_ylabel(r"Diffusion coefficient [$\mu m^2 /s$]")
            axs[0].legend(title="PSF", bbox_to_anchor=(1.05, 1), loc="upper left")
            axs[0].grid(True)

        x_limits = axs[0].get_xlim()
        y_limits = axs[0].get_ylim()

        ## Plot 2 - Linear Fits with Highlighted Min Slope.

        # Initialize lists to store slopes and intercepts.
        self.slopes = []
        self.intercepts = []

        for a in range(a_size):
            x_values = np.arange(param["bin start"], param["bin end"] + 1)
            # Mask invalid points based on RSD_tres.
            y_values = arr[a, :, 0]
            y_ratios = arr[a, :, 1] / y_values
            y_mask = y_ratios > RSD_tres
            y_errors = arr[a, :, 1]
            y_values[y_mask] = np.nan
            y_errors[y_mask] = np.nan

            # Remove NaN values for fitting.
            valid_mask = ~np.isnan(y_values)
            x_valid = x_values[valid_mask]
            y_valid = y_values[valid_mask]

            # Fit a straight line if valid data exists.
            if len(x_valid) > 1:
                slope, intercept = np.polyfit(x_valid, y_valid, deg=1)
                self.slopes.append(slope)
                self.intercepts.append(intercept)
            else:
                # Store NaN if not enough points for a fit.
                self.slopes.append(np.nan)
                self.intercepts.append(np.nan)

        # Find the index of the line with the smallest slope closer to zero.
        valid_slopes = np.array(self.slopes)
        valid_slopes[np.isnan(valid_slopes)] = (
            np.inf
        )  # Replace NaN with infinity to exclude them.
        self.min_slope_index = np.argmin(np.abs(valid_slopes))
        print(f"min slope index: {self.min_slope_index}")
        print(f"slope: {self.slopes[self.min_slope_index]}")

        # Find the correct PSF parameter.
        self.correct_psf_param = param["psf start"] + (
            self.min_slope_index * param["psf step"]
        )
        print(f"correct psf param: {self.correct_psf_param:.1f}")

        # Plot the lines.
        for a in range(a_size):
            # Only plot lines for valid fits.
            if a == self.min_slope_index:
                # Highlight the line with the smallest slope in red.
                y_fit = self.slopes[a] * x_values + self.intercepts[a]
                axs[1].plot(
                    x_values,
                    y_fit,
                    "r-",
                    linewidth=2,
                    label=f"PSF params. ({self.correct_psf_param:.1f})",
                )
            elif not np.isnan(self.slopes[a]):
                # Plot other lines in black.
                y_fit = self.slopes[a] * x_values + self.intercepts[a]
                axs[1].plot(x_values, y_fit, "k-", linewidth=1)

        # Show the plot.
        axs[1].set_title("Linear Fits with Highlighted Min Slope")
        axs[1].set_xlabel("Pixel binning")
        axs[1].set_ylabel(r"Diffusion coefficient [$\mu m^2 /s$]")
        axs[1].legend(title="", bbox_to_anchor=(1.05, 1), loc="upper left")
        axs[1].grid(True)
        axs[1].set_xlim(x_limits)
        axs[1].set_ylim(y_limits)

        ## Plot 3 - Plot the average D of the best fit line (min slope)

        # Arbitrary point to overlay
        best_fit_d = self.intercepts[self.min_slope_index]
        print(f"best fit D: {best_fit_d:.1f}")

        # D values of correct PSF parameter
        correct_mean_values = arr[self.min_slope_index, :, 0]

        # Filter out NaN values
        valid_mask = ~np.isnan(correct_mean_values)
        valid_mean_values = correct_mean_values[valid_mask]

        # Compute the mean
        mean_value = np.nanmean(valid_mean_values)
        print(f"Davr: {mean_value:.1f}")

        # Plotting the boxplot
        axs[2].boxplot(valid_mean_values)

        # Overlay individual points
        x_positions = np.random.normal(
            1, 0.04, size=len(valid_mean_values)
        )  # Add jitter for better visibility
        axs[2].scatter(
            x_positions, valid_mean_values, color="black", alpha=0.6, label="Individual"
        )

        # Overlay arbitrary point
        axs[2].scatter(
            1,
            best_fit_d,
            color="red",
            s=50,
            marker="x",
            label=f"Best fit slope ({best_fit_d:.2f})",
        )
        axs[2].scatter(
            1,
            mean_value,
            color="blue",
            s=50,
            marker="x",
            label=f"Mean ({mean_value:.2f})",
        )

        # Adding labels and title
        axs[2].set_title("Boxplot correct PSF")
        axs[2].set_ylabel(r"Diffusion coefficient [$\mu m^2 /s$]")
        axs[2].set_xticks([])
        axs[2].legend(title="", bbox_to_anchor=(1.05, 1), loc="upper left")

        fig.suptitle(subptitle, fontsize=16, fontweight="bold")
        plt.tight_layout()
        basename = os.path.splitext(subptitle)[0]
        # plt.savefig("/Users/danielaik/Downloads/test/" + basename + ".svg", format="svg", dpi=300, bbox_inches="tight")
        plt.show()

    def get_box_plot_values(self):

        correct_mean_values = self.arr[self.min_slope_index, :, 0]
        # Filter out NaN values
        valid_mask = ~np.isnan(correct_mean_values)
        valid_mean_values = correct_mean_values[valid_mask]
        return valid_mean_values

    def get_basename(self):
        return self.filename

    def get_best_fit_d(self):
        return self.intercepts[self.min_slope_index]

    def get_psf_param(self):
        return round(self.correct_psf_param, 1)

    def get_d_avr_bin(self):
        correct_mean_values = self.arr[self.min_slope_index, :, 0]

        valid_mask = ~np.isnan(correct_mean_values)
        valid_mean_values = correct_mean_values[valid_mask]

        return np.nanmean(valid_mean_values)

    def main(self):
        file_path = self.get_file_path()
        df = imfcsread.read_excel_imfcs_saved(path_excel=file_path)

        param_dict = imfcsread.get_param(excel_data=df, panel_param=self.PANEL_PARAM)

        p, self.arr = imfcsread.get_psf(excel_data=df)

        self.plot_psf_calib_all(
            param=p, arr=self.arr, subptitle=self.filename, RSD_tres=self.RSD_t
        )

    def __str__(self):
        return f"PSF instance ({self.filename})"


if __name__ == "__main__":
    print(f"Script File Name: {__file__}")
