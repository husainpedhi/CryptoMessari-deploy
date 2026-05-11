from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.models.asset_profile import MessariAssetProfile


def upsert_asset_profiles(session: Session, profiles: list[dict]) -> int:
    if not profiles:
        return 0
    stmt = (
        insert(MessariAssetProfile)
        .values(profiles)
        .on_conflict_do_update(
            constraint="uq_messari_asset_profiles_slug",
            set_={
                col: insert(MessariAssetProfile).excluded[col]
                for col in [
                    "symbol", "name", "tagline", "summary", "project_details",
                    "category", "sector", "tags", "official_links", "whitepaper_link",
                    "launch_date", "launch_style", "fundraising_rounds", "token_usage",
                    "consensus_mechanism", "emission_type", "technology_overview",
                    "open_source", "audits", "governance_details",
                    "onchain_governance_type", "team_members", "advisors",
                    "investors", "fetched_at", "updated_at",
                ]
            },
        )
    )
    session.execute(stmt)
    return len(profiles)
