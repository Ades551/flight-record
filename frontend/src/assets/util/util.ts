import { useEffect, useRef } from 'react';
import { boundries } from './types';
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone';
import dayjs, { Dayjs } from "dayjs";

dayjs.extend(utc)
dayjs.extend(timezone);
const userZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

export const CENTER: [number, number] = [50.4, 14.25];
export const BASIC_ZOOM = 6;

export const useInterval = (callback: () => void, delay: number) => {
    const savedCallback = useRef(null);

    // Remember the latest callback.
    useEffect(() => {
        savedCallback.current = callback;
    }, [callback]);

    // Set up the interval.
    useEffect(() => {
        const tick = () => {
            savedCallback.current();
        }
        if (delay !== null) {
            let id = setInterval(tick, delay);
            return () => clearInterval(id);
        }
    }, [delay]);
}

/**
 * Get position in boundries.
 * @param position position
 * @param boundries boudries
 * @returns true if position is in the boudries else false
 */
export const positionInBoundries = (position: [number, number], boundries: boundries) =>  {    
    let isInLat = boundries.north >= position[0] && position[0] >= boundries.south;
    let isInLong = boundries.west <= position[1] && position[1] <= boundries.east;
    return ( isInLat && isInLong );
}

/**
 * Get date time.
 * @param date date as string or dayjs object
 * @returns datetime within current timezone 
 */
export const getDateTime = (date: Dayjs | string) => {
    return dayjs.utc(date, "YYYY-MM-DD HH:mm:ss UTC")?.tz(userZone).format('YYYY-MM-DD HH:mm:ss');
}

/**
 * ApiRequests
 */
export class ApiRequest {
    url: string;
    method: string;
    ended: boolean;
    private controller: AbortController;

    /**
     * 
     * @param url URL path
     * @param method request mehtod (GET, POST, ...)
     */
    constructor(url: string, method: string) {
        this.url = url;
        this.method = method;
        this.ended = true;
        this.controller = new AbortController();
    }
    
    request(callback: (response: any) => void, onFinished?: () => void) {
        fetch(this.url, {
            method: this.method,
            signal: this.controller.signal
        })
        .then(response => response.json())
        .then(response => {
            callback(response);
            this.ended = true;
            if( onFinished ) { onFinished(); }
        })
    }

    abort() {
        this.controller.abort();
    }
}
