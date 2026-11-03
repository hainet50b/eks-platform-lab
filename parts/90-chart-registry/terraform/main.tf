resource "aws_ecr_repository" "workload_spring_boot" {
  name                 = "charts/workload-spring-boot"
  image_tag_mutability = "IMMUTABLE"

  force_delete = true
}
