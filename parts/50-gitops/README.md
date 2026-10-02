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

## Creating the Argo CD capability with Terraform

[Argo CD](https://argo-cd.readthedocs.io/) keeps the resources in a cluster
in sync with the manifests in a Git repository. EKS runs it as the
[Argo CD capability](https://docs.aws.amazon.com/eks/latest/userguide/argocd.html),
outside the nodes of the cluster. An Argo CD capability comes with three things:

- An IAM role that the capability assumes. The role needs permissions only
  when Argo CD reads the sources of the manifests from AWS services.
- Sign-in through IAM Identity Center. Its users and groups are mapped to
  the roles of Argo CD.
- Access to the cluster. EKS creates an access entry for the IAM role, but
  the entry does not let Argo CD apply manifests until an access policy is
  associated with it.

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
   - Create the Terraform configuration in parts/50-gitops/terraform.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 50-gitops
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - IAM role: 1
   - EKS capability: 1
   - EKS access policy association: 1

   ### IAM role
   - Name it eks-platform-lab-argocd.
   - Make it a role that the Argo CD capability of EKS assumes.
   - Attach no permissions policy. Argo CD reads public repositories only.

   ### EKS capability
   - Make it an Argo CD capability.
   - Name it argocd.
   - Put the resources of Argo CD in the namespace argocd.
   - Authenticate with IAM Identity Center.
   - Map the IAM Identity Center group eks-platform-lab-admins to the Argo CD role ADMIN.
   - Create it after the IAM role has propagated, so that EKS accepts the trust policy of the role.

   ### EKS access policy association
   - Associate the access policy AmazonEKSClusterAdminPolicy, scoped to the whole cluster,
     with the access entry that the EKS capability creates.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Use the S3 backend.
   - Use parts/50-gitops/terraform.tfstate as the state key.
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
   AWS provider, that the instance of IAM Identity Center and the group
   are found by name, with no IDs in the configuration, and that the
   `backend "s3"` block has no `bucket` line. The files in
   [terraform/](terraform/) are the result of this step.

2. Plan and apply. Make sure that the AWS CLI is signed in to the profile
   `<account-name>-admin`, then ask the agent:

   ```text
   /terraform-skill
   Initialize parts/50-gitops/terraform with the profile <account-name>-admin.
   Take the bucket name from the output bucket_name of parts/05-terraform-state/terraform,
   and pass it as -backend-config.
   Then show me the plan, and apply it after I approve.
   ```

   The plan adds 4 resources: the IAM role, a wait for the role to
   propagate, the capability, and the access policy association. The
   capability takes several minutes to become active.

   Or run the commands yourself:

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-gitops/terraform \
     init -backend-config="bucket=${bucket_name}"

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-gitops/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/50-gitops/terraform \
     apply terraform.tfplan
   ```

3. Check the capability. The capability is active, the cluster has the
   namespace `argocd`, and the access entry of the IAM role has the access
   policy `AmazonEKSClusterAdminPolicy`.

   To check this, ask the agent:

   ```text
   Check the Argo CD capability argocd of the cluster eks-platform-lab, with the profile <account-name>-admin:

   - The capability is active, and shows the URL of its UI.
   - The cluster has the namespace argocd.
   - The access entry of the IAM role eks-platform-lab-argocd has the access policy AmazonEKSClusterAdminPolicy.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     eks describe-capability --cluster-name eks-platform-lab --capability-name argocd \
     --query 'capability.[status, configuration.argoCd.serverUrl]' \
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

   The first command prints `ACTIVE` and the URL of the UI. The last
   lists `AmazonEKSClusterAdminPolicy`, and two more that EKS associated
   with the access entry when it created the capability.

4. Sign in to the UI of Argo CD. Open the URL that the first command
   printed, and sign in as the administrator through the AWS access portal.
   The UI shows no applications yet.

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
   - Create the manifest at parts/50-gitops/manifests/cluster.yaml.

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
   Apply parts/50-gitops/manifests/cluster.yaml to the cluster,
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

   sed "s|<cluster-arn>|${cluster_arn}|" parts/50-gitops/manifests/cluster.yaml | kubectl apply -f -
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
