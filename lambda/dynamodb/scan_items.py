"""
Scan items in an Amazon DynamoDB table using boto3.

Lab: AWS Fundamentals with Boto3 — DynamoDB
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
TABLE_NAME = os.environ.get("TABLE_NAME", "LabUsers")


def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=AWS_REGION)


def scan_items(
    table_name: str,
    limit: int = 25,
    filter_expression: Optional[str] = None,
    expression_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Scan table items with optional filter (use Query with GSI in production)."""
    table = get_dynamodb_resource().Table(table_name)

    params: Dict[str, Any] = {"Limit": limit}
    if filter_expression:
        params["FilterExpression"] = filter_expression
    if expression_values:
        params["ExpressionAttributeValues"] = expression_values

    response = table.scan(**params)
    items: List[Dict[str, Any]] = response.get("Items", [])

    logger.info("Scanned table %s — returned %d item(s)", table_name, len(items))
    return {
        "table_name": table_name,
        "count": len(items),
        "scanned_count": response.get("ScannedCount", 0),
        "last_evaluated_key": response.get("LastEvaluatedKey"),
        "items": items,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - table_name (optional): defaults to TABLE_NAME env var
      - limit (optional): max items to return (default 25)
      - filter_expression (optional): DynamoDB filter expression
      - expression_values (optional): values for filter expression
    """
    try:
        table_name = event.get("table_name") or TABLE_NAME
        limit = int(event.get("limit", 25))
        filter_expression = event.get("filter_expression")
        expression_values = event.get("expression_values")

        if not table_name:
            raise ValueError("table_name is required (event or TABLE_NAME env var)")

        result = scan_items(table_name, limit, filter_expression, expression_values)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Scan completed successfully", **result}, default=str),
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
    "limit": 10,
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
