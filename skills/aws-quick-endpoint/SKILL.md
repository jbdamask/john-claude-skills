---
name: aws-quick-endpoint
description: Create a token-secured REST API endpoint backed by AWS Lambda and DynamoDB with full CRUD and paginated list support. Deploys via CloudFormation. Use when user wants to quickly spin up an API endpoint, create a simple REST API on AWS, build a quick data store with an API, set up a Lambda+DynamoDB endpoint, or needs a fast way to log and retrieve structured data. Triggers on "create an endpoint", "quick API", "Lambda endpoint", "DynamoDB API", "CRUD endpoint", "log data to AWS".
---

# AWS Quick Endpoint

Deploy a token-secured REST API (API Gateway HTTP API + Lambda + DynamoDB) with full CRUD and paginated list operations via CloudFormation. Everything is IaC.

## Prerequisites

- AWS CLI configured with a profile that has permissions for CloudFormation, Lambda, API Gateway, DynamoDB, and IAM
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
AUTH_TOKEN=$(python3 -c "import uuid; print(uuid.uuid4())")
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
    ParameterKey=AuthToken,ParameterValue=$AUTH_TOKEN \
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

Extract the API URL from outputs for the test step. The auth token is NOT in the outputs (NoEcho parameter) — use the `$AUTH_TOKEN` variable from step 2.

### 5. Test the Endpoint

Run a quick smoke test to confirm everything works. Use the resource name and partition key from step 1:

```bash
API_URL="<ResourceEndpoint output value>"

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

**IMPORTANT:** Always write a markdown file called `USAGE.md` in the working directory with ready-to-copy curl examples using the actual URL, token, profile, and stack name from this deployment. The user should be able to paste commands directly into their terminal without editing.

Use this template, substituting all `<placeholders>` with real values from the deployment:

```markdown
# <Resource Name> API

**Endpoint:** `<ResourceEndpoint URL>`
**Auth token:** `<actual auth token>`

## Setup

```bash
TOKEN="<actual auth token>"
URL="<actual ResourceEndpoint URL>"
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
curl -s "$URL?limit=25&next_token=<TOKEN_FROM_RESPONSE>" \
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

## Cleanup

**Warning:** This permanently deletes the DynamoDB table and all data.

```bash
aws cloudformation delete-stack --profile <profile> --stack-name <stack-name>
```
```

After writing the file, tell the user: `Usage examples saved to USAGE.md`

### 7. Done

The `USAGE.md` from step 6 contains everything the user needs: URL, token, curl examples, and cleanup command. No separate info file is needed.

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

**Warning:** This permanently deletes the DynamoDB table and all its data.

**Stack update gotcha:** The AuthToken parameter uses `NoEcho`, so if you update the stack, you must re-provide the exact same token value. CloudFormation cannot recover NoEcho parameter values from previous deployments. Always save the token locally (step 7).

## CloudFormation Template

Located at: `assets/cloudformation-quick-endpoint.yaml`

Creates:
- **DynamoDB Table** — On-demand billing (pay-per-request), point-in-time recovery enabled, configurable partition key
- **Lambda Function** — Python 3.14, inline CRUD handler with token auth, auto-timestamps, Decimal/float handling, paginated scan, input validation (10KB body limit, max depth 5, max 50 attrs per level), HMAC-signed pagination tokens
- **IAM Role** — Least-privilege: only DynamoDB CRUD actions scoped to the single table, plus CloudWatch Logs
- **API Gateway HTTP API** — Routes for GET (list), GET/{id}, POST, PUT/{id}, DELETE/{id} with CORS enabled
- **Auto-deploy stage** — Changes deploy immediately, no manual stage management
