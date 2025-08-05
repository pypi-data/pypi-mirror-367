"""
Module that contains functions to convert some basic types into Bool1D types

The easier example is from string:
* "{}" represents a empty set, so returns the Empty instance
* "(-inf, +inf)" represents the entire real line, returns Whole instance
"""

from numbers import Real
from typing import Any, Dict, List, Set, Tuple

from .base import Empty, Future, SubSetR1, Whole
from .error import NotExpectedError
from .numbs import NEGINF, POSINF, To
from .singles import Interval, SingleValue, bigger, lower


# pylint: disable=too-many-return-statements
def from_any(obj: Any) -> SubSetR1:
    """
    Converts an arbitrary object into a SubSetR1 instance.
    If it's already a SubSetR1 instance, returns the object

    Example
    -------
    >>> Future.convert("{}")
    {}
    >>> Future.convert("(-inf, +inf)")
    (-inf, +inf)
    """
    if isinstance(obj, SubSetR1):
        return obj
    if isinstance(obj, Real):
        number = To.finite(obj)
        return SingleValue(number)
    if isinstance(obj, str):
        return from_str(obj)
    if isinstance(obj, dict):
        return from_dict(obj)
    if isinstance(obj, set):
        return from_set(obj)
    if isinstance(obj, tuple):
        return from_tuple(obj)
    if isinstance(obj, list):
        return from_list(obj)
    raise NotExpectedError(f"Received object {type(obj)} = {obj}")


def from_str(string: str) -> SubSetR1:
    """
    Converts a string into a SubSetR1 instance.

    Example
    -------
    >>> from_str("{}")  # Empty
    {}
    >>> from_str("(-inf, +inf)")  # Whole
    (-inf, +inf)
    >>> from_str("{10}")  # SingleValue
    {10}
    >>> from_str("[-10, 0] U {5, 10}")  # Disjoint
    [-10, 0] U {5, 10}
    """
    string = string.strip()
    if "U" in string:
        return Future.unite(*map(from_str, string.split("U")))
    if string[0] == "{" and string[-1] == "}":
        result = Empty()
        for substr in string[1:-1].split(","):
            if not substr:  # Empty string
                continue
            finite = To.finite(substr)
            result |= SingleValue(finite)
        return result
    if string[0] in "([" and string[-1] in ")]":
        stastr, endstr = string[1:-1].split(",")
        start = To.real(stastr)
        end = To.real(endstr)
        if start == NEGINF and end == POSINF:
            return Whole()
        left = string[0] == "["
        right = string[-1] == "]"
        return Interval(start, end, left, right)
    raise ValueError(f"Cannot parse '{string}' into a SubSetR1 instance")


def from_dict(dic: Dict) -> SubSetR1:
    """
    Converts a dictonary into a SubSetR1 instance

    Only accepts an empty dict, since it's the standard type of {}:

    Example
    -------
    >>> variable = {}
    >>> type(variable)
    <class 'dict'>
    >>> subset = from_dict(variable)
    >>> subset
    {}
    >>> type(subset)
    <class 'Empty'>
    """
    if not isinstance(dic, dict):
        raise TypeError
    result = Empty()
    if len(dic) != 0:
        raise NotExpectedError
    return result


def from_set(items: Set[object]) -> SubSetR1:
    """
    Converts a set into a SubSetR1 instance

    Example
    -------
    >>> variable = {-10, 5}
    >>> type(variable)
    <class 'set'>
    >>> subset = from_set(variable)
    >>> subset
    {-10, 5}
    >>> type(subset)
    <class 'Disjoint'>
    """
    if not isinstance(items, set):
        raise TypeError
    result = Empty()
    for item in items:
        result |= To.finite(item)
    return result


def from_tuple(pair: Tuple[object]) -> SubSetR1:
    """
    Converts a tuple of two values into a SubSetR1 instance

    It's the standard open interval, or the Whole

    Example
    -------
    >>> variable = (-10, 10)
    >>> type(variable)
    <class 'tuple'>
    >>> subset = from_tuple(variable)
    >>> subset
    (-10, 10)
    >>> type(subset)
    <class 'Interval'>
    >>> variable = ("-inf", "inf")
    >>> subset = from_tuple(variable)
    >>> type(subset)
    <class 'Whole'>
    """
    if not isinstance(pair, tuple):
        raise TypeError
    if len(pair) != 2:
        raise ValueError
    sta = To.real(pair[0])
    end = To.real(pair[1])
    if sta == NEGINF and end == POSINF:
        return Whole()
    if sta == NEGINF:
        return lower(end, False)
    if end == POSINF:
        return bigger(sta, False)
    return Interval(sta, end, False, False)


def from_list(pair: List[object]) -> SubSetR1:
    """
    Converts a list of two values into a SubSetR1 instance

    It's the standard closed interval, or the Whole

    Example
    -------
    >>> variable = [-10, 10]
    >>> type(variable)
    <class 'list'>
    >>> subset = from_list(variable)
    >>> subset
    [-10, 10]
    >>> type(subset)
    <class 'Interval'>
    >>> variable = ["-inf", "inf"]
    >>> subset = from_list(variable)
    >>> subset
    (-inf, +inf)
    >>> type(subset)
    <class 'Whole'>
    """
    if not isinstance(pair, list):
        raise TypeError
    if len(pair) != 2:
        raise ValueError
    sta = To.real(pair[0])
    end = To.real(pair[1])
    if sta == NEGINF and end == POSINF:
        return Whole()
    if sta == NEGINF:
        return lower(end, True)
    if end == POSINF:
        return bigger(sta, True)
    return Interval(sta, end, True, True)
