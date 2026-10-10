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
│   │            │  │  ┌─ 5. ───────────────────────────────┐  │                         │
│   │            ├──┼─▶│  manifest of the sample workload   │  │                         │
│   │            │  │  └──────────────────┬─────────────────┘  │                         │
│   │            │  └─────────────────────┼────────────────────┘                         │
│   │            │                        │ is copied to                                 │
│   │            │                        ▼                                              │
│   │            │  ┌─ 5. ─────────────────────────────────────┐                         │
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
│  │  │  ┌─ 4. ───────────────────┐  │  │  ┌─ 3. ────────────────────────────────┐  │ │  │
│  │  │  │  AppProject            │  │  │  │  Role and RoleBindings              │  │ │  │
│  │  │  └────────────────────────┘  │  │  └─────────────────────────────────────┘  │ │  │
│  │  │  ┌─ 5. ───────────────────┐  │  │  ┌─ 5. ────────────────────────────────┐  │ │  │
│  │  │  │  ApplicationSet        │  │  │  │  sample workload                    │  │ │  │
│  │  │  └────────────┬───────────┘  │  │  │  ┌────────────┐   ┌───────────────┐ │  │ │  │
│  │  │               │ creates      │  │  │  │  Rollout   │   │  ReplicaSets  │ │  │ │  │
│  │  │               ▼              │  │  │  └────────────┘   └───────────────┘ │  │ │  │
│  │  │  ┌─ 5. ───────────────────┐  │  │  │        ▲                 ▲          │  │ │  │
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
| [3. Granting permissions to write Rollouts with a Kubernetes manifest](#granting-permissions-to-write-rollouts-with-a-kubernetes-manifest) | Creates the Role and the RoleBindings that let the developers and Argo CD write Rollouts in the tenant namespace |
| [4. Allowing the Applications of the tenant to sync Rollouts with a Kubernetes manifest](#allowing-the-applications-of-the-tenant-to-sync-rollouts-with-a-kubernetes-manifest) | Adds Rollout to the allow list of the AppProject of the tenant |
| [5. Creating the sample workload](#creating-the-sample-workload) | Creates a sample workload as a Rollout, and the ApplicationSet that syncs it into the tenant namespace |
| [6. Rolling out a new version](#rolling-out-a-new-version) | Rolls out a new version of the sample workload, and promotes it |
| [7. Aborting a rollout](#aborting-a-rollout) | Aborts a rollout of the sample workload in progress, and the previous version keeps running |

## Reviewing the Argo Rollouts design

The steps that follow install Argo Rollouts and deploy a sample workload
of the tenant as a Rollout through the Argo CD capability. Before you ask
the agent to write the Kubernetes manifests, review their design with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the design, start a Claude Code session at the repository root
and paste the following review request. Fill its "Design" section with
the "Kubernetes resource settings" sections of the prompts of steps 2 to
5, in this order.

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
(the "Kubernetes resource settings" sections of the prompts of steps 2 to 5)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 5
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

## Granting permissions to write Rollouts with a Kubernetes manifest

The developers and Argo CD may read Rollouts through the built-in role
view, but writing them needs a Role that allows writing Rollouts and
their status. This step grants the Role to the developers and Argo CD.

To grant the permissions:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest that grants the developers and the Argo CD capability the permissions to write Rollouts of Argo Rollouts in the tenant of the EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/60-argo-rollouts/manifests/rbac.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace team-a.

   ### Kubernetes resource list
   - Role: 1
   - RoleBinding: 2

   ### Role
   - Name it rollouts-edit.
   - Allow creating, updating, and deleting Rollouts.
   - Allow updating the status of Rollouts.

   ### RoleBinding for the developers
   - Name it developer-rollouts.
   - Grant the permissions of the Role rollouts-edit to the group team-a-dev.

   ### RoleBinding for Argo CD
   - Name it argocd-rollouts.
   - Grant the permissions of the Role rollouts-edit to the group argocd.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the Role allows nothing but Rollouts
   and their status, and that nothing was added that the prompt did not
   ask for. The file [manifests/rbac.yaml](manifests/rbac.yaml) is the
   result of this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/60-argo-rollouts/manifests/rbac.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/60-argo-rollouts/manifests/rbac.yaml
   ```

3. Check the permissions. The developers and Argo CD may create Rollouts
   and update their status in the namespace `team-a`.

   To check this, ask the agent:

   ```text
   Check the permissions on Rollouts in the cluster:

   - With the context <account-name>-team-a-dev, Rollouts can be created and their status can be patched in the namespace team-a.
   - The group argocd can create Rollouts and patch their status in the namespace team-a.
   ```

   Or run the commands yourself:

   ```bash
   kubectl --context <account-name>-team-a-dev \
     auth can-i create rollouts.argoproj.io -n team-a

   kubectl --context <account-name>-team-a-dev \
     auth can-i patch rollouts.argoproj.io --subresource=status -n team-a

   kubectl --as=argocd-check --as-group=argocd \
     auth can-i create rollouts.argoproj.io -n team-a

   kubectl --as=argocd-check --as-group=argocd \
     auth can-i patch rollouts.argoproj.io --subresource=status -n team-a
   ```

   All four commands print `yes`.

## Allowing the Applications of the tenant to sync Rollouts with a Kubernetes manifest

The AppProject of the tenant lists the kinds of resources in namespaces
that its Applications may sync. Rollout is not in the list, so Argo CD
does not sync a Rollout of the tenant until the AppProject allows it.

To allow the Applications to sync Rollouts:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest that adds Rollouts of Argo Rollouts to the kinds of resources that an AppProject of the Argo CD capability allows to sync.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/60-argo-rollouts/manifests/project.yaml.

   ## Kubernetes resource settings

   ### Kubernetes resource list
   - AppProject: 1

   ### AppProject
   - The AppProject to change is in parts/50-argo-cd/manifests/project.yaml.
   - Add Rollouts of Argo Rollouts to the kinds of resources in namespaces that it allows to sync.
   - Keep its other settings as they are.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, compare it with the
   AppProject that it changes:

   ```bash
   diff \
     parts/50-argo-cd/manifests/project.yaml \
     parts/60-argo-rollouts/manifests/project.yaml
   ```

   The only difference is Rollout with the group `argoproj.io`. The file
   [manifests/project.yaml](manifests/project.yaml) is the result of this
   step.

2. Apply the manifest, with the ID of the group in place of
   `<eks-platform-lab-team-a-group-id>`. Ask the agent:

   ```text
   Apply parts/60-argo-rollouts/manifests/project.yaml to the cluster,
   with <eks-platform-lab-team-a-group-id> replaced by the ID of the IAM Identity Center group eks-platform-lab-team-a,
   taken with the profile <account-name>-admin.
   ```

   Or run the commands yourself:

   ```bash
   store_id=$( \
   aws --profile <account-name>-admin \
     sso-admin list-instances \
     --query 'Instances[0].IdentityStoreId' \
     --output text \
   )

   group_id=$( \
   aws --profile <account-name>-admin \
     identitystore get-group-id --identity-store-id "$store_id" \
     --alternate-identifier '{"UniqueAttribute":{"AttributePath":"DisplayName","AttributeValue":"eks-platform-lab-team-a"}}' \
     --query 'GroupId' \
     --output text \
   )

   sed "s|<eks-platform-lab-team-a-group-id>|${group_id}|" parts/60-argo-rollouts/manifests/project.yaml | kubectl apply -f -
   ```

3. Check the AppProject. The AppProject `team-a` allows Rollouts.

   To check this, ask the agent:

   ```text
   Check that the AppProject team-a in the namespace argocd of the cluster allows Rollouts in namespaces.
   ```

   Or run the command yourself:

   ```bash
   kubectl get appproject team-a -n argocd \
     -o jsonpath='{.spec.namespaceResourceWhitelist[?(@.kind=="Rollout")]}'
   ```

   The output is Rollout with the group `argoproj.io`.
