variable "aws_region" {
  description = "Região da AWS"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  default     = "coworkflow"
}

variable "db_username" {
  description = "Usuário do Banco de Dados"
  default     = "postgres"
}

variable "db_password" {
  description = "Senha do Banco de Dados"
  type        = string
  sensitive   = true
}

variable "image_tag" {
  description = "Tag usada para imagens Docker (ex: commit SHA ou 'latest')"
  default     = "latest"
}
