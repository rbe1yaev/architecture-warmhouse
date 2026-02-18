import random
from flask import Flask, request, jsonify
from datetime import datetime, timezone


app = Flask(__name__)


def generate_temp_response(sensor_id=None, location=None):
    if not location:
        mapping = {"1": "Living Room", "2": "Bedroom", "3": "Kitchen"}
        location = mapping.get(sensor_id, "Unknown")

    if not sensor_id:
        mapping = {"Living Room": "1", "Bedroom": "2", "Kitchen": "3"}
        sensor_id = mapping.get(location, "0")

    return {
        "value": round(random.uniform(15.0, 30.0), 2),
        "unit": "°C",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
        "status": "active",
        "sensor_id": sensor_id,
        "sensor_type": "temperature",
        "description": f"Temperature sensor in {location}"
    }


@app.route('/temperature', methods=['GET'])
def get_location_temp():
    location = request.args.get('location')
    sensor_id = request.args.get('sensorId')
    return jsonify(generate_temp_response(sensor_id, location))


@app.route('/temperature/<sensor_id>/', methods=['GET'])
def get_sensor_temp(sensor_id):
    return jsonify(generate_temp_response(sensor_id=sensor_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)