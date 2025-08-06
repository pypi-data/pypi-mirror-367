"""
Defines the methods used to do the usual transformations,
like translating, scaling and rotating the SubSetR2 instances on the plane
"""

from numbers import Real

from .base import Empty, Future, SubSetR1, Whole
from .error import NotExpectedError
from .numbs import To
from .singles import Disjoint, Interval, SingleValue


def move(subset: SubSetR1, amount: Real) -> SubSetR1:
    """
    Translates the subset on the the real line by given amount

    Parameters
    ----------
    subset: SubSetR1
        The subset to be displaced
    amount: Real
        The quantity to be displaced

    Return
    ------
    SubSetR1
        The translated subset, of the same type
    """
    subset = Future.convert(subset)
    amount = To.finite(amount)
    if isinstance(subset, (Empty, Whole)):
        return subset
    if isinstance(subset, SingleValue):
        return SingleValue(subset.internal + amount)
    if isinstance(subset, Interval):
        newlef = subset[0] + amount
        newrig = subset[1] + amount
        return Interval(
            newlef, newrig, subset.closed_left, subset.closed_right
        )
    if isinstance(subset, Disjoint):
        amount = To.finite(amount)
        newiterable = (move(sub, amount) for sub in subset)
        return Disjoint(newiterable)
    raise NotExpectedError(f"Missing typo? {type(subset)}")


def scale(subset: SubSetR1, amount: Real) -> SubSetR1:
    """
    Scales the subset on the real line by given amount.

    Parameters
    ----------
    subset: SubSetR1
        The subset to be scaled
    amount: Real
        The amount to be scaled

    Return
    ------
    SubSetR1
        The scaled subset, of the same type

    Example
    -------
    >>> subset = [-2, 3]
    >>> scale(subset, 3)
    [-6, 9]
    """
    subset = Future.convert(subset)
    amount = To.finite(amount)
    if amount == 0:
        raise ValueError
    if isinstance(subset, (Empty, Whole)):
        return subset
    if isinstance(subset, SingleValue):
        return SingleValue(subset.internal * amount)
    if isinstance(subset, Interval):
        newlef = subset[0] * amount
        newrig = subset[1] * amount
        clolef = subset.closed_left
        clorig = subset.closed_right
        if amount < 0:
            newlef, newrig = newrig, newlef
            clolef, clorig = clorig, clolef
        return Interval(newlef, newrig, clolef, clorig)
    if isinstance(subset, Disjoint):
        amount = To.finite(amount)
        newiterable = (scale(sub, amount) for sub in subset)
        return Disjoint(newiterable)
    raise NotExpectedError(f"Missing typo? {type(subset)}")
