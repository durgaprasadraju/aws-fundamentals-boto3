# Deploy `create_secret.py` in AWS Lambda (Console UI)

Step-by-step guide to run `create_secret.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Secret must not already exist.

---

## Step 1: Create IAM Role (Console)

1. Open **IAM** → **Roles** → **Create role**
2. **Trusted entity:** AWS service → **Lambda**
3. **Permissions:** attach:
   - `AWSLambdaBasicExecutionRole`
   - Custom inline policy (replace `REGION`, `ACCOUNT_ID`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:DeleteSecret",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:boto3-learning/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `secrets-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `secrets-create-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `secrets-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `create_secret.py`
2. **Runtime settings** → **Handler:** `create_secret.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `SECRET_NAME` | Optional |
| `SECRET_VALUE` | Optional |

---

## Step 5: General Configuration

**Configuration** → **General configuration** → **Edit**

| Setting | Value |
|--------|--------|
| **Timeout** | `30` seconds |
| **Memory** | `128` MB |



---

## Step 6: Test in Console

1. **Test** tab → **Create new event**
2. **Event name:** `CreateSecretTest`
3. **Event JSON:**

```json
{
  "secret_name": "boto3-learning/db-credentials",
  "secret_string": "{\"username\":\"admin\",\"password\":\"ChangeMe123!\"}",
  "description": "Database credentials for learning lab"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"secret_name\": \"boto3-learning/db-credentials\", \"secret_arn\": \"arn:aws:secretsmanager:...\", \"version_id\": \"...\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `ResourceExistsException` | Secret already exists |
| `AccessDeniedException` | Add secretsmanager:CreateSecret |

---

## Quick Checklist

```
[ ] Run before get/update
[ ] Never log secret values
[ ] Handler: create_secret.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../create_secret.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
