import { flight } from "./flights"

interface cluster {
    cluster: number,
    position: [number, number],
}

export interface flightCluster extends cluster {
    data: flight[]
}

export interface boundries {
    north: number,
    east: number,
    south: number, 
    west: number
}
