# 01 aws-cli

The AWS CLI and agent skills, signed in to the account.

## Overview

```
┌─ 01 aws-cli ───────────────────────────────────────────────────┐
│                                                                │
│   you ──────▶ coding agent                                     │
│    │            │                                              │
│    │            │  ┌─ 2. Agent Toolkit for AWS skills ─────┐   │
│    │            ├─▶│  signing-in-to-aws, aws-iam,          │   │
│    │            │  │  aws-billing-and-cost-management      │   │
│    │            │  └───────────────────────────────────────┘   │
│    │            │ runs                                         │
│    ▼            ▼                                              │
│   ┌─ 1. AWS CLI ──────────────────────────────────────────┐    │
│   │  sso-session (the access portal subdomain)            │    │
│   │  profile (<account-name>-admin)                       │    │
│   └───────────────────────────┬───────────────────────────┘    │
│                               │ operates                       │
└───────────────────────────────┼────────────────────────────────┘
                                ▼
                      AWS resources (part 00)
```

## Tools

| Tool | Provides |
| --- | --- |
| [1. AWS CLI](#aws-cli) | Commands to operate AWS resources from the shell |
| [2. Agent Toolkit for AWS skills](#agent-toolkit-for-aws-skills) | AWS know-how for the coding agent |

## AWS CLI

The [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
operates AWS resources from the shell with one `aws` command. Commands run under a
**profile**: a named set of settings that says which account, which role, and
which Region. With IAM Identity Center, a profile points at an **sso-session**, the
connection to one IAM Identity Center instance, and names an account and a
permission set in it.

To install the AWS CLI and sign in:

1. [Install AWS CLI version 2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
   in the way that suits your operating system.
2. [Configure a profile with `aws configure sso`](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html).
   It needs the values below and opens the browser for you to sign in at the
   access portal.

   ```bash
   aws configure sso --profile <account-name>-admin
   ```

   | Value | Answer | Set in (part 00) |
   | --- | --- | --- |
   | `<account-name>` | The name of the account you sign in to | [AWS account](../00-aws-account/README.md#aws-account), step 1 |
   | SSO session name | The access portal subdomain, that is, the organization | [IAM Identity Center](../00-aws-account/README.md#iam-identity-center), step 2 |
   | SSO start URL | The access portal URL | [IAM Identity Center](../00-aws-account/README.md#iam-identity-center), step 2 |
   | SSO region | The Region of IAM Identity Center | [IAM Identity Center](../00-aws-account/README.md#iam-identity-center), step 1 |
   | SSO registration scopes | `sso:account:access`, the default | |
   | Account and role | The account, then `AdministratorAccess` | [IAM Identity Center](../00-aws-account/README.md#iam-identity-center), step 4 |
   | Default client Region | The Region you build in | |
   | CLI default output format | `json`, the default | |

   It then writes the profile and its sso-session to `~/.aws/config`:

   ```ini
   [profile <account-name>-admin]
   sso_session = <subdomain>
   sso_account_id = <12 digits>
   sso_role_name = AdministratorAccess
   region = <region>

   [sso-session <subdomain>]
   sso_start_url = https://<subdomain>.awsapps.com/start
   sso_region = <identity-center-region>
   sso_registration_scopes = sso:account:access
   ```

3. Check who you are signed in as with `aws sts get-caller-identity`. `sts` is AWS
   Security Token Service, which issues the temporary credentials you are now
   using.

   ```bash
   aws sts get-caller-identity --profile <account-name>-admin
   ```

   ```json
   {
       "UserId": "AROA<random>:<user>",
       "Account": "<12 digits>",
       "Arn": "arn:aws:sts::<12 digits>:assumed-role/AWSReservedSSO_AdministratorAccess_<random>/<user>"
   }
   ```

   The `Arn` says that you act as the IAM role that IAM Identity Center created
   for AdministratorAccess. `<user>` after the last slash is the IAM Identity
   Center user you signed in as in step 2.

> [!NOTE]
> A profile is one account and one permission set, so it is named after both,
> `admin` standing for AdministratorAccess. A second permission set gets a second
> profile beside the first:
>
> | Profile | Account | Permission set |
> | --- | --- | --- |
> | `<account-name>-admin` | the account | AdministratorAccess |
> | `<account-name>-readonly` | the account | ReadOnlyAccess |

> [!NOTE]
> When the sign-in expires, `aws sso login` opens the browser for you to sign in
> again.

## Agent Toolkit for AWS skills

The [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/what-is-agent-toolkit.html)
provides [Agent Skills](https://agentskills.io/specification) for AI coding
agents: curated packages of instructions, scripts, and reference material for
specific AWS tasks. This part installs the skills that account work needs. Later
parts add more.

To install them:

1. Install the skills with the AWS CLI. They are installed at user scope, so
   every project on the machine sees them. The Agent Toolkit lives in the
   `us-east-1` Region only, so pass that Region whatever your default is.

   ```bash
   aws agent-toolkit add-skill --skill-name signing-in-to-aws --region us-east-1
   aws agent-toolkit add-skill --skill-name aws-iam --region us-east-1
   aws agent-toolkit add-skill --skill-name aws-billing-and-cost-management --region us-east-1
   ```

> [!NOTE]
> Without `--agent`, the AWS CLI installs into every coding agent it detects on
> your machine. `--agent universal` installs into `~/.agents/skills`, the shared
> directory of the Agent Skills specification. Claude Code reads its own
> `~/.claude/skills` instead, so it needs a separate run with
> `--agent claude-code`. `aws agent-toolkit add-skill help` lists the accepted
> names.
>
> ```bash
> aws agent-toolkit add-skill --skill-name aws-iam --agent universal --region us-east-1
> aws agent-toolkit add-skill --skill-name aws-iam --agent claude-code --region us-east-1
> ```

In this lab, the step installed these skills:

| Skill | Use it for |
| --- | --- |
| `signing-in-to-aws` | Getting and refreshing CLI credentials |
| `aws-iam` | IAM policies and roles |
| `aws-billing-and-cost-management` | Costs, budgets, and Free Tier usage |
