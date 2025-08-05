"""
Contains some functions to compute the limits of the given subsets
"""

from numbers import Real
from typing import Union

from .base import Empty, Future, SubSetR1, Whole
from .error import NotExpectedError
from .numbs import NEGINF, POSINF, Is
from .singles import Disjoint, Interval, SingleValue


def infimum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the infimum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the infimum

    Return
    ------
    Real | None
        The infimum value, or None if receives Empty

    Example
    -------
    >>> infimum("{}")  # Empty
    None
    >>> infimum("(-inf, +inf)")  # Whole
    -inf
    >>> infimum("{-10}")  # SingleValue
    -10
    >>> infimum("[-10, 10]")  # Interval
    -10
    >>> infimum("(-10, 10)")  # Interval
    -10
    >>> infimum("{0, 10, 20}")  # Disjoint
    0
    """
    subset = Future.convert(subset)
    if isinstance(subset, Empty):
        return None
    if isinstance(subset, Whole):
        return NEGINF
    if isinstance(subset, SingleValue):
        return subset.internal
    if isinstance(subset, Interval):
        return subset[0]
    if isinstance(subset, Disjoint):
        return min(map(infimum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def minimum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the minimum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the minimum

    Return
    ------
    Real | None
        The minimum value or None

    Example
    -------
    >>> minimum("{}")  # Empty
    None
    >>> minimum("(-inf, +inf)")  # Whole
    None
    >>> minimum("{-10}")  # SingleValue
    -10
    >>> minimum("[-10, 10]")  # Interval
    -10
    >>> minimum("(-10, 10)")  # Interval
    None
    >>> minimum("{0, 10, 20}")  # Disjoint
    0
    """
    subset = Future.convert(subset)
    if isinstance(subset, (Empty, Whole)):
        return None
    if isinstance(subset, SingleValue):
        return subset.internal
    if isinstance(subset, Interval):
        return (
            subset[0]
            if (Is.finite(subset[0]) and subset.closed_left)
            else None
        )
    if isinstance(subset, Disjoint):
        infval = POSINF
        global_minval = POSINF
        for sub in subset:
            infval = min(infval, infimum(sub))
            minval = minimum(sub)
            if minval is not None:
                global_minval = min(global_minval, minval)
        return infval if (global_minval == infval) else None
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def maximum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the maximum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the maximum

    Return
    ------
    Real | None
        The maximum value of the subset

    Example
    -------
    >>> maximum("{}")  # Empty
    None
    >>> maximum("(-inf, +inf)")  # Whole
    None
    >>> maximum("{-10}")  # SingleValue
    -10
    >>> maximum("[-10, 10]")  # Interval
    10
    >>> maximum("(-10, 10)")  # Interval
    None
    >>> maximum("{0, 10, 20}")  # Disjoint
    20
    """
    subset = Future.convert(subset)
    if isinstance(subset, (Empty, Whole)):
        return None
    if isinstance(subset, SingleValue):
        return subset.internal
    if isinstance(subset, Interval):
        return (
            subset[1]
            if (Is.finite(subset[1]) and subset.closed_right)
            else None
        )
    if isinstance(subset, Disjoint):
        supval = NEGINF
        global_maxval = NEGINF
        for sub in subset:
            supval = max(supval, supremum(sub))
            maxval = maximum(sub)
            if maxval is not None:
                global_maxval = max(global_maxval, maxval)
        return maxval if (global_maxval == supval) else None
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def supremum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the supremum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the supremum

    Return
    ------
    Real | None
        The supremum value, or None if receives Empty

    Example
    -------
    >>> supremum("{}")  # Empty
    None
    >>> supremum("(-inf, +inf)")  # Whole
    +inf
    >>> supremum("{-10}")  # SingleValue
    -10
    >>> supremum("[-10, 10]")  # Interval
    10
    >>> supremum("(-10, 10)")  # Interval
    10
    >>> supremum("{0, 10, 20}")  # Disjoint
    20
    """
    subset = Future.convert(subset)
    if isinstance(subset, Empty):
        return None
    if isinstance(subset, Whole):
        return POSINF
    if isinstance(subset, SingleValue):
        return subset.internal
    if isinstance(subset, Interval):
        return subset[1]
    if isinstance(subset, Disjoint):
        return max(map(supremum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")
