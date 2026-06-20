"""
Delete a secret from AWS Secrets Manager using Boto3.

Environment variables:
    AWS_REGION              - AWS region (default: us-east-1)
    SECRET_NAME             - Secret name or ARN (optional)
    FORCE_DELETE            - Skip recovery window if "true" (default: false)
    RECOVERY_WINDOW_DAYS    - Days before permanent delete (default: 7)
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
FORCE_DELETE = os.environ.get("FORCE_DELETE", "false").lower() == "true"
RECOVERY_WINDOW_DAYS = int(os.environ.get("RECOVERY_WINDOW_DAYS", "7"))

EXAMPLE_EVENT: Dict[str, Any] = {
    "secret_name": "boto3-learning/db-credentials",
    "force_delete": False,
    "recovery_window_days": 7,
}


def delete_secret(
    secret_name: str,
    force_delete: bool = False,
    recovery_window_days: int = 7,
) -> Dict[str, Any]:
    """Schedule or immediately delete a secret."""
    client = boto3.client("secretsmanager", region_name=AWS_REGION)
    try:
        if force_delete:
            response = client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
        else:
            response = client.delete_secret(
                SecretId=secret_name,
                RecoveryWindowInDays=recovery_window_days,
            )
        logger.info("Deleted secret: %s (force=%s)", secret_name, force_delete)
        return {
            "secret_name": secret_name,
            "secret_arn": response.get("ARN"),
            "deletion_date": response.get("DeletionDate", "").isoformat() if response.get("DeletionDate") else None,
            "force_delete": force_delete,
        }
    except ClientError as exc:
        logger.error("delete_secret failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    secret_name = event.get("secret_name") or SECRET_NAME
    force_delete = bool(event.get("force_delete", FORCE_DELETE))
    recovery_window_days = int(event.get("recovery_window_days", RECOVERY_WINDOW_DAYS))

    if not secret_name:
        return {"statusCode": 400, "body": json.dumps({"error": "secret_name is required"})}

    try:
        result = delete_secret(secret_name, force_delete, recovery_window_days)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
