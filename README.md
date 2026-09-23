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
               │
               ▼
┌─ 00 aws-account ────────────────────────────────────────────┐
│                                                             │
│   AWS account                                               │
│                                                             │
│   ┌─ 05 terraform-state ────────────────────────────────┐   │
│   │                                                     │   │
│   │   S3 bucket for the Terraform state                 │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─ 10 vpc ────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   VPC with public, private, and data subnets        │   │
│   │   in two Availability Zones                         │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
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

## Tools

The tools that this repository uses.

| Name | Installed in |
| --- | --- |
| [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) | [01 aws-cli](parts/01-aws-cli/README.md#aws-cli) |
| [Terraform](https://developer.hashicorp.com/terraform) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |

## Skills

The skills that this repository uses.

| Kind | Name | Installed in |
| --- | --- | --- |
| Agent Toolkit for AWS | [`signing-in-to-aws`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/signing-in-to-aws/SKILL.md) | [01 aws-cli](parts/01-aws-cli/README.md#agent-toolkit-for-aws-skills) |
| Agent Toolkit for AWS | [`aws-billing-and-cost-management`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/aws-billing-and-cost-management/SKILL.md) | [01 aws-cli](parts/01-aws-cli/README.md#agent-toolkit-for-aws-skills) |
| Agent Toolkit for AWS | [`securing-s3-buckets`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/specialized-skills/storage-skills/securing-s3-buckets/SKILL.md) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |
| APEX Skills | [`terraform-skill`](https://aws-samples.github.io/sample-apex-skills/docs/skills/general/terraform-skill/) | [05 terraform-state](parts/05-terraform-state/README.md#creating-the-bucket-with-terraform) |
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
