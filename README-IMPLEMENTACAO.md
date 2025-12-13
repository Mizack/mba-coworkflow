# CoworkFlow - Implementação Completa

Sistema de gestão de coworkings implementado com arquitetura de microsserviços.

## Estrutura do Projeto

```
coworkflow/
├── ms-usuarios/          # Microsserviço de usuários e autenticação
├── ms-espacos/           # Microsserviço de espaços
├── ms-reservas/          # Microsserviço de reservas
├── ms-pagamentos/        # Microsserviço de pagamentos
├── ms-precos/            # Microsserviço de preços e planos
├── ms-checkin/           # Microsserviço de checkin/checkout
├── ms-notificacoes/      # Microsserviço de notificações
├── ms-financeiro/        # Microsserviço financeiro
├── ms-analytics/         # Microsserviço de analytics
├── api-gateway/          # API Gateway
├── frontend/             # Interface web
├── .github/workflows/    # Pipeline CI/CD
└── docker-compose.yml    # Orquestração Docker
```

## Como Executar

1. **Pré-requisitos:**
   - Docker e Docker Compose instalados
   - Git (opcional)

2. **Executar o sistema:**
   ```bash
   docker-compose up --build -d
   ```

3. **Acessar a aplicação:**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Swagger dos microsserviços: http://localhost:500X/apidocs

## Endpoints Principais

### Autenticação
- `POST /auth/signup` - Cadastro de usuário
- `POST /auth/login` - Login
- `GET /users/me` - Dados do usuário

### Espaços
- `GET /spaces` - Listar espaços
- `POST /spaces` - Criar espaço
- `GET /spaces/{id}` - Detalhes do espaço
- `GET /spaces/{id}/availability` - Verificar disponibilidade

### Reservas
- `POST /reservations` - Criar reserva
- `GET /reservations/{id}` - Detalhes da reserva
- `GET /reservations/user/{userId}` - Reservas do usuário
- `DELETE /reservations/{id}` - Cancelar reserva

### Pagamentos
- `POST /payments/charge` - Processar pagamento
- `POST /payments/refund` - Estornar pagamento

### Outros
- `POST /pricing/calc` - Calcular preço
- `POST /checkin/{reservationId}` - Check-in
- `POST /notify/email` - Enviar e-mail
- `GET /analytics/dashboard` - Dashboard analytics
- `GET /financial/revenue` - Relatório financeiro

## Tecnologias Utilizadas

- **Backend:** Python + Flask
- **Banco de Dados:** PostgreSQL
- **Frontend:** HTML + Bootstrap 5 + Jinja2
- **Containerização:** Docker + Docker Compose
- **API Documentation:** Swagger/OpenAPI
- **CI/CD:** GitHub Actions
- **Arquitetura:** Microsserviços + API Gateway

## Funcionalidades Implementadas

✅ Autenticação JWT  
✅ CRUD de usuários  
✅ CRUD de espaços  
✅ Sistema de reservas  
✅ Processamento de pagamentos  
✅ Cálculo de preços  
✅ Check-in/Check-out  
✅ Sistema de notificações  
✅ Relatórios financeiros  
✅ Analytics e dashboard  
✅ API Gateway com proxy  
✅ Interface web responsiva  
✅ Documentação Swagger  
✅ Pipeline CI/CD  

## Próximos Passos

- Implementar testes unitários e de integração
- Adicionar autenticação OAuth2
- Implementar cache com Redis
- Adicionar monitoramento com Prometheus
- Configurar logging centralizado
- Implementar backup automático dos bancos