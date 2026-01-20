---
name: ec2-claude-code
description: Create an Ubuntu 24.04 LTS EC2 instance with Claude Code, Playwright (headless browser testing), tmux, git, beads (bd) task tracking, and agent-deck session manager pre-installed. Use when user wants to spin up a cloud development environment, create an EC2 for Claude Code, launch a remote Claude Code instance, or set up a dev box on AWS. Supports multiple instances per account with unique naming.
---

# EC2 with Claude Code

Provision a ready-to-use AWS EC2 instance with Claude Code, Playwright (headless Chromium), tmux, git, beads (bd) task tracking, and agent-deck session manager.

## Prerequisites

- AWS CLI configured
- GitHub CLI (`gh`) authenticated with repo access
- User must provide an AWS profile with EC2 permissions

## Workflow

### 1. Gather Information

Ask user for:
- **AWS Profile** (required): Which AWS CLI profile to use
- **Key Pair** (optional): Use existing or create new
- **GitHub Repo** (required): URL to clone (e.g., https://github.com/user/repo). A deploy key will be created for this repo, giving the EC2 write access to only this specific repository.

### 2. Set Up Variables

Generate unique names using profile and timestamp to allow multiple instances per account:

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STACK_NAME="claude-code-${AWS_PROFILE}-${TIMESTAMP}"
KEY_NAME="claude-code-key-${AWS_PROFILE}-${TIMESTAMP}"
DEPLOY_KEY_NAME="deploy-key-${STACK_NAME}"
DEPLOY_KEY_TITLE="EC2-${STACK_NAME}"
```

Parse the GitHub repo URL to extract owner and repo name:

```bash
# Extract owner/repo from URL (handles both https://github.com/owner/repo and git@github.com:owner/repo.git)
REPO_FULL=$(echo "$GITHUB_REPO" | sed -E 's|https://github.com/||; s|git@github.com:||; s|\.git$||')
REPO_OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_FULL" | cut -d'/' -f2)
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

### 4. Generate Deploy Key and Add to GitHub

Generate a new SSH key pair specifically for this EC2/repo combination:

```bash
ssh-keygen -t ed25519 -f ${DEPLOY_KEY_NAME} -N "" -C "${DEPLOY_KEY_TITLE}"
chmod 400 ${DEPLOY_KEY_NAME}
```

Add the public key as a deploy key to the GitHub repo with write access:

```bash
gh repo deploy-key add ${DEPLOY_KEY_NAME}.pub \
  --repo ${REPO_OWNER}/${REPO_NAME} \
  --title "${DEPLOY_KEY_TITLE}" \
  --allow-write
```

### 5. Copy and Deploy CloudFormation

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
    ParameterKey=SSHLocation,ParameterValue=0.0.0.0/0 \
    ParameterKey=GitHubRepo,ParameterValue=$GITHUB_REPO
```

### 6. Wait and Get Outputs

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

### 7. Verify Installation

Wait ~90 seconds for user data to complete (Playwright installation takes longer), then verify:

```bash
ssh -o StrictHostKeyChecking=no -i ${KEY_NAME}.pem ubuntu@<PUBLIC_IP> \
  "cat ~/setup-complete.txt && git --version && tmux -V && ~/.local/bin/claude --version && bd --version && npx playwright --version"
```

### 8. Provide Connection Info

Give user the SSH command and note that:
- `claude` is available at `~/.local/bin/claude`
- `bd` (beads) is available for task tracking
- `agent-deck` is available for managing Claude Code sessions
- Playwright with Chromium is pre-installed for headless browser testing
- A CLAUDE.md file with instructions is in `/home/ubuntu/.claude`

### 9. Set Up GitHub SSH Access with Deploy Key

Copy the deploy key to the EC2 and configure SSH for GitHub access:

1. Copy the deploy key to the EC2:
   ```bash
   scp -i ${KEY_NAME}.pem ${DEPLOY_KEY_NAME} ubuntu@<PUBLIC_IP>:~/.ssh/
   ```

2. Configure SSH to use the deploy key for GitHub:
   ```bash
   ssh -i ${KEY_NAME}.pem ubuntu@<PUBLIC_IP> "
     chmod 600 ~/.ssh/${DEPLOY_KEY_NAME}
     cat >> ~/.ssh/config << EOF
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/${DEPLOY_KEY_NAME}
       IdentitiesOnly yes
   EOF
     chmod 600 ~/.ssh/config
   "
   ```

3. Update the cloned repo's remote URL to use SSH:
   ```bash
   ssh -i ${KEY_NAME}.pem ubuntu@<PUBLIC_IP> "
     cd ~/${REPO_NAME}
     git remote set-url origin git@github.com:${REPO_OWNER}/${REPO_NAME}.git
   "
   ```

4. Verify GitHub authentication:
   ```bash
   ssh -i ${KEY_NAME}.pem ubuntu@<PUBLIC_IP> "ssh -o StrictHostKeyChecking=no -T git@github.com"
   ```

## Cleanup Command

**Important:** The cleanup removes the deploy key from GitHub by looking up its ID using the unique title. This ensures only the specific key for this EC2 instance is removed.

```bash
# Remove the deploy key from GitHub (lookup by title to get the key ID)
DEPLOY_KEY_ID=$(gh repo deploy-key list --repo ${REPO_OWNER}/${REPO_NAME} --json id,title \
  -q ".[] | select(.title == \"${DEPLOY_KEY_TITLE}\") | .id")
if [ -n "$DEPLOY_KEY_ID" ]; then
  gh repo deploy-key delete --repo ${REPO_OWNER}/${REPO_NAME} $DEPLOY_KEY_ID
  echo "Removed deploy key '${DEPLOY_KEY_TITLE}' from ${REPO_OWNER}/${REPO_NAME}"
else
  echo "Warning: Deploy key '${DEPLOY_KEY_TITLE}' not found in ${REPO_OWNER}/${REPO_NAME}"
fi

# Delete AWS resources
aws cloudformation delete-stack --profile $AWS_PROFILE --stack-name $STACK_NAME
aws ec2 delete-key-pair --profile $AWS_PROFILE --key-name $KEY_NAME

# Remove local key files
rm -f ${KEY_NAME}.pem ${DEPLOY_KEY_NAME} ${DEPLOY_KEY_NAME}.pub
```

## CloudFormation Template

Located at: `assets/cloudformation-ec2-claude-code.yaml`

Creates:
- EC2 instance (Ubuntu 24.04 LTS via SSM parameter, 30GB gp3)
- Security group (SSH on port 22)
- User data installs: apt update, Node.js 20 LTS, git, tmux, Claude Code, Playwright with Chromium, beads (bd), agent-deck
- CLAUDE.md with task tracking and browser testing instructions in /home/ubuntu/.claude
