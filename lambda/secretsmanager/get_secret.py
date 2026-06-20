"""
Retrieve a secret from AWS Secrets Manager using Boto3.

Environment variables:
    AWS_REGION   - AWS region (default: us-east-1)
    SECRET_NAME  - Secret name or ARN (optional)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SECRET_NAME = os.environ.get("SECRET_NAME", "")

EXAMPLE_EVENT: Dict[str, Any] = {
    "secret_name": "boto3-learning/db-credentials",
}


def get_secret(secret_name: str) -> Dict[str, Any]:
    """Fetch the current secret value from Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=AWS_REGION)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString", "")
        logger.info("Retrieved secret: %s", secret_name)

        parsed: Any = secret_string
        try:
            parsed = json.loads(secret_string)
        except (json.JSONDecodeError, TypeError):
            pass

        return {
            "secret_name": secret_name,
            "secret_arn": response.get("ARN"),
            "version_id": response.get("VersionId"),
            "value": parsed,
        }
    except ClientError as exc:
        logger.error("get_secret_value failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    secret_name = event.get("secret_name") or SECRET_NAME

    if not secret_name:
        return {"statusCode": 400, "body": json.dumps({"error": "secret_name is required"})}

    try:
        result = get_secret(secret_name)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
