resource "aws_ecs_cluster" "main" {
  name = "forgeops-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "forgeops-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "forgeops-container",
      image     = "ghcr.io/obsidianmaximus/forgeops:latest",
      essential = true,
      portMappings = [
        {
          containerPort = 5000,
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "main" {
  name            = "forgeops-service"
  cluster         = aws_ecs_cluster.main.id
  launch_type     = "FARGATE"
  desired_count   = 1
  task_definition = aws_ecs_task_definition.app.arn

  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "forgeops-container"
    container_port   = 5000
  }

  depends_on = [aws_lb_listener.http]
}