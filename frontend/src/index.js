import React from "react";
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'leaflet/dist/leaflet.css';
import "./assets/css/leaflet.css";
import "./assets/css/main.css";

import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <BrowserRouter>
        <App/>
    </BrowserRouter>
);
