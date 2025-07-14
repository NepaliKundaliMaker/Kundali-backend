from flask import Flask, request, jsonify
from flask_cors import CORS
from district_coords import get_coords
from swisseph_utils import get_planet_data
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route("/kundali", methods=["POST"])
def kundali():
    data = request.get_json()
    # Support test mode
    if data.get("test_mode"):
        # fixed sample data
        birth_date = "1985-05-15T06:30:00"
        birth_loc = (27.7172, 85.3240)
    else:
        bd = data["birth_date"]
        bt = data["birth_time"]
        dt_str = f"{bd}T{bt}"
        birth_date = datetime.fromisoformat(dt_str)
        birth_loc = get_coords(data.get("birth_location", "Kathmandu"))

    result = get_planet_data(birth_date, birth_loc, test_mode=data.get("test_mode", False))
    return jsonify(result)

if __name__ == "__main__":
    # debug mode if FLASK_DEBUG env var is set
    app.run(debug=True, host="0.0.0.0", port=5000)