# AWS Serverless Data Analytics Pipeline

An end-to-end AWS proof of concept for event-driven sales CSV ingestion, SQL transformation, data-quality checks, partitioned Parquet publication, metadata cataloging, operational monitoring, and a published QuickSight dashboard.

> **Source-code publication status:** Documentation only. The original deployed Lambda packages and Step Functions state-machine definition have not yet been exported and verified. Do not treat this repository as a deployable reproduction until reviewed source files and configuration templates are added.

## Architecture

1. A CSV file arrives in a private Amazon S3 incoming prefix.
2. Amazon EventBridge initiates an AWS Step Functions ingestion workflow.
3. AWS Lambda stages the file and coordinates processing.
4. Amazon Athena transforms and validates the data.
5. Validated Parquet output is published to a curated, batch-partitioned S3 prefix; AWS Glue Data Catalog exposes the table and partitions.
6. DynamoDB records ingestion status and supports duplicate detection; Lambda monitoring and SNS notifications surface operational issues.
7. Amazon QuickSight queries the curated dataset through Athena and provides a published sales dashboard. SPICE refreshes are manual.

## AWS services

| Service | Responsibility |
| --- | --- |
| Amazon S3 | Incoming, staging, validation, curated, and query-result storage |
| Amazon EventBridge | Object-arrival workflow trigger |
| AWS Step Functions | Orchestration and execution state |
| AWS Lambda | Staging, publishing, monitoring, inspection, and recovery planning |
| Amazon Athena | SQL transformation, validation, and analytics |
| AWS Glue Data Catalog | Dataset metadata and partition registration |
| Amazon DynamoDB | Ingestion ledger and recovery coordination locks |
| Amazon SNS | Operational alert notifications |
| Amazon QuickSight | Published sales analytics dashboard |
| AWS IAM | Scoped service permissions |

## Demonstrated capabilities

- Automated processing of new CSV batches
- Curated Parquet data queryable through Athena
- Batch partition registration in Glue
- Ingestion status and deduplication ledger
- Stale-processing monitoring and SNS alert testing
- Recovery inspection, dry-run planning, and conditional lock testing
- Published QuickSight dashboard

Recovery execution is **manual**; this proof of concept does not claim automated replay. Curated data uses **Parquet**, not a transactional Apache Iceberg, Delta Lake, or Hudi table.

## Security and publication policy

The deployed resources and original code must be reviewed **before** publication. Do not commit:

- AWS credentials, tokens, private keys, passwords, or connection secrets
- Account-specific ARNs, account IDs, personal email addresses, or private resource identifiers
- Real production data, execution logs with sensitive payloads, or unreviewed configuration exports
- IAM policies with unnecessarily broad permissions

Use environment variables or deployment parameters for bucket names, table names, workgroups, state-machine ARNs, SNS topic ARNs, and DynamoDB table names. Prefer IAM roles and least-privilege policies over embedded credentials. Sanitize a copy of each original file, then compare control flow, queries, and error handling to verify that the example still represents the deployed behavior.

## Planned source layout

```text
lambda/                 # Reviewed and commented original Lambda sources
step-functions/         # Sanitized state-machine definition
sql/                    # Athena transformation and validation SQL
iam/                    # Reviewed example least-privilege policies
config/                 # Non-secret configuration examples
tests/                  # Syntax and behavior-preservation checks
docs/                   # Architecture and operational documentation
```

These directories are planned, **not yet published**.

## Portfolio

[Project portfolio](https://wconnorgunn.com/)

## Scope

Personal learning project, not a production deployment blueprint. Review security, access controls, cost settings, retries, and data governance requirements before adapting it to another environment.
