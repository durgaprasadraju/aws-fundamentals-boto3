"""
Update a row in an RDS MySQL table.

Lab: AWS Fundamentals with Boto3 — RDS
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import mysql.connector
from mysql.connector import Error as MySQLError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DB_HOST = os.environ.get("DB_HOST", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "lab_db")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DEFAULT_TABLE = "employees"


def get_connection(database: Optional[str] = None):
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=database or DB_NAME,
        connect_timeout=10,
    )


def update_data(
    table_name: str,
    row_id: int,
    department: str,
    database_name: str,
) -> Dict[str, Any]:
    """Update the department column for a row."""
    connection = get_connection(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"UPDATE `{table_name}` SET department = %s WHERE id = %s",
            (department, row_id),
        )
        connection.commit()
        updated = cursor.rowcount
        logger.info("Updated %d row(s) in %s where id=%s", updated, table_name, row_id)
        return {"id": row_id, "department": department, "rows_updated": updated}
    finally:
        cursor.close()
        connection.close()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        table_name = event.get("table_name", DEFAULT_TABLE)
        database_name = event.get("database_name", DB_NAME)
        row_id = event.get("id")
        department = event.get("department")

        if row_id is None or not department:
            raise ValueError("id and department are required")
        if not DB_HOST or not DB_USER or not DB_PASSWORD:
            raise ValueError("DB_HOST, DB_USER, and DB_PASSWORD env vars are required")

        result = update_data(table_name, int(row_id), department, database_name)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Row updated successfully", **result}),
        }
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        return {"statusCode": 400, "body": json.dumps({"error": str(exc)})}
    except MySQLError as exc:
        logger.error("MySQL error: %s", exc)
        return {"statusCode": 500, "body": json.dumps({"error": str(exc), "error_code": "MySQLError"})}
    except Exception as exc:
        logger.exception("Unexpected error")
        return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}


EXAMPLE_EVENT = {
    "id": 1,
    "department": "Platform Engineering",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
