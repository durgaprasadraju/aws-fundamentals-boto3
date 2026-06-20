"""
Delete an item from Amazon DynamoDB using boto3.

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


def delete_item(table_name: str, user_id: str) -> Dict[str, Any]:
    """Delete a single item by partition key."""
    table = get_dynamodb_resource().Table(table_name)
    response = table.delete_item(
        Key={"user_id": user_id},
        ReturnValues="ALL_OLD",
    )

    deleted_item = response.get("Attributes")
    logger.info("Deleted item user_id=%s from table %s (existed=%s)", user_id, table_name, deleted_item is not None)
    return {
        "table_name": table_name,
        "user_id": user_id,
        "deleted": deleted_item is not None,
        "previous_item": deleted_item,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - table_name (optional): defaults to TABLE_NAME env var
      - user_id (required): partition key value
    """
    try:
        table_name = event.get("table_name") or TABLE_NAME
        user_id = event.get("user_id")

        if not table_name:
            raise ValueError("table_name is required (event or TABLE_NAME env var)")
        if not user_id:
            raise ValueError("user_id is required")

        result = delete_item(table_name, user_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Delete completed", **result}, default=str),
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
    "user_id": "user-001",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
