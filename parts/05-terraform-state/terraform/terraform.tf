terraform {
  required_version = "~> 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Pass the bucket name at init time:
  #   terraform init -backend-config="bucket=<bucket name>"
  # backend "s3" {
  #   key          = "parts/05-terraform-state/terraform.tfstate"
  #   region       = "ap-northeast-1"
  #   encrypt      = true
  #   use_lockfile = true
  # }
}
