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
