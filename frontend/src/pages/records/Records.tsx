import { useEffect, useState } from "react";
import NavBar from "../../components/navbar/NavBar";
import { flightTableInfo, getFlightRecords, getFlightsWithRecord, waveRecord } from "../../assets/util/flights";
import WaveForm from "../../components/waveform/WaveForm";
import { Button, Table, Modal } from "react-bootstrap";
import {
    DatatableWrapper,
    Filter,
    Pagination,
    PaginationOptions,
    TableBody,
    TableHeader,
} from "react-bs-datatable";
import { getDateTime } from "../../assets/util/util";
import "./style.css";

export const Records = () => {
    const [tableInfo, setTableInfo] = useState<flightTableInfo[]>(null);
    const [waveForms, setWaveForms] = useState<waveRecord[]>(null);
    const [showModal, setShowModal] = useState(false);
    const [index, setIndex] = useState<number>(null);

    // table headers
    const HEADERS = [
        {
            prop: "callsign",
            title: "Callsign",
            isFilterable: true
        },
        {
          prop: "airports",
          title: "Airports",
          isFilterable: true
        },
        {
          prop: "date",
          title: "Last record",
          isSortable: true
        },
        { // create button in the cell
          prop: "button",
          cell: (row) => (
            <Button
                variant="outline-primary"
                size="sm"
                onClick={() => { // get flight recordings
                    if (row.id !== index) {
                        setWaveForms(null);
                        getFlightRecords(row.id).request((response) => setWaveForms(response.records));
                        setIndex(row.id);
                    }
                    setShowModal(true);
                }}
            >
                Show records
            </Button>
          )
        },
        {
            prop: "id",
            thProps: {
                style: {"display": "none"}
            },
            cellProps: {
                style: {"display": "none"}
            }
        }
    ]

    useEffect(() => {
        // reuest flights with recordings
        getFlightsWithRecord().request((response) => {
            // for data modification
            let updated_data: flightTableInfo[] = response.table.map(flight => {
                return { ...flight, 
                        date: getDateTime(flight.date), // correct datetime
                        airports: flight.airports.join(', ') // 'PRG, BRN' in case of multiple detections
                    };
            });
            // set table info
            setTableInfo(updated_data);
        })
    }, []);

    return (
        <>
            <div className="vw-100">
                <NavBar/>
                <Modal
                    scrollable={true}
                    onHide={() => setShowModal(false)}
                    show={showModal}
                    aria-labelledby="contained-modal-title-vcenter"
                    centered
                    size="lg"
                >
                    <Modal.Header closeButton>
                        <Modal.Title id="contained-modal-title-vcenter">
                            Records
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>                            
                        {
                            waveForms?.map((wave) => (
                                <WaveForm
                                    key={wave.mp3}
                                    audio_url={wave.mp3}
                                    transcript={wave.transcript}
                                />
                            ))
                        }
                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={() => setShowModal(false)}>Close</Button>
                    </Modal.Footer>
                </Modal>
                <div className="container my-2">
                    {
                        tableInfo ? 
                        (
                            <DatatableWrapper
                                body={tableInfo}
                                headers={HEADERS}
                                paginationOptionsProps={{
                                    initialState: {
                                        rowsPerPage: 25,
                                        options: [10, 25, 50],
                                    }
                                }}
                                >
                                <div className="row g-3 justify-content-between">
                                    <div className="col-9 col-lg-3">
                                        <Filter placeholder="Filter text..."/>
                                    </div>
                                    <div className="col-3 col-lg-1">
                                        <PaginationOptions/>
                                    </div>
                                    <div className="col-lg-3">
                                        <Pagination labels={{
                                            firstPage: "<<",
                                            lastPage: ">>",
                                            nextPage: ">",
                                            prevPage: "<"
                                        }}/>
                                    </div>
                                </div>
                                <Table>
                                    <TableHeader/>
                                    <TableBody/>
                                </Table>
                            </DatatableWrapper>
                        ) : 
                        (null)
                    }
                </div>
            </div>
        </>
    );
}
