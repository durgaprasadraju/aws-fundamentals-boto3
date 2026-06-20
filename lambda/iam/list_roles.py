"""
List IAM roles using Boto3.

Environment variables:
    AWS_REGION   - AWS region (default: us-east-1)
    PATH_PREFIX  - IAM path prefix filter (default: /)
    MAX_ITEMS    - Maximum roles to return (default: 50)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
PATH_PREFIX = os.environ.get("PATH_PREFIX", "/")
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "50"))

EXAMPLE_EVENT: Dict[str, Any] = {
    "path_prefix": "/",
    "max_items": 20,
}


def list_roles(path_prefix: str = "/", max_items: int = 50) -> List[Dict[str, Any]]:
    """Return IAM role summaries."""
    iam = boto3.client("iam", region_name=AWS_REGION)
    roles: List[Dict[str, Any]] = []
    try:
        paginator = iam.get_paginator("list_roles")
        for page in paginator.paginate(PathPrefix=path_prefix, PaginationConfig={"MaxItems": max_items}):
            for role in page.get("Roles", []):
                roles.append(
                    {
                        "role_name": role["RoleName"],
                        "role_arn": role["Arn"],
                        "create_date": role["CreateDate"].isoformat(),
                        "description": role.get("Description", ""),
                    }
                )
        logger.info("Listed %d IAM roles", len(roles))
        return roles
    except ClientError as exc:
        logger.error("list_roles failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    path_prefix = event.get("path_prefix", PATH_PREFIX)
    max_items = int(event.get("max_items", MAX_ITEMS))

    try:
        roles = list_roles(path_prefix, max_items)
        return {"statusCode": 200, "body": json.dumps({"count": len(roles), "roles": roles})}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
