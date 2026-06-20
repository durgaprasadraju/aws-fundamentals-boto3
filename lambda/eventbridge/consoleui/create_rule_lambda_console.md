# Deploy `create_rule.py` in AWS Lambda (Console UI)

Step-by-step guide to run `create_rule.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Run before attach_target.

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
| **Function name** | `lab-eventbridge-create-rule` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-eventbridge-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `create_rule.py`
2. **Runtime settings** → **Handler:** `create_rule.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `RULE_NAME` | `lab-order-created-rule` |

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
2. **Event name:** `CreateRuleTest`
3. **Event JSON:**

```json
{
  "rule_name": "lab-order-created-rule",
  "event_bus_name": "default",
  "event_pattern": {
    "source": [
      "com.lab.orders"
    ],
    "detail-type": [
      "OrderCreated"
    ]
  }
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"EventBridge rule created successfully\", \"rule_name\": \"lab-order-created-rule\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Add events:PutRule |

---

## Quick Checklist

```
[ ] Rule in EventBridge console
[ ] Handler: create_rule.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../create_rule.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
