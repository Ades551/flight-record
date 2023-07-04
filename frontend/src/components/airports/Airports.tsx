import { useEffect, useState } from "react";
import { airport, getAirports, getDetectedFligths } from "../../assets/util/airports";
import { Marker, useMap } from "react-leaflet";
import { AirportIcon } from "../icons/icons";
import { flightInfo } from "../../assets/util/flights";
import InfoPanel from "../info-panel/InfoPanel";
import { Card, Collapse } from "react-bootstrap";
import CustomDateTimePicker from "../datetimepicker/DateTimePicker";
import dayjs, { Dayjs } from "dayjs";
import { SearchIcon } from "./icon";
import { getDateTime, CENTER, BASIC_ZOOM, ApiRequest } from "../../assets/util/util";

type AirportsProps = {
    selectedFlight: flightInfo
    onSelectedFlight?: (flight: flightInfo) => void
}

export const Airports = ({selectedFlight, onSelectedFlight}: AirportsProps) => {
    const [airports, setAirports] = useState<airport[]>(null);
    const [selectedAirport, setSelectedAirport] = useState<airport>(null);
    const [airportFlights, setAirportFlights] = useState<flightInfo[]>(null);
    const [filteredFlights, setFilteredFlights] = useState<flightInfo[]>(null);
    const [collapse, setCollapse] = useState(false);
    const [request, setRequest] = useState<ApiRequest>(null)
    const [loading, setLoading] = useState(false);

    const map = useMap();
    
    const handleSearch = (date: Dayjs, from: Dayjs, to: Dayjs) => {
        if ( from == null ) {
            from = dayjs().startOf('day');
        }
        
        if ( to == null ) {
            to = dayjs().endOf('day');
        } 
        
        if ( date == null ) {
            setFilteredFlights(airportFlights);
        } else {
            let start: Dayjs = date.set('hour', from.hour()).set('minute', from.minute());
            let end: Dayjs = date.set('hour', to.hour()).set('minute', to.minute());
            
            let tmp: flightInfo[] = [];
            
            for (const flight of airportFlights) {
                let flight_start = dayjs(flight.first);
                let flight_end = dayjs(flight.last);
                if ((flight_start.isBefore(end) && flight_end.isAfter(start)) || 
                flight_start.isSame(end) || flight_end.isSame(start)) {
                        tmp.push(flight);
                }
            }
            setFilteredFlights(tmp);
        }
    }
    
    
    useEffect(() => {
        map.setView(CENTER, BASIC_ZOOM, {
            animate: true
        });
        getAirports().request((response) => {
            setAirports(response.airports);
        });
    }, [map]);

    return (
        <>
            {
                airports?.map((airport) => (
                    <Marker
                        key={airport.id}
                        position={airport.position}
                        icon={AirportIcon(selectedAirport?.id === airport.id, loading)}
                        eventHandlers={{click: () => {
                            request?.abort();
                            let req = getDetectedFligths(airport.id);
                            setLoading(true);
                            setRequest(req);

                            setSelectedAirport(airport);
                            map.setView(airport.position, BASIC_ZOOM, {
                                animate: true,
                            });

                            req.request((response) => {
                                setAirportFlights(
                                    response.flights.sort((a: any, b: any) => {
                                        return dayjs(b.last).diff(dayjs(a.last))
                                    })
                                );
                                setFilteredFlights(response.flights);
                                setLoading(false);
                            }, () => setLoading(false));
                        }}}
                    />
                ))
            }
            {
                selectedAirport ? (

                    <InfoPanel
                        onClose={() => {
                            setAirportFlights(null);
                            setSelectedAirport(null);
                        }}
                        className="start-0"
                        style={{
                            top: "10%",
                            zIndex: 1000
                        }}
                    >
                        <InfoPanel.Title>
                            <div className="d-flex mb-2 align-items-center">
                                <h4 className="m-0 me-3">{selectedAirport?.name}</h4>
                                <div
                                    aria-controls="datetime-collapse"
                                    aria-expanded={collapse}
                                >
                                    <SearchIcon onClick={() => setCollapse(!collapse)}/>
                                </div>
                            </div>
                            <Collapse in={collapse}>
                                <div id="datetime-collapse bg-dark">
                                    <CustomDateTimePicker
                                        onChange={(date, from, to) => handleSearch(date, from, to)}
                                    />
                                </div>
                            </Collapse>
                        </InfoPanel.Title>
                        <InfoPanel.Body isLoading={loading}>
                            {
                                filteredFlights?.map((flight, index) => (
                                    <Card
                                        key={index}
                                        className={`p-1 m-1 clickable ${
                                            selectedFlight?.id === flight.id ?
                                                "bg-dark" : "bg-dark bg-gradient"
                                        }`}
                                        onClick={() => {
                                            onSelectedFlight(flight);
                                        }}
                                    >
                                            <div className="container">
                                                <div className="row">
                                                    <div className="col-4">
                                                        <h6>
                                                            Callsign:<br/>
                                                            {flight.callsign}
                                                        </h6>
                                                    </div>
                                                    <div className="col-8 row">
                                                        <h6>Last Contact:<br/>
                                                            {getDateTime(flight.last)}
                                                        </h6>
                                                    </div>
                                                </div>
                                            </div>
                                    </Card>
                                ))
                            }
                        </InfoPanel.Body>
                    </InfoPanel>
                ) : null 
            }
        </>
    );
}
