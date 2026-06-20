"""
Launch an Amazon EC2 instance using boto3.

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
AMI_ID = os.environ.get("AMI_ID", "")
INSTANCE_TYPE = os.environ.get("INSTANCE_TYPE", "t3.micro")
KEY_NAME = os.environ.get("KEY_NAME", "")
SUBNET_ID = os.environ.get("SUBNET_ID", "")
SECURITY_GROUP_IDS = os.environ.get("SECURITY_GROUP_IDS", "")


def get_ec2_client():
    return boto3.client("ec2", region_name=AWS_REGION)


def create_instance(
    ami_id: str,
    instance_type: str,
    key_name: Optional[str] = None,
    subnet_id: Optional[str] = None,
    security_group_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Run a new EC2 instance with optional networking parameters."""
    client = get_ec2_client()

    params: Dict[str, Any] = {
        "ImageId": ami_id,
        "InstanceType": instance_type,
        "MinCount": 1,
        "MaxCount": 1,
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "aws-fundamentals-boto3-lab"},
                    {"Key": "Project", "Value": "aws-fundamentals-boto3"},
                ],
            }
        ],
    }

    if key_name:
        params["KeyName"] = key_name
    if subnet_id:
        params["SubnetId"] = subnet_id
    if security_group_ids:
        params["SecurityGroupIds"] = security_group_ids

    response = client.run_instances(**params)
    instance = response["Instances"][0]
    instance_id = instance["InstanceId"]

    logger.info("Created instance %s (%s)", instance_id, instance_type)
    return {
        "instance_id": instance_id,
        "instance_type": instance_type,
        "state": instance["State"]["Name"],
        "ami_id": ami_id,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - ami_id (optional): defaults to AMI_ID env var
      - instance_type (optional): defaults to INSTANCE_TYPE env var
      - key_name, subnet_id, security_group_ids (optional)
    """
    try:
        ami_id = event.get("ami_id") or AMI_ID
        instance_type = event.get("instance_type") or INSTANCE_TYPE
        key_name = event.get("key_name") or KEY_NAME or None
        subnet_id = event.get("subnet_id") or SUBNET_ID or None
        sg_ids_raw = event.get("security_group_ids") or SECURITY_GROUP_IDS
        security_group_ids = [s.strip() for s in sg_ids_raw.split(",") if s.strip()] if sg_ids_raw else None

        if not ami_id:
            raise ValueError("ami_id is required (event or AMI_ID env var)")

        result = create_instance(ami_id, instance_type, key_name, subnet_id, security_group_ids)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Instance created successfully", **result}),
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
    "ami_id": "ami-0c55b159cbfafe1f0",
    "instance_type": "t3.micro",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
