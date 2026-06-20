# Deploy `create_alarm.py` in AWS Lambda (Console UI)

Step-by-step guide to run `create_alarm.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Publish metrics first with put_metric.py or alarm may show INSUFFICIENT_DATA.
2. Same region (e.g. us-east-1).

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
| **Function name** | `lab-cw-create-alarm` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-cloudwatch-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `create_alarm.py`
2. **Runtime settings** → **Handler:** `create_alarm.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `METRIC_NAMESPACE` | `Lab/Application` |
| `METRIC_NAME` | `OrdersProcessed` |
| `ALARM_NAME` | `lab-orders-high-alarm` |

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
2. **Event name:** `CreateAlarmTest`
3. **Event JSON:**

```json
{
  "alarm_name": "lab-orders-high-alarm",
  "namespace": "Lab/Application",
  "metric_name": "OrdersProcessed",
  "threshold": 100,
  "comparison_operator": "GreaterThanThreshold"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"CloudWatch alarm created successfully\", \"alarm_name\": \"lab-orders-high-alarm\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Add cloudwatch:PutMetricAlarm |
| `Validation error` | Verify threshold and metric names |

---

## Quick Checklist

```
[ ] Metrics published
[ ] Handler: create_alarm.lambda_handler
[ ] Alarm in CloudWatch console
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../create_alarm.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
