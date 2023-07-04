import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker, TimeField, LocalizationProvider } from '@mui/x-date-pickers';
import { useEffect, useState } from 'react';
import { Dayjs } from 'dayjs';

const design = {
    '& .MuiOutlinedInput-notchedOutline': {
        'borderColor': 'white'
    },
    'svg': { 'color': 'white' },
    'input': { 'color': 'white' },
    'label': { 'color': 'white' },
    'width': '100%'
}

type DateTimePickerProps = {
    onChange: (
        date: Dayjs,
        start: Dayjs,
        end: Dayjs
    ) => void
}

const CustomDateTimePicker = ({ onChange }: DateTimePickerProps ) => {
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedStart, setSelectedStart] = useState(null);
    const [selectedEnd, setSelectedEnd] = useState(null);

    const handleDateChange = (date: Dayjs) => {
        setSelectedDate(date);
    };

    const handleTimeStart = (time: Dayjs) => {
        setSelectedStart(time);
    }
    
    const handleTimeEnd = (time: Dayjs) => {
        setSelectedEnd(time);
    }

    useEffect(() => {
        onChange(selectedDate, selectedStart, selectedEnd);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedDate, selectedStart, selectedEnd]);

    return (
        <>
            <div>
                <div className="row g-3">
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <div className="col-md-4 col-sm-4 col-lg-4">
                            <DatePicker
                                label="Date"
                                value={selectedDate}
                                sx={design}
                                onChange={handleDateChange}
                            />
                        </div>
                        <div className="col-6 col-sm-4 col-md-4 col-lg-4">
                            <TimeField
                                label="From"
                                ampm={false}
                                value={selectedStart}
                                sx={design}
                                onChange={handleTimeStart}
                            />
                        </div>
                        <div className="col-6 col-sm-4 col-md-4 col-lg-4">
                            <TimeField
                                label="To"
                                ampm={false}
                                value={selectedEnd}
                                sx={design}
                                onChange={handleTimeEnd}
                            />
                        </div>
                    </LocalizationProvider>
                </div>
            </div>
        </>
    );
}

export default CustomDateTimePicker;
