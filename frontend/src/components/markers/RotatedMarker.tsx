import { Marker } from 'react-leaflet';
import "leaflet-rotatedmarker";
import { LatLngTuple } from 'leaflet';

type RotatedMarkerProps = {
    position: LatLngTuple,
    angle: number,
    icon: any, 
    onClick?: () => void,
    children?: JSX.Element
}

const RotatedMarker = ({ position, angle, icon, onClick, children }: RotatedMarkerProps) => {
    return (
        <>
            <Marker
                eventHandlers={{ click: () => onClick() }}
                position={position}
                icon={icon}
                // @ts-ignore
                rotationAngle={angle}
            >
                { children }
            </Marker>
        </>
    );
}

export default RotatedMarker;
