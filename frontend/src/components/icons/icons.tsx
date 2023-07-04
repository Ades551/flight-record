import { divIcon } from "leaflet";
import { Soundwave, AirplaneFill, FlagFill, ArrowLeft, ArrowRight } from "react-bootstrap-icons";
import { renderToStaticMarkup } from 'react-dom/server';
import { Spinner } from "react-bootstrap";
import CSS from 'csstype';
import "./style.css";

/**
 * 
 * @returns element of sound icon
 */
export const soundIcon = () => {
    return divIcon({
        iconAnchor: [16, 16],
        html: renderToStaticMarkup(
            <div className="position-absolute border rounded-circle border-1 border-secondary sound-icon-background">
                <Soundwave className="p-1 sound-icon" size={32}/>
            </div>
        )
    })
}

/**
 * 
 * @param color color of the icon
 * @returns element of the plane icon
 */
export const planeIcon = (color?: string) => {
    return divIcon({
        iconAnchor: [10, 10],
        html: renderToStaticMarkup(
            <AirplaneFill
                color={color}
                className="custom-flight-icon"
                size={20}/>
        )
    });
}

/**
 * 
 * @param count number displayed under the cluster icon
 * @param color color of the icon
 * @returns element of the cluster icon
 */
export const clusterIcon = (count: number, color?: string) => {
    return divIcon({
        iconAnchor: [10, 10],
        html: renderToStaticMarkup(
            <div>
                <AirplaneFill
                    color={color}
                    size={20}
                    className="custom-flight-icon"
                    style={{
                        transform: "rotate(45deg)"
                    }}
                />
                <p>{count}</p>
            </div>
        )
    });
}

/**
 * 
 * @param clicked icon clicked status
 * @param loading icon loading status
 * @returns element of the airport icon
 */
export const AirportIcon = (clicked?: boolean, loading?: boolean) => {
    return divIcon({
        iconAnchor: [10, 10],
        html: renderToStaticMarkup(
            <div className={"flag-icon ".concat(clicked ? "flag-clicked": "")}>
                <FlagFill className="m-1" size={18}/>
                {
                    clicked && loading ? (
                        <Spinner className="loading" size="sm" animation="border"/>
                        ) : (
                            null
                        )
                }
            </div>
        )
    });
}

type ArrowProps = {
    side: string
    onClick: () => void
    className?: string
    style?: CSS.Properties
}

export const ArrowIcon = ({side, onClick, className, style}: ArrowProps) => {
    return (
        <>
            <div onClick={onClick} className={`${className} custom-arrow`} style={style}>
                {side === "left" ? (
                    <ArrowLeft size={24}/>
                ) : (
                    <ArrowRight size={24}/>
                )}
            </div>
        </>
    );
}
