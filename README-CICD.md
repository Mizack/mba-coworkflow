# CI/CD Pipeline - CoworkFlow

## Pipelines Implementados

### 1. CI/CD Principal (`ci-cd.yml`)
**Triggers:**
- Push em `main` e `develop`
- Pull requests para `main`


**Jobs:**
1. **Lint** - Validação de código com flake8
2. **Test** - Execução de testes unitários
3. **Build** - Build de todas as imagens Docker
4. **Integration Test** - Testes de integração
5. **Deploy Staging** - Deploy automático em develop
6. **Deploy Production** - Deploy automático em main

### 2. Docker Publish (`docker-publish.yml`)
**Triggers:**
- Releases
- Manual (workflow_dispatch)

**Funcionalidades:**
- Build e push de imagens para GitHub Container Registry
- Versionamento automático (semver)
- Tags por branch, PR e SHA

### 3. Security Scan (`security-scan.yml`)
**Triggers:**
- Push em `main` e `develop`
- Agendado semanalmente (domingos)

**Verificações:**
- Scan de dependências Python (safety)
- Scan de vulnerabilidades em imagens Docker (Trivy)
- Upload de resultados para GitHub Security

### 4. Performance Tests (`performance-test.yml`)
**Triggers:**
- Agendado semanalmente (segundas)
- Manual (workflow_dispatch)

**Testes:**
- Load testing com k6
- 10 usuários virtuais
- Duração de 30 segundos

## Estrutura de Branches

```
main (production)
  ↑
develop (staging)
  ↑
feature/* (development)
```

## Fluxo de Deploy

### Development → Staging
```bash
git checkout develop
git merge feature/nova-funcionalidade
git push origin develop
# Deploy automático para staging
```

### Staging → Production
```bash
git checkout main
git merge develop
git push origin main
# Deploy automático para production
```

## Comandos Úteis

### Local
```bash
# Instalar dependências
make install

# Executar testes
make test

# Executar lint
make lint

# Build e start
make build
make up

# Stop e clean
make down
make clean
```

### GitHub Actions
```bash
# Ver status dos workflows
gh workflow list

# Executar workflow manualmente
gh workflow run docker-publish.yml

# Ver logs
gh run view
```

## Variáveis de Ambiente

### Secrets Necessários
- `GITHUB_TOKEN` - Automático (GitHub)
- `DOCKER_USERNAME` - Docker Hub (opcional)
- `DOCKER_PASSWORD` - Docker Hub (opcional)
- `AWS_ACCESS_KEY_ID` - AWS Deploy (opcional)
- `AWS_SECRET_ACCESS_KEY` - AWS Deploy (opcional)

## Métricas e Monitoramento

### Code Coverage
- Gerado automaticamente em cada PR
- Relatório disponível em `htmlcov/`

### Security Reports
- Disponível em GitHub Security tab
- Alertas automáticos para vulnerabilidades

### Performance Metrics
- Relatórios k6 em artifacts
- Threshold: 95% requests < 500ms

## Boas Práticas

1. **Sempre criar PR** para mudanças
2. **Aguardar CI passar** antes de merge
3. **Revisar security alerts** semanalmente
4. **Testar localmente** antes de push
5. **Usar semantic versioning** para releases

## Troubleshooting

### Pipeline falhou no lint
```bash
make lint
# Corrigir erros reportados
```

### Pipeline falhou nos testes
```bash
make test
# Verificar testes falhando
```

### Build Docker falhou
```bash
docker-compose build --no-cache
# Verificar Dockerfiles
```

## Próximos Passos

- [ ] Adicionar testes E2E com Selenium
- [ ] Implementar deploy em Kubernetes
- [ ] Adicionar monitoramento com Prometheus
- [ ] Configurar alertas no Slack
- [ ] Implementar rollback automático