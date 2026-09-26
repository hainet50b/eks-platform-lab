# 20 eks-cluster

An EKS Auto Mode cluster.

## Overview

```
┌─ 20 eks-cluster ──────────────────────────────────────────────┐
│                                                               │
│  you ──────▶ coding agent                                     │
│   │            │                                              │
│   │            │  ┌─ agent skills ─────────────────────────┐  │
│   │            ├─▶│  /apex:eks-design (APEX Skills)        │  │
│   │            │  │  terraform-skill (APEX Skills)         │  │
│   │            │  │  terraform-style-guide (HashiCorp)     │  │
│   │            │  └────────────────────────────────────────┘  │
│   │            │ reviews, writes, and runs                    │
│   ▼            ▼                                              │
│  ┌─ 1. Creating the cluster with Terraform ────────────────┐  │
│  │                                                         │  │
│  │  ┌─ Terraform ──────────────────────────────────────┐   │  │
│  │  │  configuration   terraform/*.tf                  │   │  │
│  │  │  state           S3 bucket created in part 05    │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                           │ creates                     │  │
│  │                           ▼                             │  │
│  │  ┌─ EKS Auto Mode cluster ──────────────────────────┐   │  │
│  │  │                                                  │   │  │
│  │  │  control plane (run by AWS)                      │   │  │
│  │  │                                                  │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                           │ places                      │  │
│  └───────────────────────────┼─────────────────────────────┘  │
│  ┌─ VPC (part 10) ───────────┼─────────────────────────────┐  │
│  │  ┌─ private subnets ──────┼──────────────────────────┐  │  │
│  │  │                        ▼                          │  │  │
│  │  │         ┌─ 1. ────────────────────────┐           │  │  │
│  │  │         │  control plane ENIs         │           │  │  │
│  │  │         └─────────────────────────────┘           │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Creating the cluster with Terraform](#creating-the-cluster-with-terraform) | Builds the cluster, with its IAM roles, access entry, and log group, from a Terraform configuration |

## Creating the cluster with Terraform

An [Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
cluster is a Kubernetes cluster. AWS runs the **control plane**. The **nodes**
run in your VPC. With
[EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html),
AWS also launches and replaces the nodes, and runs the cluster components on
them: networking, DNS, storage, load balancing, and pod identity.

This part creates the cluster, an IAM role for the cluster, an IAM role for its
nodes, an access entry for your IAM role, the one that runs Terraform, and a
log group for the control plane logs. The configuration reads the VPC ID and
the subnet IDs from the Terraform state of the VPC.

To create the cluster:

1. Before you ask the agent to write the configuration, review the cluster
   design with the
   [`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
   command.

   To review the cluster design, start a Claude Code session at the repository
   root and paste the following review request. Fill its "Design" section with
   the "AWS resource settings" section of the step 2 prompt.

   ````text
   /apex:eks-design

   # Review request
   I am building an EKS cluster.
   The design below is for its control plane and nodes.
   Review the design with the context in mind.

   ## Context
   - This is a personal lab. It is torn down every night to keep the cost down.
   - The VPC that hosts the EKS cluster already exists.
   - The following are created later, separately.
     - Add-ons
     - EKS Pod Identity
     - NodePools

   ## Design
   ```
   (the "AWS resource settings" section of the step 2 prompt)
   ```
   ````

   The command answers with a table of findings ranked by severity and the
   details of each finding. Fix the cluster design according to the findings,
   and review it again until nothing new comes up. The prompt of step 2 is the
   result of a few rounds.

