import ipywidgets as widgets
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from ..core.image_info import ImageInfo
from . import plotter


class DisplayAnalysis:
    """
    A utility class for displaying analysis plots inside an IPython/Jupyter.
    """

    output: widgets.Output
    fig: plt.figure
    gs: GridSpec

    def __init__(self, output):
        self.output = output
        self.fig = None
        self.gs = None

    def plot_analysis(self, current_coordinates: list, image_info: ImageInfo):

        plotter.plot_combined_analysis_imfcs(
            fig=self.fig,
            gs=self.gs,
            acf=image_info.get_variable("acf1"),
            lag=image_info.get_variable("lagtimes"),
            fit=image_info.get_variable("fit1"),
            avr_intensity=image_info.get_variable("avr_intensity"),
            xy_coordinate=image_info.get_coordinates(),
            fit_res=image_info.get_variable("fit1_results"),
            index=0,
            is_plot_with_fit=True,
            indices_histogram_pmap=[1, 2, 12],
            labels_histogram_pmap=["N", "D", "chi square"],
            output=self.output,
        )

        self._show_output()

    def kill_plot_analysis(self):
        plt.close("all")
        with self.output:
            self.output.clear_output()
        self._hide_output()

    def _show_output(self):
        """Make the Output widget visible."""
        self.output.layout.display = "block"

    def _hide_output(self):
        """Hide the Output widget."""
        self.output.layout.display = "none"
