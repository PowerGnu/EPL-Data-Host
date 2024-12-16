"""
EPL Data API - Version 1.3
Features:
1. On-Demand JSON Loading for Scalability
2. Centralised Filtering Logic for Reusability
3. Enhanced Documentation
4. Input Validation for Security
5. JSON Schema Validation for Data Integrity
"""

import os
import json
import logging
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jsonschema import validate, ValidationError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    headers_enabled=True  # Enable rate limit headers
)

# JSON Data File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = {
    "players": os.path.join(BASE_DIR, "EPL_Players_2024.json"),
    "all_players": os.path.join(BASE_DIR, "EPL_AllPlayers_2024.json"),
    "matches": os.path.join(BASE_DIR, "EPL_Matches_2024.json"),
    "teams": os.path.join(BASE_DIR, "EPL_Teams_2024.json"),
}

# JSON Schemas for Validation
def generate_properties(key):
    if key in ["all_players", "players"]:
        return {
            "player_id": {"type": "integer"},
            "player_name": {"type": "string"},
            "team_title": {"type": "string"},
            "position": {"type": "string"}
        }
    elif key == "teams":
        return {
            "team_id": {"type": "integer"},
            "team_name": {"type": "string"},
            "stadium": {"type": "string"},
            "manager": {"type": "string"}
        }
    elif key == "matches":
        return {
            "datetime": {"type": "string"},
            "team_a": {"type": "string"},
            "team_b": {"type": "string"},
            "score": {"type": "string"}
        }

def generate_properties(key):
    """
    Dynamically generate properties based on the key.
    """
    if key in ["all_players", "players"]:
        return {
            "player_id": {"type": "integer"},
            "player_name": {"type": "string"},
            "team_title": {"type": "string"},
            "position": {"type": "string"}
        }
    elif key == "teams":
        return {
            "team_id": {"type": "integer"},
            "team_name": {"type": "string"},
            "stadium": {"type": "string"},
            "manager": {"type": "string"}
        }
    elif key == "matches":
        return {
            "datetime": {"type": "string"},
            "team_a": {"type": "string"},
            "team_b": {"type": "string"},
            "score": {"type": "string"}
        }
    else:
        return {}

def generate_required(key):
    """
    Dynamically generate the required fields based on the key.
    """
    if key in ["all_players", "players"]:
        return ["player_id", "player_name", "team_title", "position"]
    elif key == "teams":
        return ["team_id", "team_name", "stadium", "manager"]
    elif key == "matches":
        return ["datetime", "team_a", "team_b"]
    else:
        return []

# Assuming DATA_FILES is defined as a dictionary of data file names and keys
DATA_FILES = {
    "all_players": "all_players.json",
    "players": "players.json",
    "teams": "teams.json",
    "matches": "matches.json"
}

SCHEMAS = {
    key: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": generate_properties(key),
            "required": generate_required(key)
        }
    }
    for key in DATA_FILES.keys()
}


# Utility: Load and Validate JSON Data
from functools import lru_cache

@lru_cache(maxsize=10)
def load_json_file(file_path, schema=None):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            if schema:
                validate(instance=data, schema=schema)
            return data
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {file_path}")
        return []
    except ValidationError as e:
        logging.error(f"Schema validation error for file {file_path}: {e.message}")
        return []

# Utility: Filter Data by Key
from datetime import datetime

def filter_by_key(data_list, key, value):
    """
    Filter a list of dictionaries by a specific key-value pair.
    Args:
        data_list (list): List of dictionaries to filter.
        key (str): Key to filter by.
        value (str): Value to match (case-insensitive).
    Returns:
        list: Filtered list of dictionaries.
    """
    return [item for item in data_list if item.get(key, "").lower() == value.lower()]

