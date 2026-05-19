"""
CoinGecko API client (free tier, no auth required).

Populates Messari schema tables from CoinGecko's free public API:
  - messari_asset_metrics  ← /coins/markets + /coins/{id} (developer data)
  - messari_global_metrics ← /global
  - messari_price_history  ← /coins/{id}/ohlc

Free-tier limits: ~10-30 calls/minute (we pace at 6.5s between calls).
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# CoinGecko free tier: 10-30 calls/min depending on time of day
_MIN_CALL_INTERVAL = 6.5
_last_call_time: float = 0.0


def _rate_limit() -> None:
    global _last_call_time
    elapsed = time.monotonic() - _last_call_time
    if elapsed < _MIN_CALL_INTERVAL:
        time.sleep(_MIN_CALL_INTERVAL - elapsed)
    _last_call_time = time.monotonic()


def _headers() -> dict:
    h = {"Accept": "application/json"}
    if settings.coingecko_api_key:
        # Demo keys use x-cg-demo-api-key, Pro keys use x-cg-pro-api-key
        header_name = "x-cg-pro-api-key" if "pro" in settings.coingecko_base_url else "x-cg-demo-api-key"
        h[header_name] = settings.coingecko_api_key
    return h


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=8, max=60),
    retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
    reraise=True,
)
def _get(path: str, params: dict | None = None) -> Any:
    _rate_limit()
    url = f"{settings.coingecko_base_url}{path}"
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── Market data (bulk) ────────────────────────────────────────────────────────

def fetch_markets(ids: list[str]) -> list[dict]:
    """
    Bulk market data for many assets in ONE call.
    Returns rows shaped for messari_asset_metrics table.
    """
    if not ids:
        return []

    try:
        data = _get("/coins/markets", params={
            "vs_currency": "usd",
            "ids": ",".join(ids),
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d,30d,1y",
        })
        now = datetime.now(timezone.utc)
        rows = []
        for d in data:
            rows.append({
                "slug": d.get("id"),
                "symbol": (d.get("symbol") or "").upper()[:32],
                "name": (d.get("name") or "")[:256],
                "price_usd": d.get("current_price"),
                "volume_last_24h": d.get("total_volume"),
                "percent_change_1h": d.get("price_change_percentage_1h_in_currency"),
                "percent_change_24h": d.get("price_change_percentage_24h_in_currency"),
                "percent_change_7d": d.get("price_change_percentage_7d_in_currency"),
                "ohlcv_last_24h_high": d.get("high_24h"),
                "ohlcv_last_24h_low": d.get("low_24h"),
                "current_marketcap_usd": d.get("market_cap"),
                "circulating_supply": d.get("circulating_supply"),
                "total_supply": d.get("total_supply"),
                "max_supply": d.get("max_supply"),
                "roi_1m": d.get("price_change_percentage_30d_in_currency"),
                "roi_1y": d.get("price_change_percentage_1y_in_currency"),
                "fetched_at": now,
            })
        logger.info("coingecko.fetch_markets: %d rows for %d ids", len(rows), len(ids))
        return rows
    except Exception as exc:
        logger.error("coingecko.fetch_markets failed: %s", exc)
        raise


# ── Developer data (per-asset enrichment) ─────────────────────────────────────

def fetch_developer_data(coin_id: str) -> dict | None:
    """GitHub-style developer stats. One call per asset."""
    try:
        data = _get(f"/coins/{coin_id}", params={
            "localization": "false",
            "tickers": "false",
            "market_data": "false",
            "community_data": "false",
            "developer_data": "true",
            "sparkline": "false",
        })
        dev = data.get("developer_data") or {}
        return {
            "slug": coin_id,
            "github_stars": dev.get("stars"),
            "github_watchers": dev.get("subscribers"),
            "github_forks": dev.get("forks"),
            "github_commits_last_3_months": dev.get("commit_count_4_weeks"),  # closest match
        }
    except Exception as exc:
        logger.warning("coingecko.fetch_developer_data(%s) failed: %s", coin_id, exc)
        return None


# ── Global market data ────────────────────────────────────────────────────────

def fetch_global() -> dict | None:
    """Global crypto market snapshot."""
    try:
        data = _get("/global")
        d = (data.get("data") or {})
        mc_pct = d.get("market_cap_percentage") or {}
        total_mc = d.get("total_market_cap") or {}
        total_vol = d.get("total_volume") or {}
        now = datetime.now(timezone.utc)
        return {
            "bitcoin_dominance_pct": mc_pct.get("btc"),
            "ethereum_dominance_pct": mc_pct.get("eth"),
            "total_market_cap_usd": total_mc.get("usd"),
            "volume_24h_usd": total_vol.get("usd"),
            "active_cryptocurrencies": d.get("active_cryptocurrencies"),
            "active_markets": d.get("markets"),
            "fetched_at": now,
        }
    except Exception as exc:
        logger.error("coingecko.fetch_global failed: %s", exc)
        raise


# ── OHLC price history (per-asset) ────────────────────────────────────────────

def fetch_ohlc(coin_id: str, days: int = 30) -> list[dict]:
    """
    Daily OHLC price history. CoinGecko returns [[timestamp_ms, open, high, low, close], ...]
    Note: no volume in /ohlc endpoint — that field stays NULL.
    """
    try:
        data = _get(f"/coins/{coin_id}/ohlc", params={"vs_currency": "usd", "days": days})
        now = datetime.now(timezone.utc)
        rows = []
        for row in data:
            if len(row) < 5:
                continue
            ts_ms, o, h, l, c = row
            rows.append({
                "slug": coin_id,
                "timestamp": datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": None,  # /ohlc doesn't return volume
                "fetched_at": now,
            })
        logger.info("coingecko.fetch_ohlc(%s): %d rows", coin_id, len(rows))
        return rows
    except Exception as exc:
        logger.warning("coingecko.fetch_ohlc(%s) failed: %s", coin_id, exc)
        return []


# ── Merger helper ─────────────────────────────────────────────────────────────

def merge_metrics(market_row: dict, dev_row: dict | None) -> dict:
    """Combine market data + developer data into one messari_asset_metrics row."""
    if dev_row:
        market_row.update({
            "github_stars": dev_row.get("github_stars"),
            "github_watchers": dev_row.get("github_watchers"),
            "github_forks": dev_row.get("github_forks"),
            "github_commits_last_3_months": dev_row.get("github_commits_last_3_months"),
        })
    return market_row
