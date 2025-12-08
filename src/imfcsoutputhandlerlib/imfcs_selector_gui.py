import ipywidgets as widgets
from IPython.display import display

from .error_output_manager import ErrorOutputManager


class ImfcsScreenerGUI:
    """
    Graphical user interface for the IM-FCS screener.

    This class builds an interactive layout using ipywidgets for:
    - Loading raw data (with progress bar)
    - Selecting files and viewing associated metadata
    - Displaying selected images and console output
    - Toggling ROI selection and analysis views
    - Displaying error messages

    """

    debug_button: widgets.Button

    caption_select_file: widgets.HTML
    dropdown: widgets.Dropdown
    text_area: widgets.Textarea
    next_button: widgets.Button
    previous_button: widgets.Button
    clear_button: widgets.Button
    output: widgets.Output
    selected_filename: widgets.Label
    horizontal_line: widgets.HTML
    selected_input_folder_label: widgets.Label
    selected_image_output: widgets.Output
    caption_select_roi: widgets.HTML
    roi_selection_output: widgets.Output
    roi_selection_toggle_button = widgets.ToggleButton
    display_analysis_toggle_button = widgets.ToggleButton
    analysis_output: widgets.Output

    layout: widgets.VBox

    def __init__(self, error_manager: ErrorOutputManager):

        error_output: widgets.Output = error_manager.get_error_output()

        self.horizontal_line = widgets.HTML(
            value="<hr style='border: 1px solid gray;'>"
        )

        # Load raw data with progress bar.
        self.caption_load_raw_data = widgets.HTML(
            value="<span style='color: blue; font-weight: bold;'>(0) (Optional) load the database all at once, otherwise will be done on the fly</span>"
        )

        self.load_raw_start_button = widgets.Button(
            description="Start", button_style="success"
        )
        self.load_raw_stop_button = widgets.Button(
            description="Stop", button_style="danger"
        )
        self.load_raw_progress = widgets.IntProgress(
            value=0, min=0, max=100, description="Progress:"
        )
        self.load_raw_progress_label = widgets.Label(value="0%")
        self.load_raw_output = widgets.Output()

        # File selection.
        self.caption_select_file = widgets.HTML(
            value="<span style='color: blue; font-weight: bold;'>(1) Select file via Dropdown Menu or 'Next' and 'Previous' button</span>"
        )
        self.selected_input_folder_label = widgets.Label(value=("Input Folder: "))
        self.dropdown = widgets.Dropdown(
            description="Select File:", layout=widgets.Layout(width="80%")
        )
        self.text_area = widgets.Textarea(
            value="",
            description="Files:",
            layout=widgets.Layout(width="100%", height="70px"),
            disabled=True,
        )
        self.next_button = widgets.Button(description="Next")
        self.previous_button = widgets.Button(description="Previous")
        self.clear_button = widgets.Button(description="Clear Output")
        self.output = widgets.Output(
            layout=widgets.Layout(
                width="300px",
                height="300px",
                overflow="auto",  # Enable scrolling for overflowing content.
                border="1px dashed blue",
            )
        )
        self.selected_filename = widgets.Label(value=("Selected Image: "))
        self.selected_image_output = widgets.Output(
            layout=widgets.Layout(
                width="300px",
                height="300px",
                overflow="auto",  # Enable scrolling for overflowing content.
                border="1px dashed blue",
            )
        )

        # Select ROI.
        self.caption_select_roi = widgets.HTML(
            value="<span style='color: blue; font-weight: bold;'>(2) Select ROI with cursor</span>"
        )
        self.roi_selection_toggle_button = widgets.ToggleButton(
            value=False,
            description="ROI selection Off",  # Initial description.
            disabled=False,
            button_style="",  # Options: 'primary', 'success', 'info', 'warning', 'danger' or ''
            tooltip="Toggle Button",
            icon="toggle-off",  # Use an appropriate FontAwesome icon.
        )
        self.display_analysis_toggle_button = widgets.ToggleButton(
            value=False,
            description="Analysis Off",  # Initial description.
            disabled=False,
            button_style="",  # Options: 'primary', 'success', 'info', 'warning', 'danger' or ''
            tooltip="Toggle Button",
            icon="toggle-off",  # Use an appropriate FontAwesome icon.
        )
        self.roi_selection_output = widgets.Output(
            layout=widgets.Layout(
                width="600px",
                height="600px",
                overflow="auto",  # Enable scrolling for overflowing content.
                border="1px dashed blue",
                display="none",
            )
        )

        # Analysis window.
        self.analysis_output = widgets.Output(
            layout=widgets.Layout(
                width="1200px",
                height="800px",
                overflow="auto",  # Enable scrolling for overflowing content.
                border="1px dashed blue",
                display="none",
            )
        )

        # Debug.
        self.debug_button = widgets.Button(description="Debug")

        # Combine H and V boxes.
        disp_hbox1_file_selector = widgets.HBox(
            [self.previous_button, self.next_button, self.clear_button],
            layout=widgets.Layout(justify_content="center", padding="20px"),
        )

        disp_load_with_progress = widgets.VBox(
            [
                widgets.HBox([self.load_raw_start_button, self.load_raw_stop_button]),
                self.load_raw_progress,
                self.load_raw_progress_label,
                self.load_raw_output,
            ]
        )

        output_hbox = widgets.HBox([self.selected_image_output, self.output])

        toggle_disp_roi_hbox = widgets.HBox(
            [self.roi_selection_toggle_button, self.display_analysis_toggle_button]
        )

        # Create layout.
        self.layout = widgets.VBox(
            [
                self.caption_load_raw_data,
                disp_load_with_progress,
                self.horizontal_line,
                self.caption_select_file,
                self.selected_input_folder_label,
                self.dropdown,
                self.text_area,
                disp_hbox1_file_selector,
                self.selected_filename,
                output_hbox,
                self.horizontal_line,
                self.caption_select_roi,
                toggle_disp_roi_hbox,
                self.roi_selection_output,
                self.analysis_output,
                self.horizontal_line,
                error_output,
                self.debug_button,
            ],
            layout=widgets.Layout(padding="10px"),
        )

    def display(self):
        """Display the GUI."""
        display(self.layout)
