from ..utils import filename_utils


class ImfcsScreenerLogic:
    """
    Logic layer for managing input files and navigation in the ImFCS screener.

    This class is responsible for:
    - Discovering and grouping input files by basename.
    - Providing ordered keys for navigation.
    - Returning file lists associated with each key.

    """

    grouped_files: dict  # Dictionary with keys for basename and value with list of associated files.
    keys: list  # List of basename.
    input_path: str  # Path to input folder.

    def __init__(self, input_path, loaded_group_files: dict = None):
        if loaded_group_files is None:
            self.grouped_files = filename_utils.get_input_files(input_path=input_path)
        else:
            self.grouped_files = loaded_group_files
        self.keys = list(self.grouped_files.keys())
        self.input_path = input_path

    def get_next_key(self, current_key) -> str:
        """Return the next key in the list."""
        current_index = self.keys.index(current_key)
        if current_index < len(self.keys) - 1:
            return self.keys[current_index + 1]
        return current_key

    def get_previous_key(self, current_key) -> str:
        """Return the previous key in the list."""
        current_index = self.keys.index(current_key)
        if current_index > 0:
            return self.keys[current_index - 1]
        return current_key

    def get_files_for_key(self, key) -> list:
        """Return the files associated with a key."""
        return self.grouped_files[key]

    def get_intensity_excel_filename(self, key) -> list[str]:
        associated_files = self.get_files_for_key(key)
        return filename_utils.get_sorted_useful_filenames(input_list=associated_files)

    def get_input_path(self):
        return self.input_path

    def get_group_files(self):
        return self.grouped_files