def filter_by_date(data_list, date):
    """
    Filter a list of dictionaries by a specific date.
    Args:
        data_list (list): List of dictionaries to filter.
        date (str): Target date in YYYY-MM-DD format.
    Returns:
        list: Filtered list of dictionaries matching the date, or error message for invalid date.
    """
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d')
        validated_items = [
            item for item in data_list
            if datetime.strptime(item["datetime"], '%Y-%m-%dT%H:%M:%S').date() == target_date.date()
        ]
        validate(instance=validated_items, schema=SCHEMAS.get("matches"))
        return validated_items
    except (ValueError, ValidationError) as e:
        error_message = "Invalid date format. Expected YYYY-MM-DD." if isinstance(e, ValueError) else f"Schema validation failed after filtering: {e.message}"
        return jsonify({"error": error_message}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400
    except ValidationError as e:
        return jsonify({"error": f"Schema validation failed after filtering: {e.message}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400
    except ValidationError as e:
        return jsonify({"error": f"Schema validation failed after filtering: {e.message}"}), 400
    """
    Filter a list of dictionaries by a specific key-value pair.
    Args:
        data_list (list): List of dictionaries to filter.
        key (str): Key to filter by.
        value (str): Value to match (case-insensitive).
    Returns:
        list: Filtered list of dictionaries.
    """
    return [item for item in data_list if item.get(key, "").lower() == value.lower()]

# Utility: Pagination Logic
def paginate(data_list):
    """
    Paginate a list of data based on query parameters.
    Logs pagination details for debugging.
    """
    if not data_list:
        logging.info("Pagination request returned no results.")
        return jsonify({"message": "No results available for the given parameters."}), 404

    try:
        page = max(1, int(request.args.get('page', 1)))  # Ensure positive integer
        per_page = min(100, max(1, int(request.args.get('per_page', 50))))  # Enforce limits: 1 <= per_page <= 100
    except ValueError:
        logging.warning("Invalid pagination parameters provided.")
        return jsonify({"error": "Invalid pagination parameters. Both must be positive integers."}), 400

    start = (page - 1) * per_page
    end = start + per_page

    returned_items = len(data_list[start:end])
    logging.info(f"Pagination: page={page}, per_page={per_page}, total_items={len(data_list)}, returned_items={returned_items}")
    return data_list[start:end]
    return data_list
    if not data_list:
        return jsonify({"message": "No results available for the given parameters."}), 404
    page = request.args.get('page', 1)
    try:
        page = max(1, int(page))  # Ensure page is a positive integer
    except ValueError:
        return jsonify({"error": "Invalid page parameter. Must be a positive integer."}), 400  # Default to page 1
    per_page = request.args.get('per_page', 50)
    try:
        per_page = min(100, max(1, int(per_page)))  # Enforce limits: 1 <= per_page <= 100
    except ValueError:
        return jsonify({"error": "Invalid per_page parameter. Must be a positive integer."}), 400  # Default to 50 items per page
    start = (page - 1) * per_page
    end = start + per_page
    return data_list[start:end]

@app.route('/')
def home():
    """
    Welcome Endpoint
    ---
    This endpoint provides an overview of available API routes and their query parameters, along with rate-limiting information.
    """
    return jsonify({
        "message": "Welcome to the EPL Data API!",
        "rate_limits": {
            "/players": "50 requests per hour",
            "/all_players": "200 requests per hour",
            "/matches": "100 requests per hour",
            "/teams": "100 requests per hour"
        },
        "endpoints": {
            "/players": "Get players data. Query params: team, page, per_page",
            "/all_players": "Get all players data. Query params: page, per_page",
            "/matches": "Get matches data. Query params: date, page, per_page",
            "/teams": "Get teams data. Query params: page, per_page"
        }
    })

@limiter.limit("50 per hour")
@app.route('/players', methods=['GET'])
def get_players():
    players = load_json_file(DATA_FILES["players"], schema=SCHEMAS.get("players"))
    team = request.args.get('team')
    if team and not team.isalpha():  # Validate team name contains only letters
        return jsonify({"error": "Invalid team parameter. Must contain only alphabetic characters."}), 400

    if not players:
        return jsonify({"error": "Player data not available"}), 500

    if team:
        players = filter_by_key(players, "team_title", team)
    return jsonify(paginate(players))

@limiter.limit("200 per hour")
@app.route('/all_players', methods=['GET'])
def get_all_players():
    all_players = load_json_file(DATA_FILES["all_players"], schema=SCHEMAS.get("all_players"))

    if not all_players:
        return jsonify({"error": "All players data not available"}), 500

    return jsonify(paginate(all_players))

@limiter.limit("100 per hour")
@app.route('/matches', methods=['GET'])
def get_matches():
    matches = load_json_file(DATA_FILES["matches"], schema=SCHEMAS.get("matches"))
    date = request.args.get('date')

    if not matches:
        return jsonify({"error": "Match data not available"}), 500

    if date:
        matches = filter_by_date(matches, date)
    return jsonify(paginate(matches))

@limiter.limit("100 per hour")
@app.route('/teams', methods=['GET'])
def get_teams():
    teams = load_json_file(DATA_FILES["teams"], schema=SCHEMAS.get("teams"))

    if not teams:
        return jsonify({"error": "Team data not available"}), 500

    return jsonify(paginate(teams))

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
    except ValueError:
        logging.error("Invalid port configuration. Please set PORT to a valid integer.")
        port = 5000  # Default to 5000
    logging.info(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)
