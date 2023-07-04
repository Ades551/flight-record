import { Search } from "react-bootstrap-icons";
import { useState } from "react";
import "./style.css"

type Props = {
    onClick?: () => void
}

export const SearchIcon = ({onClick}: Props) => {
    const [clicked, setClicked] = useState(false);

    const handleClick = () => {
        setClicked(!clicked);
        onClick();
    }
    
    return (
        <>
            <div
                className={`search-icon ${clicked ? "clicked": ""}`}
                onClick={handleClick}
            >
                <Search
                    className="m-2"
                    size={16}
                />
            </div>
        </>
    );
}
