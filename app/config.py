from __future__ import annotations
from urllib.parse import quote_plus
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── DB backend: "local" or "supabase" ─────────────────────────────────────
    db_backend: str = "supabase"

    # ── Local PostgreSQL ───────────────────────────────────────────────────────
    database_url: str = "postgresql://postgres:@localhost:5432/VCrypto"

    # ── Supabase connection params ─────────────────────────────────────────────
    db_host: str = ""
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = ""
    db_url: str = ""  # full connection string override (takes priority over params)

    # ── Messari API ────────────────────────────────────────────────────────────
    messari_api_key: str = "QHO0BmsTehozNB+z4kPKEks+tnl1aWtP0hepFSo0ADSdfJm+"
    messari_base_url: str = "https://api.messari.io"

    # ── Assets ─────────────────────────────────────────────────────────────────
    tracked_assets: str = (
        "bitcoin,ethereum,solana,cardano,polkadot,"
        "avalanche-2,chainlink,uniswap,polygon,cosmos"
    )

    # ── Scheduler intervals (seconds) ─────────────────────────────────────────
    scheduler_enabled: bool = True
    global_metrics_interval_seconds: int = Field(default=3600, ge=300)
    asset_metrics_interval_seconds: int = Field(default=3600, ge=300)
    asset_list_interval_seconds: int = Field(default=86400, ge=3600)
    asset_profile_interval_seconds: int = Field(default=604800, ge=3600)
    price_history_interval_seconds: int = Field(default=86400, ge=3600)

    # ── Price history ──────────────────────────────────────────────────────────
    price_history_lookback_days: int = Field(default=30, ge=1)

    # ── Logging ────────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: str = "logs/messari.log"

    # ── Derived properties ─────────────────────────────────────────────────────

    @property
    def active_database_url(self) -> str:
        if self.db_backend.lower() == "supabase":
            return self._build_supabase_url()
        return self.database_url

    def _build_supabase_url(self) -> str:
        if self.db_url:
            return self.db_url
        if not self.db_host:
            raise ValueError(
                "DB_BACKEND=supabase requires DB_HOST "
                "(e.g. DB_HOST=db.<project-ref>.supabase.co)"
            )
        if not self.db_password:
            raise ValueError("DB_BACKEND=supabase requires DB_PASSWORD")
        # quote_plus handles special chars in passwords (@ → %40, etc.)
        return (
            f"postgresql://{self.db_user}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"
        )

    @property
    def is_supabase(self) -> bool:
        return self.db_backend.lower() == "supabase"

    @property
    def tracked_assets_list(self) -> list[str]:
        return [s.strip() for s in self.tracked_assets.split(",") if s.strip()]

    @property
    def request_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.messari_api_key:
            headers["x-messari-api-key"] = self.messari_api_key
        return headers


settings = Settings()
