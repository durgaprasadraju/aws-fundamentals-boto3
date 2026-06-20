"""
Create an EventBridge rule with an event pattern.

Lab: AWS Fundamentals with Boto3 — EventBridge
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
EVENT_BUS_NAME = os.environ.get("EVENT_BUS_NAME", "default")
RULE_NAME = os.environ.get("RULE_NAME", "lab-order-created-rule")


def get_events_client():
    return boto3.client("events", region_name=AWS_REGION)


def create_rule(
    rule_name: str,
    event_pattern: Dict[str, Any],
    event_bus_name: str,
    description: str = "",
) -> Dict[str, Any]:
    """Create or update an EventBridge rule."""
    client = get_events_client()
    params: Dict[str, Any] = {
        "Name": rule_name,
        "EventPattern": json.dumps(event_pattern),
        "State": "ENABLED",
    }
    if event_bus_name and event_bus_name != "default":
        params["EventBusName"] = event_bus_name
    if description:
        params["Description"] = description

    response = client.put_rule(**params)
    logger.info("Rule ready: %s on bus %s", rule_name, event_bus_name)
    return {
        "rule_name": rule_name,
        "rule_arn": response["RuleArn"],
        "event_bus_name": event_bus_name,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        rule_name = event.get("rule_name", RULE_NAME)
        event_bus_name = event.get("event_bus_name", EVENT_BUS_NAME)
        description = event.get("description", "Lab rule for OrderCreated events")
        event_pattern = event.get(
            "event_pattern",
            {
                "source": ["com.lab.orders"],
                "detail-type": ["OrderCreated"],
            },
        )

        if not isinstance(event_pattern, dict):
            raise ValueError("event_pattern must be a JSON object")

        result = create_rule(rule_name, event_pattern, event_bus_name, description)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "EventBridge rule created successfully", **result}),
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
    "event_bus_name": "default",
    "event_pattern": {
        "source": ["com.lab.orders"],
        "detail-type": ["OrderCreated"],
    },
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
