---
name: aws-learnings
description: "Proactively catch common AWS infrastructure mistakes before they happen. Use when creating or modifying AWS components — CloudFormation, CDK, Lambda, API Gateway, IAM, S3, CloudFront, EC2, EventBridge, SQS, Secrets Manager, or SSM — to find and apply hard-won deployment lessons and avoid known pitfalls. Read-only: fetches lessons, does not add them."
---

# AWS Learnings (Find Lessons)

## Overview

This skill finds hard-won lessons from real AWS deployments covering API Gateway, Lambda, IAM, S3, CloudFront, CloudFormation, Secrets Management, EC2, EventBridge, SQS, and more. Use it to avoid common pitfalls when architecting or modifying AWS infrastructure.

The library is published in [llms.txt](https://llmstxt.org/) format: a single index file links to one self-contained Markdown file per lesson. **Fetch only the lessons relevant to the AWS services in the current task** — don't pull the whole library.

This skill is **read-only**. To contribute a new lesson, use the `aws-learnings-add` skill instead.

## Instructions

Before creating or modifying AWS infrastructure (CloudFormation, CDK, SAM, Terraform, or manual configuration):

1. **Fetch the index** (it's small — just links + one-line summaries):

   **URL:** https://raw.githubusercontent.com/jbdamask/aws-learnings-library/main/llms.txt

   Use `WebFetch` or `curl` to retrieve it.

2. **Identify which AWS services are involved** in the current task (API Gateway, Lambda, IAM, etc.).

3. **Scan the matching sections** of the index. Each entry is a link followed by a one-line summary — enough to tell whether the lesson applies.

4. **Fetch only the relevant lesson files.** Each link in the index is the fully-qualified raw URL of a single lesson, e.g.
   `https://raw.githubusercontent.com/jbdamask/aws-learnings-library/main/lessons/apigw-001.md`.
   Fetch them with `WebFetch` or `curl`.

5. **Apply the lessons proactively** — check the current code/templates against the known gotchas before making changes. If a lesson is relevant, cite it (by id, e.g. `apigw-001`) when explaining decisions to the user.

## When to Consult

- Writing or modifying CloudFormation templates
- Configuring API Gateway resources, methods, or CORS
- Setting up Lambda functions (handler paths, modules, permissions, warm-container state)
- Managing IAM roles across stacks, or Lambda-invoked CloudFormation
- Configuring S3 buckets with CloudFront distributions, or presigned-URL uploads
- Working with Secrets Manager or SSM Parameter Store
- Setting up EC2 instances with UserData scripts, or spot instances
- Wiring EventBridge rules or SQS + Lambda async job processing
- Any cross-stack CloudFormation references or exports
