from flask import Flask, request, jsonify
from flask_cors import CORS
from swisseph_utils import get_planet_data

app = Flask(__name__)
CORS(app)

@app.route("/kundali", methods=["POST"])
def kundali():
    data = request.get_json()
    birth_date = data["birth_date"]
    birth_time = data["birth_time"]
    birth_location = data["birth_location"]  # currently unused, defaults to Kathmandu

    result = get_planet_data(birth_date, birth_time)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
