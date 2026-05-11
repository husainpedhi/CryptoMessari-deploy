from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint
from app.models.base import Base, TimestampMixin


class MessariAsset(Base, TimestampMixin):
    """Registry of all Messari-tracked crypto assets. Synced daily."""

    __tablename__ = "messari_assets"
    __table_args__ = (UniqueConstraint("slug", name="uq_messari_assets_slug"),)

    id = Column(String(64), primary_key=True)
    slug = Column(String(128), nullable=False)
    symbol = Column(String(32), nullable=False)
    name = Column(String(256), nullable=False)
    category = Column(String(128), nullable=True)
    sector = Column(String(128), nullable=True)
    tags = Column(Text, nullable=True)
    serial_id = Column(String(32), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
