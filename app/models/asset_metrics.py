from sqlalchemy import Column, String, Numeric, BigInteger, DateTime, Index
from app.models.base import Base, TimestampMixin


class MessariAssetMetrics(Base, TimestampMixin):
    """
    Wide snapshot of all Messari metrics per asset: market data, supply,
    on-chain data, developer activity, and ROI. Appended hourly.
    """

    __tablename__ = "messari_asset_metrics"
    __table_args__ = (
        Index("ix_messari_asset_metrics_slug_fetched", "slug", "fetched_at"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    slug = Column(String(128), nullable=False)
    symbol = Column(String(32), nullable=True)
    name = Column(String(256), nullable=True)

    # ── Market data ───────────────────────────────────────────────────────────
    price_usd = Column(Numeric(30, 10), nullable=True)
    volume_last_24h = Column(Numeric(30, 4), nullable=True)
    real_volume_last_24h = Column(Numeric(30, 4), nullable=True)
    volume_overstatement_multiple = Column(Numeric(12, 4), nullable=True)
    percent_change_1h = Column(Numeric(12, 6), nullable=True)
    percent_change_24h = Column(Numeric(12, 6), nullable=True)
    percent_change_7d = Column(Numeric(12, 6), nullable=True)
    ohlcv_last_1h_open = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_1h_high = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_1h_low = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_1h_close = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_1h_volume = Column(Numeric(30, 4), nullable=True)
    ohlcv_last_24h_open = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_24h_high = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_24h_low = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_24h_close = Column(Numeric(30, 10), nullable=True)
    ohlcv_last_24h_volume = Column(Numeric(30, 4), nullable=True)

    # ── Market cap ────────────────────────────────────────────────────────────
    current_marketcap_usd = Column(Numeric(30, 4), nullable=True)
    y_2050_marketcap_usd = Column(Numeric(30, 4), nullable=True)
    y_plus10_marketcap_usd = Column(Numeric(30, 4), nullable=True)
    liquid_marketcap_usd = Column(Numeric(30, 4), nullable=True)
    volume_turnover_last_24h = Column(Numeric(12, 6), nullable=True)
    realized_marketcap_usd = Column(Numeric(30, 4), nullable=True)
    marketcap_dominance_pct = Column(Numeric(12, 6), nullable=True)

    # ── Supply ────────────────────────────────────────────────────────────────
    y_2050_issued_pct = Column(Numeric(12, 6), nullable=True)
    annual_inflation_pct = Column(Numeric(12, 6), nullable=True)
    stock_to_flow = Column(Numeric(20, 6), nullable=True)
    circulating_supply = Column(Numeric(30, 4), nullable=True)
    total_supply = Column(Numeric(30, 4), nullable=True)
    max_supply = Column(Numeric(30, 4), nullable=True)

    # ── On-chain data ─────────────────────────────────────────────────────────
    active_addresses = Column(BigInteger, nullable=True)
    transactions_last_24h = Column(BigInteger, nullable=True)
    average_fee_usd = Column(Numeric(20, 8), nullable=True)
    median_fee_usd = Column(Numeric(20, 8), nullable=True)
    average_transfer_value_usd = Column(Numeric(30, 4), nullable=True)
    median_transfer_value_usd = Column(Numeric(30, 4), nullable=True)
    nvt = Column(Numeric(20, 6), nullable=True)
    nvt_adj = Column(Numeric(20, 6), nullable=True)
    adjusted_txn_volume_usd = Column(Numeric(30, 4), nullable=True)
    hashrate = Column(Numeric(30, 4), nullable=True)
    mining_revenue_usd = Column(Numeric(30, 4), nullable=True)

    # ── Developer activity ────────────────────────────────────────────────────
    github_stars = Column(BigInteger, nullable=True)
    github_watchers = Column(BigInteger, nullable=True)
    github_forks = Column(BigInteger, nullable=True)
    github_commits_last_3_months = Column(BigInteger, nullable=True)
    github_commits_last_1_year = Column(BigInteger, nullable=True)
    github_lines_added_last_3_months = Column(BigInteger, nullable=True)
    github_lines_deleted_last_3_months = Column(BigInteger, nullable=True)

    # ── ROI data ──────────────────────────────────────────────────────────────
    roi_1w = Column(Numeric(12, 6), nullable=True)
    roi_1m = Column(Numeric(12, 6), nullable=True)
    roi_3m = Column(Numeric(12, 6), nullable=True)
    roi_1y = Column(Numeric(12, 6), nullable=True)
    roi_btc_1y = Column(Numeric(12, 6), nullable=True)
    roi_eth_1y = Column(Numeric(12, 6), nullable=True)

    fetched_at = Column(DateTime(timezone=True), nullable=False)
