import numpy as np


def calculate_nrmsd(observed: np.array, predicted: np.array, N_fit: np.array):
    """
    Compute the normalized root-mean-square deviation (NRMSD) between
    observed and predicted correlation curves.

    Parameters
    ----------
    observed : numpy.ndarray
        3D array of observed values with shape ``(n, m, t)``, where:
        - ``n`` is the number of rows,
        - ``m`` is the number of columns,
        - ``t`` is the number of lag times.
    predicted : numpy.ndarray
        3D array of predicted values with the same shape as ``observed``.
    N_fit : numpy.ndarray
        2D array of normalization factors with shape ``(n, m)``.
        Each value corresponds to the estimated particle number ``N`` at each pixel.

    Returns
    -------
    numpy.ndarray
        2D array of NRMSD values with shape ``(n, m)``, where each element
        represents the NRMSD for the corresponding pixel.

    Notes
    -----
    - Lag time index 0 is excluded from the NRMSD calculation.
    - NRMSD is computed as:

      ``NRMSD(n, m) = sqrt(sum((observed - predicted)^2)) * N_fit``

    Raises
    ------
    ValueError
        If ``observed`` and ``predicted`` do not have matching shapes.
    """

    if observed.shape != predicted.shape:
        raise ValueError("Observed and predicted arrays must have the same shape.")

    # Calculate residuals, square them, and take the mean along the last axis (t).
    # Exclude time lag = 0.
    residuals_squared_mean = np.sum(
        (observed[:, :, 1:] - predicted[:, :, 1:]) ** 2, axis=2
    )

    # Compute the square root of the mean residuals to get RMSD.
    rmsd_matrix = np.sqrt(residuals_squared_mean)

    # Normalisation.
    rmsd_matrix *= N_fit

    return rmsd_matrix


def calculate_snr(cf: np.array, last_lag: int = 6):
    """
    Compute the signal-to-noise ratio (SNR) of an autocorrelation function (ACF)
    for each pixel using vectorized operations.

    Parameters
    ----------
    cf : numpy.ndarray
        3D array of autocorrelation values with shape ``(n, m, t)``, where:
        - ``n`` : number of rows (pixels along axis 0)
        - ``m`` : number of columns (pixels along axis 1)
        - ``t`` : number of lag times
    last_lag : int, optional
        Number of initial lag times (starting from lag index 1) used for
        computing the SNR. Default is ``6``, meaning lag times ``1`` to ``5``
        are included.

    Returns
    -------
    numpy.ndarray
        2D array of shape ``(n, m)`` containing the SNR for each pixel.

    Notes
    -----
    - Lag time index ``0`` is excluded because it contains the autocorrelation
      amplitude and does not represent noise behavior.
    - SNR is defined as:

      ``SNR = mean(cf[lag 1 : lag N]) / std(cf[lag 1 : lag N])``

    - Division by zero will produce ``inf`` or ``nan`` in accordance with
      NumPy's broadcasting rules.

    Raises
    ------
    ValueError
        If ``last_lag`` is less than or equal to 1.
    """

    mean = np.mean(cf[:, :, 1:last_lag], axis=2)
    std = np.std(cf[:, :, 1:last_lag], axis=2)

    snr = np.divide(mean, std)

    return snr
