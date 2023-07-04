import { useState, FunctionComponent, useEffect, useRef } from "react";
import { Marker, Popup, Polyline, useMap } from "react-leaflet";
import WaveForm from "../waveform/WaveForm";
import { planeIcon, soundIcon, ArrowIcon } from "../icons/icons";
import { flightInfo, polylineMarker, getFlightTimestamps, polyline } from "../../assets/util/flights";
import RotatedMarker from "../markers/RotatedMarker";
import { COLORS } from "../../values/colors";
import { interpolateCividis } from "d3-scale-chromatic";
import { getDateTime } from "../../assets/util/util";
import L from "leaflet";
import "./style.css";

type PolylineProps = {
    selectedFlight: flightInfo,
}

export const CustomPolyline: FunctionComponent<PolylineProps> = ({ selectedFlight }) => {
    const [markers, setMarkers] = useState<polylineMarker[]>(null);
    const [lines, setLines] = useState<polyline[]>(null);
    const [id, setId] = useState<number>(null);

    const map = useMap();
    const markersRef = useRef([]);

    /**
     * Get color from palette.
     * @param altitude alitude
     * @returns color from specific color palette
     */
    const getColor = (altitude: number) => {
        if ( altitude ) {
            return interpolateCividis(altitude / 13000);
        }
        return interpolateCividis(0);
    }

    // removes polylines
    const removePolylines = () => {
        map.eachLayer((layer) => {
            if(layer instanceof L.Polyline) {
                layer.remove();
            }
        });
    }

    useEffect(() => {
        if (selectedFlight) { // flight is selected
            let req = getFlightTimestamps(selectedFlight.id);
            req.request((response) => { // get timestamps callback 
                if (markers === null || id !== selectedFlight.id) {
                    let markers: polylineMarker[] = response.markers; // get markers
    
                    if ( markers.length > 0 ) {
                        // zoom to the first recording marker
                        map.setView(markers[0].position, 10, {animate: true});
                    }
    
                    setId(selectedFlight.id);
                    setMarkers(markers);
                    removePolylines();
                }
                setLines(response.lines);
            });
        } else { // null everything
            setMarkers(null);
            setLines(null);
            removePolylines();
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id, map, markers, selectedFlight]);
    return (
        <>
            {
                markers?.map((marker, index) => (
                    <Marker
                        icon={soundIcon()}
                        position={marker.position}
                        key={marker.mp3}
                        ref={el => markersRef.current[index] = el}
                    >
                        <Popup>
                            {
                                index > 0 ? (
                                    <ArrowIcon
                                        onClick={() => {markersRef?.current[index - 1].fire('click')}}
                                        className="position-absolute top-50 start-0 translate-middle"
                                        side="left"
                                    />
                                ) : null
                            }
                            <div className="popup-div">
                                <div className="row">
                                    <div className="col-12">
                                        <h6><b>Callsign:</b> {selectedFlight?.callsign}</h6> 
                                    </div>
                                    <div className="col-12">
                                        <h6><b>Timestamp:</b> {getDateTime(marker.timestamp)}</h6> 
                                    </div>
                                </div>
                                <WaveForm
                                    audio_url={marker.mp3}
                                    transcript={marker.transcript}
                                    autoPlay={true}
                                />
                            </div>
                            {
                                index < markers.length - 1 ? (
                                    <ArrowIcon
                                        onClick={() => markersRef.current[index + 1].fire('click')}
                                        className="position-absolute top-50 start-100 translate-middle"
                                        side="right"
                                    />
                                ) : null
                            }
                        </Popup>
                    </Marker>
                ))
            }
            {
                lines?.map((line) => (
                    <Polyline
                        key={line.positions.toString() + selectedFlight?.icao24}
                        positions={line.positions}
                        color={line.distance < 100 ? getColor(line.altitude) : COLORS.black}
                    />
                ))
            }
            {
                selectedFlight? (
                    <RotatedMarker
                        key={selectedFlight.icao24 + selectedFlight.position}
                        position={selectedFlight.position}
                        angle={selectedFlight.angle}
                        icon={planeIcon(COLORS.blue)}
                    />
                ) : null
            }
        </>
    );
}
