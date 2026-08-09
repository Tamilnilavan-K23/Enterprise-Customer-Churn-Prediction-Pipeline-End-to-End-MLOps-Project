import os
import sys
import requests
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

# Fix Windows console UTF-8 output encoding if supported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Make src importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

url = "http://127.0.0.1:8000/predict"

sample_data = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 5,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35,
    "TotalCharges": 350.75
}

print("=== Testing FastAPI Endpoint ===")

try:
    # Attempt to send request to a running live server on 127.0.0.1:8000
    response = requests.post(url, json=sample_data, timeout=2)
    print("Mode: Live Server (http://127.0.0.1:8000)")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    # If live server is not running, test app in-process using TestClient
    print("Notice: Live server at 127.0.0.1:8000 not detected. Testing via FastAPI TestClient...")
    
    from src.app.main import app

    client = TestClient(app)

    # Health Check test
    health_res = client.get("/health")
    print("Health Check Status Code:", health_res.status_code, "Body:", health_res.json())

    # Prediction test
    res = client.post("/predict", json=sample_data)
    print("Prediction Endpoint Status Code:", res.status_code)
    print("Response:", res.json())
