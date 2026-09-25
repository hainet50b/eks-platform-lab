output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "cluster_security_group_id" {
  description = "ID of the cluster security group created by EKS"
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}
