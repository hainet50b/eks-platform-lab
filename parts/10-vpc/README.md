# 10 vpc

A VPC with public, private, and data subnets in two Availability Zones.

## Overview

```
┌─ 10 vpc ───────────────────────────────────────────────────────────────────┐
│                                                                            │
│  you ──────▶ coding agent                                                  │
│   │            │                                                           │
│   │            │  ┌─ agent skills ─────────────────────────┐               │
│   │            ├─▶│  eks-design (APEX Skills)              │               │
│   │            │  │  terraform-skill (APEX Skills)         │               │
│   │            │  │  terraform-style-guide (HashiCorp)     │               │
│   │            │  └────────────────────────────────────────┘               │
│   │            │ reviews, writes, and runs                                 │
│   ▼            ▼                                                           │
│  ┌─ 1. Creating the network with Terraform ───────────────────────────┐    │
│  │                                                                    │    │
│  │   ┌─ Terraform ──────────────────────────────────────────────────┐ │    │
│  │   │  configuration   terraform/*.tf                              │ │    │
│  │   │  state           S3 bucket created in part 05                │ │    │
│  │   └──────────────────────────────────────────────────────────────┘ │    │
│  │                             │ creates                              │    │
│  │                             ▼                                      │    │
│  │   ┌─ VPC 10.0.0.0/16 ────────────────────────────────────────────┐ │    │
│  │   │                                                              │ │    │
│  │   │            ap-northeast-1a      ap-northeast-1c   routes     │ │    │
│  │   │                                                              │ │    │
│  │   │  public    10.0.0.0/24          10.0.1.0/24       → local    │ │    │
│  │   │                                                   → IGW      │ │    │
│  │   │            NAT gateway + EIP                                 │ │    │
│  │   │                                                              │ │    │
│  │   │  private   10.0.16.0/20         10.0.32.0/20      → local    │ │    │
│  │   │                                                   → NAT      │ │    │
│  │   │                                                   → S3       │ │    │
│  │   │                                                     endpoint │ │    │
│  │   │                                                              │ │    │
│  │   │  data      10.0.2.0/24          10.0.3.0/24       → local    │ │    │
│  │   │                                                              │ │    │
│  │   └──────────────┬─────────────────────────────────┬─────────────┘ │    │
│  │                  │ internet gateway                │ gateway       │    │
│  │                  ▼                                 ▼ endpoint      │    │
│  │              Internet                          Amazon S3           │    │
│  │                                                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Creating the network with Terraform](#creating-the-network-with-terraform) | Builds the VPC, its subnets, and its routes from a Terraform configuration |
