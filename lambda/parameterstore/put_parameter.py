"""
Store a parameter in AWS Systems Manager Parameter Store using Boto3.

Environment variables:
    AWS_REGION     - AWS region (default: us-east-1)
    PARAMETER_NAME - Default parameter name (optional)
    PARAMETER_TYPE - String, StringList, or SecureString (default: String)
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
PARAMETER_TYPE = os.environ.get("PARAMETER_TYPE", "String")

EXAMPLE_EVENT: Dict[str, Any] = {
    "parameter_name": "/boto3-learning/app/config",
    "parameter_value": "production",
    "parameter_type": "String",
    "description": "Application environment config",
    "overwrite": True,
}


def put_parameter(
    parameter_name: str,
    parameter_value: str,
    parameter_type: str = "String",
    description: str = "",
    overwrite: bool = True,
) -> Dict[str, Any]:
    """Create or update a parameter in SSM Parameter Store."""
    ssm = boto3.client("ssm", region_name=AWS_REGION)
    try:
        response = ssm.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Type=parameter_type,
            Description=description or f"Parameter {parameter_name}",
            Overwrite=overwrite,
        )
        logger.info("Put parameter: %s (type=%s)", parameter_name, parameter_type)
        return {
            "parameter_name": parameter_name,
            "version": response["Version"],
            "tier": response.get("Tier", "Standard"),
            "type": parameter_type,
        }
    except ClientError as exc:
        logger.error("put_parameter failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    parameter_name = event.get("parameter_name") or PARAMETER_NAME
    parameter_value = event.get("parameter_value")
    parameter_type = event.get("parameter_type", PARAMETER_TYPE)
    description = event.get("description", "")
    overwrite = bool(event.get("overwrite", True))

    if not parameter_name or parameter_value is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "parameter_name and parameter_value are required"}),
        }

    try:
        result = put_parameter(parameter_name, str(parameter_value), parameter_type, description, overwrite)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
