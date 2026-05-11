from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.models.asset import MessariAsset

# PostgreSQL limit is 65535 bind params; 9 cols per row → safe batch size
_BATCH_SIZE = 500


def upsert_assets(session: Session, assets: list[dict]) -> int:
    if not assets:
        return 0

    total = 0
    for i in range(0, len(assets), _BATCH_SIZE):
        batch = assets[i : i + _BATCH_SIZE]
        stmt = (
            insert(MessariAsset)
            .values(batch)
            .on_conflict_do_update(
                constraint="uq_messari_assets_slug",
                set_={
                    "symbol": insert(MessariAsset).excluded.symbol,
                    "name": insert(MessariAsset).excluded.name,
                    "category": insert(MessariAsset).excluded.category,
                    "sector": insert(MessariAsset).excluded.sector,
                    "tags": insert(MessariAsset).excluded.tags,
                    "serial_id": insert(MessariAsset).excluded.serial_id,
                    "fetched_at": insert(MessariAsset).excluded.fetched_at,
                    "updated_at": insert(MessariAsset).excluded.updated_at,
                },
            )
        )
        session.execute(stmt)
        total += len(batch)

    return total
