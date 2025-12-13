# Executar CoworkFlow Localmente (Sem Docker)

## Pré-requisitos

```bash
pip install Flask werkzeug PyJWT flasgger requests
```

## Executar Todos os Serviços

### Windows
```bash
run-local.bat
```

### Manual (cada serviço em um terminal separado)

```bash
# Terminal 1 - MS-Usuarios
cd ms-usuarios
python app.py

# Terminal 2 - MS-Espacos
cd ms-espacos
python app.py

# Terminal 3 - MS-Reservas
cd ms-reservas
python app.py

# Terminal 4 - MS-Pagamentos
cd ms-pagamentos
python app.py

# Terminal 5 - MS-Precos
cd ms-precos
python app.py

# Terminal 6 - MS-Checkin
cd ms-checkin
python app.py

# Terminal 7 - MS-Notificacoes
cd ms-notificacoes
python app.py

# Terminal 8 - MS-Financeiro
cd ms-financeiro
python app.py

# Terminal 9 - MS-Analytics
cd ms-analytics
python app.py

# Terminal 10 - API Gateway
cd api-gateway
python app.py

# Terminal 11 - Frontend
cd frontend
python app.py
```

## Acessar

- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:8000
- **Swagger MS-Usuarios:** http://localhost:5001/apidocs
- **Swagger MS-Espacos:** http://localhost:5002/apidocs

## Testar API Gateway

```bash
python test-gateway.py
```

## Observações

- Todos os microsserviços usam banco de dados em memória
- Os dados são perdidos ao reiniciar os serviços
- Ideal para desenvolvimento e testes