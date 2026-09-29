# 40 tenant

A namespace with guardrails, and a developer who may work only there.

## Overview

```
┌─ 40 tenant ───────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                       │
│  you ──────▶ coding agent                                                             a developer     │
│   │            │                                                                       │              │
│   │            │  ┌─ agent skills ─────────────────────────┐                           │              │
│   │            ├─▶│  /apex:eks-design (APEX Skills)        │                           │              │
│   │            │  │  terraform-skill (APEX Skills)         │                           │              │
│   │            │  │  terraform-style-guide (HashiCorp)     │                           │              │
│   │            │  │  aws-containers (Agent Toolkit)        │                           │              │
│   │            │  └────────────────────────────────────────┘                           │              │
│   │            │ reviews, writes, runs, and applies                                    │              │
│   │            │  ┌─ 1. ───────────────────────────────────┐                           │              │
│   │            ├─▶│  the tenant design                     │                           │              │
│   │            │  └────────────────────────────────────────┘                           │              │
│   │            │                                                                       │ signs in as  │
│   │            │                               ┌─ IAM Identity Center (part 00) ─────┐ │              │
│   │            │                               │                                     │ │              │
│   │            │                               │  ┌─ 6. ──────────────────────────┐  │ │              │
│   ├─ creates ──┼───────────────────────────────┼─▶│  user, in a group with a      │◀─┼─┤              │
│   │            │                               │  │  permission set and its role  │  │ │              │
│   │            │                               │  └─────┬─────────────────────────┘  │ │              │
│   │            │                               └────────┼────────────────────────────┘ │              │
│   │            │                                        │ is the principal of          │              │
│   ▼            ▼                                        │                              │              │
│  ┌─ EKS Auto Mode cluster (part 20) ────────────────────┼──────────────────────────────┼───────────┐  │
│  │                                                      ▼                              │           │  │
│  │  ┌─ 2. ───────────────────────────────┐     ┌─ 7. ────────────────────────────────┐ │           │  │
│  │  │  ConfigMap that enables            │     │  access entry                       │ │           │  │
│  │  │  the network policy controller     │     └────────┬────────────────────────────┘ │           │  │
│  │  └────────────────────────────────────┘              │ grants edit access           │           │  │
│  │                                                      │                              │ works in  │  │
│  │                                                      ▼                              │           │  │
│  │  ┌─ 3. ────────────────────────────────────────────────────────────────────────┐    │           │  │
│  │  │  namespace, with Pod Security Standards restricted                          │◀───┤           │  │
│  │  │                                                                             │    │           │  │
│  │  │  ┌─ 4. ──────────────────────────────────────────────────────────────────┐  │    │           │  │
│  │  │  │  NetworkPolicies                                                      │  │    │           │  │
│  │  │  │  rules for the traffic of the pods                                    │  │    │           │  │
│  │  │  └───────────────────────────────────────────────────────────────────────┘  │    │           │  │
│  │  │  ┌─ 5. ──────────────────────────────────────────────────────────────────┐  │    │           │  │
│  │  │  │  ResourceQuota and LimitRange                                         │  │    │           │  │
│  │  │  │  caps and defaults for the resources of the pods                      │  │    │           │  │
│  │  │  └───────────────────────────────────────────────────────────────────────┘  │    │           │  │
│  │  │  ┌─ 8. ──────────────────────────────────────────────────────────────────┐  │    │           │  │
│  │  │  │  sample workload                                                      │  │    │           │  │
│  │  │  └───────────────────────────────────────────────────────────────────────┘  │    │           │  │
│  │  │                                    ╳                                        │    │           │  │
│  │  └────────────────────────────────────┼────────────────────────────────────────┘    │           │  │
│  │                                       │ traffic                                     │           │  │
│  │                                       ╳                                             │           │  │
│  │  ┌─ other namespaces ──────────────────────────────────────────────────────────┐    │           │  │
│  │  │  other workloads                                                            │╳───┘           │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘                │  │
│  │                                                                                                 │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                       │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Reviewing the tenant design](#reviewing-the-tenant-design) | Reviews the design of the tenant: the namespace, its guardrails, the access of the developers, and the sample workload |
| [2. Enabling the network policy controller with a Kubernetes manifest](#enabling-the-network-policy-controller-with-a-kubernetes-manifest) | Creates the ConfigMap that enables the network policy controller of the cluster |
| [3. Creating the namespace with a Kubernetes manifest](#creating-the-namespace-with-a-kubernetes-manifest) | Creates the namespace, with Pod Security Standards restricted |
| [4. Creating the NetworkPolicies with a Kubernetes manifest](#creating-the-networkpolicies-with-a-kubernetes-manifest) | Creates the NetworkPolicies that restrict the traffic of the pods |
| [5. Limiting the resources of the namespace with a Kubernetes manifest](#limiting-the-resources-of-the-namespace-with-a-kubernetes-manifest) | Creates the ResourceQuota and the LimitRange that cap the resources of the namespace and fill in defaults |
| [6. Creating the developer with IAM Identity Center](#creating-the-developer-with-iam-identity-center) | Creates the user, the group, and the permission set of the developer |
| [7. Granting the developer access with Terraform](#granting-the-developer-access-with-terraform) | Creates the access entry that gives the developer access to the namespace |
| [8. Creating the sample workload as the developer with a Kubernetes manifest](#creating-the-sample-workload-as-the-developer-with-a-kubernetes-manifest) | Creates the Deployment, Service, and Ingress of the sample workload, as the developer |

## The tenant design

A tenant is a team that uses a platform shared with other teams. The
platform gives each team a place of its own, so that the teams do not
disturb one another.

On an EKS cluster, the place is a namespace. The namespace comes with
rules set on it as guardrails, and only its own team may enter.

This part builds one tenant for a team of developers. Its guardrails are
of three kinds:

- The access of the developers: what they may do, and where.
- The traffic of the pods: what they may talk to.
- The resources of the pods: how much they may use.

**The access of the developers.** The developers should touch only the
workloads of their own tenant. In this lab, that comes out as follows:

| | | Administrator | | Developers | |
| --- | --- | :---: | :---: | :---: | :---: |
| | | read | write | read | write |
| In AWS | The cluster | ✅ | ✅ | ✅\* | ❌ |
| | Other resources | ✅ | ✅ | ❌ | ❌ |
| In the cluster | Nodes, NodePools, IngressClasses | ✅ | ✅ | ❌ | ❌ |
| | The list of namespaces | ✅ | ✅ | ❌ | ❌ |
| In the namespace `team-a` | The namespace itself | ✅ | ✅ | ✅ | ❌ |
| | ResourceQuota, LimitRange | ✅ | ✅ | ✅ | ❌ |
| | NetworkPolicies | ✅ | ✅ | ✅ | ✅\*\* |
| | Workloads | ✅ | ✅ | ✅ | ✅ |
| In other namespaces | Everything | ✅ | ✅ | ❌ | ❌ |

\* Needed to connect to the EKS cluster.

\*\* Allowed to keep the implementation simple. Restrict it in production.

**The traffic of the pods.** Pods should talk only to the pods of the
same tenant, and they also have to reach the load balancer and the DNS
server. In this lab, that comes out as follows:

| Peer | Ingress | Egress |
| --- | :---: | :---: |
| The load balancer | ✅ | ❌ |
| The DNS server | ❌ | ✅ |
| Pods of the same namespace | ✅ | ✅ |
| Pods of other namespaces | ❌ | ❌ |
| Anything else | ❌ | ❌ |

**The resources of the pods.** Caps and defaults, set per tenant and
per container, keep the resources of the pods in balance with what the
NodePool launches. In this lab, they are set as follows:

| | Default per container | Cap per container | Cap for the tenant |
| --- | :---: | :---: | :---: |
| CPU request | 100m | — | 2 vCPUs |
| CPU limit\* | — | — | — |
| Memory request | 128 MiB | — | 4 GiB |
| Memory limit | 128 MiB | 2 GiB | 4 GiB |
| Pods | | | 10 |
| Ingresses | | | 2 |
| Services of type LoadBalancer or NodePort | | | 0 |

\* No CPU limit anywhere: a CPU limit throttles a container while its
node has CPU to spare.

## Reviewing the tenant design

The steps that follow write the tenant as Kubernetes manifests and one
Terraform configuration. Before you ask the agent to write them, review
the tenant design with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the tenant design, start a Claude Code session at the
repository root and paste the following review request. Fill its "Design"
section with the following sections of the prompts, in this order:

- The "Kubernetes resource settings" sections of steps 2 to 5
- The "AWS resource settings" section of step 7
- The "Kubernetes resource settings" section of step 8

````text
/apex:eks-design

# Review request
I am creating one tenant on an EKS Auto Mode cluster.
The design below consists of the following.
- A ConfigMap that enables the network policy controller
- The namespace of the tenant and its Pod Security labels
- NetworkPolicies
- A ResourceQuota and a LimitRange
- The access entry and the access policy of the developers
- The Deployment, Service, and Ingress of a sample workload in the tenant
Review the design with the context in mind.

## Context
- This is a personal lab. It is torn down every night to keep the cost down.
- The VPC, the EKS Auto Mode cluster, the NodePool, and the IngressClass already exist.
- There is one tenant, meant for a trusted internal team.
- The following concerns are out of scope here.
  - Scaling and availability
  - Pod health checks
  - Secret injection
  - A custom domain and HTTPS

## Design
```
(the sections of the prompts of steps 2 to 5, 7, and 8)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 5,
7, and 8 are the result of a few rounds.

