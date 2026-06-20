"""
Publish a message to an Amazon SNS topic.

Lab: AWS Fundamentals with Boto3 — SNS
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
TOPIC_ARN = os.environ.get("TOPIC_ARN", "")


def get_sns_client():
    return boto3.client("sns", region_name=AWS_REGION)


def publish_message(topic_arn: str, message: str, subject: str) -> Dict[str, Any]:
    """Publish a text message to an SNS topic."""
    client = get_sns_client()
    response = client.publish(TopicArn=topic_arn, Message=message, Subject=subject)
    message_id = response["MessageId"]
    logger.info("Published message %s to %s", message_id, topic_arn)
    return {"topic_arn": topic_arn, "message_id": message_id, "subject": subject}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        topic_arn = event.get("topic_arn") or TOPIC_ARN
        message = event.get("message", "Hello from Lambda SNS lab!")
        subject = event.get("subject", "Lambda SNS Notification")

        if not topic_arn:
            raise ValueError("topic_arn is required (event or TOPIC_ARN env var)")

        result = publish_message(topic_arn, message, subject)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "SNS message published successfully", **result}),
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
    "topic_arn": "arn:aws:sns:us-east-1:123456789012:lab-notifications",
    "message": "Order ORD-001 has shipped.",
    "subject": "Order Shipped",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
