# Deploy `create_role.py` in AWS Lambda (Console UI)

Step-by-step guide to run `create_role.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Lambda execution role needs IAM admin permissions.

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
| **Function name** | `iam-create-role-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `iam-lambda-admin-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `create_role.py`
2. **Runtime settings** → **Handler:** `create_role.lambda_handler`
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
2. **Event name:** `CreateRoleTest`
3. **Event JSON:**

```json
{
  "role_name": "boto3-learning-lambda-role",
  "description": "Lab role"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"role_name\": \"boto3-learning-lambda-role\", \"role_arn\": \"arn:aws:iam::...\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Execution role needs iam:CreateRole |

---

## Quick Checklist

```
[ ] Elevated IAM on execution role
[ ] Handler: create_role.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../create_role.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
