from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.models.price_history import MessariPriceHistory


def upsert_price_history(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    stmt = (
        insert(MessariPriceHistory)
        .values(rows)
        .on_conflict_do_update(
            constraint="uq_messari_price_history_slug_ts",
            set_={
                col: insert(MessariPriceHistory).excluded[col]
                for col in ["open", "high", "low", "close", "volume", "fetched_at", "updated_at"]
            },
        )
    )
    session.execute(stmt)
    return len(rows)
