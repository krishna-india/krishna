from fastapi.testclient import TestClient
from krishna_india.api import app

client = TestClient(app)

def test_chat():
    resp = client.post('/chat', params={'message': 'hi', 'session_id': 'test'})
    assert resp.status_code == 200
    assert 'reply' in resp.json()

def test_stream():
    resp = client.get('/stream', params={'message': 'hi', 'session_id': 'test'})
    assert resp.status_code == 200
