# Deploy `publish_message.py` in AWS Lambda (Console UI)

Step-by-step guide to run `publish_message.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. SNS topic must exist.

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
        "sns:Publish",
        "sns:Subscribe",
        "sns:Unsubscribe"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `lab-sns-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-sns-publish` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-sns-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `publish_message.py`
2. **Runtime settings** → **Handler:** `publish_message.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `TOPIC_ARN` | Your topic ARN |

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
2. **Event name:** `PublishMessageTest`
3. **Event JSON:**

```json
{
  "topic_arn": "arn:aws:sns:us-east-1:ACCOUNT:lab-notifications",
  "message": "Order ORD-001 has shipped.",
  "subject": "Order Shipped"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"SNS message published successfully\", \"message_id\": \"...\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `NotFound` | Create SNS topic first |

---

## Quick Checklist

```
[ ] Topic ARN in event
[ ] Handler: publish_message.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../publish_message.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
