"""
Update an item in Amazon DynamoDB using boto3.

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


def update_item(table_name: str, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update attributes on an existing item using UpdateExpression."""
    if not updates:
        raise ValueError("updates dict must not be empty")

    table = get_dynamodb_resource().Table(table_name)

    expression_parts = []
    expression_values: Dict[str, Any] = {}
    expression_names: Dict[str, str] = {}

    for idx, (key, value) in enumerate(updates.items()):
        placeholder = f"#k{idx}"
        value_placeholder = f":v{idx}"
        expression_parts.append(f"{placeholder} = {value_placeholder}")
        expression_names[placeholder] = key
        expression_values[value_placeholder] = value

    update_expression = "SET " + ", ".join(expression_parts)

    response = table.update_item(
        Key={"user_id": user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    updated_item = response.get("Attributes", {})
    logger.info("Updated item user_id=%s in table %s", user_id, table_name)
    return {"table_name": table_name, "user_id": user_id, "item": updated_item}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - table_name (optional): defaults to TABLE_NAME env var
      - user_id (required): partition key
      - updates (required): dict of attribute names and new values
    """
    try:
        table_name = event.get("table_name") or TABLE_NAME
        user_id = event.get("user_id")
        updates = event.get("updates")

        if not table_name:
            raise ValueError("table_name is required (event or TABLE_NAME env var)")
        if not user_id:
            raise ValueError("user_id is required")
        if not updates or not isinstance(updates, dict):
            raise ValueError("updates is required and must be a non-empty dict")

        result = update_item(table_name, user_id, updates)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Item updated successfully", **result}, default=str),
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
    "updates": {
        "role": "superadmin",
        "last_login": "2026-06-20T10:00:00Z",
    },
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
