import os

import tifffile
from IPython.display import display

from . import plotter
from .all_image import AllImage
from .display_analysis import DisplayAnalysis
from .imfcs_selector_gui import ImfcsScreenerGUI
from .imfcs_selector_logic import ImfcsScreenerLogic
from .roi_selector import ROISelector


class ImfcsScreenerProcess:

    logic: ImfcsScreenerLogic
    gui: ImfcsScreenerGUI
    list_all_image: AllImage
    roi_selector: ROISelector
    display_analysis: DisplayAnalysis

    def __init__(
        self,
        logic: ImfcsScreenerLogic,
        gui: ImfcsScreenerGUI,
        allimage: AllImage,
        roi_selector: ROISelector,
        display_analysis: DisplayAnalysis,
    ):
        self.logic = logic
        self.gui = gui
        self.list_all_image = allimage
        self.roi_selector = roi_selector
        self.display_analysis = display_analysis

    def display_selected_image(self, key):
        # tiffile read image everytime function is called. Consider storing value for faster performance at expense of memory
        to_be_process_fn = self.logic.get_intensity_excel_filename(key)
        output = self.gui.selected_image_output
        input_path = self.logic.get_input_path()

        assert to_be_process_fn[0].endswith(
            "_AVR.tif"
        ), f"{key} no file with _AVR.tif suffix"
        path_avr = os.path.join(input_path, to_be_process_fn[0])

        avr_intensity = tifffile.imread(path_avr)

        im = self.list_all_image.get_image_info(key)
        coord = im.get_coordinates()

        plotter.plot_selected_image_full_frame(
            output=output, array=avr_intensity, index=0, xy_coordinate=coord
        )

    def set_roi_selection_output(self, key):

        display_on = self.gui.roi_selection_toggle_button.value
        assert isinstance(
            display_on, bool
        ), "on_roi_selection_toggle_change value is not boolean"

        if display_on:
            to_be_process_fn = self.logic.get_intensity_excel_filename(key)
            input_path = self.logic.get_input_path()

            assert to_be_process_fn[0].endswith(
                "_AVR.tif"
            ), f"{key} no file with _AVR.tif suffix"

            path_avr = os.path.join(input_path, to_be_process_fn[0])
            avr_intensity = tifffile.imread(path_avr)

            def handle_coords(coords):
                # store selected coordinate
                im = self.list_all_image.get_image_info(key)
                im.add_coordinates(coordinate=coords)

                # if toggle display analysis is on
                if self.gui.display_analysis_toggle_button.value:
                    current_coordinates = self.list_all_image.get_image_info(
                        key
                    ).get_coordinates()
                    im = self.list_all_image.get_image_info(key)
                    self.display_analysis.plot_analysis(
                        current_coordinates=current_coordinates, image_info=im
                    )

            current_coordinates = self.list_all_image.get_image_info(
                key
            ).get_coordinates()

            self.roi_selector.plot_roi_selection(
                index=0,
                array=avr_intensity,
                cmap="gray",
                callback=handle_coords,
                current_coordinates=current_coordinates,
            )

        else:
            self.roi_selector.kill_plot_roi_selection()

    def set_analysis_output(self, key):

        is_display_on = self.gui.display_analysis_toggle_button.value
        assert isinstance(
            is_display_on, bool
        ), "display_analysis_toggle_button value is not boolean"

        if is_display_on:
            current_coordinates = self.list_all_image.get_image_info(
                key
            ).get_coordinates()
            im = self.list_all_image.get_image_info(key)
            self.display_analysis.plot_analysis(
                current_coordinates=current_coordinates, image_info=im
            )

        else:
            self.display_analysis.kill_plot_analysis()

    def read_raw_data(self, input):
        input_path = self.logic.get_input_path()
        if input[0].endswith(".tif"):
            path_avr = os.path.join(input_path, input[0])
            print(f"path avr: {path_avr}")

            avr_intensity = tifffile.imread(path_avr)
            plotter.plot_intensity_projection(
                array=avr_intensity, index=0, xy_coordinate=[15, 30, 50, 50]
            )

        if input[1].endswith(".xlsx"):
            path_excel = os.path.join(input_path, input[1])
            print(f"path excel: {path_excel}")
