import math

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.patches import Rectangle


def plot_selected_image_full_frame(
    output: widgets.Output,
    array: np.array,
    index: int = 0,
    cmap="gray",
    xy_coordinate=None,
):

    with output:

        if array.ndim != 3:
            raise ValueError("Input array must have 3 dimensions (t, h, w).")

        output.clear_output(wait=True)

        # Get the widget's dimensions in pixels.
        widget_width = int(output.layout.width.replace("px", ""))
        widget_height = int(output.layout.height.replace("px", ""))

        # Convert widget dimensions to inches for the figure.
        dpi = 100  # Default DPI
        fig_width_in = widget_width / dpi
        fig_height_in = widget_height / dpi

        # Create a figure with adjusted size.
        fig = plt.figure(figsize=(fig_width_in, fig_height_in))

        # fig = plt.figure(figsize=(3, 3))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])

        ax.imshow(array[index, :, :], cmap=cmap)
        ax.set_title(f"Intensity projection")
        ax.axis("off")

        if xy_coordinate is not None:
            rect = Rectangle(
                (xy_coordinate[0], xy_coordinate[1]),
                xy_coordinate[2],
                xy_coordinate[3],
                linewidth=1,
                edgecolor="red",
                facecolor="none",
            )
            ax.add_patch(rect)

        plt.close(fig)  # Supress interactive notebook line output.
        display(fig)


"""
## Plotter for Display Analysis Window
# calculate_nrmsd(..)
# calculate_snr(..)
# plot_acfs(..)
# plot_intensity_projection(..)
# plot_histograms_with_heatmaps(..)
# plot_two_histograms(..)
# plot_combined_analysis_imfcs(..)
"""


def calculate_nrmsd(observed: np.array, predicted: np.array, N_fit: np.array):
    """
    Compute the normalized root-mean-square deviation (NRMSD) between
    observed and predicted correlation curves.

    Parameters
    ----------
    observed : numpy.ndarray
        3D array of observed values with shape ``(n, m, t)``, where:
        - ``n`` is the number of rows,
        - ``m`` is the number of columns,
        - ``t`` is the number of lag times.
    predicted : numpy.ndarray
        3D array of predicted values with the same shape as ``observed``.
    N_fit : numpy.ndarray
        2D array of normalization factors with shape ``(n, m)``.
        Each value corresponds to the estimated particle number ``N`` at each pixel.

    Returns
    -------
    numpy.ndarray
        2D array of NRMSD values with shape ``(n, m)``, where each element
        represents the NRMSD for the corresponding pixel.

    Notes
    -----
    - Lag time index 0 is excluded from the NRMSD calculation.
    - NRMSD is computed as:

      ``NRMSD(n, m) = sqrt(sum((observed - predicted)^2)) * N_fit``

    Raises
    ------
    ValueError
        If ``observed`` and ``predicted`` do not have matching shapes.
    """

    if observed.shape != predicted.shape:
        raise ValueError("Observed and predicted arrays must have the same shape.")

    # Calculate residuals, square them, and take the mean along the last axis (t).
    # Exclude time lag = 0.
    residuals_squared_mean = np.sum(
        (observed[:, :, 1:] - predicted[:, :, 1:]) ** 2, axis=2
    )

    # Compute the square root of the mean residuals to get RMSD.
    rmsd_matrix = np.sqrt(residuals_squared_mean)

    # Normalisation.
    rmsd_matrix *= N_fit

    return rmsd_matrix


def calculate_snr(cf: np.array, last_lag: int = 6):
    """
    Compute the signal-to-noise ratio (SNR) of an autocorrelation function (ACF)
    for each pixel using vectorized operations.

    Parameters
    ----------
    cf : numpy.ndarray
        3D array of autocorrelation values with shape ``(n, m, t)``, where:
        - ``n`` : number of rows (pixels along axis 0)
        - ``m`` : number of columns (pixels along axis 1)
        - ``t`` : number of lag times
    last_lag : int, optional
        Number of initial lag times (starting from lag index 1) used for
        computing the SNR. Default is ``6``, meaning lag times ``1`` to ``5``
        are included.

    Returns
    -------
    numpy.ndarray
        2D array of shape ``(n, m)`` containing the SNR for each pixel.

    Notes
    -----
    - Lag time index ``0`` is excluded because it contains the autocorrelation
      amplitude and does not represent noise behavior.
    - SNR is defined as:

      ``SNR = mean(cf[lag 1 : lag N]) / std(cf[lag 1 : lag N])``

    - Division by zero will produce ``inf`` or ``nan`` in accordance with
      NumPy's broadcasting rules.

    Raises
    ------
    ValueError
        If ``last_lag`` is less than or equal to 1.
    """

    mean = np.mean(cf[:, :, 1:last_lag], axis=2)
    std = np.std(cf[:, :, 1:last_lag], axis=2)

    snr = np.divide(mean, std)

    return snr


