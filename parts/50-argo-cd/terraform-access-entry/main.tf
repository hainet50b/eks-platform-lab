data "aws_caller_identity" "current" {}

data "terraform_remote_state" "eks_cluster" {
  backend = "s3"

  config = {
    bucket = "eks-platform-lab-terraform-state-${data.aws_caller_identity.current.account_id}"
    key    = "parts/20-eks-cluster/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

data "aws_iam_role" "argocd" {
  name = "eks-platform-lab-argocd"
}

# The access entry was created by the Argo CD EKS Capability.
import {
  to = aws_eks_access_entry.argocd
  id = "${data.terraform_remote_state.eks_cluster.outputs.cluster_name}:${data.aws_iam_role.argocd.arn}"
}

resource "aws_eks_access_entry" "argocd" {
  cluster_name      = data.terraform_remote_state.eks_cluster.outputs.cluster_name
  principal_arn     = data.aws_iam_role.argocd.arn
  kubernetes_groups = ["argocd"]
}
