# Deploy `select_data.py` in AWS Lambda (Console UI)

Step-by-step guide to run `select_data.py` as a Lambda function using the **AWS Console**.

## Prerequisites

1. Rows in `employees` table.

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
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Role name:** `lab-rds-lambda-role` → **Create role**

---

## Step 2: Create Lambda Function (Console)

1. Open **Lambda** → **Create function** → **Author from scratch**
2. Settings:

| Setting | Value |
|--------|--------|
| **Function name** | `lab-rds-select` |
| **Runtime** | Python 3.12 |
| **Architecture** | x86_64 |
| **Execution role** | `lab-rds-lambda-role` |

3. Click **Create function**

---

## Step 3: Paste Code

1. **Code** tab → paste full contents of `select_data.py`
2. **Runtime settings** → **Handler:** `select_data.lambda_handler`
3. Click **Deploy**

> Add **mysql-connector-python** via Lambda layer or deployment zip. Configure Lambda **VPC** with security group allowing port 3306 to RDS.

---

## Step 4: Environment Variables

**Configuration** → **Environment variables** → **Edit**

| Key | Value |
|-----|--------|
| `DB_HOST` | RDS endpoint |
| `DB_USER` | admin |
| `DB_PASSWORD` | Your password |
| `DB_PORT` | `3306` |
| `DB_NAME` | `lab_db` |

---

## Step 5: General Configuration

**Configuration** → **General configuration** → **Edit**

| Setting | Value |
|--------|--------|
| **Timeout** | `60` seconds |
| **Memory** | `128` MB |

**VPC:** Configuration → VPC → select subnets + security group with RDS access.

---

## Step 6: Test in Console

1. **Test** tab → **Create new event**
2. **Event name:** `SelectDataTest`
3. **Event JSON:**

```json
{
  "table_name": "employees",
  "limit": 10
}
```

4. Click **Test**

---

## Expected Success Response

```json
{
  "statusCode": 200,
  "body": "{\"count\": 1, \"rows\": []}"
}
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `Connection error` | Check VPC and credentials |

---

## Quick Checklist

```
[ ] Data inserted
[ ] Handler: select_data.lambda_handler
```

---

## Related Files

| File | Purpose |
|------|---------|
| `../select_data.py` | Lambda handler source code |
| `../README.md` | Module overview and CLI deployment |
