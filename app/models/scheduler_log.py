from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, func, Index
from app.models.base import Base


class MessariSchedulerLog(Base):
    """Audit log for every scheduler job run."""

    __tablename__ = "messari_scheduler_logs"
    __table_args__ = (Index("ix_messari_scheduler_logs_job_ran", "job_name", "ran_at"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    records_processed = Column(Integer, nullable=True)
    duration_seconds = Column(Numeric(10, 3), nullable=True)
    error_message = Column(Text, nullable=True)
    ran_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
