import os
import json
import datetime
import numpy as np
import tensorflow as tf

from flask import Flask, request, jsonify, render_template
from web3 import Web3

from carbon_model import estimate_carbon

# ==============================
# FLASK SETUP
# ==============================
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

AI_CONFIDENCE_THRESHOLD = 0.70

# ==============================
# LOAD MANGROVE MODEL (.h5)
# ==============================
MODEL_PATH = "mangrove_classifier.h5"
model = tf.keras.models.load_model(MODEL_PATH)

IMG_SIZE = 128  # Must match training size


def verify_image(image_path):
    """
    Uses mangrooves.h5 model to classify:
    0 → Non-Mangrove
    1 → Mangrove
    """

    img = tf.keras.preprocessing.image.load_img(
        image_path,
        target_size=(IMG_SIZE, IMG_SIZE)
    )

    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]

    confidence = float(prediction)

    if prediction >= 0.5:
        return "Verified", confidence
    else:
        return "Rejected", 1 - confidence


# ==============================
# ETHEREUM CONNECTION
# ==============================

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

with open("contract_data.json") as f:
    contract_json = json.load(f)

contract = w3.eth.contract(
    address=contract_json["address"],
    abi=contract_json["abi"]
)

account = w3.eth.accounts[0]


# ==============================
# ROUTES
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_project():
    try:
        area = float(request.form["area"])
        file = request.files["image"]

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        # -----------------------------
        # AI CLASSIFICATION (Mangrove Model)
        # -----------------------------
        status, confidence = verify_image(path)
        os.remove(path)

        classification_label = (
            "Mangrove Detected" if status == "Verified"
            else "Non-Mangrove"
        )

        # -----------------------------
        # AI VALIDATION CHECK
        # -----------------------------
        if status != "Verified" or confidence < AI_CONFIDENCE_THRESHOLD:
            return jsonify({
                "success": False,
                "classification": classification_label,
                "confidence": round(confidence, 3),
                "message": "AI verification failed. Credits cannot be issued."
            })

        # -----------------------------
        # CARBON ESTIMATION
        # -----------------------------
        carbon = estimate_carbon(area, confidence)

        carbon_price_per_ton = 10  # USD (demo)
        total_value = carbon * carbon_price_per_ton

        # -----------------------------
        # BLOCKCHAIN ENTRY (Ethereum)
        # -----------------------------
        project_id = f"Project_{int(datetime.datetime.now().timestamp())}"

        tx = contract.functions.addProject(
            project_id,
            int(area),
            int(carbon),
            int(total_value),
            classification_label,
            int(confidence * 100)
        ).transact({"from": account})

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)

        transaction_hash = tx_receipt.transactionHash.hex()

        return jsonify({
            "success": True,
            "classification": classification_label,
            "confidence": round(confidence, 3),
            "carbon": carbon,
            "estimated_value": total_value,
            "transaction_hash": transaction_hash
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/chain", methods=["GET"])
def get_chain():

    total = contract.functions.getTotalProjects().call()
    projects = []

    for i in range(total):
        p = contract.functions.getProject(i).call()

        projects.append({
            "id": p[0],
            "projectId": p[1],
            "area": p[2],
            "carbonCredits": p[3],
            "estimatedValue": p[4],
            "classification": p[5],
            "confidenceScore": p[6],
            "timestamp": p[7]
        })

    return jsonify(projects)


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)