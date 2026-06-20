"""
Create a MySQL database on Amazon RDS using mysql-connector-python.

Lab: AWS Fundamentals with Boto3 — RDS

Environment variables:
    DB_HOST      - RDS endpoint hostname (required)
    DB_USER      - Database master username (required)
    DB_PASSWORD  - Database password (required; use Secrets Manager in production)
    DB_PORT      - MySQL port (default: 3306)
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
DB_PORT = int(os.environ.get("DB_PORT", "3306"))


def get_connection(database: Optional[str] = None):
    """Open a MySQL connection to the RDS instance."""
    config: Dict[str, Any] = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "port": DB_PORT,
        "connect_timeout": 10,
    }
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)


def create_database(database_name: str) -> Dict[str, Any]:
    """Create a database if it does not already exist."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        connection.commit()
        logger.info("Database ready: %s", database_name)
        return {"database_name": database_name, "created": True}
    finally:
        cursor.close()
        connection.close()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Event keys:
      - database_name (required): name of the database to create
    """
    try:
        database_name = event.get("database_name")
        if not database_name:
            raise ValueError("database_name is required")
        if not DB_HOST or not DB_USER or not DB_PASSWORD:
            raise ValueError("DB_HOST, DB_USER, and DB_PASSWORD env vars are required")

        result = create_database(database_name)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Database created successfully", **result}),
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
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(lambda_handler(EXAMPLE_EVENT, None), indent=2))
