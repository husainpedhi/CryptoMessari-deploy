from sqlalchemy.orm import Session

from app.models.global_metrics import MessariGlobalMetrics


def insert_global_metrics(session: Session, row: dict) -> int:
    session.add(MessariGlobalMetrics(**row))
    return 1
