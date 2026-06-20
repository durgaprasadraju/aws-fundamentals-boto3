"""
Delete a message from an Amazon SQS queue.

Lab: AWS Fundamentals with Boto3 — SQS
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
QUEUE_URL = os.environ.get("QUEUE_URL", "")


def get_sqs_client():
    return boto3.client("sqs", region_name=AWS_REGION)


def delete_message(queue_url: str, receipt_handle: str) -> Dict[str, Any]:
    """Delete a message using its receipt handle."""
    client = get_sqs_client()
    client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    logger.info("Deleted message from %s", queue_url)
    return {"queue_url": queue_url, "deleted": True}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        queue_url = event.get("queue_url") or QUEUE_URL
        receipt_handle = event.get("receipt_handle")

        if not queue_url:
            raise ValueError("queue_url is required (event or QUEUE_URL env var)")
        if not receipt_handle:
            raise ValueError("receipt_handle is required")

        result = delete_message(queue_url, receipt_handle)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "SQS message deleted successfully", **result}),
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
    "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/lab-queue",
    "receipt_handle": "AQEBexampleReceiptHandle",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
