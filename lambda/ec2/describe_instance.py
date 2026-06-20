"""
Describe Amazon EC2 instances using boto3.

Lab: AWS Fundamentals with Boto3 — EC2
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
INSTANCE_ID = os.environ.get("INSTANCE_ID", "")


def get_ec2_client():
    return boto3.client("ec2", region_name=AWS_REGION)


def describe_instances(instance_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Describe EC2 instances, optionally filtered by instance IDs."""
    client = get_ec2_client()
    params: Dict[str, Any] = {}
    if instance_ids:
        params["InstanceIds"] = instance_ids

    response = client.describe_instances(**params)
    instances: List[Dict[str, Any]] = []

    for reservation in response.get("Reservations", []):
        for inst in reservation.get("Instances", []):
            instances.append(
                {
                    "instance_id": inst["InstanceId"],
                    "instance_type": inst["InstanceType"],
                    "state": inst["State"]["Name"],
                    "public_ip": inst.get("PublicIpAddress"),
                    "private_ip": inst.get("PrivateIpAddress"),
                    "ami_id": inst.get("ImageId"),
                    "launch_time": inst.get("LaunchTime", "").isoformat() if inst.get("LaunchTime") else None,
                    "tags": {t["Key"]: t["Value"] for t in inst.get("Tags", [])},
                }
            )

    logger.info("Described %d instance(s)", len(instances))
    return {"count": len(instances), "instances": instances}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - instance_id (optional): single ID or comma-separated list
      - instance_ids (optional): list of instance IDs
    """
    try:
        instance_ids: Optional[List[str]] = None

        if event.get("instance_ids"):
            instance_ids = event["instance_ids"]
        elif event.get("instance_id") or INSTANCE_ID:
            raw = event.get("instance_id") or INSTANCE_ID
            instance_ids = [i.strip() for i in raw.split(",") if i.strip()]

        result = describe_instances(instance_ids)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Instances described successfully", **result}, default=str),
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
