from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, PickleType, String, Table
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# This is just used for better structure
# all properties can be used directly in the Flight table
class LastContactInfo:
    """Last contact information."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        track_angle: float,
        vertical_rate: Optional[float],
        velocity: Optional[float],
        altitude: Optional[float],
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.track_angle = track_angle
        self.vertical_rate = vertical_rate
        self.velocity = velocity
        self.altitude = altitude

    @property
    def position(self) -> tuple[float, float]:
        return self.latitude, self.longitude


class Base(DeclarativeBase):
    ...


# note for a Core table, we use the sqlalchemy.Column construct,
# not sqlalchemy.orm.mapped_column
association_table = Table(
    "association_table",
    Base.metadata,
    Column("airport_id", ForeignKey("airport.id", ondelete="CASCADE")),
    Column("flight_id", ForeignKey("flight.id", ondelete="CASCADE")),
)


class Airport(Base):
    __tablename__ = "airport"

    id: Mapped[int] = mapped_column(primary_key=True)

    iata_code: Mapped[str] = mapped_column(String(10), nullable=True)
    gps_code: Mapped[str] = mapped_column(String(10), nullable=True)
    local_code: Mapped[str] = mapped_column(String(10), nullable=True)
    type: Mapped[str] = mapped_column(String(24), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    detected_flights: Mapped[list["Flight"]] = relationship(
        secondary=association_table, cascade="all, delete"
    )

    @property
    def position(self) -> tuple[float, float]:
        return self.latitude, self.longitude


class Aircraft(Base):
    __tablename__ = "aircraft"

    icao24: Mapped[str] = mapped_column(String(24), primary_key=True)
    origin_country: Mapped[str] = mapped_column(String(50), nullable=False)
    flights: Mapped[list["Flight"]] = relationship(cascade="all")


# TODO: consider storing first and last record as int
# since there is a lot of conversion in the code, (very inconsistent)
class Flight(Base):
    __tablename__ = "flight"

    id: Mapped[int] = mapped_column(primary_key=True)
    aircraft_icao24: Mapped[str] = mapped_column(
        ForeignKey("aircraft.icao24", ondelete="CASCADE")
    )

    callsign: Mapped[str] = mapped_column(String(8), nullable=False)
    _first_record: Mapped[datetime] = mapped_column(nullable=False)
    _last_record: Mapped[datetime] = mapped_column(nullable=False)
    ended: Mapped[bool] = mapped_column(default=False)
    has_record: Mapped[bool] = mapped_column(nullable=False, default=False)
    last_contact_info: Mapped[LastContactInfo] = mapped_column(
        PickleType, nullable=False
    )
    airports: Mapped[list[Airport]] = relationship(
        secondary=association_table, back_populates="detected_flights"
    )
    timestamps: Mapped[list["Timestamp"]] = relationship(cascade="all, delete")

    def add_timestamp(self, timestamp: "Timestamp") -> None:
        self.timestamps.append(timestamp)

    @property
    def first_record(self) -> int:
        return int(datetime.timestamp(self._first_record))

    @first_record.setter
    def first_record(self, timestamp):
        self._first_record = datetime.fromtimestamp(timestamp)

    @property
    def last_record(self) -> int:
        return int(datetime.timestamp(self._last_record))

    @last_record.setter
    def last_record(self, timestamp):
        self._last_record = datetime.fromtimestamp(timestamp)

    def update_last_contact(self, info: LastContactInfo) -> None:
        self.last_contact_info = info

    @hybrid_method
    def within_interval(self, start: int, end: int) -> bool:
        d_start = datetime.fromtimestamp(start)
        d_end = datetime.fromtimestamp(end)
        return ((self._first_record <= d_end) & (d_end <= self._last_record)) | (
            (self._first_record <= d_start) & (d_start <= self._last_record)
        )

    def end(self):
        self.ended = True


class Timestamp(Base):
    __tablename__ = "timestamp"

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flight.id", ondelete="CASCADE"))

    timestamp: Mapped[int] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    altitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    mp3: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None)
    transcript: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None
    )

    @property
    def position(self) -> tuple[float, float]:
        return self.latitude, self.longitude


TABLES: list[type[Base]] = [Airport, Aircraft, Flight, Timestamp]
