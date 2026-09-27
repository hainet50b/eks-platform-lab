# 30 workload

A NodePool, an IngressClass, and a sample workload.

## Overview

```
┌─ 30 workload ───────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                 │
│  you ──────▶ coding agent                                                                       │
│   │            │                                                                                │
│   │            │  ┌─ agent skills ─────────────────────────┐                                    │
│   │            ├─▶│  /apex:eks-design (APEX Skills)        │                                    │
│   │            │  │  aws-containers (Agent Toolkit)        │                                    │
│   │            │  └────────────────────────────────────────┘                                    │
│   │            │ reviews, writes, and applies                                                   │
│   │            │  ┌─ 1. ───────────────────────────────────┐                                    │
│   │            ├─▶│  the workload design                   │                                    │
│   │            │  └────────────────────────────────────────┘                                    │
│   ▼            ▼                                                                                │
│  ┌─ EKS Auto Mode cluster (part 20) ─────────────────────────────────────────────────────────┐  │
│  │                                                                                           │  │
│  │  ┌─ 2. ────────────────────────────┐                        ┌─ 3. ──────────────────┐     │  │
│  │  │  NodePool                       │                        │  IngressClass and     │     │  │
│  │  └──────────────────┬──────────────┘                        │  IngressClassParams   │     │  │
│  │                     │                                       └───────────────────────┘     │  │
│  │                     │                                                   ▲                 │  │
│  │                     │                                                   │ references      │  │
│  │                     │  ┌─ 4. ───────────────────────────────────────────┼──────────────┐  │  │
│  │                     │  │  sample workload                               │              │  │  │
│  │                     │  │  ┌──────────────────┐              ┌───────────┴───────────┐  │  │  │
│  │                     │  │  │  Service         │◀─ routes to ─│  Ingress              │  │  │  │
│  │                     │  │  └────────┬─────────┘              └───────────┬───────────┘  │  │  │
│  │                     │  │           │ selects the pods of                │              │  │  │
│  │                     │  │           ▼                                    │              │  │  │
│  │                     │  │  ┌──────────────────┐                          │              │  │  │
│  │                     │  │  │  Deployment      │                          │              │  │  │
│  │                     │  │  └────────┬─────────┘                          │              │  │  │
│  │                     │  └───────────┼────────────────────────────────────┼──────────────┘  │  │
│  │                     │ launches     │ runs                               │ creates         │  │
│  └─────────────────────┼──────────────┼────────────────────────────────────┼─────────────────┘  │
│  ┌─ VPC (part 10) ─────┼──────────────┼────────────────────────────────────┼─────────────────┐  │
│  │  ┌─ private subnets ┼──────────────┼──────────────┐                     │                 │  │
│  │  │                  ▼              │              │                     │                 │  │
│  │  │  ┌─ 4. ─────────────────────────┼───────────┐  │                     │                 │  │
│  │  │  │  nodes                       ▼           │  │                     │                 │  │
│  │  │  │                    ┌─ 4. ──────────────┐ │  │                     │                 │  │
│  │  │  │                    │  pods             │ │  │                     │                 │  │
│  │  │  │                    └───────────────────┘ │  │                     │                 │  │
│  │  │  │                              ▲           │  │                     │                 │  │
│  │  │  └──────────────────────────────┼───────────┘  │                     │                 │  │
│  │  └─────────────────────────────────┼──────────────┘                     │                 │  │
│  │                                    │ forwards to                        │                 │  │
│  │  ┌─ public subnets ────────────────┼────────────────────────────────────┼──────────────┐  │  │
│  │  │                                 │                                    ▼              │  │  │
│  │  │  ┌─ 4. ─────────────────────────┴────────────────────────────────────────────────┐  │  │  │
│  │  │  │  load balancer                                                                │  │  │  │
│  │  │  └───────────────────────────────────────────────────────────────────────────────┘  │  │  │
│  │  │                                                                      ▲              │  │  │
│  │  └──────────────────────────────────────────────────────────────────────┼──────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┼─────────────────┘  │
│                                                                            │ reaches            │
│                                                                        internet                 │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Reviewing the workload design](#reviewing-the-workload-design) | Reviews the design of the NodePool, the IngressClass, and the sample workload |
| [2. Creating the NodePool with a Kubernetes manifest](#creating-the-nodepool-with-a-kubernetes-manifest) | Creates the NodePool that the cluster launches nodes from |
| [3. Creating the IngressClass with a Kubernetes manifest](#creating-the-ingressclass-with-a-kubernetes-manifest) | Creates the IngressClass, and its IngressClassParams, that the cluster creates a load balancer from |
| [4. Creating the sample workload with a Kubernetes manifest](#creating-the-sample-workload-with-a-kubernetes-manifest) | Creates the Deployment, Service, and Ingress of the sample workload |

## Reviewing the workload design

The workload is the first thing to run on the cluster. It takes three
kinds of Kubernetes resources, and each of them is a manifest of its own
in the steps that follow:

- A NodePool, which the cluster launches nodes from.
- An IngressClass, with its IngressClassParams, which the cluster creates a
  load balancer from.
- The Deployment, the Service, and the Ingress of the sample workload.

The NodePool and the IngressClass are cluster-wide resources that the
platform owns, and they outlive any one workload. The Deployment, the
Service, and the Ingress live in a namespace and belong to the workload.

Before you ask the agent to write the manifests, review the three designs
together with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the workload design, start a Claude Code session at the
repository root and paste the following review request. Fill its "Design"
section with the "Kubernetes resource settings" sections of the prompts of
steps 2, 3, and 4, in that order.

````text
/apex:eks-design

# Review request
I am running the first workload on an EKS Auto Mode cluster.
The design below consists of the following.
- A NodePool for workloads
- An IngressClass and IngressClassParams for routing
- The Deployment, Service, and Ingress of a sample workload
Review the design with the context in mind.

## Context
- This is a personal lab. It is torn down every night to keep the cost down.
- The VPC and the EKS Auto Mode cluster already exist.
  - The subnets of the VPC have the following tags.
    - public: kubernetes.io/role/elb = 1
    - private: kubernetes.io/role/internal-elb = 1
  - Among the built-in NodePools, only system is enabled.
- The following concerns are out of scope here.
  - Tenant isolation
  - Scaling and availability
  - Pod health checks
  - Pod security
  - A custom domain and HTTPS

## Design
```
(the "Kubernetes resource settings" sections of the prompts of steps 2, 3, and 4)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 4
are the result of a few rounds.
