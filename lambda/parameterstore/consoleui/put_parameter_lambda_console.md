# Deploy `put_parameter.py` in AWS Lambda (Console UI)

Step-by-step guide to run `put_parameter.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Parameter path uses leading `/`.

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
        "ssm:PutParameter",
        "ssm:GetParameter",
        "ssm:DeleteParameter"
      ],
      "Resource": "arn:aws:ssm:REGION:ACCOUNT_ID:parameter/boto3-learning/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `ssm-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `ssm-put-parameter-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `ssm-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `put_parameter.py`
2. **Runtime settings** → **Handler:** `put_parameter.lambda_handler`
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
2. **Event name:** `PutParameterTest`
3. **Event JSON:**

```json
{
  "parameter_name": "/boto3-learning/app/config",
  "parameter_value": "production",
  "parameter_type": "String",
  "overwrite": true
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"parameter_name\": \"/boto3-learning/app/config\", \"version\": 1}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Add ssm:PutParameter |

---

## Quick Checklist

```
[ ] Run first in SSM lab
[ ] Handler: put_parameter.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../put_parameter.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
