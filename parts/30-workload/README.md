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

## Creating the sample workload with a Kubernetes manifest

A [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
runs pods from a template and keeps the number of them that you ask for.
Each pod gets an IP address of the VPC, from the subnet of its node. A
[Service](https://kubernetes.io/docs/concepts/services-networking/service/)
gives a set of pods, selected by a label, one DNS name and one IP
address, the cluster IP, that stay the same while the pods come and go.
An Ingress, as above, maps the path of a request to a Service.

Together, the three are the sample workload. The cluster launches a node
for the pods, creates an ALB for the Ingress, and registers the IP
addresses of the pods as the targets of the ALB, so that a request from
the internet goes from the ALB straight to a pod.

The sample workload, `nginx`, is set as follows. The three resources
share the name, the namespace `default`, and the label
`app.kubernetes.io/name: nginx`, which later parts select on.

| Setting | Value |
| --- | --- |
| Image | [nginx](https://gallery.ecr.aws/nginx/nginx) from the Amazon ECR Public Gallery, the latest release of the stable line |
| Replicas | 2 |
| Resources of a pod | 100m of CPU and 128 MiB of memory, with the memory also as the limit |
| Targets of the ALB | The pods, by IP address |

Two pods with these resources fit on one node, so the node appears when
the pods are created and disappears when they are deleted. The targets
are the pods themselves because they have addresses of the VPC. The
image comes from the ECR Public Gallery, which has no pull limit.

To create the sample workload:

1. Ask the agent to write the manifest. Start a Claude Code session at the
   repository root and paste the following prompt.

   ```text
   /aws-containers

   # Summary
   Create a manifest for the Deployment, Service, and Ingress of a sample workload on an EKS Auto Mode cluster.

   ## Prerequisites
   - The IngressClass alb exists.

   ## Working environment
   - Create the manifest at parts/30-workload/manifests/nginx.yaml.

   ## Kubernetes resource settings

   ### Common
   - Use the namespace default.
   - Use the label app.kubernetes.io/name: nginx.

   ### Kubernetes resource list
   - Deployment: 1
   - Service: 1
   - Ingress: 1

   ### Deployment
   - Name it nginx.
   - Run 2 replicas.
   - Use the following container image.
     - Image: public.ecr.aws/nginx/nginx
     - Tag: the latest version of the stable line
   - Request the following resources.
     - CPU: 100m
     - Memory: 128Mi
   - Limit the memory only, to 128Mi.

   ### Service
   - Name it nginx.
   - Make it reachable only from inside the cluster.
   - Send to the pods of the Deployment nginx.
   - Receive on port 80 and send to port 80 of the pods.

   ### Ingress
   - Name it nginx.
   - Use the IngressClass alb.
   - Make the IP addresses of the pods the targets of the ALB.
   - Set no host, and send every request under the path / to port 80 of the Service nginx.

   ## Style
   - Keep the manifest, and especially the comments, to the minimum.
   ```

   The agent writes the manifest. Before you go on, read it against the
   prompt. In particular, check that the tag of the image is the latest
   stable release on the
   [gallery page](https://gallery.ecr.aws/nginx/nginx), that the
   selectors of the Deployment and the Service use the label of the
   prompt, and that nothing was added that the prompt did not ask for.
   The file [manifests/nginx.yaml](manifests/nginx.yaml) is the result of
   this step.

2. Apply the manifest. Ask the agent:

   ```text
   Apply parts/30-workload/manifests/nginx.yaml to the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl apply -f parts/30-workload/manifests/nginx.yaml
   ```

   From now on, the node and the ALB are charged (see [Cost](#cost)), so
   tear the workload down when you stop for the day.

   It takes about three minutes for the workload to answer. The pods are
   `Pending` at first, because no node has room for them. The cluster
   decides to launch one, which a NodeClaim records at once with the
   instance type it picked, and a minute or two later the node is `Ready`
   and the pods are `Running`.

   Meanwhile the cluster creates the ALB, which takes two to three
   minutes, and the Ingress shows the DNS name of the ALB as its address.
   To watch this happen, run:

   ```bash
   watch -n 2 kubectl get pods,nodeclaims,nodes,ingress -o wide
   ```

3. Check the workload from outside Kubernetes. The checks come in four
   groups, each covering related resources.

   **The pods and their node.** The Deployment has two pods `Running`, on
   one node of the NodePool `apps`. The pods have IP addresses of the
   private subnets.

   To check this, ask the agent:

   ```text
   Check the Deployment nginx of the cluster:

   - It has 2 pods, and both are running.
   - Both are on one node, and that node is of the NodePool apps.
   - The IP address of each pod is in a private subnet of the VPC.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get pods -l app.kubernetes.io/name=nginx -o wide

   kubectl get nodeclaims,nodes -l karpenter.sh/nodepool=apps -o wide
   ```

   **The Service.** The Service has an address of its own, outside the
   VPC, and its endpoints are the two pods. A request from inside the
   cluster reaches the pods through the name of the Service.

   To check this, ask the agent:

   ```text
   Check the Service nginx of the cluster:

   - It has a cluster IP, and that address is not in the VPC.
   - Its endpoints are the IP addresses of the two pods.
   - A request to http://nginx from a temporary pod in the cluster is answered by nginx with 200.
   ```

   Or run the commands yourself:

   ```bash
   kubectl get service nginx

   kubectl get endpointslices -l kubernetes.io/service-name=nginx

   kubectl run check --rm -it --restart=Never --image=public.ecr.aws/docker/library/busybox:1.37 -- \
     wget -S --spider http://nginx
   ```

   **The ALB.** The Ingress has the DNS name of the ALB as its address.
   The ALB faces the internet, and its targets are the two pods, by IP
   address, both healthy.

   To check this, ask the agent:

   ```text
   Check the Ingress nginx of the cluster and its ALB, with the profile <account-name>-admin:

   - The Ingress has the DNS name of the ALB as its address.
   - The ALB faces the internet.
   - Its targets are the two pods, by IP address, and both are healthy.
   ```

   Or run the commands yourself. The second takes the ARN of the ALB from
   its tag for the others:

   ```bash
   kubectl get ingress nginx

   alb_arn=$( \
   aws --profile <account-name>-admin \
     resourcegroupstaggingapi get-resources \
     --tag-filters Key=eks:eks-cluster-name,Values=eks-platform-lab \
     --resource-type-filters elasticloadbalancing:loadbalancer \
     --query 'ResourceTagMappingList[0].ResourceARN' \
     --output text \
   )

   aws --profile <account-name>-admin \
     elbv2 describe-load-balancers --load-balancer-arns $alb_arn \
     --query 'LoadBalancers[].[DNSName, Scheme]' \
     --output table

   target_group_arn=$( \
   aws --profile <account-name>-admin \
     elbv2 describe-target-groups --load-balancer-arn $alb_arn \
     --query 'TargetGroups[0].TargetGroupArn' \
     --output text \
   )

   aws --profile <account-name>-admin \
     elbv2 describe-target-health --target-group-arn $target_group_arn \
     --query 'TargetHealthDescriptions[].[Target.Id, TargetHealth.State]' \
     --output table
   ```

   **The response.** A request from the internet to the DNS name of the
   ALB gets the welcome page of nginx, and the access log of nginx shows
   the health checks of the ALB.

   To check this, ask the agent:

   ```text
   Check that http://<alb-dns-name>/ answers with the nginx welcome page,
   and show me a few lines of the log of the Deployment nginx.
   ```

   Or run the commands yourself, and open the same URL in a browser. Type
   `http://` in the browser: the ALB has no HTTPS listener.

   ```bash
   curl http://<alb-dns-name>/

   kubectl logs deployment/nginx --tail=5
   ```

   The log shows a `GET /` from `ELB-HealthChecker/2.0` every fifteen
   seconds, from an address in a public subnet: the ALB itself.

## Teardown

This part is torn down every night and built again the next day, because
the node and the ALB are charged by the hour. Tear it down before the
cluster, in the reverse order of the steps: the sample workload first,
so that the cluster removes the ALB and lets the node go, then the
IngressClass and the NodePool.

To tear down the workload:

1. Delete the sample workload. Ask the agent:

   ```text
   Delete parts/30-workload/manifests/nginx.yaml from the cluster.
   ```

   Or run the command yourself:

   ```bash
   kubectl delete -f parts/30-workload/manifests/nginx.yaml
   ```

   The command takes a little while to return, because the Ingress is
   not gone until the cluster has deleted the ALB, its target group, and
   its security groups. The pods go at once, and the node about a minute
   later, once the cluster sees it empty.

2. Delete the IngressClass and the NodePool. Ask the agent:

   ```text
   Delete parts/30-workload/manifests/ingressclass.yaml and
   parts/30-workload/manifests/nodepool.yaml from the cluster.
   ```

   Or run the commands yourself:

   ```bash
   kubectl delete -f parts/30-workload/manifests/ingressclass.yaml

   kubectl delete -f parts/30-workload/manifests/nodepool.yaml
   ```

   Deleting the NodePool terminates its node if it is still there.

3. Confirm that nothing of this part is left and nothing is charged: no
   load balancer, target group, or security group of the cluster exists,
   and the NodePool `apps` has no node.

   To check this, ask the agent:

   ```text
   Check with the profile <account-name>-admin
   that no load balancer, target group, or security group
   tagged eks:eks-cluster-name = eks-platform-lab exists,
   and that the cluster has no node of the NodePool apps.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     resourcegroupstaggingapi get-resources \
     --tag-filters Key=eks:eks-cluster-name,Values=eks-platform-lab \
     --resource-type-filters \
       elasticloadbalancing:loadbalancer \
       elasticloadbalancing:targetgroup \
       ec2:security-group \
     --query 'ResourceTagMappingList[].ResourceARN' \
     --output table

   kubectl get nodeclaims,nodes -l karpenter.sh/nodepool=apps
   ```

   The first command prints nothing, and the second finds no resources.

> [!NOTE]
> Delete the Ingress before the cluster. The cluster deletes the ALB
> when it goes, but it may leave a security group behind, and that
> security group blocks the teardown of the VPC. If that happens, find
> the leftovers by the tag `eks:eks-cluster-name` and delete them with
> the AWS CLI.

## Cost

This part is charged for the following resources while the sample
workload runs.

| Resource | Name | Per day | Per month |
| --- | --- | --- | --- |
| EC2 instance for the node | `c5a.large`\* | 2.30 USD | 70.08 USD |
| EKS Auto Mode management of the node | | 0.28 USD | 8.41 USD |
| Application Load Balancer | `k8s-default-nginx-<hash>` | 0.58 USD | 17.74 USD |
| Capacity used by the load balancer | | 0.008 USD per LCU-hour | 0.008 USD per LCU-hour |
| Public IPv4 addresses of the load balancer, one per Availability Zone | | 0.24 USD | 7.30 USD |
| Data processed by the NAT gateway, such as the image pulled by the node | | 0.062 USD per GB | 0.062 USD per GB |

\* The type that the cluster picked as the cheapest that satisfies the
NodePool. It may pick another type of the same size.
