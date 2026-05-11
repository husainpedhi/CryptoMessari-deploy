"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── messari_assets ────────────────────────────────────────────────────────
    op.create_table(
        "messari_assets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column("sector", sa.String(128), nullable=True),
        sa.Column("tags", sa.Text, nullable=True),
        sa.Column("serial_id", sa.String(32), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_messari_assets_slug"),
    )

    # ── messari_asset_metrics ─────────────────────────────────────────────────
    op.create_table(
        "messari_asset_metrics",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=True),
        sa.Column("name", sa.String(256), nullable=True),
        # market data
        sa.Column("price_usd", sa.Numeric(30, 10), nullable=True),
        sa.Column("volume_last_24h", sa.Numeric(30, 4), nullable=True),
        sa.Column("real_volume_last_24h", sa.Numeric(30, 4), nullable=True),
        sa.Column("volume_overstatement_multiple", sa.Numeric(12, 4), nullable=True),
        sa.Column("percent_change_1h", sa.Numeric(12, 6), nullable=True),
        sa.Column("percent_change_24h", sa.Numeric(12, 6), nullable=True),
        sa.Column("percent_change_7d", sa.Numeric(12, 6), nullable=True),
        sa.Column("ohlcv_last_1h_open", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_1h_high", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_1h_low", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_1h_close", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_1h_volume", sa.Numeric(30, 4), nullable=True),
        sa.Column("ohlcv_last_24h_open", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_24h_high", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_24h_low", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_24h_close", sa.Numeric(30, 10), nullable=True),
        sa.Column("ohlcv_last_24h_volume", sa.Numeric(30, 4), nullable=True),
        # market cap
        sa.Column("current_marketcap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("y_2050_marketcap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("y_plus10_marketcap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("liquid_marketcap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("volume_turnover_last_24h", sa.Numeric(12, 6), nullable=True),
        sa.Column("realized_marketcap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("marketcap_dominance_pct", sa.Numeric(12, 6), nullable=True),
        # supply
        sa.Column("y_2050_issued_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("annual_inflation_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("stock_to_flow", sa.Numeric(20, 6), nullable=True),
        sa.Column("circulating_supply", sa.Numeric(30, 4), nullable=True),
        sa.Column("total_supply", sa.Numeric(30, 4), nullable=True),
        sa.Column("max_supply", sa.Numeric(30, 4), nullable=True),
        # on-chain
        sa.Column("active_addresses", sa.BigInteger, nullable=True),
        sa.Column("transactions_last_24h", sa.BigInteger, nullable=True),
        sa.Column("average_fee_usd", sa.Numeric(20, 8), nullable=True),
        sa.Column("median_fee_usd", sa.Numeric(20, 8), nullable=True),
        sa.Column("average_transfer_value_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("median_transfer_value_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("nvt", sa.Numeric(20, 6), nullable=True),
        sa.Column("nvt_adj", sa.Numeric(20, 6), nullable=True),
        sa.Column("adjusted_txn_volume_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("hashrate", sa.Numeric(30, 4), nullable=True),
        sa.Column("mining_revenue_usd", sa.Numeric(30, 4), nullable=True),
        # developer
        sa.Column("github_stars", sa.BigInteger, nullable=True),
        sa.Column("github_watchers", sa.BigInteger, nullable=True),
        sa.Column("github_forks", sa.BigInteger, nullable=True),
        sa.Column("github_commits_last_3_months", sa.BigInteger, nullable=True),
        sa.Column("github_commits_last_1_year", sa.BigInteger, nullable=True),
        sa.Column("github_lines_added_last_3_months", sa.BigInteger, nullable=True),
        sa.Column("github_lines_deleted_last_3_months", sa.BigInteger, nullable=True),
        # roi
        sa.Column("roi_1w", sa.Numeric(12, 6), nullable=True),
        sa.Column("roi_1m", sa.Numeric(12, 6), nullable=True),
        sa.Column("roi_3m", sa.Numeric(12, 6), nullable=True),
        sa.Column("roi_1y", sa.Numeric(12, 6), nullable=True),
        sa.Column("roi_btc_1y", sa.Numeric(12, 6), nullable=True),
        sa.Column("roi_eth_1y", sa.Numeric(12, 6), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messari_asset_metrics_slug_fetched", "messari_asset_metrics", ["slug", "fetched_at"])

    # ── messari_asset_profiles ────────────────────────────────────────────────
    op.create_table(
        "messari_asset_profiles",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=True),
        sa.Column("name", sa.String(256), nullable=True),
        sa.Column("tagline", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("project_details", sa.Text, nullable=True),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column("sector", sa.String(128), nullable=True),
        sa.Column("tags", sa.Text, nullable=True),
        sa.Column("official_links", sa.Text, nullable=True),
        sa.Column("whitepaper_link", sa.Text, nullable=True),
        sa.Column("launch_date", sa.Date, nullable=True),
        sa.Column("launch_style", sa.String(128), nullable=True),
        sa.Column("fundraising_rounds", sa.Text, nullable=True),
        sa.Column("token_usage", sa.Text, nullable=True),
        sa.Column("consensus_mechanism", sa.String(256), nullable=True),
        sa.Column("emission_type", sa.String(128), nullable=True),
        sa.Column("technology_overview", sa.Text, nullable=True),
        sa.Column("open_source", sa.String(16), nullable=True),
        sa.Column("audits", sa.Text, nullable=True),
        sa.Column("governance_details", sa.Text, nullable=True),
        sa.Column("onchain_governance_type", sa.String(256), nullable=True),
        sa.Column("team_members", sa.Text, nullable=True),
        sa.Column("advisors", sa.Text, nullable=True),
        sa.Column("investors", sa.Text, nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_messari_asset_profiles_slug"),
    )

    # ── messari_price_history ─────────────────────────────────────────────────
    op.create_table(
        "messari_price_history",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(30, 10), nullable=True),
        sa.Column("high", sa.Numeric(30, 10), nullable=True),
        sa.Column("low", sa.Numeric(30, 10), nullable=True),
        sa.Column("close", sa.Numeric(30, 10), nullable=True),
        sa.Column("volume", sa.Numeric(30, 4), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", "timestamp", name="uq_messari_price_history_slug_ts"),
    )
    op.create_index("ix_messari_price_history_slug", "messari_price_history", ["slug"])

    # ── messari_global_metrics ────────────────────────────────────────────────
    op.create_table(
        "messari_global_metrics",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("bitcoin_dominance_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("ethereum_dominance_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("total_market_cap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("volume_24h_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("defi_volume_24h_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("defi_market_cap_usd", sa.Numeric(30, 4), nullable=True),
        sa.Column("defi_dominance_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("active_cryptocurrencies", sa.BigInteger, nullable=True),
        sa.Column("active_markets", sa.BigInteger, nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messari_global_metrics_fetched", "messari_global_metrics", ["fetched_at"])

    # ── messari_scheduler_logs ────────────────────────────────────────────────
    op.create_table(
        "messari_scheduler_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("job_name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("records_processed", sa.Integer, nullable=True),
        sa.Column("duration_seconds", sa.Numeric(10, 3), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("ran_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messari_scheduler_logs_job_ran", "messari_scheduler_logs", ["job_name", "ran_at"])


def downgrade() -> None:
    op.drop_table("messari_scheduler_logs")
    op.drop_table("messari_global_metrics")
    op.drop_table("messari_price_history")
    op.drop_table("messari_asset_profiles")
    op.drop_table("messari_asset_metrics")
    op.drop_table("messari_assets")
