# Deploy `delete_secret.py` in AWS Lambda (Console UI)

Step-by-step guide to run `delete_secret.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Secret exists.
2. Default 7-day recovery unless force_delete is true.

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
| **Function name** | `secrets-delete-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `secrets-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `delete_secret.py`
2. **Runtime settings** → **Handler:** `delete_secret.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |

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
2. **Event name:** `DeleteSecretTest`
3. **Event JSON:**

```json
{
  "secret_name": "boto3-learning/db-credentials",
  "force_delete": false,
  "recovery_window_days": 7
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"secret_name\": \"boto3-learning/db-credentials\", \"force_delete\": false}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `ResourceNotFoundException` | Secret not found |

---

## Quick Checklist

```
[ ] Confirm secret name
[ ] Handler: delete_secret.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../delete_secret.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
