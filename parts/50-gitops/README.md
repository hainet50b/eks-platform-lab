# 50 gitops

Argo CD, which keeps the workloads in sync with a Git repository.

## Overview

```
┌─ 50 gitops ──────────────────────────────────────────────────────────────────┐
│                                                                              │
│  you ──────▶ coding agent                                                    │
│   │            │                                                             │
│   │            │  ┌─ agent skills ───────────────────────────┐               │
│   │            ├─▶│  /apex:eks-design (APEX Skills)          │               │
│   │            │  │  terraform-skill (APEX Skills)           │               │
│   │            │  │  terraform-style-guide (HashiCorp)       │               │
│   │            │  │  aws-containers (Agent Toolkit)          │               │
│   │            │  └──────────────────────────────────────────┘               │
│   │            │ reviews, writes, runs, and applies                          │
│   │            │  ┌─ 1. ─────────────────────────────────────┐               │
│   │            ├─▶│  the GitOps design                       │               │
│   │            │  └──────────────────────────────────────────┘               │
│   │            │                                                             │
│   │            │  ┌─ this repository ────────────────────────┐               │
│   │            │  │  ┌─ 4. ───────────────────────────────┐  │               │
│   │            ├──┼─▶│  manifest of the sample workload   │  │               │
│   │            │  │  └──────────────────┬─────────────────┘  │               │
│   │            │  └─────────────────────┼────────────────────┘               │
│   │            │                        │ is copied to                       │
│   │            │                        ▼                                    │
│   │            │  ┌─ 4. ─────────────────────────────────────┐               │
│   ├─ pushes ───┼─▶│  workloads repository                    │               │
│   │            │  └─────────────────────┬────────────────────┘               │
│   ▼            ▼                        │ is read by                         │
│  ┌─ EKS Auto Mode cluster (part 20) ────┼─────────────────────────────────┐  │
│  │                                      ▼                                 │  │
│  │  ┌─ 2. ─────────────────────────────────┐                              │  │
│  │  │  Argo CD capability                  ├─── syncs ───┐                │  │
│  │  └─────────────┬────────────────────────┘             │                │  │
│  │                │ follows                              │                │  │
│  │                ▼                                      ▼                │  │
│  │  ┌─ argocd namespace ───────────────┐    ┌─ namespace (part 40) ───┐   │  │
│  │  │  ┌─ 3. ───────────────────────┐  │    │  ┌─ 5. ──────────────┐  │   │  │
│  │  │  │  cluster registration      │  │    │  │  sample workload  │  │   │  │
│  │  │  └────────────────────────────┘  │    │  └───────────────────┘  │   │  │
│  │  │  ┌─ 5. ───────────────────────┐  │    │                         │   │  │
│  │  │  │  Application               │  │    │                         │   │  │
│  │  │  └────────────────────────────┘  │    │                         │   │  │
│  │  └──────────────────────────────────┘    └─────────────────────────┘   │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Reviewing the GitOps design](#reviewing-the-gitops-design) | Reviews the design of the Argo CD capability, the cluster registration, the Application, and the sample workload |
| [2. Creating the Argo CD capability with Terraform](#creating-the-argo-cd-capability-with-terraform) | Creates the Argo CD capability, with its IAM role and the access that lets it apply manifests to the cluster |
| [3. Registering the cluster with a Kubernetes manifest](#registering-the-cluster-with-a-kubernetes-manifest) | Registers the cluster with Argo CD as the destination for workloads |
| [4. Creating the workloads repository](#creating-the-workloads-repository) | Writes the manifest of the sample workload and copies it to a new Git repository that Argo CD reads |
| [5. Syncing the sample workload](#syncing-the-sample-workload) | Creates the Application, and Argo CD syncs the sample workload from the workloads repository into the tenant namespace |
| [6. Deploying and rolling back the sample workload](#deploying-and-rolling-back-the-sample-workload) | Changes the image of the sample workload with a push to the workloads repository, then reverts the change |
