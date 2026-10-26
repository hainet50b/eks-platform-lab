output "repository_url" {
  description = "URL of the ECR repository for the application"
  value       = aws_ecr_repository.spring_boot.repository_url
}
