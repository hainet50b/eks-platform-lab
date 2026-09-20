# 00 aws-account

An AWS account ready to build in.

## Overview

```
┌─ 00 aws-account ───────────────────────────────────┐
│                                                    │
│   AWS Organizations                                │
│   ├─ AWS account (management account)              │
│   │  ├─ root user                                  │
│   │  └─ IAM role (from the permission set)         │
│   └─ IAM Identity Center (organization instance)   │
│      ├─ user (you)                                 │
│      ├─ group (this platform's administrators)     │
│      └─ permission set (AdministratorAccess)       │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Resources

| Resource | Provides |
| --- | --- |
| [AWS account](#aws-account) | The container for resources and the boundary for billing and security |
| [AWS Organizations](#aws-organizations) | Central management of accounts: one bill, policies, and services enabled organization-wide |
| [IAM Identity Center](#iam-identity-center) | Sign-in for users, and their permissions per AWS account |

## AWS account

An [AWS account](https://docs.aws.amazon.com/accounts/latest/reference/accounts-welcome.html)
is the container for everything you create on AWS: every resource belongs to
exactly one account, no other account can access the resource, and every bill is
issued per account. The account comes with a **root user**, the identity that has
complete access to every service and resource in the account.

To create the account and protect its root user:

1. Sign up at <https://aws.amazon.com/free/> and choose the **paid plan**. The
   free plan offers only a subset of services, and AWS Organizations, which this
   part enables later, requires the paid plan.
2. [Enable MFA on the root user](https://docs.aws.amazon.com/IAM/latest/UserGuide/enable-virt-mfa-for-root.html).
   The root user can do anything in the account, so its sign-in deserves a second
   factor.

> [!NOTE]
> The root user is needed only until a person can sign in through IAM Identity
> Center: it enables AWS Organizations and Identity Center, and activates billing
> access for Identity Center users. Otherwise, the root user is used only to manage
> the account itself. AWS lists the
> [tasks that require the root user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html#root-user-tasks).

## AWS Organizations

[AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
groups accounts into an **organization** managed from one **management account**:
one consolidated bill, policies that cap what each account may do, and AWS
services enabled across all accounts at once.

To create the organization:

1. As the root user, [create an organization](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_create.html).
   IAM Identity Center, enabled in the next section, requires an organization even
   for a single account. The account you created becomes the management account.

## IAM Identity Center

[IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
(IdC) manages who signs in to AWS accounts and what they may do there. It keeps
its own **users** and **groups**, separate from IAM users, and grants them access
to accounts through **permission sets**. Users sign in at the **access portal**, a
page with its own URL rather than the console's sign-in page, and choose an account
and a permission set.

To set up sign-in for yourself:

1. As the root user, [enable IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/enable-identity-center.html)
   as a single-Region organization instance in the Region you will build in. An
   instance cannot be moved to another Region.
2. [Customize the access portal URL](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtochangeURL.html)
   with a subdomain that names the organization, not a user, a group, or a project
   such as this platform.
3. [Add a user](https://docs.aws.amazon.com/singlesignon/latest/userguide/addusers.html)
   for yourself and [a group](https://docs.aws.amazon.com/singlesignon/latest/userguide/addgroups.html)
   for this platform's administrators, and put yourself in the group.
4. [Create a permission set](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtocreatepermissionset.html)
   from the predefined **AdministratorAccess** policy, then
   [grant the group access to the account](https://docs.aws.amazon.com/singlesignon/latest/userguide/assignusers.html)
   with that permission set. IAM Identity Center creates the matching IAM role in
   the account.
5. Set your password from the invitation email and
   [register an MFA device](https://docs.aws.amazon.com/singlesignon/latest/userguide/user-device-registration.html),
   then sign in at the access portal URL from step 2 and open the account with
   AdministratorAccess. This is how you work in the account from now on.

In this lab, the steps created these objects:

| Object | Name | Denotes | Where |
| --- | --- | --- | --- |
| access portal URL | `***.awsapps.com/start` (redacted) | Typically a company or organization name | IAM Identity Center → Dashboard → Settings summary |
| user | `hainet50b` | The person, so it is your own handle | IAM Identity Center → Users |
| group | `eks-platform-lab-admins` | A role in one specific project | IAM Identity Center → Groups |
| permission set | `AdministratorAccess` | The AWS managed policy | IAM Identity Center → Multi-account permissions → Permission sets |
| IAM role | `AWSReservedSSO_AdministratorAccess_<random>` | The permission set, in a name generated by IAM Identity Center | IAM → Roles, filtered by `AWSReservedSSO_` |

> [!NOTE]
> An assignment ties a group (or a user), an AWS account, and a permission set
> together, and IAM Identity Center creates an IAM role in that account for it. A
> group can hold more than one permission set in an account, and different
> permission sets in different accounts. Each assignment appears at the access
> portal as a role to choose. For one group, for example:
>
> | Group | AWS account | Permission set |
> | --- | --- | --- |
> | group A | development account | AdministratorAccess |
> | group A | development account | ReadOnlyAccess |
> | group A | production account | ReadOnlyAccess |
>
> You cannot sign in to the IAM role directly. When you sign in through the access
> portal and choose the account and AdministratorAccess, IAM Identity Center puts
> you into this role: the console session and the CLI credentials you receive
> belong to the role, and AWS records your actions under it. The console shows the
> role you are in at the top right, as `AdministratorAccess/<user>`.
