"""
Messari API client (api.messari.io).

Free-tier key gives access to:
  - /metrics/v2/assets            → asset registry (all assets, basic fields)

Enterprise-only (returns 401 without upgrade):
  - /metrics/v1/assets/{slug}/metrics         → per-asset metrics
  - /metrics/v1/assets/{slug}/profile         → full profile
  - /metrics/v2/assets/{slug}/metrics/price/time-series/1d  → OHLCV
  - /metrics/v1/global/market-data            → global market data

Jobs that call Enterprise endpoints log a clear warning and return empty
results so the scheduler keeps running normally.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 20 calls/minute free tier → stay under with 3 s gap (be conservative)
_MIN_CALL_INTERVAL = 3.5
_last_call_time: float = 0.0


class MessariEnterpriseRequired(Exception):
    """Raised when an endpoint requires an Enterprise API key (HTTP 401/403)."""


def _rate_limit() -> None:
    global _last_call_time
    elapsed = time.monotonic() - _last_call_time
    if elapsed < _MIN_CALL_INTERVAL:
        time.sleep(_MIN_CALL_INTERVAL - elapsed)
    _last_call_time = time.monotonic()


def _get(path: str, params: dict | None = None) -> dict:
    _rate_limit()
    url = f"{settings.messari_base_url}{path}"
    resp = requests.get(url, headers=settings.request_headers, params=params, timeout=30)

    if resp.status_code in (401, 403):
        msg = (resp.json() or {}).get("error", resp.text[:120])
        raise MessariEnterpriseRequired(f"{resp.status_code} {path}: {msg}")

    resp.raise_for_status()
    return resp.json()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
    reraise=True,
)
def _get_with_retry(path: str, params: dict | None = None) -> dict:
    return _get(path, params)


# ── Asset list — FREE ──────────────────────────────────────────────────────────

def _parse_asset_row(a: dict, now: datetime) -> dict:
    return {
        "id": (a.get("id") or "")[:64],
        "slug": (a.get("slug") or "")[:128],
        "symbol": (a.get("symbol") or "")[:32],
        "name": (a.get("name") or "")[:256],
        "category": (a.get("category") or "")[:128] or None,
        "sector": (a.get("sector") or "")[:128] or None,
        "tags": _safe_json(a.get("tags")),
        "serial_id": str(a.get("rank"))[:32] if a.get("rank") else None,
        "fetched_at": now,
    }


def fetch_assets_paged(page_size: int = 500):
    """
    Generator — yields one page of parsed asset dicts at a time.
    Keeps memory flat for the 42k+ asset list.
    """
    page = 1
    total_fetched = 0
    try:
        while True:
            data = _get_with_retry("/metrics/v2/assets", params={"limit": page_size, "page": page})
            rows = data.get("data") or []
            if not rows:
                break
            now = datetime.now(timezone.utc)
            parsed = [_parse_asset_row(a, now) for a in rows]
            total_fetched += len(parsed)
            yield parsed
            meta = data.get("metadata") or {}
            if page >= meta.get("totalPages", 1):
                break
            page += 1
        logger.info("fetch_assets_paged: %d total assets across %d pages", total_fetched, page)
    except MessariEnterpriseRequired as exc:
        logger.warning("fetch_assets — Enterprise required: %s", exc)
        return
    except Exception as exc:
        logger.error("fetch_assets failed: %s", exc)
        raise


def fetch_assets(limit: int = 500) -> list[dict]:
    """Convenience wrapper that collects all pages into a list."""
    return [row for page in fetch_assets_paged(page_size=limit) for row in page]


# ── Asset metrics — ENTERPRISE ────────────────────────────────────────────────

def fetch_asset_metrics(slug: str) -> dict | None:
    """Fetch per-asset metrics. Requires Enterprise API key (returns None otherwise)."""
    try:
        data = _get_with_retry(f"/metrics/v1/assets/{slug}/metrics")
        a = data.get("data", {}) or {}
        if not a:
            return None

        mkt = a.get("market_data") or {}
        cap = a.get("marketcap") or {}
        sup = a.get("supply") or {}
        onc = a.get("on_chain_data") or {}
        dev = a.get("developer_activity") or {}
        roi = a.get("roi_data") or {}
        ohlcv_1h = mkt.get("ohlcv_last_1_hour") or {}
        ohlcv_24h = mkt.get("ohlcv_last_24_hours") or {}

        now = datetime.now(timezone.utc)
        return {
            "slug": slug,
            "symbol": a.get("symbol"),
            "name": a.get("name"),
            "price_usd": mkt.get("price_usd"),
            "volume_last_24h": mkt.get("volume_last_24_hours"),
            "real_volume_last_24h": mkt.get("real_volume_last_24_hours"),
            "volume_overstatement_multiple": mkt.get("volume_last_24_hours_overstatement_multiple"),
            "percent_change_1h": mkt.get("percent_change_usd_last_1_hour"),
            "percent_change_24h": mkt.get("percent_change_usd_last_24_hours"),
            "percent_change_7d": mkt.get("percent_change_usd_last_7_days"),
            "ohlcv_last_1h_open": ohlcv_1h.get("open"),
            "ohlcv_last_1h_high": ohlcv_1h.get("high"),
            "ohlcv_last_1h_low": ohlcv_1h.get("low"),
            "ohlcv_last_1h_close": ohlcv_1h.get("close"),
            "ohlcv_last_1h_volume": ohlcv_1h.get("volume"),
            "ohlcv_last_24h_open": ohlcv_24h.get("open"),
            "ohlcv_last_24h_high": ohlcv_24h.get("high"),
            "ohlcv_last_24h_low": ohlcv_24h.get("low"),
            "ohlcv_last_24h_close": ohlcv_24h.get("close"),
            "ohlcv_last_24h_volume": ohlcv_24h.get("volume"),
            "current_marketcap_usd": cap.get("current_marketcap_usd"),
            "y_2050_marketcap_usd": cap.get("y_2050_marketcap_usd"),
            "y_plus10_marketcap_usd": cap.get("y_plus10_marketcap_usd"),
            "liquid_marketcap_usd": cap.get("liquid_market_cap"),
            "volume_turnover_last_24h": cap.get("volume_turnover_last_24_hours"),
            "realized_marketcap_usd": cap.get("realized_marketcap_usd"),
            "marketcap_dominance_pct": cap.get("marketcap_dominance_percent"),
            "y_2050_issued_pct": sup.get("y_2050_issued_percent"),
            "annual_inflation_pct": sup.get("annual_inflation_percent"),
            "stock_to_flow": sup.get("stock_to_flow"),
            "circulating_supply": sup.get("circulating"),
            "total_supply": sup.get("supply_total"),
            "max_supply": sup.get("supply_max"),
            "active_addresses": onc.get("active_addresses"),
            "transactions_last_24h": onc.get("transactions_last_24_hours"),
            "average_fee_usd": onc.get("average_fee_usd"),
            "median_fee_usd": onc.get("median_fee_usd"),
            "average_transfer_value_usd": onc.get("average_transfer_value_usd"),
            "median_transfer_value_usd": onc.get("median_transfer_value_usd"),
            "nvt": onc.get("nvt"),
            "nvt_adj": onc.get("nvt_adj"),
            "adjusted_txn_volume_usd": onc.get("adjusted_txn_volume_usd"),
            "hashrate": onc.get("hash_rate"),
            "mining_revenue_usd": onc.get("mining_revenue_usd"),
            "github_stars": dev.get("stars"),
            "github_watchers": dev.get("watchers"),
            "github_forks": dev.get("forks"),
            "github_commits_last_3_months": dev.get("commits_last_3_months"),
            "github_commits_last_1_year": dev.get("commits_last_1_year"),
            "github_lines_added_last_3_months": dev.get("lines_added_last_3_months"),
            "github_lines_deleted_last_3_months": dev.get("lines_deleted_last_3_months"),
            "roi_1w": roi.get("percent_change_last_1_week"),
            "roi_1m": roi.get("percent_change_last_1_month"),
            "roi_3m": roi.get("percent_change_last_3_months"),
            "roi_1y": roi.get("percent_change_last_1_year"),
            "roi_btc_1y": roi.get("percent_change_btc_last_1_year"),
            "roi_eth_1y": roi.get("percent_change_eth_last_1_year"),
            "fetched_at": now,
        }
    except MessariEnterpriseRequired as exc:
        logger.warning("fetch_asset_metrics(%s) — Enterprise required: %s", slug, exc)
        return None
    except Exception as exc:
        logger.error("fetch_asset_metrics(%s) failed: %s", slug, exc)
        raise


# ── Asset profile — ENTERPRISE ────────────────────────────────────────────────

def fetch_asset_profile(slug: str) -> dict | None:
    """Fetch full asset profile. Requires Enterprise API key (returns None otherwise)."""
    try:
        data = _get_with_retry(f"/metrics/v1/assets/{slug}/profile")
        a = data.get("data", {}) or {}
        if not a:
            return None

        p = a.get("profile", {})
        general = (p.get("general") or {})
        overview = (general.get("overview") or {})
        economics = (p.get("economics") or {})
        launch = (economics.get("launch") or {}).get("general") or {}
        token = (economics.get("token") or {})
        consensus = (economics.get("consensus_and_emission") or {})
        tech = (p.get("technology") or {})
        gov = (p.get("governance") or {})
        contributors = (p.get("contributors") or {})
        investors = (p.get("investors") or {})

        links_raw = overview.get("official_links") or []
        now = datetime.now(timezone.utc)
        return {
            "id": a.get("id", ""),
            "slug": slug,
            "symbol": a.get("symbol"),
            "name": a.get("name"),
            "tagline": overview.get("tagline"),
            "summary": overview.get("summary"),
            "project_details": overview.get("project_details"),
            "category": overview.get("category"),
            "sector": overview.get("sector"),
            "tags": _safe_json(a.get("tags")),
            "official_links": _safe_json(links_raw),
            "whitepaper_link": _safe_json(
                next((l.get("link") for l in (links_raw if isinstance(links_raw, list) else [])
                      if isinstance(l, dict) and "whitepaper" in str(l.get("name", "")).lower()), None)
            ),
            "launch_date": _parse_date(launch.get("project_launch_date")),
            "launch_style": launch.get("launch_style"),
            "fundraising_rounds": _safe_json(investors.get("funding_rounds") or []),
            "token_usage": token.get("usage"),
            "consensus_mechanism": _safe_json(consensus.get("consensus_type")),
            "emission_type": _safe_json(consensus.get("emission_type")),
            "technology_overview": (tech.get("overview") or {}).get("technology_overview"),
            "open_source": str((tech.get("security") or {}).get("open_source", "")),
            "audits": _safe_json((tech.get("security") or {}).get("audits")),
            "governance_details": _safe_json(gov.get("onchain_governance")),
            "onchain_governance_type": str(
                (gov.get("onchain_governance") or {}).get("onchain_governance_type", "")
            ),
            "team_members": _safe_json(contributors.get("team")),
            "advisors": _safe_json(contributors.get("advisors")),
            "investors": _safe_json(investors.get("funding_rounds")),
            "fetched_at": now,
        }
    except MessariEnterpriseRequired as exc:
        logger.warning("fetch_asset_profile(%s) — Enterprise required: %s", slug, exc)
        return None
    except Exception as exc:
        logger.error("fetch_asset_profile(%s) failed: %s", slug, exc)
        raise


# ── Price history — ENTERPRISE ────────────────────────────────────────────────

def fetch_price_history(slug: str, lookback_days: int = 30) -> list[dict]:
    """Fetch daily OHLCV price history. Requires Enterprise API key (returns [] otherwise)."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    try:
        data = _get_with_retry(
            f"/metrics/v2/assets/{slug}/metrics/price/time-series/1d",
            params={
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            },
        )
        values = (data.get("data") or {}).get("values") or []
        now = datetime.now(timezone.utc)
        rows = []
        for row in values:
            if len(row) < 6:
                continue
            ts_ms, o, h, l, c, v = row[0], row[1], row[2], row[3], row[4], row[5]
            rows.append({
                "slug": slug,
                "timestamp": datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": v,
                "fetched_at": now,
            })
        logger.info("fetch_price_history(%s): %d rows", slug, len(rows))
        return rows
    except MessariEnterpriseRequired as exc:
        logger.warning("fetch_price_history(%s) — Enterprise required: %s", slug, exc)
        return []
    except Exception as exc:
        logger.error("fetch_price_history(%s) failed: %s", slug, exc)
        raise


