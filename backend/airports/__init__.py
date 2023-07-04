import csv

import requests
from database.models import Airport
from database.session import Session

CSV_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"

TYPE = 2
NAME = 3
LATITUDE = 4
LONGITUDE = 5
GPS_CODE = 12
IATA_CODE = 13
LOCAL_CODE = 14


def db_insert_airports():
    session = Session()
    response = requests.get(CSV_URL)

    if response.status_code != 200:
        raise RuntimeError("Invalid response code!")

    reader = csv.reader(response.content.decode("utf-8").splitlines(), delimiter=",")
    _ = next(reader)
    airports = [
        Airport(
            iata_code=row[IATA_CODE].lower(),
            gps_code=row[GPS_CODE].lower(),
            local_code=row[LOCAL_CODE].lower(),
            type=row[TYPE],
            name=row[NAME],
            latitude=float(row[LATITUDE]),
            longitude=float(row[LONGITUDE]),
        )
        for row in reader
        if "airport" in row[TYPE]
    ]

    session.insert_models(airports)
    session.update_models()
