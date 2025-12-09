import os

import numpy as np
import tifffile

from ..io import (
    get_cfs,
    get_fit_param,
    get_fit_results,
    get_lagtimes,
    get_param,
    read_excel_imfcs_saved,
)
from ..utils import filename_utils


class ImageInfo:
    """
    Class to store and manage data and metadata for a single image/key entry.

    Parameters
    ----------
    key : str
        Identifier associated with this image entry (e.g., basename of a file group).
    associated_files : list of str
        List of file paths associated with this image/key.

    Attributes
    ----------
    rect_coordinates : dict or None
        Dictionary storing ROI rectangle coordinates, or ``None`` if not set.
    is_roi_selected : bool or None
        Flag indicating whether a valid ROI has been selected.
    key : str
        Identifier for this image entry.
    associated_files : list of str
        Associated filenames for this image entry.
    lagtimes : numpy.ndarray
        1D array of lag times.
    acf1 : numpy.ndarray
        3D array containing autocorrelation function data.
    sd1 : numpy.ndarray
        3D array containing standard deviation of ACF data.
    fit1 : numpy.ndarray
        3D array containing fit functions for ACF data.
    fit1_param : numpy.ndarray
        Array containing fit parameter values.
    fit1_results : numpy.ndarray
        Array containing fit results (e.g., parameter maps).
    avr_intensity : numpy.ndarray
        Average intensity image stack.
    is_excel_data_and_avr_intensity_loaded : bool
        Flag indicating whether Excel-derived data and average intensity have
        been loaded from disk.
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
            False  # TODO: change when loading database from json.
        )

    # Handle Backward Compatibility for Pickled Objects.
    def __setstate__(self, state):
        """
        Called when unpickling to ensure all required attributes exist.
        Automatically handles missing attributes in older pickled versions.
        """
        self.__dict__.update(state)

        # Handle missing attributes (assign default values).
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

        # Handle missing large NumPy attributes.
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
                setattr(self, attr, np.array([]))  # Default to an empty NumPy array.
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
        """
        Check whether the provided rectangle coordinates are valid.

        Parameters
        ----------
        coordinate : dict
            Rectangle coordinate specification to validate.

        Returns
        -------
        bool
            ``True`` if the coordinates are considered valid, ``False`` otherwise.
        """
        # TODO
        return True

    def get_coordinates(self):
        """
        Return the ROI coordinates as a list.

        Returns
        -------
        list or None
            List of coordinate values if available, otherwise ``None``.
        """
        if self.rect_coordinates is not None:
            return list(self.rect_coordinates.values())
        else:
            return None

    def get_intensity_excel_filename(self, key) -> list[str]:
        """
        Return the list of intensity-related filenames (TIFF and Excel) for a key.

        Parameters
        ----------
        key : str
            Key used to filter associated files. Typically matches ``self.key``.

        Returns
        -------
        list of str
            Sorted list of filenames containing average intensity (``*_AVR.tif``)
            and the main Excel file (``*.xlsx`` but not ``*_metadata.xlsx``).
        """

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
        """
        Load Excel-based correlation data and average intensity images from disk.

        Parameters
        ----------
        input_folder : str
            Path to the folder containing the associated Excel and TIFF files.

        Notes
        -----
        - Only runs once per instance; subsequent calls are skipped unless the
          `is_excel_data_and_avr_intensity_loaded` flag is reset.
        - Populates the following attributes:

          ``lagtimes``, ``acf1``, ``sd1``, ``fit1``, ``fit1_param``,
          ``fit1_results``, and ``avr_intensity``.
        """

        if not self.is_excel_data_and_avr_intensity_loaded:

            # Sort .tif and .xlsx file.
            sorted_files = filename_utils.get_sorted_useful_filenames(
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

            df = read_excel_imfcs_saved(path_excel=path_excel)

            panel_param = [
                "Image width",
                "Image height",
                "Binning X",
                "Binning Y",
                "Overlap",
            ]
            param_dict = get_param(excel_data=df, panel_param=panel_param)
            self.lagtimes = get_lagtimes(excel_data=df)

            self.acf1 = get_cfs(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                num_lag=self.lagtimes.shape[0],
                sheet_name="ACF1",
            )

            self.sd1 = get_cfs(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                num_lag=self.lagtimes.shape[0],
                sheet_name="SD (ACF1)",
            )
            self.fit1 = get_cfs(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                num_lag=self.lagtimes.shape[0],
                sheet_name="Fit functions (ACF1)",
            )

            self.fit1_param = get_fit_param(
                excel_data=df,
                width=int(param_dict["Image width"]),
                height=int(param_dict["Image height"]),
                sheet_name="Fit Parameters (ACF1)",
            )

            self.fit1_results = get_fit_results(
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
        Return the value of an instance attribute by name.

        Parameters
        ----------
        variable_name : str
            Name of the attribute to retrieve.

        Returns
        -------
        any
            Value of the requested attribute.

        Raises
        ------
        AttributeError
            If the attribute does not exist, or if it has not yet been loaded
            (for Excel/averaged-intensity–dependent attributes).
        """
        # Check if the attribute exists.
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

    def __repr__(self):
        return (
            f"ImageInfo(key={self.key}, "
            f"associated_files={self.associated_files}, "
            f"rect_coordinates={self.rect_coordinates}, "
            f"is_roi_selected={self.is_roi_selected})"
        )

    def __repr__(self):
        return (
            f"ImageInfo(key={self.key}, "
            f"associated_files={self.associated_files}, "
            f"rect_coordinates={self.rect_coordinates}, "
            f"is_roi_selected={self.is_roi_selected})"
        )
