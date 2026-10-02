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

## Reviewing the GitOps design

The steps that follow write the Argo CD capability as a Terraform
configuration, and the cluster registration, the sample workload, and
the Application as Kubernetes manifests. Before you ask the agent to
write them, review the design with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the design, start a Claude Code session at the repository root
and paste the following review request. Fill its "Design" section with
the following sections of the prompts, in this order:

- The "AWS resource settings" section of step 2
- The "Kubernetes resource settings" sections of steps 3 to 5

````text
/apex:eks-design

# Review request
On an EKS Auto Mode cluster, I am deploying a sample application to a tenant with GitOps, using the Argo CD capability of EKS.
The design below consists of the following.
- The Argo CD capability, its IAM role, and its access to the cluster
- The registration of the cluster with Argo CD
- The Deployment, Service, and Ingress of the sample application, kept in a Git repository
- The Argo CD Application that syncs the sample application
Review the design with the context in mind.

## Context
- This is a personal lab. It is torn down every night to keep the cost down.
- The following components already exist.
  - The VPC
  - The EKS Auto Mode cluster
  - The namespace of the tenant and its guardrails
- The Git repository is a public repository on GitHub.
- Only the administrators of the cluster create Applications.
- The following concern is out of scope here.
  - Scaling and availability

## Design
```
(the sections of the prompts of steps 2 to 5)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 5
are the result of a few rounds.
