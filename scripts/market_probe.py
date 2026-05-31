#!/usr/bin/env python3
"""Public, no-key market discovery probe for the overnight profit research.

This is intentionally a measurement script, not the trading engine. It pulls
public REST ticker/market metadata, normalizes spot markets, and ranks same-lane
top-of-book routes after simple taker-fee assumptions.
"""

from __future__ import annotations

import json
import math
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

QUOTES = {"USDT", "USDC", "USD", "MXN", "EUR"}
PRIORITY_BASES = {
    "BTC", "ETH", "SOL", "XRP", "DOGE", "LTC", "ADA", "AVAX", "LINK",
    "SUI", "TON", "NEAR", "APT", "ARB", "OP", "BCH", "TRX", "DOT", "INJ",
    "SEI", "BNB", "XLM", "HBAR", "AAVE", "ONDO", "UNI", "FIL", "PEPE",
    "RENDER", "WLD", "FET",
}

# bps. Expansion venues use public baseline fees where already known; treat
# source docs in docs/overnight-profit-opportunities.md as the authority.
TAKER_BPS = {
    "binance": 10.0,
    "bybit": 10.0,
    "okx": 10.0,
    "coinbase": 120.0,
    "kraken": 40.0,
    "gemini": 120.0,
    "gate": 10.0,
    "kucoin": 10.0,
    "mexc": 5.0,
    "bitget": 10.0,
    "cryptocom": 7.5,
    "bitfinex": 0.0,
    "bitstamp": 40.0,
    "bitso": 50.0,
}


@dataclass
class Market:
    exchange: str
    symbol: str
    base: str
    quote: str
    bid: float | None = None
    ask: float | None = None
    quote_volume: float | None = None

    @property
    def key(self) -> tuple[str, str]:
        return self.base, self.quote

    @property
    def spread_bps(self) -> float | None:
        if not self.bid or not self.ask or self.bid <= 0:
            return None
        return (self.ask - self.bid) / self.bid * 10_000


def fetch_json(url: str, timeout: float = 10.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hackathon-btc-market-probe/0.1",
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
        if not math.isfinite(parsed) or parsed <= 0:
            return None
        return parsed
    except (TypeError, ValueError):
        return None


def split_symbol(symbol: str) -> tuple[str, str] | None:
    for sep in ("-", "_", "/"):
        if sep in symbol:
            base, quote = symbol.split(sep, 1)
            return base.upper(), quote.upper()
    for quote in sorted(QUOTES, key=len, reverse=True):
        if symbol.upper().endswith(quote):
            return symbol[:-len(quote)].upper(), quote
    return None


def binance() -> list[Market]:
    rows = fetch_json("https://api.binance.com/api/v3/ticker/24hr")
    markets = []
    for row in rows:
        split = split_symbol(row["symbol"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "binance",
                    row["symbol"],
                    base,
                    quote,
                    f(row.get("bidPrice")),
                    f(row.get("askPrice")),
                    f(row.get("quoteVolume")),
                )
            )
    return markets


def bybit() -> list[Market]:
    data = fetch_json("https://api.bybit.com/v5/market/tickers?category=spot")
    markets = []
    for row in data.get("result", {}).get("list", []):
        split = split_symbol(row["symbol"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "bybit",
                    row["symbol"],
                    base,
                    quote,
                    f(row.get("bid1Price")),
                    f(row.get("ask1Price")),
                    f(row.get("turnover24h")),
                )
            )
    return markets


def okx() -> list[Market]:
    data = fetch_json("https://www.okx.com/api/v5/market/tickers?instType=SPOT")
    markets = []
    for row in data.get("data", []):
        split = split_symbol(row["instId"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "okx",
                    row["instId"],
                    base,
                    quote,
                    f(row.get("bidPx")),
                    f(row.get("askPx")),
                    f(row.get("volCcy24h")) or f(row.get("vol24h")),
                )
            )
    return markets


def gate() -> list[Market]:
    rows = fetch_json("https://api.gateio.ws/api/v4/spot/tickers")
    markets = []
    for row in rows:
        split = split_symbol(row["currency_pair"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "gate",
                    row["currency_pair"],
                    base,
                    quote,
                    f(row.get("highest_bid")),
                    f(row.get("lowest_ask")),
                    f(row.get("quote_volume")),
                )
            )
    return markets


def kucoin() -> list[Market]:
    data = fetch_json("https://api.kucoin.com/api/v1/market/allTickers")
    markets = []
    for row in data.get("data", {}).get("ticker", []):
        split = split_symbol(row["symbol"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "kucoin",
                    row["symbol"],
                    base,
                    quote,
                    f(row.get("buy")),
                    f(row.get("sell")),
                    f(row.get("volValue")),
                )
            )
    return markets


def mexc() -> list[Market]:
    rows = fetch_json("https://api.mexc.com/api/v3/ticker/24hr")
    markets = []
    for row in rows:
        split = split_symbol(row["symbol"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "mexc",
                    row["symbol"],
                    base,
                    quote,
                    f(row.get("bidPrice")),
                    f(row.get("askPrice")),
                    f(row.get("quoteVolume")),
                )
            )
    return markets


def bitget() -> list[Market]:
    data = fetch_json("https://api.bitget.com/api/v2/spot/market/tickers")
    markets = []
    for row in data.get("data", []):
        split = split_symbol(row["symbol"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "bitget",
                    row["symbol"],
                    base,
                    quote,
                    f(row.get("bidPr")),
                    f(row.get("askPr")),
                    f(row.get("quoteVolume")),
                )
            )
    return markets


def cryptocom() -> list[Market]:
    data = fetch_json("https://api.crypto.com/exchange/v1/public/get-tickers")
    markets = []
    for row in data.get("result", {}).get("data", []):
        split = split_symbol(row["i"])
        if not split:
            continue
        base, quote = split
        if quote in QUOTES:
            markets.append(
                Market(
                    "cryptocom",
                    row["i"],
                    base,
                    quote,
                    f(row.get("b")),
                    f(row.get("k")),
                    f(row.get("vv")),
                )
            )
    return markets


def bitso() -> list[Market]:
    books = fetch_json("https://api.bitso.com/v3/available_books/").get("payload", [])
    markets = []
    for book in books:
        symbol = book["book"]
        split = split_symbol(symbol)
        if not split:
            continue
        base, quote = split
        if quote not in QUOTES:
            continue
        try:
            ticker = fetch_json(f"https://api.bitso.com/v3/ticker/?book={symbol}").get("payload", {})
        except Exception:
            ticker = {}
        markets.append(
            Market(
                "bitso",
                symbol,
                base,
                quote,
                f(ticker.get("bid")),
                f(ticker.get("ask")),
                f(ticker.get("volume")) * f(ticker.get("last")) if f(ticker.get("volume")) and f(ticker.get("last")) else None,
            )
        )
    return markets


def bitfinex() -> list[Market]:
    rows = fetch_json("https://api-pub.bitfinex.com/v2/tickers?symbols=ALL")
    markets = []
    for row in rows:
        symbol = row[0]
        if not isinstance(symbol, str) or not symbol.startswith("t"):
            continue
        raw = symbol[1:]
        split = split_symbol(raw)
        if not split:
            continue
        base, quote = split
        if quote not in QUOTES:
            continue
        markets.append(
            Market(
                "bitfinex",
                symbol,
                base,
                quote,
                f(row[1]),  # bid
                f(row[3]),  # ask
                (f(row[8]) or 0.0) * (f(row[7]) or 0.0),  # rough quote volume
            )
        )
    return markets


FETCHERS = [binance, bybit, okx, gate, kucoin, mexc, bitget, cryptocom, bitfinex, bitso]


def route_candidates(markets: list[Market]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], list[Market]] = {}
    for market in markets:
        if market.bid and market.ask and market.quote in QUOTES:
            by_key.setdefault(market.key, []).append(market)

    routes = []
    for (base, quote), venues in by_key.items():
        if len({v.exchange for v in venues}) < 2:
            continue
        for buy in venues:
            for sell in venues:
                if buy.exchange == sell.exchange:
                    continue
                if not buy.ask or not sell.bid or sell.bid <= buy.ask:
                    continue
                gross_bps = (sell.bid - buy.ask) / buy.ask * 10_000
                fee_bps = TAKER_BPS.get(buy.exchange, 20.0) + TAKER_BPS.get(sell.exchange, 20.0)
                latency_bps = 2.0 if quote in {"USDT", "USDC"} else 4.0
                net_bps = gross_bps - fee_bps - latency_bps
                route_depth_proxy = min(
                    buy.quote_volume or 0.0,
                    sell.quote_volume or 0.0,
                )
                routes.append(
                    {
                        "base": base,
                        "quote": quote,
                        "buy_exchange": buy.exchange,
                        "sell_exchange": sell.exchange,
                        "buy_symbol": buy.symbol,
                        "sell_symbol": sell.symbol,
                        "buy_ask": buy.ask,
                        "sell_bid": sell.bid,
                        "gross_bps": gross_bps,
                        "fee_bps": fee_bps,
                        "latency_bps": latency_bps,
                        "net_bps": net_bps,
                        "depth_proxy_24h_quote": route_depth_proxy,
                    }
                )
    return sorted(routes, key=lambda row: row["net_bps"], reverse=True)


