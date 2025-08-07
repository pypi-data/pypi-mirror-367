"""
Core Linear Pixel Density Analyzer Module

Provides functionality to:
- Validate image paths and ROIs
- Load images
- Fit lines within specified ROIs
- Compute mean distance and statistics between fitted lines
- Perform high-level analysis combining these steps
"""

import cv2
import numpy as np
from .utils import _as_array_safe, _check_shape, _check_ndim, _check_min_length
from . import line_spacing_analyzer as lspa
from . import line_structure_analyzer as lstra
from .line_collection import LineCollection


def _validate_image_path(image_path, name="image_path"):
    """
    Validate that the input is a string pointing to a valid image file.

    :param image_path: Path to the image file.
    :param name: Parameter name for error messages.
    :return: Validated image path string.
    :raises ValueError: If validation fails.
    """
    if not isinstance(image_path, str) or not image_path.lower().endswith((".tif", ".png", ".jpg")):
        raise ValueError(f"{name} must be a valid image file path.")
    return image_path


def _validate_image(image, name="image"):
    """
    Validate that the image is non-empty and has 2 dimensions (grayscale).

    :param image: Image as a NumPy array.
    :param name: Parameter name for error messages.
    :return: Validated image array.
    :raises ValueError: If validation fails.
    """
    if image is None:
        raise ValueError(f"Could not load image.")
    _check_ndim(image, 2, name)
    if image.size == 0:
        raise ValueError(f"{name} must not be empty.")
    return image


def _validate_rois(rois, name="rois"):
    """
    Validate that ROIs are an array of shape (N, 4), where each row is (x, y, w, h).

    :param rois: List or array of ROIs.
    :param name: Parameter name for error messages.
    :return: Validated ROIs as NumPy array of integers.
    :raises ValueError: If validation fails.
    """
    rois = _as_array_safe(rois, name, dtype=int)
    _check_ndim(rois, 2, name)
    _check_shape(rois, (-1, 4))
    return rois


def _load_image(image_path):
    """
    Load image from the specified path and validate it.

    :param image_path: Path to the image file.
    :return: Loaded image as a NumPy array.
    """
    image = _validate_image(cv2.imread(image_path, cv2.IMREAD_UNCHANGED))
    return image


def fit_line(image, roi):
    """
    Fit a line to the specified region of interest (ROI) in the image.

    :param image: Image as a NumPy array.
    :param roi: Tuple (x, y, w, h) defining the ROI.
    :return: Tuple (slope, intercept, (center_x, center_y)) representing the fitted line.
    """
    x_roi, y_roi, w_roi, h_roi = roi
    (slope, intercept_roi), (x_center_roi, y_center_roi) = lstra.analyze_image_geometry(image, roi)
    x_center = x_center_roi + x_roi
    y_center = y_center_roi + y_roi
    intercept = intercept_roi + y_roi - slope * x_roi
    line = slope, intercept, (x_center, y_center)
    return line


def get_mean_distance(collection):
    """
    Compute the mean and standard deviation of distances between lines in the collection.

    :param collection: LineCollection object containing fitted lines.
    :return: Tuple (mean, std, distances) where distances is a list of individual distances.
    """
    centers = collection.centers
    slope = collection.mean_slope
    normal_vector = (-slope, 1)
    mean, std, distances = lspa.analyze_pattern(centers, normal_vector)
    return mean, std, distances


def analyze(image_path, rois):
    """
    High-level function to analyze an image given a set of ROIs.

    :param image_path: Path to the image file.
    :param rois: List or array of ROIs.
    :return: Tuple (mean, std, distances) of line spacing.
    """
    image_path = _validate_image_path(image_path)
    rois = _validate_rois(rois)
    return _analyze(image_path, rois)


def _analyze(image_path, rois):
    """
    Internal implementation of the analyze function.

    :param image_path: Validated path to the image file.
    :param rois: Validated ROIs.
    :return: Tuple (mean, std, distances).
    """
    image = _load_image(image_path)
    lines = LineCollection()
    for roi in rois:
        line = fit_line(image, roi)
        lines.insert_line(line)
    mean, std, distances = get_mean_distance(lines)
    return mean, std, distances


if __name__ == '__main__':
    import sys
    sys.exit(0)
