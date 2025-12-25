import sys
import os
import pytest
from fakeredis import FakeStrictRedis

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def mock_get_redis():
    if not hasattr(mock_get_redis, "_client"):
        mock_get_redis._client = FakeStrictRedis(decode_responses=True)
    return mock_get_redis._client

import app
app.get_redis = mock_get_redis

flask_app = app.app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_initial_value_is_zero(client):
    rv = client.get('/api/counter')
    assert rv.get_json()['value'] == 0

def test_increment(client):
    client.post('/api/counter/increment')
    rv = client.get('/api/counter')
    assert rv.get_json()['value'] == 1

def test_decrement_below_zero_fails(client):
    rv = client.post('/api/counter/decrement')
    assert rv.status_code == 400
    assert rv.get_json()['error'] == "Counter cannot be negative"

def test_decrement_from_one_works(client):
    client.post('/api/counter/increment')
    rv = client.post('/api/counter/decrement')
    assert rv.status_code == 200
    assert rv.get_json()['value'] == 0