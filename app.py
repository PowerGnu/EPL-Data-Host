import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# Load JSON data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = {
    "players": os.path.join(BASE_DIR, "EPL_Players_2024.json"),
    "all_players": os.path.join(BASE_DIR, "EPL_AllPlayers_2024.json"),
    "matches": os.path.join(BASE_DIR, "EPL_Matches_2024.json"),
    "teams": os.path.join(BASE_DIR, "EPL_Teams_2024.json"),
}

data = {}
for key, file_path in DATA_FILES.items():
    try:
        with open(file_path, "r") as f:
            data[key] = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. {key} endpoint will not work.")

@app.route('/')
def home():
    return "Welcome to the EPL Data API! Use /players, /all_players, /matches, or /teams to access data."

@app.route('/list-files', methods=['GET'])
def list_files():
    """Diagnostic route to list all files in the deployment directory."""
    return jsonify(os.listdir(BASE_DIR))

@app.route('/players', methods=['GET'])
def get_players():
    team = request.args.get('team')
    if "players" not in data:
        return jsonify({"error": "Player data not available"}), 500

    if team:
        filtered_players = [player for player in data["players"] if player["team_title"].lower() == team.lower()]
        return jsonify(filtered_players)

    return jsonify(data["players"])

@app.route('/all_players', methods=['GET'])
def get_all_players():
    if "all_players" not in data:
        return jsonify({"error": "All players data not available"}), 500
    return jsonify(data["all_players"])

@app.route('/matches', methods=['GET'])
def get_matches():
    date = request.args.get('date')
    if "matches" not in data:
        return jsonify({"error": "Match data not available"}), 500

    if date:
        filtered_matches = [match for match in data["matches"] if match["datetime"].startswith(date)]
        return jsonify(filtered_matches)

    return jsonify(data["matches"])

@app.route('/teams', methods=['GET'])
def get_teams():
    if "teams" not in data:
        return jsonify({"error": "Team data not available"}), 500
    return jsonify(data["teams"])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Starting Flask app with registered routes:")
    print(app.url_map)  # Logs all registered routes
    app.run(host='0.0.0.0', port=port)
