from ctypes import CDLL, c_double
from pathlib import Path

path = Path("haversine/distance.so")

c_haversine = CDLL(str(path.absolute()))


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    c_haversine.haversine.restype = c_double
    return c_haversine.haversine(
        c_double(lat1), c_double(lon1), c_double(lat2), c_double(lon2)
    )
