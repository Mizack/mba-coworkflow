# Guia de Testes - CoworkFlow

Este documento descreve a estrutura de testes implementada para o sistema CoworkFlow.

## Estrutura de Testes

```
tests/
├── unit/                    # Testes unitários
│   ├── test_api_gateway_unit.py
│   ├── test_ms_usuarios_unit.py
│   └── test_frontend_unit.py
├── integration/             # Testes de integração
│   ├── test_user_flow_integration.py
│   └── test_microservices_integration.py
├── ui/                      # Testes de interface
│   ├── test_frontend_ui.py
│   └── test_accessibility.py
├── performance/             # Testes de performance
│   └── test_load.py
└── conftest.py             # Configurações globais
```

## Tipos de Testes

### 1. Testes Unitários
Testam componentes individuais isoladamente:
- **API Gateway**: Autenticação, roteamento, validações
- **Microserviços**: Lógica de negócio, endpoints
- **Frontend**: Componentes, formulários, navegação

### 2. Testes de Integração
Testam fluxos completos entre serviços:
- Fluxo de registro e login
- Criação e gerenciamento de espaços
- Processo completo de reserva
- Check-in/check-out
- Notificações
- Analytics e relatórios financeiros

### 3. Testes de UI
Testam a interface do usuário:
- Navegação entre páginas
- Formulários e validações
- Responsividade
- Acessibilidade (WCAG)
- Fluxos de usuário completos

### 4. Testes de Performance
Testam carga e performance:
- Simulação de múltiplos usuários
- Cenários de pico de uso
- Tempo de resposta
- Throughput

## Executando os Testes

### Pré-requisitos
```bash
pip install -r requirements-test.txt
```

### Executar Todos os Testes
```bash
run-tests.bat
```

### Executar por Categoria

#### Testes Unitários
```bash
pytest tests/unit/ -v
```

#### Testes de Integração
```bash
# Iniciar serviços primeiro
python api-gateway/app.py &
python ms-usuarios/app.py &

pytest tests/integration/ -v
```

#### Testes de UI
```bash
# Iniciar frontend primeiro
python frontend/app.py &

pytest tests/ui/ -v
```

#### Testes de Performance
```bash
# Executar com Locust
locust -f tests/performance/test_load.py --host=http://localhost:8000
```

### Executar com Marcadores
```bash
pytest -m unit          # Apenas testes unitários
pytest -m integration   # Apenas testes de integração
pytest -m ui            # Apenas testes de UI
pytest -m slow          # Apenas testes lentos
```

## Cobertura de Código

### Gerar Relatório de Cobertura
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

O relatório HTML será gerado em `htmlcov/index.html`

### Metas de Cobertura
- **Unitários**: > 90%
- **Integração**: > 80%
- **Geral**: > 85%

## Configuração de CI/CD

Os testes estão integrados ao pipeline CI/CD em `.github/workflows/`:
- Execução automática em pull requests
- Relatórios de cobertura
- Notificações de falhas

## Dependências de Teste

### Principais Bibliotecas
- **pytest**: Framework de testes
- **requests**: Testes de API
- **selenium**: Testes de UI
- **locust**: Testes de performance
- **axe-selenium-python**: Testes de acessibilidade

### Ferramentas de Mock
- **unittest.mock**: Mocks para testes unitários
- **responses**: Mock de requisições HTTP

## Boas Práticas

### Testes Unitários
- Isolar dependências com mocks
- Testar casos de sucesso e falha
- Manter testes rápidos (< 1s cada)
- Um assert por teste quando possível

### Testes de Integração
- Usar dados de teste únicos
- Limpar estado entre testes
- Testar fluxos completos
- Verificar efeitos colaterais

### Testes de UI
- Usar seletores estáveis
- Aguardar elementos carregarem
- Testar em diferentes resoluções
- Verificar acessibilidade

### Testes de Performance
- Definir SLAs claros
- Monitorar recursos do sistema
- Testar cenários realistas
- Documentar resultados

## Troubleshooting

### Problemas Comuns

#### Testes de Integração Falhando
1. Verificar se todos os serviços estão rodando
2. Confirmar portas disponíveis
3. Verificar conectividade de rede

#### Testes de UI Falhando
1. Instalar ChromeDriver
2. Verificar se frontend está acessível
3. Ajustar timeouts se necessário

#### Testes Lentos
1. Usar marcador `@pytest.mark.slow`
2. Executar em paralelo com `pytest-xdist`
3. Otimizar setup/teardown

### Logs e Debug
```bash
pytest -v -s --tb=long    # Verbose com output completo
pytest --pdb              # Debugger em falhas
pytest --lf               # Executar apenas testes que falharam
```

## Métricas e Relatórios

### Relatórios Gerados
- **Cobertura**: `htmlcov/index.html`
- **Resultados**: `reports/pytest_report.html`
- **Performance**: Locust web interface

### Métricas Importantes
- Taxa de sucesso dos testes
- Tempo de execução
- Cobertura de código
- Performance (tempo de resposta, throughput)

## Contribuindo

### Adicionando Novos Testes
1. Seguir convenção de nomenclatura: `test_*.py`
2. Usar fixtures apropriadas
3. Adicionar marcadores relevantes
4. Documentar casos de teste complexos

### Atualizando Testes
1. Manter compatibilidade com CI/CD
2. Atualizar documentação
3. Verificar impacto na cobertura
4. Testar localmente antes do commit