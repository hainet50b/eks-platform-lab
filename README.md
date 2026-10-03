# eks-platform-lab

How to build a just-enough application platform on
[Amazon EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html)
with an AI coding agent and its skills from the
[Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/what-is-agent-toolkit.html)
and [APEX Skills](https://aws-samples.github.io/sample-apex-skills/), in
numbered, rebuildable parts.

## Overview

This repository is split into numbered parts under [`parts/`](parts/).

```
┌─ 01 aws-cli ─────────────────┐
│                              │
│   AWS CLI and agent skills   │
│                              │
└──────────────┬───────────────┘
               │ operates AWS resources
               ▼
┌─ 00 aws-account ─────────────────────────────────────────────────┐
│                                                                  │
│   AWS account                                                    │
│                                                                  │
│   ┌─ IAM Identity Center ────────────────────────────────────┐   │
│   │                                                          │   │
│   │   ┌─ 00 aws-account ──────┐  ┌─ 40 tenant ───────────┐   │   │
│   │   │                       │  │                       │   │   │
│   │   │   an administrator    │  │   a developer         │   │   │
│   │   │   who may do anything │  │   who may work        │   │   │
│   │   │   in the account      │  │   only in the tenant  │   │   │
│   │   │                       │  │                       │   │   │
│   │   └───────────────────────┘  └───────────────────────┘   │   │
│   │                                                          │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─ 05 terraform-state ─────────────────────────────────────┐   │
│   │                                                          │   │
│   │   S3 bucket for the Terraform state                      │   │
│   │                                                          │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─ 10 vpc ─────────────────────────────────────────────────┐   │
│   │                                                          │   │
│   │   VPC with public, private, and data subnets             │   │
│   │   in two Availability Zones                              │   │
│   │                                                          │   │
│   │   ┌─ 30 workload ────────────────────────────────────┐   │   │
│   │   │                                                  │   │   │
│   │   │   nodes, a load balancer, and pods               │   │   │
│   │   │                                                  │   │   │
│   │   └──────────────────────────────────────────────────┘   │   │
│   │                  ▲                                       │   │
│   └──────────────────┼───────────────────────────────────────┘   │
│                      │ places nodes, a load balancer, and pods   │
│   ┌─ 20 eks-cluster ─┴───────────────────────────────────────┐   │
│   │                                                          │   │
│   │   EKS Auto Mode cluster                                  │   │
│   │                                                          │   │
│   │   ┌─ 30 workload ────────────────────────────────────┐   │   │
│   │   │                                                  │   │   │
│   │   │   NodePool, IngressClass,                        │   │   │
│   │   │   and manifests of workloads                     │   │   │
│   │   │                                                  │   │   │
│   │   └──────────────────────────────────────────────────┘   │   │
│   │                                                          │   │
│   │   ┌─ 40 tenant ──────────────────────────────────────┐   │   │
│   │   │                                                  │   │   │
│   │   │   a namespace with guardrails,                   │   │   │
│   │   │   where the workloads of one tenant run          │   │   │
│   │   │                                                  │   │   │
│   │   └──────────────────────────────────────────────────┘   │   │
│   │                                                          │   │
│   │   ┌─ 50 argo-cd ─────────────────────────────────────┐   │   │
│   │   │                                                  │   │   │
│   │   │   Argo CD, which keeps the workloads             │   │   │
│   │   │   in sync with a Git repository                  │   │   │
│   │   │                                                  │   │   │
│   │   └──────────────────────────────────────────────────┘   │   │
│   │                                                          │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Parts

A part holds two kinds of content: configuration files and scripts, and
instructions.

| Part | Builds |
| --- | --- |
| [00 aws-account](parts/00-aws-account/README.md) | An AWS account ready to build in |
| [01 aws-cli](parts/01-aws-cli/README.md) | The AWS CLI and agent skills, signed in to the account |
| [05 terraform-state](parts/05-terraform-state/README.md) | An S3 bucket that holds the Terraform state |
| [10 vpc](parts/10-vpc/README.md) | A VPC with public, private, and data subnets in two Availability Zones |
| [20 eks-cluster](parts/20-eks-cluster/README.md) | An EKS Auto Mode cluster |
| [30 workload](parts/30-workload/README.md) | A NodePool, an IngressClass, and a sample workload |
| [40 tenant](parts/40-tenant/README.md) | A namespace with guardrails, and a developer who may work only there |
| [50 argo-cd](parts/50-argo-cd/README.md) | Argo CD, which keeps the workloads in sync with a Git repository |

## Tools

The tools that this repository uses.

| Name | Introduced in |
| --- | --- |
| [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) | [01 aws-cli](parts/01-aws-cli/README.md#aws-cli) |
| [Terraform](https://developer.hashicorp.com/terraform) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |
| [kubectl](https://kubernetes.io/docs/reference/kubectl/) | [20 eks-cluster](parts/20-eks-cluster/README.md#creating-the-cluster-with-terraform) |

## Skills

The skills that this repository uses.

| Kind | Name | Introduced in |
| --- | --- | --- |
| Agent Toolkit for AWS | [`signing-in-to-aws`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/signing-in-to-aws/SKILL.md) | [01 aws-cli](parts/01-aws-cli/README.md#agent-toolkit-for-aws-skills) |
| Agent Toolkit for AWS | [`aws-billing-and-cost-management`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/aws-billing-and-cost-management/SKILL.md) | [01 aws-cli](parts/01-aws-cli/README.md#agent-toolkit-for-aws-skills) |
| Agent Toolkit for AWS | [`securing-s3-buckets`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/specialized-skills/storage-skills/securing-s3-buckets/SKILL.md) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |
| Agent Toolkit for AWS | [`aws-containers`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/aws-containers/SKILL.md) | [30 workload](parts/30-workload/README.md#creating-the-nodepool-with-a-kubernetes-manifest) |
| APEX Skills | [`terraform-skill`](https://aws-samples.github.io/sample-apex-skills/docs/skills/general/terraform-skill/) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |
| APEX Skills | [`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design) | [10 vpc](parts/10-vpc/README.md#creating-the-network-with-terraform) |
| HashiCorp | [`terraform-style-guide`](https://github.com/hashicorp/agent-skills/blob/main/plugins/terraform/skills/terraform-style-guide/SKILL.md) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |

## License

Licensed under either of

 * Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or <http://www.apache.org/licenses/LICENSE-2.0>)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.
