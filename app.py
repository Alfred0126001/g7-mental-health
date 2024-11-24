from flask import Flask, request, jsonify
import simulation  # Import simulation.py as a module
import numpy as np

app = Flask(__name__)

# Default simulation parameters
DEFAULT_PARAMS = {
    "population": 828000,
    "initial_state": [800000, 20000, 5000, 3000],
    "scenario": "peace",
    "sim_time": 365
}

@app.route("/", methods=["GET"])
def home():
    """Welcome endpoint to check if the API is running."""
    return jsonify({"message": "Welcome to the Mental Health Simulation API!"})

@app.route("/simulate", methods=["POST"])
def simulate():
    """
    Accepts JSON input for simulation parameters and returns simulation results.
    """
    try:
        # Get input parameters from request
        params = request.get_json()

        # Use default parameters if not provided
        population = params.get("population", DEFAULT_PARAMS["population"])
        initial_state = params.get("initial_state", DEFAULT_PARAMS["initial_state"])
        scenario = params.get("scenario", DEFAULT_PARAMS["scenario"])
        sim_time = params.get("sim_time", DEFAULT_PARAMS["sim_time"])

        # Validate input parameters
        if not isinstance(population, int) or population <= 0:
            return jsonify({"error": "Invalid population size."}), 400

        if not (isinstance(initial_state, list) and len(initial_state) == 4):
            return jsonify({"error": "Initial state must be a list of four numbers."}), 400

        if scenario not in ["peace", "crisis"]:
            return jsonify({"error": "Invalid scenario. Choose 'peace' or 'crisis'."}), 400

        if not isinstance(sim_time, int) or sim_time <= 0:
            return jsonify({"error": "Simulation time must be a positive integer."}), 400

        # Set parameters for simulation.py
        simulation.healthy_population = initial_state[0]
        simulation.mild_cases = initial_state[1]
        simulation.moderate_cases = initial_state[2]
        simulation.severe_cases = initial_state[3]
        simulation.scenario = scenario
        simulation.SIM_TIME = sim_time

        # Run the simulation (using the simulation.py logic)
        exec(open("simulation.py").read())

        # Collect results (final states and key statistics)
        results = {
            "final_state": {
                "healthy": simulation.S[0],
                "mild": simulation.S[1],
                "moderate": simulation.S[2],
                "severe": simulation.S[3]
            },
            "average_waiting_times": {
                "mild": simulation.avg_waiting_time_mild,
                "moderate": simulation.avg_waiting_time_moderate,
                "severe": simulation.avg_waiting_time_severe
            },
            "average_queue_lengths": {
                "mild": simulation.avg_queue_length_mild,
                "moderate": simulation.avg_queue_length_moderate,
                "severe": simulation.avg_queue_length_severe
            },
            "monthly_resource_allocations": simulation.monthly_allocations.to_dict(orient="records")
        }

        return jsonify(results)

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
