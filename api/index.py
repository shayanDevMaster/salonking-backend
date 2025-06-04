from flask import Flask, request, jsonify
from firebase_admin import credentials, db, initialize_app
import os
import json

# Initialize Flask app
app = Flask(__name__)

# Load Firebase credentials from environment variable
firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')
if not firebase_credentials:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

cred = credentials.Certificate(json.loads(firebase_credentials))

initialize_app(cred, {
    'databaseURL': 'https://salon-booking-7a936-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Enable CORS for specific origins (allow local development and your deployed frontend)
@app.after_request
def apply_cors(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5501'  # Allow local development
    # For production, replace with your frontend URL (e.g., 'https://your-frontend.vercel.app')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
# ///////////////////////////////////////////
@app.route("/getAllSalon", methods=["POST", "OPTIONS"])
def getAllSalon():
    ref = db.reference("salons")
    result = ref.get()
    return jsonify({"status": "success", "data": result})

@app.route("/getUserBookings", methods=["POST", "OPTIONS"])
def getUserBookings():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    deviceId = data.get("deviceId")

    if not deviceId:
        return jsonify({"error": "Missing deviceId"}), 400
    
    ref = db.reference("bookings")
    bookings = ref.get()
    
    # Add there bookings filter by device id variable
    # Filter bookings by deviceId
    filtered_bookings = {
        key: value for key, value in bookings.items()
        if value.get("deviceId") == deviceId
    } if bookings else {}

    return jsonify({"status": "success", "data": filtered_bookings})

# ///////////////////////////////////////////
def Get_data(path):
    if not path:
        return jsonify({"error": "Missing path"}), 400
    try:
        ref = db.reference(path)
        result = ref.get()
        return result
    except Exception as e:
        return None

def Set_data(path , value):
    if not path or value is None:
        return
    ref = db.reference(path)
    ref.set(value)
    return
# ///////////////////////////////////////////

# ///////////////////////////////////////////
@app.route("/get", methods=["POST", "OPTIONS"])
def get():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing path"}), 400
    try:
        ref = db.reference(path)
        result = ref.get()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/set", methods=["POST", "OPTIONS"])
def set_data():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    value = data.get("value")
    if not path or value is None:
        return jsonify({"error": "Missing path or value"}), 400
    try:
        ref = db.reference(path)
        ref.set(value)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ///////////////////////////////////////////
@app.route("/update", methods=["POST", "OPTIONS"])
def update_data():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    value = data.get("value")
    if not path or not isinstance(value, dict):
        return jsonify({"error": "Missing path or value"}), 400
    try:
        ref = db.reference(path)
        ref.update(value)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete", methods=["POST", "OPTIONS"])
def delete_data():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing path"}), 400
    try:
        ref = db.reference(path)
        ref.delete()
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)