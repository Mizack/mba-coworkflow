import random
import string

try:
    from locust import HttpUser, task, between
except ImportError:
    # Mock classes for when locust is not available
    class HttpUser:
        wait_time = None
        client = None
        def on_start(self): pass
    
    def task(weight=1):
        def decorator(func):
            return func
        return decorator
    
    def between(min_wait, max_wait):
        return None

class CoworkflowUser(HttpUser):
    """Teste de carga para o sistema CoworkFlow"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup inicial para cada usuário"""
        self.token = None
        self.user_id = None
        self.signup_and_login()
    
    def signup_and_login(self):
        """Registra e faz login de um usuário"""
        # Gerar email único
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"loadtest_{random_suffix}@test.com"
        
        # Registrar usuário
        signup_data = {
            "email": email,
            "password": "test123",
            "name": f"Load Test User {random_suffix}",
            "role": "user"
        }
        
        with self.client.post("/auth/signup", json=signup_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400:  # Usuário já existe
                response.success()
            else:
                response.failure(f"Signup failed: {response.status_code}")
        
        # Fazer login
        login_data = {
            "email": email,
            "password": "test123"
        }
        
        with self.client.post("/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    def get_headers(self):
        """Retorna headers com token de autenticação"""
        return {'Authorization': f'Bearer {self.token}'} if self.token else {}
    
    @task(3)
    def view_spaces(self):
        """Visualizar lista de espaços"""
        self.client.get("/spaces")
    
    @task(2)
    def view_user_profile(self):
        """Visualizar perfil do usuário"""
        if self.token:
            self.client.get("/users/me", headers=self.get_headers())
    
    @task(2)
    def view_reservations(self):
        """Visualizar reservas do usuário"""
        if self.token:
            self.client.get("/reservations", headers=self.get_headers())
    
    @task(1)
    def create_reservation(self):
        """Criar uma nova reserva"""
        if not self.token:
            return
        
        # Primeiro, obter lista de espaços
        spaces_response = self.client.get("/spaces")
        if spaces_response.status_code != 200:
            return
        
        spaces = spaces_response.json()
        if not spaces:
            return
        
        # Selecionar espaço aleatório
        space = random.choice(spaces)
        space_id = space['id']
        
        # Obter dados do usuário
        user_response = self.client.get("/users/me", headers=self.get_headers())
        if user_response.status_code != 200:
            return
        
        user_data = user_response.json()
        
        # Calcular preço
        pricing_data = {
            'space_id': space_id,
            'start_time': '2024-12-01T10:00:00',
            'end_time': '2024-12-01T12:00:00',
            'user_plan': 'basic'
        }
        
        pricing_response = self.client.post("/pricing/calc", json=pricing_data)
        if pricing_response.status_code != 200:
            return
        
        total_price = pricing_response.json()['total']
        
        # Criar reserva
        reservation_data = {
            'user_id': user_data['id'],
            'space_id': space_id,
            'start_time': '2024-12-01T10:00:00',
            'end_time': '2024-12-01T12:00:00',
            'total_price': total_price
        }
        
        with self.client.post("/reservations", json=reservation_data, headers=self.get_headers(), catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                
                # Processar pagamento
                reservation_id = response.json()['id']
                payment_data = {
                    'reservation_id': reservation_id,
                    'amount': total_price,
                    'method': 'credit_card'
                }
                self.client.post("/payments/charge", json=payment_data, headers=self.get_headers())
            else:
                response.failure(f"Reservation creation failed: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Verificar saúde do sistema"""
        self.client.get("/health")

class AdminUser(HttpUser):
    """Usuário administrador para testes de carga"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Setup inicial para admin"""
        self.token = None
        self.signup_and_login_admin()
    
    def signup_and_login_admin(self):
        """Registra e faz login como admin"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"admin_loadtest_{random_suffix}@test.com"
        
        # Registrar admin
        signup_data = {
            "email": email,
            "password": "admin123",
            "name": f"Admin Load Test {random_suffix}",
            "role": "admin"
        }
        
        self.client.post("/auth/signup", json=signup_data)
        
        # Fazer login
        login_data = {
            "email": email,
            "password": "admin123"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get('token')
    
    def get_headers(self):
        """Retorna headers com token de autenticação"""
        return {'Authorization': f'Bearer {self.token}'} if self.token else {}
    
    @task(2)
    def view_admin_users(self):
        """Visualizar lista de usuários (admin)"""
        if self.token:
            self.client.get("/admin/users", headers=self.get_headers())
    
    @task(2)
    def view_admin_reservations(self):
        """Visualizar todas as reservas (admin)"""
        if self.token:
            self.client.get("/admin/reservations", headers=self.get_headers())
    
    @task(1)
    def create_space(self):
        """Criar novo espaço (admin)"""
        if not self.token:
            return
        
        space_data = {
            'name': f'Load Test Space {random.randint(1000, 9999)}',
            'description': 'Space created during load test',
            'capacity': random.randint(5, 20),
            'price_per_hour': random.uniform(20.0, 50.0)
        }
        
        self.client.post("/spaces", json=space_data, headers=self.get_headers())
    
    @task(1)
    def view_analytics(self):
        """Visualizar analytics (admin)"""
        if self.token:
            self.client.get("/analytics/dashboard", headers=self.get_headers())
    
    @task(1)
    def view_financial(self):
        """Visualizar dados financeiros (admin)"""
        if self.token:
            self.client.get("/financial/revenue", headers=self.get_headers())
            self.client.get("/financial/expenses", headers=self.get_headers())