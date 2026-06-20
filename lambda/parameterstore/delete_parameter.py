"""
Delete a parameter from AWS Systems Manager Parameter Store using Boto3.

Environment variables:
    AWS_REGION     - AWS region (default: us-east-1)
    PARAMETER_NAME - Parameter name (optional)
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
PARAMETER_NAME = os.environ.get("PARAMETER_NAME", "")

EXAMPLE_EVENT: Dict[str, Any] = {
    "parameter_name": "/boto3-learning/app/config",
}


def delete_parameter(parameter_name: str) -> Dict[str, Any]:
    """Delete a parameter from SSM Parameter Store."""
    ssm = boto3.client("ssm", region_name=AWS_REGION)
    try:
        ssm.delete_parameter(Name=parameter_name)
        logger.info("Deleted parameter: %s", parameter_name)
        return {"parameter_name": parameter_name, "deleted": True}
    except ClientError as exc:
        logger.error("delete_parameter failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    parameter_name = event.get("parameter_name") or PARAMETER_NAME

    if not parameter_name:
        return {"statusCode": 400, "body": json.dumps({"error": "parameter_name is required"})}

    try:
        result = delete_parameter(parameter_name)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
