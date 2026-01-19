---
name: ec2-claude-code
description: Create an Amazon Linux 2023 EC2 instance with Claude Code, tmux, git, and beads (bd) task tracking pre-installed. Use when user wants to spin up a cloud development environment, create an EC2 for Claude Code, launch a remote Claude Code instance, or set up a dev box on AWS. Supports multiple instances per account with unique naming.
---

# EC2 with Claude Code

Provision a ready-to-use AWS EC2 instance with Claude Code, tmux, git, and beads (bd) task tracking.

## Prerequisites

- AWS CLI configured
- User must provide an AWS profile with EC2 permissions

## Workflow

### 1. Gather Information

Ask user for:
- **AWS Profile** (required): Which AWS CLI profile to use
- **Key Pair** (optional): Use existing or create new

### 2. Set Up Variables

Generate unique names using profile and timestamp to allow multiple instances per account:

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STACK_NAME="claude-code-${AWS_PROFILE}-${TIMESTAMP}"
KEY_NAME="claude-code-key-${AWS_PROFILE}-${TIMESTAMP}"
```

### 3. Create Key Pair (if needed)

```bash
aws ec2 create-key-pair \
  --profile $AWS_PROFILE \
  --key-name $KEY_NAME \
  --query 'KeyMaterial' \
  --output text > ${KEY_NAME}.pem
chmod 400 ${KEY_NAME}.pem
```

### 4. Copy and Deploy CloudFormation

Copy template from skill assets to working directory, then deploy:

```bash
cp <skill-assets>/cloudformation-ec2-claude-code.yaml .

aws cloudformation create-stack \
  --profile $AWS_PROFILE \
  --stack-name $STACK_NAME \
  --template-body file://cloudformation-ec2-claude-code.yaml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=$KEY_NAME \
    ParameterKey=InstanceType,ParameterValue=t3.medium \
    ParameterKey=SSHLocation,ParameterValue=0.0.0.0/0
```

### 5. Wait and Get Outputs

```bash
aws cloudformation wait stack-create-complete \
  --profile $AWS_PROFILE \
  --stack-name $STACK_NAME

aws cloudformation describe-stacks \
  --profile $AWS_PROFILE \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs' \
  --output table
```

### 6. Verify Installation

Wait ~60 seconds for user data to complete, then verify:

```bash
ssh -o StrictHostKeyChecking=no -i ${KEY_NAME}.pem ec2-user@<PUBLIC_IP> \
  "cat ~/setup-complete.txt && git --version && tmux -V && ~/.local/bin/claude --version && bd --version"
```

### 7. Provide Connection Info

Give user the SSH command and note that:
- `claude` is available at `~/.local/bin/claude`
- `bd` (beads) is available for task tracking
- A CLAUDE.md file with beads instructions is in `/home/ec2-user/.claude`

## Optional: GitHub SSH Access

If user needs private repo access:

1. Copy their SSH key:
   ```bash
   scp -i ${KEY_NAME}.pem <LOCAL_SSH_KEY> ec2-user@<IP>:~/.ssh/
   ```

2. Configure SSH on instance:
   ```bash
   ssh -i ${KEY_NAME}.pem ec2-user@<IP> 'chmod 600 ~/.ssh/<KEY> && cat >> ~/.ssh/config << EOF
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/<KEY>
       IdentitiesOnly yes
   EOF
   chmod 600 ~/.ssh/config'
   ```

3. Test: `ssh -T git@github.com`

## Cleanup Command

```bash
aws cloudformation delete-stack --profile $AWS_PROFILE --stack-name $STACK_NAME
aws ec2 delete-key-pair --profile $AWS_PROFILE --key-name $KEY_NAME
rm ${KEY_NAME}.pem
```

## CloudFormation Template

Located at: `assets/cloudformation-ec2-claude-code.yaml`

Creates:
- EC2 instance (Amazon Linux 2023 via SSM parameter, 30GB gp3)
- Security group (SSH on port 22)
- User data installs: dnf update, git, tmux, Claude Code, beads (bd)
- CLAUDE.md with beads task tracking instructions in /home/ec2-user/.claude
