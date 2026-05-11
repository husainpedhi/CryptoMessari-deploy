from __future__ import annotations
from typing import Optional

from sqlalchemy.orm import Session

from app.models.scheduler_log import MessariSchedulerLog


def log_job(
    session: Session,
    job_name: str,
    status: str,
    records_processed: Optional[int] = None,
    duration_seconds: Optional[float] = None,
    error_message: Optional[str] = None,
) -> None:
    session.add(
        MessariSchedulerLog(
            job_name=job_name,
            status=status,
            records_processed=records_processed,
            duration_seconds=round(duration_seconds, 3) if duration_seconds is not None else None,
            error_message=error_message,
        )
    )
