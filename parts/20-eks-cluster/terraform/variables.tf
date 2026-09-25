variable "public_access_cidrs" {
  description = "IPv4 CIDR blocks allowed to access the public endpoint of the EKS API server"
  type        = list(string)

  validation {
    condition     = length(var.public_access_cidrs) > 0 && !contains(var.public_access_cidrs, "0.0.0.0/0")
    error_message = "public_access_cidrs must not be empty and must not contain 0.0.0.0/0."
  }
}
