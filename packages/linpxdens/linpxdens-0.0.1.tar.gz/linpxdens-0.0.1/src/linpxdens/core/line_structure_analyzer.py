"""
Line Structure Analyzer Module

Functions for detecting line extrema, filtering pixels, fitting lines,
and computing weighted centers from images or pixel data.
"""

import cv2
import numpy as np
from utils import _as_array_safe, _check_shape, _check_ndim, _check_min_length

_COL = 'column'
_ROW = 'row'
_INTENSITY = 'intensity'
_PIXELS_ARRAY_DTYPE = [(_COL, int), (_ROW, int), (_INTENSITY, float)]
_ALLOWED_METHODS = ("mean", "median")
_DEFAULT_METHOD = _ALLOWED_METHODS[0]
_DEFAULT_FILTER_LEVEL = 2

def _validate_image(image, name="image"):
    """
    Validate and convert image to structured array with correct dtype.

    :param image: Input image array.
    :param name: Name used for error messages.
    :return: Validated numpy structured array with _PIXELS_ARRAY_DTYPE.
    :raises ValueError: If the image is empty.
    """
    image = _as_array_safe(image, name, dtype=_PIXELS_ARRAY_DTYPE)
    if image.size == 0:
        raise ValueError(f"{name} must not be empty.")
    return image

def _validate_roi(roi, name="roi"):
    """
    Validate region of interest (ROI) as an array of shape (4,).

    :param roi: ROI array-like.
    :param name: Name used for error messages.
    :return: Validated numpy array of shape (4,).
    :raises ValueError: If shape is invalid.
    """
    roi = _as_array_safe(roi, name, dtype=int)
    _check_shape(roi, (4,), name)
    return roi

def _validate_method(method, name="method"):
    """
    Validate filtering method string.

    :param method: Method string.
    :param name: Name used for error messages.
    :return: Valid method string.
    :raises ValueError: If method not in allowed methods.
    """
    if method not in _ALLOWED_METHODS:
        raise ValueError(f"Invalid {name}. Choose from {_ALLOWED_METHODS}.")
    return method

def _validate_filter_level(filter_level, name="filter_level"):
    """
    Validate filter level as positive number.

    :param filter_level: Numeric filter level.
    :param name: Name used for error messages.
    :return: Validated filter level.
    :raises ValueError: If filter_level is not positive.
    """
    if not isinstance(filter_level, (int, float)) or filter_level <= 0:
        raise ValueError(f"{name} must be a positive number.")
    return filter_level

def _validate_pixel(pixels, name="pixels"):
    """
    Validate pixels structured array.

    :param pixels: Array of pixels.
    :param name: Name used for error messages.
    :return: Validated pixels array.
    :raises ValueError: If pixels length < 2 or all intensities zero.
    """
    pixels = _as_array_safe(pixels, name, dtype=_PIXELS_ARRAY_DTYPE)
    _check_min_length(pixels, 2, name)
    if np.all(pixels[_INTENSITY] == 0):
        raise ValueError(f"Cannot compute center: all weights in {name} are zero.")
    return pixels

def crop_image_to_roi(image, roi):
    """
    Crop an image to the specified ROI.

    :param image: Image array.
    :param roi: ROI tuple or array (x, y, w, h).
    :return: Cropped image array.
    :raises ValueError: If ROI is out of image bounds.
    """
    image = _validate_image(image)
    roi = _validate_roi(roi)
    return _crop_image_to_roi(image, roi)

def _crop_image_to_roi(image, roi):
    """
    Internal function to crop image to ROI without validation.

    :param image: Image array.
    :param roi: ROI tuple (x, y, w, h).
    :return: Cropped image array.
    """
    x, y, w, h = roi
    if x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
        raise ValueError("ROI is out of image bounds.")
    return image[y:y+h, x:x+w]

def _detect_extremum(line):
    """
    Detect position and value of an extremum (min or max) in a 1D line.

    :param line: 1D numpy array of intensity values.
    :return: Tuple (position, value) of detected extremum.
    """
    line = _as_array_safe(line)
    position_min = np.argmin(line)
    position_max = np.argmax(line)
    first_deriv = np.diff(line)
    min_part = first_deriv[:position_min] if position_min > 0 else np.array([0])
    max_part = first_deriv[:position_max] if position_max > 0 else np.array([0])
    min_part_sum = np.sum(min_part)
    max_part_sum = np.sum(max_part)
    trend = line[0] - line[-1]
    if trend > 0:
        min_part_sum += trend
    else:
        max_part_sum += trend
    if min_part_sum < 0:
        return position_min, line[position_min]
    elif max_part_sum > 0:
        return position_max, line[position_max]
    else:
        return 0, line[0]

def _locate_column_extrema(image):
    """
    Locate extrema in each column of an image.

    :param image: Structured image array.
    :return: Structured array of extrema pixels per column.
    """
    extrema = np.zeros(image.shape[1], dtype=_PIXELS_ARRAY_DTYPE)
    for x, column in enumerate(image.T):
        y, value = _detect_extremum(column[_INTENSITY])
        extrema[x] = (x, y, value)
    return extrema

