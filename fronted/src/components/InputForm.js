import React, { useState } from "react";

const API_URL = "https://g7-mentalhealth-45cfa93773b9.herokuapp.com/"; // Replace with your Heroku backend URL

function InputForm() {
  const [population, setPopulation] = useState(828000);
  const [initialState, setInitialState] = useState("800000,20000,5000,3000");
  const [scenario, setScenario] = useState("peace");
  const [simTime, setSimTime] = useState(365);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setError(null);

    const initialStateArray = initialState.split(",").map(Number);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          population,
          initial_state: initialStateArray,
          scenario,
          sim_time: simTime,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Total Population:
          <input
            type="number"
            value={population}
            onChange={(e) => setPopulation(Number(e.target.value))}
            required
          />
        </label>
        <br />
        <label>
          Initial State (Healthy, Mild, Moderate, Severe):
          <input
            type="text"
            value={initialState}
            onChange={(e) => setInitialState(e.target.value)}
            required
          />
        </label>
        <br />
        <label>
          Scenario:
          <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
            <option value="peace">Peace</option>
            <option value="crisis">Crisis</option>
          </select>
        </label>
        <br />
        <label>
          Simulation Time (days):
          <input
            type="number"
            value={simTime}
            onChange={(e) => setSimTime(Number(e.target.value))}
            required
          />
        </label>
        <br />
        <button type="submit">Run Simulation</button>
      </form>
      {result && (
        <div>
          <h2>Simulation Results</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default InputForm;
