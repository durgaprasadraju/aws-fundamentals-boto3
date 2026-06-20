# Deploy `unsubscribe.py` in AWS Lambda (Console UI)

Step-by-step guide to run `unsubscribe.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Confirmed subscription ARN from subscribe_email.

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
| **Function name** | `lab-sns-unsubscribe` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-sns-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `unsubscribe.py`
2. **Runtime settings** → **Handler:** `unsubscribe.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `SUBSCRIPTION_ARN` | Subscription ARN |

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
2. **Event name:** `UnsubscribeTest`
3. **Event JSON:**

```json
{
  "subscription_arn": "arn:aws:sns:us-east-1:ACCOUNT:lab-notifications:abc123"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Subscription removed successfully\", \"unsubscribed\": true}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `NotFound` | Invalid subscription ARN |

---

## Quick Checklist

```
[ ] Subscription confirmed
[ ] Handler: unsubscribe.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../unsubscribe.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
