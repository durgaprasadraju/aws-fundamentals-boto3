"""
Upload an object to Amazon S3 using boto3.

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
OBJECT_KEY = os.environ.get("OBJECT_KEY", "uploads/sample.txt")


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def upload_object(bucket_name: str, object_key: str, body: str, content_type: str) -> Dict[str, Any]:
    """Upload string content to S3."""
    client = get_s3_client()
    client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=body.encode("utf-8"),
        ContentType=content_type,
    )
    logger.info("Uploaded s3://%s/%s (%d bytes)", bucket_name, object_key, len(body))
    return {
        "bucket_name": bucket_name,
        "object_key": object_key,
        "size_bytes": len(body),
        "content_type": content_type,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - bucket_name (optional): defaults to BUCKET_NAME env var
      - object_key (optional): defaults to OBJECT_KEY env var
      - body (optional): string content to upload
      - content_type (optional): MIME type (default: text/plain)
    """
    try:
        bucket_name = event.get("bucket_name") or BUCKET_NAME
        object_key = event.get("object_key") or OBJECT_KEY
        body = event.get("body", "Hello from Lambda S3 lab!")
        content_type = event.get("content_type", "text/plain")

        if not bucket_name:
            raise ValueError("bucket_name is required (event or BUCKET_NAME env var)")
        if not object_key:
            raise ValueError("object_key is required (event or OBJECT_KEY env var)")

        result = upload_object(bucket_name, object_key, body, content_type)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Object uploaded successfully", **result}),
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
    "body": "Hello from Lambda S3 lab!",
    "content_type": "text/plain",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
