import logging
import time
from datetime import datetime
from threading import Thread
from typing import Any, Optional

from api.opensky import OpenSkyApi
from clustering import get_clusters
from database.models import Aircraft, Flight, LastContactInfo, Timestamp
from database.session import Session
from haversine import haversine
from profiling_decorators import log_duration, time_profile, time_profile_sum
from threads import flights, lock, to_valid_callsign

logger = logging.getLogger(__name__)


P_END_INACTIVE_MAX = 2 * 60  # 2min
MAXIMAL_INACTIVE = 5 * 3600  # 5h
MINIMAL_VELOCITY = 100
MINIMAL_VERTICAL_RATE = 0
MAXIMAL_AIRPLANE_SPEED = 950  # km/h


def time_diff(timestamp: int) -> int:
    return int(datetime.now().strftime("%s")) - timestamp


def is_valid_timestamp(prev_time: int, time_now: int, distance: float) -> bool:
    speed = distance / (abs(time_now - prev_time) / 3600)
    if speed > MAXIMAL_AIRPLANE_SPEED:
        if distance >= 3000:
            return True
        return False

    return True


class FlightProps:
    def __init__(self, flight: Flight, active: bool) -> None:
        self.flight = flight
        self.active = active


class Flights:
    def __init__(self, flights: Optional[list[Flight]]) -> None:
        self.flights: dict[str, FlightProps] = {}
        if flights:
            self.flights = {
                flight.aircraft_icao24: FlightProps(flight, False) for flight in flights
            }

    def exists(self, icao24: str) -> bool:
        """Check flight existence."""
        return icao24 in self.flights.keys()

    def add_flight(self, flight: Flight) -> None:
        """Add new flight."""
        self.flights[flight.aircraft_icao24] = FlightProps(flight, False)

    def get_flight(self, icao24: str) -> Optional[Flight]:
        """Get flight."""
        if self.exists(icao24):
            return self.flights[icao24].flight

        return None

    def set_active(self, icao24: str, value: bool) -> None:
        """Set flight active state."""
        if self.exists(icao24):
            self.flights[icao24].active = value


