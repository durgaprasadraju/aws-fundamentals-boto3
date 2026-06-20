"""
Send log events to Amazon CloudWatch Logs.

Lab: AWS Fundamentals with Boto3 — CloudWatch
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
LOG_GROUP_NAME = os.environ.get("LOG_GROUP_NAME", "/aws/lambda/lab-app")
LOG_STREAM_NAME = os.environ.get("LOG_STREAM_NAME", "lab-stream")


def get_logs_client():
    return boto3.client("logs", region_name=AWS_REGION)


def ensure_log_group_and_stream(log_group_name: str, log_stream_name: str) -> None:
    """Create log group and stream if they do not exist."""
    client = get_logs_client()
    try:
        client.create_log_group(logGroupName=log_group_name)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ResourceAlreadyExistsException":
            raise
    try:
        client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ResourceAlreadyExistsException":
            raise


def get_sequence_token(log_group_name: str, log_stream_name: str) -> Optional[str]:
    client = get_logs_client()
    response = client.describe_log_streams(
        logGroupName=log_group_name,
        logStreamNamePrefix=log_stream_name,
        limit=1,
    )
    streams = response.get("logStreams", [])
    if not streams:
        return None
    return streams[0].get("uploadSequenceToken")


def send_logs(log_group_name: str, log_stream_name: str, message: str) -> Dict[str, Any]:
    """Write one log event to CloudWatch Logs."""
    ensure_log_group_and_stream(log_group_name, log_stream_name)
    client = get_logs_client()
    params: Dict[str, Any] = {
        "logGroupName": log_group_name,
        "logStreamName": log_stream_name,
        "logEvents": [
            {
                "timestamp": int(time.time() * 1000),
                "message": message,
            }
        ],
    }
    sequence_token = get_sequence_token(log_group_name, log_stream_name)
    if sequence_token:
        params["sequenceToken"] = sequence_token

    response = client.put_log_events(**params)
    logger.info("Sent log event to %s:%s", log_group_name, log_stream_name)
    return {
        "log_group_name": log_group_name,
        "log_stream_name": log_stream_name,
        "next_sequence_token": response.get("nextSequenceToken"),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        log_group_name = event.get("log_group_name", LOG_GROUP_NAME)
        log_stream_name = event.get("log_stream_name", LOG_STREAM_NAME)
        message = event.get("message", "Lab log event from Lambda")

        if not log_group_name or not log_stream_name:
            raise ValueError("log_group_name and log_stream_name are required")

        result = send_logs(log_group_name, log_stream_name, message)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Log event sent successfully", **result}),
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
    "log_group_name": "/aws/lambda/lab-app",
    "log_stream_name": "lab-stream",
    "message": "Order ORD-001 processed successfully",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
