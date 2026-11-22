---
name: aws-quick-endpoint
description: Create a token-secured REST API endpoint backed by AWS Lambda and DynamoDB with full CRUD and paginated list support. Deploys via CloudFormation. Use when user wants to quickly spin up an API endpoint, create a simple REST API on AWS, build a quick data store with an API, set up a Lambda+DynamoDB endpoint, or needs a fast way to log and retrieve structured data. Triggers on "create an endpoint", "quick API", "Lambda endpoint", "DynamoDB API", "CRUD endpoint", "log data to AWS".
---

# AWS Quick Endpoint

Deploy a token-secured REST API (API Gateway HTTP API + Lambda + DynamoDB) with full CRUD and paginated list operations via CloudFormation. Everything is IaC.

## Token handling rule

The auth token lives only in AWS Secrets Manager. The stack generates it, so it never passes through a template parameter or a file.

- **Never write the token value to any file**, including `USAGE.md`. Files reference the secret ARN and fetch the token at run time.
- **Never show the token value in chat.** Keep it in a shell variable for the smoke test and say where to fetch it.

This way the skill's output is safe to commit no matter which directory or repo it runs in.

## Prerequisites

- AWS CLI configured with a profile that has permissions for CloudFormation, Lambda, API Gateway, DynamoDB, IAM, Secrets Manager, and CloudWatch Logs
- The profile must be able to create IAM roles

## Workflow

### 1. Gather Information

Ask user for:
- **AWS Profile** (required): Which AWS CLI profile to use
- **Resource name** (required): The REST resource (e.g., `pets`, `logs`, `records`). Must be lowercase, letters/numbers/hyphens only.
- **Partition key** (optional, default `id`): The DynamoDB primary key field name
- **Brief description** (optional): What data will be stored (helps generate usage examples)

### 2. Set Up Variables

Generate unique names using profile and timestamp:

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STACK_NAME="quick-ep-${RESOURCE_NAME}-${AWS_PROFILE}-${TIMESTAMP}"
```

### 3. Deploy CloudFormation

Copy template from skill assets to working directory, then deploy:

```bash
cp <skill-assets>/cloudformation-quick-endpoint.yaml .

aws cloudformation create-stack \
  --profile $AWS_PROFILE \
  --stack-name $STACK_NAME \
  --template-body file://cloudformation-quick-endpoint.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters \
    ParameterKey=ResourceName,ParameterValue=$RESOURCE_NAME \
    ParameterKey=PartitionKey,ParameterValue=${PARTITION_KEY:-id}
```

**Important:** `--capabilities CAPABILITY_NAMED_IAM` is required because the template creates an IAM role for the Lambda function.

### 4. Wait and Get Outputs

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

Extract `ResourceEndpoint` and `AuthTokenSecretArn` from the outputs. The token itself is not an output.

### 5. Test the Endpoint

Fetch the token into a shell variable (do not echo it), then run a quick smoke test. Use the resource name and partition key from step 1:

```bash
API_URL="<ResourceEndpoint output value>"
SECRET_ARN="<AuthTokenSecretArn output value>"
AUTH_TOKEN=$(aws secretsmanager get-secret-value \
  --profile $AWS_PROFILE \
  --secret-id "$SECRET_ARN" \
  --query SecretString --output text)

# Create a record
curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-token: $AUTH_TOKEN" \
  -d '{"name": "test-record"}'
# List records (paginated)
curl -s "$API_URL?limit=10" \
  -H "x-api-token: $AUTH_TOKEN"```

Verify both return 200/201 with valid JSON. If the create returns a record with an auto-generated `id`, `created_at`, and `updated_at`, the endpoint is working.

### 6. Provide Usage Info

**IMPORTANT:** Always write a markdown file called `USAGE.md` in the working directory with ready-to-copy curl examples using the actual URL, secret ARN, profile, and stack name from this deployment. The user should be able to paste commands directly into their terminal without editing. **Never put the token value in this file** — the Setup block fetches it from Secrets Manager.

Use this template, substituting all `<placeholders>` with real values from the deployment:

```markdown
# <Resource Name> API

**Endpoint:** `<ResourceEndpoint URL>`
**Auth token:** stored in Secrets Manager at `<AuthTokenSecretArn>`

