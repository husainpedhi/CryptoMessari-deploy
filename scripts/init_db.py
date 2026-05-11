#!/usr/bin/env python
"""Initialize the database by running Alembic migrations."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import check_connection
from app.utils.logger import get_logger

logger = get_logger("init_db")


def main():
    logger.info("Checking database connection...")
    if not check_connection():
        logger.error("Cannot connect to database — aborting")
        sys.exit(1)

    logger.info("Running Alembic migrations...")
    ret = os.system("alembic upgrade head")
    if ret != 0:
        logger.error("Alembic migration failed")
        sys.exit(1)

    logger.info("Database initialised successfully")


if __name__ == "__main__":
    main()
