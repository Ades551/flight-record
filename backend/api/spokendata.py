from datetime import datetime, timezone
from typing import Callable

import requests
from api import load_credentials


class SpokenDataApi:
    record_date_format = "%Y-%m-%dT%H:%M:%S"

    def __init__(self) -> None:
        self.api_url = "https://engine.spokendata.com/api/v2"

        if key := load_credentials("spokendata", values=["API-key"]):
            self._api_key = key[0]
        else:
            raise Exception("Missing credentials for SpokenData API.")

    @staticmethod
    def __check_params(valid_params: list):
        def decorator(func: Callable[..., dict]):
            def wrapper(self, **kwargs):
                for key in kwargs.keys():
                    if key not in valid_params:
                        raise Exception(f"Invalid parameter {key}!")
                return func(self, **kwargs)

            return wrapper

        return decorator

    def __api_call(self, api_path: str, params: dict[str, str] = {}):
        response = requests.get(
            f"{self.api_url}/{api_path}",
            params=params,
            headers={"X-API-Key": self._api_key},
            timeout=15.00,
        )
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def get_job_timestamp(time_value: str) -> int:
        time_value = time_value.split(".")[0][0:19]
        return int(
            datetime.strptime(time_value, SpokenDataApi.record_date_format)
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

    @__check_params(["limit", "offset"])
    def get_jobs(self, **kwargs):
        return self.__api_call("jobs", kwargs)
