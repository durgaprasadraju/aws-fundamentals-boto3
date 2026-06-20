"""
Create an IAM role for AWS Lambda using Boto3.

Environment variables:
    AWS_REGION          - AWS region (default: us-east-1)
    ROLE_NAME           - Default role name (optional)
    LAMBDA_TRUST_POLICY - Set to "true" to use Lambda trust policy (default)
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
ROLE_NAME = os.environ.get("ROLE_NAME", "")

LAMBDA_ASSUME_ROLE_POLICY: Dict[str, Any] = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}

EXAMPLE_EVENT: Dict[str, Any] = {
    "role_name": "boto3-learning-lambda-role",
    "description": "IAM role created by aws-fundamentals-boto3 lab",
    "trust_policy": LAMBDA_ASSUME_ROLE_POLICY,
}


def create_role(
    role_name: str,
    trust_policy: Dict[str, Any],
    description: str = "",
) -> Dict[str, Any]:
    """Create an IAM role with the given trust policy."""
    iam = boto3.client("iam", region_name=AWS_REGION)
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description or f"Role {role_name} created via Boto3",
        )
        role = response["Role"]
        logger.info("Created IAM role: %s", role_name)
        return {
            "role_name": role["RoleName"],
            "role_arn": role["Arn"],
            "create_date": role["CreateDate"].isoformat(),
        }
    except ClientError as exc:
        logger.error("create_role failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    role_name = event.get("role_name") or ROLE_NAME
    description = event.get("description", "")
    trust_policy = event.get("trust_policy", LAMBDA_ASSUME_ROLE_POLICY)

    if not role_name:
        return {"statusCode": 400, "body": json.dumps({"error": "role_name is required"})}

    try:
        result = create_role(role_name, trust_policy, description)
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
