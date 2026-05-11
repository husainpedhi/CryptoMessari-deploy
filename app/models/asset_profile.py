from sqlalchemy import Column, String, Text, Date, DateTime, UniqueConstraint
from app.models.base import Base, TimestampMixin


class MessariAssetProfile(Base, TimestampMixin):
    """Full asset profile: team, governance, economics, technology. Synced weekly."""

    __tablename__ = "messari_asset_profiles"
    __table_args__ = (UniqueConstraint("slug", name="uq_messari_asset_profiles_slug"),)

    id = Column(String(64), primary_key=True)
    slug = Column(String(128), nullable=False)
    symbol = Column(String(32), nullable=True)
    name = Column(String(256), nullable=True)

    # ── General ───────────────────────────────────────────────────────────────
    tagline = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    project_details = Column(Text, nullable=True)
    category = Column(String(128), nullable=True)
    sector = Column(String(128), nullable=True)
    tags = Column(Text, nullable=True)

    # ── Links ─────────────────────────────────────────────────────────────────
    official_links = Column(Text, nullable=True)
    whitepaper_link = Column(Text, nullable=True)

    # ── Launch / fundraising ──────────────────────────────────────────────────
    launch_date = Column(Date, nullable=True)
    launch_style = Column(String(128), nullable=True)
    fundraising_rounds = Column(Text, nullable=True)

    # ── Economics ─────────────────────────────────────────────────────────────
    token_usage = Column(Text, nullable=True)
    consensus_mechanism = Column(String(256), nullable=True)
    emission_type = Column(String(128), nullable=True)

    # ── Technology ────────────────────────────────────────────────────────────
    technology_overview = Column(Text, nullable=True)
    open_source = Column(String(16), nullable=True)
    audits = Column(Text, nullable=True)

    # ── Governance ────────────────────────────────────────────────────────────
    governance_details = Column(Text, nullable=True)
    onchain_governance_type = Column(String(256), nullable=True)

    # ── Team ──────────────────────────────────────────────────────────────────
    team_members = Column(Text, nullable=True)
    advisors = Column(Text, nullable=True)
    investors = Column(Text, nullable=True)

    fetched_at = Column(DateTime(timezone=True), nullable=False)
