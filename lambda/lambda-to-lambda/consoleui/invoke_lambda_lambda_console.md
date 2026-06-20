# Deploy `invoke_lambda.py` in AWS Lambda (Console UI)

Step-by-step guide to run `invoke_lambda.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Target Lambda deployed and invokable.

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
        "lambda:InvokeFunction"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `lambda-invoke-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lambda-orchestrator-demo` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lambda-invoke-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `invoke_lambda.py`
2. **Runtime settings** → **Handler:** `invoke_lambda.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `TARGET_FUNCTION_NAME` | Optional |

---

## Step 5: General Configuration

**Configuration** → **General configuration** → **Edit**

| Setting | Value |
|--------|--------|
| **Timeout** | `60` seconds |
| **Memory** | `128` MB |



---

## Step 6: Test in Console

1. **Test** tab → **Create new event**
2. **Event name:** `InvokeLambdaTest`
3. **Event JSON:**

```json
{
  "function_name": "target-lambda-function",
  "payload": {
    "action": "process",
    "order_id": "ORD-1001"
  },
  "invocation_type": "RequestResponse"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"function_name\": \"target-lambda-function\", \"invocation_type\": \"RequestResponse\", \"status_code\": 200}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `AccessDeniedException` | Add lambda:InvokeFunction |
| `ResourceNotFoundException` | Deploy target Lambda |

---

## Quick Checklist

```
[ ] Target Lambda exists
[ ] Timeout 60s
[ ] Handler: invoke_lambda.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../invoke_lambda.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
