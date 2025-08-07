import numpy as np

def _as_array_safe(array_like, name="input", dtype=float):
    """
    Safely converts input to a numpy array with specified dtype.

    Parameters:
        array_like: array-like
            Input data to convert to numpy array.
        name: str, optional
            Name used in error messages (default is "input").
        dtype: data-type, optional
            Desired numpy dtype of the output array (default is float).

    Returns:
        np.ndarray:
            Converted numpy array with specified dtype.

    Raises:
        TypeError: If conversion to numpy array with given dtype fails.
    """
    try:
        return np.asarray(array_like, dtype=dtype)
    except Exception as e:
        raise TypeError(f"Could not convert {name} to an array with dtype {dtype}: {e}")

def _check_shape(array_data, expected_shape, name="input"):
    """
    Checks if the input array has the expected shape dimensions.

    Parameters:
        array_data: np.ndarray
            Array to check.
        expected_shape: tuple
            Expected shape tuple. Use -1 for any size in that dimension.
        name: str, optional
            Name used in error messages (default is "input").

    Raises:
        ValueError: If array shape doesn't match expected shape.
    """
    actual_shape = array_data.shape
    if len(actual_shape) != len(expected_shape):
        raise ValueError(f"{name} must have shape {expected_shape}, got {actual_shape}.")
    for i, expected in enumerate(expected_shape):
        if expected != -1 and expected != actual_shape[i]:
            raise ValueError(f"{name} must have shape {expected_shape}, got {actual_shape}.")

def _check_ndim(array_data, ndim, name="input"):
    """
    Checks if the input array has the expected number of dimensions.

    Parameters:
        array_data: np.ndarray
            Array to check.
        ndim: int
            Expected number of dimensions.
        name: str, optional
            Name used in error messages (default is "input").

    Raises:
        ValueError: If array dimensionality doesn't match expected ndim.
    """
    if array_data.ndim != ndim:
        raise ValueError(f"{name} must be {ndim}D, got {array_data.ndim}D.")

def _check_min_length(array_data, min_len, name="input"):
    """
    Checks if the input array has at least a minimum number of elements.

    Parameters:
        array_data: np.ndarray
            Array to check.
        min_len: int
            Minimum number of elements required.
        name: str, optional
            Name used in error messages (default is "input").

    Raises:
        ValueError: If array length is less than min_len.
    """
    if array_data.shape[0] < min_len:
        raise ValueError(f"{name} must contain at least {min_len} elements, got {array_data.shape[0]}.")

if __name__ == '__main__':
    import sys
    sys.exit(0)
