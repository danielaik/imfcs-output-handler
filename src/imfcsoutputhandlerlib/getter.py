import numpy as np

from .all_image import AllImage


def get_total_num_cell(allimage: AllImage):
    """
    return the number of cells or distinct file in the database

    Args:
        allimage (AllImage): _description_

    Returns:
        _type_: _description_
    """
    return len(allimage.get_list_of_image())


def get_array_intensity(allimage: AllImage, cell_index: int = None):
    """
    Return the average intensity of one cell or all cells
    Args:
        allimage (AllImage): _description_
        cell_index (int, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    if cell_index is not None:
        arr_int_single_cell = allimage.get_image_info_from_list(
            cell_index
        ).get_variable(variable_name="avr_intensity")
        return arr_int_single_cell
    else:
        # sample the first frame, assume all files has the same dimension TODO: add checker
        num_cell = get_total_num_cell(allimage)
        n, w, h = get_array_intensity(allimage, 0).shape
        array_int_all_cell = np.empty((num_cell, n, w, h))
        for i in range(num_cell):
            array_int_all_cell[i, :, :, :] = allimage.get_image_info_from_list(
                i
            ).get_variable(variable_name="avr_intensity")
        return array_int_all_cell


def get_array_parameter_map(allimage: AllImage, cell_index: int = None):
    """
    Return the parameter map of one cell or all cells

    Args:
        allimage (AllImage): _description_
        cell_index (int, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    if cell_index is not None:
        arr_pmap_single_cell = allimage.get_image_info_from_list(
            cell_index
        ).get_variable(variable_name="fit1_results")
        return arr_pmap_single_cell
    else:
        # assume all files has the same dimension TODO: add checker
        num_cell = get_total_num_cell(allimage)
        w, h, p = get_array_parameter_map(allimage, 0).shape
        arr_pmap_all_cell = np.empty((num_cell, w, h, p))
        for i in range(num_cell):
            arr_pmap_all_cell[i, :, :, :] = allimage.get_image_info_from_list(
                i
            ).get_variable(variable_name="fit1_results")
        return arr_pmap_all_cell


def get_list_of_file_id(allimage: AllImage):
    """
    get the list of file ID, the basename of tiff stacks

    Args:
        allimage (AllImage): _description_

    Returns:
        _type_: _description_
    """
    num_cell = get_total_num_cell(allimage)
    l_id = [img.key for img in allimage.get_list_of_image()]
    return l_id


def get_cfs_related(allimage: AllImage, var: str = "acf1", cell_index: int = None):
    # option for var = acf1, sd1, fit1

    """
    get acf1, sd1, fit1 values for each pixels in a cell or all cells

    Returns:
        _type_: _description_
    """

    if cell_index is not None:
        arr_single_cell = allimage.get_image_info_from_list(cell_index).get_variable(
            variable_name=var
        )
        return arr_single_cell
    else:
        # assume all files has the same dimension TODO: add checker
        # assume all pixel in each file are processed the same way with identical correlator scheme
        num_cell = get_total_num_cell(allimage)
        w, h, lag = get_cfs_related(allimage, var, 0).shape
        arr_all_cell = np.empty((num_cell, w, h, lag))
        for i in range(num_cell):
            arr_all_cell[i, :, :, :] = allimage.get_image_info_from_list(
                i
            ).get_variable(variable_name=var)
        return arr_all_cell


def get_lagtimes(allimage: AllImage, cell_index: int = None):
    """
    get lagtimes for a single cell or all cells


    Returns:
        _type_: _description_
    """

    var = "lagtimes"

    if cell_index is not None:
        lagtimes_single_cell = allimage.get_image_info_from_list(
            cell_index
        ).get_variable(variable_name=var)
        return lagtimes_single_cell
    else:
        # assume all pixel in each file are processed the same way with identical correlator scheme
        num_cell = get_total_num_cell(allimage)
        lag = get_lagtimes(allimage, 0).shape[0]
        lagtimes_all_cell = np.empty((num_cell, lag))
        for i in range(num_cell):
            lagtimes_all_cell[i, :] = allimage.get_image_info_from_list(i).get_variable(
                variable_name=var
            )
        return lagtimes_all_cell
