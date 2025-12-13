#!/usr/bin/env python3
import requests
import json

# Teste do API Gateway
BASE_URL = 'http://localhost:8000'

def test_health():
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def test_signup():
    data = {
        "email": "test@exemplo.com",
        "password": "senha123",
        "name": "Usuário Teste"
    }
    try:
        response = requests.post(f'{BASE_URL}/auth/signup', json=data)
        print(f"Signup: {response.status_code} - {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Signup Failed: {e}")
        return False

def test_login():
    data = {
        "email": "test@exemplo.com",
        "password": "senha123"
    }
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"Login: {response.status_code} - {response.json()}")
        if response.status_code == 200:
            return response.json().get('token')
        return None
    except Exception as e:
        print(f"Login Failed: {e}")
        return None

def test_spaces():
    try:
        response = requests.get(f'{BASE_URL}/spaces')
        print(f"Spaces: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Spaces Failed: {e}")
        return False

if __name__ == '__main__':
    print("=== Testando API Gateway ===")
    
    if test_health():
        print("✅ Health Check OK")
    else:
        print("❌ Health Check Failed")
    
    if test_signup():
        print("✅ Signup OK")
    
    token = test_login()
    if token:
        print("✅ Login OK")
    else:
        print("❌ Login Failed")
    
    if test_spaces():
        print("✅ Spaces OK")
    else:
        print("❌ Spaces Failed")