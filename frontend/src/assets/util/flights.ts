import { LatLngTuple } from "leaflet";
import { boundries, flightCluster } from "./types";
import { ApiRequest, positionInBoundries } from "./util";

// records
interface timeInterval {
    start: number,
    end: number
}

interface word extends timeInterval {
    word: string
}

interface segment extends timeInterval {
    words: word[]
}

export interface transcript {
    segments: segment[]
}

export interface waveRecord {
    mp3: string,
    transcript: transcript
}

// flight basic info
export interface flight {
    icao24: string
    id: number
    position: LatLngTuple
    angle: number
    has_record: boolean
}

// extended flight info
export interface flightInfo extends flight {
    callsign: string
    last: string
    first: string
    active: boolean
    origin_country: string
    velocity: number
    vertical_rate: number
    altitude: number
}

export interface polylineMarker {
    mp3: string
    transcript: transcript
    position: LatLngTuple
    timestamp: string
}

export interface flightTableInfo {
    callsign: string
    date: string
    id: number
    airports: string
}

export interface polyline {
    altitude: number | null
    positions: LatLngTuple[]
    distance: number
}

/**
 * Get flights in bondires.
 * @param flights list of flights
 * @param boundries map boundries
 * @returns list of flights within the specified boudries
 */
export const getFlightsInBoundries = (flights: flight[], boundries: boundries) => {
    if (boundries === undefined) {
        return flights
    }

    let temp_flights: flight[] = [];

    for (const flight of flights) {
        if (positionInBoundries(flight.position, boundries)) {
            temp_flights.push(flight);
        }
    }

    return temp_flights;
}

/**
 * Get clusters in boudries.
 * @param clusters list of clusters
 * @param boundries map boundries
 * @returns list of clusters that are within the specified boundries
 */
export const getClusterFlightsInBoundries = (clusters: flightCluster[], boundries: boundries) => {
    if (!boundries || !clusters) {
        return clusters;
    }

    let tmp: flightCluster[] = [];

    for (const cluster of clusters) {
        if (positionInBoundries(cluster.position, boundries)) {
            tmp.push(cluster);
        }
    }

    return tmp;
}

/**
 * 
 * @param zoom map zoom
 * @returns ApiRequest instance for creating API call to receive flights
 */
export const getFlightsFromAPI = (zoom: number): ApiRequest => {
    return new ApiRequest("api/flights?".concat(new URLSearchParams({
        zoom: zoom.toString()
    }).toString()), "GET");
}

/**
 * 
 * @param id flight id
 * @returns ApiRequest instance for creating API call to receive flight info
 */
export const getFlightInfo = (id: number): ApiRequest => {
    return new ApiRequest("api/flight?".concat(new URLSearchParams({
        id: id.toString()
    }).toString()), "GET");
}

/**
 * Get flight timestamp
 * @param id id of the flight
 * @returns timestamps for the flight
 */
export const getFlightTimestamps = (id: number): ApiRequest => {    
    return new ApiRequest("api/flight/timestamps?".concat(new URLSearchParams({
        id: id.toString(),
    }).toString()), "GET");
}

/**
 * Get flights with recording.
 * @returns flights that have at least one recording
 */
export const getFlightsWithRecord = (): ApiRequest => {
    return new ApiRequest("api/flights/record/all", "GET");
}

/**
 * Get flight records.
 * @param id flight id
 * @returns flight recordings
 */
export const getFlightRecords = (id: number): ApiRequest => {
    return new ApiRequest("api/flight/records?".concat(new URLSearchParams({
        id: id.toString()
    }).toString()), "GET");
}
