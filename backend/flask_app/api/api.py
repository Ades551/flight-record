import json
from datetime import datetime
from typing import Any

import pytz
from database.models import Flight, Timestamp
from database.session import Session
from flask import Blueprint, Response, jsonify, request
from flask_app import PATH_TO_APP, flights, get_api_url
from haversine import haversine
from profiling_decorators import time_profile
from threads import ZOOM_LEVELS, lock_flights

MAX_SPEED = 950
OVERLAP = 3000


def return_error() -> tuple[Response, int]:
    return jsonify({"message": "Invalid request"}), 400


api = Blueprint("api", __name__)


def to_date(timestamp: int) -> str:
    """Get datetime with timezone."""
    return datetime.fromtimestamp(timestamp, tz=pytz.UTC).strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )


def check_requets(*args: str) -> bool:
    """Decorator for checking requests arguments."""
    if any(i not in request.args for i in args) and len(args) != len(request.args):
        return False
    return True


def get_flight_info(*flights: Flight) -> list[dict[str, Any]]:
    """Get JSON like representation of flights models."""
    output = []

    for flight in flights:
        if flight:
            info = flight.last_contact_info
            output.append(
                {
                    "id": flight.id,
                    "callsign": flight.callsign,
                    "last": to_date(flight.last_record),
                    "first": to_date(flight.first_record),
                    "icao24": flight.aircraft_icao24,
                    "angle": info.track_angle,
                    "position": info.position,
                    "ended": flight.ended,
                    "velocity": info.velocity,
                    "vertical_rate": info.vertical_rate,
                    "altitude": info.altitude,
                }
            )

    return output


# NOTE: for future needs
# def bezier_curve(positions: list[tuple[float, float]]) -> list[tuple[float, float]]:
#     ls = LineString(positions)
#     f = Feature(geometry=ls)
#     bs = bezier_spline(f)

#     return bs["geometry"]["coordinates"]


@api.route("/airport/flights", methods=["GET"])
def get_airport():
    if not check_requets("id"):
        return jsonify({"flights": []}), 200

    session = Session()
    flights = session.get_flight_from_airport(request.args["id"])
    session.close()

    return (
        jsonify({"flights": get_flight_info(*flights)}),
        200,
    )


# NOTE: In case that in the future we will want to display multiple airports
# @api.route("/airports", methods=["GET"])
# def get_airports():
#     if not check_requets("zoom"):
#         return jsonify({"clusters": []})

#     zoom = int(request.args["zoom"])

#     if zoom > max(ZOOM_LEVELS):
#         zoom = -1

#     return jsonify({"clusters": [cluster.json() for cluster in airports[zoom]]}), 200


@api.route("/airports")
def get_airports() -> tuple[Response, int]:
    """Get airports with recordings."""
    session = Session()
    airports = session.get_active_airports()
    session.close()

    return (
        jsonify(
            {
                "airports": [
                    {
                        "id": airport.id,
                        "gps_code": airport.gps_code,
                        "local_code": airport.local_code,
                        "iata_code": airport.iata_code,
                        "position": airport.position,
                        "name": airport.name,
                    }
                    for airport in airports
                ]
            }
        ),
        200,
    )


@api.route("/flight", methods=["GET"])
@lock_flights
def get_flight() -> tuple[Response, int]:
    """Get specific flight."""
    if not check_requets("id"):
        return return_error()

    session = Session()
    flight = session.get_flight(int(request.args["id"]))
    session.close()
    if flight:
        return (
            jsonify({"flight": get_flight_info(flight)[0]}),
            200,
        )
    return jsonify({"flight": []}), 200


@api.route("/flights", methods=["GET"])
@lock_flights
def get_flights() -> tuple[Response, int]:
    """Get clustered flights."""
    if not check_requets("zoom"):
        return return_error()

    zoom = int(float(request.args["zoom"]))

    if zoom > max(ZOOM_LEVELS):
        zoom = -1
    elif zoom < min(ZOOM_LEVELS):
        zoom = min(ZOOM_LEVELS)
    return jsonify({"clusters": [cluster.json() for cluster in flights[zoom]]}), 200


# TODO: move to other file
def parse_transcript(transcript_path: str) -> Any:
    """Get parsed transcript."""
    if transcript_path is None:
        return None

    # segments [{start, end, words: [{start, end, word}]}]
    output: dict[str, list[Any]] = {"segments": []}

    try:
        with open(PATH_TO_APP / transcript_path) as file:
            transcript = json.load(file)

            for segment in transcript["segments"]:
                start = segment["start"]
                end = segment["end"]
                words = []
                for word in segment["words"]:
                    words.append(
                        {
                            "start": round(start + word["start"], 2),
                            "end": round(start + word["end"], 2),
                            "word": word["label"],
                        }
                    )
                output["segments"].append({"start": start, "end": end, "words": words})
    except FileNotFoundError:
        return None

    return output


def get_lines(timestamps: list[Timestamp]) -> list[dict[str, Any]]:
    """Get lines with specific attribute."""
    # calculate positions with distance between every 2 points
    positions = [
        (
            timestamps[i].position,
            timestamps[i + 1].position,
            timestamps[i].altitude,
            haversine(*timestamps[i].position, *timestamps[i + 1].position),
        )
        for i in range(len(timestamps) - 1)
    ]

    lines: list[dict[str, Any]] = []

    # filter positions
    for position in positions:
        if position[3] >= OVERLAP:
            continue
        else:
            lines.append(
                {
                    "positions": [position[0], position[1]],
                    "altitude": position[2],
                    "distance": position[3],
                }
            )

    return lines


@api.route("/flight/timestamps", methods=["GET"])
@time_profile
def get_flight_timestamps() -> tuple[Response, int]:
    """Get timestamps for the flight."""
    if not check_requets("id"):
        return return_error()

    session = Session()
    flight = session.get_flight(int(request.args["id"]))

    if not flight:
        session.close()
        return return_error()

    markers = [
        {
            "position": timestamp.position,
            "mp3": get_api_url(timestamp.mp3),
            "timestamp": to_date(timestamp.timestamp),
            "transcript": parse_transcript(timestamp.transcript),
        }
        for timestamp in flight.timestamps
        if timestamp.mp3
    ]
    lines = get_lines(flight.timestamps)
    session.close()

    return jsonify({"lines": lines, "markers": markers}), 200


@api.route("/flights/record/all", methods=["GET"])
@time_profile
def get_flights_with_record() -> tuple[Response, int]:
    """Get all flights with recordigns."""
    session = Session()
    db_flights = session.get_flight_with_records()
    output = [
        {
            "id": flight.id,
            "callsign": flight.callsign,
            "date": to_date(flight.last_record),
            "airports": [airport.iata_code.upper() for airport in flight.airports]
            if flight.airports
            else None,
        }
        for flight in db_flights
    ]
    session.close()

    return jsonify({"table": output}), 200


@api.route("/flight/records", methods=["GET"])
@time_profile
def get_flight_records() -> tuple[Response, int]:
    """Get flight recordings."""
    if not check_requets("id"):
        return return_error()

    session = Session()

    db_flight = session.get_flight(request.args["id"])

    output = [
        {
            "mp3": get_api_url(timestamp.mp3),
            "transcript": parse_transcript(timestamp.transcript),
        }
        for timestamp in db_flight.timestamps
        if timestamp.mp3
    ]
    session.close()

    return jsonify({"records": output}), 200
