from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import tempfile
import os
import base64

app = Flask(__name__)

# FIX CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# FIREBASE
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# SAVE BASE64 IMAGE
def save_base64_image(base64_string):

    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    image_data = base64.b64decode(base64_string)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

    temp.write(image_data)
    temp.close()

    return temp.name

# DOWNLOAD IMAGE
def download_image(url):

    response = requests.get(url)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

    temp.write(response.content)
    temp.close()

    return temp.name

@app.route("/match", methods=["POST"])
def match():

    try:

        data = request.get_json()

        uploaded_image = data["image"]

        uploaded_path = save_base64_image(uploaded_image)

        reports = db.collection("reports").stream()

        matches = []

        for report in reports:

            report_data = report.to_dict()

            report_image = report_data.get("image")

            if not report_image:
                continue

            try:

                report_path = download_image(report_image)

                result = DeepFace.verify(
                    img1_path=uploaded_path,
                    img2_path=report_path,
                    enforce_detection=False
                )

                print(result)

                if result["verified"]:

                    matches.append({
                        "name": report_data.get("name", ""),
                        "location": report_data.get("location", ""),
                        "contact": report_data.get("contact", ""),
                        "description": report_data.get("description", ""),
                        "image": report_image,
                        "pincode": report_data.get("pincode", "")
                    })

                os.remove(report_path)

            except Exception as e:
                print("COMPARE ERROR:", e)

        os.remove(uploaded_path)

        return jsonify({
            "matches": matches
        })

    except Exception as e:

        print("SERVER ERROR:", e)

        return jsonify({
            "matches": []
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)