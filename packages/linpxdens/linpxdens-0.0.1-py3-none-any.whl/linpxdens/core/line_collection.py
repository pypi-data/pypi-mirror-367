"""
Line Collection Module

Defines the LineCollection class to manage a collection of lines,
each represented by slope, intercept, center coordinates, and a unique ID.
"""

import numpy as np
import random

class LineCollection():
    """
    Collection class to manage multiple lines with properties and unique IDs.

    Each line is stored as a structured NumPy array with fields:
    - id (string): unique identifier for the line.
    - slope (float): slope of the line.
    - intercept (float): y-intercept of the line.
    - center (2-float tuple): center point (x, y) on the line.
    """

    _ID = 'id'
    _SLOPE = 'slope'
    _INTERCEPT = 'intercept'
    _CENTER = 'center'
    _DTYPE = np.dtype([(_ID, 'U4'), (_SLOPE, 'float'), (_INTERCEPT, 'float'), (_CENTER, '2f4')])

    def __init__(self):
        """
        Initialize an empty LineCollection.
        """
        self._lines = []

    def __iter__(self):
        """
        Iterator over stored lines.

        :return: Iterator of line structured arrays.
        """
        return iter(self._lines)

    def __len__(self):
        """
        Number of lines in the collection.

        :return: Integer count of lines.
        """
        return len(self._lines)

    def _check_tuple(self, input):
        """
        Validate that input tuple is length 3 with correct types.

        :param input: Tuple to validate (slope, intercept, center).
        :raises ValueError: If tuple length is not 3 or center length not 2.
        :raises TypeError: If elements are not numeric.
        """
        if len(input) == 3:
            if not isinstance(input[2], tuple) or len(input[2]) != 2:
                raise ValueError(f"Third element must be a tuple of length 2")
            if not all(isinstance(x, (int, float)) for x in (input[0], input[1], input[2][0], input[2][1])):
                raise TypeError("All elements must be int or float.")
        else:
            raise ValueError(f"Expected tuple of length 3")

    def _check_struc_array(self, input):
        """
        Validate that input numpy structured array matches expected dtype (except ID).

        :param input: numpy structured array to validate.
        :raises TypeError: If dtype mismatch.
        """
        expected_dtype = np.dtype(self._DTYPE.descr[1:])
        if input.dtype != expected_dtype:
            raise TypeError(f"Expected dtype (except id) {expected_dtype}, got {input.dtype}")

    def insert_line(self, line):
        """
        Insert a new line into the collection with a unique ID.

        :param line: Tuple (slope, intercept, center) or structured numpy array.
        :return: Generated unique ID string for the line.
        :raises TypeError: If line format is invalid.
        """
        new_id = self._generate_unique_id()
        if isinstance(line, tuple):
            self._check_tuple(line)
            full_line = (new_id,) + line
            struct_line = np.array(full_line, dtype=self._DTYPE)
        elif isinstance(line, np.ndarray):
            self._check_struc_array(line)
            struct_line = np.empty((), dtype=self._DTYPE)  # 0-dim scalar
            struct_line[self._ID] = new_id
            for name in line.dtype.names:
                struct_line[name] = line[name]
        else:
            raise TypeError("Line must be a tuple or structured numpy array with fields slope, intercept, center")
        self._lines.append(struct_line)
        return new_id

    def remove_line(self, line_id):
        """
        Remove a line by its unique ID.

        :param line_id: String ID of the line to remove.
        :return: True if removal successful.
        :raises KeyError: If no line with given ID exists.
        """
        for i, line in enumerate(self._lines):
            if line[self._ID] == line_id:
                del self._lines[i]
                return True
        raise KeyError(f"Line with id {line_id} not found.")

    def _generate_unique_id(self):
        """
        Generate a new unique 4-digit string ID for a line.

        :return: Unique ID string.
        """
        existing_ids = [line[self._ID] for line in self._lines]
        while True:
            new_id = f"{random.randint(0, 9999):04d}"
            if new_id not in existing_ids:
                return new_id

    def _get_column(self, name):
        """
        Extract a column of values from all lines by field name.

        :param name: Field name to extract (e.g., 'slope', 'intercept', 'center').
        :return: NumPy array of the column values.
        :raises KeyError: If field name does not exist.
        """
        if not name in self._DTYPE.fields:
            raise KeyError(f"Field {name} not found in dtype")
        dtype_base = self._DTYPE.fields[name][0].base
        return np.array([line[name] for line in self._lines], dtype=dtype_base)

    @property
    def id(self):
        """
        Get an array of all line IDs.

        :return: Array of string IDs.
        """
        return self._get_column(self._ID)

    @property
    def slopes(self):
        """
        Get an array of all line slopes.

        :return: Array of floats.
        """
        return self._get_column(self._SLOPE)

    @property
    def intercepts(self):
        """
        Get an array of all line intercepts.

        :return: Array of floats.
        """
        return self._get_column(self._INTERCEPT)

    @property
    def centers(self):
        """
        Get an array of all line centers as (x, y) tuples.

        :return: Array of 2-element float tuples.
        """
        return self._get_column(self._CENTER)

    @property
    def lines(self):
        """
        Get the internal list of structured line arrays.

        :return: List of numpy structured arrays.
        """
        return self._lines

    @property
    def mean_slope(self):
        """
        Compute mean slope across all stored lines.

        :return: Mean slope as float, or 0.0 if empty.
        """
        return np.mean(self.slopes) if len(self._lines) > 0 else 0.0

    def line(self, id):
        """
        Retrieve a line by its unique ID.

        :param id: String ID of the line.
        :return: Structured numpy array (without the ID field).
        :raises KeyError: If no line with the given ID exists.
        """
        for line in self._lines:
            if line[self._ID] == id:
                dtype_no_id = np.dtype(self._DTYPE.descr[1:])
                values = tuple(line[field] for field in dtype_no_id.names)
                return np.array(values, dtype=dtype_no_id)
        raise KeyError(f"Line with id {id} not found.")


if __name__ == '__main__':
    import sys
    sys.exit(0)
