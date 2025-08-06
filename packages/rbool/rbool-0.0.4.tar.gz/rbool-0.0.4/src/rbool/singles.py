"""
Defines some basic types of boolean 1D
"""

from __future__ import annotations

from numbers import Real
from typing import Iterable, List, Set, Tuple, Union

from .base import Empty, Future, SubSetR1
from .error import NotExpectedError
from .numbs import NEGINF, POSINF, Is, To


def lower(number: Real, closed: bool = True) -> Interval:
    """
    Gives the interval such points are lower than given number

    Parameters
    ----------
    number : Real
        The finite number
    closed : bool, default = True
        If the interval is closed on the right end

    Return
    ------
    Interval
        The Interval such is lower than the given `number`

    Example
    -------
    >>> lower(0)
    (-inf, 0]
    >>> lower(0, False)
    (-inf, 0)
    >>> lower(10, True)
    (-inf, 10]
    """
    return Interval(NEGINF, To.finite(number), False, closed)


def bigger(finite: Real, closed: bool = True) -> Interval:
    """
    Gives the interval such points are bigger than given number

    Parameters
    ----------
    number : Real
        The finite number
    closed : bool, default = True
        If the interval is closed on the left end

    Return
    ------
    Interval
        The Interval such is bigger than the given `number`

    Example
    -------
    >>> bigger(0)
    [0, +inf)
    >>> bigger(0, False)
    (0, +inf)
    >>> bigger(10, True)
    [10, +inf)
    """
    return Interval(finite, POSINF, closed, False)


class SingleValue(SubSetR1):
    """
    SingleValue stores only one value, being a subset of the real line

    Only finite values are acceptable
    """

    def __init__(self, value: Real):
        self.__internal = To.finite(value)

    @property
    def internal(self) -> Real:
        """
        Gives the internal real value of the SingleValue

        :getter: Returns the internal value of the SubSetR1
        :type: Real
        """
        return self.__internal

    def __str__(self) -> str:
        return "{" + str(self.__internal) + "}"

    def __repr__(self):
        return f"SingleValue({self.__internal})"

    def __contains__(self, other):
        if Is.infinity(other):
            return False
        other = Future.convert(other)
        return isinstance(other, Empty) or self == other

    def __eq__(self, other):
        other = Future.convert(other)
        return (
            isinstance(other, self.__class__)
            and self.internal == other.internal
        )

    def __invert__(self):
        return Disjoint(
            [
                lower(self.internal, False),
                bigger(self.internal, False),
            ]
        )

    def __and__(self, other: SubSetR1):
        other = Future.convert(other)
        return self if other.__contains__(self) else Empty()

    def __hash__(self):
        return hash(self.internal)


class Interval(SubSetR1):
    """
    Interval stores a continuous set of points on R1


    """

    def __init__(
        self, start: Real, end: Real, left: bool = True, right: bool = True
    ):
        start = To.real(start)
        end = To.real(end)
        if end <= start:
            raise ValueError(
                "Received interval [{start}, {end}], but {end} <= {start}"
            )
        if Is.infinity(start) and Is.infinity(end):
            raise ValueError("Received interval (-inf, +inf), use Whole")
        if start == NEGINF:
            left = False
        if end == POSINF:
            right = False
        self.__start = start
        self.__end = end
        self.__left = left
        self.__right = right

    # pylint: disable=too-many-return-statements
    def __contains__(self, other):
        if Is.infinity(other):
            return other in (self[0], self[1])
        other = Future.convert(other)
        if isinstance(other, SingleValue):
            other = other.internal
            if other < self[0] or self[1] < other:
                return False
            if self[0] < other < self[1]:
                return True
            return self.closed_left if self[0] == other else self.closed_right
        if isinstance(other, Interval):
            if other[0] < self[0] or self[1] < other[1]:
                return False
            if self[0] < other[0] and other[1] < self[1]:
                return True
            if self[0] == other[0] and (self.closed_left ^ other.closed_left):
                return False
            if self[1] == other[1] and (
                self.closed_right ^ other.closed_right
            ):
                return False
            return True
        if isinstance(other, Disjoint):
            return all(map(self.__contains__, other))
        return isinstance(other, Empty)

    def __invert__(self):
        if self[0] == NEGINF:
            return bigger(self[1], not self.closed_right)
        if self[1] == POSINF:
            return lower(self[0], not self.closed_left)
        return Disjoint(
            [
                lower(self[0], not self.closed_left),
                bigger(self[1], not self.closed_right),
            ]
        )

    def __getitem__(self, index):
        return self.__end if index else self.__start

    def __eq__(self, other):
        other = Future.convert(other)
        return (
            isinstance(other, Interval)
            and self[0] == other[0]
            and self[1] == other[1]
            and self.closed_left == other.closed_left
            and self.closed_right == other.closed_right
        )

    def __str__(self):
        msg = "[" if self.closed_left else "("
        msg += str(self[0]) + ", " + str(self[1])
        msg += "]" if self.closed_right else ")"
        return msg

    @property
    def closed_left(self) -> bool:
        """
        Tells if the interval is closed on the left side

        :getter: Returns a boolean that tells if interval is bounded on bot
        :type: bool
        """
        return self.__left

    @property
    def closed_right(self) -> bool:
        """
        Tells if the interval is closed on the right side

        :getter: Returns a boolean that tells if interval is bounded on top
        :type: bool
        """
        return self.__right

    def __hash__(self):
        return hash((self[0], self[1]))


