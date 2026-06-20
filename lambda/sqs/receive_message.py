"""
Receive messages from an Amazon SQS queue.

Lab: AWS Fundamentals with Boto3 — SQS
"""

import json
import logging
import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
QUEUE_URL = os.environ.get("QUEUE_URL", "")


def get_sqs_client():
    return boto3.client("sqs", region_name=AWS_REGION)


def receive_messages(
    queue_url: str,
    max_messages: int = 1,
    wait_time_seconds: int = 0,
    visibility_timeout: int = 30,
) -> List[Dict[str, Any]]:
    """Receive up to max_messages from the queue."""
    client = get_sqs_client()
    response = client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max(1, min(max_messages, 10)),
        WaitTimeSeconds=max(0, min(wait_time_seconds, 20)),
        VisibilityTimeout=visibility_timeout,
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
    )
    messages = []
    for item in response.get("Messages", []):
        messages.append(
            {
                "message_id": item["MessageId"],
                "receipt_handle": item["ReceiptHandle"],
                "body": item["Body"],
                "attributes": item.get("Attributes", {}),
            }
        )
    logger.info("Received %d message(s) from %s", len(messages), queue_url)
    return messages


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        queue_url = event.get("queue_url") or QUEUE_URL
        max_messages = int(event.get("max_messages", 1))
        wait_time_seconds = int(event.get("wait_time_seconds", 0))
        visibility_timeout = int(event.get("visibility_timeout", 30))

        if not queue_url:
            raise ValueError("queue_url is required (event or QUEUE_URL env var)")

        messages = receive_messages(queue_url, max_messages, wait_time_seconds, visibility_timeout)
        return {
            "statusCode": 200,
            "body": json.dumps({"count": len(messages), "messages": messages}),
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
    "max_messages": 5,
    "wait_time_seconds": 2,
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
