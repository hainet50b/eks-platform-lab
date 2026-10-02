data "aws_iam_policy_document" "eks_capabilities_assume_role" {
  statement {
    actions = ["sts:AssumeRole", "sts:TagSession"]

    principals {
      type        = "Service"
      identifiers = ["capabilities.eks.amazonaws.com"]
    }
  }
}

# No permissions policy: Argo CD reads public repositories only.
resource "aws_iam_role" "argocd" {
  name               = "eks-platform-lab-argocd"
  assume_role_policy = data.aws_iam_policy_document.eks_capabilities_assume_role.json
}

# EKS rejects the trust policy of a role that IAM has not propagated yet.
resource "time_sleep" "argocd_role_propagation" {
  create_duration = "60s"

  triggers = {
    role_arn = aws_iam_role.argocd.arn
  }
}

data "aws_caller_identity" "current" {}

data "terraform_remote_state" "eks_cluster" {
  backend = "s3"

  config = {
    bucket = "eks-platform-lab-terraform-state-${data.aws_caller_identity.current.account_id}"
    key    = "parts/20-eks-cluster/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

data "aws_ssoadmin_instances" "identity_center" {}

data "aws_identitystore_group" "admins" {
  identity_store_id = one(data.aws_ssoadmin_instances.identity_center.identity_store_ids)

  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = "eks-platform-lab-admins"
    }
  }
}

resource "aws_eks_capability" "argocd" {
  cluster_name              = data.terraform_remote_state.eks_cluster.outputs.cluster_name
  capability_name           = "argocd"
  type                      = "ARGOCD"
  role_arn                  = time_sleep.argocd_role_propagation.triggers["role_arn"]
  delete_propagation_policy = "RETAIN"

  configuration {
    argo_cd {
      namespace = "argocd"

      aws_idc {
        idc_instance_arn = one(data.aws_ssoadmin_instances.identity_center.arns)
      }

      rbac_role_mapping {
        role = "ADMIN"

        identity {
          id   = data.aws_identitystore_group.admins.group_id
          type = "SSO_GROUP"
        }
      }
    }
  }
}

# The capability creates the access entry for its role.
resource "aws_eks_access_policy_association" "argocd" {
  cluster_name  = aws_eks_capability.argocd.cluster_name
  principal_arn = aws_eks_capability.argocd.role_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }
}
