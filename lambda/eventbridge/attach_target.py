"""
Attach a target to an EventBridge rule.

Lab: AWS Fundamentals with Boto3 — EventBridge
"""

import json
import logging
import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
EVENT_BUS_NAME = os.environ.get("EVENT_BUS_NAME", "default")
RULE_NAME = os.environ.get("RULE_NAME", "lab-order-created-rule")
TARGET_ARN = os.environ.get("TARGET_ARN", "")


def get_events_client():
    return boto3.client("events", region_name=AWS_REGION)


def attach_target(
    rule_name: str,
    target_arn: str,
    event_bus_name: str,
    target_id: str = "lab-target-1",
) -> Dict[str, Any]:
    """Attach a Lambda, SQS, or SNS target to a rule."""
    client = get_events_client()
    params: Dict[str, Any] = {
        "Rule": rule_name,
        "Targets": [{"Id": target_id, "Arn": target_arn}],
    }
    if event_bus_name and event_bus_name != "default":
        params["EventBusName"] = event_bus_name

    response = client.put_targets(**params)
    failed = int(response.get("FailedEntryCount", 0))
    if failed:
        failures: List[Dict[str, Any]] = response.get("FailedEntries", [])
        raise ClientError(
            {"Error": {"Code": "PutTargetsFailed", "Message": json.dumps(failures)}},
            "PutTargets",
        )

    logger.info("Attached target %s to rule %s", target_arn, rule_name)
    return {
        "rule_name": rule_name,
        "target_id": target_id,
        "target_arn": target_arn,
        "event_bus_name": event_bus_name,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        rule_name = event.get("rule_name", RULE_NAME)
        target_arn = event.get("target_arn") or TARGET_ARN
        event_bus_name = event.get("event_bus_name", EVENT_BUS_NAME)
        target_id = event.get("target_id", "lab-target-1")

        if not target_arn:
            raise ValueError("target_arn is required (event or TARGET_ARN env var)")

        result = attach_target(rule_name, target_arn, event_bus_name, target_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Target attached successfully", **result}),
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
    "rule_name": "lab-order-created-rule",
    "target_arn": "arn:aws:lambda:us-east-1:123456789012:function:lab-order-processor",
    "target_id": "lab-target-1",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