## Enabling the network policy controller with a Kubernetes manifest

A [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
is a set of rules for the traffic of the pods that it selects. The API
server stores a NetworkPolicy but does not enforce it: the network plugin
of the cluster does. With EKS Auto Mode, the network plugin on each node
enforces the NetworkPolicies, with a
[network policy controller](https://docs.aws.amazon.com/eks/latest/userguide/auto-net-pol.html)
that runs on the control plane of the cluster. The controller stays
disabled until a ConfigMap enables it.

To enable the network policy controller:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest that enables the network policy controller on an EKS Auto Mode cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/40-tenant/manifests/network-policy-controller.yaml.

   ## Kubernetes resource settings

   ### Kubernetes resource list
   - ConfigMap: 1

   ### ConfigMap
   - Make it the ConfigMap that enables the network policy controller.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the key of the ConfigMap is that of
   the [Auto Mode documentation](https://docs.aws.amazon.com/eks/latest/userguide/auto-net-pol.html),
   and that nothing was added that the prompt did not ask for. The file
   [manifests/network-policy-controller.yaml](manifests/network-policy-controller.yaml)
   is the result of this step.

2. Apply the manifest. Make sure that
   [the cluster](../20-eks-cluster/README.md#creating-the-cluster-with-terraform)
   is up and that kubectl is set up for it again, with
   `aws eks update-kubeconfig`, then ask the agent:

   ```text
   Apply parts/40-tenant/manifests/network-policy-controller.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/40-tenant/manifests/network-policy-controller.yaml
   ```

3. Check the ConfigMap. It exists in the namespace `kube-system` and
   enables the network policy controller.

   To check this, ask the agent:

   ```text
   Check the ConfigMap amazon-vpc-cni in the namespace kube-system of the cluster:

   - It exists.
   - It enables the network policy controller.
   ```

   Or run the command yourself:

   ```bash
   kubectl get configmap amazon-vpc-cni -n kube-system -o yaml
   ```

   The command prints the ConfigMap with
   `enable-network-policy-controller` set to `"true"` in its `data`.

## Creating the namespace with a Kubernetes manifest

A [namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
divides the resources of a cluster into groups. The name of a resource
is unique within its namespace, and access and quotas can be set per
namespace. The namespace of the tenant is where its workloads run, and
the guardrails of the tenant are set on it.

[Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
define three levels of what a pod may do on its node, each stricter than
the one before:

- `privileged`: The pod may do anything.
- `baseline`: The pod may not use the known ways to escalate its
  privileges.
- `restricted`: The pod must also follow the practices of hardening a
  pod.

With [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/),
a label on the namespace applies a level in one of three modes:

- `enforce`: The API server rejects a pod that violates the level.
- `warn`: The API server warns the client.
- `audit`: The API server records the violation in the audit log.

The namespace of the tenant, `team-a`, applies `restricted` in all three
modes.

To create the namespace:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the namespace of a tenant on an EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/40-tenant/manifests/namespace.yaml.

   ## Kubernetes resource settings

   ### Kubernetes resource list
   - Namespace: 1

   ### Namespace
   - Name it team-a.
   - Apply the restricted level of Pod Security Standards in all of the following modes.
     - enforce
     - warn
     - audit

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that nothing was added that the prompt
   did not ask for. The file
   [manifests/namespace.yaml](manifests/namespace.yaml) is the result of
   this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/40-tenant/manifests/namespace.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/40-tenant/manifests/namespace.yaml
   ```

3. Check the namespace. It exists and applies `restricted` in the three
   modes, and it rejects a pod that does not meet `restricted`.

   To check this, ask the agent:

   ```text
   Check the namespace team-a of the cluster:

   - It exists.
   - It applies the restricted level of Pod Security Standards in the modes enforce, warn, and audit.
   - It rejects a pod that does not meet restricted. Try this with a server-side dry run, so that nothing is created.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get namespace team-a -o yaml

   kubectl run check -n team-a \
     --image=public.ecr.aws/docker/library/busybox:1.37 \
     --restart=Never \
     --dry-run=server \
     -- sleep 5
   ```

   The first command prints the namespace with the three labels
   `pod-security.kubernetes.io/<mode>: restricted`. The second sends a pod
   with no security settings as a server-side dry run, which is checked
   but not stored. The API server rejects the pod and lists the four
   settings that it lacks.

## Creating the NetworkPolicies with a Kubernetes manifest

The pods of the tenant talk only to the pods of the tenant, the load
balancer, and the DNS server. NetworkPolicies put this in place in two
steps:

- A NetworkPolicy with no rules blocks all the traffic of the pods.
- A separate NetworkPolicy for each peer allows the traffic with that
  peer.

The four NetworkPolicies apply to all the pods of the namespace:

| NetworkPolicy | Allows ingress | Allows egress |
| --- | --- | --- |
| Default deny | Nothing | Nothing |
| Load balancer | From the public subnets | — |
| DNS | — | To the DNS server, on port 53 |
| Same namespace | From the pods of the namespace | To the pods of the namespace |

The load balancer and the DNS server are not pods of the cluster, so
their rules name them by address. The load balancer sends requests from
its addresses in the public subnets. With EKS Auto Mode, CoreDNS runs
on each node, and the pods reach it at the tenth address of the service
CIDR of the cluster, `172.20.0.10`.

To create the NetworkPolicies:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the NetworkPolicies of the namespace of a tenant on an EKS Auto Mode cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/40-tenant/manifests/network-policies.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace team-a.
   - Apply each NetworkPolicy to all the pods of the namespace.

   ### Kubernetes resource list
   - NetworkPolicy: 4

   ### NetworkPolicy (default deny)
   - Deny all incoming and outgoing traffic.

   ### NetworkPolicy (traffic from the ALB)
   - Allow incoming traffic from the public subnets of the VPC, where the ALB is placed.
     - The public subnets are 10.0.0.0/24 and 10.0.1.0/24.
   - Do not restrict the ports.

   ### NetworkPolicy (DNS)
   - Allow traffic to UDP and TCP port 53 of CoreDNS.
     - The pods see CoreDNS at 172.20.0.10.

   ### NetworkPolicy (same namespace)
   - Allow traffic with the pods of the same namespace, in both directions.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that nothing was added that the prompt
   did not ask for. The file
   [manifests/network-policies.yaml](manifests/network-policies.yaml) is
   the result of this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/40-tenant/manifests/network-policies.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/40-tenant/manifests/network-policies.yaml
   ```

3. Check the NetworkPolicies. The namespace has the four, each applying
   to all its pods and allowing the traffic of the table, and the network
   policy controller has made a PolicyEndpoint for each of them.

   To check this, ask the agent:

   ```text
   Check the NetworkPolicies of the namespace team-a of the cluster:

   - There are four, and each applies to all the pods of the namespace.
   - One allows no traffic in either direction.
   - One allows ingress from the ALB in 10.0.0.0/24 and 10.0.1.0/24, on any port.
   - One allows egress to CoreDNS at 172.20.0.10, on UDP and TCP port 53.
   - One allows ingress and egress with the pods of the namespace.
   - There is a PolicyEndpoint for each of them.
   ```

   Or run the commands yourself:

   ```bash
   kubectl describe networkpolicies -n team-a

   kubectl get policyendpoints -n team-a
   ```

   The first command prints each NetworkPolicy with the traffic that it
   allows. The second lists a PolicyEndpoint for each NetworkPolicy,
   named after it, which the network policy controller writes for the
   nodes to enforce.

## Limiting the resources of the namespace with a Kubernetes manifest

The pods of the tenant use no more resources than the tenant is given.
Two Kubernetes resources put this in place:

- A [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
  holds the caps for the tenant, on the totals of all its pods.
- A [LimitRange](https://kubernetes.io/docs/concepts/policy/limit-range/)
  holds the defaults and the caps per container.

To limit the resources of the namespace:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the ResourceQuota and the LimitRange of the namespace of a tenant on an EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/40-tenant/manifests/quota.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace team-a.

   ### Kubernetes resource list
   - ResourceQuota: 1
   - LimitRange: 1

   ### ResourceQuota
   - Cap the namespace as follows.
     - CPU requests: 2
     - Memory requests: 4Gi
     - Memory limits: 4Gi
     - Number of pods: 10
     - Number of Ingresses: 2
   - Allow no Service of the following types.
     - LoadBalancer
     - NodePort

   ### LimitRange
   - Set the following for each container.
     - Default requests
       - CPU: 100m
       - Memory: 128Mi
     - Default limits
       - Memory: 128Mi
     - Maximum
       - Memory: 2Gi

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that nothing was added that the prompt
   did not ask for. The file [manifests/quota.yaml](manifests/quota.yaml)
   is the result of this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/40-tenant/manifests/quota.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/40-tenant/manifests/quota.yaml
   ```

3. Check the ResourceQuota and the LimitRange. Their caps and defaults are
   those of the manifest.

   To check this, ask the agent:

   ```text
   Show me the ResourceQuota and the LimitRange of the namespace team-a of the cluster:
   the caps of the ResourceQuota,
   and the defaults and the caps per container of the LimitRange.
   ```

   Or run the command yourself:

   ```bash
   kubectl describe resourcequota,limitrange -n team-a
   ```

   The command prints the caps of the ResourceQuota, with what the
   namespace uses, and the defaults and the caps of the LimitRange.

## Creating the developer with IAM Identity Center

The developers sign in through IAM Identity Center, as the administrator
does, with a permission set of their own. The permission set allows only
the two actions that kubectl needs from AWS: `eks:ListClusters` to find
the cluster, and `eks:DescribeCluster` to connect to it. What the
developers may do inside the cluster is set in the cluster.

In this lab, you play the developer too, from the same machine, with an
AWS CLI profile and a kubectl context of the developer.

To create the developer:

1. [Add a user](https://docs.aws.amazon.com/singlesignon/latest/userguide/addusers.html)
   for the developer, with an email address other than yours, and
   [a group](https://docs.aws.amazon.com/singlesignon/latest/userguide/addgroups.html)
   for the developers of the tenant, and put the user in the group. The
   table at the end of this section lists their names in this lab.
2. [Create a permission set](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtocreatepermissionset.html)
   as a custom permission set, with the following inline policy only.
   Name it after what it allows and the tenant it is for, such as
   `EKSDeveloperTeamA`.

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["eks:DescribeCluster", "eks:ListClusters"],
         "Resource": "*"
       }
     ]
   }
   ```

3. [Grant the group access to the account](https://docs.aws.amazon.com/singlesignon/latest/userguide/assignusers.html)
   with that permission set. IAM Identity Center then creates the
   matching IAM role in the account.
4. Open the invitation email, set the password of the developer, and
   [register an MFA device](https://docs.aws.amazon.com/singlesignon/latest/userguide/user-device-registration.html).
5. Configure a profile for the developer with `aws configure sso`. When
   the command opens the browser, copy the URL into a private window and
   sign in there as the developer: in your usual window, the access
   portal is signed in as you, and the command would go through as you.

   ```bash
   aws --profile <account-name>-team-a-dev \
     configure sso
   ```

   The command needs the values below.

   | Value | Answer |
   | --- | --- |
   | `<account-name>` | The name of the account you sign in to |
   | SSO session name | The name of the user of the developer, not the name of your own sso-session |
   | SSO start URL | The access portal URL |
   | SSO region | The Region of IAM Identity Center |
   | SSO registration scopes | `sso:account:access`, the default |
   | Account and role | The account, then `EKSDeveloperTeamA` |
   | Default client Region | The Region you build in |
   | CLI default output format | `json`, the default |

6. Add the cluster to the configuration of kubectl for the developer,
   and make `team-a` the default namespace of the context.

   ```bash
   aws --profile <account-name>-team-a-dev \
     eks update-kubeconfig --name eks-platform-lab --region ap-northeast-1 \
     --alias <account-name>-team-a-dev \
     --user-alias <account-name>-team-a-dev

   kubectl config set-context <account-name>-team-a-dev --namespace team-a

   kubectl config use-context <account-name>-admin
   ```

   The first command makes the new context the current one, so the
   last command makes your own context current again. From now on, the
   commands of the developer name the context with `--context`.

   > [!NOTE]
   > If you set up kubectl without `--alias`, your own context has the ARN
   > of the cluster as its name. `kubectl config get-contexts` lists the
   > contexts in `~/.kube/config`. Use that name, or rename the context with
   > `kubectl config rename-context <ARN of the cluster> <account-name>-admin`.

7. Check who the developer is signed in as.

   ```bash
   aws --profile <account-name>-team-a-dev \
     sts get-caller-identity
   ```

   The `Arn` ends with
   `assumed-role/AWSReservedSSO_EKSDeveloperTeamA_<random>/<user>-dev`.

In this lab, the steps created these objects:

| Object | Name | Denotes |
| --- | --- | --- |
| user | `<user>-dev` | The same person in the role of a developer |
| group | `eks-platform-lab-team-a` | The developers of one tenant in one specific project |
| permission set | `EKSDeveloperTeamA` | What the developers of the tenant may do in AWS |
| IAM role | `AWSReservedSSO_EKSDeveloperTeamA_<random>` | The permission set, in a name generated by IAM Identity Center |
| sso-session | `<user>-dev` | The user who signs in |
| profile and kubectl context | `<account-name>-team-a-dev` | The account and the permission set |

## Granting the developer access with Terraform

The developers may work only in the namespace of the tenant. The
cluster lets them in through an
[access entry](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html)
for the IAM role of their permission set. The access policy of the entry
decides what the role may do, and the scope of the policy decides where.
The developers get `AmazonEKSEditPolicy`, with the namespace `team-a` as
its scope.

To grant the developer access:

1. Ask the agent to write the configuration. Start a Claude Code session at
   the repository root and paste the following prompt.

   ```text
   /terraform-skill
   /terraform-style-guide

   # Summary
   Create a Terraform configuration for an access entry of the developers on an EKS cluster.

   ## Prerequisites
   - AWS credentials are passed at run time through AWS_PROFILE.
   - The EKS cluster already exists.
     - Its state is in the following S3 location.
       - Bucket: eks-platform-lab-terraform-state-<account ID>
       - Key: parts/20-eks-cluster/terraform.tfstate
     - The state has the following output.
       - cluster_name: the name of the EKS cluster

   ## Working environment
   - Create the Terraform configuration in parts/40-tenant/terraform.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 40-tenant
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - EKS access entry: 1

   ### EKS access entry
   - Create it for the IAM role of the IAM Identity Center permission set EKSDeveloperTeamA.
   - Set no user name and no Kubernetes groups.
   - Associate the access policy AmazonEKSEditPolicy with the namespace team-a only.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Use the S3 backend.
   - Use parts/40-tenant/terraform.tfstate as the state key.
   - Lock with S3 native locking.
   - Do not include the bucket name in the backend configuration;
     pass it with -backend-config on terraform init.

   ### Output
   - None.

   ### Style
   - Place each data source right before the resource that references it.
   - Name each data source label after its content.
   - Do not add unnecessary depends_on.
   - Keep the configuration, and especially the comments, to the minimum.
   ```

   The agent writes the configuration files and a `.gitignore` under
   [terraform/](terraform/), then runs `terraform init -backend=false`,
   `fmt`, and `validate`.

   Before you go on, read the result against the prompt. In particular,
   check that no profile name and no account ID appear anywhere, that the
   `backend "s3"` block has no `bucket` line, and that the IAM role is
   found by the name of the permission set, with no random part of its
   name in the configuration. The files in [terraform/](terraform/) are the
   result of this step.

2. Plan and apply. Make sure that the AWS CLI is signed in to the profile
   `<account-name>-admin`, then ask the agent:

   ```text
   /terraform-skill
   Initialize parts/40-tenant/terraform with the profile <account-name>-admin.
   Take the bucket name from the output bucket_name of parts/05-terraform-state/terraform,
   and pass it as -backend-config.
   Then show me the plan, and apply it after I approve.
   ```

   The plan adds 2 resources: the access entry and its policy
   association.

   Or run the commands yourself:

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/40-tenant/terraform \
     init -backend-config="bucket=${bucket_name}"

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/40-tenant/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/40-tenant/terraform \
     apply terraform.tfplan
   ```

3. Check the access of the developer. The cluster lets the developer in
   as the IAM role of the permission set, and the developer may list the
   pods of `team-a` but not those of `default`, nor the nodes.

   To check this, ask the agent:

   ```text
   Check the access of the developer, with the kubectl context <account-name>-team-a-dev:

   - The cluster authenticates the developer as the IAM role of the permission set EKSDeveloperTeamA.
   - The developer can list the pods of the namespace team-a.
   - The developer cannot list the pods of the namespace default, nor the nodes of the cluster.
   ```

   Or run the commands yourself:

   ```bash
   kubectl --context <account-name>-team-a-dev auth whoami

   kubectl --context <account-name>-team-a-dev get pods

   kubectl --context <account-name>-team-a-dev get pods -n default

   kubectl --context <account-name>-team-a-dev get nodes
   ```

   The first command prints the ARN of the IAM role, with the name of the
   user at its end. The second finds no pods in `team-a` yet. The third
   and the fourth are forbidden, with a message that names the developer,
   the resource, and the namespace or the cluster scope.
