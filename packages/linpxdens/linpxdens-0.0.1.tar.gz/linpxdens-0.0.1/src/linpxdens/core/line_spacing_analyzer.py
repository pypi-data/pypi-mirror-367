import numpy as np
from utils import _as_array_safe, _check_shape, _check_ndim, _check_min_length

def _validate_direction_vector(direction_vector, name="direction_vector"):
    """
    Validate a 2D direction vector.

    :param direction_vector: Array-like, expected shape (2,).
    :param name: Name for error messages.
    :return: numpy.ndarray, validated vector of shape (2,).
    :raises ValueError: If vector components are infinite or zero vector.
    """
    vector = _as_array_safe(direction_vector, name)
    _check_ndim(vector, 1, name)
    _check_shape(vector, (2,), name)
    if np.any(np.isinf(vector)):
        raise ValueError(f"{name} components cannot be infinite.")
    if np.all(vector == 0):
        raise ValueError(f"{name} cannot be the zero vector (0, 0).")
    return vector

def _validate_position_values(position_values, name="position_values"):
    """
    Validate position values array (1D, at least length 2).

    :param position_values: Array-like 1D values.
    :param name: Name for error messages.
    :return: numpy.ndarray validated position values.
    """
    values = _as_array_safe(position_values, name)
    _check_ndim(values, 1, name)
    _check_min_length(values, 2, name)
    return values

def _validate_distance_values(distance_values, name="distance_values"):
    """
    Validate distance values array (1D, at least length 1).

    :param distance_values: Array-like 1D values.
    :param name: Name for error messages.
    :return: numpy.ndarray validated distance values.
    """
    values = _as_array_safe(distance_values, name)
    _check_ndim(values, 1, name)
    _check_min_length(values, 1, name)
    return values

def _validate_data(data, name="data"):
    """
    Validate generic 1D data array with at least 1 element.

    :param data: Array-like data.
    :param name: Name for error messages.
    :return: numpy.ndarray validated data.
    """
    data = _as_array_safe(data, name)
    _check_ndim(data, 1, name)
    _check_min_length(data, 1, name)
    return data

def _validate_points(points, name="points"):
    """
    Validate 2D points array with shape (N, 2), N >= 2.

    :param points: Array-like points.
    :param name: Name for error messages.
    :return: numpy.ndarray validated points array.
    """
    points = _as_array_safe(points, name)
    _check_ndim(points, 2, name)
    _check_shape(points, (-1, 2), name)
    _check_min_length(points, 2, name)
    return points

def project_points_orthogonal(points, direction_vector):
    """
    Project 2D points orthogonally onto a direction vector.

    :param points: Array-like shape (N, 2), points coordinates.
    :param direction_vector: Array-like shape (2,), direction vector.
    :return: numpy.ndarray 1D array of projections.
    """
    points = _validate_points(points)
    vector = _validate_direction_vector(direction_vector)
    return _project_points_orthogonal(points, vector)

def _project_points_orthogonal(points, vector):
    """
    Internal function to project points orthogonally on normalized vector.

    :param points: numpy.ndarray shape (N, 2).
    :param vector: numpy.ndarray normalized vector (2,).
    :return: numpy.ndarray projections (N,).
    """
    norm_vector = vector / np.linalg.norm(vector)
    return points @ norm_vector

def filter_outliers(data):
    """
    Filter outliers from 1D data using median absolute deviation.

    :param data: Array-like 1D data.
    :return: numpy.ndarray filtered data within tolerance.
    """
    data = _validate_data(data)
    return _filter_outliers(data)

def _filter_outliers(data):
    """
    Internal function for median-based outlier filtering.

    :param data: numpy.ndarray 1D.
    :return: numpy.ndarray filtered data.
    """
    median = np.median(data)
    median_abs_dev = np.median(np.abs(data - median))
    tolerance = 2 * 0.6745 * median_abs_dev
    is_within_tolerance = np.isclose(data, median, atol=tolerance)
    return data[is_within_tolerance]

