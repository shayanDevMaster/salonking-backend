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
@app.route("/getYourSalon", methods=["POST", "OPTIONS"])
def getYourSalon():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content

    # Get request data
    data = request.get_json()
    index = data.get("index")
    salon_name = data.get("salon_id")

    # Validate input
    if index is None or not salon_name:
        return jsonify({"status": "error", "message": "Missing index or salon_id"}), 400

    try:
        # Convert index to string for Firebase path
        # index_str = str(index)

        # Fetch the salon at the specified index
        ref = db.reference("salons/0")
        result = ref.get()

        # Check if the salon matches the salon_name
        if result and result.get("salon_name") == salon_name:
            return jsonify({"status": "success", "data": result})

        # # If not found at the given index, search through all salons
        # all_salons = db.reference("salons").get() or {}
        # ind = 0
        # # Handle case where all_salons is a dictionary (Firebase key-value structure)
        # for key, salon in all_salons.items():
        #     if salon.get("salon_name") == salon_name:
        #         return jsonify({"status": "success", "salon": salon, "index": ind})
        #     ind += 1

        # # If no match is found
        # return jsonify({"status": "not_found", "index": -1})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500221


# ///////////////////////////////////////////
def Get_data(path):
    if not path:
        return jsonify({"error": "Missing path"}), 400
    try:
        ref = db.reference(path)
        result = ref.get()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def Set_data(path , value):
    if not path or value is None:
        return jsonify({"error": "Missing path or value"}), 400
    try:
        ref = db.reference(path)
        ref.set(value)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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