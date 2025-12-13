import pytest
import requests
import time
import json

BASE_URL = 'http://localhost:8000'

class TestUserFlowIntegration:
    """Testes de integração para fluxo completo do usuário"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.test_user = {
            'email': f'test_{int(time.time())}@test.com',
            'password': 'test123',
            'name': 'Test User',
            'role': 'user'
        }
        self.admin_user = {
            'email': f'admin_{int(time.time())}@test.com',
            'password': 'admin123',
            'name': 'Admin User',
            'role': 'admin'
        }

    def test_complete_user_registration_and_login_flow(self):
        """Testa o fluxo completo de registro e login"""
        
        # 1. Registrar usuário
        signup_response = requests.post(f'{BASE_URL}/auth/signup', json=self.test_user)
        assert signup_response.status_code == 201
        
        # 2. Fazer login
        login_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password']
        }
        login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()['token']
        assert token is not None
        
        # 3. Acessar dados do usuário
        headers = {'Authorization': f'Bearer {token}'}
        user_response = requests.get(f'{BASE_URL}/users/me', headers=headers)
        assert user_response.status_code == 200
        
        user_data = user_response.json()
        assert user_data['email'] == self.test_user['email']
        assert user_data['name'] == self.test_user['name']

    def test_admin_space_management_flow(self):
        """Testa o fluxo de gerenciamento de espaços pelo admin"""
        
        # 1. Registrar admin
        signup_response = requests.post(f'{BASE_URL}/auth/signup', json=self.admin_user)
        assert signup_response.status_code == 201
        
        # 2. Login como admin
        login_data = {
            'email': self.admin_user['email'],
            'password': self.admin_user['password']
        }
        login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        assert login_response.status_code == 200
        
        admin_token = login_response.json()['token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # 3. Criar espaço
        space_data = {
            'name': f'Test Space {int(time.time())}',
            'description': 'Test space description',
            'capacity': 10,
            'price_per_hour': 25.0
        }
        create_response = requests.post(f'{BASE_URL}/spaces', json=space_data, headers=admin_headers)
        assert create_response.status_code == 201
        
        space_id = create_response.json()['id']
        
        # 4. Listar espaços
        spaces_response = requests.get(f'{BASE_URL}/spaces')
        assert spaces_response.status_code == 200
        
        spaces = spaces_response.json()
        created_space = next((s for s in spaces if s['id'] == space_id), None)
        assert created_space is not None
        assert created_space['name'] == space_data['name']

    def test_reservation_flow_integration(self):
        """Testa o fluxo completo de reserva"""
        
        # 1. Criar admin e espaço
        requests.post(f'{BASE_URL}/auth/signup', json=self.admin_user)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': self.admin_user['email'],
            'password': self.admin_user['password']
        })
        admin_token = admin_login.json()['token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        space_data = {
            'name': f'Reservation Test Space {int(time.time())}',
            'description': 'Space for reservation test',
            'capacity': 5,
            'price_per_hour': 30.0
        }
        space_response = requests.post(f'{BASE_URL}/spaces', json=space_data, headers=admin_headers)
        space_id = space_response.json()['id']
        
        # 2. Criar usuário regular
        requests.post(f'{BASE_URL}/auth/signup', json=self.test_user)
        user_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': self.test_user['email'],
            'password': self.test_user['password']
        })
        user_token = user_login.json()['token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # 3. Obter dados do usuário
        user_data = requests.get(f'{BASE_URL}/users/me', headers=user_headers).json()
        
        # 4. Calcular preço da reserva
        pricing_data = {
            'space_id': space_id,
            'start_time': '2024-12-01T10:00:00',
            'end_time': '2024-12-01T12:00:00',
            'user_plan': 'basic'
        }
        pricing_response = requests.post(f'{BASE_URL}/pricing/calc', json=pricing_data)
        assert pricing_response.status_code == 200
        total_price = pricing_response.json()['total']
        
        # 5. Criar reserva
        reservation_data = {
            'user_id': user_data['id'],
            'space_id': space_id,
            'start_time': '2024-12-01T10:00:00',
            'end_time': '2024-12-01T12:00:00',
            'total_price': total_price
        }
        reservation_response = requests.post(f'{BASE_URL}/reservations', json=reservation_data, headers=user_headers)
        assert reservation_response.status_code == 201
        
        reservation_id = reservation_response.json()['id']
        
        # 6. Processar pagamento
        payment_data = {
            'reservation_id': reservation_id,
            'amount': total_price,
            'method': 'credit_card'
        }
        payment_response = requests.post(f'{BASE_URL}/payments/charge', json=payment_data, headers=user_headers)
        assert payment_response.status_code == 200
        
        # 7. Verificar reserva criada
        reservations_response = requests.get(f'{BASE_URL}/reservations/user/{user_data["id"]}', headers=user_headers)
        assert reservations_response.status_code == 200
        
        reservations = reservations_response.json()
        created_reservation = next((r for r in reservations if r['id'] == reservation_id), None)
        assert created_reservation is not None

    def test_checkin_checkout_flow(self):
        """Testa o fluxo de check-in e check-out"""
        
        # Setup: criar usuário, espaço e reserva
        requests.post(f'{BASE_URL}/auth/signup', json=self.admin_user)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': self.admin_user['email'],
            'password': self.admin_user['password']
        })
        admin_headers = {'Authorization': f'Bearer {admin_login.json()["token"]}'}
        
        space_response = requests.post(f'{BASE_URL}/spaces', json={
            'name': f'Checkin Test Space {int(time.time())}',
            'description': 'Space for checkin test',
            'capacity': 3,
            'price_per_hour': 20.0
        }, headers=admin_headers)
        space_id = space_response.json()['id']
        
        requests.post(f'{BASE_URL}/auth/signup', json=self.test_user)
        user_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': self.test_user['email'],
            'password': self.test_user['password']
        })
        user_headers = {'Authorization': f'Bearer {user_login.json()["token"]}'}
        user_data = requests.get(f'{BASE_URL}/users/me', headers=user_headers).json()
        
        # Criar reserva
        reservation_response = requests.post(f'{BASE_URL}/reservations', json={
            'user_id': user_data['id'],
            'space_id': space_id,
            'start_time': '2024-12-01T14:00:00',
            'end_time': '2024-12-01T16:00:00',
            'total_price': 40.0
        }, headers=user_headers)
        reservation_id = reservation_response.json()['id']
        
        # 1. Check-in
        checkin_response = requests.post(f'{BASE_URL}/checkin/{reservation_id}', headers=user_headers)
        assert checkin_response.status_code == 200
        
        # 2. Check-out
        checkout_response = requests.post(f'{BASE_URL}/checkout/{reservation_id}', headers=user_headers)
        assert checkout_response.status_code == 200

    def test_admin_analytics_flow(self):
        """Testa o fluxo de analytics para admin"""
        
        # 1. Criar admin
        requests.post(f'{BASE_URL}/auth/signup', json=self.admin_user)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': self.admin_user['email'],
            'password': self.admin_user['password']
        })
        admin_headers = {'Authorization': f'Bearer {admin_login.json()["token"]}'}
        
        # 2. Acessar analytics do dashboard
        analytics_response = requests.get(f'{BASE_URL}/analytics/dashboard', headers=admin_headers)
        assert analytics_response.status_code == 200
        
        analytics_data = analytics_response.json()
        assert 'total_reservations' in analytics_data
        
        # 3. Acessar dados financeiros
        revenue_response = requests.get(f'{BASE_URL}/financial/revenue', headers=admin_headers)
        assert revenue_response.status_code == 200
        
        expenses_response = requests.get(f'{BASE_URL}/financial/expenses', headers=admin_headers)
        assert expenses_response.status_code == 200

    def test_notification_flow(self):
        """Testa o fluxo de notificações"""
        
        # 1. Enviar notificação por email
        email_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test message body'
        }
        email_response = requests.post(f'{BASE_URL}/notify/email', json=email_data)
        assert email_response.status_code == 200
        
        # 2. Enviar notificação por SMS
        sms_data = {
            'phone': '+1234567890',
            'message': 'Test SMS message'
        }
        sms_response = requests.post(f'{BASE_URL}/notify/sms', json=sms_data)
        assert sms_response.status_code == 200
        
        # 3. Enviar notificação push
        push_data = {
            'user_id': 1,
            'title': 'Test Push',
            'message': 'Test push notification'
        }
        push_response = requests.post(f'{BASE_URL}/notify/push', json=push_data)
        assert push_response.status_code == 200