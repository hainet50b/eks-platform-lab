# 05 terraform-state

An S3 bucket that holds the Terraform state.

## Overview

```
┌─ 05 terraform-state ───────────────────────────────────────────┐
│                                                                │
│  you ──────▶ coding agent                                      │
│   │            │                                               │
│   │            │  ┌─ agent skills ─────────────────────────┐   │
│   │            ├─▶│  terraform-skill (APEX Skills)         │   │
│   │            │  │  terraform-style-guide (HashiCorp)     │   │
│   │            │  │  securing-s3-buckets (Agent Toolkit)   │   │
│   │            │  └────────────────────────────────────────┘   │
│   │            │ writes and runs                               │
│   ▼            ▼                                               │
│  ┌─ 1. Creating the bucket with Terraform ──────────────────┐  │
│  │                                                          │  │
│  │   ┌─ Terraform ────────────────────────────────────────┐ │  │
│  │   │  configuration   terraform/*.tf                    │ │  │
│  │   │  state           terraform.tfstate (local)         │ │  │
│  │   └────────────────────────────────────────────────────┘ │  │
│  │                             │ creates                    │  │
│  │                             ▼                            │  │
│  │   ┌─ S3 bucket ────────────────────────────────────────┐ │  │
│  │   │                                                    │ │  │
│  │   │   ┌─ 2. Moving the state into the bucket ────────┐ │ │  │
│  │   │   │  parts/05-terraform-state/terraform.tfstate  │ │ │  │
│  │   │   │  parts/<later part>/terraform.tfstate        │ │ │  │
│  │   │   └──────────────────────────────────────────────┘ │ │  │
│  │   │                                                    │ │  │
│  │   └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Creating the bucket with Terraform](#creating-the-bucket-with-terraform) | Builds the bucket from a Terraform configuration, with a local state |
| [2. Moving the state into the bucket](#moving-the-state-into-the-bucket) | Puts that state into the bucket it describes |

## Creating the bucket with Terraform

[Terraform](https://developer.hashicorp.com/terraform) builds AWS resources
from **configuration** files written in HashiCorp Configuration Language (HCL)
and records what it built in a **state** file. Where the state file lives is
set by a **backend**. From this part on, every AWS resource is built with
Terraform, and this part creates the
[Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
bucket in which the
[S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3)
of every part holds its state.

To create the bucket:

1. [Install Terraform](https://developer.hashicorp.com/terraform/install) 1.10
   or later. Version 1.10 introduced S3 native locking, which the backend of
   this repository relies on.

2. Install the two skills that the agent uses to write the configuration, at
   user scope.

   The [`terraform-skill`](https://aws-samples.github.io/sample-apex-skills/docs/skills/general/terraform-skill/)
   skill, a workflow for writing and running Terraform, comes with
   [APEX Skills](https://aws-samples.github.io/sample-apex-skills/), a
   collection of agent skills for platform engineering on AWS. Its installer
   clones the collection to `~/.apex-skills` and links the skills from there
   into `~/.claude/skills`. It does not yet link the `steering` directory that
   the `/apex:*` commands read their workflows from
   ([issue #121](https://github.com/aws-samples/sample-apex-skills/issues/121)),
   so link it yourself.

   ```bash
   npx apex-skills --claude-only
   ln -sfn ~/.apex-skills/steering ~/.claude/apex-steering
   ```

   The [`terraform-style-guide`](https://github.com/hashicorp/agent-skills/blob/main/plugins/terraform/skills/terraform-style-guide/SKILL.md)
   skill is HashiCorp's own style conventions. Install it with the
   [GitHub CLI](https://cli.github.com/) or in any way you like.

   ```bash
   gh skill install hashicorp/agent-skills terraform-style-guide --agent claude-code --scope user
   ```

3. Ask the agent to write the configuration. Writing the prompt is the
   development work of this repository: where you once wrote the configuration
   yourself, you now describe the bucket and the configuration that you want,
   and the agent writes the configuration. The prompt is also the
   specification of the bucket, so to see what the bucket looks like, read the
   prompt.

   Start a Claude Code session at the repository root and paste the prompt.
   Its first two lines invoke the skills.

   ```text
   /terraform-skill
   /terraform-style-guide

   # Summary
   Create a Terraform configuration for an S3 bucket that holds Terraform state.

   ## Prerequisites
   - AWS credentials are passed at run time through AWS_PROFILE.
   - The state is managed locally at first and migrated to S3 later.

   ## Working environment
   - Create the Terraform configuration in parts/05-terraform-state/terraform.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 05-terraform-state
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - S3 bucket: 1

   ### S3 bucket
   - Name the bucket eks-platform-lab-terraform-state-<account ID>
     with the account ID of the credentials that run Terraform.
   - Enable versioning.
   - Keep noncurrent versions for 90 days.
   - Encrypt with SSE-S3. Do not use Bucket Keys.
   - Block public access.
   - Deny requests that do not use HTTPS with a bucket policy.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Write the S3 backend configuration commented out.
   - Use parts/05-terraform-state/terraform.tfstate as the state key.
   - Lock with S3 native locking.
   - Do not include the bucket name in the backend configuration;
     pass it with -backend-config on terraform init.
   - Protect the bucket from accidental deletion.

   ### Output
   - Output the bucket name as bucket_name.

   ### Style
   - Place each data source right before the resource that references it.
   - Name each data source label after its content.
   - Do not add unnecessary depends_on.
   - Keep the configuration, and especially the comments, to the minimum.
   ```

   The agent writes the configuration files and a `.gitignore` under
   [terraform/](terraform/), then runs `terraform init`, which downloads the
   AWS provider into `.terraform/`, then `fmt` and `validate`.

   Before you go on, read the result against the prompt. In particular, check
   that no profile name and no account ID appear anywhere, including comments;
   that the bucket is protected with `prevent_destroy`; and that the
   `backend "s3"` block is commented out and has no `bucket` line. Ask the
   agent to fix what differs. The files in [terraform/](terraform/) are the
   result of this step.

4. Plan and apply. Make sure that the AWS CLI is signed in to the profile
   `<account-name>-admin`, then ask the agent:

   ```text
   /terraform-skill
   Plan parts/05-terraform-state/terraform with the profile <account-name>-admin,
   show me the plan, and apply it after I approve.
   ```

   The agent runs `plan`, which compares the configuration with the resources
   in your AWS account. The plan adds six resources: the bucket and its five
   settings. After you approve, the agent runs `apply`, and Terraform creates
   the bucket and writes the state to `terraform.tfstate` next to the
   configuration.

   Or run the commands yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     apply terraform.tfplan
   ```

   > [!NOTE]
   > Every Terraform command in this repository has this three-line form: the
   > profile, the command with the part's directory, and the subcommand with
   > its arguments. `AWS_PROFILE` in front of the command passes the AWS
   > profile to that one command, so no profile name is written into the
   > configuration. `-chdir` lets you run every part from the repository root.

