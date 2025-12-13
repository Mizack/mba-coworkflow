import pytest
import os
import sys

def pytest_configure(config):
    """Configuração global do pytest"""
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "ui: marca testes de UI"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )

@pytest.fixture(scope="session")
def test_config():
    """Configuração global para testes"""
    return {
        'base_url': 'http://localhost:8000',
        'frontend_url': 'http://localhost:3000',
        'test_user': {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'Test User'
        },
        'test_admin': {
            'email': 'admin@test.com',
            'password': 'admin123',
            'name': 'Admin User',
            'role': 'admin'
        }
    }

@pytest.fixture
def mock_services():
    """Mock para serviços externos"""
    class MockServices:
        def __init__(self):
            self.responses = {}
        
        def set_response(self, service, endpoint, response):
            self.responses[f"{service}_{endpoint}"] = response
        
        def get_response(self, service, endpoint):
            return self.responses.get(f"{service}_{endpoint}", {'status': 'ok'})
    
    return MockServices()

# Marcadores para organizar testes
pytestmark = [
    pytest.mark.unit,
    pytest.mark.integration,
    pytest.mark.ui
]