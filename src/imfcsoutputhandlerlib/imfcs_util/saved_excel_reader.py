import math
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def check_matching_metadata():
    # iterate through metadata file for all basename and check for matching parameters
    pass


def read_excel_imfcs_saved(path_excel: str):
    return pd.ExcelFile(path_excel)


def get_param(excel_data: pd.DataFrame, panel_param: list[str]):
    assert (
        "Panel Parameters" in excel_data.sheet_names
    ), "Panel Parameters is not in the sheet"

    # Extract Image width and Image height based on their parameter names
    panel_parameters_sheet = excel_data.parse(
        sheet_name="Panel Parameters", header=None
    )

    first_column = panel_parameters_sheet.iloc[:, 0]  # First column by index
    values = []
    for j in panel_param:
        index = first_column[first_column == j].index

        assert not index.empty, " index empty"
        # print(f"The value '{j}' is found at index: {index[0]}, val: {panel_parameters_sheet.iloc[index[0], 1]}")
        values.append(panel_parameters_sheet.iloc[index[0], 1])

    param_dict = {key: value for key, value in zip(panel_param, values)}
    return param_dict


def get_lagtimes(excel_data: pd.DataFrame):
    sn = "lagtime"
    assert sn in excel_data.sheet_names, f"{sn} is not in the sheet"

    # Load lagtimes
    lagtime_sheet = excel_data.parse(sheet_name=sn, header=None)
    lagtimes = lagtime_sheet.iloc[1:, 1].to_numpy()

    return lagtimes


def get_cfs(
    excel_data: pd.DataFrame, width: int, height: int, num_lag: int, sheet_name: str
):
    # TODO: slow. can be improved 1) convert panda to numpy 2) Use numpy Directly for Numeric Sheets
    # Sheet names: "ACF1", "SD (ACF1)", "Fit functions (ACF1)"
    assert sheet_name in excel_data.sheet_names, f"{sheet_name} is not in the sheet"

    sheet = excel_data.parse(sheet_name=sheet_name, header=None)

    res = np.empty((height, width, num_lag), dtype=float)

    for i in range(height):
        for j in range(width):
            row_idx = j + (i * height)
            res[i][j] = sheet.iloc[row_idx, 1:]

    return res


def get_fit_param(excel_data: pd.DataFrame, width: int, height: int, sheet_name: str):
    # Sheet names: "Fit Parameters (ACF1)", "Fit Parameters (ACF2)", "Fit Parameters (CCF)"
    assert sheet_name in excel_data.sheet_names, f"{sheet_name} is not in the sheet"

    sheet = excel_data.parse(sheet_name=sheet_name, header=None)

    return sheet.iloc[0, 1:].to_list()


def get_fit_results(excel_data: pd.DataFrame, width: int, height: int, sheet_name: str):
    # TODO: slow. can be improved 1) convert panda to numpy 2) Use numpy Directly for Numeric Sheets
    # Sheet names: "Fit Parameters (ACF1)", "Fit Parameters (ACF2)", "Fit Parameters (CCF)"
    assert sheet_name in excel_data.sheet_names, f"{sheet_name} is not in the sheet"

    sheet = excel_data.parse(sheet_name=sheet_name, header=None)

    fit_param = get_fit_param(
        excel_data=excel_data, width=width, height=height, sheet_name=sheet_name
    )
    num_param = len(fit_param)

    res = np.zeros((height, width, num_param), dtype=float)

    # fill N, D, .. valid pixels onwards
    for i in range(height):
        for j in range(width):
            row_idx = j + (i * height) + 1
            res[i, j, 1:] = sheet.iloc[row_idx, 2:]

    # fill fitted
    for i in range(height):
        for j in range(width):
            row_idx = j + (i * height) + 1
            val = str(sheet.iloc[row_idx, 1])
            if val in ["true", "false"]:
                val = 1.0 if val == "true" else 0.0
            res[i, j, 0] = val

    return res


def get_psf(excel_data: pd.DataFrame):

    sheet_name = "PSF"
    assert sheet_name in excel_data.sheet_names, f"{sheet_name} is not in the sheet"

    sheet = excel_data.parse(sheet_name=sheet_name, header=None)

    search_value = "PSF start"
    row_index = int(sheet[sheet.iloc[:, 0] == search_value].index[0]) + 1

    # reading psf calibration parameter
    parameters = {
        "psf start": float(sheet.iloc[row_index, 0]),
        "psf end": float(sheet.iloc[row_index, 1]),
        "psf step": float(sheet.iloc[row_index, 2]),
        "num psf": math.ceil(
            (
                (float(sheet.iloc[row_index, 1]) - float(sheet.iloc[row_index, 0]))
                / float(sheet.iloc[row_index, 2])
                + 1
            )
        ),
        "num bin": row_index - 3,
        "bin start": int(sheet.iloc[1, 0]),
        "bin end": int(sheet.iloc[1, 0]) + row_index - 3 - 1,
    }

    # Fill array with D and std D for each combination of pixel bin and PSF value
    arr = np.zeros((parameters["num psf"], parameters["num bin"], 2), dtype=float)

    for i in range(parameters["num psf"]):
        for j in range(parameters["num bin"]):
            c = i * 3
            r = j + 1
            arr[i, j, :] = sheet.iloc[r, c + 1 : c + 3]

    return parameters, arr


if __name__ == "__main__":
    print(f"Script File Name: {__file__}")
