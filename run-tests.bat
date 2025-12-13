@echo off
echo ========================================
echo           COWORKFLOW TESTS
echo ========================================

echo.
echo Instalando dependencias de teste...
pip install -r requirements-test.txt

echo.
echo ========================================
echo         TESTES UNITARIOS
echo ========================================
python -m pytest tests/unit/test_simple_unit.py -v --tb=short

echo.
echo ========================================
echo       TESTES DE INTEGRACAO
echo ========================================
python -m pytest tests/integration/test_simple_integration.py -v --tb=short

echo.
echo ========================================
echo           TESTES DE UI
echo ========================================
echo Testes de UI requerem Selenium e ChromeDriver
echo Pulando testes de UI por enquanto...

echo.
echo ========================================
echo       RELATORIO DE COBERTURA
echo ========================================
python -m pytest tests/unit/test_simple_unit.py tests/integration/test_simple_integration.py --cov=. --cov-report=html --cov-report=term-missing

echo.
echo ========================================
echo         TESTES CONCLUIDOS
echo ========================================
echo Relatorio HTML disponivel em: htmlcov/index.html

pause