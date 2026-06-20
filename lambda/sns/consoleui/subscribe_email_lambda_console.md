# Deploy `subscribe_email.py` in AWS Lambda (Console UI)

Step-by-step guide to run `subscribe_email.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. SNS topic exists.
2. Confirm subscription via email link.

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
| **Function name** | `lab-sns-subscribe-email` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-sns-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `subscribe_email.py`
2. **Runtime settings** → **Handler:** `subscribe_email.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `TOPIC_ARN` | Topic ARN |
| `EMAIL` | your@email.com |

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
2. **Event name:** `SubscribeEmailTest`
3. **Event JSON:**

```json
{
  "topic_arn": "arn:aws:sns:us-east-1:ACCOUNT:lab-notifications",
  "email": "you@example.com"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Email subscription created\", \"pending_confirmation\": true}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `InvalidParameter` | Check email format |

---

## Quick Checklist

```
[ ] Confirm email
[ ] Handler: subscribe_email.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../subscribe_email.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