class OpenSkyThread(Thread):
    def __init__(self) -> None:
        Thread.__init__(self)
        self.api = OpenSkyApi()

        # flights considered as possibly ended
        self.possibly_ended_flights: set[str] = set()

        # models to upload to database after every iteration
        self.add_aircrafts: list[Aircraft] = []
        self.add_flights: list[Flight] = []
        self.add_timestamps: list[Timestamp] = []

        self.__flights: Flights  # flight management
        self.__session: Session  # db session

    @time_profile
    def update_flights_db_state(self) -> None:
        self.__session.insert_models(self.add_aircrafts)
        self.__session.insert_models(self.add_flights)
        self.__session.insert_models(self.add_timestamps)
        self.__session.update_models()
        self.add_aircrafts = []
        self.add_timestamps = []
        self.add_flights = []

    @time_profile_sum
    def create_flight_check(
        self,
        icao24: str,
        callsign: str,
        timestamp: int,
        **options: Any,
    ) -> Flight:
        # create new flight
        flight = Flight(
            aircraft_icao24=icao24,
            callsign=callsign,
            first_record=timestamp,
            last_record=timestamp,
        )

        if prev_flight := self.__flights.get_flight(icao24):
            # check if callsign is the same
            if not (prev_flight.callsign == callsign):
                # end previous flight
                prev_flight.end()
                self.remove_from_possibly_ended(prev_flight.aircraft_icao24)
                self.add_flights.append(flight)
            else:  # just return already existing flight
                return prev_flight
        else:  # aircraft not detected in the current flights
            # get from database
            aircraft = self.__session.get_aircraft(icao24)
            # new aircraft
            if not aircraft:
                aircraft = Aircraft(icao24=icao24, **options)
                self.add_aircrafts.append(aircraft)

            # add flight to the current tracking flights
            self.__flights.add_flight(flight)
            self.add_flights.append(flight)

        return flight

    @time_profile_sum
    def last_contact_check(
        self, flight: Flight, info: LastContactInfo, timestamp: Timestamp
    ) -> None:
        MIN_TRAVELLED_DISTANCE = 25 * 0.001  # (from meters) km

        # new flight
        if flight.id is None:
            flight.add_timestamp(timestamp)
            flight.update_last_contact(info)

        # get previous timestamp values
        prev_lat, prev_long = (
            flight.last_contact_info.latitude,
            flight.last_contact_info.longitude,
        )

        # if new timestamp is higher than previous one
        # and airplane has travelled more than 25m
        if (
            (flight.last_record < timestamp.timestamp)
            and (
                (
                    distance := haversine(
                        prev_lat, prev_long, timestamp.latitude, timestamp.longitude
                    )
                )
                > MIN_TRAVELLED_DISTANCE
            )
            and is_valid_timestamp(flight.last_record, timestamp.timestamp, distance)
        ):
            # update flight model
            flight.update_last_contact(info)
            self.add_timestamps.append(timestamp)
            flight.last_record = timestamp.timestamp
            # set flight to active
            self.__flights.set_active(flight.aircraft_icao24, True)

    @time_profile_sum
    def possible_ending_check(
        self, flight: Flight, velocity: None | float, vertical_rate: None | float
    ) -> None:
        # checks if flight is possibly ending
        # it is not accurate.. since both values can be None
        # TODO: think of something better
        if (
            (velocity is None or velocity < MINIMAL_VELOCITY)
            and (vertical_rate is None or vertical_rate < MINIMAL_VERTICAL_RATE)
            and (flight not in self.possibly_ended_flights)
        ):
            self.possibly_ended_flights.add(flight.aircraft_icao24)
        else:
            self.remove_from_possibly_ended(flight.aircraft_icao24)

    def remove_from_possibly_ended(self, icao24: str) -> None:
        try:
            self.possibly_ended_flights.remove(icao24)
        except KeyError:
            pass

    @time_profile
    def remove_flights_check(self, checked_flights: set[str]) -> None:
        non_updated_icao24 = set(self.__flights.flights.keys()) - set(checked_flights)
        non_updated_fligths = [
            flight
            for icao24 in non_updated_icao24
            if (flight := self.__flights.get_flight(icao24)) is not None
        ]

        print(
            "Number of unused flights: ",
            len(non_updated_icao24),
        )
        print(len(self.possibly_ended_flights))

        # check all remaining flights
        for flight in non_updated_fligths:
            # time difference since last contact
            diff = time_diff(flight.last_record)
            # flight has no update for maximal inactive time or
            # flight is inactive more than maximal possibly ended inactive time and its possibly ended
            if (diff > MAXIMAL_INACTIVE) or (
                diff > P_END_INACTIVE_MAX
                and flight.aircraft_icao24 in self.possibly_ended_flights
            ):
                flight.end()
                self.remove_from_possibly_ended(flight.aircraft_icao24)

    @time_profile
    def update_shared_memory(self) -> None:
        tmp = [
            {
                "icao24": icao24,
                "id": props.flight.id,
                "has_record": props.flight.has_record,
                "position": (
                    props.flight.last_contact_info.latitude,
                    props.flight.last_contact_info.longitude,
                ),
                "angle": props.flight.last_contact_info.track_angle,
            }
            for icao24, props in self.__flights.flights.items()
            if props.active
        ]

        output = get_clusters(tmp)
        lock.acquire()
        flights.update(output)
        lock.release()

    @time_profile
    def update_flights(self):
        checked_flights: list[str] = []

        # recieve all current flights
        state_vectors = self.api.get_all_state_vectors()

        # in case of some error
        if not state_vectors:
            return

        self.__flights = Flights(self.__session.get_active_flights())

        # get all active fligths
        print("Number of flights: ", len(self.__flights.flights))

        for vector in state_vectors:
            callsign = to_valid_callsign(vector.callsign)
            # skip if state vector is not valid
            if (
                callsign == to_valid_callsign("")
                or not (vector.longitude or vector.latitude)
                or not (vector.time_position)
            ):
                continue

            # get track angle
            track_angle = vector.true_track if vector.true_track is not None else 0.0

            # 1. create new flight if not exists or retrieve existing one
            flight = self.create_flight_check(
                vector.icao24,
                callsign,
                vector.time_position,
                origin_country=vector.origin_country,
            )

            # 2. create timestamp

            info = LastContactInfo(
                latitude=vector.latitude,
                longitude=vector.longitude,
                track_angle=track_angle,
                vertical_rate=vector.vertical_rate,
                velocity=vector.velocity,
                altitude=vector.geo_altitude,
            )

            timestamp = Timestamp(
                flight_id=flight.id,
                timestamp=vector.time_position,
                latitude=vector.latitude,
                longitude=vector.longitude,
                altitude=vector.geo_altitude,
            )

            # print("Checking last contact...")
            # 3. check last contact (update)
            self.last_contact_check(flight, info, timestamp)

            # print("Checking possible ending...")
            # 4. check if flight is being possibly ended
            self.possible_ending_check(flight, vector.velocity, vector.vertical_rate)

            # 5. keep track of all processed flights
            checked_flights.append(vector.icao24)

        log_duration(self.create_flight_check)
        log_duration(self.last_contact_check)
        log_duration(self.possible_ending_check)

        # 6. remove or end flights
        self.remove_flights_check(checked_flights)
        self.update_flights_db_state()
        self.update_shared_memory()
        # print("Remove time: ", round(self.profile_check, 3))

    def run(self):
        while True:
            try:
                self.__session = Session()
                self.update_flights()
            except Exception as exc:
                logger.exception(exc)
            finally:
                self.update_flights_db_state()
                self.__session.close()
                time.sleep(15)
