from flask import Flask, jsonify, request
import os
import json

app = Flask(__name__)

# Adding a comment to force redeployment
# Define JSON file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYERS_FILE = os.path.join(BASE_DIR, "EPL_Players_2024.json")
ALL_PLAYERS_FILE = os.path.join(BASE_DIR, "EPL_AllPlayers_2024.json")
MATCHES_FILE = os.path.join(BASE_DIR, "EPL_Matches_2024.json")
TEAMS_FILE = os.path.join(BASE_DIR, "EPL_Teams_2024.json")

# Helper function to load JSON data
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    return "Welcome to the EPL Data API! Use /players, /all_players, /matches, or /teams to access data."

@app.route("/players", methods=["GET"])
def get_players():
    team = request.args.get("team")
    data = load_json(PLAYERS_FILE)
    if team:
        data = [player for player in data if player.get("team_title") == team]
    return jsonify(data)

@app.route("/all_players", methods=["GET"])
def get_all_players():
    return jsonify(load_json(ALL_PLAYERS_FILE))

@app.route("/matches", methods=["GET"])
def get_matches():
    return jsonify(load_json(MATCHES_FILE))

@app.route("/teams", methods=["GET"])
def get_teams():
    return jsonify(load_json(TEAMS_FILE))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