2. Ask the agent to write the configuration. Start a Claude Code session at
   the repository root and paste the following prompt.

   ```text
   /terraform-skill
   /terraform-style-guide

   # Summary
   Create a Terraform configuration for an EKS Auto Mode cluster.

   ## Prerequisites
   - AWS credentials are passed at run time through AWS_PROFILE.
   - The VPC and its subnets already exist.
     - Their state is in the following S3 location.
       - Bucket: eks-platform-lab-terraform-state-<account ID>
       - Key: parts/10-vpc/terraform.tfstate
     - The state has the following outputs.
       - vpc_id: the VPC ID
       - private_subnet_ids: the list of private subnet IDs

   ## Working environment
   - Create the Terraform configuration in parts/20-eks-cluster/terraform.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 20-eks-cluster
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - EKS cluster: 1
   - IAM roles: 2
   - EKS access entry: 1
   - CloudWatch Logs log group: 1

   ### EKS cluster
   - Name it eks-platform-lab.
   - Use the latest Kubernetes version in standard support on EKS at the time of creation.
   - Set the support type of the upgrade policy to STANDARD.
   - Use eks-platform-lab-cluster as the cluster IAM role.
   - Enable all three of the following EKS Auto Mode capabilities.
     - Compute
     - Block storage
     - Load balancing
   - Do not install self-managed add-ons when creating the cluster.
   - Use eks-platform-lab-node as the node IAM role.
   - Enable only system among the built-in NodePools.
   - Specify only the two private subnets of the VPC as the cluster subnets.
   - Enable both of the following API server endpoints.
     - Public
     - Private
   - Use access entries as the only authentication mode.
   - Do not grant the IAM principal that creates the cluster an administrator access entry automatically.
   - Enable all five of the following control plane log types.
     - api
     - audit
     - authenticator
     - controllerManager
     - scheduler

   ### IAM roles
   - eks-platform-lab-cluster
     - In the trust policy, allow EKS (eks.amazonaws.com) the following actions.
       - sts:AssumeRole
       - sts:TagSession
     - Attach the following AWS managed policies.
       - AmazonEKSClusterPolicy
       - AmazonEKSComputePolicy
       - AmazonEKSBlockStoragePolicyV2
       - AmazonEKSLoadBalancingPolicy
       - AmazonEKSNetworkingPolicy
   - eks-platform-lab-node
     - In the trust policy, allow EC2 (ec2.amazonaws.com) the following action.
       - sts:AssumeRole
     - Attach the following AWS managed policies.
       - AmazonEKSWorkerNodeMinimalPolicy
       - AmazonEC2ContainerRegistryPullOnly

   ### EKS access entry
   - Create it for the IAM role that runs Terraform.
   - Associate the access policy AmazonEKSClusterAdminPolicy with the whole cluster.

   ### CloudWatch Logs log group
   - Name it /aws/eks/eks-platform-lab/cluster.
   - Retain logs for 1 day.
   - Create it before the EKS cluster so that EKS does not create the log group itself.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Use the S3 backend.
   - Use parts/20-eks-cluster/terraform.tfstate as the state key.
   - Lock with S3 native locking.
   - Do not include the bucket name in the backend configuration;
     pass it with -backend-config on terraform init.

   ### Output
   - Output the cluster name as cluster_name.
   - Output the ID of the cluster security group that EKS created as cluster_security_group_id.

   ### Style
   - Place each data source right before the resource that references it.
   - Name each data source label after its content.
   - Do not add unnecessary depends_on.
   - Keep the configuration, and especially the comments, to the minimum.
   ```

   The agent writes the configuration files and a `.gitignore` under
   [terraform/](terraform/), then runs `terraform init -backend=false`,
   `fmt`, and `validate`.

   Before you go on, read the result against the prompt. In particular, check
   that no profile name and no account ID appear anywhere, and that the
   `backend "s3"` block has no `bucket` line. Above all, check that the
   cluster has `depends_on` for every policy attachment of the two IAM roles.
   Without it, the cluster may be created before its roles have their
   policies, and on destroy the policies may be detached before the cluster
   is deleted, leaving behind the resources that Auto Mode created. Ask the
   agent to fix what differs. The files in [terraform/](terraform/) are the
   result of this step.

