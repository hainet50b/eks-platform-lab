data "aws_caller_identity" "current" {}

data "terraform_remote_state" "eks_cluster" {
  backend = "s3"

  config = {
    bucket = "eks-platform-lab-terraform-state-${data.aws_caller_identity.current.account_id}"
    key    = "parts/20-eks-cluster/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

data "aws_eks_cluster" "this" {
  name = data.terraform_remote_state.eks_cluster.outputs.cluster_name
}

# The add-on version that AWS marks as the default for the cluster's Kubernetes version.
data "aws_eks_addon_version" "metrics_server" {
  addon_name         = "metrics-server"
  kubernetes_version = data.aws_eks_cluster.this.version
  most_recent        = false
}

resource "aws_eks_addon" "metrics_server" {
  cluster_name  = data.aws_eks_cluster.this.name
  addon_name    = "metrics-server"
  addon_version = data.aws_eks_addon_version.metrics_server.version

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  # The default tolerations already allow the taint of the NodePool system.
  configuration_values = jsonencode({
    nodeSelector = {
      "karpenter.sh/nodepool" = "system"
    }
  })
}
