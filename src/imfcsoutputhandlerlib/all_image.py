import os
import pickle

from .image_info import ImageInfo


class AllImage:
    """
    Container class for storing and managing a collection of ``ImageInfo`` objects.
    """

    experiment_name: str
    list_image_info_object: list[ImageInfo]
    grouped_files: dict

    def __init__(self, experiment_name: str, group_files: dict):
        self.experiment_name = experiment_name
        self.grouped_files = group_files
        self.list_image_info_object = []

        for index, (key, value) in enumerate(self.grouped_files.items()):
            im = ImageInfo(key=key, associated_files=value)
            self.list_image_info_object.append(im)

        print(f"Total files: {len(self.list_image_info_object)}")

    # TODO: Handling Missing or Changed Methods.
    def __setstate__(self, state):
        """
        Restore object state during unpickling,
        including fallback handling for missing attributes or methods from older versions.
        """
        self.__dict__.update(state)

        # Handle missing methods by adding defaults.
        if not hasattr(self, "new_method"):
            self.new_method = self._default_new_method
            print("Missing 'new_method'. Added default implementation.")

        if not hasattr(self, "grouped_files"):
            self.grouped_files = {}
            print("Missing 'grouped_files'. Initialized empty.")

        if not hasattr(self, "list_image_info_object"):
            self.list_image_info_object = []
            print("Missing 'list_image_info_object'. Initialized empty.")

        if not hasattr(self, "experiment_name"):  # Fix potential typos.
            self.experiment_name = "Unknown Experiment"
            print("Missing 'experiment_name'. Initialized 'Unknown Experiment'.")

    def append(self, obj):
        self.list_image_info_object.append(obj)

    # Searching for an object by key.
    def get_image_info(self, key):
        """
        Retrieve an ``ImageInfo`` object by its key.
        """
        for image in self.list_image_info_object:
            if image.key == key:
                return image
        return None

    def get_list_of_image(self):
        return self.list_image_info_object

    def get_image_info_from_list(self, index):
        return self.list_image_info_object[index]

    def __repr__(self):
        return f"AllImage(experiment name={self.experiment_name})"

    def __len__(self):
        return len(self.list_image_info_object)

    def save(self, filename: str):
        """Save the object to a pickle file."""
        with open(filename, "wb") as f:
            pickle.dump(self, f)
        print(f"Object saved to {filename}")

    # TODO: New Default Method for Backward Compatibility.
    def _default_new_method(self):
        """Default implementation of a new method in case an old pickled object lacks it."""
        print("This is a default implementation for a missing method.")

    @classmethod
    def from_pickle(cls, filename: str):
        """Load the object safely from a pickle file, handling missing attributes."""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Pickle file '{filename}' not found.")

        with open(filename, "rb") as f:
            try:
                obj = pickle.load(f)
            except Exception as e:
                raise ValueError(f"Failed to load pickle file: {e}")

        return obj
