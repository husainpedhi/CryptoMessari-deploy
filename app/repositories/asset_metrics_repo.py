from sqlalchemy.orm import Session

from app.models.asset_metrics import MessariAssetMetrics


def insert_asset_metrics(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    session.bulk_insert_mappings(MessariAssetMetrics, rows)
    return len(rows)