5. Check the bucket from outside Terraform. Take the bucket name from the
   output `bucket_name`, either by asking the agent or by printing it yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name
   ```

   Then ask the agent:

   ```text
   Check the bucket <bucket-name> with the profile <account-name>-admin:

   - Versioning is enabled.
   - Noncurrent versions expire after 90 days.
   - Default encryption is SSE-S3 without Bucket Keys.
   - All four public access block settings are on.
   - The bucket policy denies requests that do not use HTTPS.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     s3api get-bucket-versioning --bucket <bucket-name>

   aws --profile <account-name>-admin \
     s3api get-bucket-lifecycle-configuration --bucket <bucket-name>

   aws --profile <account-name>-admin \
     s3api get-bucket-encryption --bucket <bucket-name>

   aws --profile <account-name>-admin \
     s3api get-public-access-block --bucket <bucket-name>

   aws --profile <account-name>-admin \
     s3api get-bucket-policy --bucket <bucket-name> --query Policy --output text
   ```

> [!NOTE]
> The Agent Toolkit for AWS has a skill that audits a bucket, the
> [`securing-s3-buckets`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/specialized-skills/storage-skills/securing-s3-buckets/SKILL.md)
> skill. Install it with the AWS CLI:
>
> ```bash
> aws agent-toolkit add-skill --skill-name securing-s3-buckets --region us-east-1
> ```
>
> Then ask the agent:
>
> ```text
> /securing-s3-buckets
> Audit the bucket <bucket-name> with the profile <account-name>-admin
> and report anything that does not follow the AWS security best practices for S3.
> ```
>
> The agent checks the bucket read-only and also recommends features for
> production buckets, such as access logging, Object Lock, and replication.
> This bucket holds a few small files for one person, so those are not
> adopted. The 90-day rule for noncurrent versions came from this audit.

## Moving the state into the bucket

The state is now local, so losing your machine loses the state. Terraform
lets you
[change the backend](https://developer.hashicorp.com/terraform/language/backend)
of an existing configuration and copies the state over, so this part moves its
own state into the bucket it has just created.

To move the state:

1. Take the bucket name from the output first.

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )
   ```