def plot_acfs(
    arr_acf: np.array,
    arr_lag: np.array,
    arr_sd: np.array = None,
    arr_fit: np.array = None,
    with_fits: bool = False,
    axs=None,
):

    col_profile = ["#1E88E5", "#D81B60"]

    if len(arr_lag) < 2:
        raise ValueError(
            "t_array must have at least two elements to define the x-axis value."
        )

    n_dim, m_dim, t_dim = arr_acf.shape

    assert t_dim == len(arr_lag), "non matching lagtime elem"

    if axs is None:
        fig, axs = plt.subplots(figsize=(5, 5))

    for n in range(n_dim):
        for m in range(m_dim):
            axs.plot(arr_lag[1:], arr_acf[n, m, 1:], color=col_profile[0])

    if with_fits and arr_fit is not None:
        for n in range(n_dim):
            for m in range(m_dim):
                axs.plot(
                    arr_lag[1:], arr_fit[n, m, 1:], color=col_profile[1], alpha=0.3
                )

    # Add titles, labels, and grid.
    axs.set_title("Autocorrelation Function")
    axs.set_xlabel(r"Time lag $[s]$")
    axs.set_ylabel(r"G$(0)$")
    axs.grid(False)
    axs.set_xscale("log")

    # Aspect ratio.
    xmin, xmax = axs.get_xlim()
    ymin, ymax = axs.get_ylim()
    x_range = math.log(xmax - xmin)
    y_range = ymax - ymin
    max_range = max(x_range, y_range)
    min_range = min(x_range, y_range)
    axs.set_aspect(max_range / min_range)


