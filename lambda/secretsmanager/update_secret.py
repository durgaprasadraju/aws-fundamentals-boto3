"""
Update a secret in AWS Secrets Manager using Boto3.

Environment variables:
    AWS_REGION    - AWS region (default: us-east-1)
    SECRET_NAME   - Secret name or ARN (optional)
    SECRET_VALUE  - New secret value (optional)
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
SECRET_VALUE = os.environ.get("SECRET_VALUE", "")

EXAMPLE_EVENT: Dict[str, Any] = {
    "secret_name": "boto3-learning/db-credentials",
    "secret_string": json.dumps({"username": "admin", "password": "NewSecurePass456!"}),
}


def update_secret(secret_name: str, secret_string: str) -> Dict[str, Any]:
    """Update the secret value and create a new version."""
    client = boto3.client("secretsmanager", region_name=AWS_REGION)
    try:
        response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=secret_string,
        )
        logger.info("Updated secret: %s", secret_name)
        return {
            "secret_name": secret_name,
            "secret_arn": response.get("ARN"),
            "version_id": response["VersionId"],
            "updated": True,
        }
    except ClientError as exc:
        logger.error("put_secret_value failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    secret_name = event.get("secret_name") or SECRET_NAME
    secret_string = event.get("secret_string") or SECRET_VALUE

    if not secret_name or not secret_string:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "secret_name and secret_string are required"}),
        }

    try:
        result = update_secret(secret_name, secret_string)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
