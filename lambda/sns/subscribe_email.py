"""
Subscribe an email address to an Amazon SNS topic.

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
EMAIL = os.environ.get("EMAIL", "")


def get_sns_client():
    return boto3.client("sns", region_name=AWS_REGION)


def subscribe_email(topic_arn: str, email: str) -> Dict[str, Any]:
    """Create an email subscription; recipient must confirm via email."""
    client = get_sns_client()
    response = client.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint=email)
    subscription_arn = response["SubscriptionArn"]
    logger.info("Subscribed %s to %s (status=%s)", email, topic_arn, subscription_arn)
    return {
        "topic_arn": topic_arn,
        "email": email,
        "subscription_arn": subscription_arn,
        "pending_confirmation": subscription_arn == "pending confirmation",
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        topic_arn = event.get("topic_arn") or TOPIC_ARN
        email = event.get("email") or EMAIL

        if not topic_arn:
            raise ValueError("topic_arn is required (event or TOPIC_ARN env var)")
        if not email:
            raise ValueError("email is required (event or EMAIL env var)")

        result = subscribe_email(topic_arn, email)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email subscription created", **result}),
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
    "email": "you@example.com",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
