from flask import Flask, request, jsonify
from simulation import run_simulation

app = Flask(__name__)

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    population = data.get('population')
    initial_state = data.get('initial_state')
    scenario = data.get('scenario')
    sim_time = data.get('sim_time', 365)

    if not population or not initial_state or not scenario:
        return jsonify({"error": "Missing parameters"}), 400

    results = run_simulation(population, initial_state, scenario, sim_time)
    return jsonify(results)

if __name__ == '__main__':
    app.run()