def main() -> int:
    all_markets: list[Market] = []
    errors = []
    for fetcher in FETCHERS:
        started = time.time()
        try:
            markets = fetcher()
            all_markets.extend(markets)
            print(f"[OK] {fetcher.__name__}: {len(markets)} markets in {time.time() - started:.1f}s", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as exc:
            errors.append({"exchange": fetcher.__name__, "error": str(exc)})
            print(f"[ERR] {fetcher.__name__}: {exc}", file=sys.stderr)

    by_quote: dict[str, int] = {}
    by_exchange: dict[str, int] = {}
    common: dict[str, list[tuple[str, int, float]]] = {}
    by_key: dict[tuple[str, str], list[Market]] = {}
    for market in all_markets:
        by_quote[market.quote] = by_quote.get(market.quote, 0) + 1
        by_exchange[market.exchange] = by_exchange.get(market.exchange, 0) + 1
        by_key.setdefault(market.key, []).append(market)

    for (base, quote), venues in by_key.items():
        venue_count = len({v.exchange for v in venues})
        if venue_count >= 2:
            quote_volume = sum(v.quote_volume or 0.0 for v in venues)
            common.setdefault(quote, []).append((base, venue_count, quote_volume))

    for quote in list(common):
        common[quote] = sorted(
            common[quote],
            key=lambda item: (item[1], item[2]),
            reverse=True,
        )[:40]

    routes = route_candidates(all_markets)
    sane_priority_routes = [
        row
        for row in routes
        if row["base"] in PRIORITY_BASES
        and row["depth_proxy_24h_quote"] >= 100_000
        and row["gross_bps"] <= 1_000
    ][:50]

    output = {
        "generated_at": int(time.time()),
        "markets_total": len(all_markets),
        "markets_by_exchange": dict(sorted(by_exchange.items())),
        "markets_by_quote": dict(sorted(by_quote.items())),
        "common_markets_top": common,
        "top_routes": routes[:50],
        "sane_priority_routes": sane_priority_routes,
        "errors": errors,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
