import React from "react";
import { Routes, Route } from "react-router-dom";
import { Home } from "./pages/home/Home";
import { Records } from "./pages/records/Records";


const App = () => {
    return (
        <Routes>
            <Route path="/" element={<Home/>}/>
            <Route path="/records" element={<Records/>}/>
        </Routes>
    );
}

export default App;
