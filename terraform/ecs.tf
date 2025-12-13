# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

# Capacidade Providers (opcional, mas bom ter explícito)
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# Security Group para os Containers
resource "aws_security_group" "ecs_tasks_sg" {
  name        = "${var.project_name}-ecs-tasks-sg"
  description = "Security Group for ECS Tasks"
  vpc_id      = aws_vpc.main.id

  # Permitir entrada apenas do ALB (na porta 8000 e 80/3000)
  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }
  
  # Permitir comunicação entre os próprios containers (Service Discovery seria ideal, mas SG resolve básico)
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Lista de Serviços para Iteração
locals {
  services = {
    "frontend"        = { port = 80, target_group = aws_lb_target_group.frontend.arn }
    "api-gateway"     = { port = 8000, target_group = aws_lb_target_group.api_gateway.arn }
    "ms-usuarios"     = { port = 5000, target_group = null }
    "ms-espacos"      = { port = 5000, target_group = null }
    "ms-reservas"     = { port = 5000, target_group = null }
    "ms-pagamentos"   = { port = 5000, target_group = null }
    "ms-precos"       = { port = 5000, target_group = null }
    "ms-checkin"      = { port = 5000, target_group = null }
    "ms-notificacoes" = { port = 5000, target_group = null }
    "ms-financeiro"   = { port = 5000, target_group = null }
    "ms-analytics"    = { port = 5000, target_group = null }
  }
}

# Role de Execução (Permite ao ECS baixar imagens do ECR e criar Logs)
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Logs no CloudWatch
resource "aws_cloudwatch_log_group" "logs" {
  for_each = local.services
  name     = "/ecs/${var.project_name}/${each.key}"
  retention_in_days = 7
}

# Task Definitions
resource "aws_ecs_task_definition" "main" {
  for_each = local.services

  family                   = "${each.key}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  # Inicialmente usamos NGINX pois suas imagens ainda não existem no ECR.
  # O CI/CD irá atualizar isso para a imagem real.
  container_definitions = jsonencode([
    {
      name      = "${each.key}-container"
      image     = "${aws_ecr_repository.services[each.key].repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = each.value.port
          hostPort      = each.value.port
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}/${each.key}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        # Injetamos o host do banco para todos (mesmo que alguns não usem)
        { name = "DB_HOST", value = aws_db_instance.postgres.address },
        { name = "DB_USER", value = var.db_username },
        { name = "DB_PASSWORD", value = var.db_password }
      ]
    }
  ])
}

# ECS Services
resource "aws_ecs_service" "main" {
  for_each = local.services

  name            = "${each.key}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main[each.key].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_a.id, aws_subnet.public_b.id]
    security_groups  = [aws_security_group.ecs_tasks_sg.id]
    assign_public_ip = true # Necessário para baixar imagem Docker (sem NAT Gateway)
  }

  # Configuração Condicional de Load Balancer
  dynamic "load_balancer" {
    for_each = each.value.target_group != null ? [1] : []
    content {
      target_group_arn = each.value.target_group
      container_name   = "${each.key}-container"
      container_port   = each.value.port
    }
  }

  # Ignorar mudanças na Task Definition (pois o CI/CD vai alterá-la externamente)
  lifecycle {
    ignore_changes = [task_definition]
  }
}
