# Guia de Deploy AWS - CoworkFlow

Este documento detalha o roteiro para preparar a infraestrutura na AWS (Amazon Web Services) para hospedar a aplicação CoworkFlow utilizando uma arquitetura de microsserviços containerizados.

## 1. Visão Geral da Infraestrutura

A aplicação será hospedada utilizando os seguintes serviços gerenciados:

*   **AWS ECR (Elastic Container Registry):** Armazenamento das imagens Docker dos microsserviços.
*   **AWS ECS (Elastic Container Service) + Fargate:** Orquestração e execução dos containers sem necessidade de gerenciar servidores (Serverless).
*   **AWS RDS (Relational Database Service):** Banco de dados PostgreSQL gerenciado.
*   **AWS ALB (Application Load Balancer):** Distribuição de tráfego e roteamento para o API Gateway e Frontend.

## 2. Passo 1: Repositórios ECR

Você deve criar um repositório ECR privado para **cada** serviço listado abaixo. Isso pode ser feito via Console AWS ou CLI (`aws ecr create-repository --repository-name <NOME>`).

**Nomes dos Repositórios:**
1.  `coworkflow/frontend`
2.  `coworkflow/api-gateway`
3.  `coworkflow/ms-usuarios`
4.  `coworkflow/ms-espacos`
5.  `coworkflow/ms-reservas`
6.  `coworkflow/ms-pagamentos`
7.  `coworkflow/ms-precos`
8.  `coworkflow/ms-checkin`
9.  `coworkflow/ms-notificacoes`
10. `coworkflow/ms-financeiro`
11. `coworkflow/ms-analytics`

## 3. Passo 2: Banco de Dados (RDS)

Crie uma instância de banco de dados para a aplicação.

*   **Engine:** PostgreSQL (versão 13 ou superior recomendada).
*   **Template:** Free tier ou Production (conforme necessidade).
*   **Identificador:** `coworkflow-db`.
*   **Credenciais:**
    *   **Master username:** `postgres` (ou outro de sua escolha).
    *   **Master password:** Gere uma senha forte (será usada nas variáveis de ambiente).
*   **Public Access:** `No` (por segurança, o acesso deve ser apenas de dentro da VPC).
*   **Security Group:** Deve permitir entrada na porta `5432` vindo do Security Group do ECS.

> **Nota:** Após criar o RDS, anote o `Endpoint` (host) gerado.

## 4. Passo 3: Cluster ECS e Networking

1.  **Criar Cluster ECS:**
    *   Nome: `coworkflow-cluster`.
    *   Template: `Networking only` (Powered by AWS Fargate).

2.  **Application Load Balancer (ALB):**
    *   Crie um ALB internet-facing.
    *   Defina **Target Groups** (tipo IP) para os serviços que precisam de acesso externo (principalmente Frontend e API Gateway).
    *   Configure Listeners (HTTP/80 e HTTPS/443 se tiver certificado).

## 5. Passo 4: Task Definitions (Definição das Tarefas)

Para cada microsserviço, crie uma **Task Definition** no ECS (Fargate).

**Configuração Padrão Sugerida por Task:**
*   **CPU:** `.25 vCPU`
*   **Memory:** `0.5 GB`
*   **Container Image URI:** `<ID_DA_CONTA>.dkr.ecr.<REGIAO>.amazonaws.com/coworkflow/<NOME_DO_SERVICO>:latest`
*   **Port Mappings:** A porta interna que o container usa (ex: 5000, 3000, etc - verifique no `docker-compose.yml` ou Dockerfiles).

**Variáveis de Ambiente (Environment Variables):**
Todos os serviços que acessam o banco devem ter as seguintes variáveis configuradas na Task Definition:

| Variável | Valor (Exemplo) |
| :--- | :--- |
| `DB_HOST` | `coworkflow-db...rds.amazonaws.com` (Endpoint do RDS) |
| `DB_NAME` | `coworkflow` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | `<SUA_SENHA_DO_RDS>` |
| `FLASK_ENV` | `production` |

*O `ms-notificacoes` precisará de variáveis adicionais de SMTP se configurado.*

## 6. Passo 5: Services (Execução)

No cluster `coworkflow-cluster`, crie um **Service** para cada Task Definition criada.

*   **Launch Type:** Fargate.
*   **Desired Tasks:** 1 (ou mais para alta disponibilidade).
*   **Networking:** Selecione a mesma VPC e Subnets do ALB.
*   **Security Group:** Permitir entrada na porta do serviço vindo do ALB ou dos outros containers (para comunicação interna).

## 7. Passo 6: Configuração CI/CD (GitHub)

Para automatizar o deploy, vá as configurações do seu repositório no GitHub (`Settings > Secrets and variables > Actions`) e adicione:

*   `AWS_ACCESS_KEY_ID`: Chave de acesso do usuário IAM.
*   `AWS_SECRET_ACCESS_KEY`: Segredo do usuário IAM.
*   `AWS_REGION`: Ex: `us-east-1`.

**Permissões do Usuário IAM:**
O usuário deve ter permissões para:
*   `AmazonEC2ContainerRegistryPowerUser` (Ler/Escrever no ECR).
*   `AmazonECS_FullAccess` (Atualizar serviços no ECS).

---
**Fluxo Final:**
O pipeline (GitHub Actions) irá:
1.  Buildar a imagem Docker.
2.  Logar no ECR.
3.  Enviar (Push) a imagem para o ECR.
4.  Forçar uma atualização no Serviço ECS (`aws ecs update-service --force-new-deployment`), que baixará a nova imagem e substituirá os containers antigos.
