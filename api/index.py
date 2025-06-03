from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("salon-booking-7a936-firebase-adminsdk-fbsvc-c760c28ef2.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://salon-booking-7a936-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

@app.route("/get", methods=["POST"])
def get():
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

@app.route("/set", methods=["POST"])
def set_data():
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

@app.route("/update", methods=["POST"])
def update_data():
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

@app.route("/delete", methods=["POST"])
def delete_data():
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
    app.run()
