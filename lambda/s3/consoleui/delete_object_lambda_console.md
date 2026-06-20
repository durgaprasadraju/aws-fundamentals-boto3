# Deploy `delete_object.py` in AWS Lambda (Console UI)

Step-by-step guide to run `delete_object.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Object exists in bucket.

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
        "s3:CreateBucket",
        "s3:PutPublicAccessBlock",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-lambda-lab-bucket-*",
        "arn:aws:s3:::my-lambda-lab-bucket-*/*"
      ]
    }
  ]
}
```

4. **Role name:** `lab-s3-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-s3-delete-object` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-s3-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `delete_object.py`
2. **Runtime settings** → **Handler:** `delete_object.lambda_handler`
3. Click **Deploy**

> Boto3 is included in the Lambda Python runtime — no zip needed for this lab.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `AWS_REGION` | `us-east-1` |
| `BUCKET_NAME` | Your bucket name |

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
2. **Event name:** `DeleteObjectTest`
3. **Event JSON:**

```json
{
  "bucket_name": "my-lambda-lab-bucket-UNIQUE123",
  "object_key": "uploads/hello.txt"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Object deleted successfully\", \"deleted\": true}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `NoSuchKey` | Object not found |

---

## Quick Checklist

```
[ ] Correct object key
[ ] Handler: delete_object.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../delete_object.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
