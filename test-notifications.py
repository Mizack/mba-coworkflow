#!/usr/bin/env python3
import requests

BASE_URL = 'http://localhost:8000'

def test_email():
    data = {
        "to": "usuario@exemplo.com",
        "subject": "Teste de Email",
        "body": "Este é um email de teste do CoworkFlow"
    }
    response = requests.post(f'{BASE_URL}/notify/email', json=data)
    print(f"Email: {response.status_code} - {response.json()}")

def test_sms():
    data = {
        "phone": "+5511999999999",
        "message": "Teste de SMS do CoworkFlow"
    }
    response = requests.post(f'{BASE_URL}/notify/sms', json=data)
    print(f"SMS: {response.status_code} - {response.json()}")

def test_push():
    data = {
        "user_id": 1,
        "title": "Teste Push",
        "message": "Notificação push de teste"
    }
    response = requests.post(f'{BASE_URL}/notify/push', json=data)
    print(f"Push: {response.status_code} - {response.json()}")

if __name__ == '__main__':
    print("=== Testando Notificações ===")
    test_email()
    test_sms()
    test_push()