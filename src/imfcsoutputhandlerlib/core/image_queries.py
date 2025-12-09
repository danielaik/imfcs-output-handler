import numpy as np

from .all_image import AllImage


def get_total_num_cell(allimage: AllImage):
    """
    Return the total number of distict file (i.e., the number of ``ImageInfo`` objects)
    stored in an ``AllImage`` instance.

    Parameters
    ----------
    allimage : AllImage
        The ``AllImage`` object containing a list of image entries.

    Returns
    -------
    int
        The number of image objects in the dataset.
    """

    return len(allimage.get_list_of_image())


def get_array_intensity(allimage: AllImage, cell_index: int = None):
    """
    Return the average intensity array for a specific cell or for all cells.

    Parameters
    ----------
    allimage : AllImage
        The ``AllImage`` object containing multiple ``ImageInfo`` entries.
    cell_index : int, optional
        Index of the cell whose intensity array should be returned.
        If ``None`` (default), the function returns a stacked array
        containing intensities for all cells.

    Returns
    -------
    numpy.ndarray
        If ``cell_index`` is provided:
            Returns an array of shape ``(n, w, h)`` representing the
            average intensity of a single cell.

        If ``cell_index`` is ``None``:
            Returns a stacked array of shape ``(num_cells, n, w, h)``,
            where ``num_cells`` is the number of ``ImageInfo`` objects in ``allimage``.

    Notes
    -----
    This function assumes all images have the same spatial dimensions.
    A consistency check may be added in the future.
    """

    if cell_index is not None:
        arr_int_single_cell = allimage.get_image_info_from_list(
            cell_index
        ).get_variable(variable_name="avr_intensity")
        return arr_int_single_cell
    else:
        # Sample the first frame, assume all files has the same dimension TODO: add checker.
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
    Return the parameter map array for a specific cell or for all cells.

    Parameters
    ----------
    allimage : AllImage
        The ``AllImage`` instance containing multiple ``ImageInfo`` entries.
    cell_index : int, optional
        Index of the cell whose parameter map should be retrieved.
        If ``None`` (default), the function returns a stacked array
        containing the parameter maps for all cells.

    Returns
    -------
    numpy.ndarray
        If ``cell_index`` is provided:
            Returns an array of shape ``(w, h, p)`` where each pixel
            contains a parameter vector.

        If ``cell_index`` is ``None``:
            Returns an array of shape ``(num_cells, w, h, p)`` containing
            parameter maps for all cells.

    Notes
    -----
    This function assumes that all parameter maps share identical
    dimensions. A dimension consistency check may be added later.
    """

    if cell_index is not None:
        arr_pmap_single_cell = allimage.get_image_info_from_list(
            cell_index
        ).get_variable(variable_name="fit1_results")
        return arr_pmap_single_cell
    else:
        # Assume all files has the same dimension TODO: add checker.
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
    Return a list of file identifiers (keys) for all images in the dataset.

    Parameters
    ----------
    allimage : AllImage
        The ``AllImage`` instance containing multiple ``ImageInfo`` objects.

    Returns
    -------
    list of str
        A list of file IDs, typically corresponding to the basename
        of TIFF stacks or other image group identifiers.
    """

    num_cell = get_total_num_cell(allimage)
    l_id = [img.key for img in allimage.get_list_of_image()]
    return l_id


def get_cfs_related(allimage: AllImage, var: str = "acf1", cell_index: int = None):
    # option for var = acf1, sd1, fit1

    """
    Return correlation-function–related arrays (e.g., ``acf1``, ``sd1``, ``fit1``)
    for a specific cell or for all cells.

    Parameters
    ----------
    allimage : AllImage
        The ``AllImage`` instance containing multiple ``ImageInfo`` entries.
    var : str, optional
        Name of the variable to retrieve from each ``ImageInfo`` object.
        Common options include ``"acf1"``, ``"sd1"``, and ``"fit1"``.
        Default is ``"acf1"``.
    cell_index : int, optional
        Index of the cell whose correlation-function array should be returned.
        If ``None`` (default), the function returns a stacked array for all cells.

    Returns
    -------
    numpy.ndarray
        If ``cell_index`` is provided:
            Returns an array of shape ``(w, h, lag)`` corresponding to the
            selected correlation-function variable for one cell.

        If ``cell_index`` is ``None``:
            Returns an array of shape ``(num_cells, w, h, lag)`` containing
            the variable for all cells.

    Notes
    -----
    - Assumes all files share identical spatial and lag dimensions.
    - Assumes all pixels are processed using the same correlator configuration.
    """

    if cell_index is not None:
        arr_single_cell = allimage.get_image_info_from_list(cell_index).get_variable(
            variable_name=var
        )
        return arr_single_cell
    else:
        # Assume all files has the same dimension TODO: add checker.
        # Assume all pixel in each file are processed the same way with identical correlator scheme.
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
    Return the lag-time array for a specific cell or for all cells.

    Parameters
    ----------
    allimage : AllImage
        The ``AllImage`` instance containing multiple ``ImageInfo`` objects.
    cell_index : int, optional
        Index of the cell to retrieve lag times from.
        If ``None`` (default), lag times for all cells are returned.

    Returns
    -------
    numpy.ndarray
        If ``cell_index`` is provided:
            Returns a 1D array of lag times for the selected cell.

        If ``cell_index`` is ``None``:
            Returns a 2D array of shape ``(num_cells, lag)`` containing
            the lag times for all cells.

    Notes
    -----
    Assumes all cells have the same lag-time dimensionality and were processed
    with the same correlator scheme.
    """

    var = "lagtimes"

    if cell_index is not None:
        lagtimes_single_cell = allimage.get_image_info_from_list(
            cell_index
        ).get_variable(variable_name=var)
        return lagtimes_single_cell
    else:
        # Assume all pixel in each file are processed the same way with identical correlator scheme.
        num_cell = get_total_num_cell(allimage)
        lag = get_lagtimes(allimage, 0).shape[0]
        lagtimes_all_cell = np.empty((num_cell, lag))
        for i in range(num_cell):
            lagtimes_all_cell[i, :] = allimage.get_image_info_from_list(i).get_variable(
                variable_name=var
            )
        return lagtimes_all_cell
