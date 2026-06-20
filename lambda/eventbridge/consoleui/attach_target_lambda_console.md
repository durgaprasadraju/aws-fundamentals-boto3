# Deploy `attach_target.py` in AWS Lambda (Console UI)

Step-by-step guide to run `attach_target.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Rule exists.
2. Target Lambda needs permission for events.amazonaws.com.

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
        "events:PutEvents",
        "events:PutRule",
        "events:DescribeRule",
        "events:PutTargets"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `lab-eventbridge-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-eventbridge-attach-target` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-eventbridge-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `attach_target.py`
2. **Runtime settings** → **Handler:** `attach_target.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `RULE_NAME` | `lab-order-created-rule` |
| `TARGET_ARN` | Target Lambda ARN |

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
2. **Event name:** `AttachTargetTest`
3. **Event JSON:**

```json
{
  "rule_name": "lab-order-created-rule",
  "target_arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:lab-order-processor",
  "target_id": "lab-target-1",
  "event_bus_name": "default"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Target attached successfully\", \"target_id\": \"lab-target-1\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Add events:PutTargets and lambda:AddPermission on target |

---

## Quick Checklist

```
[ ] Rule created
[ ] Handler: attach_target.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../attach_target.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
