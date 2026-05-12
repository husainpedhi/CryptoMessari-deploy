"""APScheduler — interval-based jobs for all Messari data feeds."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.scheduler.jobs import (
    job_sync_assets,
    job_fetch_asset_metrics,
    job_fetch_asset_profiles,
    job_fetch_price_history,
    job_fetch_global_metrics,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# (job_fn, interval_attr, job_id, human_name)
_JOB_SPECS = [
    # ── Hourly ────────────────────────────────────────────────────────────────
    (job_fetch_global_metrics,  "global_metrics_interval_seconds",  "fetch_global_metrics",  "Global crypto market metrics"),
    (job_fetch_asset_metrics,   "asset_metrics_interval_seconds",   "fetch_asset_metrics",   "Asset metrics (market+on-chain+ROI)"),
    # ── Daily ─────────────────────────────────────────────────────────────────
    (job_sync_assets,           "asset_list_interval_seconds",      "sync_assets",           "Asset registry sync"),
    (job_fetch_price_history,   "price_history_interval_seconds",   "fetch_price_history",   "Asset OHLCV price history"),
    # ── Weekly ────────────────────────────────────────────────────────────────
    (job_fetch_asset_profiles,  "asset_profile_interval_seconds",   "fetch_asset_profiles",  "Full asset profiles (team/governance)"),
]


def _register_jobs(scheduler) -> None:
    for fn, interval_attr, job_id, name in _JOB_SPECS:
        seconds = getattr(settings, interval_attr)
        scheduler.add_job(
            fn,
            trigger=IntervalTrigger(seconds=seconds),
            id=job_id,
            name=name,
            replace_existing=True,
            max_instances=1,
        )


def create_background_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    _register_jobs(scheduler)
    return scheduler


def run_blocking_scheduler(run_immediately: bool = True) -> None:
    scheduler = BlockingScheduler(timezone="UTC")
    _register_jobs(scheduler)

    if run_immediately:
        logger.info("Running all jobs immediately at startup...")
        for job in scheduler.get_jobs():
            logger.info("  -> %s", job.name)
            try:
                job.func()
            except Exception as exc:
                logger.error("Startup run failed for %s: %s", job.name, exc)

    logger.info("Starting Messari scheduler — %d jobs registered:", len(scheduler.get_jobs()))
    for job in scheduler.get_jobs():
        logger.info("  %-50s  every %s", job.name, job.trigger)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
