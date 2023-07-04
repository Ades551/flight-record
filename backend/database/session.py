import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Iterable, Optional

from database.models import Aircraft, Airport, Flight, Timestamp
from sqlalchemy import create_engine, or_
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_PORT = 3306
MYSQL_DB = "vhf_opensky"

CONNECTION_STRING = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

logger = logging.getLogger(__name__)

engine = create_engine(
    os.environ.get("DATABASE_URL") or CONNECTION_STRING,
    echo=False,
    pool_recycle=280,
    pool_size=20,
    max_overflow=30,
)
# Scoped_session = scoped_session(
#     sessionmaker(autocommit=False, autoflush=False, bind=engine)
# )
Scoped_session = scoped_session(sessionmaker(bind=engine))


def is_ready() -> bool:
    try:
        connection = engine.connect()
        connection.close()
    except OperationalError:
        return False
    return True


def handle_error(fnc):
    @wraps(fnc)
    def wrapper(*args, **kwargs):
        try:
            return fnc(*args, **kwargs)
        except Exception as exc:
            logger.exception(exc)
            print(f"{fnc.__name__}: There was an error with the database!")

    return wrapper


class Session:
    def __init__(self) -> None:
        self.session = Scoped_session()

    def insert_models(
        self, models: Iterable[Airport | Aircraft | Flight | Timestamp]
    ) -> None:
        # add models into a query
        self.session.add_all(models)

    @handle_error
    def get_aircrafts(self) -> list[Aircraft]:
        return self.session.query(Aircraft).all()

    @handle_error
    def get_aircraft(self, icao24: str) -> Optional[Aircraft]:
        return self.session.query(Aircraft).filter(Aircraft.icao24 == icao24).first()

    @handle_error
    def get_flight(self, id: int) -> Optional[Flight]:
        return self.session.query(Flight).get(id)

    @handle_error
    def get_active_flight(self, icao24: str) -> Optional[Flight]:
        return (
            self.session.query(Flight)
            .join(Aircraft)
            .filter((Aircraft.icao24 == icao24) & (Flight.ended == False))
            .first()
        )

    @handle_error
    def get_active_flights(self) -> list[Flight]:
        return self.session.query(Flight).filter(Flight.ended == False).all()

    @handle_error
    def get_flights_in_interval(
        self, callsigns: tuple[str, ...], start: int, end: int
    ) -> Optional[list[Flight]]:
        # TODO: ERROR database.session This result object does not return rows. It has been closed automatically.
        # because of it this function will return None
        return (
            self.session.query(Flight)
            .filter(Flight.within_interval(start, end) & Flight.callsign.in_(callsigns))
            .all()
        )

    @handle_error
    def get_flights_with_record_interval(
        self, start: datetime, end: datetime
    ) -> list[Flight]:
        return (
            self.session.query(Flight)
            .filter(
                (Flight.has_record == True)
                & (
                    ((Flight._first_record <= start) & (Flight._last_record >= start))
                    | ((Flight._first_record >= start) & (Flight._last_record <= end))
                    | ((Flight._first_record <= end) & (Flight._last_record >= end))
                )
            )
            .all()
        )

    @handle_error
    def get_flight_with_records(self) -> list[Flight]:
        return self.session.query(Flight).filter(Flight.has_record == True).all()

    @handle_error
    def get_model(
        self, model: Flight | Timestamp | Aircraft | Airport, id: str | int
    ) -> Optional[Flight | Timestamp | Aircraft | Airport]:
        return self.session.query(model).get(id)  # type: ignore[arg-type]

    @handle_error
    def get_flight_from_airport(self, id: int) -> list[Flight]:
        if airport := self.get_model(Airport, id):
            return airport.detected_flights
        return []

    @handle_error
    def get_airports(self) -> list[Airport]:
        return self.session.query(Airport).all()

    @handle_error
    def get_airport(self, code: str) -> Optional[Airport]:
        return (
            self.session.query(Airport)
            .filter(
                or_(
                    Airport.gps_code == code,
                    Airport.local_code == code,
                    Airport.iata_code == code,
                )
            )
            .first()
        )

    @handle_error
    def get_active_airports(self) -> list[Airport]:
        return self.session.query(Airport).filter(Airport.detected_flights.any()).all()

    @handle_error
    def flight_bulk_update(self, data: dict[str, Any]):
        self.session.bulk_update_mappings(Flight, data)  # type: ignore[arg-type]

    @handle_error
    def old_flights(self, date: datetime) -> list[Flight]:
        return self.session.query(Flight).filter(Flight._last_record < date).all()

    @handle_error
    def ended_no_record(self, date: datetime) -> list[Flight]:
        return (
            self.session.query(Flight)
            .filter(
                (Flight.has_record == False)
                & Flight.ended
                & (Flight._last_record < date)
            )
            .all()
        )

    @handle_error
    def remove_flights(self, flights: list[Flight]) -> None:
        for flight in flights:
            self.session.delete(flight)
        self.session.commit()

    def update_models(self) -> None:
        self.session.commit()

    def close(self) -> None:
        self.session.close()