3. Plan and apply. Make sure that
   [the VPC](../10-vpc/README.md#creating-the-network-with-terraform) is up
   and that the AWS CLI is signed in to the profile `<account-name>-admin`,
   then ask the agent:

   ```text
   /terraform-skill
   Initialize parts/20-eks-cluster/terraform with the profile <account-name>-admin.
   Take the bucket name from the output bucket_name of parts/05-terraform-state/terraform,
   and pass it as -backend-config.
   Then show me the plan, and apply it after I approve.
   ```

   The plan adds 13 resources: the log group, the two IAM roles with their
   seven policy attachments, the cluster, and the access entry with its
   policy association. The cluster takes about ten minutes to create. From
   now on the cluster costs about 2.4 USD a day (see [Cost](#cost)), so tear
   it down when you stop for the day.

   Or run the commands yourself:

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/20-eks-cluster/terraform \
     init -backend-config="bucket=${bucket_name}"

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/20-eks-cluster/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/20-eks-cluster/terraform \
     apply terraform.tfplan
   ```

4. Set up kubectl. [Install kubectl](https://kubernetes.io/docs/tasks/tools/),
   the command-line tool of Kubernetes, then write the cluster into its
   configuration file with the AWS CLI:

   ```bash
   aws --profile <account-name>-admin \
     eks update-kubeconfig --name eks-platform-lab --region ap-northeast-1
   ```

   The command writes the cluster, and how to get credentials for it, into
   `~/.kube/config`, the configuration file of kubectl. The credentials
   come from `aws eks get-token`, so kubectl authenticates with your IAM
   role, and the access entry gives that role its permissions in the
   cluster. Run the command again after every rebuild, because a new cluster
   has a new endpoint and a new certificate.

   Then check the connection:

   ```bash
   kubectl version
   ```

   With the configuration in place, the command prints the version of the
   server next to the version of the client.

5. Check the cluster from outside Terraform. The checks come in four
   groups, each covering related resources.

   **The cluster.** The cluster is `ACTIVE` and configured as designed. Its
   subnets are the two private subnets, and each holds a network interface
   of the control plane.

   To check this, ask the agent:

   ```text
   Show me the cluster eks-platform-lab with the profile <account-name>-admin.

   Its settings:
   - the status, the Kubernetes version, the upgrade policy, and the authentication mode
   - whether each Auto Mode capability is enabled, and which built-in NodePools are enabled
   - whether each endpoint is enabled
   - which log types are enabled

   Its subnets:
   - a table with the Name, the ID, and the Availability Zone
   - the network interfaces of the control plane, with the status and the subnet ID of each
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     eks describe-cluster --name eks-platform-lab \
     --query 'cluster.{
       Status: status,
       Version: version,
       UpgradePolicy: upgradePolicy.supportType,
       AuthenticationMode: accessConfig.authenticationMode,
       Compute: computeConfig.enabled,
       NodePools: join(`, `, computeConfig.nodePools),
       BlockStorage: storageConfig.blockStorage.enabled,
       LoadBalancing: kubernetesNetworkConfig.elasticLoadBalancing.enabled,
       PublicEndpoint: resourcesVpcConfig.endpointPublicAccess,
       PrivateEndpoint: resourcesVpcConfig.endpointPrivateAccess,
       LogTypes: join(`, `, logging.clusterLogging[?enabled].types[])
     }' \
     --output table

   subnet_ids=$( \
   aws --profile <account-name>-admin \
     eks describe-cluster --name eks-platform-lab \
     --query 'cluster.resourcesVpcConfig.subnetIds' \
     --output text \
   )

   aws --profile <account-name>-admin \
     ec2 describe-subnets --subnet-ids $subnet_ids \
     --query 'Subnets[].[Tags[?Key==`Name`].Value|[0], SubnetId, AvailabilityZone]' \
     --output table

   aws --profile <account-name>-admin \
     ec2 describe-network-interfaces \
     --filters Name=description,Values="Amazon EKS eks-platform-lab" \
     --query 'NetworkInterfaces[].[Status, SubnetId, PrivateIpAddress]' \
     --output table
   ```

   **Access.** Your IAM role has an access entry with the access policy
   `AmazonEKSClusterAdminPolicy` at the cluster scope. That entry is what
   lets kubectl in. The cluster has two more entries, which EKS added
   itself: the node role and the service-linked role of EKS.

   To check this, ask the agent:

   ```text
   Check the access entries of the cluster eks-platform-lab with the profile <account-name>-admin:

   - My IAM role has an access entry.
   - Its access policy is AmazonEKSClusterAdminPolicy at the cluster scope.
   ```

   Or run the commands yourself. The first lists the entries; take the ARN
   of your IAM role from it for the second:

   ```bash
   aws --profile <account-name>-admin \
     eks list-access-entries --cluster-name eks-platform-lab \
     --output table

   aws --profile <account-name>-admin \
     eks list-associated-access-policies --cluster-name eks-platform-lab \
     --principal-arn <your-role-arn> \
     --query 'associatedAccessPolicies[].[policyArn, accessScope.type]' \
     --output table
   ```

   **Logs.** The log group `/aws/eks/eks-platform-lab/cluster` is configured
   as designed, and the control plane already writes to it: it has a log
   stream for each component of the control plane.

   To check this, ask the agent:

   ```text
   Show me the log group /aws/eks/eks-platform-lab/cluster with the profile <account-name>-admin:
   its retention in days, and the names of its log streams.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     logs describe-log-groups --log-group-name-prefix /aws/eks/eks-platform-lab/cluster \
     --query 'logGroups[].[logGroupName, retentionInDays]' \
     --output table

   aws --profile <account-name>-admin \
     logs describe-log-streams --log-group-name /aws/eks/eks-platform-lab/cluster \
     --query 'logStreams[].logStreamName' \
     --output table
   ```

   **Inside the cluster.** The cluster has one NodePool, the built-in
   `system`, and no nodes: Auto Mode launches a node only for pods that are
   waiting to be scheduled, and nothing runs yet. It has no pods either. A
   cluster usually runs its own components, such as DNS, as pods in the
   `kube-system` namespace; with Auto Mode, those components are built in,
   so `kube-system` is empty.

   To check this, ask the agent:

   ```text
   Show me the NodePools, the nodes, and the pods in all namespaces of the cluster.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get nodepools

   kubectl get nodes

   kubectl get pods --all-namespaces
   ```

## Teardown

This part is torn down every night and built again the next day, because
the cluster is charged by the hour. Tear it down before the VPC, whose
subnets hold the network interfaces of the control plane. To build it
again, run step 3 of
[Creating the cluster with Terraform](#creating-the-cluster-with-terraform)
and write the kubeconfig again.

To tear down the cluster:

1. Plan and destroy. Ask the agent:

   ```text
   /terraform-skill
   Destroy parts/20-eks-cluster/terraform with the profile <account-name>-admin.
   Show me the plan first, and destroy after I approve.
   ```

   The cluster takes a few minutes to delete.

   Or run the commands yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/20-eks-cluster/terraform \
     plan -destroy -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/20-eks-cluster/terraform \
     apply terraform.tfplan
   ```

2. Confirm that nothing of this part is left and nothing is charged: the
   state has no resources, and neither the cluster nor its log group
   exists.

   To check this, ask the agent:

   ```text
   Show me with the profile <account-name>-admin:
   the resources in the state of parts/20-eks-cluster/terraform,
   the EKS clusters,
   and the log group /aws/eks/eks-platform-lab/cluster.
   ```

   Or run the commands yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/20-eks-cluster/terraform \
     state list

   aws --profile <account-name>-admin \
     eks list-clusters \
     --output table

   aws --profile <account-name>-admin \
     logs describe-log-groups --log-group-name-prefix /aws/eks/eks-platform-lab/cluster \
     --query 'logGroups[].logGroupName' \
     --output table
   ```

## Cost

This part is charged for the following resources.

| Resource | Name | Per day | Per month |
| --- | --- | --- | --- |
| EKS cluster | `eks-platform-lab` | 2.40 USD | 73.00 USD |
| Control plane logs | `/aws/eks/eks-platform-lab/cluster` | 1.30 USD\* | 39.50 USD\* |
| Control plane logs ingested by CloudWatch Logs | | 0.76 USD per GB | 0.76 USD per GB |
| Control plane logs stored by CloudWatch Logs | | 0.033 USD per GB-month | 0.033 USD per GB-month |

\* Measured on an idle cluster, which writes about 1.7 GB of logs a day,
almost all of them (over 99 %) audit logs.
