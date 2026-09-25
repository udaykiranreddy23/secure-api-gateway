from fastapi.testclient import TestClient
from app.main import app

def test_health():
    assert TestClient(app).get("/health").status_code == 200

def test_auth_required():
    assert TestClient(app).get("/proxy/orders").status_code == 401
