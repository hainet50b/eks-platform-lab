output "data_subnet_ids" {
  description = "IDs of the data subnets, in the order of ap-northeast-1a and ap-northeast-1c"
  value       = [for az in ["ap-northeast-1a", "ap-northeast-1c"] : aws_subnet.data[az].id]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets, in the order of ap-northeast-1a and ap-northeast-1c"
  value       = [for az in ["ap-northeast-1a", "ap-northeast-1c"] : aws_subnet.private[az].id]
}

output "public_subnet_ids" {
  description = "IDs of the public subnets, in the order of ap-northeast-1a and ap-northeast-1c"
  value       = [for az in ["ap-northeast-1a", "ap-northeast-1c"] : aws_subnet.public[az].id]
}

output "vpc_cidr_block" {
  description = "IPv4 CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}
