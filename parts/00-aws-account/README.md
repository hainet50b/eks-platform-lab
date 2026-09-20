# 00 aws-account

An AWS account ready to build in.

## Overview

```
┌─ 00 aws-account ──────────────────────────────┐
│                                               │
│   AWS account                                 │
│   └─ root user                                │
│                                               │
└───────────────────────────────────────────────┘
```

## Resources

| Resource | Provides |
| --- | --- |
| [AWS account](#aws-account) | The container for resources and the boundary for billing and security |

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
