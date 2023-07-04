from typing import Any, Optional

import requests
from api import load_credentials


class StateVector:
    def __init__(
        self,
        icao24: str,
        callsign: Optional[str],
        origin_country: str,
        time_position: Optional[int],
        last_contact: int,
        longitude: Optional[float],
        latitude: Optional[float],
        baro_altitude: Optional[float],
        on_ground: bool,
        velocity: Optional[float],
        true_track: Optional[float],
        vertical_rate: Optional[float],
        sensors: Optional[list[int]],
        geo_altitude: Optional[float],
        squawk: Optional[str],
        spi: bool,
        position_source: int,
    ) -> None:
        self.icao24 = icao24
        self.callsign = callsign
        self.origin_country = origin_country
        self.time_position = time_position
        self.last_contact = last_contact
        self.longitude = longitude
        self.latitude = latitude
        self.baro_altitude = baro_altitude
        self.on_ground = on_ground
        self.velocity = velocity
        self.true_track = true_track
        self.vertical_rate = vertical_rate
        self.sensors = sensors
        self.geo_altitude = geo_altitude
        self.squawk = squawk
        self.spi = spi
        self.position_source = position_source


class OpenSkyApi:
    date_format = "%d/%m/%Y-%H:%M"

    def __init__(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        self.api_url = "https://opensky-network.org/api"

        if not username or not password:
            credentials = load_credentials("opensky", values=["username", "password"])
            if not credentials:
                raise Exception("Missing credential for OpenSky API")

            username, password = credentials

        self._auth = (username, password)

    def __api_call(self, api_path: str, params: Optional[dict[str, Any]] = None):
        try:
            response = requests.get(
                f"{self.api_url}/{api_path}", auth=self._auth, params=params, timeout=20
            )
        except Exception:
            return None

        if response.status_code == 200:
            return response.json()
        return None

    def get_all_state_vectors(
        self, icao24: Optional[list[str]] = None
    ) -> Optional[list[StateVector]]:
        params = {"icao24": value for value in icao24} if icao24 is not None else None
        response = self.__api_call("/states/all", params=params)
        try:
            if response is not None:
                state_vectors: list[StateVector] = []
                for state_vector in response["states"]:
                    state_vector = [
                        attr.replace(",", "") if isinstance(attr, str) else attr
                        for attr in state_vector
                    ]
                    state_vectors.append(StateVector(*state_vector))

                return [
                    state_vector
                    for state_vector in state_vectors
                    if state_vector.latitude
                ]
        except TypeError:
            return None

        return None
