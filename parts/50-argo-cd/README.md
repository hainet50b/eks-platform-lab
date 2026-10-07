# 50 argo-cd

Argo CD, which keeps the workloads in sync with a Git repository.

## Overview

The components of this part and how they work together:

```
┌─ 50 argo-cd ─────────────────────────────────────────────────────────────────┐
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
│   │            ├─▶│  the Argo CD design                      │               │
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

How the developers and Argo CD get their permissions:

```
┌─ 50 argo-cd permissions ───────────────────────────────────────────────────────────┐
│                                                                                    │
│      ┌─ IAM Identity Center (part 40) ──┐     ┌─ 2. ───────────────────────────┐   │
│      │  developers                      │   ┌▶│  IAM role                      │   │
│      │  IdC group:                      │   │ │  name: eks-platform-lab-argocd │   │
│      │    eks-platform-lab-team-a (1)   │   │ └────────────────┬───────────────┘   │
│      └─────────────────┬────────────────┘   │                  │                   │
│                        │ sign in            │ assumes          │ is mapped by      │
│ ┌─ EKS Auto Mode cluster (part 20) ─────────┼──────────────────┼─────────────────┐ │
│ │                      ▼                    │                  ▼                 │ │
│ │    ┌─ 2. ─────────────────────────────┐   │ ┌─ 5. ───────────────────────────┐ │ │
│ │    │  Argo CD capability              ├───┘ │  access entry                  │ │ │
│ │    │  name: argocd                    │     │  Kubernetes group: argocd (2)  │ │ │
│ │    │  global role: VIEWER             │     └─────────────────────────┬──────┘ │ │
│ │    │    IdC group:                    │                               │        │ │
│ │    │      eks-platform-lab-team-a (1) │                               │        │ │
│ │    └─────────────────┬────────────────┘                   is bound to │        │ │
│ │                      │ reads roles of                                 │        │ │
│ │ ┌─ namespace ────────┼───────────────────┐  ┌─ namespace (part 40) ───┼──────┐ │ │
│ │ │  name: argocd      │                   │  │  name: team-a (3)       │      │ │ │
│ │ │                    ▼                   │  │                         ▼      │ │ │
│ │ │  ┌─ 6. ─────────────────────────────┐  │  │  ┌─ 5. ─────────────────────┐  │ │ │
│ │ │  │  AppProject                      │  │  │  │  Role                    │  │ │ │
│ │ │  │  name: team-a (4)                │  │  │  │  name: argocd            │  │ │ │
│ │ │  │  destination: team-a (3)         │  │  │  │  bound by RoleBinding:   │  │ │ │
│ │ │  │  project role: developer         │  │  │  │    name: argocd          │  │ │ │
│ │ │  │    IdC group:                    │  │  │  │    subject: argocd (2)   │  │ │ │
│ │ │  │      eks-platform-lab-team-a (1) │  │  │  └──────────────────────────┘  │ │ │
│ │ │  └──────────────────────────────────┘  │  │  sample workload               │ │ │
│ │ │                                        │  └────────────────────────────────┘ │ │
│ │ │  ┌─ 8. ─────────────────────────────┐  │                                     │ │
│ │ │  │  Application                     │  │                                     │ │
│ │ │  │  project: team-a (4)             │  │                                     │ │
│ │ │  │  destination: team-a (3)         │  │                                     │ │
│ │ │  └──────────────────────────────────┘  │                                     │ │
│ │ │                                        │                                     │ │
│ │ └────────────────────────────────────────┘                                     │ │
│ │                                                                                │ │
│ └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                    │
│   (1) the same IdC group  (2) the same Kubernetes group                            │
│   (3) the same namespace  (4) the same AppProject                                  │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Reviewing the Argo CD design](#reviewing-the-argo-cd-design) | Reviews the design of the Argo CD capability, the cluster registration, the permissions of Argo CD, the AppProject and the ApplicationSet of the tenant, and the sample workload |
| [2. Creating the Argo CD capability with Terraform](#creating-the-argo-cd-capability-with-terraform) | Creates the Argo CD capability and its IAM role, and lets the developers sign in to Argo CD |
| [3. Registering the cluster with a Kubernetes manifest](#registering-the-cluster-with-a-kubernetes-manifest) | Registers the cluster with Argo CD as the destination for workloads |
| [4. Limiting what Argo CD watches with a Kubernetes manifest](#limiting-what-argo-cd-watches-with-a-kubernetes-manifest) | Creates the ConfigMap that makes Argo CD watch only the resources that it may read |
| [5. Granting Argo CD permissions with Terraform and a Kubernetes manifest](#granting-argo-cd-permissions-with-terraform-and-a-kubernetes-manifest) | Adds a Kubernetes group to the access entry of Argo CD with Terraform, and creates the ClusterRoleBinding, the Role, and the RoleBinding that let the group read the cluster and write the workloads of the tenant |
| [6. Creating the AppProject of the tenant with Kubernetes manifests](#creating-the-appproject-of-the-tenant-with-kubernetes-manifests) | Creates the AppProject that limits what the Applications of the tenant sync and lets the developers operate them |
| [7. Creating the workloads repository](#creating-the-workloads-repository) | Writes the manifest of the sample workload and copies it to a new Git repository that Argo CD reads |
| [8. Syncing the sample workload](#syncing-the-sample-workload) | Creates the ApplicationSet, which creates an Application for each workload in the repository, and Argo CD syncs the sample workload into the tenant namespace |
| [9. Deploying and rolling back the sample workload](#deploying-and-rolling-back-the-sample-workload) | Changes the image of the sample workload with a push to the workloads repository, then reverts the change |

## Reviewing the Argo CD design

The steps that follow set up the Argo CD capability to sync a sample
workload from Git into the tenant namespace. Before you ask the agent to
write the Terraform configurations and the Kubernetes manifests, review
their design with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the design, start a Claude Code session at the repository root
and paste the following review request. Fill its "Design" section with
the following sections of the prompts, in this order:

- The "AWS resource settings" section of step 2
- The "Kubernetes resource settings" sections of steps 3 and 4
- The "AWS resource settings" and "Kubernetes resource settings" sections of step 5
- The "Kubernetes resource settings" sections of steps 6 to 8

````text
/apex:eks-design

# Review request
On an EKS Auto Mode cluster, I am deploying a sample application to a tenant with GitOps, using the Argo CD capability of EKS.
The design below consists of the following.
- The Argo CD capability and its IAM role
- The registration of the cluster with Argo CD
- The ConfigMap that makes Argo CD watch only the resources that it may read
- The Terraform configuration that adds a Kubernetes group to the access entry of Argo CD
- The ClusterRoleBinding, Role, and RoleBinding that give Argo CD its permissions in the cluster
- The AppProject of the tenant
- The Deployment, Service, and Ingress of the sample application, kept in a Git repository
- The ApplicationSet that creates the Applications of the tenant
Review the design with the context in mind.

## Context
- This is a personal lab. It is torn down every night to keep the cost down.
- The following components already exist.
  - The VPC
  - The EKS Auto Mode cluster
  - The namespace of the tenant and its guardrails
- The Git repository is a public repository on GitHub.
- The following concern is out of scope here.
  - Scaling and availability

## Design
```
(the sections of the prompts of steps 2 to 8)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 8
are the result of a few rounds.

## Creating the Argo CD capability with Terraform

[Argo CD](https://argo-cd.readthedocs.io/) keeps the resources in a cluster
in sync with the manifests in a Git repository. EKS runs it as the
[Argo CD capability](https://docs.aws.amazon.com/eks/latest/userguide/argocd.html),
outside the nodes of the cluster. An Argo CD capability comes with three things:

- An IAM role that the capability assumes. The role needs permissions only
  when Argo CD reads the sources of the manifests from AWS services.
- Sign-in through IAM Identity Center. Its users and groups are mapped to
  the global roles of Argo CD.
- Access to the cluster. EKS creates an access entry for the IAM role,
  with access policies that let Argo CD manage only its own resources.

To create the Argo CD capability:

1. Ask the agent to write the configuration. Start a Claude Code session at
   the repository root and paste the following prompt.

   ```text
   /terraform-skill
   /terraform-style-guide

   # Summary
   Create a Terraform configuration for the Argo CD capability of an EKS cluster.

   ## Prerequisites
   - AWS credentials are passed at run time through AWS_PROFILE.
   - The EKS cluster already exists.
     - Its state is in the following S3 location.
       - Bucket: eks-platform-lab-terraform-state-<account ID>
       - Key: parts/20-eks-cluster/terraform.tfstate
     - The state has the following output.
       - cluster_name: the name of the EKS cluster

   ## Working environment
   - Create the Terraform configuration in parts/50-argo-cd/terraform.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 50-argo-cd
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - IAM role: 1
   - EKS capability: 1

   ### IAM role
   - Name it eks-platform-lab-argocd.
   - Make it a role that the Argo CD capability of EKS assumes.
   - Attach no permissions policy. Argo CD reads public repositories only.

   ### EKS capability
   - Make it an Argo CD capability.
   - Name it argocd.
   - Put the resources of Argo CD in the namespace argocd.
   - Authenticate with IAM Identity Center.
   - Map the IAM Identity Center groups to the Argo CD roles as follows.
     - eks-platform-lab-admins: ADMIN
     - eks-platform-lab-team-a: VIEWER
   - Create it after the IAM role has propagated, so that EKS accepts the trust policy of the role.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Use the S3 backend.
   - Use parts/50-argo-cd/terraform.tfstate as the state key.
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
   check that the capability is the resource `aws_eks_capability` of the
   AWS provider, that the instance of IAM Identity Center and the groups
   are found by name, with no IDs in the configuration, that the
   configuration associates no access policy, and that the `backend "s3"`
   block has no `bucket` line. The files in
   [terraform/](terraform/) are the result of this step.

2. Plan and apply. Make sure that the AWS CLI is signed in to the profile
   `<account-name>-admin`, then ask the agent:

   ```text
   /terraform-skill
   Initialize parts/50-argo-cd/terraform with the profile <account-name>-admin.
   Take the bucket name from the output bucket_name of parts/05-terraform-state/terraform,
   and pass it as -backend-config.
   Then show me the plan, and apply it after I approve.
   ```

   The plan adds 3 resources: the IAM role, a wait for the role to
   propagate, and the capability. The capability takes several minutes
   to become active.

   Or run the commands yourself:

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform \
     init -backend-config="bucket=${bucket_name}"

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform \
     apply terraform.tfplan
   ```

3. Check the capability. The capability is active, the administrators and
   the developers are mapped to their roles of Argo CD, the cluster has
   the namespace `argocd`, and the access entry of the IAM role has only
   the access policies that EKS associated with it.

   To check this, ask the agent:

   ```text
   Check the Argo CD capability argocd of the cluster eks-platform-lab, with the profile <account-name>-admin:

   - The capability is active, and shows the URL of its UI.
   - The group eks-platform-lab-admins is mapped to ADMIN, and the group eks-platform-lab-team-a to VIEWER.
   - The cluster has the namespace argocd.
   - The access entry of the IAM role eks-platform-lab-argocd has only the access policies that EKS associated with it.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     eks describe-capability --cluster-name eks-platform-lab --capability-name argocd \
     --query 'capability.[status, configuration.argoCd.serverUrl]' \
     --output table

   aws --profile <account-name>-admin \
     eks describe-capability --cluster-name eks-platform-lab --capability-name argocd \
     --query 'capability.configuration.argoCd.rbacRoleMappings[].[role, identities[0].id]' \
     --output table

   kubectl get namespace argocd

   role_arn=$( \
   aws --profile <account-name>-admin \
     iam get-role --role-name eks-platform-lab-argocd \
     --query 'Role.Arn' \
     --output text \
   )

   aws --profile <account-name>-admin \
     eks list-associated-access-policies --cluster-name eks-platform-lab --principal-arn $role_arn \
     --query 'associatedAccessPolicies[].[policyArn, accessScope.type]' \
     --output table
   ```

   The first command prints `ACTIVE` and the URL of the UI. The second
   lists `ADMIN` and `VIEWER`, each with the ID of a group. The last lists
   only `AmazonEKSArgoCDClusterPolicy` and `AmazonEKSArgoCDPolicy`, which
   EKS associated with the access entry when it created the capability.

4. Sign in to the UI of Argo CD. Open the URL that the first command
   printed, and sign in as the administrator. The UI shows no applications
   yet.

## Registering the cluster with a Kubernetes manifest

Argo CD deploys to the clusters
[registered](https://docs.aws.amazon.com/eks/latest/userguide/argocd-register-clusters.html)
with it. A cluster is registered with a Secret in the namespace of Argo
CD, labeled as a cluster. An Argo CD capability does not register its
own cluster, and identifies a cluster by its ARN.

To register the cluster:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest that registers the EKS cluster itself as a destination with the Argo CD capability of the cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/50-argo-cd/manifests/cluster.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace argocd.

   ### Kubernetes resource list
   - Argo CD cluster registration: 1

   ### Cluster registration
   - Register it under the name in-cluster.
   - Specify the cluster by its ARN.

   ## Style
   - Do not write the ARN of the cluster in the file; write <cluster-arn> instead. It is replaced when the manifest is applied.
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the Secret has the label
   `argocd.argoproj.io/secret-type: cluster`, that its `server` is
   `<cluster-arn>`, and that nothing was added that the prompt did not
   ask for. The file [manifests/cluster.yaml](manifests/cluster.yaml) is
   the result of this step.

2. Apply the manifest, with the ARN of the cluster in place of
   `<cluster-arn>`. Ask the agent:

   ```text
   Apply parts/50-argo-cd/manifests/cluster.yaml to the cluster,
   with <cluster-arn> replaced by the ARN of the cluster eks-platform-lab,
   taken with the profile <account-name>-admin.
   ```

   Or run the commands yourself:

   ```bash
   cluster_arn=$( \
   aws --profile <account-name>-admin \
     eks describe-cluster --name eks-platform-lab \
     --query 'cluster.arn' \
     --output text \
   )

   sed "s|<cluster-arn>|${cluster_arn}|" parts/50-argo-cd/manifests/cluster.yaml | kubectl apply -f -
   ```

3. Check the registration. The cluster is registered with Argo CD, with
   its ARN as the `server` of the Secret.

   To check this, ask the agent:

   ```text
   Check the Secret in-cluster in the namespace argocd of the cluster:

   - It registers the cluster with Argo CD.
   - Its server is the ARN of the cluster eks-platform-lab.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get secrets -n argocd -l argocd.argoproj.io/secret-type=cluster

   kubectl get secret in-cluster -n argocd -o jsonpath='{.data.server}' | base64 -d
   ```

   The first command lists `in-cluster`. The second prints the ARN of
   the cluster.

## Limiting what Argo CD watches with a Kubernetes manifest

The controller of Argo CD watches every kind of resource in the clusters
that Argo CD deploys to, so that the controller can compare the live
state with Git. By default, the controller expects to read every kind.
With the setting
[`resource.respectRBAC`](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#auto-respect-rbac-for-controller)
in the ConfigMap `argocd-cm`, the controller watches only the kinds that
Argo CD has permission to read. The Argo CD capability
[reads `argocd-cm`](https://docs.aws.amazon.com/eks/latest/userguide/argocd-configure-settings.html#_configure_the_argocd_cm_configmap)
only when the ConfigMap has the label `app.kubernetes.io/part-of: argocd`.

To limit what Argo CD watches:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest that makes the Argo CD capability of an EKS cluster watch only the resources that it has permission to read.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/50-argo-cd/manifests/argocd-cm.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace argocd.

   ### Kubernetes resource list
   - ConfigMap: 1

   ### ConfigMap
   - Make Argo CD watch only the resources that it has permission to read.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the ConfigMap is `argocd-cm` with the
   label `app.kubernetes.io/part-of: argocd`, and that nothing was added
   that the prompt did not ask for. The file
   [manifests/argocd-cm.yaml](manifests/argocd-cm.yaml) is the result of
   this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/50-argo-cd/manifests/argocd-cm.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/50-argo-cd/manifests/argocd-cm.yaml
   ```

3. Check the ConfigMap. It has the label that the capability looks for,
   and sets `resource.respectRBAC`.

   To check this, ask the agent:

   ```text
   Check the ConfigMap argocd-cm in the namespace argocd of the cluster:

   - It has the label app.kubernetes.io/part-of: argocd.
   - It sets resource.respectRBAC.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get configmap argocd-cm -n argocd --show-labels

   kubectl get configmap argocd-cm -n argocd -o jsonpath='{.data.resource\.respectRBAC}'
   ```

   The first command lists `argocd-cm` with the label. The second prints
   `normal`.

## Granting Argo CD permissions with Terraform and a Kubernetes manifest

Kubernetes [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
grants permissions to Kubernetes users and groups, and in EKS, the access
entry maps an IAM role to them. The access entry that the Argo CD
capability creates has no Kubernetes group, and its user name changes
with each session, so RBAC has no name to grant permissions to. To solve
this, the steps below add the group `argocd` to the access entry of Argo
CD, and bind roles that fit Argo CD to the group.

To grant Argo CD permissions:

1. Ask the agent to write the Terraform configuration. Start a Claude Code
   session at the repository root and paste the following prompt.

   ```text
   /terraform-skill
   /terraform-style-guide

   # Summary
   Create a Terraform configuration that adds a Kubernetes group to the EKS access entry of the Argo CD capability.

   ## Prerequisites
   - AWS credentials are passed at run time through AWS_PROFILE.
   - The EKS cluster already exists.
     - Its state is in the following S3 location.
       - Bucket: eks-platform-lab-terraform-state-<account ID>
       - Key: parts/20-eks-cluster/terraform.tfstate
     - The state has the following output.
       - cluster_name: the name of the EKS cluster
   - The Argo CD capability of EKS has already created the EKS access entry of the IAM role eks-platform-lab-argocd.

   ## Working environment
   - Create the Terraform configuration in parts/50-argo-cd/terraform-access-entry.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 50-argo-cd
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - EKS access entry: 1

   ### EKS access entry
   - Manage the access entry that the EKS capability created with this Terraform configuration.
   - Add the Kubernetes group argocd.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Use the S3 backend.
   - Use parts/50-argo-cd/terraform-access-entry.tfstate as the state key.
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
   [terraform-access-entry/](terraform-access-entry/). Before you go on,
   read the result against the prompt. In particular, check that the
   configuration imports the access entry instead of creating one, that
   it finds the cluster and the IAM role without an account ID in the
   configuration, and that the `backend "s3"` block has no `bucket` line.
   The files in [terraform-access-entry/](terraform-access-entry/) are the
   result of this step.

2. Plan and apply. Ask the agent:

   ```text
   /terraform-skill
   Initialize parts/50-argo-cd/terraform-access-entry with the profile <account-name>-admin.
   Take the bucket name from the output bucket_name of parts/05-terraform-state/terraform,
   and pass it as -backend-config.
   Then show me the plan, and apply it after I approve.
   ```

   The plan imports the access entry that the capability created, and
   changes it: 1 to import, 0 to add, 1 to change. The change adds the
   group and the tags.

   Or run the commands yourself:

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform-access-entry \
     init -backend-config="bucket=${bucket_name}"

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform-access-entry \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform-access-entry \
     apply terraform.tfplan
   ```

3. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the ClusterRoleBinding, the Role, and the RoleBinding of the Argo CD capability of an EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/50-argo-cd/manifests/rbac.yaml.

   ## Kubernetes resource settings

   ### Kubernetes resource list
   - ClusterRoleBinding: 1
   - Role: 1
   - RoleBinding: 1

   ### ClusterRoleBinding
   - Name it argocd-view.
   - Grant the permissions of the built-in ClusterRole view to the group argocd.

   ### Role
   - Name it argocd.
   - Use the namespace team-a.
   - Allow creating, updating, and deleting the following resources.
     - Workloads
       - Deployment, StatefulSet, DaemonSet, ReplicaSet
       - Job, CronJob
     - Scaling and availability
       - HorizontalPodAutoscaler
       - PodDisruptionBudget
     - Networking
       - Service
       - Ingress
     - Configuration and storage
       - ConfigMap
       - PersistentVolumeClaim
     - Identity of pods
       - ServiceAccount
   - Allow deleting pods.

   ### RoleBinding
   - Name it argocd.
   - Use the namespace team-a.
   - Grant the permissions of the Role argocd to the group argocd.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that both bindings grant to the group
   `argocd`, and that nothing was added that the prompt did not ask for.
   The file [manifests/rbac.yaml](manifests/rbac.yaml) is the result of
   this step.

4. Apply the manifest. Ask the agent:

   ```text
   Apply parts/50-argo-cd/manifests/rbac.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/50-argo-cd/manifests/rbac.yaml
   ```

5. Check the permissions of Argo CD. The access entry of Argo CD has the
   group `argocd`, and the group may write the workloads in `team-a` but
   not in other namespaces.

   To check this, ask the agent:

   ```text
   Check the permissions of Argo CD on the cluster eks-platform-lab, with the profile <account-name>-admin:

   - The access entry of the IAM role eks-platform-lab-argocd has the Kubernetes group argocd.
   - The group argocd can write the workloads in the namespace team-a, but cannot write in the namespace default.
   ```

   Or run the commands yourself:

   ```bash
   role_arn=$( \
   aws --profile <account-name>-admin \
     iam get-role --role-name eks-platform-lab-argocd \
     --query 'Role.Arn' \
     --output text \
   )

   aws --profile <account-name>-admin \
     eks describe-access-entry --cluster-name eks-platform-lab --principal-arn $role_arn \
     --query 'accessEntry.kubernetesGroups' \
     --output text

   kubectl auth can-i create deployments -n team-a --as=argocd-check --as-group=argocd

   kubectl auth can-i create deployments -n default --as=argocd-check --as-group=argocd
   ```

   The second command prints `argocd`. The last two print `yes` and `no`.

## Creating the AppProject of the tenant with Kubernetes manifests

An [AppProject](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/)
groups Applications and sets their boundary: the repositories that they
sync from, the destinations that they sync to, and the kinds of resources
that they sync. Its project roles decide who may do what with its
Applications. Argo CD also comes with the AppProject `default`, which
allows everything, so this step closes it.

To create the AppProject of the tenant:

1. Ask the agent to write the manifests. Start a Claude Code session at
   the repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create manifests for the AppProject of a tenant, for the Argo CD capability of an EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest of the AppProject team-a at parts/50-argo-cd/manifests/project.yaml.
   - Create the manifest of the AppProject default at parts/50-argo-cd/manifests/project-default.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace argocd.

   ### Kubernetes resource list
   - AppProject: 2

   ### AppProject team-a
   - Name it team-a.
   - Allow the Applications and ApplicationSets of this AppProject to be created only in the namespace argocd.
   - Allow syncing only from the following repository.
     - https://github.com/<owner>/eks-platform-lab-workloads.git
   - Allow syncing only to the namespace team-a of the cluster in-cluster.
   - Allow syncing only the following kinds of resources in the namespace.
     - Workloads
       - Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet
       - Job, CronJob
     - Scaling and availability
       - HorizontalPodAutoscaler
       - PodDisruptionBudget
     - Networking
       - Service
       - Ingress
     - Configuration and storage
       - ConfigMap
       - PersistentVolumeClaim
     - Identity of pods
       - ServiceAccount
   - Define the following project role.
     - Name: developer
     - Members: the IAM Identity Center group <eks-platform-lab-team-a-group-id>
     - Operations allowed in team-a
       - Viewing, syncing, and running the built-in actions of Applications
       - Deleting the pods of Applications
       - Viewing ApplicationSets
       - Viewing the logs of the pods of Applications

   ### AppProject default
   - Change the existing AppProject default so that it allows none of the following.
     - Syncing from any repository
     - Syncing to any destination
     - Creating Applications and ApplicationSets
     - Syncing cluster-wide resources
     - Syncing resources in namespaces

   ## Style
   - Do not write the ID of the IAM Identity Center group eks-platform-lab-team-a in the file; write <eks-platform-lab-team-a-group-id> instead. It is replaced when the manifest is applied.
   - Keep the manifests, and especially the comments, to the minimum.
   ```

   The agent writes the manifests. Before you go on, read them against
   the prompt. In particular, check that the manifest of `default` writes
   all five of its fields, and that nothing was added that the prompt did
   not ask for. The files
   [manifests/project.yaml](manifests/project.yaml) and
   [manifests/project-default.yaml](manifests/project-default.yaml) are
   the result of this step.

2. Apply the manifests, with the ID of the group in place of
   `<eks-platform-lab-team-a-group-id>`. Ask the agent:

   ```text
   Apply parts/50-argo-cd/manifests/project.yaml to the cluster,
   with <eks-platform-lab-team-a-group-id> replaced by the ID of the IAM Identity Center group eks-platform-lab-team-a,
   taken with the profile <account-name>-admin.
   Then apply parts/50-argo-cd/manifests/project-default.yaml.
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

   sed "s|<eks-platform-lab-team-a-group-id>|${group_id}|" parts/50-argo-cd/manifests/project.yaml | kubectl apply -f -

   kubectl apply -f parts/50-argo-cd/manifests/project-default.yaml
   ```

   `kubectl` warns that `default` has no record of a previous `apply`,
   because EKS created it. The warning is expected.

3. Check the AppProjects. The AppProject `team-a` syncs from only one
   repository into only the namespace `team-a`, and maps the group of the
   developers to its project role. The AppProject `default` allows nothing.

   To check this, ask the agent:

   ```text
   Check the AppProjects in the namespace argocd of the cluster:

   - The AppProject team-a
     - allows syncing from only one repository into only the namespace team-a.
     - maps the ID of the IAM Identity Center group eks-platform-lab-team-a to its project role developer.
   - The AppProject default allows no repository, no destination, and no source namespace.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get appproject team-a -n argocd \
     -o jsonpath='{.spec.sourceRepos}{"\n"}{.spec.destinations}{"\n"}{.spec.roles[0].name} {.spec.roles[0].groups}{"\n"}'

   kubectl get appproject default -n argocd \
     -o jsonpath='{.spec.sourceRepos}{"\n"}{.spec.destinations}{"\n"}{.spec.sourceNamespaces}{"\n"}'
   ```

   The first command prints the URL of the repository, the
   destination `in-cluster` and `team-a`, and the role `developer` with
   the ID of the group, which is the `group_id` above. The second prints
   three empty lists.

## Creating the workloads repository

Argo CD syncs the manifests that it reads from a Git repository. The
sample workload goes into a new public repository on GitHub, which Argo
CD reads without credentials. Its manifest is written in this repository
first, and copied to the new one.

To create the workloads repository:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the Deployment, Service, and Ingress of a sample workload in a tenant on an EKS Auto Mode cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/50-argo-cd/workloads/team-a/nginx-argocd/nginx-argocd.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace team-a.
   - Use the label app.kubernetes.io/name: nginx-argocd.

   ### Kubernetes resource list
   - Deployment: 1
   - Service: 1
   - Ingress: 1

   ### Deployment
   - Name it nginx-argocd.
   - Run 2 replicas.
   - Use the following container image.
     - Image: public.ecr.aws/nginx/nginx-unprivileged
     - Tag: the latest release of the stable line
   - Make the pods meet the restricted level of Pod Security Standards.
   - Request the following resources.
     - CPU: 100m
     - Memory: 128Mi
   - Limit the memory only, to 128Mi.

   ### Service
   - Name it nginx-argocd.
   - Make it reachable only from inside the cluster.
   - Send to the pods of the Deployment nginx-argocd.
   - Receive on port 80 and send to port 8080 of the pods.

   ### Ingress
   - Name it nginx-argocd.
   - Use the IngressClass alb.
   - Make the IP addresses of the pods the targets of the ALB.
   - Set no host, and send every request under the path / to port 80 of the Service nginx-argocd.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that it differs from the manifest of the
   sample workload of the tenant part only in its names and labels, and
   that nothing was added that the prompt did not ask for. The file
   [workloads/team-a/nginx-argocd/nginx-argocd.yaml](workloads/team-a/nginx-argocd/nginx-argocd.yaml)
   is the result of this step.

2. Create a public repository named `eks-platform-lab-workloads` on
   GitHub, and push the directory of the sample workload to it. Replace
   `<owner>` with your GitHub user or organization:

   ```bash
   gh repo create <owner>/eks-platform-lab-workloads --public

   git init -b main ../eks-platform-lab-workloads
   cp -r parts/50-argo-cd/workloads/team-a ../eks-platform-lab-workloads/
   git -C ../eks-platform-lab-workloads add team-a
   git -C ../eks-platform-lab-workloads commit -m "Add the sample workload that Argo CD syncs"

   git -C ../eks-platform-lab-workloads remote add origin https://github.com/<owner>/eks-platform-lab-workloads.git
   git -C ../eks-platform-lab-workloads push -u origin main
   ```

   Then open the repository on GitHub, and see that it is public and holds
   `team-a/nginx-argocd/nginx-argocd.yaml`.

## Syncing the sample workload

An [Application](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/)
tells Argo CD what to sync and where to deploy it: a directory of a Git
repository, and a cluster and a namespace. With automated sync, Argo CD
applies a change in Git, deletes what is removed from Git, and reverts a
change made directly in the cluster. An
[ApplicationSet](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/)
creates Applications from a template. With the
[Git directory generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Git/#git-generator-directories),
it creates an Application for each directory of the tenant in the
workloads repository, so a developer adds a workload by adding a
directory.

To sync the sample workload:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt. Replace `<owner>` with
   the owner of the workloads repository.

   ```text
   /aws-containers

   # Summary
   Create a manifest for an ApplicationSet that creates the Applications of a tenant, for the Argo CD capability of an EKS cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/50-argo-cd/manifests/applicationset.yaml.

   ## Kubernetes resource settings

   ### Common
   - Put the ApplicationSet in the namespace argocd.

   ### Kubernetes resource list
   - ApplicationSet: 1

   ### ApplicationSet
   - Name it team-a.
   - Create an Application for each directory right under the following directory.
     - Repository: https://github.com/<owner>/eks-platform-lab-workloads.git
     - Branch: main
     - Directory: team-a
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

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the template of the Applications has
   the finalizer `resources-finalizer.argocd.argoproj.io`, and that
   nothing was added that the prompt did not ask for. The file
   [manifests/applicationset.yaml](manifests/applicationset.yaml) is the
   result of this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/50-argo-cd/manifests/applicationset.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/50-argo-cd/manifests/applicationset.yaml
   ```

3. Check the sync. The ApplicationSet creates the Application
   `team-a-nginx-argocd` in the AppProject `team-a`, the Application is
   `Synced` and `Healthy`, and the sample workload answers through its ALB.

   To check this, ask the agent:

   ```text
   Check the sync of the sample workload on the cluster:

   - The ApplicationSet team-a in the namespace argocd created the Application team-a-nginx-argocd in the AppProject team-a.
   - The Application team-a-nginx-argocd is synced and healthy.
   - The ALB of the Ingress nginx-argocd in the namespace team-a answers with the nginx welcome page.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get applications -n argocd \
     -o custom-columns=NAME:.metadata.name,PROJECT:.spec.project,SYNC:.status.sync.status,HEALTH:.status.health.status

   kubectl get ingress nginx-argocd -n team-a

   curl http://<alb-dns-name>/
   ```

   The first command lists `team-a-nginx-argocd` with the project
   `team-a`, `Synced`, and `Healthy`. The `curl` gets the welcome page.

   > [!NOTE]
   > If the first sync fails because Argo CD lacks permissions, the group
   > `argocd` on the access entry may not be in effect yet. It can take up
   > to about 15 minutes. Argo CD does not retry a failed automated sync
   > of the same commit, so wait, then sync the Application again in the
   > UI of Argo CD.

4. See Argo CD revert a change made in the cluster. As the developer,
   scale the Deployment to 5 replicas. The developer may do this in the
   tenant namespace, but Argo CD puts the Deployment back to the 2
   replicas in Git shortly after.

   ```bash
   kubectl --context <account-name>-team-a-dev \
     scale deployment nginx-argocd --replicas=5

   kubectl --context <account-name>-team-a-dev \
     get deployment nginx-argocd
   ```

   The scale succeeds, and the second command shows `2/2` again.

5. Sign in to the UI of Argo CD as the developer. The developer sees only
   the Application `team-a-nginx-argocd`, and can sync it.

## Deploying and rolling back the sample workload

With GitOps, a deployment is a commit to the Git repository that Argo CD
reads, and a rollback is a commit that reverts it. Argo CD reads the
repository every few minutes, or right away on a refresh of the
Application.

To deploy and roll back the sample workload:

1. Deploy a new version. In the workloads repository, change the image
   of the sample workload to the latest release of the mainline line of
   nginx, and push the change. Replace `<mainline-version>` with that
   release, such as `1.31.6`:

   ```bash
   sed -i 's#nginx-unprivileged:.*#nginx-unprivileged:<mainline-version>#' \
     ../eks-platform-lab-workloads/nginx-argocd/nginx-argocd.yaml

   git -C ../eks-platform-lab-workloads add nginx-argocd/nginx-argocd.yaml
   git -C ../eks-platform-lab-workloads commit -m "Update the image of nginx-argocd to nginx <mainline-version>"
   git -C ../eks-platform-lab-workloads push
   ```

   Argo CD picks up the change within about 10 minutes. To skip the wait,
   refresh the Application:

   ```bash
   kubectl annotate application team-a-nginx-argocd -n argocd \
     argocd.argoproj.io/refresh=normal
   ```

2. Check the deployment. The Application is synced at the new commit,
   and the sample workload answers with the new version of nginx.

   ```bash
   kubectl get application team-a-nginx-argocd -n argocd

   curl -sI http://<alb-dns-name>/ | grep -i '^server'
   ```

   The first command shows `Synced` and `Healthy`. The `curl` prints the
   new version of nginx in the header `Server`.

3. Roll back. Revert the commit in the workloads repository and push it,
   then wait for Argo CD, or refresh the Application as in the deployment:

   ```bash
   git -C ../eks-platform-lab-workloads revert --no-edit HEAD
   git -C ../eks-platform-lab-workloads push
   ```

   The same commands as in the check of the deployment show `Synced` and
   `Healthy` again, and the version of nginx back where it was.

## Teardown

This part is torn down every night and built again the next day, because
the Argo CD capability, its Application, and the ALB of the sample
workload are charged by the hour. Tear it down before the tenant, in the
reverse order of the steps. The workloads repository stays. To build the
part again, apply the configuration and the manifests in the order of
the steps.

To tear down the Argo CD part:

1. Delete the Application. Ask the agent:

   ```text
   Delete parts/50-argo-cd/manifests/application.yaml from the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl delete -f parts/50-argo-cd/manifests/application.yaml
   ```

   The command takes a little while to return, because Argo CD deletes
   the sample workload first, and its Ingress is not gone until the
   cluster has deleted the ALB.

2. Plan and destroy. Ask the agent:

   ```text
   /terraform-skill
   Destroy parts/50-argo-cd/terraform with the profile <account-name>-admin.
   Show me the plan first, and destroy after I approve.
   ```

   Or run the commands yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform \
     plan -destroy -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform \
     apply terraform.tfplan
   ```

3. Delete what the capability leaves. EKS keeps the access entry of the
   capability, and, in the cluster, the namespace `argocd` and the custom
   resource definitions of Argo CD. Ask the agent:

   ```text
   With the profile <account-name>-admin, delete what the capability leaves in the cluster eks-platform-lab:

   - The access entry of the IAM role eks-platform-lab-argocd.
   - The namespace argocd.
   - The custom resource definitions of Argo CD.
   ```

   Or run the commands yourself:

   ```bash
   principal_arn=$( \
   aws --profile <account-name>-admin \
     eks list-access-entries --cluster-name eks-platform-lab \
     --query 'accessEntries[?contains(@, `eks-platform-lab-argocd`)] | [0]' \
     --output text \
   )

   aws --profile <account-name>-admin \
     eks delete-access-entry --cluster-name eks-platform-lab \
     --principal-arn "${principal_arn}"

   kubectl delete namespace argocd

   kubectl delete crd \
     applications.argoproj.io applicationsets.argoproj.io appprojects.argoproj.io
   ```

4. Confirm that what the three steps above deleted is gone and that
   nothing is charged. Ask the agent:

   ```text
   Check with the profile <account-name>-admin:

   - No load balancer tagged ingress.eks.amazonaws.com/stack = team-a/nginx-argocd exists.
   - The state of parts/50-argo-cd/terraform has no resources.
   - The cluster eks-platform-lab has none of these:
     - A capability.
     - An access entry of the IAM role eks-platform-lab-argocd.
     - The namespace argocd.
     - The custom resource definitions of Argo CD.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     resourcegroupstaggingapi get-resources \
     --tag-filters Key=ingress.eks.amazonaws.com/stack,Values=team-a/nginx-argocd \
     --resource-type-filters elasticloadbalancing:loadbalancer \
     --query 'ResourceTagMappingList[].ResourceARN' \
     --output table

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-argo-cd/terraform \
     state list

   aws --profile <account-name>-admin \
     eks list-capabilities --cluster-name eks-platform-lab \
     --query 'capabilities[].capabilityName' \
     --output table

   aws --profile <account-name>-admin \
     eks list-access-entries --cluster-name eks-platform-lab \
     --query 'accessEntries[?contains(@, `eks-platform-lab-argocd`)]' \
     --output table

   kubectl get namespace argocd

   kubectl get crd -o name | grep argoproj.io
   ```

   The fifth command fails with `NotFound`, and the others print nothing.

## Cost

This part is charged for the following resources while the capability
and the sample workload run.

| Resource | Name | Per day | Per month |
| --- | --- | --- | --- |
| Argo CD capability | `argocd` | 0.90 USD | 27.36 USD |
| Application managed by the capability | `team-a-nginx-argocd` | 0.044 USD | 1.35 USD |
| EC2 instance for the node | `c5a.large`\* | 2.30 USD | 70.08 USD |
| EKS Auto Mode management of the node | | 0.28 USD | 8.41 USD |
| Application Load Balancer | `k8s-teama-nginxgit-<hash>` | 0.58 USD | 17.74 USD |
| Capacity used by the load balancer | | 0.008 USD per LCU-hour | 0.008 USD per LCU-hour |
| Public IPv4 addresses of the load balancer, one per Availability Zone | | 0.24 USD | 7.30 USD |
| Data processed by the NAT gateway, such as the image pulled by the node | | 0.062 USD per GB | 0.062 USD per GB |

\* The type that the cluster picked as the cheapest that satisfies the
NodePool. It may pick another type of the same size.
