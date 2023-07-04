import logging
import os
import time
from datetime import datetime, timedelta
from json import dumps
from multiprocessing import Pool, cpu_count
from pathlib import Path
from threading import Thread
from typing import Any, Callable, Optional

import jmespath
import requests
from api.spokendata import SpokenDataApi
from database.models import Airport, Flight
from database.session import Session
from flask_app import MP3_PATH, PATH_TO_APP, TRANSCRIPT_PATH
from profiling_decorators import time_profile

logger = logging.getLogger(__name__)

TIME_RANGE = 300  # in seconds


def find_in_json_object(
    json_obj: dict | list, *expression_paths: str
) -> list[tuple[int | str, ...]]:
    """Finds all occurrences in an object of type json.

    Args:
        json_obj (dict | list): JSON-like object
        *expression_paths (str): regex for the desired path

    Returns:
        list[tuple[int | str, ...]]: List of all occurrences
    """
    # construct expression
    expression = f"[{', '.join(expression_paths)}]"
    if isinstance(json_obj, list):
        expression = f"[*].{expression}"

    result: list[list[Any]] = jmespath.search(expression, json_obj)

    # return only values that are valid
    return [tuple(values) for values in result if None not in values]


def download_mp3(mp3_url: str, download_path: Path) -> None:
    downloaded_mp3 = requests.get(mp3_url)

    with open(download_path, "wb") as file:
        file.write(downloaded_mp3.content)


class SpokenDataThread(Thread):
    def __init__(self) -> None:
        Thread.__init__(self)
        self.api = SpokenDataApi()
        self.__session: Session

    # in order record, mp3, transcript
    def get_all_valid_jobs(self) -> list[tuple[str, str, str, str]]:
        """Get all valid jobs.

        Returns:
            list[tuple[str, str, str, str]]: values for the keys "titile", "recorded_at", "mp3", "transcript"
        """
        jobs = self.api.get_jobs(limit=200, offset=30)

        return find_in_json_object(  # type: ignore[return-value]
            jobs, "title", "recorded_at", "url.mp3", "url.transcript"
        )

    def get_matched_callsigns(
        self, transcript_url: str
    ) -> Optional[tuple[dict[str, Any], tuple[str, ...]]]:
        # download transcript
        try:
            response = requests.get(transcript_url)
        except requests.exceptions.MissingSchema:
            return None

        if response.status_code != 200:
            return None

        # transcript in json-like format in python
        transcript = response.json()

        # find only callsigns that are detected in the transcript
        matched_callsigns = tuple(
            label.ljust(8)  # type: ignore[union-attr]
            for label in find_in_json_object(transcript, "speaker_tags[*].label")[0]
            if not any(value in label for value in ("ATCO", "UNK-"))  # type: ignore[operator]
        )

        return transcript, matched_callsigns

    def get_flights_in_range(
        self, matched_callsigns: tuple[str, ...], recorded_timestamp: int, range: int
    ) -> list[Flight]:
        # search for the flights within this specific interval
        if flights := self.__session.get_flights_in_interval(
            matched_callsigns, recorded_timestamp - range, recorded_timestamp + range
        ):
            return flights
        return []

    def new_timestamp_record(
        self,
        flights: list[Flight],
        airport: Optional[Airport],
        recorded_timestamp: int,
        json_path: str,
        mp3_path: str,
    ) -> bool:
        save_data = False
        # for each flight find closes timestamp
        # and assign mp3, transcript url
        for flight in flights:
            # find closes timestamp
            timestamp = min(
                flight.timestamps,
                key=lambda timestamp: abs(timestamp.timestamp - recorded_timestamp),
            )

            # assign mp3, transcript to the timestamp
            if not any(mp3_path == timestamp.mp3 for timestamp in flight.timestamps):
                # print(flight.callsign, mp3_path)
                timestamp.mp3 = mp3_path
                timestamp.transcript = json_path
                save_data = True
            flight.has_record = True
            if airport and flight not in airport.detected_flights:
                # print(airport.iata_code)
                airport.detected_flights.append(flight)

        return save_data

    @time_profile
    def update_spoken_data(self) -> None:
        # 1. get desired data from jobs
        data = self.get_all_valid_jobs()
        mp3_download_data: list[tuple[str, Path]] = []

        # lambda function for converting title of the recording to the code of the airport
        to_code: Callable[[str], str] = lambda x: x.split(" ")[0].lower()

        # get all airport codes from the retrieved data
        codes: set[str] = {to_code(title) for title, *_ in data}
        # get specific airports from the database
        # TODO: can be done in 1 query
        airports: dict[str, Optional[Airport]] = {
            code: self.__session.get_airport(code) for code in codes
        }

        for title, recorded_time, mp3_url, transcript_url in data:
            airport = airports[to_code(title)]  # desired airport

            # convert into timestamp
            recorded_timestamp = SpokenDataApi.get_job_timestamp(recorded_time)

            # file paths to the static folder of the application
            json_full_path: Path = TRANSCRIPT_PATH / f"{recorded_timestamp}.json"
            mp3_full_path: Path = MP3_PATH / f"{recorded_timestamp}.mp3"

            # relative paths to be saved to the database
            # TODO: change it to just to the file name, no need to save "static/" also
            relative_json_path: str = str(json_full_path.relative_to(PATH_TO_APP))
            relative_mp3_path: str = str(mp3_full_path.relative_to(PATH_TO_APP))

            # 2. get only callsigns that were detected within transcript
            if res := self.get_matched_callsigns(transcript_url):
                transcript_data, matched_callsigns = res
            else:  # invalid request
                continue

            # 3. get flights that are matching callsigns
            # and have timestamp data within recorded time
            flights = self.get_flights_in_range(
                matched_callsigns, recorded_timestamp, TIME_RANGE
            )

            # 4. for each flight find nearest timestamp and assign mp3, transcipt
            has_changed = self.new_timestamp_record(
                flights,
                airport,
                recorded_timestamp,
                relative_json_path,
                relative_mp3_path,
            )

            # if there was change download record
            if has_changed:
                with open(json_full_path, "w") as file:
                    file.write(dumps(transcript_data, indent=4))

                mp3_download_data.append((mp3_url, mp3_full_path))

        self.__session.update_models()

        # NOTE: just to make downloading faster.
        # TODO: change this implementation
        with Pool(processes=cpu_count()) as p:
            p.starmap(download_mp3, mp3_download_data)

    @time_profile
    def remove_old_data(self) -> None:
        # get older flights that should be removed from database
        flights: set[Flight] = set()
        flights.update(self.__session.old_flights(datetime.now() + timedelta(days=-2)))
        flights.update(
            self.__session.ended_no_record(datetime.now() + timedelta(hours=-2))
        )

        to_remove: list[Path] = []

        # find all corresponding files
        for flight in flights:
            for timestamp in flight.timestamps:
                if timestamp.mp3:
                    to_remove.append(PATH_TO_APP / timestamp.mp3)
                if timestamp.transcript:
                    to_remove.append(PATH_TO_APP / timestamp.transcript)

        # remove those files
        for path in to_remove:
            if path.exists():
                os.remove(path)

        # remove flights from DB
        # print("Remove from DB:", len(flights))
        self.__session.remove_flights(list(flights))

    def run(self):
        while True:
            try:
                self.__session = Session()
                self.update_spoken_data()
                self.remove_old_data()
            except Exception as exc:
                logger.exception(exc)
            finally:
                self.__session.close()
                time.sleep(15 * 60)
