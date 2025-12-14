# Troubleshooting - Deploy AWS

Este documento lista os problemas mais comuns no deploy para AWS e suas soluções.

## 🔍 Como diagnosticar problemas

### 1. Execute o script de verificação
```bash
python check-aws-status.py
```

### 2. Verifique os logs do GitHub Actions
- Vá para a aba **Actions** do seu repositório
- Clique no workflow que falhou
- Examine os logs de cada step

### 3. Verifique os logs dos containers no AWS
```bash
aws logs describe-log-groups --log-group-name-prefix "/ecs/coworkflow"
aws logs get-log-events --log-group-name "/ecs/coworkflow/api-gateway" --log-stream-name "STREAM_NAME"
```

## ❌ Problemas Comuns e Soluções

### 1. "Error: Service unavailable" ou containers não iniciam

**Sintomas:**
- Serviços ECS mostram 0/1 running
- Health checks falhando
- Aplicação não responde

**Possíveis causas:**
- Imagem Docker com problemas
- Variáveis de ambiente incorretas
- Problemas de conectividade com o banco

**Soluções:**
```bash
# 1. Verificar logs do container
aws logs get-log-events --log-group-name "/ecs/coworkflow/api-gateway" --log-stream-name "LATEST_STREAM"

# 2. Testar imagem localmente
docker run -p 8000:8000 322194580427.dkr.ecr.us-east-1.amazonaws.com/coworkflow/api-gateway:latest

# 3. Verificar variáveis de ambiente no Terraform
terraform plan -var="db_password=SUA_SENHA"
```

### 2. "Repository does not exist" no GitHub Actions

**Sintomas:**
- Erro ao fazer push da imagem Docker
- "repository coworkflow/SERVICE_NAME does not exist"

**Solução:**
```bash
# Aplicar o Terraform para criar os repositórios ECR
cd terraform
terraform apply -var="db_password=SUA_SENHA"
```

### 3. "Access Denied" no GitHub Actions

**Sintomas:**
- Erro de permissão ao acessar AWS
- "Unable to locate credentials"

**Soluções:**
1. Verificar se os secrets estão configurados no GitHub:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. Verificar permissões do usuário IAM:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:UpdateService",
                "ecs:DescribeServices"
            ],
            "Resource": [
                "arn:aws:ecs:*:*:service/coworkflow-cluster/*"
            ]
        }
    ]
}
```

### 4. Health Check falhando

**Sintomas:**
- Target Groups mostram "unhealthy"
- Load Balancer retorna 503

**Soluções:**
1. Verificar se os endpoints `/health` existem:
```bash
# Testar localmente
curl http://localhost:3000/health  # Frontend
curl http://localhost:8000/health  # API Gateway
```

2. Verificar configuração de portas:
- Frontend: porta 3000 (Dockerfile e ECS devem coincidir)
- API Gateway: porta 8000 (Dockerfile e ECS devem coincidir)

### 5. Banco de dados não conecta

**Sintomas:**
- Erro "connection refused" nos logs
- Aplicação não consegue acessar dados

**Soluções:**
1. Verificar se o RDS está disponível:
```bash
aws rds describe-db-instances --db-instance-identifier coworkflow-db
```

2. Verificar Security Groups:
- RDS deve permitir entrada na porta 5432 da VPC (10.0.0.0/16)
- ECS deve ter acesso de saída para todas as portas

3. Verificar variáveis de ambiente:
```bash
# No Terraform, verificar se estão corretas:
DB_HOST=coworkflow-db.XXXXX.us-east-1.rds.amazonaws.com
DB_NAME=coworkflow
DB_USER=postgres
DB_PASSWORD=SUA_SENHA
DB_PORT=5432
```

### 6. Load Balancer retorna 504 Gateway Timeout

**Sintomas:**
- Aplicação demora muito para responder
- Timeout errors

**Soluções:**
1. Aumentar timeout do health check:
```hcl
health_check {
  timeout = 10  # Aumentar de 5 para 10 segundos
  interval = 60 # Aumentar intervalo
}
```

2. Verificar se os containers têm recursos suficientes:
```hcl
cpu    = 512  # Aumentar de 256
memory = 1024 # Aumentar de 512
```

## 🔧 Comandos Úteis

### Verificar status dos serviços
```bash
# ECS Services
aws ecs list-services --cluster coworkflow-cluster
aws ecs describe-services --cluster coworkflow-cluster --services SERVICE_NAME

# Target Groups
aws elbv2 describe-target-groups --names coworkflow-tg-frontend coworkflow-tg-api
aws elbv2 describe-target-health --target-group-arn TARGET_GROUP_ARN

# RDS
aws rds describe-db-instances --db-instance-identifier coworkflow-db
```

### Forçar novo deployment
```bash
aws ecs update-service --cluster coworkflow-cluster --service SERVICE_NAME --force-new-deployment
```

### Ver logs em tempo real
```bash
# Listar log streams
aws logs describe-log-streams --log-group-name "/ecs/coworkflow/api-gateway"

# Ver logs
aws logs tail "/ecs/coworkflow/api-gateway" --follow
```

## 🆘 Quando pedir ajuda

Se os problemas persistirem, colete as seguintes informações:

1. Output do `python check-aws-status.py`
2. Logs do GitHub Actions (screenshot ou texto)
3. Logs dos containers AWS (últimas 50 linhas)
4. Output do `terraform plan`
5. Configuração dos secrets do GitHub

## 📞 Recursos Adicionais

- [AWS ECS Troubleshooting](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/troubleshooting.html)
- [GitHub Actions Logs](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/using-workflow-run-logs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)