"""
List objects in an Amazon S3 bucket using boto3.

Lab: AWS Fundamentals with Boto3 — S3
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
BUCKET_NAME = os.environ.get("BUCKET_NAME", "")
PREFIX = os.environ.get("PREFIX", "")


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def list_objects(bucket_name: str, prefix: Optional[str] = None, max_keys: int = 100) -> Dict[str, Any]:
    """List objects in a bucket with optional prefix filter."""
    client = get_s3_client()
    params: Dict[str, Any] = {"Bucket": bucket_name, "MaxKeys": max_keys}
    if prefix:
        params["Prefix"] = prefix

    response = client.list_objects_v2(**params)
    contents = response.get("Contents", [])
    objects: List[Dict[str, Any]] = [
        {
            "key": item["Key"],
            "size_bytes": item["Size"],
            "last_modified": item["LastModified"].isoformat(),
        }
        for item in contents
    ]

    logger.info("Listed %d objects in s3://%s (prefix=%r)", len(objects), bucket_name, prefix or "")
    return {
        "bucket_name": bucket_name,
        "prefix": prefix or "",
        "count": len(objects),
        "is_truncated": response.get("IsTruncated", False),
        "objects": objects,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - bucket_name (optional): defaults to BUCKET_NAME env var
      - prefix (optional): key prefix filter
      - max_keys (optional): max results (default 100)
    """
    try:
        bucket_name = event.get("bucket_name") or BUCKET_NAME
        prefix = event.get("prefix", PREFIX) or None
        max_keys = int(event.get("max_keys", 100))

        if not bucket_name:
            raise ValueError("bucket_name is required (event or BUCKET_NAME env var)")

        result = list_objects(bucket_name, prefix, max_keys)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Objects listed successfully", **result}, default=str),
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
    "prefix": "uploads/",
    "max_keys": 50,
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
