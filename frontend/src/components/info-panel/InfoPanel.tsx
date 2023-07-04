import { XLg, ArrowBarLeft, ArrowBarRight } from "react-bootstrap-icons";
import L from "leaflet";
import { useState } from "react";
import CSS from 'csstype';
import "./style.css";
import { Spinner } from "react-bootstrap";

const ICON_SIZE = 20;

type InfoProps = {
    className?: string
    style?: CSS.Properties
    title?: string
    onClose?: () => void
    children?: JSX.Element | JSX.Element[]
}

type InfoChildrenProps = {
    isLoading?: boolean
    className?: string
    style?: CSS.Properties
    children?: JSX.Element | JSX.Element[]
}

const InfoPanel = ({ className, style, title, onClose, children }: InfoProps) => {
    // variable for setting collapsed status (invoking animation)
    const [collapsed, setCollapsed] = useState(false);

    const handleCollapse = () => {
        setCollapsed(!collapsed);
    }

    return (
        <>
            <div
                className={className?.concat(
                    " position-absolute bg-dark bg-opacity-75 px-2 py-2 text-white m-2 rounded info"
                )}
                style={{zIndex: 999, cursor: "default", ...style}}
                // there is need to disable event propagation (otherwise the events will be applied to the map) 
                onMouseDown={(e) => {
                    L.DomEvent.on(e.currentTarget, 'mousedown', L.DomEvent.stopPropagation);
                }}
                onTouchStart={(e) => {
                    L.DomEvent.on(e.currentTarget, 'touchmove', L.DomEvent.stopPropagation);
                }}
                onMouseEnter={(e) => {
                    L.DomEvent.on(e.currentTarget, 'wheel', L.DomEvent.stopPropagation);
                }}
            >
                {
                    collapsed ? (
                        <ArrowBarRight className="clickable" size={ICON_SIZE} onClick={handleCollapse}/>
                        ) : (
                            <>
                            <div className="d-flex mb-2">
                                <ArrowBarLeft
                                    className="clickable"
                                    size={ICON_SIZE}
                                    onClick={handleCollapse}/>
                                <h5 className="m-0">{title}</h5>
                                <XLg
                                    size={ICON_SIZE}
                                    className="ms-auto clickable"
                                    onClick={onClose}
                                />
                            </div>
                        </>
                    )
                }
                <div className={`box ${collapsed ? 'collapsed' : ''}`}>
                    <div className="row w-100 m-1">
                            { children }
                    </div>
                </div>
            </div>
        </>
    );
}

InfoPanel.Title = ({ className, style, children }: InfoChildrenProps) => {
    return (
        <>
            <div
                className={className}
                style={style}
            >
                {children}
            </div>
        </>
    );
}


InfoPanel.Body = ({ isLoading, className, style, children }: InfoChildrenProps) => {
    return (
        <>
            <div className={"mt-2 info-content ".concat(className)} style={style}>
                {
                    isLoading ? (
                        <Spinner className="position-absolute top-50 start-50" animation="border"/>
                    ) : (
                        children
                    )
                }
            </div>
        </>
    );
}

export default InfoPanel;
