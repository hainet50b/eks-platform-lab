# 10 vpc

A VPC with public, private, and data subnets in two Availability Zones.

## Overview

```
┌─ 10 vpc ───────────────────────────────────────────────────────────────────┐
│                                                                            │
│  you ──────▶ coding agent                                                  │
│   │            │                                                           │
│   │            │  ┌─ agent skills ─────────────────────────┐               │
│   │            ├─▶│  /apex:eks-design (APEX Skills)        │               │
│   │            │  │  terraform-skill (APEX Skills)         │               │
│   │            │  │  terraform-style-guide (HashiCorp)     │               │
│   │            │  └────────────────────────────────────────┘               │
│   │            │ reviews, writes, and runs                                 │
│   ▼            ▼                                                           │
│  ┌─ 1. Creating the network with Terraform ───────────────────────────┐    │
│  │                                                                    │    │
│  │   ┌─ Terraform ──────────────────────────────────────────────────┐ │    │
│  │   │  configuration   terraform/*.tf                              │ │    │
│  │   │  state           S3 bucket created in part 05                │ │    │
│  │   └──────────────────────────────────────────────────────────────┘ │    │
│  │                             │ creates                              │    │
│  │                             ▼                                      │    │
│  │   ┌─ VPC 10.0.0.0/16 ────────────────────────────────────────────┐ │    │
│  │   │                                                              │ │    │
│  │   │            ap-northeast-1a      ap-northeast-1c   routes     │ │    │
│  │   │                                                              │ │    │
│  │   │  public    10.0.0.0/24          10.0.1.0/24       → local    │ │    │
│  │   │                                                   → IGW      │ │    │
│  │   │            NAT gateway + EIP                                 │ │    │
│  │   │                                                              │ │    │
│  │   │  private   10.0.16.0/20         10.0.32.0/20      → local    │ │    │
│  │   │                                                   → NAT      │ │    │
│  │   │                                                   → S3       │ │    │
│  │   │                                                     endpoint │ │    │
│  │   │                                                              │ │    │
│  │   │  data      10.0.2.0/24          10.0.3.0/24       → local    │ │    │
│  │   │                                                              │ │    │
│  │   └──────────────┬─────────────────────────────────┬─────────────┘ │    │
│  │                  │ internet gateway                │ gateway       │    │
│  │                  ▼                                 ▼ endpoint      │    │
│  │              Internet                          Amazon S3           │    │
│  │                                                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Steps

| Step | Does |
| --- | --- |
| [1. Creating the network with Terraform](#creating-the-network-with-terraform) | Builds the VPC, its subnets, and its routes from a Terraform configuration |

## VPC design

An [Amazon VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
is a virtual network of your own inside your AWS account. It is divided
into **subnets**, each in one Availability Zone, and the **route table**
associated with a subnet decides where its traffic can go.

This part creates a VPC with three tiers of subnets.

| Tier | Reaches the internet | Reached from the internet | Holds |
| --- | --- | --- | --- |
| public | ✅ Through the internet gateway | ✅ Yes | The NAT gateway, and later the load balancer |
| private | ✅ Through the NAT gateway | ❌ No | Later, the EKS cluster |
| data | ❌ No | ❌ No | Later, the database |

Each tier has one subnet in each Availability Zone. The private subnets are
/20, larger than the others, because the pods of the EKS cluster take their
IP addresses from them: EKS Auto Mode assigns addresses to the nodes in
blocks of 16, and a /24 holds at most 16 such blocks, where a /20 holds 256.

| Tier | ap-northeast-1a | ap-northeast-1c |
| --- | --- | --- |
| public | 10.0.0.0/24 | 10.0.1.0/24 |
| private | 10.0.16.0/20 | 10.0.32.0/20 |
| data | 10.0.2.0/24 | 10.0.3.0/24 |

Each tier has one route table, associated with its two subnets.

| Route table | Destination | Target |
| --- | --- | --- |
| public | 10.0.0.0/16 | Local |
| | 0.0.0.0/0 | Internet gateway |
| private | 10.0.0.0/16 | Local |
| | 0.0.0.0/0 | NAT gateway |
| | S3 prefix list | Gateway endpoint for S3 |
| data | 10.0.0.0/16 | Local |

## Creating the network with Terraform

To create the network:

1. Before you ask the agent to write the configuration, review the VPC
   design with the
   [`/apex:eks-design`](https://aws-samples.github.io/sample-apex-skills/docs/steering/commands/apex/eks-design)
   command of APEX Skills, which compares an EKS design with the AWS best
   practices.

   To review the VPC design, start a Claude Code session at the repository
   root and paste the following review request. Fill its "Design" section with
   the "AWS resource settings" section of the step 2 prompt.

   ````text
   /apex:eks-design

   # Review request
   I am building an EKS cluster. The design below is for its VPC.
   Review the design with the context in mind.

   ## Context
   - This is a personal lab. It is torn down every night to keep the cost down.

   ## Design
   ```
   (the "AWS resource settings" section of the step 2 prompt)
   ```
   ````

   The command answers with a table of findings ranked by severity and the
   details of each finding. Fix the VPC design according to the findings, and
   review it again until nothing new comes up. The prompt of step 2 is the
   result of a few rounds.

2. Ask the agent to write the configuration. Start a Claude Code session at
   the repository root and paste the following prompt.

   ```text
   /terraform-skill
   /terraform-style-guide

   # Summary
   Create a Terraform configuration for a VPC that hosts an EKS cluster and a database.

   ## Prerequisites
   - AWS credentials are passed at run time through AWS_PROFILE.

   ## Working environment
   - Create the Terraform configuration in parts/10-vpc/terraform.
   - Put a .gitignore that excludes generated files in the same directory.

   ## AWS resource settings

   ### Common
   - Tag every resource with the following tags.
     - Project = eks-platform-lab
     - Part = 10-vpc
   - Name every resource eks-platform-lab-<kind>-<tier>-<AZ>.
     - The kinds are vpc, subnet, igw, eip, nat, rtb, and vpce.
     - Add the tier and the AZ only when they are needed to distinguish
       resources of the same kind.
       - eks-platform-lab-vpc
       - eks-platform-lab-subnet-public-ap-northeast-1a
       - eks-platform-lab-rtb-public
     - For the VPC endpoint, add the service name instead of the tier and the AZ.
       - eks-platform-lab-vpce-s3
   - Use the Region ap-northeast-1.

   ### AWS resource list
   - VPC: 1
   - Subnets: 6
   - Internet gateway: 1
   - Elastic IP: 1
   - NAT gateway: 1
   - Route tables: 3
   - VPC endpoint: 1

   ### VPC
   - Use the IPv4 CIDR block 10.0.0.0/16.
   - Enable DNS resolution and DNS hostnames.

   ### Subnets
   - Use the following two AZs.
     - ap-northeast-1a
     - ap-northeast-1c
   - Arrange the subnets in the following three tiers.
     - public: the NAT gateway and the load balancer
     - private: the EKS cluster
     - data: the database
   - Use the following IPv4 CIDR blocks for each tier in each AZ.
     - public
       - 10.0.0.0/24 (ap-northeast-1a)
       - 10.0.1.0/24 (ap-northeast-1c)
     - private
       - 10.0.16.0/20 (ap-northeast-1a)
       - 10.0.32.0/20 (ap-northeast-1c)
     - data
       - 10.0.2.0/24 (ap-northeast-1a)
       - 10.0.3.0/24 (ap-northeast-1c)
   - Do not assign public IP addresses automatically to instances launched in any subnet.
   - Tag the public subnets with kubernetes.io/role/elb = 1.
   - Tag the private subnets with kubernetes.io/role/internal-elb = 1.

   ### Internet gateway
   - Attach it to the VPC.

   ### Elastic IP
   - Allocate it to the NAT gateway.

   ### NAT gateway
   - Place it in the public subnet in ap-northeast-1a.

   ### Route tables
   - Do not use the main route table.
   - Create one per tier.
   - Associate the two subnets of each tier with the route table of the tier.
   - Set the target of the default route of public to the internet gateway.
   - Set the target of the default route of private to the NAT gateway.
   - Do not create a default route in data.

   ### VPC endpoint
   - Make it a gateway endpoint for S3.
   - Associate it with the route table of private.

   ## Terraform settings

   ### Versions
   - Constrain the Terraform version to ~> 1.10, which supports S3 native locking.
   - Constrain the AWS provider version to ~> 6.0.

   ### State
   - Use the S3 backend.
   - Use parts/10-vpc/terraform.tfstate as the state key.
   - Lock with S3 native locking.
   - Do not include the bucket name in the backend configuration;
     pass it with -backend-config on terraform init.

   ### Output
   - Output the VPC ID as vpc_id.
   - Output the IPv4 CIDR block of the VPC as vpc_cidr_block.
   - Output the lists of subnet IDs per tier under the following names,
     in the order of ap-northeast-1a and ap-northeast-1c.
     - public_subnet_ids
     - private_subnet_ids
     - data_subnet_ids

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
   `backend "s3"` block has no `bucket` line. Ask the agent to fix what
   differs. The files in [terraform/](terraform/) are the result of this
   step.

