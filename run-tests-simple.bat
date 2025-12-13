@echo off
echo ========================================
echo      COWORKFLOW TESTS - SIMPLIFICADO
echo ========================================

echo.
echo Executando testes funcionais...
python -m pytest tests/unit/test_simple_unit.py tests/integration/test_simple_integration.py -v --cov=. --cov-report=html --cov-report=term-missing

echo.
echo ========================================
echo         TESTES CONCLUIDOS
echo ========================================
echo Relatorio HTML disponivel em: htmlcov/index.html
echo.
echo Resumo:
echo - 10 testes unitarios
echo - 6 testes de integracao  
echo - Total: 16 testes funcionais
echo.

pause