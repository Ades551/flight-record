import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import CursorPlugin from 'wavesurfer.js/src/plugin/cursor';
import RegionsPlugin from 'wavesurfer.js/src/plugin/regions';
import { Play, Stop } from 'react-bootstrap-icons';
import { transcript } from '../../assets/util/flights';
import { Spinner, Fade, Button } from 'react-bootstrap';
import "./style.css";

/**
 * Get generated color.
 * @param alpha color alpha (opacity)
 * @returns rgba color string
 */
const generateColor = (alpha: number) => {
    let r = Math.floor(Math.random() * 255);
    let g = Math.floor(Math.random() * 255);
    let b = Math.floor(Math.random() * 255);
    let a = alpha;
    return `rgba(${r},${g},${b},${a})`;
}

type WaveFormProps = {
    audio_url: string
    transcript: transcript
    autoPlay?: boolean
}

const WaveForm = ({audio_url, transcript, autoPlay = false}: WaveFormProps) => {
    // references for the esential parts of the waveform (needs to be referenced !!)
    const containerRef = useRef(null);
    const waveSurferRef = useRef(null);
    const transcriptsRef = useRef(null);
    // states of the waveform events 
    const [isPlayling, setPlay] = useState(false);
    const [time, setTime] = useState(0);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        if (containerRef.current && waveSurferRef.current === null) {
            const waveSurfer = WaveSurfer.create({
                container: containerRef.current,
                plugins: [
                    CursorPlugin.create({
                        showTime: true,
                        opacity: "1",
                        customShowTimeStyle: {
                            'background-color': '#000',
                            color: '#fff',
                            padding: '2px',
                            'font-size': '10px'
                        }
                    }),
                    RegionsPlugin.create({})
                ]
            });

            waveSurfer.load(audio_url);

            waveSurfer.setHeight(90);

            // create regions based on the transcript
            if (transcript.segments.length > 1) {
                for (const segment of transcript.segments) {
                    waveSurfer.addRegion({
                        start: segment.start,
                        end: segment.end,
                        drag: false,
                        loop: false,
                        resize: false,
                        color: generateColor(0.4),
                    });
                }
            }

            // list of the scroll positions
            let segmentScrollPositions: Array<number> = [];

            waveSurfer.on('ready', () => {
                setLoaded(true);
                waveSurferRef.current = waveSurfer;
                
                // autoplay
                if (autoPlay) { waveSurfer.play(); }
                
                // calculate all scroll positions
                if ( transcriptsRef.current ) {
                    let element = transcriptsRef.current;
                    let scrollHeight = element.scrollHeight - element.clientHeight;
                    transcript.segments.forEach((segment, index) => {
                        segmentScrollPositions.push((scrollHeight / (transcript.segments.length - 1)) * index);                        
                    })
                }
            });
            waveSurfer.on('play', () => setPlay(true));
            waveSurfer.on('pause', () => setPlay(false));
            waveSurfer.on('finish', () => setPlay(false));
            waveSurfer.on('audioprocess', () => {
                let time = waveSurfer.getCurrentTime();
                setTime(time);

                // calculate scroll by the current time of the recording and create scroll animation
                transcript.segments.forEach((segment, index) => {
                    if (transcriptsRef.current) {
                        if (segment.start < time && segment.end > time) {
                            // start time for the segment
                            if (segment.start < time) {
                                // transcript element
                                let element = transcriptsRef.current.children[index];
                                                                
                                let scrollWidth = element.scrollWidth - element.clientWidth;
                                let scrollTo = (scrollWidth / segment.end) * time;
                                element.scrollTo({ left: scrollTo });
                            }
                            transcriptsRef.current.scrollTo({top: segmentScrollPositions[index]});
                        }
                    }
                });
            });
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [audio_url, transcript.segments]);

    return (
        <>
            <div className="row align-items-center g-0">
                <div className='col-3'>
                    <Button
                        className="w-75 px-0 py-2"
                        variant="primary"
                        onClick={() => waveSurferRef.current.playPause()}
                    >
                        {isPlayling ?
                            <>
                                <Stop className="pe-none"/> Stop
                            </>
                            :
                            <>
                                <Play className="pe-none"/> Play
                            </>
                        }

                    </Button>
                </div>
                <div className='col-9'>
                    <div className="position-relative">
                        <div className="position-absolute top-50 start-50 translate-middle">
                            {
                                !loaded ? (
                                    <Spinner animation="border"/>
                                ) : null
                            }
                        </div>
                        <Fade in={loaded}>
                            <div ref={containerRef}/>
                        </Fade>
                    </div>
                </div>
            </div>
            <div ref={transcriptsRef} style={{height: "50px", overflow: "hidden"}}>
                {
                    transcript.segments.map((segment, index) => (
                        <div
                            className={`d-flex align-items-center overflow-hidden transcript ${(segment.start < time && time < segment.end) ? "selected-region bg-warning bg-opacity-50" : ""}`}
                            key={index}
                        >
                            {segment.words.map((word, index) => (
                                <p
                                    className={`${(word.start < time) ? "selected-word" : "non-selected-word"}`}
                                    key={index}
                                >
                                    {word.word}
                                </p>
                            ))}
                        </div>
                    ))
                }
            </div>
        </>
    );
}

export default WaveForm;
