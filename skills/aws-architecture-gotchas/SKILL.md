---
name: aws-architecture-gotchas
description: "Proactively catch common AWS infrastructure mistakes before they happen. Use when creating or modifying AWS components — CloudFormation, CDK, Lambda, API Gateway, IAM, S3, CloudFront, EC2, Secrets Manager, or SSM — to apply hard-won deployment lessons and avoid known pitfalls."
---

# AWS Architecture Gotchas

## Overview

This skill provides hard-won lessons from real AWS deployments covering API Gateway, Lambda, IAM, S3, CloudFront, CloudFormation, Secrets Management, EC2, and more. Use it to avoid common pitfalls when architecting or modifying AWS infrastructure.

## Instructions

Before creating or modifying AWS infrastructure (CloudFormation, CDK, SAM, Terraform, or manual configuration), fetch and review the latest learnings document:

**URL:** https://raw.githubusercontent.com/jbdamask/scratch/refs/heads/main/AGENT_FILES/aws/AWS_LEARNINGS.md

Use `WebFetch` or `curl` to retrieve the document contents. Then:

1. Identify which AWS services are involved in the current task
2. Review the relevant sections of the learnings document for those services
3. Apply the lessons proactively — check the current code/templates against known gotchas before making changes
4. If a lesson is relevant, cite it when explaining decisions to the user

## When to Consult

- Writing or modifying CloudFormation templates
- Configuring API Gateway resources, methods, or CORS
- Setting up Lambda functions (handler paths, modules, permissions)
- Managing IAM roles across stacks
- Configuring S3 buckets with CloudFront distributions
- Working with Secrets Manager or SSM Parameter Store
- Setting up EC2 instances with UserData scripts
- Any cross-stack CloudFormation references or exports
