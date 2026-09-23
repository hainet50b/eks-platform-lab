# 01 aws-cli

The AWS CLI and agent skills, signed in to the account.

## Overview

```
┌─ 01 aws-cli ───────────────────────────────────────────────────┐
│                                                                │
│   you ──────▶ coding agent                                     │
│    │            │                                              │
│    │            │  ┌─ 2. Agent Toolkit for AWS skills ─────┐   │
│    │            ├─▶│  signing-in-to-aws,                   │   │
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
   aws --profile <account-name>-admin \
     configure sso
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
   aws --profile <account-name>-admin \
     sts get-caller-identity
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
> aws agent-toolkit add-skill --skill-name signing-in-to-aws --agent universal --region us-east-1
> aws agent-toolkit add-skill --skill-name signing-in-to-aws --agent claude-code --region us-east-1
> ```

The step installs these skills:

| Skill | Use it for |
| --- | --- |
| [`signing-in-to-aws`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/signing-in-to-aws/SKILL.md) | Getting and refreshing CLI credentials |
| [`aws-billing-and-cost-management`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/aws-billing-and-cost-management/SKILL.md) | Costs, budgets, and Free Tier usage |

## Trying the tools

With the AWS CLI signed in and the skills installed, both you and the coding
agent can operate AWS resources. This section shows what that feels like with
two examples: signing in to the account, and checking the credits and the budget.

> [!NOTE]
> Every prompt and every command in this section names the profile. On a
> machine that manages several accounts, a default profile or an `AWS_PROFILE`
> variable would let a command run against an account you did not intend.

### Signing in to the account

To sign in, ask the agent:

> Sign in to AWS with the profile `<account-name>-admin`.

The agent reads the `signing-in-to-aws` skill. The skill first
recommends `aws login`, then reads `~/.aws/config`, finds that the profile
signs in through IAM Identity Center, and runs
`aws sso login --profile <account-name>-admin` instead. The browser opens for
you to approve the sign-in. The agent then checks the result with
`aws sts get-caller-identity --profile <account-name>-admin` and reports the
account, the role, and the Region.

> [!NOTE]
> The skill ends by suggesting `AWS_PROFILE`. This lab does not set it. Pass
> `--profile` on every command instead.

### Checking the credits and the budget

To check the credits and the budget, ask the agent:

> Show the remaining credits and the budgets with the profile `<account-name>-admin`.

The agent reads the `aws-billing-and-cost-management` skill. It checks the
sign-in with `aws sts get-caller-identity`, looks at the month's costs in
[Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/pricing/),
then calls `aws billing get-credits` for the credits and commands such as
`aws budgets describe-budgets` for the budget. Of these, only Cost Explorer
bills each API request.

The skill forbids arithmetic in the agent's own reasoning, so the agent sums
the credits with a short script. It reports the credit (the Free Tier promotion,
its initial and remaining amounts, and the estimated amount after pending
usage) and the budget (its limit, the actual spend so far, its alerts, and
their recipient).

The same from the CLI:

```bash
aws --profile <account-name>-admin \
  billing get-credits --account-id <12 digits> --start-date <YYYY-MM-DD> --region us-east-1

aws --profile <account-name>-admin \
  budgets describe-budgets --account-id <12 digits> --region us-east-1
```

`--start-date` is the earliest grant date to include. The day the account was
created is a safe choice.
