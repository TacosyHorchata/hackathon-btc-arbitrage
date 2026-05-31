#!/usr/bin/env python3
"""Public, no-key spot/perp funding probe.

This is a measurement script. It does not trade and it does not require private
API keys. It ranks hedged spot/perp carry candidates by a conservative one
funding-period proxy:

    abs(funding_bps) + entry_basis_bps - 2 * (spot_taker_bps + perp_taker_bps)

Positive funding direction: long spot + short perp.
Negative funding direction: long perp + short/borrow spot.
"""

from __future__ import annotations

import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

ASSETS = ["BTC", "ETH", "DOGE", "BCH", "TRX", "WLD", "SOL", "XRP", "SUI", "ADA", "AVAX", "LINK", "LTC", "ARB"]

FEE_ASSUMPTIONS_BPS = {
    "binance": {"spot_taker": 10.0, "perp_taker": 5.0, "interval": "8h"},
    "bybit": {"spot_taker": 10.0, "perp_taker": 5.5, "interval": "8h"},
    "okx": {"spot_taker": 10.0, "perp_taker": 5.0, "interval": "8h"},
    "coinbase_intx": {"spot_taker": 2.0, "perp_taker": 4.0, "interval": "1h"},
}

SOURCES = {
    "binance": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price",
    "bybit": "https://bybit-exchange.github.io/docs/v5/market/tickers",
    "okx": "https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate",
    "coinbase_intx": "https://docs.cdp.coinbase.com/api-reference/international-exchange-api/rest-api/instruments/get-quote-per-instrument",
}


@dataclass
class Quote:
    bid: float | None = None
    ask: float | None = None
    mark: float | None = None
    funding_bps: float | None = None
    next_funding_time: str | int | None = None
    notional_24h: float | None = None
    timestamp: str | int | None = None


