"""
Publish a custom event to Amazon EventBridge.

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
EVENT_SOURCE = os.environ.get("EVENT_SOURCE", "com.lab.orders")
EVENT_DETAIL_TYPE = os.environ.get("EVENT_DETAIL_TYPE", "OrderCreated")


def get_events_client():
    return boto3.client("events", region_name=AWS_REGION)


def put_event(
    source: str,
    detail_type: str,
    detail: Dict[str, Any],
    event_bus_name: str,
) -> Dict[str, Any]:
    """Put a single custom event onto an event bus."""
    client = get_events_client()
    response = client.put_events(
        Entries=[
            {
                "Source": source,
                "DetailType": detail_type,
                "Detail": json.dumps(detail),
                "EventBusName": event_bus_name,
            }
        ]
    )
    failed = int(response.get("FailedEntryCount", 0))
    if failed:
        raise ClientError(
            {"Error": {"Code": "PutEventsFailed", "Message": str(response.get("Entries", []))}},
            "PutEvents",
        )
    entry = response["Entries"][0]
    logger.info("Published event %s to bus %s", entry["EventId"], event_bus_name)
    return {
        "event_id": entry["EventId"],
        "event_bus_name": event_bus_name,
        "source": source,
        "detail_type": detail_type,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        source = event.get("source", EVENT_SOURCE)
        detail_type = event.get("detail_type", EVENT_DETAIL_TYPE)
        detail = event.get("detail", {"order_id": "ORD-001", "status": "CREATED"})
        event_bus_name = event.get("event_bus_name", EVENT_BUS_NAME)

        if not isinstance(detail, dict):
            raise ValueError("detail must be a JSON object")

        result = put_event(source, detail_type, detail, event_bus_name)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Event published successfully", **result}),
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
    "source": "com.lab.orders",
    "detail_type": "OrderCreated",
    "detail": {"order_id": "ORD-001", "amount": 49.99},
    "event_bus_name": "default",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
