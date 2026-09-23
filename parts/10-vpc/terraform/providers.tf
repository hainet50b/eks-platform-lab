provider "aws" {
  region = "ap-northeast-1"

  default_tags {
    tags = {
      Project = "eks-platform-lab"
      Part    = "10-vpc"
    }
  }
}
