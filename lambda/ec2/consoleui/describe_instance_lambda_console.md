# Deploy `describe_instance.py` in AWS Lambda (Console UI)

Step-by-step guide to run `describe_instance.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. EC2 instance exists (or omit ID to list all).

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
        "ec2:RunInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:CreateTags",
        "ec2:DescribeImages"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `lab-ec2-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-ec2-describe-instance` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-ec2-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `describe_instance.py`
2. **Runtime settings** → **Handler:** `describe_instance.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `INSTANCE_ID` | Optional default |

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
2. **Event name:** `DescribeInstanceTest`
3. **Event JSON:**

```json
{
  "instance_id": "i-0123456789abcdef0"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Instances described successfully\", \"count\": 1}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `InvalidInstanceID.NotFound` | Check instance ID |

---

## Quick Checklist

```
[ ] Real instance ID
[ ] Handler: describe_instance.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../describe_instance.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