# ── Global metrics — ENTERPRISE ───────────────────────────────────────────────

def fetch_global_metrics() -> dict | None:
    """Fetch global crypto market data. Requires Enterprise API key (returns None otherwise)."""
    try:
        data = _get_with_retry("/metrics/v1/global/market-data")
        d = (data.get("data") or {}).get("market_data") or {}
        now = datetime.now(timezone.utc)
        return {
            "bitcoin_dominance_pct": d.get("bitcoin_dominance_percentage"),
            "ethereum_dominance_pct": d.get("ethereum_dominance_percentage"),
            "total_market_cap_usd": d.get("total_market_cap"),
            "volume_24h_usd": d.get("volume_24h"),
            "defi_volume_24h_usd": d.get("defi_volume_24h"),
            "defi_market_cap_usd": d.get("defi_market_cap"),
            "defi_dominance_pct": d.get("defi_dominance"),
            "active_cryptocurrencies": d.get("num_cryptocurrencies"),
            "active_markets": d.get("num_active_markets"),
            "fetched_at": now,
        }
    except MessariEnterpriseRequired as exc:
        logger.warning("fetch_global_metrics — Enterprise required: %s", exc)
        return None
    except Exception as exc:
        logger.error("fetch_global_metrics failed: %s", exc)
        raise


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_nested(obj: dict, path: str) -> Any:
    parts = path.split(".")
    for part in parts:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def _safe_json(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return str(value)


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
