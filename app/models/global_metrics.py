from sqlalchemy import Column, BigInteger, Numeric, DateTime, Index
from app.models.base import Base, TimestampMixin


class MessariGlobalMetrics(Base, TimestampMixin):
    """Global crypto market metrics snapshot. Appended hourly."""

    __tablename__ = "messari_global_metrics"
    __table_args__ = (Index("ix_messari_global_metrics_fetched", "fetched_at"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    bitcoin_dominance_pct = Column(Numeric(12, 6), nullable=True)
    ethereum_dominance_pct = Column(Numeric(12, 6), nullable=True)
    total_market_cap_usd = Column(Numeric(30, 4), nullable=True)
    volume_24h_usd = Column(Numeric(30, 4), nullable=True)
    defi_volume_24h_usd = Column(Numeric(30, 4), nullable=True)
    defi_market_cap_usd = Column(Numeric(30, 4), nullable=True)
    defi_dominance_pct = Column(Numeric(12, 6), nullable=True)
    active_cryptocurrencies = Column(BigInteger, nullable=True)
    active_markets = Column(BigInteger, nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
