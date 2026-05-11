#!/usr/bin/env python
"""Start the blocking Messari scheduler."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import check_connection
from app.scheduler.scheduler import run_blocking_scheduler
from app.utils.logger import get_logger

logger = get_logger("run_scheduler")


def main():
    logger.info("=== Messari Scheduler ===")
    logger.info("Tracked assets: %s", ", ".join(settings.tracked_assets_list))

    if not check_connection():
        logger.error("Database unavailable — exiting")
        sys.exit(1)

    if not settings.scheduler_enabled:
        logger.warning("SCHEDULER_ENABLED=false — nothing to do")
        sys.exit(0)

    run_blocking_scheduler()


if __name__ == "__main__":
    main()
