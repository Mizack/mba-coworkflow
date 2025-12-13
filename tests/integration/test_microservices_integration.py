import pytest
import requests
import time
import threading
import subprocess
import os

BASE_URL = 'http://localhost:8000'

class TestMicroservicesIntegration:
    """Testes de integração entre microserviços"""
    
    @pytest.fixture(scope='class', autouse=True)
    def setup_services(self):
        """Setup para inicializar serviços necessários"""
        # Este fixture assumiria que os serviços estão rodando
        # Em um ambiente real, você poderia usar docker-compose para isso
        yield
    
    def test_api_gateway_to_users_service(self):
        """Testa comunicação entre API Gateway e serviço de usuários"""
        
        # Criar usuário através do API Gateway
        user_data = {
            'email': f'integration_test_{int(time.time())}@test.com',
            'password': 'test123',
            'name': 'Integration Test User',
            'role': 'user'
        }
        
        signup_response = requests.post(f'{BASE_URL}/auth/signup', json=user_data)
        assert signup_response.status_code == 201
        
        # Login através do API Gateway
        login_response = requests.post(f'{BASE_URL}/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        assert login_response.status_code == 200
        
        token = login_response.json()['token']
        
        # Acessar dados do usuário através do API Gateway
        headers = {'Authorization': f'Bearer {token}'}
        user_response = requests.get(f'{BASE_URL}/users/me', headers=headers)
        assert user_response.status_code == 200
        
        user_info = user_response.json()
        assert user_info['email'] == user_data['email']

    def test_spaces_and_reservations_integration(self):
        """Testa integração entre serviços de espaços e reservas"""
        
        # Criar admin
        admin_data = {
            'email': f'admin_integration_{int(time.time())}@test.com',
            'password': 'admin123',
            'name': 'Admin Integration Test',
            'role': 'admin'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=admin_data)
        
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': admin_data['email'],
            'password': admin_data['password']
        })
        admin_token = admin_login.json()['token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Criar espaço
        space_data = {
            'name': f'Integration Space {int(time.time())}',
            'description': 'Space for integration testing',
            'capacity': 8,
            'price_per_hour': 35.0
        }
        space_response = requests.post(f'{BASE_URL}/spaces', json=space_data, headers=admin_headers)
        assert space_response.status_code == 201
        space_id = space_response.json()['id']
        
        # Criar usuário regular
        user_data = {
            'email': f'user_integration_{int(time.time())}@test.com',
            'password': 'user123',
            'name': 'User Integration Test',
            'role': 'user'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=user_data)
        
        user_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        user_token = user_login.json()['token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        user_info = requests.get(f'{BASE_URL}/users/me', headers=user_headers).json()
        
        # Criar reserva usando o espaço criado
        reservation_data = {
            'user_id': user_info['id'],
            'space_id': space_id,
            'start_time': '2024-12-02T09:00:00',
            'end_time': '2024-12-02T11:00:00',
            'total_price': 70.0
        }
        reservation_response = requests.post(f'{BASE_URL}/reservations', json=reservation_data, headers=user_headers)
        assert reservation_response.status_code == 201
        
        # Verificar se a reserva foi criada corretamente
        reservations = requests.get(f'{BASE_URL}/reservations/user/{user_info["id"]}', headers=user_headers).json()
        assert len(reservations) > 0
        assert any(r['space_id'] == space_id for r in reservations)

    def test_pricing_and_payments_integration(self):
        """Testa integração entre serviços de preços e pagamentos"""
        
        # Setup: criar espaço e usuário
        admin_data = {
            'email': f'pricing_admin_{int(time.time())}@test.com',
            'password': 'admin123',
            'name': 'Pricing Admin',
            'role': 'admin'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=admin_data)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': admin_data['email'],
            'password': admin_data['password']
        })
        admin_headers = {'Authorization': f'Bearer {admin_login.json()["token"]}'}
        
        space_response = requests.post(f'{BASE_URL}/spaces', json={
            'name': f'Pricing Space {int(time.time())}',
            'description': 'Space for pricing test',
            'capacity': 6,
            'price_per_hour': 40.0
        }, headers=admin_headers)
        space_id = space_response.json()['id']
        
        user_data = {
            'email': f'pricing_user_{int(time.time())}@test.com',
            'password': 'user123',
            'name': 'Pricing User',
            'role': 'user'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=user_data)
        user_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        user_headers = {'Authorization': f'Bearer {user_login.json()["token"]}'}
        user_info = requests.get(f'{BASE_URL}/users/me', headers=user_headers).json()
        
        # 1. Calcular preço
        pricing_data = {
            'space_id': space_id,
            'start_time': '2024-12-03T13:00:00',
            'end_time': '2024-12-03T15:00:00',
            'user_plan': 'basic'
        }
        pricing_response = requests.post(f'{BASE_URL}/pricing/calc', json=pricing_data)
        assert pricing_response.status_code == 200
        total_price = pricing_response.json()['total']
        
        # 2. Criar reserva com o preço calculado
        reservation_response = requests.post(f'{BASE_URL}/reservations', json={
            'user_id': user_info['id'],
            'space_id': space_id,
            'start_time': '2024-12-03T13:00:00',
            'end_time': '2024-12-03T15:00:00',
            'total_price': total_price
        }, headers=user_headers)
        reservation_id = reservation_response.json()['id']
        
        # 3. Processar pagamento
        payment_response = requests.post(f'{BASE_URL}/payments/charge', json={
            'reservation_id': reservation_id,
            'amount': total_price,
            'method': 'credit_card'
        }, headers=user_headers)
        assert payment_response.status_code == 200
        
        payment_result = payment_response.json()
        assert payment_result['status'] == 'success'

    def test_checkin_and_notifications_integration(self):
        """Testa integração entre check-in e notificações"""
        
        # Setup completo
        admin_data = {
            'email': f'checkin_admin_{int(time.time())}@test.com',
            'password': 'admin123',
            'name': 'Checkin Admin',
            'role': 'admin'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=admin_data)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': admin_data['email'],
            'password': admin_data['password']
        })
        admin_headers = {'Authorization': f'Bearer {admin_login.json()["token"]}'}
        
        space_response = requests.post(f'{BASE_URL}/spaces', json={
            'name': f'Checkin Space {int(time.time())}',
            'description': 'Space for checkin test',
            'capacity': 4,
            'price_per_hour': 25.0
        }, headers=admin_headers)
        space_id = space_response.json()['id']
        
        user_data = {
            'email': f'checkin_user_{int(time.time())}@test.com',
            'password': 'user123',
            'name': 'Checkin User',
            'role': 'user'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=user_data)
        user_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        user_headers = {'Authorization': f'Bearer {user_login.json()["token"]}'}
        user_info = requests.get(f'{BASE_URL}/users/me', headers=user_headers).json()
        
        # Criar reserva
        reservation_response = requests.post(f'{BASE_URL}/reservations', json={
            'user_id': user_info['id'],
            'space_id': space_id,
            'start_time': '2024-12-04T10:00:00',
            'end_time': '2024-12-04T12:00:00',
            'total_price': 50.0
        }, headers=user_headers)
        reservation_id = reservation_response.json()['id']
        
        # Check-in (deve disparar notificação)
        checkin_response = requests.post(f'{BASE_URL}/checkin/{reservation_id}', headers=user_headers)
        assert checkin_response.status_code == 200
        
        # Check-out (deve disparar notificação)
        checkout_response = requests.post(f'{BASE_URL}/checkout/{reservation_id}', headers=user_headers)
        assert checkout_response.status_code == 200

    def test_analytics_and_financial_integration(self):
        """Testa integração entre analytics e dados financeiros"""
        
        # Criar admin
        admin_data = {
            'email': f'analytics_admin_{int(time.time())}@test.com',
            'password': 'admin123',
            'name': 'Analytics Admin',
            'role': 'admin'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=admin_data)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': admin_data['email'],
            'password': admin_data['password']
        })
        admin_headers = {'Authorization': f'Bearer {admin_login.json()["token"]}'}
        
        # Acessar analytics
        analytics_response = requests.get(f'{BASE_URL}/analytics/dashboard', headers=admin_headers)
        assert analytics_response.status_code == 200
        analytics_data = analytics_response.json()
        
        # Acessar dados financeiros
        revenue_response = requests.get(f'{BASE_URL}/financial/revenue', headers=admin_headers)
        assert revenue_response.status_code == 200
        revenue_data = revenue_response.json()
        
        expenses_response = requests.get(f'{BASE_URL}/financial/expenses', headers=admin_headers)
        assert expenses_response.status_code == 200
        expenses_data = expenses_response.json()
        
        # Verificar consistência dos dados
        assert 'total_reservations' in analytics_data
        assert 'total_revenue' in revenue_data
        assert 'total_expenses' in expenses_data

    def test_admin_operations_integration(self):
        """Testa operações administrativas integradas"""
        
        # Criar admin
        admin_data = {
            'email': f'admin_ops_{int(time.time())}@test.com',
            'password': 'admin123',
            'name': 'Admin Operations',
            'role': 'admin'
        }
        requests.post(f'{BASE_URL}/auth/signup', json=admin_data)
        admin_login = requests.post(f'{BASE_URL}/auth/login', json={
            'email': admin_data['email'],
            'password': admin_data['password']
        })
        admin_headers = {'Authorization': f'Bearer {admin_login.json()["token"]}'}
        
        # Listar usuários (admin)
        users_response = requests.get(f'{BASE_URL}/admin/users', headers=admin_headers)
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) > 0
        
        # Listar reservas (admin)
        reservations_response = requests.get(f'{BASE_URL}/admin/reservations', headers=admin_headers)
        assert reservations_response.status_code == 200
        reservations = reservations_response.json()
        assert isinstance(reservations, list)