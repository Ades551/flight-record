import Map from "../../components/Map";
import {
    flightInfo,
    getFlightInfo,
} from "../../assets/util/flights";
import { useState } from "react";
import NavBar from "../../components/navbar/NavBar";
import { ButtonGroup, ToggleButton } from "react-bootstrap";
import { MapControl } from "../../components/map-controll/map-controll";
import InfoPanel from "../../components/info-panel/InfoPanel";
import { CustomPolyline } from "../../components/polyline/CustomPolyline";
import { Flights } from "../../components/live-flight/Flights";
import { Airports } from "../../components/airports/Airports";
import { boundries } from "../../assets/util/types";
import { ApiRequest } from "../../assets/util/util";
import "./style.css";

/**
 * Convert radians to degrees
 * @param radians radians
 * @returns degrees as a string
 */
const toDegrees = (radians: number) => {
    let degrees = Math.floor(radians);
    let minutes_full = (radians - degrees) * 60;
    let minutes = Math.floor(minutes_full);
    let seconds = Math.round((minutes_full - minutes) * 60);
    
    return `${degrees}° ${minutes}' ${seconds}''`;
}

export const Home = () => {
    const [interval, setMyInterval] = useState<boolean>(true);
    const [selectedFlight, setSelectedFlight] = useState<flightInfo>(null);
    const [boundries, setBoundries] = useState<boundries>();
    const [zoom, setZoom] = useState<number>(4);
    const [mapMode, setMapMode] = useState<number>(1);
    const [request, setRequest] = useState<ApiRequest>(null);

    /**
     * Handle new flight request
     * @param id flight id
     */
    const handleRequest = (id: number) => {
        request?.abort();

        let req = getFlightInfo(id);
        setRequest(req);
        req.request((response) => setSelectedFlight(response.flight));
    }

    return (
        <>
            <div className="d-flex flex-column vh-100">
                <NavBar/>
                <div className="flex-fill">
                    <Map>
                        <div
                            className="position-absolute top-0 start-0 m-1 bg-dark bg-opacity-75 rounded"
                            style={{zIndex: 999}}
                        >
                            <ButtonGroup>
                                <ToggleButton
                                    value={1}
                                    type="radio"
                                    variant={mapMode === 1 ? "outline-warning" : "outline-light"}
                                    onClick={() => {
                                        setMyInterval(true);
                                        setMapMode(1)
                                    }}
                                >
                                    Flights
                                </ToggleButton>
                                <ToggleButton
                                    value={2}
                                    type="radio"
                                    variant={mapMode === 2 ? "outline-warning" : "outline-light"}
                                    onClick={() => {
                                        setSelectedFlight(null);
                                        setMyInterval(false);
                                        setMapMode(2);
                                    }}
                                >
                                    Airports
                                </ToggleButton>
                            </ButtonGroup>
                        </div>
                        <MapControl
                            onZoomEnd={(zoom) => setZoom(zoom)}
                            onMooveEnd={(boundries) => setBoundries(boundries)}
                        >
                            {
                                mapMode === 1 ? (
                                    <Flights
                                        selectedFlight={selectedFlight}
                                        interval={interval}
                                        zoom={zoom}
                                        boundries={boundries}
                                        onFlightClick={(id) => handleRequest(id)}
                                        onUpdate={() => {
                                            if (selectedFlight) {
                                                handleRequest(selectedFlight.id);
                                            }
                                        }}
                                    />
                                ): (
                                    <Airports
                                        selectedFlight={selectedFlight}
                                        onSelectedFlight={(flight) => setSelectedFlight(flight)}
                                    />
                                )
                            }
                        </MapControl>
                        {
                            selectedFlight ? (
                                <InfoPanel
                                    className="start-0 bottom-0"
                                    title="Flight info"
                                    onClose={() => setSelectedFlight(null)}>
                                    <InfoPanel.Body className="h6 m-0 info overflow-auto" style={{height: "180px"}}>
                                        <p><b>Callsign: </b>{selectedFlight.callsign}</p>
                                        <p><b>ICAO24: </b>
                                            <a
                                                href={
                                                    `https://opensky-network.org/aircraft-profile?icao24=${selectedFlight.icao24}`
                                                }
                                                target="blank"
                                            >
                                                {selectedFlight.icao24}
                                            </a>
                                        </p>
                                        <p><b>Latitude: </b>{toDegrees(selectedFlight.position[0])}</p>
                                        <p><b>Longitude: </b>{toDegrees(selectedFlight.position[1])}</p>
                                        <p><b>Track angle: </b>{selectedFlight.angle}°</p>
                                        {/* <p><b>Origin country: </b>{selectedFlight.origin_country}</p> */}
                                        <p><b>Velocity: </b>{selectedFlight.velocity} m/s</p>
                                        <p><b>Vertical rate: </b>{selectedFlight.vertical_rate} m/s</p>
                                        <p><b>Altitude: </b>{selectedFlight.altitude} m</p>
                                    </InfoPanel.Body>
                                </InfoPanel>
                            ) : null
                        }
                        <CustomPolyline selectedFlight={selectedFlight}/>
                    </Map>
                </div>
            </div>
        </>
    );
}
