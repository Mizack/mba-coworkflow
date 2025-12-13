@echo off
echo Iniciando microsserviços CoworkFlow...

start "MS-Usuarios" cmd /k "cd ms-usuarios && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Espacos" cmd /k "cd ms-espacos && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Reservas" cmd /k "cd ms-reservas && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Pagamentos" cmd /k "cd ms-pagamentos && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Precos" cmd /k "cd ms-precos && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Checkin" cmd /k "cd ms-checkin && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Notificacoes" cmd /k "cd ms-notificacoes && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Financeiro" cmd /k "cd ms-financeiro && python app.py"
timeout /t 2 /nobreak >nul

start "MS-Analytics" cmd /k "cd ms-analytics && python app.py"
timeout /t 2 /nobreak >nul

start "API-Gateway" cmd /k "cd api-gateway && python app.py"
timeout /t 2 /nobreak >nul

start "Frontend" cmd /k "cd frontend && python app.py"

echo Todos os serviços foram iniciados!
echo API Gateway: http://localhost:8000
echo Frontend: http://localhost:3000