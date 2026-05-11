from sqlalchemy import Column, String, Numeric, DateTime, BigInteger, UniqueConstraint, Index
from app.models.base import Base, TimestampMixin


class MessariPriceHistory(Base, TimestampMixin):
    """Daily OHLCV price history per asset from Messari timeseries API."""

    __tablename__ = "messari_price_history"
    __table_args__ = (
        UniqueConstraint("slug", "timestamp", name="uq_messari_price_history_slug_ts"),
        Index("ix_messari_price_history_slug", "slug"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    slug = Column(String(128), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(30, 10), nullable=True)
    high = Column(Numeric(30, 10), nullable=True)
    low = Column(Numeric(30, 10), nullable=True)
    close = Column(Numeric(30, 10), nullable=True)
    volume = Column(Numeric(30, 4), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
