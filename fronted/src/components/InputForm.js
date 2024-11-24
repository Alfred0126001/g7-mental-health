import React, { useState } from 'react';
import axios from 'axios';

function InputForm({ onResults }) {
    const [population, setPopulation] = useState(800000);
    const [initialState, setInitialState] = useState({ healthy: 780000, mild: 15000, moderate: 3000, severe: 2000 });
    const [scenario, setScenario] = useState("peace");
    const [simTime, setSimTime] = useState(365);

    const handleSubmit = async () => {
        const response = await axios.post('/simulate', {
            population,
            initial_state: Object.values(initialState),
            scenario,
            sim_time: simTime
        });
        onResults(response.data);
    };

    return (
        <form>
            <label>
                Population:
                <input type="number" value={population} onChange={(e) => setPopulation(e.target.value)} />
            </label>
            <button type="button" onClick={handleSubmit}>Run Simulation</button>
        </form>
    );
}

export default InputForm;