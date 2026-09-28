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

## Reviewing the workload design

The workload is the first thing to run on the cluster. It takes three
kinds of Kubernetes resources, and each of them is a manifest of its own
in the steps that follow:

- A NodePool, which the cluster launches nodes from.
- An IngressClass, with its IngressClassParams, which the cluster creates a
  load balancer from.
- The Deployment, the Service, and the Ingress of the sample workload.

The NodePool and the IngressClass are cluster-wide resources that the
platform owns, and they outlive any one workload. The Deployment, the
Service, and the Ingress live in a namespace and belong to the workload.

Before you ask the agent to write the manifests, review the three designs
together with the
[`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
command.

To review the workload design, start a Claude Code session at the
repository root and paste the following review request. Fill its "Design"
section with the "Kubernetes resource settings" sections of the prompts of
steps 2, 3, and 4, in that order.

````text
/apex:eks-design

# Review request
I am running the first workload on an EKS Auto Mode cluster.
The design below consists of the following.
- A NodePool for workloads
- An IngressClass and IngressClassParams for routing
- The Deployment, Service, and Ingress of a sample workload
Review the design with the context in mind.

## Context
- This is a personal lab. It is torn down every night to keep the cost down.
- The VPC and the EKS Auto Mode cluster already exist.
  - The subnets of the VPC have the following tags.
    - public: kubernetes.io/role/elb = 1
    - private: kubernetes.io/role/internal-elb = 1
  - Among the built-in NodePools, only system is enabled.
- The following concerns are out of scope here.
  - Tenant isolation
  - Scaling and availability
  - Pod health checks
  - Pod security
  - A custom domain and HTTPS

## Design
```
(the "Kubernetes resource settings" sections of the prompts of steps 2, 3, and 4)
```
````

The command answers with a table of findings ranked by severity and the
details of each finding. Fix the design according to the findings, and
review it again until nothing new comes up. The prompts of steps 2 to 4
are the result of a few rounds.

## Creating the NodePool with a Kubernetes manifest

A [NodePool](https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html)
tells the cluster what nodes it may launch. With EKS Auto Mode, the
cluster launches a node when a pod is waiting to be scheduled and no node
has room for it, picks the cheapest instance type that satisfies both the
NodePool and the pod, and terminates the node once it is empty or
underused.

Auto Mode has two built-in NodePools. `system` is reserved for the
components of the cluster. `general-purpose` would run any pod, but with
no cap on what it launches, so the cluster leaves it disabled and the
workload gets a NodePool of its own.

This NodePool, `apps`, is set as follows.

| Setting | Value |
| --- | --- |
| Instance types | `c` and `m` categories, fifth generation or later, 2 vCPUs, amd64, on-demand |
| Total capacity of its nodes | 8 vCPUs and 32 GiB at most |
| Consolidation | Nodes that have been empty or underutilized for one minute |

A node with 2 vCPUs is the smallest that qualifies. Three or more nodes
are wanted, to keep redundancy and to watch the cluster scale out, and
the cap of 8 vCPUs allows four.

To create the NodePool:

1. Install the skill that the agent uses to write the manifests, at user
   scope.

   The [`aws-containers`](https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/core-skills/aws-containers/SKILL.md)
   skill, from the Agent Toolkit for AWS, covers containers on AWS: EKS,
   including Auto Mode and its NodePools and load balancers, ECS, and ECR.
   Install it with the AWS CLI:

   ```bash
   aws agent-toolkit add-skill --skill-name aws-containers --region us-east-1
   ```

2. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for a NodePool for workloads on an EKS Auto Mode cluster.

   ## Prerequisites
   - None.

   ## Working environment
   - Create the manifest at parts/30-workload/manifests/nodepool.yaml.

   ## Kubernetes resource settings

   ### Kubernetes resource list
   - NodePool: 1

   ### NodePool
   - Name it apps.
   - Reference the default NodeClass, default.
   - Require the following of the nodes.
     - Instance category: c or m
     - Instance generation: 5 or later
     - Number of vCPUs: 2
     - Architecture: amd64
     - Capacity type: on-demand
   - Cap the total CPU and memory of the nodes of this NodePool as follows.
     - CPU: 8
     - Memory: 32Gi
   - Consolidate as follows.
     - Candidates: empty nodes and underutilized nodes
     - Wait before a node becomes a candidate: 1 minute

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the requirement keys are those of EKS
   Auto Mode, not those of upstream Karpenter, and that nothing was added
   that the prompt did not ask for. The file
   [manifests/nodepool.yaml](manifests/nodepool.yaml) is the result of this
   step.

3. Apply the manifest. Make sure that
   [the cluster](../20-eks-cluster/README.md#creating-the-cluster-with-terraform)
   is up and that kubectl is set up for it again, with
   `aws eks update-kubeconfig`, then ask the agent:

   ```text
   Apply parts/30-workload/manifests/nodepool.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/30-workload/manifests/nodepool.yaml
   ```

   Nothing is launched yet. The cluster launches nodes only for pods that
   are waiting to be scheduled, and there are no pods yet.

4. Check the NodePool. It exists and is ready, its settings are those of
   the manifest, and it has no node yet.

   To check this, ask the agent:

   ```text
   Check the NodePool apps of the cluster:

   - It exists and is ready.
   - It requires instances of the categories c and m, of generation 5 or later,
     with 2 vCPUs, on amd64, and on-demand.
   - It caps its nodes at 8 CPUs and 32Gi in total.
   - It consolidates empty and underutilized nodes after 1 minute.
   - It has no node.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get nodepool apps

   kubectl get nodepool apps -o yaml

   kubectl get nodeclaims,nodes -l karpenter.sh/nodepool=apps
   ```

   The first command lists the NodePool with `READY` at `True` and `NODES`
   at 0. The second prints the NodePool as the cluster holds it: the
   manifest, the defaults that the cluster filled in, such as an
   `expireAfter` of 336 hours, and its `status`. The third finds no
   resources.

## Creating the IngressClass with a Kubernetes manifest

An [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
exposes a workload to HTTP requests from outside the cluster, with rules
that map the path of a request to a backend in the cluster. An Ingress
does nothing by itself: an ingress controller watches the Ingresses and
sets up a load balancer or a proxy that carries the requests to the
backend.

An [IngressClass](https://kubernetes.io/docs/concepts/services-networking/ingress/#ingress-class)
names that controller, and an Ingress refers to the IngressClass by name.
An IngressClass can also refer to an IngressClassParams, which holds
settings for the controller, such as whether the load balancer faces the
internet, and those settings apply to every Ingress of the class.

This IngressClass, `alb`, and its IngressClassParams, also `alb`, are set
as follows.

| Setting | Value |
| --- | --- |
| Controller | The ingress controller of EKS Auto Mode, which creates an [Application Load Balancer](https://docs.aws.amazon.com/eks/latest/userguide/auto-configure-alb.html) (ALB) |
| Default IngressClass of the cluster | No |
| Where the ALB faces | The internet |

The IngressClass is not the default, so that an Ingress gets an ALB only
when it names the class. The subnets are not set: the cluster finds the
public subnets by the tag `kubernetes.io/role/elb`, which the subnets of
the VPC carry.

To create the IngressClass:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for an IngressClass and IngressClassParams for routing on an EKS Auto Mode cluster.

   ## Prerequisites
   - The cluster is EKS Auto Mode.
   - The public subnets of the VPC have the tag kubernetes.io/role/elb = 1.

   ## Working environment
   - Create the manifest at parts/30-workload/manifests/ingressclass.yaml.

   ## Kubernetes resource settings

   ### Kubernetes resource list
   - IngressClass: 1
   - IngressClassParams: 1

   ### IngressClass
   - Name it alb.
   - Use the controller that creates ALBs.
   - Reference the IngressClassParams alb as its parameters.
   - Do not make it the default IngressClass of the cluster.

   ### IngressClassParams
   - Name it alb.
   - Make the ALBs created with these parameters reachable from the internet.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the IngressClassParams is of the API
   group of EKS Auto Mode, not of the upstream AWS Load Balancer
   Controller, and that nothing was added that the prompt did not ask
   for. The file [manifests/ingressclass.yaml](manifests/ingressclass.yaml)
   is the result of this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/30-workload/manifests/ingressclass.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/30-workload/manifests/ingressclass.yaml
   ```

   Nothing is created in AWS yet. The cluster creates a load balancer only
   for an Ingress that names this class, and there is no Ingress yet.

3. Check the IngressClass. It and its IngressClassParams exist, their
   settings are those of the manifest, and no load balancer of the cluster
   exists yet.

   To check this, ask the agent:

   ```text
   Check the IngressClass alb and the IngressClassParams alb of the cluster:

   - Both exist.
   - The controller of the IngressClass is the one of EKS Auto Mode that creates ALBs.
   - The ALBs it creates face the internet.
   - The IngressClass is not the default of the cluster.

   Then check with the profile <account-name>-admin that no load balancer
   tagged eks:eks-cluster-name = eks-platform-lab exists.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get ingressclass/alb ingressclassparams/alb

   kubectl get ingressclass alb -o yaml

   aws --profile <account-name>-admin \
     resourcegroupstaggingapi get-resources \
     --tag-filters Key=eks:eks-cluster-name,Values=eks-platform-lab \
     --resource-type-filters elasticloadbalancing:loadbalancer \
     --query 'ResourceTagMappingList[].ResourceARN' \
     --output table
   ```

   The first command lists the two resources, with the controller of the
   IngressClass and the scheme of the IngressClassParams. The second
   prints the IngressClass without the annotation
   `ingressclass.kubernetes.io/is-default-class`. The third prints
   nothing: the cluster tags every load balancer it creates with its name,
   and there is none.
