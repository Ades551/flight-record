import { useMapEvents } from "react-leaflet";
import { boundries } from "../../assets/util/types";

type MapControlProps = {
    onZoomEnd: (zoom: number) => void 
    onMooveEnd: (boundries: boundries) => void 
    children?: JSX.Element | JSX.Element[]
}

export const MapControl = ({onZoomEnd, onMooveEnd, children}: MapControlProps) => {
    const map = useMapEvents({
        moveend: () => {
            onZoomEnd(map.getZoom());
            
            const b = map.getBounds();
            const northEast = b.getNorthEast();
            const southWest = b.getSouthWest();
            
            onMooveEnd(
                {
                    north: northEast.lat,
                    east: northEast.lng,
                    south: southWest.lat, 
                    west: southWest.lng
                }
            );

        },
        zoomend: () => {
            onZoomEnd(map.getZoom());
        }
        // click: () => {
        //     handleOnMapClick();
        // }
    });

    return (
        <>
            { children }
        </>
    );
}
