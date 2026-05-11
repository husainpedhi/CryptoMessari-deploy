#!/usr/bin/env python
"""Run all Messari jobs once (useful for testing / initial data load)."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import check_connection
from app.scheduler.jobs import (
    job_sync_assets,
    job_fetch_global_metrics,
    job_fetch_asset_metrics,
    job_fetch_price_history,
    job_fetch_asset_profiles,
)
from app.utils.logger import get_logger

logger = get_logger("run_once")


def main():
    if not check_connection():
        logger.error("Database unavailable — exiting")
        sys.exit(1)

    logger.info("Running all jobs once...")

    job_fetch_global_metrics()
    job_sync_assets()
    job_fetch_asset_metrics()
    job_fetch_price_history()
    job_fetch_asset_profiles()

    logger.info("All jobs complete")


if __name__ == "__main__":
    main()
