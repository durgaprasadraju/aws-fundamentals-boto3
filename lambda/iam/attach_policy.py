"""
Attach a managed or inline IAM policy to a role using Boto3.

Environment variables:
    AWS_REGION    - AWS region (default: us-east-1)
    ROLE_NAME     - Target IAM role name (optional)
    POLICY_ARN    - Managed policy ARN to attach (optional)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
ROLE_NAME = os.environ.get("ROLE_NAME", "")
POLICY_ARN = os.environ.get("POLICY_ARN", "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")

EXAMPLE_EVENT: Dict[str, Any] = {
    "role_name": "boto3-learning-lambda-role",
    "policy_arn": "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
}


def attach_managed_policy(role_name: str, policy_arn: str) -> Dict[str, Any]:
    """Attach an AWS managed policy to an IAM role."""
    iam = boto3.client("iam", region_name=AWS_REGION)
    try:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        logger.info("Attached policy %s to role %s", policy_arn, role_name)
        return {"role_name": role_name, "policy_arn": policy_arn, "attached": True}
    except ClientError as exc:
        logger.error("attach_role_policy failed: %s", exc)
        raise


def put_inline_policy(role_name: str, policy_name: str, policy_document: Dict[str, Any]) -> Dict[str, Any]:
    """Attach an inline policy document to an IAM role."""
    iam = boto3.client("iam", region_name=AWS_REGION)
    try:
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
        )
        logger.info("Put inline policy %s on role %s", policy_name, role_name)
        return {"role_name": role_name, "policy_name": policy_name, "inline": True}
    except ClientError as exc:
        logger.error("put_role_policy failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    role_name = event.get("role_name") or ROLE_NAME
    policy_arn: Optional[str] = event.get("policy_arn") or POLICY_ARN
    inline_policy = event.get("inline_policy")
    inline_policy_name = event.get("inline_policy_name", "boto3-inline-policy")

    if not role_name:
        return {"statusCode": 400, "body": json.dumps({"error": "role_name is required"})}

    try:
        if inline_policy:
            result = put_inline_policy(role_name, inline_policy_name, inline_policy)
        elif policy_arn:
            result = attach_managed_policy(role_name, policy_arn)
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "policy_arn or inline_policy required"})}
        return {"statusCode": 200, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
