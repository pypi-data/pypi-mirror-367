
import numpy as np
from .. import Devutils as dev
from .. import Numputils as nput

__all__ = [
    "canonicalize_internal",
    "is_coordinate_list_like",
    "is_valid_coordinate",
]

def canonicalize_internal(coord):
    dupes = len(np.unique(coord)) < len(coord)
    if dupes: return None
    if len(coord) == 2:
        i, j = coord
        if i > j:
            coord = (j, i)
    elif len(coord) == 3:
        i, j, k = coord
        if i > k:
            coord = (k, j, i)
    elif len(coord) == 4:
        i, j, k, l = coord
        if i > l:
            coord = (l, k, j, i)
    elif coord[0] > coord[-1]:
        coord = tuple(reversed(coord))
    return coord

def is_valid_coordinate(coord):
    return (
        len(coord) > 1 and len(coord) < 5
        and all(nput.is_int(c) for c in coord)
    )

def is_coordinate_list_like(clist):
    return dev.is_list_like(clist) and all(
        is_valid_coordinate(c) for c in clist
    )
