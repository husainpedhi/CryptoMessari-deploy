"""Scheduler job functions — each wraps a Messari fetch + DB upsert + audit log."""

import time

from app.config import settings
from app.database import get_db
from app.repositories import (
    asset_repo,
    asset_metrics_repo,
    asset_profile_repo,
    price_history_repo,
    global_metrics_repo,
    scheduler_log_repo,
)
from app.services import messari_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _run_job(job_name: str, fn, *args, **kwargs) -> int:
    """Execute fn, log result to scheduler_logs, return record count."""
    db_label = settings.db_backend.upper()
    db_url_hint = settings.active_database_url.split("@")[-1].split("?")[0]  # host/dbname only
    logger.info("[%s] starting — writing to %s (%s)", job_name, db_label, db_url_hint)
    start = time.monotonic()
    try:
        result = fn(*args, **kwargs)
        duration = time.monotonic() - start
        records = result if isinstance(result, int) else 0
        with get_db() as session:
            scheduler_log_repo.log_job(session, job_name, "success", records, duration)
        logger.info("[%s] OK — %d records in %.2fs [%s]", job_name, records, duration, db_label)
        return records
    except Exception as exc:
        duration = time.monotonic() - start
        with get_db() as session:
            scheduler_log_repo.log_job(session, job_name, "error", 0, duration, str(exc)[:1000])
        logger.error("[%s] FAILED in %.2fs [%s]: %s", job_name, duration, db_label, exc)
        return 0


# ── Asset list (daily) ────────────────────────────────────────────────────────

def job_sync_assets() -> None:
    def _inner():
        # Stream page-by-page to avoid accumulating 40k+ rows in memory at once
        total = 0
        for page_assets in messari_service.fetch_assets_paged():
            with get_db() as session:
                total += asset_repo.upsert_assets(session, page_assets)
        return total
    _run_job("sync_assets", _inner)


# ── Asset metrics (hourly) ────────────────────────────────────────────────────

def job_fetch_asset_metrics() -> None:
    def _inner():
        rows = []
        for slug in settings.tracked_assets_list:
            try:
                row = messari_service.fetch_asset_metrics(slug)
                if row:
                    rows.append(row)
            except Exception:
                pass  # individual failure already logged in service
        if rows:
            with get_db() as session:
                return asset_metrics_repo.insert_asset_metrics(session, rows)
        return 0
    _run_job("fetch_asset_metrics", _inner)


# ── Asset profiles (weekly) ───────────────────────────────────────────────────

def job_fetch_asset_profiles() -> None:
    def _inner():
        profiles = []
        for slug in settings.tracked_assets_list:
            try:
                profile = messari_service.fetch_asset_profile(slug)
                if profile:
                    profiles.append(profile)
            except Exception:
                pass
        if profiles:
            with get_db() as session:
                return asset_profile_repo.upsert_asset_profiles(session, profiles)
        return 0
    _run_job("fetch_asset_profiles", _inner)


# ── Price history (daily) ─────────────────────────────────────────────────────

def job_fetch_price_history() -> None:
    def _inner():
        total = 0
        for slug in settings.tracked_assets_list:
            try:
                rows = messari_service.fetch_price_history(
                    slug, lookback_days=settings.price_history_lookback_days
                )
                if rows:
                    with get_db() as session:
                        total += price_history_repo.upsert_price_history(session, rows)
            except Exception:
                pass
        return total
    _run_job("fetch_price_history", _inner)


# ── Global metrics (hourly) ───────────────────────────────────────────────────

def job_fetch_global_metrics() -> None:
    def _inner():
        row = messari_service.fetch_global_metrics()
        if row:
            with get_db() as session:
                return global_metrics_repo.insert_global_metrics(session, row)
        return 0
    _run_job("fetch_global_metrics", _inner)
