# Deploy `update_item.py` in AWS Lambda (Console UI)

Step-by-step guide to run `update_item.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Item exists.

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
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/LabUsers"
    }
  ]
}
```

4. **Role name:** `lab-dynamodb-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-dynamodb-update-item` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-dynamodb-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `update_item.py`
2. **Runtime settings** → **Handler:** `update_item.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `TABLE_NAME` | `LabUsers` |

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
2. **Event name:** `UpdateItemTest`
3. **Event JSON:**

```json
{
  "table_name": "LabUsers",
  "user_id": "user-001",
  "updates": {
    "role": "superadmin"
  }
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Item updated successfully\", \"user_id\": \"user-001\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `Validation error (400)` | updates must be non-empty dict |

---

## Quick Checklist

```
[ ] Item exists
[ ] Handler: update_item.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../update_item.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