class Disjoint(SubSetR1):
    """
    Stores the union of SingleValue and Interval which are not connected

    The direct constructor should not be used.
    This object should be constructed by the standard boolean operations
    of the some SingleValue and Interval
    """

    def __init__(self, items: Iterable[Union[SingleValue, Interval]]):
        items = tuple(items)
        if len(items) < 2:
            raise ValueError("Less than 2 items!")

        knots: Set[Real] = set()
        singles: List[SingleValue] = []
        intervs: List[Interval] = []
        for item in items:
            if isinstance(item, SingleValue):
                singles.append(item)
                knots.add(item.internal)
            elif isinstance(item, Interval):
                intervs.append(item)
                if isinstance(item[0], Real):
                    knots.add(item[0])
                if isinstance(item[1], Real):
                    knots.add(item[1])
            else:
                raise TypeError("Received wrong type!")

        weights = tuple(single.internal for single in singles)
        self.__singles = tuple(
            s for _, s in sorted(zip(weights, singles), key=lambda x: x[0])
        )
        weights = tuple((interv[0] + interv[1]) / 2 for interv in intervs)
        self.__intervs = tuple(
            i for _, i in sorted(zip(weights, intervs), key=lambda x: x[0])
        )

    @property
    def singles(self) -> Tuple[SingleValue, ...]:
        """
        Gives all the isolated nodes that are inside the Disjoint

        :getter: Returns all the isolated points
        :type: Tuple[SingleValue, ...]
        """
        return self.__singles

    @property
    def intervals(self) -> Tuple[Interval, ...]:
        """
        Gives all the non-connected intervals that are inside the Disjoint

        :getter: Returns all the non-connected intervals
        :type: Tuple[SingleValue, ...]
        """
        return self.__intervs

    def __iter__(self):
        yield from self.__singles
        yield from self.__intervs

    def __contains__(self, other):
        if Is.infinity(other):
            return any(other in sub for sub in self)
        other = Future.convert(other)
        if isinstance(other, Disjoint):
            return all(sub in self for sub in other)
        return any(other in sub for sub in self)

    # pylint: disable=too-many-branches, too-many-statements
    def __str__(self) -> str:
        ssize = len(self.singles)
        isize = len(self.intervals)
        if ssize == 0:
            return " U ".join(map(str, self.intervals))
        if isize == 0:
            return (
                "{"
                + ", ".join(str(single.internal) for single in self.singles)
                + "}"
            )

        msgs: List[str] = []
        first: bool = True
        flag: bool = False
        i, s = 0, 0
        if self.intervals[0][0] == NEGINF:
            msgs.append(str(self.intervals[0]))
            i += 1
            first = False
        while i < isize and s < ssize:
            if self.singles[s].internal < self.intervals[i][0]:
                if not flag:
                    if not first:
                        msgs.append(" U ")
                    msgs.append("{")
                    first = False
                    flag = True
                else:
                    msgs.append(", ")
                msgs.append(str(self.singles[s].internal))
                s += 1
            else:
                if flag:
                    msgs.append("}")
                    flag = False
                if not first:
                    msgs.append(" U ")
                first = False
                msgs.append(str(self.intervals[i]))
                i += 1
        if s < ssize:
            if not flag:
                if not first:
                    msgs.append(" U ")
                msgs.append("{")
                first = False
                flag = True
            else:
                # msgs.append(", ")
                raise NotExpectedError("Not expected get here")
            msgs.append(str(self.singles[s].internal))
            s += 1
            while s < ssize:
                msgs.append(", ")
                msgs.append(str(self.singles[s].internal))
                s += 1
        if flag:
            msgs.append("}")
        while i < isize:
            msgs.append(" U ")
            msgs.append(str(self.intervals[i]))
            i += 1
        return "".join(msgs)

    def __eq__(self, other):
        other = Future.convert(other)
        if not isinstance(other, Disjoint):
            return False
        if len(self.singles) != len(other.singles) or len(
            self.intervals
        ) != len(other.intervals):
            return False
        return all(subs == subo for subs, subo in zip(self, other))

    def __hash__(self):
        return hash(tuple(map(hash, self)))
