resource "aws_ecr_repository" "spring_boot" {
  name                 = "team-a/spring-boot"
  image_tag_mutability = "IMMUTABLE"

  force_delete = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "spring_boot" {
  repository = aws_ecr_repository.spring_boot.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Archive the releases older than the last 10"
        selection = {
          tagStatus      = "tagged"
          tagPatternList = ["*.*.*"]
          countType      = "imageCountMoreThan"
          countNumber    = 10
        }
        action = {
          type               = "transition"
          targetStorageClass = "archive"
        }
      },
      {
        rulePriority = 2
        description  = "Expire the builds older than the last 10"
        selection = {
          tagStatus      = "tagged"
          tagPatternList = ["sha-*"]
          countType      = "imageCountMoreThan"
          countNumber    = 10
        }
        action = {
          type = "expire"
        }
      },
    ]
  })
}
