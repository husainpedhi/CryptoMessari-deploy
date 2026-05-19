"""APScheduler — interval-based jobs for Messari + CoinGecko data feeds."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.scheduler.jobs import (
    # Messari
    job_sync_assets,
    job_fetch_asset_profiles,
    # CoinGecko (free) — populates the same messari_* tables
    job_fetch_coingecko_metrics,
    job_fetch_coingecko_global,
    job_fetch_coingecko_price_history,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# (job_fn, interval_attr, job_id, human_name)
_JOB_SPECS = [
    # ── Hourly ────────────────────────────────────────────────────────────────
    (job_fetch_coingecko_global,        "global_metrics_interval_seconds",  "fetch_coingecko_global",        "CoinGecko: global crypto market"),
    (job_fetch_coingecko_metrics,       "asset_metrics_interval_seconds",   "fetch_coingecko_metrics",       "CoinGecko: asset market+dev metrics"),
    # ── Daily ─────────────────────────────────────────────────────────────────
    (job_sync_assets,                   "asset_list_interval_seconds",      "sync_assets",                   "Messari: asset registry sync (42k+ assets)"),
    (job_fetch_coingecko_price_history, "price_history_interval_seconds",   "fetch_coingecko_price_history", "CoinGecko: daily OHLC per asset"),
    # ── Weekly ────────────────────────────────────────────────────────────────
    # Messari Enterprise-only — will log warning + skip until upgraded
    (job_fetch_asset_profiles,          "asset_profile_interval_seconds",   "fetch_asset_profiles",          "Messari: full asset profiles (Enterprise)"),
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


def run_blocking_scheduler() -> None:
    scheduler = BlockingScheduler(timezone="UTC")
    _register_jobs(scheduler)

    logger.info("Starting Messari+CoinGecko scheduler — %d jobs registered:", len(scheduler.get_jobs()))
    for job in scheduler.get_jobs():
        logger.info("  %-50s  every %s", job.name, job.trigger)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
