from flask import Flask, request, jsonify
import os
import json
from jsonschema import validate, ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask app
app = Flask(__name__)

# Paths to JSON files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = {
    "players": os.path.join(BASE_DIR, "EPL_Players_2024.json"),
    "teams": os.path.join(BASE_DIR, "EPL_Teams_2024.json"),
    "matches": os.path.join(BASE_DIR, "EPL_Matches_2024.json"),
}

# Load JSON utility
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to load file {file_path}: {str(e)}"}), 500

# Query handlers
def handle_team_query(payload):
    try:
        # Extract name and metrics from the payload
        name = payload.get("name")
        metrics = payload.get("metrics")
        
        logging.debug(f"Received team query: name={name}, metrics={metrics}")

        # Load the teams dataset
        teams = load_json_file(DATA_FILES["teams"])
        logging.debug(f"Loaded teams data: {teams}")

        # Match the team by the 'title' field
        team = next((t for t in teams.values() if t["title"].lower() == name.lower()), None)
        logging.debug(f"Matched team: {team}")

        if not team:
            return jsonify({"error": f"Team '{name}' not found"}), 404

        # Filter team data by metrics, if provided
        if metrics:
            metrics = [m.lower() for m in metrics]  # Normalize metric keys
            filtered_team = {k: v for k, v in team.items() if k.lower() in metrics}
            if not filtered_team:
                logging.warning(f"No matching metrics found. Returning full team data.")
                return jsonify(team)
            return jsonify(filtered_team)

        return jsonify(team)

    except Exception as e:
        logging.error(f"Error in handle_team_query: {e}")
        return jsonify({"error": "Internal server error"}), 500



def handle_match_query(payload):
    date = payload.get("date")

    matches = load_json_file(DATA_FILES["matches"])

    if not matches:
        return jsonify({"error": "Match data not available"}), 500

    # Filter by date if provided
    if date:
        matches = [m for m in matches if m["datetime"].startswith(date)]
        if not matches:
            return jsonify({"error": f"No matches found for date {date}"}), 404

    # Format response
    formatted_matches = [
        {
            "match_id": m["id"],
            "date": m["datetime"],
            "home_team": m["h"]["title"],
            "away_team": m["a"]["title"],
            "xG_home": m["xG"]["h"],
            "xG_away": m["xG"]["a"],
            "goals_home": m["goals"]["h"],
            "goals_away": m["goals"]["a"]
        }
        for m in matches
    ]

    return jsonify(formatted_matches)

def handle_combined_query(payload):
    try:
        team_name = payload.get("team")
        player_names = payload.get("players")
        metrics = payload.get("metrics")

        logging.debug(f"Received combined query: team={team_name}, players={player_names}, metrics={metrics}")

        # Load datasets
        teams_data = load_json_file(DATA_FILES["teams"])
        players_data = load_json_file(DATA_FILES["players"])
        logging.debug(f"Loaded teams data: {teams_data}")
        logging.debug(f"Loaded players data: {players_data}")

        # Match the team
        team = next((t for t in teams_data.values() if t["title"].lower() == team_name.lower()), None)
        if not team:
            return jsonify({"error": f"Team '{team_name}' not found"}), 404

        # Filter player data
        selected_players = [
            p for p in players_data if p["player_name"].lower() in [name.lower() for name in player_names]
        ]
        if not selected_players:
            return jsonify({"error": f"No players found for the given names: {player_names}"}), 404

        # Filter metrics if provided
        if metrics:
            metrics = [m.lower() for m in metrics]
            team_metrics = {k: v for k, v in team.items() if k.lower() in metrics}
            player_metrics = [
                {k: v for k, v in player.items() if k.lower() in metrics} for player in selected_players
            ]
        else:
            team_metrics = team
            player_metrics = selected_players

        # Combine the response
        combined_response = {
            "team": {"name": team["title"], "metrics": team_metrics},
            "players": player_metrics
        }

        return jsonify(combined_response)

    except Exception as e:
        logging.error(f"Error in handle_combined_query: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Unified query endpoint
@app.route('/query', methods=['POST'])
def query():
    payload = request.get_json()
    query_type = payload.get("type")

    if not query_type:
        return jsonify({"error": "Query type is required"}), 400

    if query_type == "player":
        return handle_player_query(payload)
    elif query_type == "team":
        return handle_team_query(payload)
    elif query_type == "match":
        return handle_match_query(payload)
    elif query_type == "combined":
        return handle_combined_query(payload)
    else:
        return jsonify({"error": "Invalid query type"}), 400

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
