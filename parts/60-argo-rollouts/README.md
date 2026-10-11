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
| [2. Installing Argo Rollouts with Kustomize](#installing-argo-rollouts-with-kustomize) | Installs the CRDs and the controller of Argo Rollouts, and invalidates the cache of Argo CD |
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

2. Apply the kustomization with server-side apply, because the CRDs are
   too large for the annotation that a client-side apply adds. Ask the
   agent:

   ```text
   Apply the kustomization parts/60-argo-rollouts/manifests/argo-rollouts to the cluster
   with server-side apply.
   ```

   Or run the command yourself:

   ```bash
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

4. Invalidate the cache of Argo CD. Argo CD looks up the kinds of
   resources that it may read in the cluster, then builds a cache of the
   resources of those kinds. A kind added after the cache is built, such
   as Rollout, is not in the cache.

   To rebuild the cache, sign in to the UI of Argo CD as the
   administrator. To get the URL of the UI, run:

   ```bash
   aws --profile <account-name>-admin \
     eks describe-capability --cluster-name eks-platform-lab --capability-name argocd \
     --query 'capability.configuration.argoCd.serverUrl' \
     --output text
   ```

   Then open **Settings**, then **Clusters**, then `in-cluster`, and
   select **Invalidate Cache**.

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

## Creating the sample workload

A [Rollout](https://argo-rollouts.readthedocs.io/en/stable/features/specification/)
has the same pod template as a Deployment, and adds a strategy that
replaces the pods of the old version with those of the new version in
steps. Each step of the
[canary strategy](https://argo-rollouts.readthedocs.io/en/stable/features/canary/)
either sets the weight of the new version or pauses. Without a traffic
router, the weight is the ratio of the pods of the new version. The
sample workload takes the following steps:

- 25%, then pause until it is promoted
- 50%, then pause for 60 seconds
- 100%

Its pods also have a readiness probe and wait 10 seconds before they
stop, so that the ALB sends requests only to the pods that can answer
them while the pods are replaced.

To create the sample workload:

1. Ask the agent to write the manifest of the sample workload. Start a
   Claude Code session at the repository root and paste the following
   prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the Rollout of Argo Rollouts, Service, and Ingress of a sample workload in a tenant on an EKS Auto Mode cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/60-argo-rollouts/workloads/team-a-argo-rollouts/pod-ratio/nginx-argo-rollouts-pod-ratio/nginx-argo-rollouts-pod-ratio.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace team-a.
   - Use the label app.kubernetes.io/name: nginx-argo-rollouts-pod-ratio.

   ### Kubernetes resource list
   - Rollout: 1
   - Service: 1
   - Ingress: 1

   ### Rollout
   - Name it nginx-argo-rollouts-pod-ratio.
   - Run 4 replicas.
   - Use the following container image.
     - Image: public.ecr.aws/nginx/nginx-unprivileged
     - Tag: the latest release of the stable line
   - Make the pods meet the restricted level of Pod Security Standards.
   - Request the following resources.
     - CPU: 100m
     - Memory: 128Mi
   - Limit the memory only, to 128Mi.
   - Switch to a new version as follows.
     - Raise the ratio of the pods of the new version to 25%, 50%, and 100%, in this order.
     - At 25%, wait until a developer promotes it.
     - At 50%, wait 60 seconds, then go on.
   - Check whether a pod can take requests with an HTTP GET of the path / on port 8080.
   - Make the container wait 10 seconds before it stops.

   ### Service
   - Name it nginx-argo-rollouts-pod-ratio.
   - Make it reachable only from inside the cluster.
   - Send to the pods of the Rollout nginx-argo-rollouts-pod-ratio.
   - Receive on port 80 and send to port 8080 of the pods.

   ### Ingress
   - Name it nginx-argo-rollouts-pod-ratio.
   - Use the IngressClass alb.
   - Make the IP addresses of the pods the targets of the ALB.
   - Set no host, and send every request under the path / to port 80 of the Service nginx-argo-rollouts-pod-ratio.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt, and check that nothing was added that the prompt did not ask
   for. The file
   [workloads/team-a-argo-rollouts/pod-ratio/nginx-argo-rollouts-pod-ratio/nginx-argo-rollouts-pod-ratio.yaml](workloads/team-a-argo-rollouts/pod-ratio/nginx-argo-rollouts-pod-ratio/nginx-argo-rollouts-pod-ratio.yaml)
   is the result of this step.

2. Push the directory of the sample workload to the workloads
   repository:

   ```bash
   mkdir -p ../eks-platform-lab-workloads/team-a-argo-rollouts/pod-ratio
   cp -r parts/60-argo-rollouts/workloads/team-a-argo-rollouts/pod-ratio/nginx-argo-rollouts-pod-ratio \
     ../eks-platform-lab-workloads/team-a-argo-rollouts/pod-ratio/

   git -C ../eks-platform-lab-workloads add team-a-argo-rollouts
   git -C ../eks-platform-lab-workloads commit -m "Add the sample workload that rolls out in steps"

   git -C ../eks-platform-lab-workloads push
   ```

3. Ask the agent to write the manifest of the ApplicationSet. Start a
   Claude Code session at the repository root and paste the following
   prompt. Replace `<owner>` with the owner of the workloads repository.

   ```text
   /aws-containers

   # Summary
   Create a manifest for an ApplicationSet that creates the Applications of a tenant that use Rollouts of Argo Rollouts, for the Argo CD capability of an EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/60-argo-rollouts/manifests/applicationset.yaml.

   ## Kubernetes resource settings

   ### Common
   - Put the ApplicationSet in the namespace argocd.

   ### Kubernetes resource list
   - ApplicationSet: 1

   ### ApplicationSet
   - Name it team-a-argo-rollouts-pod-ratio.
   - Create an Application for each directory right under the following directory.
     - Repository: https://github.com/<owner>/eks-platform-lab-workloads.git
     - Branch: main
     - Directory: team-a-argo-rollouts/pod-ratio
   - Make the Applications as follows.
     - Name each team-a-<name of the directory>.
     - Use the Argo CD project team-a.
     - Sync the directory.
     - Deploy to the namespace team-a of the cluster in-cluster.
     - Sync changes in Git automatically.
       - Delete from the cluster what is removed from Git.
       - Revert changes made in the cluster to the state in Git.
     - When an Application is deleted, delete the resources that it synced.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, compare it with the
   ApplicationSet of the tenant:

   ```bash
   diff \
     parts/50-argo-cd/manifests/applicationset.yaml \
     parts/60-argo-rollouts/manifests/applicationset.yaml
   ```

   The only differences are the name and the directory. The file
   [manifests/applicationset.yaml](manifests/applicationset.yaml) is the
   result of this step.

4. Apply the manifest. Ask the agent:

   ```text
   Apply parts/60-argo-rollouts/manifests/applicationset.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/60-argo-rollouts/manifests/applicationset.yaml
   ```

5. Check the sync. The Application `team-a-nginx-argo-rollouts-pod-ratio`
   is `Synced` and `Healthy`, the Rollout in it is `Synced`, and the
   sample workload answers through its ALB. The ALB can take several
   minutes to answer.

   To check this, ask the agent:

   ```text
   Check the sync of the sample workload on the cluster:

   - The Application team-a-nginx-argo-rollouts-pod-ratio in the namespace argocd is synced and healthy.
   - In the Application, the Rollout nginx-argo-rollouts-pod-ratio is synced.
   - The ALB of the Ingress nginx-argo-rollouts-pod-ratio in the namespace team-a answers, with the version of nginx in its Server header.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get application team-a-nginx-argo-rollouts-pod-ratio -n argocd

   kubectl get application team-a-nginx-argo-rollouts-pod-ratio -n argocd \
     -o jsonpath='{.status.resources[?(@.kind=="Rollout")].status}'

   alb=$( \
   kubectl get ingress nginx-argo-rollouts-pod-ratio -n team-a \
     -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
   )

   curl -sI "http://${alb}/"
   ```

   The first command shows `Synced` and `Healthy`. The second prints
   `Synced`. The `curl` prints `Server: nginx/` followed by the version
   of the image.

6. Set up the kubectl plugin of Argo Rollouts.
   [Install the plugin](https://argo-rollouts.readthedocs.io/en/stable/installation/#kubectl-plugin-installation),
   which adds the command `kubectl argo rollouts` to see and operate
   Rollouts, then check it:

   ```bash
   kubectl argo rollouts version
   ```

7. See the Rollout as the developer:

   ```bash
   kubectl argo rollouts --context <account-name>-team-a-dev \
     get rollout nginx-argo-rollouts-pod-ratio -n team-a
   ```

   The Rollout is `Healthy`, with 4 pods of one revision, marked
   `stable`.

8. Open the Application in the UI of Argo CD as the developer. To get the
   URL of the UI, run:

   ```bash
   aws --profile <account-name>-admin \
     eks describe-capability --cluster-name eks-platform-lab --capability-name argocd \
     --query 'capability.configuration.argoCd.serverUrl' \
     --output text
   ```

   In the tree of the Application, the Rollout is `Healthy`, with its
   ReplicaSet and pods under it.

## Rolling out a new version

When the image of the sample workload changes in Git, the Rollout
replaces its pods through its steps. This step rolls out a new version,
and sees the ratio of the pods and of the requests change at each step.
At the step that waits to be promoted, the developer promotes the
Rollout in the UI of Argo CD to go on, or promotes it fully to skip the
remaining steps.

To roll out a new version:

1. Watch the Rollout as the developer, in a separate terminal:

   ```bash
   kubectl argo rollouts --context <account-name>-team-a-dev \
     get rollout nginx-argo-rollouts-pod-ratio -n team-a --watch
   ```

2. Roll out a new version. In the workloads repository, change the image
   of the sample workload to the latest release of the mainline line of
   nginx, and push the change. Replace `<mainline-version>` with that
   release, such as `1.31.6`:

   ```bash
   sed -i 's#nginx-unprivileged:.*#nginx-unprivileged:<mainline-version>#' \
     ../eks-platform-lab-workloads/team-a-argo-rollouts/pod-ratio/nginx-argo-rollouts-pod-ratio/nginx-argo-rollouts-pod-ratio.yaml

   git -C ../eks-platform-lab-workloads add team-a-argo-rollouts
   git -C ../eks-platform-lab-workloads commit -m "Update the image of nginx-argo-rollouts-pod-ratio to nginx <mainline-version>"

   git -C ../eks-platform-lab-workloads push
   ```

   Argo CD picks up the change within about 10 minutes. To skip the wait,
   refresh the Application:

   ```bash
   kubectl annotate application team-a-nginx-argo-rollouts-pod-ratio -n argocd \
     argocd.argoproj.io/refresh=normal --overwrite
   ```

   The Rollout pauses at the first step, with one pod of the new version
   and three of the old one.

3. Count the versions that answer through the ALB. Without a traffic
   router, the ALB sends requests to all the pods alike, so the ratio of
   the requests follows the ratio of the pods. Wait a minute for the ALB
   to start sending requests to the new pod, then run:

   ```bash
   alb=$( \
   kubectl get ingress nginx-argo-rollouts-pod-ratio -n team-a \
     -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
   )

   for i in $(seq 1 100); do curl -sI "http://${alb}/" | grep -i '^server'; done | sort | uniq -c
   ```

   About 25 of the 100 requests reach the new version of nginx, and the
   rest reach the old one.

4. Promote the Rollout. Open the Application in the UI of Argo CD as the
   developer, open the menu of the Rollout in its tree, and select
   **Resume**, which promotes the Rollout. The Rollout goes to 50%, waits
   60 seconds, then goes to 100%.

   When the Rollout reaches 100%, check the rollout. The Application is
   `Synced` and `Healthy`, and all the requests reach the new version.

   ```bash
   kubectl get application team-a-nginx-argo-rollouts-pod-ratio -n argocd

   alb=$( \
   kubectl get ingress nginx-argo-rollouts-pod-ratio -n team-a \
     -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
   )

   for i in $(seq 1 100); do curl -sI "http://${alb}/" | grep -i '^server'; done | sort | uniq -c
   ```

5. Roll back with promote-full. Revert the commit in the workloads
   repository, push it, and refresh the Application as above:

   ```bash
   git -C ../eks-platform-lab-workloads revert --no-edit HEAD

   git -C ../eks-platform-lab-workloads push
   ```

   The rollback is a rollout too, and pauses at the first step. Select
   **Promote-Full** in the menu of the Rollout. The Rollout skips the
   remaining steps.

   When the Rollout reaches 100%, check the rollback. The Application is
   `Synced` and `Healthy`, and all the requests reach the old version
   again.

   ```bash
   kubectl get application team-a-nginx-argo-rollouts-pod-ratio -n argocd

   alb=$( \
   kubectl get ingress nginx-argo-rollouts-pod-ratio -n team-a \
     -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
   )

   for i in $(seq 1 100); do curl -sI "http://${alb}/" | grep -i '^server'; done | sort | uniq -c
   ```

## Aborting a rollout

Abort stops a rollout in progress, and gives all the pods back to the
version that ran before it. The Rollout is then `Degraded`, because Git
still asks for the new version. A commit that reverts the change makes
Git ask for the running version again, and the Rollout becomes `Healthy`
without taking the steps.

To abort a rollout:

1. Roll out the new version again. In the workloads repository, change
   the image of the sample workload to `<mainline-version>`, and push the
   change:

   ```bash
   sed -i 's#nginx-unprivileged:.*#nginx-unprivileged:<mainline-version>#' \
     ../eks-platform-lab-workloads/team-a-argo-rollouts/pod-ratio/nginx-argo-rollouts-pod-ratio/nginx-argo-rollouts-pod-ratio.yaml

   git -C ../eks-platform-lab-workloads add team-a-argo-rollouts
   git -C ../eks-platform-lab-workloads commit -m "Update the image of nginx-argo-rollouts-pod-ratio to nginx <mainline-version>"

   git -C ../eks-platform-lab-workloads push
   ```

   Refresh the Application as in the previous step. The Rollout pauses at
   the first step.

2. Abort the rollout. Select **Abort** in the menu of the Rollout in the
   UI of Argo CD.

   Check the abort. The Application is `Synced` and `Degraded`, and all
   the requests reach the old version.

   ```bash
   kubectl get application team-a-nginx-argo-rollouts-pod-ratio -n argocd

   alb=$( \
   kubectl get ingress nginx-argo-rollouts-pod-ratio -n team-a \
     -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
   )

   for i in $(seq 1 100); do curl -sI "http://${alb}/" | grep -i '^server'; done | sort | uniq -c
   ```

3. Revert the change. Revert the commit in the workloads repository,
   push it, and refresh the Application:

   ```bash
   git -C ../eks-platform-lab-workloads revert --no-edit HEAD

   git -C ../eks-platform-lab-workloads push
   ```

   Check the revert. The Application is `Synced` and `Healthy`, and all
   the requests reach the old version.

   ```bash
   kubectl get application team-a-nginx-argo-rollouts-pod-ratio -n argocd

   alb=$( \
   kubectl get ingress nginx-argo-rollouts-pod-ratio -n team-a \
     -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
   )

   for i in $(seq 1 100); do curl -sI "http://${alb}/" | grep -i '^server'; done | sort | uniq -c
   ```