3. Plan and apply. Make sure that the AWS CLI is signed in to the profile
   `<account-name>-admin`, then ask the agent:

   ```text
   /terraform-skill
   Initialize parts/10-vpc/terraform with the profile <account-name>-admin.
   Take the bucket name from the output bucket_name of parts/05-terraform-state/terraform,
   and pass it as -backend-config.
   Then show me the plan, and apply it after I approve.
   ```

   The plan adds 20 resources: the VPC, six subnets, the internet gateway,
   the Elastic IP, the NAT gateway, three route tables with six
   associations, and the gateway endpoint for S3. The NAT gateway takes a
   minute or two to become available. From now on the network costs about
   1.6 USD a day (see [Cost](#cost)), so tear it down when you stop for the
   day.

   Or run the commands yourself:

   ```bash
   bucket_name=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/05-terraform-state/terraform \
     output -raw bucket_name \
   )

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     init -backend-config="bucket=${bucket_name}"

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     plan -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     apply terraform.tfplan
   ```

4. Check the network from outside Terraform. The checks come in four
   groups, each covering related resources.

   If you run the commands yourself instead of asking the agent, take the
   VPC ID from the output `vpc_id` first:

   ```bash
   vpc_id=$( \
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     output -raw vpc_id \
   )
   ```

   **The VPC and its subnets.** The VPC has the CIDR block 10.0.0.0/16 and
   both DNS settings enabled, and its six subnets have the tiers,
   Availability Zones, and CIDR blocks described in [VPC design](#vpc-design).
   None of them assigns public IP addresses automatically.

   To check this, ask the agent:

   ```text
   Show me the VPC eks-platform-lab-vpc with the profile <account-name>-admin:
   its CIDR block and its DNS settings,
   and a table of its subnets with the Name, the Availability Zone, the CIDR block,
   and whether public IP addresses are assigned automatically.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     ec2 describe-vpcs --vpc-ids "$vpc_id" \
     --query 'Vpcs[].[Tags[?Key==`Name`].Value|[0],CidrBlock]' \
     --output table

   aws --profile <account-name>-admin \
     ec2 describe-vpc-attribute --vpc-id "$vpc_id" --attribute enableDnsSupport \
     --query 'EnableDnsSupport.Value' \
     --output text

   aws --profile <account-name>-admin \
     ec2 describe-vpc-attribute --vpc-id "$vpc_id" --attribute enableDnsHostnames \
     --query 'EnableDnsHostnames.Value' \
     --output text

   aws --profile <account-name>-admin \
     ec2 describe-subnets --filters Name=vpc-id,Values="$vpc_id" \
     --query 'sort_by(Subnets,&Tags[?Key==`Name`].Value|[0])[].[Tags[?Key==`Name`].Value|[0],AvailabilityZone,CidrBlock,MapPublicIpOnLaunch]' \
     --output table
   ```

   **The routes.** Each tier has its own route table, with its two subnets
   associated and the routes described in [VPC design](#vpc-design). The
   main route table has no subnets.

   To check this, ask the agent:

   ```text
   Show me the route tables of the VPC eks-platform-lab-vpc with the profile <account-name>-admin:
   for each one its Name, the number of subnets associated with it,
   and its routes with the destination and the target.
   ```

   Or run the command yourself:

   ```bash
   aws --profile <account-name>-admin \
     ec2 describe-route-tables --filters Name=vpc-id,Values="$vpc_id" \
     --query 'RouteTables[].{Name:Tags[?Key==`Name`].Value|[0],Id:RouteTableId,Main:Associations[0].Main,Subnets:length(Associations[?SubnetId]),Routes:Routes[].{Destination:DestinationCidrBlock||DestinationPrefixListId,Target:GatewayId||NatGatewayId}}' \
     --output table
   ```

   **The ways out.** The internet gateway is attached to the VPC, and the
   NAT gateway is available in the public subnet in ap-northeast-1a, with
   the Elastic IP associated.

   To check this, ask the agent:

   ```text
   Show me how the VPC eks-platform-lab-vpc reaches the internet with the profile <account-name>-admin:
   the internet gateway and its attachment state,
   the NAT gateway with its subnet and its state,
   and the Elastic IP with what it is associated with.
   ```

   Or run the commands yourself:

   ```bash
   aws --profile <account-name>-admin \
     ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values="$vpc_id" \
     --query 'InternetGateways[].[Tags[?Key==`Name`].Value|[0],Attachments[0].State]' \
     --output table

   aws --profile <account-name>-admin \
     ec2 describe-nat-gateways --filter Name=vpc-id,Values="$vpc_id" \
     --query 'NatGateways[].[Tags[?Key==`Name`].Value|[0],State,SubnetId,NatGatewayAddresses[0].PublicIp]' \
     --output table

   aws --profile <account-name>-admin \
     ec2 describe-addresses --filters Name=tag:Project,Values=eks-platform-lab \
     --query 'Addresses[].[Tags[?Key==`Name`].Value|[0],PublicIp]' \
     --output table
   ```

   **The shortcut to S3.** The gateway endpoint for S3 is available and
   associated with the private route table only.

   To check this, ask the agent:

   ```text
   Show me the VPC endpoints of the VPC eks-platform-lab-vpc with the profile <account-name>-admin:
   the service, the type, the state, and the route tables they are associated with.
   ```

   Or run the command yourself:

   ```bash
   aws --profile <account-name>-admin \
     ec2 describe-vpc-endpoints --filters Name=vpc-id,Values="$vpc_id" \
     --query 'VpcEndpoints[].[Tags[?Key==`Name`].Value|[0],ServiceName,VpcEndpointType,State,join(`", "`,RouteTableIds)]' \
     --output table
   ```

## Teardown

This part is torn down every night and built again the next day, because
the NAT gateway and its Elastic IP are charged by the hour. To build it
again, run only step 3 of
[Creating the network with Terraform](#creating-the-network-with-terraform).

To tear down the network:

1. Plan and destroy. Ask the agent:

   ```text
   /terraform-skill
   Destroy parts/10-vpc/terraform with the profile <account-name>-admin.
   Show me the plan first, and destroy after I approve.
   ```

   Or run the commands yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     plan -destroy -out=terraform.tfplan

   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     apply terraform.tfplan
   ```

2. Confirm that nothing of this part is left and nothing is charged: the
   state has no resources, no Elastic IP remains, and the NAT gateway is
   either gone or in the state `deleted`. A deleted NAT gateway stays
   visible for about an hour, and it is not charged.

   To check this, ask the agent:

   ```text
   Show me with the profile <account-name>-admin:
   the resources in the state of parts/10-vpc/terraform,
   the Elastic IPs tagged Project = eks-platform-lab,
   and the NAT gateways tagged Project = eks-platform-lab with their state.
   ```

   Or run the commands yourself:

   ```bash
   AWS_PROFILE=<account-name>-admin \
   terraform -chdir=parts/10-vpc/terraform \
     state list

   aws --profile <account-name>-admin \
     ec2 describe-addresses --filters Name=tag:Project,Values=eks-platform-lab \
     --query 'Addresses[].[Tags[?Key==`Name`].Value|[0],PublicIp]' \
     --output table

   aws --profile <account-name>-admin \
     ec2 describe-nat-gateways --filter Name=tag:Project,Values=eks-platform-lab \
     --query 'NatGateways[].[Tags[?Key==`Name`].Value|[0],State]' \
     --output table
   ```

## Cost

This part is charged for the following resources.

| Resource | Name | Per day | Per month |
| --- | --- | --- | --- |
| NAT gateway | `eks-platform-lab-nat` | 1.49 USD | 45.26 USD |
| Data processed by the NAT gateway | | 0.062 USD per GB | 0.062 USD per GB |
| Elastic IP | `eks-platform-lab-eip` | 0.12 USD | 3.65 USD |
| Data transfer between Availability Zones | | 0.01 USD per GB in each direction | 0.01 USD per GB in each direction |