## Setup

```bash
URL="<actual ResourceEndpoint URL>"
TOKEN=$(aws secretsmanager get-secret-value --profile <profile> \
  --secret-id "<AuthTokenSecretArn>" --query SecretString --output text)
```

## Create a record

```bash
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "x-api-token: $TOKEN" \
  -d '{"name": "example"}'```

Omit `id` and one is auto-generated. `created_at` and `updated_at` are added automatically.

## List all (paginated)

```bash
curl -s "$URL?limit=25" -H "x-api-token: $TOKEN"```

If `next_token` appears in the response, pass it to get the next page:

```bash
curl -s -G "$URL" --data-urlencode "limit=25" \
  --data-urlencode "next_token=<TOKEN_FROM_RESPONSE>" \
  -H "x-api-token: $TOKEN"```

## Get one

```bash
curl -s "$URL/<id>" -H "x-api-token: $TOKEN"```

## Update

```bash
curl -s -X PUT "$URL/<id>" \
  -H "Content-Type: application/json" \
  -H "x-api-token: $TOKEN" \
  -d '{"name": "updated"}'```

PUT is a full replace — send all fields you want to keep. `created_at` is preserved, `updated_at` is refreshed.

## Delete

```bash
curl -s -X DELETE "$URL/<id>" -H "x-api-token: $TOKEN"```

## Notes

- **CORS:** Enabled for all origins — safe to call from browser JavaScript
- **Limits:** Max body 10KB, max nesting depth 5, max 50 attributes per level
- **Pagination tokens** are HMAC-signed and tamper-proof
- **Rotating the auth token:** run the command below. The API accepts the new token within 5 minutes, and existing pagination tokens stop working.

```bash
aws secretsmanager put-secret-value --profile <profile> --secret-id "<AuthTokenSecretArn>" \
  --secret-string "$(aws secretsmanager get-random-password --profile <profile> \
    --password-length 40 --exclude-punctuation --query RandomPassword --output text)"
```

## Cleanup

**Warning:** This permanently deletes the DynamoDB table and all data, the auth token secret, and the logs.

```bash
aws cloudformation delete-stack --profile <profile> --stack-name <stack-name>
```
```

After writing the file, tell the user: `Usage examples saved to USAGE.md`

### 7. Done

The `USAGE.md` from step 6 contains everything the user needs: URL, how to fetch the token, curl examples, and cleanup command. No separate info file is needed. Before finishing, confirm the token value appears in no file you wrote.

## Cleanup

Delete all AWS resources by deleting the CloudFormation stack:

```bash
aws cloudformation delete-stack \
  --profile $AWS_PROFILE \
  --stack-name $STACK_NAME

aws cloudformation wait stack-delete-complete \
  --profile $AWS_PROFILE \
  --stack-name $STACK_NAME
```

**Warning:** This permanently deletes the DynamoDB table and all its data, the auth token secret, and the Lambda log group. All three are owned by the stack, so nothing is left behind.

Stack updates don't change the token. It lives in Secrets Manager, not in a template parameter, so there's nothing to re-supply.

## CloudFormation Template

Located at: `assets/cloudformation-quick-endpoint.yaml`

Creates:
- **DynamoDB Table** — On-demand billing (pay-per-request), point-in-time recovery enabled, configurable partition key
- **Secrets Manager Secret** — The 40-character auth token, generated by AWS at deploy time (about $0.40/month while the stack exists)
- **Lambda Function** — Python 3.14, inline CRUD handler with token auth (token fetched from Secrets Manager, cached 5 minutes), auto-timestamps, Decimal/float handling, paginated scan, input validation (10KB body limit, max depth 5, max 50 attrs per level), HMAC-signed pagination tokens
- **IAM Role** — Least-privilege: only DynamoDB CRUD actions scoped to the single table, read access to the one auth token secret, plus CloudWatch Logs
- **CloudWatch Log Group** — Owned by the stack with 30-day retention (`LogRetentionDays` parameter), so deleting the stack deletes the logs instead of orphaning them
- **API Gateway HTTP API** — Routes for GET (list), GET/{id}, POST, PUT/{id}, DELETE/{id} with CORS enabled
- **Auto-deploy stage** — Changes deploy immediately, no manual stage management