def _locate_row_extrema(image):
    """
    Locate extrema in each row of an image.

    :param image: Structured image array.
    :return: Structured array of extrema pixels per row.
    """
    extrema = np.zeros(image.shape[0], dtype=_PIXELS_ARRAY_DTYPE)
    for y, row in enumerate(image):
        x, value = _detect_extremum(row[_INTENSITY])
        extrema[y] = (x, y, value)
    return extrema

def get_data_pixels_from_image(image):
    """
    Extract data pixels representing extrema intersections from an image.

    :param image: Input image array.
    :return: Structured array of data pixels.
    """
    image = _validate_image(image)
    return _get_data_pixels_from_image(image)

def _get_data_pixels_from_image(image):
    """
    Internal function to extract data pixels from image extrema.

    :param image: Structured image array.
    :return: Structured array of unique data pixels.
    """
    column_extrema = _locate_column_extrema(image)
    row_extrema = _locate_row_extrema(image)
    intersection_pixels = (np.intersect1d(row_extrema, column_extrema))
    row_filtered = row_extrema[np.isin(row_extrema[_COL], intersection_pixels[_COL])]
    column_filtered = column_extrema[np.isin(column_extrema[_ROW], intersection_pixels[_ROW])]
    data_pixels = np.unique(np.concatenate((row_filtered, column_filtered)), axis=0)
    return data_pixels

def filter_pixel_outliers(pixels, method=_DEFAULT_METHOD, filter_level=_DEFAULT_FILTER_LEVEL):
    """
    Filter pixel intensity outliers using mean or median method.

    :param pixels: Structured array of pixels.
    :param method: Filtering method ('mean' or 'median').
    :param filter_level: Level for filtering sensitivity.
    :return: Filtered pixels array.
    """
    pixels = _validate_pixel(pixels)
    method = _validate_method(method)
    filter_level = _validate_filter_level(filter_level)
    return _filter_pixel_outliers(pixels, method, filter_level)

def _filter_pixel_outliers(pixels, method, filter_level):
    """
    Internal function to filter pixel outliers.

    :param pixels: Pixels array.
    :param method: 'mean' or 'median'.
    :param filter_level: Filtering level.
    :return: Filtered pixels array.
    """
    values = pixels[_INTENSITY]
    if method == "mean":
        center = np.mean(values)
        tolerance = np.std(values)
    elif method == "median":
        center = np.median(values)
        mad = np.median(np.abs(values - center))
        tolerance = 0.6745 * mad * filter_level
    lower, upper = center - tolerance, center + tolerance
    return pixels[(values >= lower) & (values <= upper)]

def fit_line_to_pixels(pixels):
    """
    Fit a linear polynomial (line) to pixel coordinates.

    :param pixels: Structured array of pixels.
    :return: Tuple (slope, intercept) of the fitted line.
    """
    pixels = _validate_pixel(pixels)
    return _fit_line_to_pixels(pixels)

def _fit_line_to_pixels(pixels):
    """
    Internal line fitting using numpy.polyfit.

    :param pixels: Pixels array.
    :return: (slope, intercept) tuple.
    """
    return np.polyfit(pixels[_COL], pixels[_ROW], 1)

def compute_weighted_center(pixels):
    """
    Compute weighted center of pixels using intensity as weights.

    :param pixels: Pixels array.
    :return: Numpy array [x_center, y_center].
    """
    pixels = _validate_pixel(pixels)
    return _compute_weighted_center(pixels)

def _compute_weighted_center(pixels):
    """
    Internal computation of weighted center.

    :param pixels: Pixels array.
    :return: Array with weighted center coordinates.
    """
    weights = pixels[_INTENSITY]
    x_center = np.sum(pixels[_COL] * weights) / np.sum(weights)
    y_center = np.sum(pixels[_ROW] * weights) / np.sum(weights)
    return np.array([x_center, y_center])

def analyze_image_geometry(image, roi=None, method=_DEFAULT_METHOD, filter_level=_DEFAULT_FILTER_LEVEL):
    """
    Analyze image geometry to fit line and compute center within optional ROI.

    :param image: Input image array.
    :param roi: Optional ROI tuple (x, y, w, h).
    :param method: Filtering method for pixel outliers.
    :param filter_level: Filtering sensitivity level.
    :return: Tuple (line_fit, center) where line_fit=(slope, intercept) and center is weighted center array.
    """
    image = _validate_image(image)
    if roi is not None:
        roi = _validate_roi(roi)
        image = crop_image_to_roi(image, roi)
    method = _validate_method(method)
    filter_level = _validate_filter_level(filter_level)
    return _analyze_image_geometry(image, method, filter_level)

def _analyze_image_geometry(image, method, filter_level):
    """
    Internal function to perform line fitting and center computation.

    :param image: Image array.
    :param method: Filtering method.
    :param filter_level: Filtering level.
    :return: Tuple (line_fit, center).
    """
    if np.issubdtype(image.dtype, np.unsignedinteger):
        image = image.astype(np.float32)
    pixels = _get_data_pixels_from_image(image)
    filtered_pixels = filter_pixel_outliers(pixels, method, filter_level)
    center = compute_weighted_center(filtered_pixels)
    line_fit = fit_line_to_pixels(filtered_pixels)
    return line_fit, center

if __name__ == '__main__':
    import sys
    sys.exit(0)
