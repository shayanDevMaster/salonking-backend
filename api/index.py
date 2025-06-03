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

# Helper function to set data
def set_data(path, value):
    try:
        ref = db.reference(path)
        ref.set(value)
        return {"success": True, "message": "Data saved successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Helper function to get data
def get_data(path):
    try:
        ref = db.reference(path)
        data = ref.get()
        if data is None:
            return {"success": True, "data": None}
        if isinstance(data, dict) and all(k.isdigit() for k in data.keys()):
            data = list(data.values())
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# API Routes
@app.route('/api/data/<path:path>', methods=['GET'])
def read_data(path):
    result = get_data(path)
    return jsonify(result), 200 if result["success"] else 500

@app.route('/api/data/<path:path>', methods=['POST'])
def write_data(path):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    result = set_data(path, data)
    return jsonify(result), 200 if result["success"] else 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)