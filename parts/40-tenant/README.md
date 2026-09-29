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
