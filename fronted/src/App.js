import React, { useState } from 'react';
import InputForm from './components/InputForm';
import Charts from './components/Charts';

function App() {
    const [results, setResults] = useState(null);

    return (
        <div>
            <h1>Mental Health Simulation</h1>
            <InputForm onResults={setResults} />
            {results && <Charts data={results} />}
        </div>
    );
}

export default App;