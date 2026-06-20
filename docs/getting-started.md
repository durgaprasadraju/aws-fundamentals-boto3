# Getting Started

## Prerequisites

- AWS account with programmatic access (IAM user or role)
- Python 3.11+ locally
- AWS CLI v2 configured (`aws configure`)
- Basic understanding of Lambda and IAM

## Quick Setup

```bash
cd aws-fundamentals-boto3
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export AWS_REGION=us-east-1
```

## Run Locally (without Lambda)

Each script supports local execution:

```bash
cd lambda/iam
python list_roles.py
```

Set environment variables before running (see each module README).

## Deploy to Lambda

General pattern:

```bash
cd lambda/iam
pip install -r ../../requirements.txt -t package/
cp *.py package/
cd package && zip -r ../iam-handlers.zip . && cd ..

aws lambda create-function \
  --function-name iam-list-roles-demo \
  --runtime python3.12 \
  --handler list_roles.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --zip-file fileb://iam-handlers.zip \
  --timeout 30 \
  --memory-size 256
```

Replace handler name per function. See each service README for IAM policies and env vars.

## Recommended Learning Order

1. IAM → understand permissions first
2. S3 → simple object storage
3. DynamoDB → serverless database
4. SNS / SQS → messaging
5. EventBridge → event routing
6. CloudWatch → observability
7. Secrets Manager / Parameter Store → configuration
8. EC2 / RDS → traditional compute and databases
9. Lambda-to-Lambda → orchestration patterns

## Cleanup

Always run cleanup steps in each module README after labs to avoid ongoing charges.
