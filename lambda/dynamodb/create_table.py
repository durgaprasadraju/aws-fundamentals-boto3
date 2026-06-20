"""
Create an Amazon DynamoDB table using boto3.

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


def get_dynamodb_client():
    return boto3.client("dynamodb", region_name=AWS_REGION)


def create_table(table_name: str, billing_mode: str = "PAY_PER_REQUEST") -> Dict[str, Any]:
    """Create a DynamoDB table with a partition key `user_id` (String)."""
    client = get_dynamodb_client()

    params: Dict[str, Any] = {
        "TableName": table_name,
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "user_id", "AttributeType": "S"}],
        "BillingMode": billing_mode,
        "Tags": [{"Key": "Project", "Value": "aws-fundamentals-boto3"}],
    }

    response = client.create_table(**params)
    table_desc = response["TableDescription"]

    logger.info("Created table %s (status: %s)", table_name, table_desc["TableStatus"])
    return {
        "table_name": table_name,
        "table_arn": table_desc["TableArn"],
        "table_status": table_desc["TableStatus"],
        "billing_mode": billing_mode,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - table_name (optional): defaults to TABLE_NAME env var
      - billing_mode (optional): PAY_PER_REQUEST or PROVISIONED (default: PAY_PER_REQUEST)
    """
    try:
        table_name = event.get("table_name") or TABLE_NAME
        billing_mode = event.get("billing_mode", "PAY_PER_REQUEST")

        if not table_name:
            raise ValueError("table_name is required (event or TABLE_NAME env var)")

        result = create_table(table_name, billing_mode)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Table created successfully", **result}),
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
    "billing_mode": "PAY_PER_REQUEST",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
