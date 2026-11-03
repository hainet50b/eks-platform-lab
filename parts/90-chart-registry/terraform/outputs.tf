output "repository_url" {
  description = "URL of the ECR repository for the workload chart"
  value       = aws_ecr_repository.workload_spring_boot.repository_url
}
