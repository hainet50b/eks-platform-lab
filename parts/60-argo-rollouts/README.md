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

## Reviewing the Argo Rollouts design

The steps that follow install Argo Rollouts and deploy a sample workload
of the tenant as a Rollout through the Argo CD capability. Before you ask
the agent to write the Kubernetes manifests, review their design with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the design, start a Claude Code session at the repository root
and paste the following review request. Fill its "Design" section with
the "Kubernetes resource settings" sections of the prompts of steps 2 to
4, in this order.

````text
/apex:eks-design

# Review request
On an EKS Auto Mode cluster, I am installing Argo Rollouts and rolling out a sample application of a tenant in steps with a Rollout, through the Argo CD capability.
The design below consists of the following.
- The installation of Argo Rollouts
- The permissions for the developers and Argo CD to write Rollouts in the tenant
- The AppProject of the tenant
- The Rollout, Service, and Ingress of the sample application, kept in a Git repository
- The ApplicationSet that creates the Applications of the workloads that use Rollouts
Review the design with the context in mind.

## Context
- This is a personal lab. It is torn down every night to keep the cost down.

## Design
```
(the "Kubernetes resource settings" sections of the prompts of steps 2 to 4)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 4
are the result of a few rounds.

## Installing Argo Rollouts with Kustomize

[Argo Rollouts](https://argo-rollouts.readthedocs.io/en/stable/) is a
Kubernetes controller and a set of CRDs for rolling out a new version of
a workload in steps. The installation manifest introduced in the
[official documentation](https://argo-rollouts.readthedocs.io/en/stable/installation/)
includes:

- The CRDs, such as Rollout
- The controller, as a Deployment in the namespace argo-rollouts
- ClusterRoles that add the permissions on Rollouts to the built-in
  roles view, edit, and admin

[Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/),
which is built into kubectl, customizes manifests without changing them.
This step installs Argo Rollouts by customizing the installation
manifest with Kustomize.

To install Argo Rollouts:

1. Ask the agent to write the kustomization. Start a Claude Code session
   at the repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a kustomization that installs Argo Rollouts on the EKS Auto Mode cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the kustomization in parts/60-argo-rollouts/manifests/argo-rollouts/.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace argo-rollouts.

   ### Kubernetes resource list
   - Namespace: 1
   - The resources in the official installation manifest of Argo Rollouts

   ### Namespace
   - Name it argo-rollouts.

   ### Argo Rollouts
   - Refer to the official installation manifest of the latest stable release by a URL that includes its version.
   - Place the pods of the controller on the nodes of the NodePool system.

   ## Style
   - Make it possible to apply with kubectl apply -k --server-side.
   - Keep the configuration, and especially the comments, to the minimum.
   ```

   The agent writes the kustomization. Before you go on, read it against
   the prompt. In particular, check that the controller has a toleration
   for the taint `CriticalAddonsOnly`, and that nothing was added that the
   prompt did not ask for. To list the resources that the kustomization
   produces, run:

   ```bash
   kubectl create -k parts/60-argo-rollouts/manifests/argo-rollouts --dry-run=client
   ```

   The list starts with the namespace argo-rollouts, followed by the
   resources of the installation manifest, such as the CRDs, the
   ClusterRoles, and the Deployment of the controller.

   The directory [manifests/argo-rollouts](manifests/argo-rollouts) is
   the result of this step.

2. Apply the kustomization in two passes: first the ClusterRoles that
   add the permissions on Rollouts to the built-in roles, then the rest.
   Argo CD checks whether it may read Rollouts when their CRD appears,
   and leaves them out if it may not. With the ClusterRoles in place
   first, Argo CD can read Rollouts as soon as the CRD appears.
   Both passes use server-side apply, because the CRDs are too large for
   the annotation that a client-side apply adds. Ask the agent:

   ```text
   Apply the kustomization parts/60-argo-rollouts/manifests/argo-rollouts to the cluster
   with server-side apply, in two passes:

   1. Only the ClusterRoles labeled app.kubernetes.io/component=aggregate-cluster-role
   2. All of it
   ```

   Or run the commands yourself:

   ```bash
   kubectl apply -k parts/60-argo-rollouts/manifests/argo-rollouts \
     --server-side \
     -l app.kubernetes.io/component=aggregate-cluster-role

   kubectl apply -k parts/60-argo-rollouts/manifests/argo-rollouts \
     --server-side
   ```

3. Check the installation. The controller runs on a node of the NodePool
   `system`, the API group argoproj.io has the kind Rollout, and the
   developers may read Rollouts in the tenant namespace. A new node for
   the controller can take several minutes to appear.

   To check this, ask the agent:

   ```text
   Check Argo Rollouts in the cluster:

   - The pod of the controller in the namespace argo-rollouts runs on a node of the NodePool system.
   - The API group argoproj.io has the kind Rollout.
   - With the context <account-name>-team-a-dev, Rollouts can be listed in the namespace team-a.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get pods -n argo-rollouts -o wide

   kubectl get nodes -L karpenter.sh/nodepool

   kubectl api-resources --api-group=argoproj.io

   kubectl --context <account-name>-team-a-dev \
     get rollouts -n team-a
   ```

   The pod is `Running` on a node whose NodePool is `system`. The API
   group lists Rollout. The last command prints `No resources found`, not
   `Forbidden`.
