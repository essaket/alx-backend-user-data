#!/usr/bin/env python3
"""0. Regex-ing
   1. Log formatter
   2. Create logger
   3. Connect to secure database
   4. Read and filter data
"""
import os
import re
import mysql.connector
from typing import List
import logging


def filter_datum(
        fields: List[str],
        redaction: str,
        message: str,
        separator: str) -> str:
    """Obfuscates specified fields in a log message."""
    for field in fields:
        message = re.sub(f'{field}=.*?{separator}',
                         f'{field}={redaction}{separator}', message)
    return message


class RedactingFormatter(logging.Formatter):
    """Custom logging formatter that redacts sensitive information."""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initializes the RedactingFormatter."""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record, redacting sensitive fields."""
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def get_logger() -> logging.Logger:
    """Creates and configures a logger for user data."""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))

    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Establishes and returns a database connection."""
    config = {
        "host": os.getenv("PERSONAL_DATA_DB_HOST", "localhost"),
        "database": os.getenv("PERSONAL_DATA_DB_NAME"),
        "user": os.getenv("PERSONAL_DATA_DB_USERNAME", "root"),
        "password": os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    }
    return mysql.connector.connect(**config)


def main() -> None:
    """Fetches data from the database and logs each row."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    fields = [i[0] for i in cursor.description]

    logger = get_logger()

    for row in cursor:
        row_dict = dict(zip(fields, row))
        log_record = "; ".join(
            [f"{key}={value}" for key, value in row_dict.items()]) + ";"
        logger.info(log_record)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()