import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["USE_GEMINI"] = "false"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_register_login_and_home_plan():
    email = 'test@example.com'
    client.post('/api/auth/register', json={'email':email,'password':'password123'})
    r = client.post('/api/auth/login', json={'email':email,'password':'password123'})
    assert r.status_code == 200
    r = client.post('/api/generate-home', json={'budget':50000,'currency':'INR','rooms':['Living Room'],'style':'Modern','priorities':'Value for money','quantities':{}})
    assert r.status_code == 200
    assert r.json()['planner_type'] == 'home'
    assert r.json()['source_mode'] == 'fallback'


def test_unauthorized():
    c = TestClient(app)
    assert c.get('/api/history').status_code == 401
