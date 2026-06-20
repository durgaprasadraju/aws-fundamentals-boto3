"""
Put an item into Amazon DynamoDB using boto3.

Lab: AWS Fundamentals with Boto3 — DynamoDB
"""

import json
import logging
import os
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
TABLE_NAME = os.environ.get("TABLE_NAME", "LabUsers")


def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=AWS_REGION)


def put_item(table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or replace an item in DynamoDB."""
    table = get_dynamodb_resource().Table(table_name)
    table.put_item(Item=item)

    logger.info("Put item user_id=%s into table %s", item.get("user_id"), table_name)
    return {"table_name": table_name, "item": item}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - table_name (optional): defaults to TABLE_NAME env var
      - item (required): dict with at least user_id (String)
    """
    try:
        table_name = event.get("table_name") or TABLE_NAME
        item = event.get("item")

        if not table_name:
            raise ValueError("table_name is required (event or TABLE_NAME env var)")
        if not item or not isinstance(item, dict):
            raise ValueError("item is required and must be a dict")
        if not item.get("user_id"):
            raise ValueError("item.user_id is required (partition key)")

        result = put_item(table_name, item)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Item put successfully", **result}, default=str),
        }
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        return {"statusCode": 400, "body": json.dumps({"error": str(exc)})}
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "Unknown")
        logger.error("AWS ClientError [%s]: %s", error_code, exc)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc), "error_code": error_code}),
        }
    except Exception as exc:
        logger.exception("Unexpected error")
        return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}


EXAMPLE_EVENT = {
    "table_name": "LabUsers",
    "item": {
        "user_id": "user-001",
        "name": "Alice",
        "email": "alice@example.com",
        "role": "admin",
    },
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
