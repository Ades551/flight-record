import threading
import time
from functools import wraps


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


BASE = 5
custom_round = lambda x: BASE * round(x / BASE)


def color_message(duration, message) -> None:
    duration = round(duration, 2)
    end = f"{Colors.BOLD}{duration}{Colors.END} seconds"
    start = "Execution time of the function"
    thred_info = f"{Colors.OKBLUE}{Colors.UNDERLINE}{Colors.BOLD}{threading.current_thread().name}{Colors.END}"

    match custom_round(duration):
        case 0:
            print(f"{thred_info} {start} {Colors.OKGREEN}{message} {end}")
        case 5:
            print(f"{thred_info} {start} {Colors.WARNING}{message} {end}")
        case _:
            print(f"{thred_info} {start} {Colors.FAIL}{message} {end}")


def time_profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        color_message(time.time() - start, func.__name__)
        return res

    return wrapper


def time_profile_sum(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        decorator.time += time.time() - start
        return res

    decorator.time = 0

    return decorator


def log_duration(func):
    color_message(func.time, func.__name__)
    func.__dict__["time"] = 0
