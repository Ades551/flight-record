import { Marker, useMap } from "react-leaflet";
import RotatedMarker from "../markers/RotatedMarker";
import { clusterIcon, planeIcon } from "../icons/icons";
import { getFlightsInBoundries, getFlightsFromAPI, getClusterFlightsInBoundries, flightInfo } from "../../assets/util/flights";
import { flightCluster } from "../../assets/util/types";
import { useState, useEffect } from "react";
import { useInterval, CENTER } from "../../assets/util/util";
import { boundries } from "../../assets/util/types";
import { COLORS } from "../../values/colors";

const BASIC_ZOOM = 10;

type FlightProps = {
    selectedFlight: flightInfo
    interval: boolean
    zoom: number
    boundries: boundries
    onFlightClick?: (id: number) => void
    onUpdate?: () => void
}

export const Flights = ({ selectedFlight, interval, zoom, boundries, onFlightClick, onUpdate }: FlightProps) => {
    // variable used for rendering flight markers/clusters 
    const [clusters, setClusters] = useState<flightCluster[]>(null);
    
    const map = useMap(); // to be able to interact with the map 

    /**
     * Cluster on click handler
     * @param cluster cluster to handle
     */
    const handleClusterClick = (cluster: flightCluster) => {
        // find position for the fist flight that has recording  
        let position = cluster.data?.find(flight => flight.has_record)?.position;
        let new_zoom = BASIC_ZOOM

        // there is no flight with recording, so just zoom
        if (!position) {
            position = cluster.position;
            new_zoom = zoom + 2;
        }

        // update position and zoom
        map.setView(position, new_zoom, {
            animate: true
        });
    }

    /**
     * Get clusters from backend
     */
    const getFlights = () => {
        if (interval === true) {
            let req = getFlightsFromAPI(zoom);
            req.request((response) => setClusters(response.clusters));
            if (onUpdate) {
                onUpdate();
            }
        }
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => getFlights(), [zoom]);

    // set interval for recieving new flights positions and data
    useInterval(() => {
        getFlights();
    }, 5000);

    useEffect(() => {
        map.setView(CENTER, 8, {animate: true});
    }, [map]);

    return (
        <>
            {
                clusters?.find(cluster => cluster.cluster === -1) ? ( // display all fligts 
                    getFlightsInBoundries(clusters[0].data, boundries).map((flight) => (
                            selectedFlight?.id !== flight.id ? (
                                <RotatedMarker
                                    key={flight.icao24 + flight.position}
                                    position={flight.position}
                                    angle={flight.angle}
                                    icon={planeIcon(flight.has_record ? COLORS.red : null)}
                                    onClick={() => {
                                        onFlightClick(flight.id);
                                    }}
                                />
                            ) : null
                    ))
                ) : (
                    getClusterFlightsInBoundries(clusters, boundries)?.map((cluster) => ( // display clustered flights
                        <Marker
                            key={cluster.cluster}
                            position={cluster.position}
                            icon={clusterIcon(cluster.data?.length, cluster.data?.find(flight => flight.has_record) ? 
                                COLORS.red : null)}
                            eventHandlers={{click: () => handleClusterClick(cluster)}}
                        />
                    ))
                )
            }
        </>
    );
}
