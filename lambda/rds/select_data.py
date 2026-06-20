"""
Select rows from an RDS MySQL table.

Lab: AWS Fundamentals with Boto3 — RDS
"""

import json
import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

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


def _serialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    serialized: Dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (datetime, date)):
            serialized[key] = value.isoformat()
        elif isinstance(value, Decimal):
            serialized[key] = float(value)
        else:
            serialized[key] = value
    return serialized


def select_data(
    table_name: str,
    database_name: str,
    row_id: Optional[int] = None,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """Select rows by id or return the latest rows up to limit."""
    connection = get_connection(database_name)
    cursor = connection.cursor(dictionary=True)
    try:
        if row_id is not None:
            cursor.execute(f"SELECT * FROM `{table_name}` WHERE id = %s", (row_id,))
        else:
            cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY id DESC LIMIT %s", (limit,))
        rows = [_serialize_row(row) for row in cursor.fetchall()]
        logger.info("Selected %d rows from %s", len(rows), table_name)
        return rows
    finally:
        cursor.close()
        connection.close()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        table_name = event.get("table_name", DEFAULT_TABLE)
        database_name = event.get("database_name", DB_NAME)
        row_id = event.get("id")
        limit = int(event.get("limit", 25))

        if not DB_HOST or not DB_USER or not DB_PASSWORD:
            raise ValueError("DB_HOST, DB_USER, and DB_PASSWORD env vars are required")

        rows = select_data(table_name, database_name, row_id, limit)
        return {
            "statusCode": 200,
            "body": json.dumps({"count": len(rows), "rows": rows}),
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
    "table_name": "employees",
    "limit": 10,
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
