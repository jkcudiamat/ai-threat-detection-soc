from flask import Flask, request, jsonify
import pickle
import numpy as np
from datetime import datetime
import json
import os

app = Flask(__name__)

# ── Load model and preprocessors when API starts ──────────────────
print("Loading model and preprocessors...")

with open('models/preprocessed_data.pkl', 'rb') as f:
    data = pickle.load(f)

scaler = data['scaler']
le = data['label_encoder']
feature_names = data['feature_names']

with open('models/threat_detection_model.pkl', 'rb') as f:
    model = pickle.load(f)

print(f"Model loaded successfully")
print(f"Expecting {len(feature_names)} features per request")
print(f"Labels: {le.classes_}")

# ── In-memory alert storage ────────────────────────────────────────
alert_log = []

# ── Helper function — determine severity from confidence ───────────
def get_severity(confidence):
    if confidence >= 0.95:
        return "CRITICAL"
    elif confidence >= 0.85:
        return "HIGH"
    elif confidence >= 0.70:
        return "MEDIUM"
    else:
        return "LOW"

# ── Routes ────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    """API info and available endpoints"""
    return jsonify({
        "service": "AI Threat Detection API",
        "model": "Random Forest Classifier",
        "accuracy": "99.98%",
        "dataset": "CICIDS 2017 — 221K network flows",
        "status": "online",
        "endpoints": {
            "GET  /":           "API info (this page)",
            "GET  /health":     "Health check",
            "POST /predict":    "Submit network flow for threat analysis",
            "GET  /alerts":     "View detected threats",
            "GET  /stats":      "Detection statistics",
            "POST /reset":      "Clear alert log"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Simple health check"""
    return jsonify({
        "status": "online",
        "model_loaded": True,
        "features_expected": len(feature_names),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts a network flow as JSON and returns a threat prediction.
    
    Expected input:
    {
        "features": [val1, val2, ..., val77]  // 77 numeric values
    }
    
    Returns:
    {
        "id": 1,
        "timestamp": "2026-05-31T...",
        "prediction": "DDoS" or "Benign",
        "threat_detected": true or false,
        "confidence_pct": 99.5,
        "severity": "CRITICAL" / "HIGH" / "MEDIUM" / "LOW" / "NONE"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        if 'features' not in data:
            return jsonify({
                "error": "Missing 'features' key",
                "expected_format": {"features": [0.1, 0.2, "...77 values total"]}
            }), 400

        features = np.array(data['features'])

        # Validate feature count
        if len(features) != len(feature_names):
            return jsonify({
                "error": f"Wrong number of features",
                "received": len(features),
                "expected": len(feature_names)
            }), 400

        # Scale features using the same scaler from training
        features_scaled = scaler.transform(features.reshape(1, -1))

        # Make prediction
        prediction_encoded = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]

        # Decode prediction back to label
        predicted_label = le.inverse_transform([prediction_encoded])[0]
        confidence = float(max(probabilities))
        threat_detected = predicted_label != 'Benign'

        # Build alert object
        alert = {
            "id": len(alert_log) + 1,
            "timestamp": datetime.now().isoformat(),
            "prediction": predicted_label,
            "threat_detected": threat_detected,
            "confidence_pct": round(confidence * 100, 2),
            "severity": get_severity(confidence) if threat_detected else "NONE",
            "probabilities": {
                label: round(float(prob) * 100, 2)
                for label, prob in zip(le.classes_, probabilities)
            }
        }

        # Log the alert
        alert_log.append(alert)

        return jsonify(alert)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Returns all detected threats"""
    threats = [a for a in alert_log if a['threat_detected']]

    return jsonify({
        "total_analyzed": len(alert_log),
        "threats_detected": len(threats),
        "benign_detected": len(alert_log) - len(threats),
        "recent_threats": threats[-20:]
    })


@app.route('/stats', methods=['GET'])
def get_stats():
    """Returns detection statistics"""
    threats = [a for a in alert_log if a['threat_detected']]
    critical = [a for a in threats if a['severity'] == 'CRITICAL']
    high = [a for a in threats if a['severity'] == 'HIGH']
    medium = [a for a in threats if a['severity'] == 'MEDIUM']

    detection_rate = (len(threats) / len(alert_log) * 100) if alert_log else 0

    return jsonify({
        "total_analyzed": len(alert_log),
        "threats_detected": len(threats),
        "detection_rate_pct": round(detection_rate, 2),
        "severity_breakdown": {
            "CRITICAL": len(critical),
            "HIGH": len(high),
            "MEDIUM": len(medium)
        },
        "model_accuracy": "99.98%",
        "model_type": "Random Forest (100 trees)"
    })


@app.route('/reset', methods=['POST'])
def reset():
    """Clears the alert log"""
    global alert_log
    count = len(alert_log)
    alert_log = []
    return jsonify({
        "message": f"Alert log cleared",
        "alerts_removed": count
    })


@app.route('/features', methods=['GET'])
def get_features():
    """Returns list of expected feature names in order"""
    return jsonify({
        "feature_count": len(feature_names),
        "features": feature_names
    })


# ── Run the API ───────────────────────────────────────────────────
if __name__ == '__main__':
    print("\nAI Threat Detection API starting...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)