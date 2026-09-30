import os
os.environ["DATABASE_URL"]="sqlite:///./test_pocketsmart.db"
os.environ["USE_MOCK_AI"]="true"
os.environ["SECRET_KEY"]="test-secret"

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client=TestClient(app)

def test_health():
    r=client.get("/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_register_login_and_home():
    email="test_unique@example.com"
    client.post("/register",json={"name":"Test User","email":email,"password":"secret123"})
    r=client.post("/login",json={"email":email,"password":"secret123"})
    assert r.status_code==200
    r=client.post("/generate-home",json={"budget":50000,"rooms":["Living Room"],"items":{"lights":4,"sofa":1},"style":"Modern","notes":""})
    assert r.status_code==200
    assert r.json()["planner_type"]=="home"
    assert len(r.json()["recommendations"])>0

def test_party_and_history():
    email="party_unique@example.com"
    client.post("/register",json={"name":"Party User","email":email,"password":"secret123"})
    r=client.post("/generate-party",json={"budget":30000,"guests":25,"event_type":"Birthday","venue":"Home","city":"Puducherry","preferences":"Vegetarian"})
    assert r.status_code==200
    h=client.get("/history")
    assert h.status_code==200
    assert len(h.json()["items"])>=1
