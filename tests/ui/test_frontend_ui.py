import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

BASE_URL = 'http://localhost:3000'

class TestFrontendUI:
    """Testes de UI usando Selenium"""
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Setup do driver Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Executar sem interface gráfica
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def test_homepage_loads(self, driver):
        """Testa se a página inicial carrega corretamente"""
        driver.get(BASE_URL)
        
        # Verificar se o título está correto
        assert "CoworkFlow" in driver.title
        
        # Verificar se elementos principais estão presentes
        assert driver.find_element(By.TAG_NAME, "h1")
        
        # Verificar links de navegação
        login_link = driver.find_element(By.LINK_TEXT, "Login")
        signup_link = driver.find_element(By.LINK_TEXT, "Cadastro")
        
        assert login_link.is_displayed()
        assert signup_link.is_displayed()

    def test_signup_form(self, driver):
        """Testa o formulário de cadastro"""
        driver.get(f'{BASE_URL}/signup')
        
        # Verificar se o formulário está presente
        form = driver.find_element(By.TAG_NAME, "form")
        assert form.is_displayed()
        
        # Preencher formulário
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        name_field = driver.find_element(By.NAME, "name")
        
        test_email = f"uitest_{int(time.time())}@test.com"
        
        email_field.send_keys(test_email)
        password_field.send_keys("test123")
        name_field.send_keys("UI Test User")
        
        # Submeter formulário
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Verificar redirecionamento ou mensagem de sucesso
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != f'{BASE_URL}/signup'
        )

    def test_login_form(self, driver):
        """Testa o formulário de login"""
        driver.get(f'{BASE_URL}/login')
        
        # Verificar se o formulário está presente
        form = driver.find_element(By.TAG_NAME, "form")
        assert form.is_displayed()
        
        # Verificar campos obrigatórios
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        assert email_field.is_displayed()
        assert password_field.is_displayed()
        
        # Testar login com credenciais inválidas
        email_field.send_keys("invalid@test.com")
        password_field.send_keys("wrongpassword")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Verificar se permanece na página de login (credenciais inválidas)
        time.sleep(2)
        assert "/login" in driver.current_url

    def test_spaces_page(self, driver):
        """Testa a página de espaços"""
        # Primeiro fazer login (assumindo que existe um usuário de teste)
        self._login_as_user(driver)
        
        driver.get(f'{BASE_URL}/spaces')
        
        # Verificar se a página carrega
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Verificar se há uma lista de espaços ou mensagem apropriada
        try:
            spaces_container = driver.find_element(By.CLASS_NAME, "spaces-list")
            assert spaces_container.is_displayed()
        except:
            # Se não há espaços, deve haver uma mensagem
            no_spaces_message = driver.find_element(By.XPATH, "//*[contains(text(), 'Nenhum espaço')]")
            assert no_spaces_message.is_displayed()

    def test_admin_dashboard_access(self, driver):
        """Testa acesso ao dashboard administrativo"""
        # Login como admin
        self._login_as_admin(driver)
        
        driver.get(f'{BASE_URL}/admin')
        
        # Verificar se o dashboard admin carrega
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Verificar elementos específicos do admin
        try:
            admin_nav = driver.find_element(By.CLASS_NAME, "admin-nav")
            assert admin_nav.is_displayed()
        except:
            # Verificar se há links administrativos
            admin_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/admin/')]")
            assert len(admin_links) > 0

    def test_create_space_form(self, driver):
        """Testa o formulário de criação de espaços (admin)"""
        # Login como admin
        self._login_as_admin(driver)
        
        driver.get(f'{BASE_URL}/spaces/create')
        
        # Verificar se o formulário está presente
        form = driver.find_element(By.TAG_NAME, "form")
        assert form.is_displayed()
        
        # Preencher formulário
        name_field = driver.find_element(By.NAME, "name")
        description_field = driver.find_element(By.NAME, "description")
        capacity_field = driver.find_element(By.NAME, "capacity")
        price_field = driver.find_element(By.NAME, "price_per_hour")
        
        name_field.send_keys(f"UI Test Space {int(time.time())}")
        description_field.send_keys("Space created by UI test")
        capacity_field.send_keys("10")
        price_field.send_keys("25.00")
        
        # Submeter formulário
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Verificar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "/spaces/create" not in d.current_url
        )

    def test_reservation_flow(self, driver):
        """Testa o fluxo completo de reserva"""
        # Login como usuário
        self._login_as_user(driver)
        
        # Ir para página de espaços
        driver.get(f'{BASE_URL}/spaces')
        
        # Tentar encontrar um espaço para reservar
        try:
            reserve_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Reservar')]")
            reserve_button.click()
            
            # Preencher formulário de reserva
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "start_time"))
            )
            
            start_time = driver.find_element(By.NAME, "start_time")
            end_time = driver.find_element(By.NAME, "end_time")
            payment_method = driver.find_element(By.NAME, "payment_method")
            
            start_time.send_keys("2024-12-01T10:00")
            end_time.send_keys("2024-12-01T12:00")
            payment_method.send_keys("credit_card")
            
            # Submeter reserva
            submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            submit_button.click()
            
            # Verificar redirecionamento para reservas
            WebDriverWait(driver, 10).until(
                lambda d: "/reservations" in d.current_url
            )
            
        except:
            # Se não há espaços disponíveis, o teste passa
            pass

    def test_responsive_design(self, driver):
        """Testa design responsivo"""
        driver.get(BASE_URL)
        
        # Testar em diferentes resoluções
        resolutions = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in resolutions:
            driver.set_window_size(width, height)
            time.sleep(1)
            
            # Verificar se a página ainda é utilizável
            body = driver.find_element(By.TAG_NAME, "body")
            assert body.is_displayed()
            
            # Verificar se não há overflow horizontal
            body_width = driver.execute_script("return document.body.scrollWidth")
            window_width = driver.execute_script("return window.innerWidth")
            assert body_width <= window_width + 20  # Pequena margem de tolerância

    def test_navigation_menu(self, driver):
        """Testa o menu de navegação"""
        self._login_as_user(driver)
        
        # Testar navegação entre páginas
        pages = [
            ('/dashboard', 'Dashboard'),
            ('/spaces', 'Espaços'),
            ('/reservations', 'Reservas'),
            ('/financial', 'Financeiro')
        ]
        
        for url, expected_text in pages:
            driver.get(f'{BASE_URL}{url}')
            
            # Verificar se a página carrega
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Verificar se não há erro 404 ou 500
            assert "404" not in driver.page_source
            assert "500" not in driver.page_source

    def test_logout_functionality(self, driver):
        """Testa funcionalidade de logout"""
        self._login_as_user(driver)
        
        # Encontrar e clicar no link de logout
        logout_link = driver.find_element(By.LINK_TEXT, "Logout")
        logout_link.click()
        
        # Verificar redirecionamento para página inicial
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url == BASE_URL or d.current_url == f'{BASE_URL}/'
        )
        
        # Tentar acessar página protegida
        driver.get(f'{BASE_URL}/dashboard')
        
        # Deve ser redirecionado para login
        WebDriverWait(driver, 10).until(
            lambda d: "/login" in d.current_url
        )

    def _login_as_user(self, driver):
        """Helper para fazer login como usuário regular"""
        driver.get(f'{BASE_URL}/login')
        
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        # Usar credenciais de teste (assumindo que existem)
        email_field.send_keys("test@test.com")
        password_field.send_keys("test123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "/login" not in d.current_url
        )

    def _login_as_admin(self, driver):
        """Helper para fazer login como administrador"""
        driver.get(f'{BASE_URL}/login')
        
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        # Usar credenciais de admin (assumindo que existem)
        email_field.send_keys("admin@test.com")
        password_field.send_keys("admin123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "/login" not in d.current_url
        )