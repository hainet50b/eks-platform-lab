# 60 argo-rollouts

Argo Rollouts, which rolls out a new version of a workload in steps.

## Overview

The components of this part and how they work together:

```
┌─ 60 argo-rollouts ─────────────────────────────────────────────────────────────────────┐
│                                                                                        │
│  you ──────▶ coding agent                                                              │
│   │            │                                                                       │
│   │            │  ┌─ agent skills ───────────────────────────┐                         │
│   │            ├─▶│  /apex:eks-design (APEX Skills)          │                         │
│   │            │  │  aws-containers (Agent Toolkit)          │                         │
│   │            │  └──────────────────────────────────────────┘                         │
│   │            │ reviews, writes, and applies                                          │
│   │            │  ┌─ 1. ─────────────────────────────────────┐                         │
│   │            ├─▶│  the Argo Rollouts design                │                         │
│   │            │  └──────────────────────────────────────────┘                         │
│   │            │  ┌─ this repository ────────────────────────┐                         │
│   │            │  │  ┌─ 4. ───────────────────────────────┐  │                         │
│   │            ├──┼─▶│  manifest of the sample workload   │  │                         │
│   │            │  │  └──────────────────┬─────────────────┘  │                         │
│   │            │  └─────────────────────┼────────────────────┘                         │
│   │            │                        │ is copied to                                 │
│   │            │                        ▼                                              │
│   │            │  ┌─ 4. ─────────────────────────────────────┐                         │
│   ├─ pushes ───┼─▶│  workloads repository                    │                         │
│   │            │  └─────────────────────┬────────────────────┘                         │
│   ▼            ▼                        │ is read by                                   │
│  ┌─ EKS Auto Mode cluster (part 20) ────┼───────────────────────────────────────────┐  │
│  │                                      ▼                                           │  │
│  │  ┌─ part 50 ────────────────────────────┐                                        │  │
│  │  │  Argo CD capability                  ├─── syncs ────┐                         │  │
│  │  └───────────────┬──────────────────────┘              │                         │  │
│  │                  │ reads                               │                         │  │
│  │                  ▼                                     ▼                         │  │
│  │  ┌─ argocd namespace ───────────┐  ┌─ namespace (part 40) ─────────────────────┐ │  │
│  │  │  ┌─ 3. ───────────────────┐  │  │  ┌─ 3. ────────────────────────────────┐  │ │  │
│  │  │  │  AppProject            │  │  │  │  Role and RoleBindings              │  │ │  │
│  │  │  └────────────────────────┘  │  │  └─────────────────────────────────────┘  │ │  │
│  │  │  ┌─ 4. ───────────────────┐  │  │  ┌─ 4. ────────────────────────────────┐  │ │  │
│  │  │  │  ApplicationSet        │  │  │  │  sample workload                    │  │ │  │
│  │  │  └────────────┬───────────┘  │  │  │  ┌────────────┐   ┌───────────────┐ │  │ │  │
│  │  │               │ creates      │  │  │  │  Rollout   │   │  ReplicaSets  │ │  │ │  │
│  │  │               ▼              │  │  │  └────────────┘   └───────────────┘ │  │ │  │
│  │  │  ┌─ 4. ───────────────────┐  │  │  │        ▲                 ▲          │  │ │  │
│  │  │  │  Application           │  │  │  └────────┼─────────────────┼──────────┘  │ │  │
│  │  │  └────────────────────────┘  │  │           │                 │             │ │  │
│  │  └──────────────────────────────┘  └───────────┼─────────────────┼─────────────┘ │  │
│  │                                                │ reads and       │ creates and   │  │
│  │  ┌─ argo-rollouts namespace ────┐              │ updates         │ scales        │  │
│  │  │  ┌─ 2. ───────────────────┐  │              │                 │               │  │
│  │  │  │  Argo Rollouts         ├──┼──────────────┘                 │               │  │
│  │  │  │  controller            ├──┼────────────────────────────────┘               │  │
│  │  │  └────────────────────────┘  │                                                │  │
│  │  └──────────────────────────────┘                                                │  │
│  │                                                                                  │  │
│  │     ┌─ 2. ───────────────────┐                                                   │  │
│  │     │  Argo Rollouts CRDs    │                                                   │  │
│  │     └────────────────────────┘                                                   │  │
│  │                                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Reviewing the Argo Rollouts design](#reviewing-the-argo-rollouts-design) | Reviews the design of the Argo Rollouts controller, the permissions to write Rollouts, the AppProject of the tenant, the sample workload, and its ApplicationSet |
| [2. Installing Argo Rollouts with Kustomize](#installing-argo-rollouts-with-kustomize) | Installs the CRDs and the controller of Argo Rollouts |
| [3. Granting permissions to write Rollouts with Kubernetes manifests](#granting-permissions-to-write-rollouts-with-kubernetes-manifests) | Creates the Role and the RoleBindings that let the developers and Argo CD write Rollouts in the tenant namespace, and lets the AppProject of the tenant sync Rollouts |
| [4. Creating the sample workload](#creating-the-sample-workload) | Creates a sample workload as a Rollout, and the ApplicationSet that syncs it into the tenant namespace |
| [5. Rolling out a new version](#rolling-out-a-new-version) | Rolls out a new version of the sample workload, and promotes it |
| [6. Aborting a rollout](#aborting-a-rollout) | Aborts a rollout of the sample workload in progress, and the previous version keeps running |
