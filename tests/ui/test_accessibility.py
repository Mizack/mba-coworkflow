import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from axe_selenium_python import Axe

BASE_URL = 'http://localhost:3000'

class TestAccessibility:
    """Testes de acessibilidade usando axe-core"""
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Setup do driver Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def test_homepage_accessibility(self, driver):
        """Testa acessibilidade da página inicial"""
        driver.get(BASE_URL)
        
        axe = Axe(driver)
        axe.inject()
        
        results = axe.run()
        
        # Verificar se não há violações críticas
        violations = results['violations']
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]
        
        if critical_violations:
            print("Violações de acessibilidade encontradas:")
            for violation in critical_violations:
                print(f"- {violation['description']} (Impacto: {violation['impact']})")
        
        assert len(critical_violations) == 0, f"Encontradas {len(critical_violations)} violações críticas de acessibilidade"

    def test_login_page_accessibility(self, driver):
        """Testa acessibilidade da página de login"""
        driver.get(f'{BASE_URL}/login')
        
        axe = Axe(driver)
        axe.inject()
        
        results = axe.run()
        violations = results['violations']
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]
        
        assert len(critical_violations) == 0, f"Encontradas {len(critical_violations)} violações críticas de acessibilidade"

    def test_signup_page_accessibility(self, driver):
        """Testa acessibilidade da página de cadastro"""
        driver.get(f'{BASE_URL}/signup')
        
        axe = Axe(driver)
        axe.inject()
        
        results = axe.run()
        violations = results['violations']
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]
        
        assert len(critical_violations) == 0, f"Encontradas {len(critical_violations)} violações críticas de acessibilidade"

    def test_keyboard_navigation(self, driver):
        """Testa navegação por teclado"""
        driver.get(BASE_URL)
        
        # Verificar se elementos focáveis têm indicadores visuais de foco
        focusable_elements = driver.find_elements(By.CSS_SELECTOR, 
            "a, button, input, select, textarea, [tabindex]:not([tabindex='-1'])")
        
        for element in focusable_elements[:5]:  # Testar apenas os primeiros 5 elementos
            try:
                element.click()  # Simular foco
                
                # Verificar se o elemento tem outline ou algum indicador de foco
                outline = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).outline;", element
                )
                box_shadow = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).boxShadow;", element
                )
                
                # Deve ter pelo menos um indicador de foco
                has_focus_indicator = (
                    outline and outline != 'none' and outline != 'rgb(0, 0, 0) none 0px'
                ) or (
                    box_shadow and box_shadow != 'none'
                )
                
                if not has_focus_indicator:
                    print(f"Elemento sem indicador de foco: {element.tag_name}")
                
            except:
                continue  # Ignorar elementos que não podem receber foco

    def test_form_labels(self, driver):
        """Testa se formulários têm labels apropriados"""
        pages_with_forms = [
            f'{BASE_URL}/login',
            f'{BASE_URL}/signup'
        ]
        
        for page_url in pages_with_forms:
            driver.get(page_url)
            
            # Encontrar todos os inputs
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='password'], textarea, select")
            
            for input_element in inputs:
                input_id = input_element.get_attribute('id')
                input_name = input_element.get_attribute('name')
                
                # Verificar se há label associado
                label_found = False
                
                if input_id:
                    try:
                        label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        label_found = True
                    except:
                        pass
                
                # Verificar aria-label ou aria-labelledby
                aria_label = input_element.get_attribute('aria-label')
                aria_labelledby = input_element.get_attribute('aria-labelledby')
                
                has_accessible_name = label_found or aria_label or aria_labelledby
                
                if not has_accessible_name:
                    print(f"Input sem label acessível: {input_name or input_id or 'sem identificador'}")

    def test_color_contrast(self, driver):
        """Testa contraste de cores (básico)"""
        driver.get(BASE_URL)
        
        # Verificar elementos de texto principais
        text_elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, p, a, button, label")
        
        for element in text_elements[:10]:  # Testar apenas os primeiros 10 elementos
            try:
                # Obter cores de texto e fundo
                color = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).color;", element
                )
                background_color = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).backgroundColor;", element
                )
                
                # Verificação básica - cores não devem ser iguais
                if color and background_color and color != background_color:
                    # Se chegou aqui, pelo menos as cores são diferentes
                    continue
                    
            except:
                continue

    def test_alt_text_images(self, driver):
        """Testa se imagens têm texto alternativo"""
        driver.get(BASE_URL)
        
        images = driver.find_elements(By.TAG_NAME, "img")
        
        for img in images:
            alt_text = img.get_attribute('alt')
            role = img.get_attribute('role')
            aria_label = img.get_attribute('aria-label')
            
            # Imagens decorativas podem ter alt="" ou role="presentation"
            is_decorative = (
                alt_text == "" or 
                role == "presentation" or 
                role == "none"
            )
            
            # Imagens informativas devem ter alt text ou aria-label
            has_accessible_name = alt_text or aria_label
            
            if not is_decorative and not has_accessible_name:
                src = img.get_attribute('src')
                print(f"Imagem sem texto alternativo: {src}")

    def test_heading_structure(self, driver):
        """Testa estrutura hierárquica de cabeçalhos"""
        pages_to_test = [
            BASE_URL,
            f'{BASE_URL}/login',
            f'{BASE_URL}/signup'
        ]
        
        for page_url in pages_to_test:
            driver.get(page_url)
            
            headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            
            if not headings:
                continue
            
            # Verificar se há pelo menos um h1
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            assert len(h1_elements) >= 1, f"Página {page_url} deve ter pelo menos um h1"
            
            # Verificar ordem hierárquica (simplificado)
            heading_levels = []
            for heading in headings:
                level = int(heading.tag_name[1])  # Extrair número do h1, h2, etc.
                heading_levels.append(level)
            
            # Primeiro cabeçalho deve ser h1
            if heading_levels:
                assert heading_levels[0] == 1, f"Primeiro cabeçalho deve ser h1 em {page_url}"