# 20 eks-cluster

An EKS Auto Mode cluster.

## Overview

```
┌─ 20 eks-cluster ─────────────────────────────────────────────────────────────┐
│                                                                              │
│  you ──────▶ coding agent                                                    │
│   │            │                                                             │
│   │            │  ┌─ agent skills ─────────────────────────┐                 │
│   │            ├─▶│  /apex:eks-design (APEX Skills)        │                 │
│   │            │  │  terraform-skill (APEX Skills)         │                 │
│   │            │  │  terraform-style-guide (HashiCorp)     │                 │
│   │            │  └────────────────────────────────────────┘                 │
│   │            │ reviews, writes, and runs                                   │
│   ▼            ▼                                                             │
│  ┌─ 1. Creating the cluster with Terraform ────────────────────────────┐     │
│  │                                                                     │     │
│  │  ┌─ Terraform ──────────────────────────────────────────────────┐   │     │
│  │  │  configuration   terraform/*.tf                              │   │     │
│  │  │  state           S3 bucket created in part 05                │   │     │
│  │  └──────────────────────────────────────────────────────────────┘   │     │
│  │                                 │ creates                           │     │
│  │                                 ▼                                   │     │
│  │  ┌─ EKS Auto Mode cluster ──────────────────────────────────────┐   │     │
│  │  │                                                              │   │     │
│  │  │  control plane (run by AWS)                                  │   │     │
│  │  │                                                              │   │     │
│  │  └──────────────────────────────────────────────────────────────┘   │     │
│  │                                 │ places                            │     │
│  └─────────────────────────────────┼───────────────────────────────────┘     │
│  ┌─ VPC (part 10) ─────────────────┼───────────────────────────────────┐     │
│  │  ┌─ private subnets ────────────┼────────────────────────────────┐  │     │
│  │  │                              ▼                                │  │     │
│  │  │                ┌─ 1. ──────────────────────┐                  │  │     │
│  │  │                │  control plane ENIs       │                  │  │     │
│  │  │                └───────────────────────────┘                  │  │     │
│  │  └───────────────────────────────────────────────────────────────┘  │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Creating the cluster with Terraform](#creating-the-cluster-with-terraform) | Builds the cluster, with its IAM roles, access entry, and log group, from a Terraform configuration |
