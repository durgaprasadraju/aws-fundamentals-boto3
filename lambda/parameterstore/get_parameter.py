"""
Retrieve a parameter from AWS Systems Manager Parameter Store using Boto3.

Environment variables:
    AWS_REGION      - AWS region (default: us-east-1)
    PARAMETER_NAME  - Parameter name (optional)
    WITH_DECRYPTION - Decrypt SecureString if "true" (default: true)
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
WITH_DECRYPTION = os.environ.get("WITH_DECRYPTION", "true").lower() == "true"

EXAMPLE_EVENT: Dict[str, Any] = {
    "parameter_name": "/boto3-learning/app/config",
    "with_decryption": True,
}


def get_parameter(parameter_name: str, with_decryption: bool = True) -> Dict[str, Any]:
    """Fetch a single parameter value from Parameter Store."""
    ssm = boto3.client("ssm", region_name=AWS_REGION)
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=with_decryption)
        param = response["Parameter"]
        logger.info("Retrieved parameter: %s", parameter_name)
        return {
            "parameter_name": param["Name"],
            "value": param["Value"],
            "type": param["Type"],
            "version": param["Version"],
            "last_modified": param["LastModifiedDate"].isoformat(),
        }
    except ClientError as exc:
        logger.error("get_parameter failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    parameter_name = event.get("parameter_name") or PARAMETER_NAME
    with_decryption = bool(event.get("with_decryption", WITH_DECRYPTION))

    if not parameter_name:
        return {"statusCode": 400, "body": json.dumps({"error": "parameter_name is required"})}

    try:
        result = get_parameter(parameter_name, with_decryption)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
