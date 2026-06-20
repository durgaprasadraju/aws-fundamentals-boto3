"""
Create an Amazon S3 bucket using boto3.

Lab: AWS Fundamentals with Boto3 — S3
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
BUCKET_NAME = os.environ.get("BUCKET_NAME", "")


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def create_bucket(bucket_name: str, region: str) -> Dict[str, Any]:
    """Create an S3 bucket in the specified region."""
    client = get_s3_client()

    if region == "us-east-1":
        client.create_bucket(Bucket=bucket_name)
    else:
        client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )

    client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )

    logger.info("Created bucket %s in %s", bucket_name, region)
    return {"bucket_name": bucket_name, "region": region}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - bucket_name (optional): defaults to BUCKET_NAME env var
      - region (optional): defaults to AWS_REGION env var
    """
    try:
        bucket_name = event.get("bucket_name") or BUCKET_NAME
        region = event.get("region") or AWS_REGION

        if not bucket_name:
            raise ValueError("bucket_name is required (event or BUCKET_NAME env var)")

        result = create_bucket(bucket_name, region)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Bucket created successfully", **result}),
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
    "bucket_name": "my-lambda-lab-bucket-12345",
    "region": "us-east-1",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
