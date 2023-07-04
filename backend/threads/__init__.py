import logging
from functools import wraps
from threading import Lock
from typing import Any, Callable, Optional

from clustering import ZOOM_LEVELS, Cluster

logging.basicConfig(
    level=logging.ERROR,
    filename="/tmp/flight-record.log",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

lock = Lock()

flights: dict[int, list[Cluster]] = {i: [] for i in ZOOM_LEVELS} | {-1: []}  # type: ignore[assignment]


def lock_flights(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        lock.acquire()
        result = func(*args, **kwargs)
        lock.release()
        return result

    return decorator


def to_valid_callsign(callsign: Optional[str]) -> str:
    if callsign is not None and len(callsign.strip()) >= 6:
        return callsign.ljust(8)
    return ""
