"""
Send a message to an Amazon SQS queue.

Lab: AWS Fundamentals with Boto3 — SQS
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
QUEUE_URL = os.environ.get("QUEUE_URL", "")


def get_sqs_client():
    return boto3.client("sqs", region_name=AWS_REGION)


def send_message(queue_url: str, message_body: str, delay_seconds: int = 0) -> Dict[str, Any]:
    """Send a message to an SQS standard queue."""
    client = get_sqs_client()
    params: Dict[str, Any] = {
        "QueueUrl": queue_url,
        "MessageBody": message_body,
    }
    if delay_seconds > 0:
        params["DelaySeconds"] = delay_seconds

    response = client.send_message(**params)
    message_id = response["MessageId"]
    logger.info("Sent message %s to %s", message_id, queue_url)
    return {
        "queue_url": queue_url,
        "message_id": message_id,
        "md5_of_message_body": response.get("MD5OfMessageBody"),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        queue_url = event.get("queue_url") or QUEUE_URL
        message_body = event.get("message_body")
        delay_seconds = int(event.get("delay_seconds", 0))

        if not queue_url:
            raise ValueError("queue_url is required (event or QUEUE_URL env var)")
        if not message_body:
            raise ValueError("message_body is required")

        result = send_message(queue_url, message_body, delay_seconds)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "SQS message sent successfully", **result}),
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
    "message_body": json.dumps({"order_id": "ORD-001", "action": "process"}),
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
