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
from datetime import datetime
from functools import lru_cache

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Initializing EPL Data API application...")

# Initialize Flask app
app = Flask(__name__)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    headers_enabled=True  # Enable rate limit headers
)
logging.info("Rate limiter configured with default limits: 100 requests per hour.")

# JSON Data File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = {
    "players": os.path.join(BASE_DIR, "EPL_Players_2024.json"),
    "all_players": os.path.join(BASE_DIR, "EPL_AllPlayers_2024.json"),
    "matches": os.path.join(BASE_DIR, "EPL_Matches_2024.json"),
    "teams": os.path.join(BASE_DIR, "EPL_Teams_2024.json"),
}
logging.info(f"Data files configured: {DATA_FILES}")

# JSON Schemas for Validation
def generate_properties(key):
    """Function to generate schema properties dynamically."""
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

# Add logging before the dynamic schema generation
logging.info("Schemas generation starts here.")

# Dictionary comprehension to dynamically generate schemas
SCHEMAS = {
    key: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": generate_properties(key),
            "required": list(generate_properties(key).keys())
        }
    }
    for key in DATA_FILES.keys()
}

# Logging after schema generation
logging.info("JSON schemas for validation have been generated.")

# Manually add non-dynamic schemas
SCHEMAS.update({
    "all_players": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "player_id": {"type": "integer"},
                "player_name": {"type": "string"},
                "team_title": {"type": "string"},
                "position": {"type": "string"}
            },
            "required": ["player_id", "player_name", "team_title", "position"]
        }
    },
    "teams": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "team_id": {"type": "integer"},
                "team_name": {"type": "string"},
                "stadium": {"type": "string"},
                "manager": {"type": "string"}
            },
            "required": ["team_id", "team_name", "stadium", "manager"]
        }
    },
    "players": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "team_title": {"type": "string"},
                "player_name": {"type": "string"},
                "position": {"type": "string"}
            },
            "required": ["team_title", "player_name", "position"]
        }
    },
    "matches": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "datetime": {"type": "string"},
                "team_a": {"type": "string"},
                "team_b": {"type": "string"},
                "score": {"type": "string"}
            },
            "required": ["datetime", "team_a", "team_b"]
        }
    }
})

# Log that the schemas were manually added
logging.info("Manually added schemas (all_players, teams, players, matches) to SCHEMAS.")

# Utility to load and validate JSON data
@lru_cache(maxsize=10)
def load_json_file(file_path, schema=None):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            if schema:
                validate(instance=data, schema=schema)
            logging.info(f"Successfully loaded and validated data from {file_path}.")
            return data
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}. Returning an empty list.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {file_path}. Returning an empty list.")
        return []
    except ValidationError as e:
        logging.error(f"Schema validation error for file {file_path}: {e.message}. Returning an empty list.")
        return []

# Utility to filter data by key-value
def filter_by_key(data_list, key, value):
    try:
        filtered_data = [item for item in data_list if item.get(key, "").lower() == value.lower()]
        logging.info(f"Filtered {len(filtered_data)} items based on key='{key}' and value='{value}'.")
        return filtered_data
    except Exception as e:
        logging.error(f"Error during filtering by key: {e}")
        return []

# Utility to filter data by date
def filter_by_date(data_list, date):
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        filtered_data = [
            item for item in data_list
            if datetime.strptime(item["datetime"], "%Y-%m-%dT%H:%M:%S").date() == target_date
        ]
        logging.info(f"Filtered {len(filtered_data)} items for the date '{date}'.")
        return filtered_data
    except ValueError:
        logging.error(f"Invalid date format for filtering: {date}. Expected 'YYYY-MM-DD'.")
        return []
    except Exception as e:
        logging.error(f"Unexpected error during date filtering: {e}")
        return []

# Utility for pagination
def paginate(data_list):
    if not data_list:
        logging.info("Pagination request returned no results.")
        return []

    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 50))))
    except ValueError:
        logging.warning("Invalid pagination parameters provided.")
        return []

    start = (page - 1) * per_page
    end = start + per_page

    returned_items = len(data_list[start:end])
    logging.info(f"Pagination: page={page}, per_page={per_page}, total_items={len(data_list)}, returned_items={returned_items}")
    return data_list[start:end]

@app.route('/players', methods=['GET'])
@limiter.limit("50 per hour")
def get_players():
    players = load_json_file(DATA_FILES["players"], schema=SCHEMAS.get("players"))
    team = request.args.get('team')

    if not players:
        logging.error("Player data not available.")
        return jsonify({"error": "Player data not available."}), 500

    if team:
        if not team.isalpha():
            logging.warning(f"Invalid team parameter: {team}")
            return jsonify({"error": "Invalid team parameter. Must contain only alphabetic characters."}), 400
        players = filter_by_key(players, "team_title", team)

    logging.info(f"Returning {len(players)} player records.")
    return jsonify(paginate(players))

# More routes go here (similar to above)...
# All routes like /all_players, /matches, /teams...

if __name__ == "__main__":
    logging.info("Starting the EPL Data API server...")
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logging.error(f"Error occurred while running the server: {e}")
