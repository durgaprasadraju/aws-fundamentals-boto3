"""
Terminate an Amazon EC2 instance using boto3.

Lab: AWS Fundamentals with Boto3 — EC2
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
INSTANCE_ID = os.environ.get("INSTANCE_ID", "")


def get_ec2_client():
    return boto3.client("ec2", region_name=AWS_REGION)


def terminate_instance(instance_id: str) -> Dict[str, Any]:
    """Permanently terminate an EC2 instance."""
    client = get_ec2_client()
    response = client.terminate_instances(InstanceIds=[instance_id])
    state_change = response["TerminatingInstances"][0]

    logger.info("Terminating instance %s (previous state: %s)", instance_id, state_change["PreviousState"]["Name"])
    return {
        "instance_id": instance_id,
        "previous_state": state_change["PreviousState"]["Name"],
        "current_state": state_change["CurrentState"]["Name"],
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - instance_id (optional): defaults to INSTANCE_ID env var
    """
    try:
        instance_id = event.get("instance_id") or INSTANCE_ID

        if not instance_id:
            raise ValueError("instance_id is required (event or INSTANCE_ID env var)")

        result = terminate_instance(instance_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Terminate initiated successfully", **result}),
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
    "instance_id": "i-0123456789abcdef0",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
