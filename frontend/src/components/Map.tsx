import { MapContainer, TileLayer, ZoomControl } from "react-leaflet";
import { CENTER } from "../assets/util/util";

type MapProps = {
    children?: JSX.Element | JSX.Element[] 
}

const Map = ({ children }: MapProps) => {
    return (
        <>
            <MapContainer
                className="h-100 w-100"
                preferCanvas={true}
                center={CENTER}
                zoom={4}
                minZoom={2}
                maxBounds={[[180, 180], [-180, -180]]}
                zoomControl={false}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <ZoomControl position="bottomright"/>
                { children }
            </MapContainer>
        </>
    );
}

export default Map;

