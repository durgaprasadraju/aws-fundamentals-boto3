# Deploy `get_secret.py` in AWS Lambda (Console UI)

Step-by-step guide to run `get_secret.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. **Secret must exist** in Secrets Manager (same region as Lambda), e.g. `boto3-learning/db-credentials`.
   - Create it first with `create_secret.py` locally or in the Secrets Manager console.
2. **Same region** for Lambda and the secret (e.g. `us-east-1`).

---

## Step 1: Create IAM Role (Console)

1. Open **IAM** → **Roles** → **Create role**
2. **Trusted entity:** AWS service → **Lambda**
3. **Permissions:** attach:
   - `AWSLambdaBasicExecutionRole` (CloudWatch Logs)
   - Custom inline policy (replace `REGION`, `ACCOUNT_ID`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:boto3-learning/*"
    },
    {
      "Effect": "Allow",
      "Action": ["kms:Decrypt"],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `secrets-get-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function**
2. Choose **Author from scratch**
3. Use these settings:

| Setting | Value |
|--------|--------|
| **Function name** | `secrets-get-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | Use existing role → `secrets-get-lambda-role` |

4. Click **Create function**

---

## Step 3: Paste Code

1. In the function page, open the **Code** tab
2. Replace the default code with the full contents of `get_secret.py`
3. Confirm **Runtime settings**:

| Setting | Value |
|--------|--------|
| **Handler** | `get_secret.lambda_handler` |

4. Click **Deploy**

> Boto3 is already included in the Lambda Python runtime, so you do not need to upload a zip for this lab.

---

## Step 4: Environment Variables (Optional but Recommended)

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `SECRET_NAME` | `boto3-learning/db-credentials` |
| `AWS_REGION` | `us-east-1` (only if your secret is not in the Lambda region) |

If `SECRET_NAME` is set, the test event can be `{}`.

---

## Step 5: General Configuration

**Configuration** → **General configuration** → **Edit**

| Setting | Value |
|--------|--------|
| **Timeout** | `30` seconds |
| **Memory** | `128` MB (default is fine) |

---

## Step 6: Test in Console

1. **Test** tab → **Create new event**
2. **Event name:** `GetSecretTest`
3. **Event JSON:**

```json
{
  "secret_name": "boto3-learning/db-credentials"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"secret_name\": \"boto3-learning/db-credentials\", \"secret_arn\": \"arn:aws:secretsmanager:...\", \"version_id\": \"...\", \"value\": {\"username\": \"admin\", \"password\": \"ChangeMe123!\"}}"
}
```

The `body` field is a JSON string; parse it to read the secret fields.

---

## Alternative Test Event (Uses Env Var Only)

If you set `SECRET_NAME` in Step 4:

```json
{}
```

The handler falls back to the env var:

```python
secret_name = event.get("secret_name") or SECRET_NAME
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | IAM role missing `secretsmanager:GetSecretValue` or `kms:Decrypt` |
| `ResourceNotFoundException` | Secret name wrong, or secret in a different region |
| `secret_name is required` (400) | No `secret_name` in event and no `SECRET_NAME` env var |
| Timeout | Increase timeout; check VPC config if Lambda is in a VPC without endpoints |

---

## Quick Checklist

```
[ ] Secret exists in Secrets Manager
[ ] IAM role: GetSecretValue + kms:Decrypt + CloudWatch Logs
[ ] Lambda: Python 3.12, handler get_secret.lambda_handler
[ ] Code deployed from get_secret.py
[ ] Test event with secret_name (or SECRET_NAME env var set)
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../get_secret.py` | Lambda handler source code |
| `../create_secret.py` | Create the secret before testing get |
| `../README.md` | Module overview, CLI deployment, IAM reference |
