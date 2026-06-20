# Deploy `upload_file.py` in AWS Lambda (Console UI)

Step-by-step guide to run `upload_file.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. S3 bucket exists.

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
| **Function name** | `lab-s3-upload-file` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-s3-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `upload_file.py`
2. **Runtime settings** → **Handler:** `upload_file.lambda_handler`
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
2. **Event name:** `UploadFileTest`
3. **Event JSON:**

```json
{
  "bucket_name": "my-lambda-lab-bucket-UNIQUE123",
  "object_key": "uploads/hello.txt",
  "body": "Hello from Lambda S3 lab!",
  "content_type": "text/plain"
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Object uploaded successfully\", \"object_key\": \"uploads/hello.txt\"}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `NoSuchBucket` | Create bucket first |

---

## Quick Checklist

```
[ ] Bucket exists
[ ] Handler: upload_file.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../upload_file.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