def fetch_json(url: str, timeout: float = 10.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hackathon-btc-funding-probe/0.1",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def f(value: Any) -> float | None:
    try:
        if value in (None, "", "0", 0):
            return None
        parsed = float(value)
        if not math.isfinite(parsed):
            return None
        return parsed
    except (TypeError, ValueError):
        return None


def parse_epoch_ms(value: Any) -> str | int | None:
    parsed = f(value)
    if parsed is None:
        return value
    return int(parsed)


def route_score(
    venue: str,
    asset: str,
    quote: str,
    spot: Quote,
    perp: Quote,
) -> dict[str, Any] | None:
    if not spot.bid or not spot.ask or not perp.bid or not perp.ask or perp.funding_bps is None:
        return None

    fees = FEE_ASSUMPTIONS_BPS[venue]
    entry_fee_bps = fees["spot_taker"] + fees["perp_taker"]
    round_trip_fee_bps = 2.0 * entry_fee_bps
    funding_bps = perp.funding_bps

    if funding_bps >= 0:
        direction = "long_spot_short_perp"
        entry_basis_bps = (perp.bid - spot.ask) / spot.ask * 10_000
        inventory_requirement = "spot inventory or quote balance; perp margin"
    else:
        direction = "long_perp_short_or_borrow_spot"
        entry_basis_bps = (spot.bid - perp.ask) / perp.ask * 10_000
        inventory_requirement = "spot borrow or existing spot inventory to sell short; perp margin"

    net_one_period_bps_proxy = abs(funding_bps) + entry_basis_bps - round_trip_fee_bps
    return {
        "venue": venue,
        "asset": asset,
        "quote": quote,
        "direction": direction,
        "spot_bid": spot.bid,
        "spot_ask": spot.ask,
        "perp_bid": perp.bid,
        "perp_ask": perp.ask,
        "perp_mark": perp.mark,
        "funding_bps": funding_bps,
        "funding_interval": fees["interval"],
        "entry_basis_bps": entry_basis_bps,
        "entry_fee_bps": entry_fee_bps,
        "round_trip_fee_bps": round_trip_fee_bps,
        "net_one_period_bps_proxy": net_one_period_bps_proxy,
        "perp_notional_24h": perp.notional_24h,
        "next_funding_time": perp.next_funding_time,
        "timestamp": perp.timestamp or spot.timestamp,
        "inventory_requirement": inventory_requirement,
        "decision": "MEASURE" if net_one_period_bps_proxy > 0 else "REJECT_PROXY_NEGATIVE",
    }


def binance_routes() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    routes: list[dict[str, Any]] = []
    try:
        spot_books = {row["symbol"]: row for row in fetch_json("https://api.binance.com/api/v3/ticker/bookTicker")}
        perp_books = {row["symbol"]: row for row in fetch_json("https://fapi.binance.com/fapi/v1/ticker/bookTicker")}
        premiums = {row["symbol"]: row for row in fetch_json("https://fapi.binance.com/fapi/v1/premiumIndex")}
        volumes = {row["symbol"]: row for row in fetch_json("https://fapi.binance.com/fapi/v1/ticker/24hr")}
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as exc:
        return [], [{"venue": "binance", "error": str(exc)}]

    for asset in ASSETS:
        symbol = f"{asset}USDT"
        try:
            spot_row = spot_books[symbol]
            perp_row = perp_books[symbol]
            premium_row = premiums[symbol]
            volume_row = volumes.get(symbol, {})
            spot = Quote(bid=f(spot_row.get("bidPrice")), ask=f(spot_row.get("askPrice")))
            perp = Quote(
                bid=f(perp_row.get("bidPrice")),
                ask=f(perp_row.get("askPrice")),
                mark=f(premium_row.get("markPrice")),
                funding_bps=(f(premium_row.get("lastFundingRate")) or 0.0) * 10_000,
                next_funding_time=parse_epoch_ms(premium_row.get("nextFundingTime")),
                notional_24h=f(volume_row.get("quoteVolume")),
                timestamp=parse_epoch_ms(premium_row.get("time")),
            )
            scored = route_score("binance", asset, "USDT", spot, perp)
            if scored:
                routes.append(scored)
        except KeyError as exc:
            errors.append({"venue": "binance", "asset": asset, "error": f"missing {exc}"})
    return routes, errors


def bybit_routes() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    routes: list[dict[str, Any]] = []
    try:
        spot_rows = fetch_json("https://api.bybit.com/v5/market/tickers?category=spot").get("result", {}).get("list", [])
        linear_rows = fetch_json("https://api.bybit.com/v5/market/tickers?category=linear").get("result", {}).get("list", [])
        spot_books = {row["symbol"]: row for row in spot_rows}
        perps = {row["symbol"]: row for row in linear_rows}
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as exc:
        return [], [{"venue": "bybit", "error": str(exc)}]

    for asset in ASSETS:
        symbol = f"{asset}USDT"
        try:
            spot_row = spot_books[symbol]
            perp_row = perps[symbol]
            spot = Quote(bid=f(spot_row.get("bid1Price")), ask=f(spot_row.get("ask1Price")))
            perp = Quote(
                bid=f(perp_row.get("bid1Price")),
                ask=f(perp_row.get("ask1Price")),
                mark=f(perp_row.get("markPrice")),
                funding_bps=(f(perp_row.get("fundingRate")) or 0.0) * 10_000,
                next_funding_time=parse_epoch_ms(perp_row.get("nextFundingTime")),
                notional_24h=f(perp_row.get("turnover24h")),
            )
            scored = route_score("bybit", asset, "USDT", spot, perp)
            if scored:
                routes.append(scored)
        except KeyError as exc:
            errors.append({"venue": "bybit", "asset": asset, "error": f"missing {exc}"})
    return routes, errors


def okx_routes() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    routes: list[dict[str, Any]] = []
    try:
        spot_rows = fetch_json("https://www.okx.com/api/v5/market/tickers?instType=SPOT").get("data", [])
        swap_rows = fetch_json("https://www.okx.com/api/v5/market/tickers?instType=SWAP").get("data", [])
        mark_rows = fetch_json("https://www.okx.com/api/v5/public/mark-price?instType=SWAP").get("data", [])
        spot_books = {row["instId"]: row for row in spot_rows}
        swaps = {row["instId"]: row for row in swap_rows}
        marks = {row["instId"]: row for row in mark_rows}
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as exc:
        return [], [{"venue": "okx", "error": str(exc)}]

    for asset in ASSETS:
        spot_symbol = f"{asset}-USDT"
        swap_symbol = f"{asset}-USDT-SWAP"
        try:
            spot_row = spot_books[spot_symbol]
            swap_row = swaps[swap_symbol]
            mark_row = marks.get(swap_symbol, {})
            funding = fetch_json(
                "https://www.okx.com/api/v5/public/funding-rate?"
                + urllib.parse.urlencode({"instId": swap_symbol})
            ).get("data", [{}])[0]
            spot = Quote(bid=f(spot_row.get("bidPx")), ask=f(spot_row.get("askPx")))
            perp = Quote(
                bid=f(swap_row.get("bidPx")),
                ask=f(swap_row.get("askPx")),
                mark=f(mark_row.get("markPx")),
                funding_bps=(f(funding.get("fundingRate")) or 0.0) * 10_000,
                next_funding_time=parse_epoch_ms(funding.get("fundingTime")),
                notional_24h=f(swap_row.get("volCcy24h")) or f(swap_row.get("vol24h")),
                timestamp=parse_epoch_ms(swap_row.get("ts")),
            )
            scored = route_score("okx", asset, "USDT", spot, perp)
            if scored:
                routes.append(scored)
        except (KeyError, IndexError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            errors.append({"venue": "okx", "asset": asset, "error": str(exc)})
    return routes, errors


def coinbase_intx_routes() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    routes: list[dict[str, Any]] = []
    instruments: dict[str, Any] = {}
    try:
        instruments = {
            row["symbol"]: row
            for row in fetch_json("https://api.international.coinbase.com/api/v1/instruments")
            if isinstance(row, dict) and row.get("symbol")
        }
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as exc:
        errors.append({"venue": "coinbase_intx", "asset": "ALL", "error": f"instruments: {exc}"})

    for asset in ["BTC", "ETH", "DOGE", "SOL", "XRP"]:
        try:
            perp_row = fetch_json(f"https://api.international.coinbase.com/api/v1/instruments/{asset}-PERP/quote")
            spot_row = fetch_json(f"https://api.international.coinbase.com/api/v1/instruments/{asset}-USDC/quote")
            perp_meta = instruments.get(f"{asset}-PERP", {})
            spot = Quote(
                bid=f(spot_row.get("best_bid_price")),
                ask=f(spot_row.get("best_ask_price")),
                mark=f(spot_row.get("mark_price")),
                timestamp=spot_row.get("timestamp"),
            )
            perp = Quote(
                bid=f(perp_row.get("best_bid_price")),
                ask=f(perp_row.get("best_ask_price")),
                mark=f(perp_row.get("mark_price")),
                funding_bps=(f(perp_row.get("predicted_funding")) or 0.0) * 10_000,
                notional_24h=f(perp_meta.get("notional_24hr")) or f(perp_meta.get("avg_daily_notional")),
                timestamp=perp_row.get("timestamp"),
            )
            scored = route_score("coinbase_intx", asset, "USDC", spot, perp)
            if scored:
                routes.append(scored)
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as exc:
            errors.append({"venue": "coinbase_intx", "asset": asset, "error": str(exc)})
    return routes, errors


def main() -> int:
    started = time.time()
    routes: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for fetcher in (binance_routes, bybit_routes, okx_routes, coinbase_intx_routes):
        venue_started = time.time()
        venue_routes, venue_errors = fetcher()
        routes.extend(venue_routes)
        errors.extend(venue_errors)
        print(
            f"[OK] {fetcher.__name__}: {len(venue_routes)} routes, {len(venue_errors)} errors in {time.time() - venue_started:.1f}s",
            file=sys.stderr,
        )

    routes.sort(key=lambda row: row["net_one_period_bps_proxy"], reverse=True)
    output = {
        "generated_at": int(time.time()),
        "elapsed_seconds": round(time.time() - started, 3),
        "assumptions": {
            "formula": "abs(funding_bps) + entry_basis_bps - 2 * (spot_taker_bps + perp_taker_bps)",
            "fees_bps": FEE_ASSUMPTIONS_BPS,
            "sources": SOURCES,
            "notes": [
                "Positive proxy is not an execution signal; it requires borrow/inventory, margin, duration, and exit validation.",
                "Negative-funding routes require long perp plus short/borrow spot, which is materially harder than long spot plus short perp.",
            ],
        },
        "routes": routes,
        "top_routes": routes[:20],
        "errors": errors,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
