# Deploy `send_message.py` in AWS Lambda (Console UI)

Step-by-step guide to run `send_message.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. SQS queue must exist.

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
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:REGION:ACCOUNT_ID:*"
    }
  ]
}
```

4. **Role name:** `lab-sqs-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-sqs-send` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-sqs-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `send_message.py`
2. **Runtime settings** → **Handler:** `send_message.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `QUEUE_URL` | Your queue URL |

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
2. **Event name:** `SendMessageTest`
3. **Event JSON:**

```json
{
  "queue_url": "https://sqs.us-east-1.amazonaws.com/ACCOUNT/lab-queue",
  "message_body": "{\"order_id\":\"ORD-001\",\"action\":\"process\"}"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"SQS message sent successfully\", \"message_id\": \"...\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `NonExistentQueue` | Create queue first |
| `AccessDenied` | Add sqs:SendMessage |

---

## Quick Checklist

```
[ ] Queue URL correct
[ ] Handler: send_message.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../send_message.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
