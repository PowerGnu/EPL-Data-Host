from flask import Flask, jsonify, request
import json
import os

# Initialize Flask app
app = Flask(__name__)

# Path to the JSON data
DATA_FOLDER = r"C:/Users/ferga/OneDrive/Modular Framework/EPL_Data"

# Helper function to load JSON data
def load_json(file_name):
    try:
        with open(os.path.join(DATA_FOLDER, file_name), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": f"File {file_name} not found."}

# Route: Fetch all teams
@app.route('/teams', methods=['GET'])
def get_teams():
    data = load_json("EPL_Teams_2024.json")
    return jsonify(data)

# Route: Fetch players
@app.route('/players', methods=['GET'])
def get_players():
    team = request.args.get("team")  # Filter by team
    data = load_json("EPL_Players_2024.json")
    if team:
        filtered_data = [player for player in data if player.get("team_title") == team]
        return jsonify(filtered_data)
    return jsonify(data)

# Route: Fetch all players
@app.route('/all_players', methods=['GET'])
def get_all_players():
    data = load_json("EPL_AllPlayers_2024.json")
    return jsonify(data)

# Route: Fetch matches
@app.route('/matches', methods=['GET'])
def get_matches():
    team = request.args.get("team")  # Filter by team
    date = request.args.get("date")  # Filter by date
    data = load_json("EPL_Matches_2024.json")
    filtered_data = [
        match for match in data
        if (not team or team in (match.get("h_team"), match.get("a_team"))) and
           (not date or match.get("datetime", "").startswith(date))
    ]
    return jsonify(filtered_data)

# Home route
@app.route('/')
def home():
    return "Welcome to the EPL Data API! Use /teams, /players, /all_players, or /matches to access data."

if __name__ == '__main__':
    # Run app on port 5000 for testing
    app.run(host="0.0.0.0", port=5000)
