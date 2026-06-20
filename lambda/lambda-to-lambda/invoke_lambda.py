"""
Invoke another AWS Lambda function using Boto3.

Environment variables:
    AWS_REGION           - AWS region (default: us-east-1)
    TARGET_FUNCTION_NAME - Default target Lambda function name (optional)
    INVOCATION_TYPE      - RequestResponse (sync) or Event (async) (default: RequestResponse)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Literal

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
TARGET_FUNCTION_NAME = os.environ.get("TARGET_FUNCTION_NAME", "")
INVOCATION_TYPE = os.environ.get("INVOCATION_TYPE", "RequestResponse")

InvocationType = Literal["RequestResponse", "Event", "DryRun"]

EXAMPLE_EVENT: Dict[str, Any] = {
    "function_name": "target-lambda-function",
    "payload": {"action": "process", "order_id": "ORD-1001"},
    "invocation_type": "RequestResponse",
}


def invoke_lambda(
    function_name: str,
    payload: Dict[str, Any],
    invocation_type: InvocationType = "RequestResponse",
) -> Dict[str, Any]:
    """Invoke a Lambda function synchronously or asynchronously."""
    client = boto3.client("lambda", region_name=AWS_REGION)
    try:
        response = client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload).encode("utf-8"),
        )
        logger.info(
            "Invoked %s (type=%s, status=%s)",
            function_name,
            invocation_type,
            response.get("StatusCode"),
        )

        result: Dict[str, Any] = {
            "function_name": function_name,
            "invocation_type": invocation_type,
            "status_code": response.get("StatusCode"),
            "executed_version": response.get("ExecutedVersion"),
        }

        if invocation_type == "RequestResponse" and "Payload" in response:
            raw = response["Payload"].read().decode("utf-8")
            try:
                result["response"] = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                result["response"] = raw

            if response.get("FunctionError"):
                result["function_error"] = response["FunctionError"]

        return result
    except ClientError as exc:
        logger.error("invoke failed: %s", exc)
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    function_name = event.get("function_name") or TARGET_FUNCTION_NAME
    payload = event.get("payload", {})
    invocation_type: InvocationType = event.get("invocation_type", INVOCATION_TYPE)  # type: ignore[assignment]

    if not function_name:
        return {"statusCode": 400, "body": json.dumps({"error": "function_name is required"})}

    try:
        result = invoke_lambda(function_name, payload, invocation_type)
        status = 500 if result.get("function_error") else 200
        return {"statusCode": status, "body": json.dumps(result)}
    except ClientError as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": exc.response["Error"]["Message"]}),
        }


if __name__ == "__main__":
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
