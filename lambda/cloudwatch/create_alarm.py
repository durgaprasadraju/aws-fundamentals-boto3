"""
Create a CloudWatch alarm on a custom metric.

Lab: AWS Fundamentals with Boto3 — CloudWatch
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
NAMESPACE = os.environ.get("METRIC_NAMESPACE", "Lab/Application")
METRIC_NAME = os.environ.get("METRIC_NAME", "OrdersProcessed")
ALARM_NAME = os.environ.get("ALARM_NAME", "lab-orders-high-alarm")


def get_cloudwatch_client():
    return boto3.client("cloudwatch", region_name=AWS_REGION)


def create_alarm(
    alarm_name: str,
    namespace: str,
    metric_name: str,
    threshold: float,
    comparison_operator: str,
    evaluation_periods: int,
    period: int,
    statistic: str,
    dimensions: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Create or update a metric alarm."""
    client = get_cloudwatch_client()
    client.put_metric_alarm(
        AlarmName=alarm_name,
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        Statistic=statistic,
        Period=period,
        EvaluationPeriods=evaluation_periods,
        Threshold=threshold,
        ComparisonOperator=comparison_operator,
        TreatMissingData="notBreaching",
    )
    logger.info("Alarm ready: %s", alarm_name)
    return {
        "alarm_name": alarm_name,
        "namespace": namespace,
        "metric_name": metric_name,
        "threshold": threshold,
        "comparison_operator": comparison_operator,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        alarm_name = event.get("alarm_name", ALARM_NAME)
        namespace = event.get("namespace", NAMESPACE)
        metric_name = event.get("metric_name", METRIC_NAME)
        threshold = float(event.get("threshold", 100))
        comparison_operator = event.get("comparison_operator", "GreaterThanThreshold")
        evaluation_periods = int(event.get("evaluation_periods", 1))
        period = int(event.get("period", 60))
        statistic = event.get("statistic", "Sum")
        dimensions = event.get(
            "dimensions",
            [{"Name": "Environment", "Value": "lab"}],
        )

        result = create_alarm(
            alarm_name,
            namespace,
            metric_name,
            threshold,
            comparison_operator,
            evaluation_periods,
            period,
            statistic,
            dimensions,
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "CloudWatch alarm created successfully", **result}),
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
    "alarm_name": "lab-orders-high-alarm",
    "namespace": "Lab/Application",
    "metric_name": "OrdersProcessed",
    "threshold": 100,
    "comparison_operator": "GreaterThanThreshold",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