2. Remove the comment markers from the `backend "s3"` block in `terraform.tf`
   and initialize again, with two options. `-migrate-state` copies the local
   state to the new backend, and `-backend-config` supplies the bucket name.
   Terraform asks whether to copy the state; answer `yes`. This step is done
   by hand because of that question.

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     init -migrate-state -backend-config="bucket=${bucket_name}"
   ```

3. Confirm that nothing changed and that the state now comes from the bucket.
   Ask the agent:

   ```text
   /terraform-skill
   Plan parts/05-terraform-state/terraform with the profile <account-name>-admin,
   confirm that it reports No changes,
   and confirm that the state is read from the S3 backend.
   ```

   Or run `plan` yourself and read `.terraform/terraform.tfstate`, the file in
   which Terraform records the backend in use:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     plan

   grep -E '"(type|bucket|key)"' parts/05-terraform-state/terraform/.terraform/terraform.tfstate
   ```

   Then delete the local `terraform.tfstate` and `terraform.tfstate.backup`,
   which are no longer needed.

4. Read the state in the bucket. Ask the agent:

   ```text
   List the objects under parts/05-terraform-state/
   in the bucket <bucket-name> with the profile <account-name>-admin,
   and print the state file.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     s3 ls s3://<bucket-name>/parts/05-terraform-state/

   aws --profile <account-name>-admin \
     s3 cp s3://<bucket-name>/parts/05-terraform-state/terraform.tfstate - | head -40
   ```

   The state is a JSON document. Three of its top-level fields are worth
   reading: `serial`, a counter that increases with every `apply`; `lineage`,
   a unique ID given to the state when it was first created; and `resources`,
   the list of the bucket and its settings with their real ARNs.

   The state can also be read with Terraform: `state list` prints the address
   of every resource, and `state show` prints one resource.

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     state list

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     state show aws_s3_bucket.terraform_state
   ```

## Teardown

If you tear this part down, do it last, after every other part has been torn
down, because the bucket holds their state. Terraform writes the state back to
its backend after every apply, and it would have nowhere to write after tearing
down the backend itself. That is why you move the state back to the local
backend first.

To tear down the bucket:

1. Move the state back to the local backend. Comment out the `backend "s3"`
   block in `terraform.tf` and initialize again with `-migrate-state`.

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     init -migrate-state
   ```

2. Remove the protection and destroy. The bucket resource needs two changes:
   `force_destroy = true`, which lets Terraform empty the versioned bucket
   before deleting it, and its `lifecycle` block commented out. The changed
   configuration must be applied before the destroy, because the destroy
   reads the settings from the state.

   ```hcl
   resource "aws_s3_bucket" "terraform_state" {
     bucket        = "eks-platform-lab-terraform-state-${data.aws_caller_identity.current.account_id}"
     force_destroy = true

     # lifecycle {
     #   prevent_destroy = true
     # }
   }
   ```

   Ask the agent:

   ```text
   /terraform-skill
   I want to destroy parts/05-terraform-state/terraform with the profile <account-name>-admin.
   Set force_destroy = true on the bucket, comment out its lifecycle block, and apply.
   Then plan the destroy, show me the plan, and destroy after I approve.
   ```

   Or make the changes yourself and run the commands:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     apply terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     plan -destroy -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     apply terraform.tfplan
   ```

## Cost

This part is charged for the following resources.

| Resource | Name | Per month |
| --- | --- | --- |
| S3 bucket | `eks-platform-lab-terraform-state-<account ID>` | Less than 0.02 USD |
