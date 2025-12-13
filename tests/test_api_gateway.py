import pytest
import requests

BASE_URL = 'http://localhost:8000'

def test_health_check():
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

def test_signup():
    data = {
        "email": "test@example.com",
        "password": "test123",
        "name": "Test User",
        "role": "user"
    }
    response = requests.post(f'{BASE_URL}/auth/signup', json=data)
    assert response.status_code in [201, 400]

def test_login():
    data = {
        "email": "test@example.com",
        "password": "test123"
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=data)
    assert response.status_code in [200, 401]

def test_spaces_list():
    response = requests.get(f'{BASE_URL}/spaces')
    assert response.status_code == 200
    assert isinstance(response.json(), list)