from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import firebase_admin
from firebase_admin import credentials, firestore
import tempfile
import requests
import os
import json

app = Flask(__name__)
CORS(app)

# FIREBASE FROM RENDER ENV VARIABLE
firebase_json = json.loads(os.environ["FIREBASE_KEY"])

cred = credentials.Certificate(firebase_json)

try:
    firebase_admin.initialize_app(cred)
except:
    pass

db = firestore.client()

@app.route("/")
def home():
    return "SafeReturn AI Server Running"

@app.route("/match", methods=["POST"])
def match_faces():
    try:
        data = request.json

        uploaded_image = data.get("image")

        if not uploaded_image:
            return jsonify({
                "success": False,
                "error": "No image provided"
            }), 400

        # DOWNLOAD UPLOADED IMAGE
        uploaded_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        uploaded_response = requests.get(uploaded_image)

        uploaded_temp.write(uploaded_response.content)
        uploaded_temp.close()

        uploaded_path = uploaded_temp.name

        # GET REPORTS
        reports = db.collection("reports").stream()

        matches = []

        for report in reports:
            report_data = report.to_dict()

            report_image = report_data.get("image")

            if not report_image:
                continue

            try:
                # DOWNLOAD REPORT IMAGE
                report_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                report_response = requests.get(report_image)

                report_temp.write(report_response.content)
                report_temp.close()

                report_path = report_temp.name

                # FACE MATCH
                result = DeepFace.verify(
                    img1_path=uploaded_path,
                    img2_path=report_path,
                    enforce_detection=False,
                    model_name="Facenet"
                )

                similarity = round((1 - result["distance"]) * 100, 2)

                if result["verified"]:
                    matches.append({
                        "id": report.id,
                        "name": report_data.get("name", "Unknown"),
                        "age": report_data.get("age", ""),
                        "location": report_data.get("location", ""),
                        "image": report_image,
                        "similarity": similarity
                    })

                os.remove(report_path)

            except Exception as e:
                print("MATCH ERROR:", e)

        os.remove(uploaded_path)

        return jsonify({
            "success": True,
            "matches": matches
        })

    except Exception as e:
        print("SERVER ERROR:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)