def estimate_base_period(position_values):
    """
    Estimate base period from position values by averaging filtered differences.

    :param position_values: Array-like 1D position values.
    :return: float estimated base period.
    """
    values = _validate_position_values(position_values)
    return _estimate_base_period(values)

def _estimate_base_period(values):
    """
    Internal base period estimation from position differences.

    :param values: numpy.ndarray 1D position values.
    :return: float estimated base period.
    """
    distances = np.diff(values)
    filter_distances = _filter_outliers(distances)
    return np.mean(filter_distances)

def compute_pairwise_distances(position_values):
    """
    Compute all pairwise absolute distances between position values.

    :param position_values: Array-like 1D position values.
    :return: numpy.ndarray 1D array of pairwise distances.
    """
    values = _validate_position_values(position_values)
    return _compute_pairwise_distances(values)

def _compute_pairwise_distances(values):
    """
    Internal computation of pairwise distances from values.

    :param values: numpy.ndarray 1D.
    :return: numpy.ndarray 1D pairwise distances.
    """
    diff_matrix = np.abs(values[:, None] - values[None, :])
    i_upper, j_upper = np.triu_indices(len(values), k=1)
    distance_values = diff_matrix[i_upper, j_upper]
    return distance_values

def filter_periodic_distance_values(distance_values, period):
    """
    Filter distance values that are multiples of a given period.

    :param distance_values: Array-like 1D distance values.
    :param period: float base period.
    :return: numpy.ndarray base distance values after filtering.
    """
    values = _validate_distance_values(distance_values)
    return _filter_periodic_distance_values(values, period)

def _filter_periodic_distance_values(values, period):
    """
    Internal filtering of distance values close to multiples of period.

    :param values: numpy.ndarray 1D distances.
    :param period: float base period.
    :return: numpy.ndarray filtered base distances.
    """
    distance_ratios = values / period
    median_ratios_dev = np.median(np.abs(distance_ratios - np.round(distance_ratios)))
    tolerance = 2 * median_ratios_dev
    is_period_multiple = np.isclose(distance_ratios, np.round(distance_ratios), atol=tolerance)
    period_multiples = np.round(distance_ratios[is_period_multiple]).astype(int)
    filtered_values = values[is_period_multiple]
    base_values = filtered_values / period_multiples
    return base_values

def calculate_mean_distance(distance_values):
    """
    Calculate mean and standard deviation of distance values.

    :param distance_values: Array-like 1D distances.
    :return: Tuple (mean, std) of distances.
    """
    values = _validate_distance_values(distance_values)
    return _calculate_mean_distance(values)

def _calculate_mean_distance(values):
    """
    Internal calculation of mean and standard deviation.

    :param values: numpy.ndarray 1D distances.
    :return: Tuple (mean, std).
    """
    mean_distance = np.mean(values)
    std_distance = np.std(values)
    return mean_distance, std_distance

def analyze_pattern(points, direction_vector):
    """
    Analyze periodic pattern in points projected onto direction vector.

    :param points: Array-like shape (N, 2), coordinates.
    :param direction_vector: Vector (2,) or scalar slope.
    :return: Tuple (mean_distance, std_dev, base_distances).
    """
    if isinstance(direction_vector, (int, float)):
        direction_vector = np.array([1.0, direction_vector])
    direction_vector = _validate_direction_vector(direction_vector)
    points = _validate_points(points)
    return _analyze_pattern(points, direction_vector)

def _analyze_pattern(points, vector):
    """
    Internal pattern analysis pipeline.

    :param points: numpy.ndarray shape (N, 2).
    :param vector: numpy.ndarray normalized vector (2,).
    :return: Tuple (mean_distance, std_dev, base_distances).
    """
    projection = _project_points_orthogonal(points, vector)
    period = _estimate_base_period(projection)
    distances = _compute_pairwise_distances(projection)
    base_distances = _filter_periodic_distance_values(distances, period)
    mean_distance, mean_distance_std = _calculate_mean_distance(base_distances)
    return mean_distance, mean_distance_std, base_distances

if __name__ == '__main__':
    import sys
    sys.exit(0)
