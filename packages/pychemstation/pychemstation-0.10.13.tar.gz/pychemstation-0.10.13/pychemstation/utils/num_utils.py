from typing import Tuple

import numpy as np


def find_nearest_value_index(array, value) -> Tuple[float, int]:
    """Returns closest value and its index in a given array.

    :param array: An array to search in.
    :type array: np.array(float)
    :param value: Target value.
    :type value: float

    :return: Nearest value in array and its index.
    """

    index_ = np.argmin(np.abs(array - value))
    return array[index_], index_


def interpolate_to_index(array, ids, precision: int = 100) -> np.ndarray:
    """Find value in between arrays elements.

    Constructs linspace of size "precision" between index+1 and index to
    find approximate value for array[index], where index is float number.
    Used for 2D data, where default scipy analysis occurs along one axis only,
    e.g. signal.peak_width.

    Rough equivalent of array[index], where index is float number.

    :param array: Target array.
    :type array: np.array(float)
    :param ids: An array with "intermediate" indexes to interpolate to.
    :type ids: np.array[float]
    :param precision: Desired presion.

    :return: New array with interpolated values according to provided indexes "ids".

    Example:
        >>> interpolate_to_index(np.array([1.5]), np.array([1, 2, 3], 100))
            ... array([2.50505051])
    """

    # breaking ids into fractional and integral parts
    prec, ids = np.modf(ids)

    # rounding and switching type to int
    prec = np.around(prec * precision).astype("int32")
    ids = ids.astype("int32")

    # linear interpolation for each data point
    # as (n x m) matrix where n is precision and m is number of indexes
    space = np.linspace(array[ids], array[ids + 1], precision)

    # due to rounding error the index may become 100 in (100, ) array
    # as a consequence raising IndexError when such array is indexed
    # therefore index 100 will become the last (-1)
    prec[prec == 100] = -1

    # precise slicing
    true_values = np.array(
        [space[:, index[0]][value] for index, value in np.ndenumerate(prec)]
    )

    return true_values
