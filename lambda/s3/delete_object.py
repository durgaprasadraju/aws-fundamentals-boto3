"""
Delete an object from Amazon S3 using boto3.

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
OBJECT_KEY = os.environ.get("OBJECT_KEY", "")


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def delete_object(bucket_name: str, object_key: str) -> Dict[str, Any]:
    """Delete a single object from S3."""
    client = get_s3_client()
    client.delete_object(Bucket=bucket_name, Key=object_key)
    logger.info("Deleted s3://%s/%s", bucket_name, object_key)
    return {"bucket_name": bucket_name, "object_key": object_key, "deleted": True}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - bucket_name (optional): defaults to BUCKET_NAME env var
      - object_key (required): S3 object key to delete
    """
    try:
        bucket_name = event.get("bucket_name") or BUCKET_NAME
        object_key = event.get("object_key") or OBJECT_KEY

        if not bucket_name:
            raise ValueError("bucket_name is required (event or BUCKET_NAME env var)")
        if not object_key:
            raise ValueError("object_key is required (event or OBJECT_KEY env var)")

        result = delete_object(bucket_name, object_key)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Object deleted successfully", **result}),
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
    "object_key": "uploads/hello.txt",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
