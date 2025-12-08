import time

import matplotlib.pyplot as plt
from IPython.display import display

from .all_image import AllImage
from .display_analysis import DisplayAnalysis
from .error_output_manager import ErrorOutputManager
from .imfcs_output_data_loader import (
    OutputDataLoaderMultiThread,
    OutputDataLoaderSingleThread,
)
from .imfcs_selector_gui import ImfcsScreenerGUI
from .imfcs_selector_logic import ImfcsScreenerLogic
from .imfcs_selector_process import ImfcsScreenerProcess
from .roi_selector import ROISelector


class ImfcsScreenerApp:
    """
    High-level application class for the ImFCS screener.

    This class wires together the GUI, logic, processing pipeline, ROI selection,
    display of analysis, and raw-data loading for an ImFCS screening workflow.
    """

    gui: ImfcsScreenerGUI
    logic: ImfcsScreenerLogic
    process: ImfcsScreenerProcess
    list_all_image: AllImage
    # raw_data_loader: OutputDataLoaderMultiThread
    raw_data_loader: OutputDataLoaderSingleThread
    roi_selector: ROISelector
    display_analysis: DisplayAnalysis
    error_manager: ErrorOutputManager

    def __init__(self, input_path: str, loaded_database: AllImage = None):
        self.error_manager = ErrorOutputManager()
        self.gui = ImfcsScreenerGUI(error_manager=self.error_manager)

        # Setup from scratch or previously saved database.
        if loaded_database is None:
            self.logic = ImfcsScreenerLogic(input_path=input_path)
            self.list_all_image = AllImage(
                experiment_name="exp1", group_files=self.logic.get_group_files()
            )
        else:
            self.logic = ImfcsScreenerLogic(
                input_path=input_path, loaded_group_files=loaded_database.grouped_files
            )
            self.list_all_image = loaded_database
            print(
                f"Total files loaded from database: {len(self.list_all_image.list_image_info_object)}"
            )

        self.roi_selector = ROISelector(output=self.gui.roi_selection_output)
        self.display_analysis = DisplayAnalysis(output=self.gui.analysis_output)
        self.process = ImfcsScreenerProcess(
            logic=self.logic,
            gui=self.gui,
            allimage=self.list_all_image,
            roi_selector=self.roi_selector,
            display_analysis=self.display_analysis,
        )

        """
        self.raw_data_loader = OutputDataLoaderMultiThread(
            list_all_image_object=self.list_all_image,
            progress=self.gui.load_raw_progress,
            progress_label=self.gui.load_raw_progress_label,
            output=self.gui.load_raw_output,
            input_folder=self.logic.get_input_path(),
        )
        """

        self.raw_data_loader = OutputDataLoaderSingleThread(
            list_all_image_object=self.list_all_image,
            progress=self.gui.load_raw_progress,
            progress_label=self.gui.load_raw_progress_label,
            output=self.gui.load_raw_output,
            input_folder=self.logic.get_input_path(),
        )

        # Initialize dropdown options and value.
        self.gui.dropdown.options = self.logic.keys
        self.gui.dropdown.value = self.logic.keys[0]

        # Initialize.
        self.update_text_area(None)
        self.update_selected_filename_label(None)
        self.update_selected_input_folder()
        self.process.display_selected_image(key=self.gui.dropdown.value)

        # Attach event handlers.
        self.gui.debug_button.on_click(self.on_debug_button_clicked)
        self.gui.clear_button.on_click(self.on_clear_button_clicked)
        self.gui.next_button.on_click(lambda b: self.on_next_button_clicked(b, "next"))
        self.gui.previous_button.on_click(
            lambda b: self.on_previous_button_clicked(b, "previous")
        )
        self.gui.dropdown.observe(self.update_text_area, names="value")
        self.gui.dropdown.observe(self.callback_dropdown_filename, names="value")
        self.gui.dropdown.observe(self.callback_dropdown_showimage, names="value")
        self.gui.load_raw_start_button.on_click(self.raw_data_loader.on_start_clicked)
        self.gui.load_raw_stop_button.on_click(self.raw_data_loader.on_stop_clicked)
        self.gui.roi_selection_toggle_button.observe(
            self.on_roi_selection_toggle_change, names="value"
        )
        self.gui.display_analysis_toggle_button.observe(
            self.on_display_analysis_toggle_change, names="value"
        )

        for _ in range(5):
            print()  # Prints an empty line.

    def on_debug_button_clicked(self, b):
        # Example Usage: Trigger an error.
        try:
            raise ValueError("This is a test error!")
        except ValueError as e:
            self.error_manager.display_error(str(e))

        # Example: Clear and hide the error output after handling.
        time.sleep(3)
        self.error_manager.clear_error()

    def on_clear_button_clicked(self, b):
        """Handle Clear button click."""
        self.gui.output.clear_output()
        self.gui.roi_selection_output.clear_output()

    def on_next_button_clicked(self, b, label):
        """Handle Next button click."""

        current_key = self.gui.dropdown.value
        next_key = self.logic.get_next_key(current_key)
        self.gui.dropdown.value = next_key
        self.update_selected_filename_label(self.gui.dropdown.value)
        self.process.display_selected_image(key=self.gui.dropdown.value)

        self.gui.roi_selection_output.clear_output()
        self.process.set_roi_selection_output(key=self.gui.dropdown.value)

        with self.gui.output:
            print(f"click: {label}")

    def on_previous_button_clicked(self, b, label):
        """Handle Previous button click."""
        current_key = self.gui.dropdown.value
        previous_key = self.logic.get_previous_key(current_key)
        self.gui.dropdown.value = previous_key
        self.update_selected_filename_label(self.gui.dropdown.value)
        self.process.display_selected_image(key=self.gui.dropdown.value)

        self.gui.roi_selection_output.clear_output()
        self.process.set_roi_selection_output(key=self.gui.dropdown.value)

        with self.gui.output:
            print(f"click: {label}")

    def update_text_area(self, change):
        """Update the text area based on the selected dropdown value."""
        selected_key = self.gui.dropdown.value
        associated_files = self.logic.get_files_for_key(selected_key)
        self.gui.text_area.value = "\n".join(associated_files)

    def update_selected_filename_label(self, value):
        if value is None:
            self.gui.selected_filename.value = "Selected Image: {}".format(
                self.gui.dropdown.value
            )
        else:
            self.gui.selected_filename.value = "Selected Image: {}".format(value)

    def update_selected_input_folder(self):
        self.gui.selected_input_folder_label.value = "Input Folder: {}".format(
            self.logic.get_input_path()
        )

    def callback_dropdown_filename(self, change):
        if change is None:
            self.update_selected_filename_label(change)
        else:
            self.update_selected_filename_label(change["new"])

    def callback_dropdown_showimage(self, change):
        if change is not None:
            self.process.display_selected_image(key=change["new"])

    def on_roi_selection_toggle_change(self, change):
        if change["new"]:
            self.gui.roi_selection_toggle_button.description = "ROI Selection On"
            self.gui.roi_selection_toggle_button.icon = "toggle-on"
        else:
            self.gui.roi_selection_toggle_button.description = "ROI Selection Off"
            self.gui.roi_selection_toggle_button.icon = "toggle-off"

        self.process.set_roi_selection_output(key=self.gui.dropdown.value)

    def on_display_analysis_toggle_change(self, change):
        if change["new"]:
            self.gui.display_analysis_toggle_button.description = "Analysis On"
            self.gui.display_analysis_toggle_button.icon = "toggle-on"
        else:
            self.gui.display_analysis_toggle_button.description = "Analysis Off"
            self.gui.display_analysis_toggle_button.icon = "toggle-off"

        self.process.set_analysis_output(key=self.gui.dropdown.value)

    def get_AllImage(self) -> AllImage:
        return self.list_all_image

    def run(self):
        """Run the application."""
        self.gui.display()

    # TODELETE
    def test(self):
        print("display output")
        display(self.gui.load_raw_output)
