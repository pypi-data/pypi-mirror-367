"""
Init file that includes the most used classes and functions of the module
"""

from .base import Empty, Future, SubSetR1, Whole
from .bool1d import contains, extract_knots, intersect, invert, unite
from .converter import from_any
from .limits import infimum, maximum, minimum, supremum
from .singles import Disjoint, Interval, SingleValue, bigger, lower
from .transform import move, scale

Future.convert = from_any
Future.unite = unite
Future.intersect = intersect
Future.invert = invert
Future.contains = contains
Future.scale = scale
Future.move = move

__version__ = "0.0.4"

if __name__ == "__main__":
    pass
