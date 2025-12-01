import os

import numpy as np
import tifffile

from . import util_filename
from .imfcs_util import saved_excel_reader


class ImageInfo:
    """
    A class to store information for each key in the dictionary.
    """

    rect_coordinates: dict
    is_roi_selected: bool

    key: str
    associated_files: list[str]

    lagtimes: np.array
    acf1: np.array
    sd1: np.array
    fit1: np.array
    fit1_param: np.array
    fit1_results: np.array

    avr_intensity: np.array

    is_excel_data_and_avr_intensity_loaded: bool

    def __init__(self, key: str, associated_files: list[str]):
        self.key = key
        self.associated_files = associated_files
        self.rect_coordinates = None
        self.is_roi_selected = None
        self.is_excel_data_and_avr_intensity_loaded = (
            False  # TODO: change when loading database from json
        )

    # Handle Backward Compatibility for Pickled Objects
    def __setstate__(self, state):
        """
        Called when unpickling to ensure all required attributes exist.
        Automatically handles missing attributes in older pickled versions.
        """
        self.__dict__.update(state)

        # Handle missing attributes (assign default values)
        if "rect_coordinates" not in state:
            self.rect_coordinates = None
            print("Missing 'rect_coordinates'. Initialized to None.")

        if "is_roi_selected" not in state:
            self.is_roi_selected = False
            print("Missing 'is_roi_selected'. Initialized to False.")

        if "is_excel_data_and_avr_intensity_loaded" not in state:
            self.is_excel_data_and_avr_intensity_loaded = False
            print(
                "Missing 'is_excel_data_and_avr_intensity_loaded'. Initialized to False."
            )

        # Handle missing large NumPy attributes
        for attr in [
            "lagtimes",
            "acf1",
            "sd1",
            "fit1",
            "fit1_param",
            "fit1_results",
            "avr_intensity",
        ]:
            if attr not in state:
                setattr(self, attr, np.array([]))  # Default to an empty NumPy array
                print(f"Missing '{attr}'. Initialized to empty NumPy array.")

    def add_coordinates(self, coordinate: dict):

        assert coordinate is not None, f"invalid coordinate {self}"

        if self.is_rect_coordinate_valid(coordinate):  # TODO
            self.rect_coordinates = coordinate
            self.is_roi_selected = True
        else:
            self.rect_coordinates = None
            self.is_roi_selected = False

    def is_rect_coordinate_valid(self, coordinate: dict):
        # TODO
        return True

    def get_coordinates(self):
        if self.rect_coordinates is not None:
            return list(self.rect_coordinates.values())
        else:
            return None

    def get_intensity_excel_filename(self, key) -> list[str]:
        filtered = []
        associated_files = self.get_files_for_key(key)
        for filename in associated_files:
            if filename.endswith("_AVR.tif") or (
                filename.endswith(".xlsx") and not filename.endswith("_metadata.xlsx")
            ):
                filtered.append(filename)

        sorted_files = sorted(filtered, key=lambda x: (not x.endswith(".tif"), x))

        return sorted_files

    def read_excel_df_and_avr_int(self, input_folder: str):

        if not self.is_excel_data_and_avr_intensity_loaded:

            # sort .tif and .xlsx file
            sorted_files = util_filename.get_sorted_useful_filenames(
                input_list=self.associated_files
            )

            excel_filename = [file for file in sorted_files if file.endswith(".xlsx")]
            assert len(excel_filename) == 1, "multiple .xlsx files"
            path_excel = os.path.join(input_folder, excel_filename[0])

            avr_intensity_filename = [
                file for file in sorted_files if file.endswith(".tif")
            ]
            assert len(avr_intensity_filename) == 1, "multiple .tif files"
            path_avr_intensity = os.path.join(input_folder, avr_intensity_filename[0])

            df = saved_excel_reader.read_excel_imfcs_saved(path_excel=path_excel)

            panel_param = [
                "Image width",
                "Image height",
                "Binning X",
                "Binning Y",
                "Overlap",
            ]
            param_dict = saved_excel_reader.get_param(
                excel_data=df, panel_param=panel_param
            )
            self.lagtimes = saved_excel_reader.get_lagtimes(excel_data=df)

            self.acf1 = saved_excel_reader.get_cfs(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                num_lag=self.lagtimes.shape[0],
                sheet_name="ACF1",
            )

            self.sd1 = saved_excel_reader.get_cfs(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                num_lag=self.lagtimes.shape[0],
                sheet_name="SD (ACF1)",
            )
            self.fit1 = saved_excel_reader.get_cfs(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                num_lag=self.lagtimes.shape[0],
                sheet_name="Fit functions (ACF1)",
            )

            self.fit1_param = saved_excel_reader.get_fit_param(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                sheet_name="Fit Parameters (ACF1)",
            )

            self.fit1_results = saved_excel_reader.get_fit_results(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                sheet_name="Fit Parameters (ACF1)",
            )
            self.fit1_results[:, :, 2] *= 10**12

            self.avr_intensity = tifffile.imread(path_avr_intensity)

            self.is_excel_data_and_avr_intensity_loaded = True

    def get_variable(self, variable_name: str):
        """
        Return the value of the instance variable matching the string argument.

        Parameters:
            variable_name (str): The name of the variable to retrieve.

        Returns:
            Any: The value of the requested variable, or None if it does not exist.
        """
        # Check if the attribute exists
        if hasattr(self, variable_name):
            return getattr(self, variable_name)
        else:
            if self.is_excel_data_and_avr_intensity_loaded:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{variable_name}'"
                )
            else:
                raise AttributeError(
                    f"'{type(self).__name__}' object attribute '{variable_name} has not been loaded'"
                )

    def __repr__(self):
        return (
            f"ImageInfo(key={self.key}, "
            f"associated_files={self.associated_files}, "
            f"rect_coordinates={self.rect_coordinates}, "
            f"is_roi_selected={self.is_roi_selected})"
        )
