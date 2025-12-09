import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display
from matplotlib.widgets import RectangleSelector


class ROISelector:
    """
    Interactive rectangular ROI (region-of-interest) selector for 2D images.

    This class displays an image inside a Jupyter/IPython
    ``ipywidgets.Output`` widget and allows the user to draw a rectangular
    ROI using ``matplotlib.widgets.RectangleSelector``. The selected ROI
    is reported via a callback and shown in a label.
    """

    output: widgets.Output

    def __init__(self, output):
        """
        Initialize the ROISelector.
        """
        self.fig = None
        self.ax = None
        self.rectangle_selector = None
        self.coordinates_label = widgets.Label(value="No selection made yet.")
        self.output = output

    # Callback function for rectangle selection.
    def onselect(self, eclick, erelease):
        """
        Callback for rectangle selection.
        eclick and erelease are the press and release mouse events.
        """
        x_top = int(min(eclick.xdata, erelease.xdata))
        y_top = int(min(eclick.ydata, erelease.ydata))
        width = int(abs(eclick.xdata - erelease.xdata))
        height = int(abs(eclick.ydata - erelease.ydata))

        coords = {"x_top": x_top, "y_top": y_top, "width": width, "height": height}

        self.coordinates_label.value = f"ROI Selected: {list(coords.values())}."

        # Call the user-provided callback function, if available.
        if self.callback:
            self.callback(coords)

    def plot_roi_selection(
        self,
        index=0,
        array=None,
        cmap="gray",
        callback=None,
        current_coordinates: list[int] = None,
    ):
        """
        Plot the ROI selection tool for a specific index in the array.
        """

        self.callback = callback

        if current_coordinates is None:
            self.coordinates_label.value = "No selection made yet."
        else:
            self.coordinates_label.value = f"ROI Selected: {current_coordinates}."

        plt.close("all")

        with self.output:
            self.output.clear_output(wait=True)

            # Get the widget's dimensions in pixels.
            widget_width = int(self.output.layout.width.replace("px", "")) - 120
            widget_height = int(self.output.layout.height.replace("px", "")) - 120

            # Convert widget dimensions to inches for the figure.
            dpi = 100  # Default DPI
            fig_width_in = widget_width / dpi
            fig_height_in = widget_height / dpi

            self.fig, self.ax = plt.subplots(figsize=(fig_width_in, fig_height_in))
            self.ax.imshow(array[index, :, :], cmap=cmap)
            self.ax.set_title("Drag to select a region-of-interest (ROI)")

            # Initialize RectangleSelector.
            self.rectangle_selector = RectangleSelector(
                self.ax,
                self.onselect,
                interactive=True,
                button=[1],
                minspanx=5,
                minspany=5,
            )  # Minimum size for the rectangle.

            # Display.
            display(widgets.VBox([self.coordinates_label, self.fig.canvas]))

        self._show_output()

    def kill_plot_roi_selection(self):
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
