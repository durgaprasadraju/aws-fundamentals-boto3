# Deploy `attach_policy.py` in AWS Lambda (Console UI)

Step-by-step guide to run `attach_policy.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Role from create_role exists.

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
        "iam:CreateRole",
        "iam:GetRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:ListRoles"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `iam-lambda-admin-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `iam-attach-policy-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `iam-lambda-admin-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `attach_policy.py`
2. **Runtime settings** → **Handler:** `attach_policy.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `ROLE_NAME` | `boto3-learning-lambda-role` |

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
2. **Event name:** `AttachPolicyTest`
3. **Event JSON:**

```json
{
  "role_name": "boto3-learning-lambda-role",
  "policy_arn": "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"role_name\": \"boto3-learning-lambda-role\", \"attached\": true}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `NoSuchEntity` | Role must exist first |

---

## Quick Checklist

```
[ ] Role exists
[ ] Handler: attach_policy.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../attach_policy.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
