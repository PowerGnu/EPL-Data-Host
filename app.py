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

app = Flask(__name__)
logging.info("Flask application instance created.")

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

47e83f5c75916e6fcc3bc443d6a81e486cedfd33
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

SCHEMAS = {
    key: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": generate_properties(key),
            "required": list(generate_properties(key).keys())
        }
    } for key in DATA_FILES.keys()  # No comma after this line
}



logging.info("Schemas generation starts here.")
logging.info("JSON schemas for validation have been generated.")

# Utility: Load JSON File
@lru_cache(maxsize=10)
def load_json_file(file_path, schema=None):
    """Load and validate JSON data from a file."""
    }
    for key in DATA_FILES.keys()
} for key in DATA_FILES.keys()},
                "player_name": {"type": "string"},
                "team_title": {"type": "string"},
                "position": {"type": "string"}
            } if key in ["all_players", "players"] else {
                "team_id": {"type": "integer"},
                "team_name": {"type": "string"},
                "stadium": {"type": "string"},
                "manager": {"type": "string"}
            } if key == "teams" else {
                "datetime": {"type": "string"},
                "team_a": {"type": "string"},
                "team_b": {"type": "string"},
                "score": {"type": "string"}
            })
        },
        "required": ["player_id", "player_name", "team_title", "position"] if key in ["all_players", "players"] else ["team_id", "team_name", "stadium", "manager"] if key == "teams" else ["datetime", "team_a", "team_b"]
    }
} for key in DATA_FILES.keys()
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
}

# Utility: Load and Validate JSON Data
from functools import lru_cache

@lru_cache(maxsize=10)
def load_json_file(file_path, schema=None):
47e83f5c75916e6fcc3bc443d6a81e486cedfd33
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

# Utility: Filter Data by Key
def filter_by_key(data_list, key, value):
    """
    Filter a list of dictionaries by a specific key-value pair.
    Returns: Filtered list of dictionaries.
    """
    try:
        filtered_data = [item for item in data_list if item.get(key, "").lower() == value.lower()]
        logging.info(f"Filtered {len(filtered_data)} items based on key='{key}' and value='{value}'.")
        return filtered_data
    except Exception as e:
        logging.error(f"Error during filtering by key: {e}")
        return []

# Utility: Filter Data by Date
def filter_by_date(data_list, date):
    """
    Filter a list of dictionaries by a specific date in 'YYYY-MM-DD' format.
    Returns: Filtered list of dictionaries or an error message.
    """
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

# Utility: Pagination Logic
def paginate(data_list):
    """
    Paginate a list of data based on query parameters.
    Logs pagination details for debugging.
    """
    if not data_list:
        logging.info("Pagination request returned no results.")
        return []

    try:
        page = max(1, int(request.args.get('page', 1)))  # Ensure positive integer
        per_page = min(100, max(1, int(request.args.get('per_page', 50))))  # Enforce limits: 1 <= per_page <= 100
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
    """
    Fetch player data filtered by team, if specified.
    """
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

@app.route('/all_players', methods=['GET'])
@limiter.limit("200 per hour")
def get_all_players():
    """
    Fetch all player data.
    """
    all_players = load_json_file(DATA_FILES["all_players"], schema=SCHEMAS.get("all_players"))

    if not all_players:
        logging.error("All players data not available.")
        return jsonify({"error": "All players data not available."}), 500

    logging.info(f"Returning {len(all_players)} player records.")
    return jsonify(paginate(all_players))

@app.route('/matches', methods=['GET'])
@limiter.limit("100 per hour")
def get_matches():
    """
    Fetch match data filtered by date, if specified.
    """
    matches = load_json_file(DATA_FILES["matches"], schema=SCHEMAS.get("matches"))
    date = request.args.get('date')

    if not matches:
        logging.error("Match data not available.")
        return jsonify({"error": "Match data not available."}), 500

    if date:
        matches = filter_by_date(matches, date)

    logging.info(f"Returning {len(matches)} match records.")
    return jsonify(paginate(matches))

@app.route('/teams', methods=['GET'])
@limiter.limit("100 per hour")
def get_teams():
    """
    Fetch team data.
    """
    teams = load_json_file(DATA_FILES["teams"], schema=SCHEMAS.get("teams"))

    if not teams:
        logging.error("Team data not available.")
        return jsonify({"error": "Team data not available."}), 500

    logging.info(f"Returning {len(teams)} team records.")
    return jsonify(paginate(teams))
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
47e83f5c75916e6fcc3bc443d6a81e486cedfd33

@app.route('/')
def home():
    """
    Home route for the EPL API.
    """
    return jsonify({
        "message": "Welcome to the EPL Data API!",
        "endpoints": {
            "/players": "Retrieve player data.",
            "/all_players": "Retrieve all player data.",
            "/matches": "Retrieve match data.",
            "/teams": "Retrieve team data."
        }
    })

if __name__ == "__main__":
    logging.info("Starting the EPL Data API server...")
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logging.error(f"Error occurred while running the server: {e}")

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
47e83f5c75916e6fcc3bc443d6a81e486cedfd33
