import requests
import numpy as np
import json

BASE_URL = "http://localhost:5000"

print("=" * 55)
print("AI THREAT DETECTION API — TEST SUITE")
print("=" * 55)

# Test 1: Health check
print("\n[1] Health Check")
r = requests.get(f"{BASE_URL}/health")
result = r.json()
print(f"    Status: {result['status']}")
print(f"    Features expected: {result['features_expected']}")

# Test 2: Send 10 predictions
print("\n[2] Sending 10 test predictions...")
predictions = []
for i in range(10):
    # Generate random features
    features = np.random.rand(77).tolist()
    r = requests.post(f"{BASE_URL}/predict",
                      json={"features": features})
    result = r.json()
    predictions.append(result)

    icon = "🚨" if result['threat_detected'] else "✓"
    print(f"    {icon} Prediction {i+1:2d}: "
          f"{result['prediction']:8s} | "
          f"Confidence: {result['confidence_pct']:6.2f}% | "
          f"Severity: {result['severity']}")

# Test 3: Stats
print("\n[3] Detection Statistics")
r = requests.get(f"{BASE_URL}/stats")
stats = r.json()
print(f"    Total analyzed:   {stats['total_analyzed']}")
print(f"    Threats detected: {stats['threats_detected']}")
print(f"    Detection rate:   {stats['detection_rate_pct']}%")

# Test 4: Wrong feature count (error handling)
print("\n[4] Error Handling Test")
r = requests.post(f"{BASE_URL}/predict",
                  json={"features": [1.0, 2.0, 3.0]})
result = r.json()
print(f"    Expected error: {result.get('error', 'No error returned')}")

print("\n" + "=" * 55)
print("All tests complete")
print("=" * 55)