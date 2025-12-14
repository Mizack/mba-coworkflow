# Configuração dos Secrets do GitHub

Para que o deploy funcione corretamente, você precisa configurar os seguintes secrets no seu repositório GitHub:

## Como configurar:

1. Vá para o seu repositório no GitHub
2. Clique em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Adicione os seguintes secrets:

## Secrets necessários:

### AWS_ACCESS_KEY_ID
- **Nome**: `AWS_ACCESS_KEY_ID`
- **Valor**: Sua Access Key ID da AWS (obtida do usuário IAM criado)

### AWS_SECRET_ACCESS_KEY
- **Nome**: `AWS_SECRET_ACCESS_KEY`
- **Valor**: Sua Secret Access Key da AWS (obtida do usuário IAM criado)

### AWS_REGION
- **Nome**: `AWS_REGION`
- **Valor**: `us-east-1` (ou a região que você está usando)

## Como obter as credenciais AWS:

1. Acesse o Console AWS
2. Vá para **IAM** > **Users**
3. Encontre o usuário `github-actions-deployer` (ou crie conforme o DEPLOY-AWS.md)
4. Vá na aba **Security credentials**
5. Clique em **Create access key**
6. Escolha **Command Line Interface (CLI)**
7. Copie a **Access key ID** e **Secret access key**

## Verificação:

Após configurar os secrets, o próximo push para a branch `main` deve executar o deploy automaticamente.

## Troubleshooting:

Se o deploy ainda falhar, verifique:
- Se as credenciais AWS estão corretas
- Se o usuário IAM tem as permissões necessárias
- Se a infraestrutura Terraform foi aplicada corretamente
- Se os repositórios ECR existem na AWS