# Deploy `send_logs.py` in AWS Lambda (Console UI)

Step-by-step guide to run `send_logs.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Same region (e.g. us-east-1). Log group may be auto-created.

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
        "cloudwatch:PutMetricData",
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DescribeAlarms",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `lab-cloudwatch-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-cw-send-logs` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-cloudwatch-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `send_logs.py`
2. **Runtime settings** → **Handler:** `send_logs.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `LOG_GROUP_NAME` | `/aws/lambda/lab-app` |
| `LOG_STREAM_NAME` | `lab-stream` |

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
2. **Event name:** `SendLogsTest`
3. **Event JSON:**

```json
{
  "log_group_name": "/aws/lambda/lab-app",
  "log_stream_name": "lab-stream",
  "message": "Order ORD-001 processed successfully"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Log event sent successfully\", \"log_group_name\": \"/aws/lambda/lab-app\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Add CloudWatch Logs permissions |
| `InvalidParameterException` | Check log group/stream names |

---

## Quick Checklist

```
[ ] Logs IAM on role
[ ] Handler: send_logs.lambda_handler
[ ] Event in CloudWatch Logs
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../send_logs.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
