data "aws_caller_identity" "current" {}

data "terraform_remote_state" "eks_cluster" {
  backend = "s3"

  config = {
    bucket = "eks-platform-lab-terraform-state-${data.aws_caller_identity.current.account_id}"
    key    = "parts/20-eks-cluster/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

# IAM Identity Center creates this role for the EKSDeveloperTeamA permission set.
data "aws_iam_roles" "eks_developer_team_a" {
  name_regex  = "^AWSReservedSSO_EKSDeveloperTeamA_[0-9a-f]+$"
  path_prefix = "/aws-reserved/sso.amazonaws.com/"
}

resource "aws_eks_access_entry" "eks_developer_team_a" {
  cluster_name      = data.terraform_remote_state.eks_cluster.outputs.cluster_name
  principal_arn     = one(data.aws_iam_roles.eks_developer_team_a.arns)
  kubernetes_groups = ["team-a-dev"]
}
