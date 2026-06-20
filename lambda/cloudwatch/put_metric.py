"""
Publish a custom metric to Amazon CloudWatch.

Lab: AWS Fundamentals with Boto3 — CloudWatch
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
NAMESPACE = os.environ.get("METRIC_NAMESPACE", "Lab/Application")
METRIC_NAME = os.environ.get("METRIC_NAME", "OrdersProcessed")


def get_cloudwatch_client():
    return boto3.client("cloudwatch", region_name=AWS_REGION)


def put_metric(
    namespace: str,
    metric_name: str,
    value: float,
    unit: str,
    dimensions: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Publish a single custom metric data point."""
    client = get_cloudwatch_client()
    client.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.now(timezone.utc),
                "Dimensions": dimensions,
            }
        ],
    )
    logger.info("Published metric %s/%s=%s", namespace, metric_name, value)
    return {
        "namespace": namespace,
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "dimensions": dimensions,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        namespace = event.get("namespace", NAMESPACE)
        metric_name = event.get("metric_name", METRIC_NAME)
        value = float(event.get("value", 1))
        unit = event.get("unit", "Count")
        dimensions = event.get(
            "dimensions",
            [{"Name": "Environment", "Value": "lab"}],
        )

        result = put_metric(namespace, metric_name, value, unit, dimensions)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Metric published successfully", **result}),
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
    "namespace": "Lab/Application",
    "metric_name": "OrdersProcessed",
    "value": 1,
    "unit": "Count",
    "dimensions": [{"Name": "Environment", "Value": "lab"}],
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
