import { boundries } from "./types"
import { positionInBoundries, ApiRequest } from "./util"

export interface airport {
    id: number
    gps_code: string
    local_code: string
    iata_code: string
    name: string
    position: [number, number]
}

/**
 * Get airports.
 * @returns available airports (with recordings)
 */
export const getAirports = (): ApiRequest => {
    return new ApiRequest("api/airports", "GET");
}

/**
 * Get detected flights.
 * @param id id of the airport
 * @returns detected flights within airport
 */
export const getDetectedFligths = (id: number): ApiRequest => {
    return new ApiRequest("api/airport/flights?".concat(new URLSearchParams({
        id: id.toString()
    }).toString()), "GET");
}

/**
 * Get airports only in boudnries.
 * @param airports list of airports
 * @param boundries map boundries
 * @returns airports that are within the specified boundries
 */
export const getAirportsInBoundries = (airports: airport[], boundries: boundries) => {
    if (!boundries || !airports) {
        return airports
    }

    let tmp: airport[] = [];

    for (const airport of airports) {
        if (positionInBoundries(airport.position, boundries)) {
            tmp.push(airport);
        }
    }

    return tmp;
}
