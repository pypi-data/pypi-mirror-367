"""
Image Linear Pixel Density Analyzer GUI

This module provides functionality for:
- Interactively selecting ROIs in images
- Fitting lines within selected ROIs
- Visualizing fitted lines and their properties
- Analyzing distances between multiple fitted lines

Dependencies:
    - cv2
    - numpy
    - matplotlib
    - line_collection (custom module)
    - distance_analyzer_core (custom module)
"""

import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import RectangleSelector
from linpxdens.core.line_collection import LineCollection
import linpxdens.core as core


def ask(prompt, default=True):
    """
    Prompt the user with a yes/no question.

    :param prompt: The question to display.
    :param default: The default response if the user presses enter.
    :return: True for 'yes', False for 'no'.
    """
    return _ask(f"{prompt} [Y/n]: ", default=default)


def _ask(prompt, default=None, true='y', false='n', exit='exit'):
    """
    Handle generic yes/no/exit input.

    :param prompt: The question string.
    :param default: Default return value if input is empty.
    :param true: Accepted input string for True.
    :param false: Accepted input string for False.
    :param exit: Input that triggers system exit.
    :return: Boolean response.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == '' and default is not None:
            return default
        elif user_input in (true, false):
            return user_input == true
        elif user_input == exit:
            sys.exit(0)
        else:
            print("Invalid input!")


def _confirm_roi_selection():
    """
    Ask user to confirm ROI selection.

    :return: True if user confirms, False otherwise.
    """
    return ask("Have you selected an ROI? [Y/n]: ", default=True)


def _confirm_fit_acceptance():
    """
    Ask user to confirm if the fitted line is acceptable.

    :return: True if accepted, False otherwise.
    """
    return ask("Is the acquired fit satisfying? [Y/n]: ", default=True)


def _ask_continue_fit():
    """
    Ask user if they want to perform another fit.

    :return: True to continue, False to stop.
    """
    return ask("Start another fit? [Y/n]: ", default=True)


def preprocess_image(image, roi_coords):
    """
    Preprocess the image by selecting the ROI and converting data type.

    :param image: Input image as NumPy array.
    :param roi_coords: Tuple (x, y, w, h) defining the ROI.
    :return: Cropped or original image as float32.
    """
    if np.issubdtype(image.dtype, np.unsignedinteger):
        image = image.astype(np.float32)
    if not roi_coords:
        return image
    else:
        x, y, w, h = roi_coords
        return image[y:y + h, x:x + w]


def _on_select(event_container, eclick, erelease):
    """
    Rectangle selector callback to store ROI coordinates.

    :param event_container: Dictionary to store selection.
    :param eclick: Mouse press event.
    :param erelease: Mouse release event.
    """
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)
    event_container['roi'] = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def _select_roi(selector, event_dict):
    """
    Wait for user to select ROI and confirm it.

    :param selector: RectangleSelector widget.
    :param event_dict: Dictionary storing selected ROI.
    :return: Tuple containing ROI coordinates.
    """
    selector.set_active(True)
    if 'roi' in event_dict:
        del event_dict['roi']
    while True:
        if _confirm_roi_selection():
            if 'roi' in event_dict:
                break
            else:
                print("No ROI found, try again.")
    selector.set_active(False)
    return event_dict['roi']


def _show_image_to_select_roi(image):
    """
    Show image in a window and allow user to draw ROI.

    :param image: Image as NumPy array.
    :return: Tuple of RectangleSelector and event_dict containing ROI.
    """
    fig_select, ax_select = plt.subplots()
    fig_select.suptitle("Select ROI from the Image", fontsize=16)
    ax_select.imshow(image, cmap='gray')
    event_dict = {}
    roi_selector = RectangleSelector(
        ax_select,
        lambda eclick, erelease: _on_select(event_dict, eclick, erelease),
        useblit=True,
        button=[1],
        minspanx=5,
        minspany=5,
        spancoords='pixels',
        interactive=True,
        ignore_event_outside=True,
        use_data_coordinates=True)
    ax_select.set_title("Drag to select ROI")
    fig_select.show()
    plt.show(block=False)
    plt.pause(1)
    return roi_selector, event_dict


def _add_line_to_plot(ax, line, shape):
    """
    Add a line and its center to the plot.

    :param ax: Matplotlib Axes object.
    :param line: Tuple (slope, intercept, (cx, cy)) of the fitted line.
    :param shape: Shape of the image.
    """
    slope, intercept, (center_x, center_y) = line
    x_img = np.array([0, shape[1]])
    y_img = slope * x_img + intercept
    line_obj, = ax.plot(x_img, y_img, color="green", linewidth=0.5)
    point, = ax.plot(center_x, center_y, marker='o', color='red', linestyle='None')
    labels = [f"Slope = {slope:.2f}", f"Center = ({center_x:.2f}, {center_y:.2f})"]
    ax.legend([line_obj, point], labels, ncol=1)
    plt.pause(0.05)


def _collect_lines(image, lines):
    """
    Interactive loop to collect multiple fitted lines from image.

    :param image: Input image as NumPy array.
    :param lines: LineCollection object to store fitted lines.
    """
    fig_selector = None
    image_shape = image.shape
    while True:
        if fig_selector is None or fig_selector.number not in plt.get_fignums():
            selector, event_dict = _show_image_to_select_roi(image)
            fig_selector = selector.ax.figure
            ax_selector = selector.ax
        roi = _select_roi(selector, event_dict)
        fitted_line = core.fit_line(image, roi)
        _add_line_to_plot(ax_selector, fitted_line, image_shape)
        if _confirm_fit_acceptance():
            lines.insert_line(fitted_line)
        else:
            line.remove()
            plt.pause(0.05)
        if not _ask_continue_fit():
            plt.close()
            break


def _plot_fit_results(image, centers, slope):
    """
    Plot image with fitted lines based on their center points and slope.

    :param image: Original image.
    :param centers: List of (x, y) center points.
    :param slope: Average slope of the fitted lines.
    """
    fig, ax = plt.subplots()
    fig.suptitle("Line Fit Result", fontsize=16)
    ax.imshow(image, cmap='gray')
    ax.set_title("Result of Fit")
    x = np.array([0, image.shape[1]])
    line_handle = None
    for i, center in enumerate(centers):
        y_fit = slope * (x - center[0]) + center[1]
        line, = ax.plot(x, y_fit, color='red', linewidth=0.5)
        if i == 0:
            line_handle = line
    if line_handle:
        ax.legend([line_handle], [f"Slope: {slope:.2f}"])
    plt.xlim(left=0, right=image.shape[1])
    plt.ylim(bottom=image.shape[0], top=0)
    fig.show()


def _plot_distance_distribution(mean, std, distances):
    """
    Plot histogram of distances between lines with mean and std lines.

    :param mean: Mean of distances.
    :param std: Standard deviation.
    :param distances: List of distance values.
    """
    fig, ax = plt.subplots()
    fig.suptitle("Distance Distribution", fontsize=16)
    ax.hist(distances, bins=30, edgecolor='black')
    ax.axvline(x=mean, color='orange', label=f"Mean = {mean:.2f}")
    ax.axvline(x=mean + (std / 2), color='green', linestyle='--', label=f"Std = {std:.2f}")
    ax.axvline(x=mean - (std / 2), color='green', linestyle='--')
    ax.legend()
    fig.show()


def analyze(image_path):
    """
    Analyze a given image by fitting lines and computing distances.

    :param image_path: Path to the image file.
    :return: Tuple (mean, std, distances) of line spacing.
    """
    image_path = core._validate_image_path(image_path)
    return _analyze(image_path)


def _analyze(image_path):
    """
    Internal implementation of the analyze function.

    :param image_path: Path to validated image.
    :return: Tuple (mean, std, distances).
    """
    image = core._load_image(image_path)
    lines = LineCollection()
    _collect_lines(image, lines)
    slope = lines.mean_slope
    centers = lines.centers
    _plot_fit_results(image, centers, slope)
    mean, std, distances = core.get_mean_distance(lines)
    _plot_distance_distribution(mean, std, distances)
    plt.show()
    return mean, std, distances


if __name__ == "__main__":
    sys.exit(0)
