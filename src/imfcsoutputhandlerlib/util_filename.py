import os
from collections import defaultdict


def get_input_files(input_path: str) -> dict:
    input_files = []

    for file in os.listdir(input_path):
        if file.endswith((".tif", ".xlsx")):
            input_files.append(file)

    grouped_files = defaultdict(list)

    for file_name in input_files:
        base_name = "_".join(
            file_name.split("_")[:-1]
        )  # Remove the last suffix starting with "_"
        grouped_files[base_name].append(file_name)

    grouped_files = dict(sorted(grouped_files.items()))

    return grouped_files


def get_sorted_useful_filenames(input_list: list[str]) -> list[str]:
    # find usable filename for analysis and sort .tif first followed by .xlsx second
    filtered = []
    for filename in input_list:
        if filename.endswith("_AVR.tif") or (
            filename.endswith(".xlsx") and not filename.endswith("_metadata.xlsx")
        ):
            filtered.append(filename)

    sorted_files = sorted(filtered, key=lambda x: (not x.endswith(".tif"), x))

    return sorted_files
