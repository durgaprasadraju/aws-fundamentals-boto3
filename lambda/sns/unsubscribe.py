"""
Unsubscribe from an Amazon SNS topic.

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
SUBSCRIPTION_ARN = os.environ.get("SUBSCRIPTION_ARN", "")


def get_sns_client():
    return boto3.client("sns", region_name=AWS_REGION)


def unsubscribe(subscription_arn: str) -> Dict[str, Any]:
    """Remove an SNS subscription by ARN."""
    client = get_sns_client()
    client.unsubscribe(SubscriptionArn=subscription_arn)
    logger.info("Unsubscribed %s", subscription_arn)
    return {"subscription_arn": subscription_arn, "unsubscribed": True}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        subscription_arn = event.get("subscription_arn") or SUBSCRIPTION_ARN
        if not subscription_arn:
            raise ValueError("subscription_arn is required (event or SUBSCRIPTION_ARN env var)")

        result = unsubscribe(subscription_arn)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Subscription removed successfully", **result}),
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
    "subscription_arn": "arn:aws:sns:us-east-1:123456789012:lab-notifications:abc123",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
