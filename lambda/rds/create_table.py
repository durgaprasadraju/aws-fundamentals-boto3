"""
Create a sample table in an RDS MySQL database.

Lab: AWS Fundamentals with Boto3 — RDS

Environment variables:
    DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
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


def create_table(table_name: str, database_name: str) -> Dict[str, Any]:
    """Create a simple employees table for lab exercises."""
    connection = get_connection(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                department VARCHAR(50) DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
        logger.info("Table ready: %s.%s", database_name, table_name)
        return {"database_name": database_name, "table_name": table_name, "created": True}
    finally:
        cursor.close()
        connection.close()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        table_name = event.get("table_name", DEFAULT_TABLE)
        database_name = event.get("database_name", DB_NAME)
        if not DB_HOST or not DB_USER or not DB_PASSWORD:
            raise ValueError("DB_HOST, DB_USER, and DB_PASSWORD env vars are required")

        result = create_table(table_name, database_name)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Table created successfully", **result}),
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
    "database_name": "lab_db",
    "table_name": "employees",
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