def plot_intensity_projection(
    array: np.array,
    index: int,
    cmap="gray",
    xy_coordinate: list = None,
    gs: GridSpec = None,
    fig: plt.figure = None,
):

    # Validate input array.
    if array.ndim != 3:
        raise ValueError("Input array must have 3 dimensions (t, h, w).")

    assert xy_coordinate is not None, "invalid cropped xy coordinates"

    rows = 1
    cols = 2

    if (gs is None) or (fig is None):
        fig = plt.figure(figsize=(cols * 6, rows * 6))
        gs = GridSpec(rows, cols, figure=fig)  # GridSpec for flexible layout
    else:
        # Create a 1-row, 2-column GridSpecFromSubplotSpec
        sub_gs = GridSpecFromSubplotSpec(
            rows, cols, subplot_spec=gs, wspace=0.2, hspace=0.5
        )
        gs = sub_gs

    ax1 = fig.add_subplot(gs[0 // cols, 0 % cols])  # Grid layout
    ax2 = fig.add_subplot(gs[1 // cols, 1 % cols])  # Grid layout

    # Plot full frame pic with rectangular selection.
    ax1.imshow(array[index, :, :], cmap=cmap)
    ax1.set_title(f"Intensity projection")
    ax1.axis("off")  # Hide axes for a cleaner display.
    # Add a red rectangle.
    rect = Rectangle(
        (xy_coordinate[0], xy_coordinate[1]),
        xy_coordinate[2],
        xy_coordinate[3],
        linewidth=2,
        edgecolor="red",
        facecolor="none",
    )
    ax1.add_patch(rect)

    # Plot the zoomed-in picture.
    ax2.imshow(
        array[
            index,
            xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
            xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
        ],
        cmap=cmap,
    )
    ax2.set_title(f"Zoomed")
    ax2.axis("off")  # Hide axes for a cleaner display.


def plot_histograms_with_heatmaps(
    data, indices, labels=None, cmap="hot", gs: GridSpec = None, fig: plt.figure = None
):

    if len(data.shape) != 3:
        raise ValueError("Input data must be a 3D array (M, N, K).")

    # Check if indices are valid.
    for index in indices:
        if index < 0 or index >= data.shape[2]:
            raise IndexError(f"Index must be in the range [0, {data.shape[2] - 1}].")

    # Validate labels length.
    if labels and len(labels) != len(indices):
        raise ValueError("The length of labels must match the number of indices.")

    # Create subplots.
    n = len(indices)
    cols = min(3, n)  # Up to 3 columns per row.
    rows = (n + cols - 1) // cols  # Calculate the required number of rows.

    if (gs is None) or (fig is None):
        fig = plt.figure(figsize=(cols * 6, rows * 6))
        gs = GridSpec(rows, cols, figure=fig)  # GridSpec for flexible layout.
    else:
        # Create a 1-row, 3-column GridSpecFromSubplotSpec.
        sub_gs = GridSpecFromSubplotSpec(
            rows, cols, subplot_spec=gs, wspace=0.2, hspace=0.5
        )
        gs = sub_gs

    for i, index in enumerate(indices):
        # Extract the 2D slice.
        heatmap_data = data[:, :, index]
        flat_data = heatmap_data.flatten()  # Flatten the 2D array for the histogram.

        # Subplot for combined visualization.
        ax_hist = fig.add_subplot(gs[i // cols, i % cols])  # Grid layout.
        ax_hist.hist(flat_data, bins=20, color="gray", alpha=0.7, edgecolor="black")

        # Determine the title for each subplot.
        title = labels[i] if labels else f"Index {index}"
        ax_hist.set_title(f"Histogram & Heatmap\n{title}")
        ax_hist.set_xlabel(labels[i])
        if i == 0:
            ax_hist.set_ylabel("Frequency")

        # Inset for the heatmap.
        ax_heatmap = ax_hist.inset_axes(
            [0.56, 0.55, 0.4, 0.4]
        )  # [x, y, width, height] in figure fraction
        heatmap = ax_heatmap.imshow(heatmap_data, cmap=cmap)
        ax_heatmap.axis("off")  # Hide axes for the heatmap.

        # Display mean and standard deviation as text.
        text_x = 0.9  # Adjust x-position of the text.
        text_y = 0.5  # Adjust y-position of the text.
        ax_hist.text(
            text_x,
            text_y,
            f"Mean: {np.mean(heatmap_data):.2f}\nStd Dev: {np.std(heatmap_data):.2f}",
            transform=ax_hist.transAxes,
            fontsize=10,
            ha="right",
            va="top",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="gray"),
        )

    if (gs is None) or (fig is None):
        plt.tight_layout()
        plt.show()


def plot_two_histograms(
    data1,
    data2,
    bins=30,
    titles=("Histogram 1", "Histogram 2"),
    xlabels=("Value 1", "Value 2"),
    ylabels=("Frequency", "Frequency"),
    colors=("blue", "green"),
    alphas=(0.7, 0.7),
    density=False,
    figsize=(12, 6),
    axs1=None,
    axs2=None,
):

    if (axs1 is None) or (axs2 is None):
        fig, (axs1, axs2) = plt.subplots(1, 2, figsize=figsize)

    for i, (ax, data, title, xlabel, ylabel, color, alpha) in enumerate(
        zip([axs1, axs2], [data1, data2], titles, xlabels, ylabels, colors, alphas)
    ):
        if data.ndim > 1:
            data = data.flatten()

        ax.hist(
            data,
            bins=bins,
            density=density,
            alpha=alpha,
            color=color,
            edgecolor="black",
        )
        y_min, y_max = ax.get_ylim()

        ax.vlines(np.mean(data), y_min, y_max, "red", linestyles="--")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        if i == 0:
            ax.set_ylabel(ylabel if not density else "Probability")

        # Add a text box with mean ± std dev.
        textstr = f"Mean ± Std Dev: {np.mean(data):.2f} ± {np.std(data):.2f}"
        ax.text(
            0.95,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.5),
        )

    if (axs1 is None) or (axs2 is None):
        plt.tight_layout()
        plt.show()  # Show the figure only if new axes were created.


def plot_combined_analysis_imfcs(
    fig: plt.figure,
    gs: GridSpec,
    acf: np.array,
    lag: np.array,
    fit: np.array,
    avr_intensity: np.array,
    xy_coordinate: list[int],
    fit_res: np.array,
    index: int = 0,
    is_plot_with_fit: bool = True,
    indices_histogram_pmap: list[int] = [1, 2, 12],
    labels_histogram_pmap: list[str] = ["N", "D", "chi square"],
    output: widgets.Output = None,
):

    if output is not None:
        with output:
            output.clear_output(wait=True)

            # Get the widget's dimensions in pixels.
            widget_width = int(output.layout.width.replace("px", ""))
            widget_height = int(output.layout.height.replace("px", ""))

            # Convert widget dimensions to inches for the figure.
            dpi = 100  # Default DPI
            fig_width_in = widget_width / dpi
            fig_height_in = widget_height / dpi

            # Create a custom grid layout using gridspec.
            fig = plt.figure(figsize=(fig_width_in, fig_height_in))
            gs = GridSpec(
                3, 2, figure=fig, wspace=0.1, hspace=0.5
            )  # Updated to 3 rows for flexibility.

            # Create individual axes.
            ax1a = fig.add_subplot(gs[0, 0])  # Top-left subplot
            # ax1b = fig.add_subplot(gs[0, 1])  # Top-right subplot
            ax3a = fig.add_subplot(gs[2, 0])  # 2nd row left
            ax3b = fig.add_subplot(gs[2, 1])  # 2nd row right

            # fig.delaxes(ax1b)

            # Calculate nRMSD and SNR.
            nrmsd = calculate_nrmsd(
                observed=acf[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    :,
                ],
                predicted=fit[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    :,
                ],
                N_fit=fit_res[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    1,
                ],
            )

            snr = calculate_snr(
                cf=acf[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    :,
                ],
                last_lag=6,
            )

            # Plot individual components.
            plot_acfs(
                arr_acf=acf[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    :,
                ],
                arr_lag=lag,
                arr_fit=fit[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    :,
                ],
                with_fits=is_plot_with_fit,
                axs=ax1a,
            )

            plot_intensity_projection(
                array=avr_intensity,
                index=index,
                cmap="gray",
                xy_coordinate=xy_coordinate,
                gs=gs[0, 1],
                fig=fig,
            )

            plot_histograms_with_heatmaps(
                data=fit_res[
                    xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                    xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                    :,
                ],
                indices=indices_histogram_pmap,  # [1, 2, 12]
                labels=labels_histogram_pmap,  # ["N", "D", "chi square"]
                gs=gs[1, :],
                fig=fig,
            )
            plot_two_histograms(
                data1=nrmsd,
                data2=snr,
                bins=30,
                titles=("nRMSD", "SNR"),
                xlabels=("", ""),
                ylabels=("Frequency", "Frequency"),
                colors=("#FFC107", "#FFC107"),
                alphas=(0.7, 0.7),
                density=True,
                figsize=(12, 3),
                axs1=ax3a,
                axs2=ax3b,
            )
            plt.close(fig)  # supress interactive notebook line output
            display(fig)

    else:
        # Create a custom grid layout using gridspec.
        fig = plt.figure(figsize=(14, 12))
        gs = GridSpec(
            3, 2, figure=fig, wspace=0.1, hspace=0.5
        )  # Updated to 3 rows for flexibility.

        # Create individual axes
        ax1a = fig.add_subplot(gs[0, 0])  # Top-left subplot
        # ax1b = fig.add_subplot(gs[0, 1])  # Top-right subplot
        ax3a = fig.add_subplot(gs[2, 0])  # 2nd row left
        ax3b = fig.add_subplot(gs[2, 1])  # 2nd row right

        # fig.delaxes(ax1b)

        # Calculate nRMSD and SNR.
        nrmsd = calculate_nrmsd(
            observed=acf[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                :,
            ],
            predicted=fit[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                :,
            ],
            N_fit=fit_res[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                1,
            ],
        )

        snr = calculate_snr(
            cf=acf[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                :,
            ],
            last_lag=6,
        )

        # Plot individual components.
        plot_acfs(
            arr_acf=acf[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                :,
            ],
            arr_lag=lag,
            arr_fit=fit[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                :,
            ],
            with_fits=is_plot_with_fit,
            axs=ax1a,
        )

        plot_intensity_projection(
            array=avr_intensity,
            index=index,
            cmap="gray",
            xy_coordinate=xy_coordinate,
            gs=gs[0, 1],
            fig=fig,
        )

        plot_histograms_with_heatmaps(
            data=fit_res[
                xy_coordinate[1] : xy_coordinate[1] + xy_coordinate[3],
                xy_coordinate[0] : xy_coordinate[0] + xy_coordinate[2],
                :,
            ],
            indices=indices_histogram_pmap,  # [1, 2, 12]
            labels=labels_histogram_pmap,  # ["N", "D", "chi square"]
            gs=gs[1, :],
            fig=fig,
        )
        plot_two_histograms(
            data1=nrmsd,
            data2=snr,
            bins=30,
            titles=("nRMSD", "SNR"),
            xlabels=("", ""),
            ylabels=("Frequency", "Frequency"),
            colors=("#FFC107", "#FFC107"),
            alphas=(0.7, 0.7),
            density=True,
            figsize=(12, 3),
            axs1=ax3a,
            axs2=ax3b,
        )
