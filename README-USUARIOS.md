# Sistema de Usuários - CoworkFlow

## Tipos de Usuário

### 1. Usuário Comum (user)
**Funcionalidades:**
- ✅ Cadastro e login
- ✅ Visualizar espaços disponíveis
- ✅ Fazer reservas
- ✅ Gerenciar suas reservas
- ✅ Check-in/Check-out
- ✅ Cancelar reservas
- ✅ Ver dashboard pessoal

**Acesso:**
- Dashboard: `/dashboard`
- Espaços: `/spaces`
- Reservas: `/reservations`

### 2. Administrador (admin)
**Funcionalidades:**
- ✅ Todas as funcionalidades de usuário comum
- ✅ Painel administrativo completo
- ✅ Criar e gerenciar espaços
- ✅ Visualizar todas as reservas
- ✅ Gerenciar usuários
- ✅ Relatórios financeiros
- ✅ Analytics e métricas
- ✅ Enviar notificações

**Acesso:**
- Painel Admin: `/admin`
- Gerenciar Usuários: `/admin/users`
- Gerenciar Reservas: `/admin/reservations`
- Financeiro: `/financial`

## Como Criar Usuários

### Usuário Comum
```json
POST /auth/signup
{
  "email": "usuario@exemplo.com",
  "password": "senha123",
  "name": "João Silva",
  "role": "user"
}
```

### Administrador
```json
POST /auth/signup
{
  "email": "admin@exemplo.com",
  "password": "admin123",
  "name": "Admin Sistema",
  "role": "admin"
}
```

## Login
```json
POST /auth/login
{
  "email": "usuario@exemplo.com",
  "password": "senha123"
}

Response:
{
  "token": "eyJ...",
  "role": "user"
}
```

## Fluxo de Navegação

### Usuário Comum:
1. Cadastro → Login
2. Dashboard → Ver métricas pessoais
3. Espaços → Escolher espaço
4. Reservar → Pagar
5. Minhas Reservas → Check-in/Check-out

### Administrador:
1. Cadastro → Login
2. Painel Admin → Visão geral do sistema
3. Gerenciar Espaços → CRUD completo
4. Gerenciar Reservas → Todas as reservas
5. Financeiro → Receitas e despesas
6. Notificações → Enviar para usuários