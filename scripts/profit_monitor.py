#!/usr/bin/env python3
"""Continuous public-market arbitrage monitor.

This is a no-key, no-trading monitor. It dynamically discovers public spot
markets across many venues, ranks same-quote routes, depth-checks the best
candidates, and persists only routes that remain profitable after taker fees,
book walking, and a latency haircut.

Execution model: inventory-based arbitrage. A saved opportunity assumes quote
inventory already exists on the buy venue and base inventory already exists on
the sell venue. Transfers and withdrawals are slow rebalance operations and are
not counted as hot-path execution.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import math
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Any, Callable, Iterable

getcontext().prec = 40

DEFAULT_QUOTES = {
    "BTC",
    "ETH",
    "BNB",
    "USDT",
    "USDC",
    "USD",
    "USDS",
    "MXN",
    "COP",
    "CNYT",
    "EUR",
    "GBP",
    "BRL",
    "ARS",
    "CLP",
    "PEN",
    "TRY",
    "PHP",
    "TWD",
    "JPY",
    "AUD",
    "CAD",
    "CHF",
    "KRW",
    "IDR",
    "UAH",
    "PLN",
    "RUB",
    "ZAR",
    "THB",
    "MYR",
    "NGN",
    "UGX",
    "SGD",
    "HKD",
    "NZD",
    "FDUSD",
    "TUSD",
    "DAI",
    "USDE",
    "PYUSD",
    "RLUSD",
    "USDD",
}

DEFAULT_TAKER_BPS = {
    "binance": Decimal("10"),
    "binanceus": Decimal("2"),
    "bybit": Decimal("10"),
    "okx": Decimal("10"),
    "gate": Decimal("10"),
    "kucoin": Decimal("10"),
    "mexc": Decimal("5"),
    "bitget": Decimal("10"),
    "bitmex": Decimal("5"),
    "cryptocom": Decimal("7.5"),
    "deribit": Decimal("0"),
    "hitbtc": Decimal("25"),
    "bitfinex": Decimal("0"),
    "bitstamp": Decimal("40"),
    "bitso": Decimal("50"),
    "bullish": Decimal("10"),
    "coincheck": Decimal("10"),
    "coinex": Decimal("20"),
    "cointr": Decimal("10"),
    "coinw": Decimal("20"),
    "coinsph": Decimal("10"),
    "htx": Decimal("20"),
    "bitmart": Decimal("25"),
    "kraken": Decimal("40"),
    "gemini": Decimal("120"),
    "lbank": Decimal("10"),
    "poloniex": Decimal("14.5"),
    "ascendex": Decimal("10"),
    "exmo": Decimal("30"),
    "btcturk": Decimal("20"),
    "cexio": Decimal("25"),
    "whitebit": Decimal("10"),
    "upbit": Decimal("25"),
    "indodax": Decimal("30"),
    "buda": Decimal("80"),
    "novadax": Decimal("25"),
    "foxbit": Decimal("50"),
    "mercadobitcoin": Decimal("70"),
    "bitvavo": Decimal("25"),
    "luno": Decimal("25"),
    "valr": Decimal("10"),
    "bitkub": Decimal("25"),
    "bitflyer": Decimal("15"),
    "bithumb": Decimal("25"),
    "bitbank": Decimal("12"),
    "bitrue": Decimal("10"),
    "coinone": Decimal("20"),
    "korbit": Decimal("20"),
    "gmocoin": Decimal("5"),
    "independentreserve": Decimal("50"),
    "btcmarkets": Decimal("85"),
    "ndax": Decimal("20"),
    "bitopro": Decimal("20"),
    "digifinex": Decimal("20"),
    "hashkey": Decimal("10"),
    "hyperliquid": Decimal("10"),
    "latoken": Decimal("20"),
    "toobit": Decimal("10"),
    "xt": Decimal("20"),
    "bingx": Decimal("10"),
    "backpack": Decimal("10"),
    "phemex": Decimal("10"),
    "pionex": Decimal("10"),
    "woox": Decimal("10"),
}

DEFAULT_QUOTE_NOTIONALS = {
    "BTC": "0.001,0.005,0.01,0.02,0.05",
    "ETH": "0.05,0.2,0.5,1,2",
    "BNB": "0.2,1,2,5,10",
    "MXN": "1000,5000,10000,50000,100000,200000",
    "COP": "100000,500000,1000000,2500000,5000000,10000000",
    "BRL": "500,2500,5000,10000,25000",
    "ARS": "100000,500000,1000000,2500000,5000000",
    "CLP": "100000,500000,1000000,2500000,5000000",
    "CNYT": "1000,5000,10000,50000,100000",
    "PEN": "500,2500,5000,10000,25000",
    "TRY": "5000,25000,50000,100000,250000",
    "PHP": "5000,25000,50000,100000,250000,500000",
    "TWD": "1000,5000,10000,50000,100000,250000",
    "CAD": "100,500,1000,2500,5000,10000",
    "JPY": "10000,50000,100000,500000,1000000",
    "KRW": "100000,500000,1000000,5000000,10000000",
    "IDR": "1000000,5000000,10000000,50000000,100000000",
    "UAH": "5000,25000,50000,100000,250000",
    "PLN": "500,2500,5000,10000,25000",
    "RUB": "10000,50000,100000,500000,1000000",
    "ZAR": "1000,5000,10000,50000,100000",
    "THB": "1000,5000,10000,50000,100000",
    "MYR": "100,500,1000,2500,5000",
    "NGN": "100000,500000,1000000,2500000,5000000",
    "UGX": "100000,500000,1000000,2500000,5000000",
    "SGD": "100,500,1000,2500,5000",
    "HKD": "1000,5000,10000,25000,50000",
    "NZD": "100,500,1000,2500,5000",
}

DEFAULT_MIN_VOLUME_BY_QUOTE = {
    "BTC": Decimal("1"),
    "ETH": Decimal("25"),
    "BNB": Decimal("150"),
}

DEFAULT_STATUS_DB = Path.home() / "Library/Application Support/hackathon-btc/status/status.sqlite"

DEFAULT_EXCHANGE_NAMES = {
    "binance",
    "binanceus",
    "backpack",
    "bitfinex",
    "bitget",
    "bitbank",
    "bitflyer",
    "bitmart",
    "bitmex",
    "bitopro",
    "bitso",
    "bitstamp",
    "bitvavo",
    "bithumb",
    "bitkub",
    "bitrue",
    "btcmarkets",
    "bybit",
    "buda",
    "foxbit",
    "coinbase",
    "coincheck",
    "coinex",
    "coinone",
    "cointr",
    "coinw",
    "coinsph",
    "cryptocom",
    "deribit",
    "digifinex",
    "gate",
    "gemini",
    "gmocoin",
    "hitbtc",
    "hashkey",
    "hyperliquid",
    "htx",
    "ascendex",
    "btcturk",
    "cexio",
    "exmo",
    "independentreserve",
    "kraken",
    "korbit",
    "kucoin",
    "latoken",
    "luno",
    "mercadobitcoin",
    "mexc",
    "ndax",
    "novadax",
    "okx",
    "poloniex",
    "phemex",
    "toobit",
    "indodax",
    "upbit",
    "valr",
    "whitebit",
    "bingx",
    "xt",
}

BITFINEX_QUOTE_ALIASES = {
    "UST": "USDT",
}

PRIORITY_BASES = {
    "BTC",
    "ETH",
    "SOL",
    "XRP",
    "DOGE",
    "LTC",
    "BCH",
    "ADA",
    "AVAX",
    "LINK",
    "SUI",
    "TON",
    "NEAR",
    "XLM",
}


@dataclass(frozen=True)
class Market:
    exchange: str
    symbol: str
    base: str
    quote: str
    bid: Decimal
    ask: Decimal
    quote_volume: Decimal | None
    taker_bps: Decimal
    exchange_ts_ms: int | None = None

    @property
    def key(self) -> tuple[str, str]:
        return self.base, self.quote


@dataclass(frozen=True)
class RouteCandidate:
    base: str
    quote: str
    buy_exchange: str
    sell_exchange: str
    buy_symbol: str
    sell_symbol: str
    buy_ask: Decimal
    sell_bid: Decimal
    buy_taker_bps: Decimal
    sell_taker_bps: Decimal
    gross_bps: Decimal
    fee_bps: Decimal
    latency_bps: Decimal
    top_net_bps: Decimal
    depth_proxy_quote: Decimal | None

    @property
    def route_key(self) -> str:
        return (
            f"{self.base}/{self.quote}:"
            f"{self.buy_exchange}:{self.buy_symbol}->"
            f"{self.sell_exchange}:{self.sell_symbol}"
        )


@dataclass(frozen=True)
class Fill:
    requested_quote: Decimal
    base: Decimal
    quote: Decimal
    avg_price: Decimal | None
    full: bool
    levels: int


@dataclass(frozen=True)
class SellFill:
    requested_base: Decimal
    base: Decimal
    quote: Decimal
    avg_price: Decimal | None
    full: bool
    levels: int


@dataclass(frozen=True)
class Opportunity:
    detected_at_ms: int
    mode: str
    base: str
    quote: str
    buy_exchange: str
    sell_exchange: str
    buy_symbol: str
    sell_symbol: str
    notional_quote: Decimal
    base_size: Decimal
    buy_avg: Decimal
    sell_avg: Decimal
    buy_quote: Decimal
    sell_quote: Decimal
    buy_fee_quote: Decimal
    sell_fee_quote: Decimal
    latency_haircut_quote: Decimal
    net_profit_quote: Decimal
    net_bps: Decimal
    gross_bps: Decimal
    top_net_bps: Decimal
    buy_levels: int
    sell_levels: int
    depth_proxy_quote: Decimal | None
    evidence_json: str
    operational_grade: str = "status_unavailable"
    status_hint: str = ""
    status_json: str = "{}"

    @property
    def route_key(self) -> str:
        return (
            f"{self.base}/{self.quote}:"
            f"{self.buy_exchange}:{self.buy_symbol}->"
            f"{self.sell_exchange}:{self.sell_symbol}"
        )


class MonitorError(Exception):
    pass


def dec(value: Any) -> Decimal | None:
    try:
        if value in (None, "", "0", 0):
            return None
        parsed = Decimal(str(value))
        if not parsed.is_finite() or parsed <= 0:
            return None
        return parsed
    except (InvalidOperation, ValueError):
        return None


def now_ms() -> int:
    return int(time.time() * 1000)


def fetch_json(url: str, timeout: float = 12.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hackathon-btc-profit-monitor/0.1",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def post_json(url: str, payload: dict[str, Any], timeout: float = 12.0) -> Any:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "User-Agent": "hackathon-btc-profit-monitor/0.1",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        response_payload = response.read().decode("utf-8")
    return json.loads(response_payload)


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def fetch_many(items: list[Any], worker_env: str, default_workers: int, fn: Callable[[Any], Any]) -> list[Any]:
    if not items:
        return []
    workers = max(1, min(len(items), env_int(worker_env, default_workers)))
    if workers == 1:
        out: list[Any] = []
        for item in items:
            try:
                out.append(fn(item))
            except Exception:
                continue
        return out
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fn, item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            try:
                out.append(future.result())
            except Exception:
                continue
    return out


def chunks(items: list[Any], size: int) -> Iterable[list[Any]]:
    size = max(1, size)
    for index in range(0, len(items), size):
        yield items[index : index + size]


def split_symbol(symbol: str, quotes: set[str]) -> tuple[str, str] | None:
    upper = symbol.upper()
    for sep in ("-", "_", "/"):
        if sep in upper:
            base, quote = upper.split(sep, 1)
            if base and quote in quotes:
                return base, quote
    for quote in sorted(quotes, key=len, reverse=True):
        if upper.endswith(quote) and len(upper) > len(quote):
            return upper[: -len(quote)], quote
    return None


def split_bitfinex_symbol(symbol: str, quotes: set[str]) -> tuple[str, str] | None:
    upper = symbol.upper()
    candidate_quotes = quotes | set(BITFINEX_QUOTE_ALIASES)
    if ":" in upper:
        base, quote = upper.split(":", 1)
        normalized_quote = BITFINEX_QUOTE_ALIASES.get(quote, quote)
        if base and normalized_quote in quotes:
            return base, normalized_quote
        return None
    for quote in sorted(candidate_quotes, key=len, reverse=True):
        if upper.endswith(quote) and len(upper) > len(quote):
            normalized_quote = BITFINEX_QUOTE_ALIASES.get(quote, quote)
            if normalized_quote in quotes:
                return upper[: -len(quote)], normalized_quote
    return None


def quote_volume_from_base_volume(volume: Any, price: Any) -> Decimal | None:
    vol = dec(volume)
    px = dec(price)
    if vol is None or px is None:
        return None
    return vol * px


def make_market(
    exchange: str,
    symbol: str,
    base: str,
    quote: str,
    bid: Any,
    ask: Any,
    quote_volume: Any,
    taker_bps: Decimal | None = None,
    exchange_ts_ms: int | None = None,
) -> Market | None:
    bid_dec = dec(bid)
    ask_dec = dec(ask)
    if bid_dec is None or ask_dec is None or bid_dec >= ask_dec:
        return None
    volume_dec = dec(quote_volume)
    return Market(
        exchange=exchange,
        symbol=symbol,
        base=base.upper(),
        quote=quote.upper(),
        bid=bid_dec,
        ask=ask_dec,
        quote_volume=volume_dec,
        taker_bps=taker_bps or DEFAULT_TAKER_BPS.get(exchange, Decimal("20")),
        exchange_ts_ms=exchange_ts_ms,
    )


def normalized_levels(rows: Iterable[Any], *, signed_bitfinex: bool = False) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
    bids: list[tuple[Decimal, Decimal]] = []
    asks: list[tuple[Decimal, Decimal]] = []
    for row in rows:
        if signed_bitfinex:
            if not isinstance(row, list) or len(row) < 3:
                continue
            price = dec(row[0])
            amount = Decimal(str(row[2]))
            if price is None or amount == 0:
                continue
            if amount > 0:
                bids.append((price, amount))
            else:
                asks.append((price, -amount))
        else:
            if not isinstance(row, (list, tuple)) or len(row) < 2:
                continue
            price = dec(row[0])
            qty = dec(row[1])
            if price is None or qty is None:
                continue
            bids.append((price, qty))
    bids.sort(key=lambda item: item[0], reverse=True)
    asks.sort(key=lambda item: item[0])
    return bids, asks


def pairs(rows: Iterable[Any]) -> list[tuple[Decimal, Decimal]]:
    out: list[tuple[Decimal, Decimal]] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 2:
            continue
        price = dec(row[0])
        qty = dec(row[1])
        if price is not None and qty is not None:
            out.append((price, qty))
    return out


def dict_pairs(rows: Iterable[Any], price_key: str = "price", qty_key: str = "quantity") -> list[tuple[Decimal, Decimal]]:
    out: list[tuple[Decimal, Decimal]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        price = dec(row.get(price_key))
        qty = dec(row.get(qty_key))
        if price is not None and qty is not None:
            out.append((price, qty))
    return out


def bitkub_pairs(rows: Iterable[Any]) -> list[tuple[Decimal, Decimal]]:
    out: list[tuple[Decimal, Decimal]] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 5:
            continue
        price = dec(row[3])
        qty = dec(row[4])
        if price is not None and qty is not None:
            out.append((price, qty))
    return out


def sorted_book(
    bids: list[tuple[Decimal, Decimal]],
    asks: list[tuple[Decimal, Decimal]],
) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
    return sorted(bids, key=lambda item: item[0], reverse=True), sorted(asks, key=lambda item: item[0])


def flat_pairs(values: Iterable[Any]) -> list[tuple[Decimal, Decimal]]:
    rows = list(values)
    out: list[tuple[Decimal, Decimal]] = []
    for index in range(0, len(rows) - 1, 2):
        price = dec(rows[index])
        qty = dec(rows[index + 1])
        if price is not None and qty is not None:
            out.append((price, qty))
    return out


def buy_with_quote(asks: list[tuple[Decimal, Decimal]], quote_budget: Decimal) -> Fill:
    remaining = quote_budget
    base = Decimal("0")
    spent = Decimal("0")
    levels = 0
    for price, qty in asks:
        levels += 1
        cost = price * qty
        if cost <= remaining:
            base += qty
            spent += cost
            remaining -= cost
        else:
            take = remaining / price
            base += take
            spent += remaining
            remaining = Decimal("0")
            break
    return Fill(
        requested_quote=quote_budget,
        base=base,
        quote=spent,
        avg_price=(spent / base if base > 0 else None),
        full=remaining == 0,
        levels=levels,
    )


def sell_base(bids: list[tuple[Decimal, Decimal]], base_amount: Decimal) -> SellFill:
    remaining = base_amount
    sold = Decimal("0")
    got = Decimal("0")
    levels = 0
    for price, qty in bids:
        levels += 1
        take = min(qty, remaining)
        sold += take
        got += take * price
        remaining -= take
        if remaining <= 0:
            break
    return SellFill(
        requested_base=base_amount,
        base=sold,
        quote=got,
        avg_price=(got / sold if sold > 0 else None),
        full=remaining == 0,
        levels=levels,
    )


def json_decimal_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return format(value, "f")
    raise TypeError(f"not json serializable: {type(value)!r}")


def quant(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def open_status_db(path: Path) -> sqlite3.Connection | None:
    if not path.exists():
        return None
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.row_factory = sqlite3.Row
    return conn


def lookup_symbol_status(conn: sqlite3.Connection, exchange: str, symbol: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT tradable, status, observed_at_ms
        FROM symbol_status
        WHERE exchange = ? AND (symbol = ? OR UPPER(symbol) = UPPER(?))
        LIMIT 1
        """,
        (exchange, symbol, symbol),
    ).fetchone()
    if row is None:
        return {"known": False, "hint": "?", "tradable": None, "status": "unknown"}
    if row["tradable"] == 1:
        hint = "T"
        tradable = True
    elif row["tradable"] == 0:
        hint = f"BLOCKED:{row['status']}"
        tradable = False
    else:
        hint = f"?:{row['status']}"
        tradable = None
    return {
        "known": True,
        "hint": hint,
        "tradable": tradable,
        "status": row["status"],
        "observed_at_ms": row["observed_at_ms"],
    }


def lookup_asset_flag(conn: sqlite3.Connection, exchange: str, asset: str, field: str) -> dict[str, Any]:
    rows = conn.execute(
        f"""
        SELECT network, {field}, status, observed_at_ms
        FROM asset_status
        WHERE exchange = ? AND asset = ?
        """,
        (exchange, asset),
    ).fetchall()
    if not rows:
        return {"known": False, "hint": "?", "enabled": None, "networks": []}
    values = [row[field] for row in rows if row[field] is not None]
    if not values:
        return {"known": True, "hint": "?", "enabled": None, "networks": [dict(row) for row in rows]}
    enabled = any(value == 1 for value in values)
    return {
        "known": True,
        "hint": "Y" if enabled else "N",
        "enabled": enabled,
        "networks": [dict(row) for row in rows],
    }


def attach_operational_status(opportunity: Opportunity, status_conn: sqlite3.Connection | None) -> Opportunity:
    if status_conn is None:
        return replace(
            opportunity,
            operational_grade="status_unavailable",
            status_hint="trade=?/? quote_dep=? base_wd=?",
            status_json=json.dumps({"reason": "status_db_unavailable"}, sort_keys=True),
        )

    buy_trade = lookup_symbol_status(status_conn, opportunity.buy_exchange, opportunity.buy_symbol)
    sell_trade = lookup_symbol_status(status_conn, opportunity.sell_exchange, opportunity.sell_symbol)
    quote_deposit = lookup_asset_flag(status_conn, opportunity.buy_exchange, opportunity.quote, "deposit_enabled")
    base_withdraw = lookup_asset_flag(status_conn, opportunity.sell_exchange, opportunity.base, "withdraw_enabled")

    if buy_trade["tradable"] is False or sell_trade["tradable"] is False:
        grade = "trading_blocked"
    elif quote_deposit["enabled"] is False or base_withdraw["enabled"] is False:
        grade = "rebalance_blocked"
    elif (
        buy_trade["tradable"] is True
        and sell_trade["tradable"] is True
        and quote_deposit["enabled"] is True
        and base_withdraw["enabled"] is True
    ):
        grade = "tradable_rebalance_public_ok"
    elif buy_trade["tradable"] is True and sell_trade["tradable"] is True:
        grade = "tradable_rebalance_unknown"
    else:
        grade = "status_unknown"

    status_hint = (
        f"trade={buy_trade['hint']}/{sell_trade['hint']} "
        f"quote_dep={quote_deposit['hint']} "
        f"base_wd={base_withdraw['hint']}"
    )
    return replace(
        opportunity,
        operational_grade=grade,
        status_hint=status_hint,
        status_json=json.dumps(
            {
                "buy_symbol": buy_trade,
                "sell_symbol": sell_trade,
                "quote_deposit": quote_deposit,
                "base_withdraw": base_withdraw,
            },
            sort_keys=True,
        ),
    )


class ExchangeAdapter:
    name: str

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        raise NotImplementedError

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        raise NotImplementedError


class BinanceAdapter(ExchangeAdapter):
    def __init__(self, name: str, base_url: str, taker_bps: Decimal) -> None:
        self.name = name
        self.base_url = base_url
        self.taker_bps = taker_bps

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json(f"{self.base_url}/api/v3/ticker/24hr")
        markets: list[Market] = []
        for row in rows:
            split = split_symbol(str(row.get("symbol", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["symbol"],
                base,
                quote,
                row.get("bidPrice"),
                row.get("askPrice"),
                row.get("quoteVolume"),
                self.taker_bps,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"{self.base_url}/api/v3/depth?{urllib.parse.urlencode({'symbol': symbol, 'limit': 1000})}")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class BybitAdapter(ExchangeAdapter):
    name = "bybit"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://api.bybit.com/v5/market/tickers?category=spot")
        markets: list[Market] = []
        for row in data.get("result", {}).get("list", []):
            split = split_symbol(str(row.get("symbol", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["symbol"],
                base,
                quote,
                row.get("bid1Price"),
                row.get("ask1Price"),
                row.get("turnover24h"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bybit.com/v5/market/orderbook?category=spot&{urllib.parse.urlencode({'symbol': symbol, 'limit': 200})}")
        result = data.get("result", {})
        return pairs(result.get("b", [])), pairs(result.get("a", []))


class OkxAdapter(ExchangeAdapter):
    name = "okx"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://www.okx.com/api/v5/market/tickers?instType=SPOT")
        markets: list[Market] = []
        for row in data.get("data", []):
            split = split_symbol(str(row.get("instId", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["instId"],
                base,
                quote,
                row.get("bidPx"),
                row.get("askPx"),
                row.get("volCcy24h") or row.get("vol24h"),
                exchange_ts_ms=int(row["ts"]) if str(row.get("ts", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://www.okx.com/api/v5/market/books?{urllib.parse.urlencode({'instId': symbol, 'sz': 400})}")
        row = data.get("data", [{}])[0]
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class GateAdapter(ExchangeAdapter):
    name = "gate"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.gateio.ws/api/v4/spot/tickers")
        markets: list[Market] = []
        for row in rows:
            split = split_symbol(str(row.get("currency_pair", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["currency_pair"],
                base,
                quote,
                row.get("highest_bid"),
                row.get("lowest_ask"),
                row.get("quote_volume"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.gateio.ws/api/v4/spot/order_book?{urllib.parse.urlencode({'currency_pair': symbol, 'limit': 100})}")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class KuCoinAdapter(ExchangeAdapter):
    name = "kucoin"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://api.kucoin.com/api/v1/market/allTickers")
        markets: list[Market] = []
        for row in data.get("data", {}).get("ticker", []):
            split = split_symbol(str(row.get("symbol", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["symbol"],
                base,
                quote,
                row.get("buy"),
                row.get("sell"),
                row.get("volValue"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.kucoin.com/api/v1/market/orderbook/level2_100?{urllib.parse.urlencode({'symbol': symbol})}")
        row = data.get("data", {})
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class MexcAdapter(ExchangeAdapter):
    name = "mexc"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.mexc.com/api/v3/ticker/24hr")
        markets: list[Market] = []
        for row in rows:
            split = split_symbol(str(row.get("symbol", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["symbol"],
                base,
                quote,
                row.get("bidPrice"),
                row.get("askPrice"),
                row.get("quoteVolume"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.mexc.com/api/v3/depth?{urllib.parse.urlencode({'symbol': symbol, 'limit': 500})}")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class BitgetAdapter(ExchangeAdapter):
    name = "bitget"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://api.bitget.com/api/v2/spot/market/tickers")
        markets: list[Market] = []
        for row in data.get("data", []):
            split = split_symbol(str(row.get("symbol", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["symbol"],
                base,
                quote,
                row.get("bidPr"),
                row.get("askPr"),
                row.get("quoteVolume"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bitget.com/api/v2/spot/market/orderbook?{urllib.parse.urlencode({'symbol': symbol, 'type': 'step0', 'limit': 100})}")
        row = data.get("data", {})
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class CoinTrAdapter(ExchangeAdapter):
    name = "cointr"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://api.cointr.pro/api/v2/spot/public/symbols").get("data", [])
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in symbol_rows
            if str(row.get("status", "")).lower() == "online"
            and str(row.get("quoteCoin", "")).upper() in quotes
        }
        ticker_rows = fetch_json("https://api.cointr.pro/api/v2/spot/market/tickers").get("data", [])
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            fee = dec(meta.get("takerFeeRate"))
            market = make_market(
                self.name,
                symbol,
                str(meta.get("baseCoin", "")).upper(),
                str(meta.get("quoteCoin", "")).upper(),
                row.get("bidPr"),
                row.get("askPr"),
                row.get("quoteVolume"),
                taker_bps=fee * Decimal("10000") if fee is not None else None,
                exchange_ts_ms=int(row["ts"]) if str(row.get("ts", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "type": "step0", "limit": 100})
        data = fetch_json(f"https://api.cointr.pro/api/v2/spot/market/orderbook?{query}").get("data", {})
        return sorted_book(pairs(data.get("bids", [])), pairs(data.get("asks", [])))


class CoinWAdapter(ExchangeAdapter):
    name = "coinw"
    base_url = "https://api.coinw.com/api/v1/public"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_query = urllib.parse.urlencode({"command": "returnSymbol"})
        symbol_rows = fetch_json(f"{self.base_url}?{symbol_query}").get("data", [])
        metadata = {
            str(row.get("currencyPair", "")).upper(): row
            for row in symbol_rows
            if int(row.get("state") or 0) == 1
            and str(row.get("currencyQuote", "")).upper() in quotes
        }
        ticker_query = urllib.parse.urlencode({"command": "returnTicker"})
        ticker_rows = fetch_json(f"{self.base_url}?{ticker_query}").get("data", {})
        markets: list[Market] = []
        for symbol, row in ticker_rows.items():
            symbol = str(symbol).upper()
            meta = metadata.get(symbol)
            if not meta or int(row.get("isFrozen") or 0) != 0:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("currencyBase", "")).upper(),
                str(meta.get("currencyQuote", "")).upper(),
                row.get("highestBid"),
                row.get("lowestAsk"),
                quote_volume_from_base_volume(row.get("baseVolume"), row.get("last")),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"command": "returnOrderBook", "symbol": symbol.upper(), "size": 100})
        data = fetch_json(f"{self.base_url}?{query}")
        if str(data.get("code")) != "200":
            return [], []
        book = data.get("data", {})
        return sorted_book(pairs(book.get("bids", [])), pairs(book.get("asks", [])))


class DeribitAdapter(ExchangeAdapter):
    name = "deribit"
    base_url = "https://www.deribit.com/api/v2/public"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        selected = [
            row for row in self.fetch_instruments()
            if str(row.get("quote_currency", "")).upper() in quotes
            and str(row.get("state", "")).lower() == "open"
            and bool(row.get("is_active"))
        ]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("instrument_name", "")).upper()
            ticker = fetch_json(
                f"{self.base_url}/ticker?{urllib.parse.urlencode({'instrument_name': symbol})}",
                timeout=8.0,
            ).get("result", {})
            if str(ticker.get("state", "")).lower() != "open":
                return None
            taker = dec(row.get("taker_commission"))
            stats = ticker.get("stats", {})
            return make_market(
                self.name,
                symbol,
                str(row.get("base_currency", "")).upper(),
                str(row.get("quote_currency", "")).upper(),
                ticker.get("best_bid_price"),
                ticker.get("best_ask_price"),
                stats.get("volume_notional") or quote_volume_from_base_volume(stats.get("volume"), ticker.get("last_price")),
                taker_bps=taker * Decimal("10000") if taker is not None else None,
                exchange_ts_ms=int(ticker["timestamp"]) if str(ticker.get("timestamp", "")).isdigit() else None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_DERIBIT_WORKERS", 8, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"instrument_name": symbol.upper(), "depth": 100})
        data = fetch_json(f"{self.base_url}/get_order_book?{query}", timeout=8.0).get("result", {})
        if str(data.get("state", "")).lower() != "open":
            return [], []
        return sorted_book(pairs(data.get("bids", [])), pairs(data.get("asks", [])))

    def fetch_instruments(self) -> list[dict[str, Any]]:
        currencies = fetch_json(f"{self.base_url}/get_currencies").get("result", [])
        codes = sorted({str(row.get("currency", "")).upper() for row in currencies if row.get("currency")})

        def fetch_currency(currency: str) -> list[dict[str, Any]]:
            query = urllib.parse.urlencode({"currency": currency, "kind": "spot"})
            return fetch_json(f"{self.base_url}/get_instruments?{query}", timeout=8.0).get("result", [])

        deduped: dict[str, dict[str, Any]] = {}
        for rows in fetch_many(codes, "PROFIT_MONITOR_DERIBIT_INSTRUMENT_WORKERS", 6, fetch_currency):
            for row in rows or []:
                symbol = str(row.get("instrument_name", "")).upper()
                if symbol:
                    deduped[symbol] = row
        return list(deduped.values())


class HitBtcAdapter(ExchangeAdapter):
    name = "hitbtc"
    base_url = "https://api.hitbtc.com/api/3/public"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json(f"{self.base_url}/symbol")
        metadata = {
            str(symbol).upper(): row
            for symbol, row in symbol_rows.items()
            if str(row.get("type", "")).lower() == "spot"
            and str(row.get("status", "")).lower() == "working"
            and str(row.get("quote_currency", "")).upper() in quotes
        }
        ticker_rows = fetch_json(f"{self.base_url}/ticker")
        markets: list[Market] = []
        for symbol, row in ticker_rows.items():
            symbol = str(symbol).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            taker = dec(meta.get("take_rate"))
            market = make_market(
                self.name,
                symbol,
                str(meta.get("base_currency", "")).upper(),
                str(meta.get("quote_currency", "")).upper(),
                row.get("bid"),
                row.get("ask"),
                row.get("volume_quote") or quote_volume_from_base_volume(row.get("volume"), row.get("last")),
                taker_bps=taker * Decimal("10000") if taker is not None else None,
                exchange_ts_ms=self._parse_ts(row.get("timestamp")),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(
            f"{self.base_url}/orderbook/{urllib.parse.quote(symbol.upper())}?{urllib.parse.urlencode({'depth': 100})}",
            timeout=8.0,
        )
        return sorted_book(pairs(data.get("bid", [])), pairs(data.get("ask", [])))

    @staticmethod
    def _parse_ts(value: Any) -> int | None:
        if not value:
            return None
        try:
            return int(datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            return None


class BitMexAdapter(ExchangeAdapter):
    name = "bitmex"
    base_url = "https://www.bitmex.com/api/v1"

    def __init__(self) -> None:
        self.instrument_by_symbol: dict[str, dict[str, Any]] = {}

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        markets: list[Market] = []
        for row in self.load_instruments().values():
            quote = self._asset(row.get("quoteCurrency"))
            if quote not in quotes:
                continue
            quote_volume = dec(row.get("foreignNotional24h"))
            if quote_volume is None:
                continue
            taker = dec(row.get("takerFee"))
            market = make_market(
                self.name,
                str(row.get("symbol", "")).upper(),
                self._asset(row.get("underlying")),
                quote,
                row.get("bidPrice"),
                row.get("askPrice"),
                quote_volume,
                taker_bps=taker * Decimal("10000") if taker is not None else None,
                exchange_ts_ms=self._parse_ts(row.get("timestamp")),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        meta = self.load_instruments().get(symbol.upper())
        if not meta:
            return [], []
        multiplier = dec(meta.get("underlyingToPositionMultiplier"))
        if multiplier is None:
            return [], []
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "depth": 100})
        rows = fetch_json(f"{self.base_url}/orderBook/L2?{query}", timeout=8.0)
        current_ms = now_ms()
        max_age_ms = env_int("PROFIT_MONITOR_BITMEX_MAX_LEVEL_AGE_MS", 300000)
        bids: list[tuple[Decimal, Decimal]] = []
        asks: list[tuple[Decimal, Decimal]] = []
        for row in rows:
            level_ms = self._parse_ts(row.get("transactTime"))
            if level_ms is not None and current_ms - level_ms > max_age_ms:
                continue
            price = dec(row.get("price"))
            size = dec(row.get("size"))
            if price is None or size is None:
                continue
            qty = size / multiplier
            if row.get("side") == "Buy":
                bids.append((price, qty))
            elif row.get("side") == "Sell":
                asks.append((price, qty))
        return sorted_book(bids, asks)

    def load_instruments(self) -> dict[str, dict[str, Any]]:
        if self.instrument_by_symbol:
            return self.instrument_by_symbol
        rows = fetch_json(f"{self.base_url}/instrument/active")
        self.instrument_by_symbol = {
            str(row.get("symbol", "")).upper(): row
            for row in rows
            if str(row.get("typ", "")) == "IFXXXP"
            and "_" in str(row.get("symbol", ""))
            and str(row.get("state", "")) == "Open"
            and bool(row.get("hasLiquidity"))
            and row.get("underlyingToPositionMultiplier") is not None
        }
        return self.instrument_by_symbol

    @staticmethod
    def _asset(value: Any) -> str:
        asset = str(value or "").upper()
        return "BTC" if asset in {"XBT", "XBTM"} else asset

    @staticmethod
    def _parse_ts(value: Any) -> int | None:
        if not value:
            return None
        try:
            return int(datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            return None


class CoinsPhAdapter(ExchangeAdapter):
    name = "coinsph"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        info = fetch_json("https://api.pro.coins.ph/openapi/v1/exchangeInfo")
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in info.get("symbols", [])
            if str(row.get("status", "")).lower() == "trading"
            and str(row.get("quoteAsset", "")).upper() in quotes
        }
        ticker_rows = fetch_json("https://api.pro.coins.ph/openapi/quote/v1/ticker/24hr")
        tickers: dict[str, dict[str, Any]] = {}
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).upper()
            if symbol not in metadata:
                continue
            current_ts = int(row["closeTime"]) if str(row.get("closeTime", "")).isdigit() else 0
            previous_ts = int(tickers[symbol]["closeTime"]) if symbol in tickers and str(tickers[symbol].get("closeTime", "")).isdigit() else -1
            if current_ts >= previous_ts:
                tickers[symbol] = row
        markets: list[Market] = []
        for symbol, row in tickers.items():
            meta = metadata[symbol]
            market = make_market(
                self.name,
                symbol,
                str(meta.get("baseAsset", "")).upper(),
                str(meta.get("quoteAsset", "")).upper(),
                row.get("bidPrice"),
                row.get("askPrice"),
                row.get("quoteVolume"),
                exchange_ts_ms=int(row["closeTime"]) if str(row.get("closeTime", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "limit": 100})
        data = fetch_json(f"https://api.pro.coins.ph/openapi/quote/v1/depth?{query}")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class CryptoComAdapter(ExchangeAdapter):
    name = "cryptocom"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://api.crypto.com/exchange/v1/public/get-tickers")
        markets: list[Market] = []
        for row in data.get("result", {}).get("data", []):
            split = split_symbol(str(row.get("i", "")), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row["i"],
                base,
                quote,
                row.get("b"),
                row.get("k"),
                row.get("vv"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.crypto.com/exchange/v1/public/get-book?{urllib.parse.urlencode({'instrument_name': symbol, 'depth': 50})}")
        row = data.get("result", {}).get("data", [{}])[0]
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class BitfinexAdapter(ExchangeAdapter):
    name = "bitfinex"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api-pub.bitfinex.com/v2/tickers?symbols=ALL")
        markets: list[Market] = []
        for row in rows:
            if not isinstance(row, list) or len(row) < 11:
                continue
            symbol = str(row[0])
            if not symbol.startswith("t"):
                continue
            split = split_bitfinex_symbol(symbol[1:], quotes)
            if not split:
                continue
            base, quote = split
            quote_volume = None
            volume = dec(row[8])
            last = dec(row[7])
            if volume is not None and last is not None:
                quote_volume = volume * last
            market = make_market(self.name, symbol, base, quote, row[1], row[3], quote_volume)
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        rows = fetch_json(f"https://api-pub.bitfinex.com/v2/book/{symbol}/P0?len=100")
        return normalized_levels(rows, signed_bitfinex=True)


class CoinbaseAdapter(ExchangeAdapter):
    name = "coinbase"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        products = fetch_json("https://api.exchange.coinbase.com/products")
        eligible = [
            row
            for row in products
            if row.get("status") == "online"
            and not row.get("trading_disabled")
            and str(row.get("quote_currency", "")).upper() in quotes
        ]
        eligible.sort(
            key=lambda row: (
                str(row.get("base_currency", "")).upper() not in PRIORITY_BASES,
                str(row.get("quote_currency", "")) not in {"USD", "USDC", "USDT"},
                str(row.get("id", "")),
            )
        )
        limit = int(os.getenv("PROFIT_MONITOR_COINBASE_MARKET_LIMIT", "160"))
        selected = eligible[:limit]

        def fetch_product(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("id", ""))
            ticker = fetch_json(f"https://api.exchange.coinbase.com/products/{urllib.parse.quote(symbol)}/ticker")
            return make_market(
                self.name,
                symbol,
                str(row.get("base_currency", "")).upper(),
                str(row.get("quote_currency", "")).upper(),
                ticker.get("bid"),
                ticker.get("ask"),
                quote_volume_from_base_volume(ticker.get("volume"), ticker.get("price")),
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_COINBASE_WORKERS", 10, fetch_product) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.exchange.coinbase.com/products/{urllib.parse.quote(symbol)}/book?level=2")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class BitstampAdapter(ExchangeAdapter):
    name = "bitstamp"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://www.bitstamp.net/api/v2/ticker/")
        markets: list[Market] = []
        if not isinstance(rows, list):
            return markets
        for row in rows:
            pair = str(row.get("pair", "")).upper()
            split = split_symbol(pair, quotes)
            if not split:
                continue
            base, quote = split
            symbol = pair.replace("/", "").lower()
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("bid"),
                row.get("ask"),
                quote_volume_from_base_volume(row.get("volume"), row.get("last")),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://www.bitstamp.net/api/v2/order_book/{symbol}/")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class BitsoAdapter(ExchangeAdapter):
    name = "bitso"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        books = fetch_json("https://api.bitso.com/v3/available_books/").get("payload", [])
        selected = []
        for book in books:
            symbol = str(book.get("book", ""))
            split = split_symbol(symbol, quotes)
            if not split:
                continue
            selected.append((book, split))

        def fetch_book(item: tuple[dict[str, Any], tuple[str, str]]) -> Market | None:
            book, (base, quote) = item
            symbol = str(book.get("book", ""))
            ticker = fetch_json(f"https://api.bitso.com/v3/ticker/?{urllib.parse.urlencode({'book': symbol})}").get("payload", {})
            return make_market(
                self.name,
                symbol,
                base,
                quote,
                ticker.get("bid"),
                ticker.get("ask"),
                quote_volume_from_base_volume(ticker.get("volume"), ticker.get("last")),
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BITSO_WORKERS", 10, fetch_book) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bitso.com/v3/order_book/?{urllib.parse.urlencode({'book': symbol, 'aggregate': 'false'})}")
        row = data.get("payload", {})
        bids = [(dec(item.get("price")), dec(item.get("amount"))) for item in row.get("bids", [])]
        asks = [(dec(item.get("price")), dec(item.get("amount"))) for item in row.get("asks", [])]
        return [(p, q) for p, q in bids if p and q], [(p, q) for p, q in asks if p and q]


class CoinExAdapter(ExchangeAdapter):
    name = "coinex"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        metadata = {
            row["market"]: row
            for row in fetch_json("https://api.coinex.com/v2/spot/market").get("data", [])
            if row.get("status") == "online" and str(row.get("quote_ccy", "")).upper() in quotes
        }
        tickers = fetch_json("https://api.coinex.com/v1/market/ticker/all").get("data", {}).get("ticker", {})
        values = {
            row.get("market"): row
            for row in fetch_json("https://api.coinex.com/v2/spot/ticker").get("data", [])
        }
        markets: list[Market] = []
        for symbol, meta in metadata.items():
            ticker = tickers.get(symbol, {})
            value_row = values.get(symbol, {})
            taker = dec(meta.get("taker_fee_rate"))
            taker_bps = taker * Decimal("10000") if taker is not None else DEFAULT_TAKER_BPS[self.name]
            market = make_market(
                self.name,
                symbol,
                str(meta.get("base_ccy", "")).upper(),
                str(meta.get("quote_ccy", "")).upper(),
                ticker.get("buy"),
                ticker.get("sell"),
                value_row.get("value"),
                taker_bps,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.coinex.com/v2/spot/depth?{urllib.parse.urlencode({'market': symbol, 'limit': 100, 'interval': '0'})}")
        row = data.get("data", {})
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class HtxAdapter(ExchangeAdapter):
    name = "htx"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        meta_rows = fetch_json("https://api.huobi.pro/v2/settings/common/symbols").get("data", [])
        metadata = {
            row["sc"]: row
            for row in meta_rows
            if str(row.get("state")) == "online" and str(row.get("qc", "")).upper() in quotes
        }
        tickers = fetch_json("https://api.huobi.pro/market/tickers").get("data", [])
        markets: list[Market] = []
        for row in tickers:
            symbol = str(row.get("symbol", ""))
            meta = metadata.get(symbol)
            if not meta:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("bc", "")).upper(),
                str(meta.get("qc", "")).upper(),
                row.get("bid"),
                row.get("ask"),
                row.get("vol"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.huobi.pro/market/depth?{urllib.parse.urlencode({'symbol': symbol, 'type': 'step0', 'depth': 20})}")
        row = data.get("tick", {})
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class BitMartAdapter(ExchangeAdapter):
    name = "bitmart"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://api-cloud.bitmart.com/spot/v1/ticker")
        rows = data.get("data", {}).get("tickers", [])
        markets: list[Market] = []
        for row in rows:
            symbol = str(row.get("symbol", ""))
            split = split_symbol(symbol, quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("best_bid"),
                row.get("best_ask"),
                row.get("quote_volume_24h"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api-cloud.bitmart.com/spot/quotation/v3/books?{urllib.parse.urlencode({'symbol': symbol, 'limit': 50})}")
        return pairs(data.get("data", {}).get("bids", [])), pairs(data.get("data", {}).get("asks", []))


class KrakenAdapter(ExchangeAdapter):
    name = "kraken"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        pairs_data = fetch_json("https://api.kraken.com/0/public/AssetPairs").get("result", {})
        eligible: dict[str, tuple[str, str, str]] = {}
        for pair_id, row in pairs_data.items():
            wsname = str(row.get("wsname", ""))
            split = split_symbol(wsname, quotes)
            if not split:
                continue
            altname = str(row.get("altname") or pair_id)
            eligible[altname] = (pair_id, *split)
        markets: list[Market] = []
        altnames = list(eligible.keys())
        chunk_size = env_int("PROFIT_MONITOR_KRAKEN_CHUNK_SIZE", 120)

        def fetch_chunk(chunk: list[str]) -> dict[str, Any]:
            return fetch_json(
                "https://api.kraken.com/0/public/Ticker?"
                + urllib.parse.urlencode({"pair": ",".join(chunk)})
            ).get("result", {})

        for data in fetch_many(list(chunks(altnames, chunk_size)), "PROFIT_MONITOR_KRAKEN_WORKERS", 4, fetch_chunk):
            for result_key, row in data.items():
                found = None
                for altname, values in eligible.items():
                    if values[0] == result_key or altname == result_key:
                        found = (altname, values)
                        break
                if not found:
                    continue
                altname, (_pair_id, base, quote) = found
                bid = row.get("b", [None])[0]
                ask = row.get("a", [None])[0]
                last = row.get("c", [None])[0]
                volume = row.get("v", [None, None])[1]
                market = make_market(
                    self.name,
                    altname,
                    base.replace("XBT", "BTC"),
                    quote,
                    bid,
                    ask,
                    quote_volume_from_base_volume(volume, last),
                )
                if market:
                    markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.kraken.com/0/public/Depth?{urllib.parse.urlencode({'pair': symbol, 'count': 100})}")
        result = data.get("result", {})
        row = next(iter(result.values()))
        return pairs(row.get("bids", [])), pairs(row.get("asks", []))


class GeminiAdapter(ExchangeAdapter):
    name = "gemini"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbols = fetch_json("https://api.gemini.com/v1/symbols")
        selected = []
        for symbol in symbols:
            split = split_symbol(str(symbol).upper(), quotes)
            if not split:
                continue
            selected.append((symbol, split))

        def fetch_symbol(item: tuple[str, tuple[str, str]]) -> Market | None:
            symbol, (base, quote) = item
            ticker = fetch_json(f"https://api.gemini.com/v1/pubticker/{symbol}")
            return make_market(
                self.name,
                str(symbol),
                base,
                quote,
                ticker.get("bid"),
                ticker.get("ask"),
                quote_volume_from_base_volume(ticker.get("volume", {}).get(base), ticker.get("last")),
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_GEMINI_WORKERS", 12, fetch_symbol) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.gemini.com/v1/book/{symbol}?limit_bids=100&limit_asks=100")
        bids = [(dec(item.get("price")), dec(item.get("amount"))) for item in data.get("bids", [])]
        asks = [(dec(item.get("price")), dec(item.get("amount"))) for item in data.get("asks", [])]
        return [(p, q) for p, q in bids if p and q], [(p, q) for p, q in asks if p and q]


class PoloniexAdapter(ExchangeAdapter):
    name = "poloniex"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.poloniex.com/markets/ticker24h")
        markets: list[Market] = []
        for row in rows:
            symbol = str(row.get("symbol", "")).upper()
            split = split_symbol(symbol, quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("bid"),
                row.get("ask"),
                row.get("amount"),
                exchange_ts_ms=int(row["ts"]) if row.get("ts") else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.poloniex.com/markets/{urllib.parse.quote(symbol)}/orderBook?limit=100")
        return flat_pairs(data.get("bids", [])), flat_pairs(data.get("asks", []))


class AscendExAdapter(ExchangeAdapter):
    name = "ascendex"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://ascendex.com/api/pro/v1/ticker")
        rows = data.get("data", []) if isinstance(data, dict) else []
        markets: list[Market] = []
        for row in rows:
            if row.get("type") != "spot":
                continue
            symbol = str(row.get("symbol", "")).upper()
            split = split_symbol(symbol, quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                (row.get("bid") or [None])[0],
                (row.get("ask") or [None])[0],
                quote_volume_from_base_volume(row.get("volume"), row.get("close")),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://ascendex.com/api/pro/v1/depth?{urllib.parse.urlencode({'symbol': symbol})}")
        book = data.get("data", {}).get("data", {})
        return pairs(book.get("bids", [])), pairs(book.get("asks", []))


class ExmoAdapter(ExchangeAdapter):
    name = "exmo"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.exmo.com/v1.1/ticker")
        markets: list[Market] = []
        for symbol, row in rows.items():
            split = split_symbol(str(symbol).upper(), quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                str(symbol).upper(),
                base,
                quote,
                row.get("buy_price"),
                row.get("sell_price"),
                row.get("vol_curr"),
                exchange_ts_ms=int(row["updated"]) * 1000 if row.get("updated") else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.exmo.com/v1.1/order_book?{urllib.parse.urlencode({'pair': symbol, 'limit': 100})}")
        book = data.get(symbol, {})
        return pairs(book.get("bid", [])), pairs(book.get("ask", []))


class BtcTurkAdapter(ExchangeAdapter):
    name = "btcturk"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.btcturk.com/api/v2/ticker").get("data", [])
        markets: list[Market] = []
        for row in rows:
            base = str(row.get("numeratorSymbol", "")).upper()
            quote = str(row.get("denominatorSymbol", "")).upper()
            if not base or quote not in quotes:
                continue
            market = make_market(
                self.name,
                str(row.get("pair", "")).upper(),
                base,
                quote,
                row.get("bid"),
                row.get("ask"),
                quote_volume_from_base_volume(row.get("volume"), row.get("last")),
                exchange_ts_ms=int(row["timestamp"]) if row.get("timestamp") else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.btcturk.com/api/v2/orderbook?{urllib.parse.urlencode({'pairSymbol': symbol, 'limit': 100})}")
        book = data.get("data", {})
        return pairs(book.get("bids", [])), pairs(book.get("asks", []))


class CexIoAdapter(ExchangeAdapter):
    name = "cexio"
    supported_quotes = {"USD", "EUR", "GBP", "USDT"}

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        selected_quotes = sorted(self.supported_quotes.intersection(quotes))
        if not selected_quotes:
            return []
        data = fetch_json(f"https://cex.io/api/tickers/{'/'.join(selected_quotes)}")
        rows = data.get("data", [])
        markets: list[Market] = []
        for row in rows:
            pair = str(row.get("pair", ""))
            if ":" not in pair:
                continue
            base, quote = [part.upper() for part in pair.split(":", 1)]
            if quote not in quotes:
                continue
            market = make_market(
                self.name,
                f"{base}/{quote}",
                base,
                quote,
                row.get("bid"),
                row.get("ask"),
                quote_volume_from_base_volume(row.get("volume"), row.get("last")),
                exchange_ts_ms=int(row["timestamp"]) * 1000 if row.get("timestamp") else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://cex.io/api/order_book/{urllib.parse.quote(symbol, safe='/')}?depth=100")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class WhiteBitAdapter(ExchangeAdapter):
    name = "whitebit"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        market_rows = fetch_json("https://whitebit.com/api/v4/public/markets")
        metadata = {
            row["name"]: row
            for row in market_rows
            if row.get("type") == "spot"
            and bool(row.get("tradesEnabled"))
            and str(row.get("money", "")).upper() in quotes
        }
        tickers = fetch_json("https://whitebit.com/api/v2/public/ticker").get("result", [])
        markets: list[Market] = []
        for row in tickers:
            symbol = str(row.get("tradingPairs", "")).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            taker = dec(meta.get("takerFee"))
            taker_bps = taker * Decimal("100") if taker is not None else DEFAULT_TAKER_BPS[self.name]
            market = make_market(
                self.name,
                symbol,
                str(meta.get("stock", "")).upper(),
                str(meta.get("money", "")).upper(),
                row.get("highestBid"),
                row.get("lowestAsk"),
                row.get("quoteVolume24h"),
                taker_bps,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://whitebit.com/api/v4/public/orderbook/{urllib.parse.quote(symbol)}?limit=100")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class UpbitAdapter(ExchangeAdapter):
    name = "upbit"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        market_rows = fetch_json("https://api.upbit.com/v1/market/all?isDetails=true")
        eligible: dict[str, tuple[str, str]] = {}
        for row in market_rows:
            market_id = str(row.get("market", "")).upper()
            if "-" not in market_id:
                continue
            quote, base = market_id.split("-", 1)
            if quote not in quotes:
                continue
            event = row.get("market_event") or {}
            if bool(event.get("warning")):
                continue
            eligible[market_id] = (base, quote)

        tickers: dict[str, dict[str, Any]] = {}
        books: dict[str, dict[str, Any]] = {}
        symbols = list(eligible.keys())
        chunk_size = env_int("PROFIT_MONITOR_UPBIT_CHUNK_SIZE", 120)

        def fetch_chunk(chunk: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            query = urllib.parse.urlencode({"markets": ",".join(chunk)})
            ticker_rows = fetch_json(f"https://api.upbit.com/v1/ticker?{query}")
            book_rows = fetch_json(f"https://api.upbit.com/v1/orderbook?{query}")
            return ticker_rows, book_rows

        for ticker_rows, book_rows in fetch_many(list(chunks(symbols, chunk_size)), "PROFIT_MONITOR_UPBIT_WORKERS", 3, fetch_chunk):
            for row in ticker_rows:
                tickers[str(row.get("market", "")).upper()] = row
            for row in book_rows:
                books[str(row.get("market", "")).upper()] = row

        markets: list[Market] = []
        for symbol, (base, quote) in eligible.items():
            book = books.get(symbol, {})
            units = book.get("orderbook_units") or []
            if not units:
                continue
            top = units[0]
            ticker = tickers.get(symbol, {})
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                top.get("bid_price"),
                top.get("ask_price"),
                ticker.get("acc_trade_price_24h") or ticker.get("acc_trade_price"),
                exchange_ts_ms=int(book["timestamp"]) if str(book.get("timestamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        rows = fetch_json(f"https://api.upbit.com/v1/orderbook?{urllib.parse.urlencode({'markets': symbol})}")
        units = rows[0].get("orderbook_units", []) if rows else []
        bids = [(dec(row.get("bid_price")), dec(row.get("bid_size"))) for row in units]
        asks = [(dec(row.get("ask_price")), dec(row.get("ask_size"))) for row in units]
        return [(p, q) for p, q in bids if p and q], [(p, q) for p, q in asks if p and q]


class IndodaxAdapter(ExchangeAdapter):
    name = "indodax"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        pair_rows = fetch_json("https://indodax.com/api/pairs")
        metadata: dict[str, dict[str, Any]] = {}
        for row in pair_rows:
            quote = str(row.get("base_currency", "")).upper()
            if quote not in quotes:
                continue
            if int(row.get("is_maintenance") or 0) or int(row.get("is_market_suspended") or 0):
                continue
            ticker_id = str(row.get("ticker_id", ""))
            if ticker_id:
                metadata[ticker_id] = row
        tickers = fetch_json("https://indodax.com/api/summaries").get("tickers", {})
        markets: list[Market] = []
        for ticker_id, meta in metadata.items():
            row = tickers.get(ticker_id)
            if not row:
                continue
            base = str(meta.get("traded_currency_unit") or meta.get("traded_currency", "")).upper()
            quote = str(meta.get("base_currency", "")).upper()
            taker = dec(meta.get("trade_fee_percent_taker") or meta.get("trade_fee_percent"))
            taker_bps = taker * Decimal("100") if taker is not None else DEFAULT_TAKER_BPS[self.name]
            market = make_market(
                self.name,
                str(meta.get("id", "")).lower(),
                base,
                quote,
                row.get("buy"),
                row.get("sell"),
                row.get(f"vol_{quote.lower()}"),
                taker_bps,
                exchange_ts_ms=int(row["server_time"]) * 1000 if row.get("server_time") else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://indodax.com/api/depth/{urllib.parse.quote(symbol)}")
        return pairs(data.get("buy", [])), pairs(data.get("sell", []))


class BudaAdapter(ExchangeAdapter):
    name = "buda"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://www.buda.com/api/v2/markets").get("markets", [])
        selected = []
        for row in rows:
            quote = str(row.get("quote_currency", "")).upper()
            if quote not in quotes or bool(row.get("disabled")):
                continue
            selected.append(row)

        def fetch_market(row: dict[str, Any]) -> Market | None:
            quote = str(row.get("quote_currency", "")).upper()
            symbol = str(row.get("name") or row.get("id", "")).lower()
            ticker = fetch_json(f"https://www.buda.com/api/v2/markets/{urllib.parse.quote(symbol)}/ticker").get("ticker", {})
            taker = dec(row.get("taker_fee"))
            taker_bps = taker * Decimal("100") if taker is not None else DEFAULT_TAKER_BPS[self.name]
            return make_market(
                self.name,
                symbol,
                str(row.get("base_currency", "")).upper(),
                quote,
                (ticker.get("max_bid") or [None])[0],
                (ticker.get("min_ask") or [None])[0],
                (ticker.get("quote_volume") or [None])[0],
                taker_bps,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BUDA_WORKERS", 6, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://www.buda.com/api/v2/markets/{urllib.parse.quote(symbol)}/order_book")
        book = data.get("order_book", {})
        return pairs(book.get("bids", [])), pairs(book.get("asks", []))


class NovaDaxAdapter(ExchangeAdapter):
    name = "novadax"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://api.novadax.com/v1/common/symbols").get("data", [])
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in symbol_rows
            if str(row.get("quoteCurrency", "")).upper() in quotes
            and str(row.get("status", "")).upper() == "ONLINE"
        }
        ticker_rows = fetch_json("https://api.novadax.com/v1/market/tickers").get("data", [])
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("baseCurrency", "")).upper(),
                str(meta.get("quoteCurrency", "")).upper(),
                row.get("bid"),
                row.get("ask"),
                row.get("quoteVolume24h"),
                exchange_ts_ms=int(row["timestamp"]) if str(row.get("timestamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol, "limit": 100})
        data = fetch_json(f"https://api.novadax.com/v1/market/depth?{query}").get("data", {})
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class FoxbitAdapter(ExchangeAdapter):
    name = "foxbit"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.foxbit.com.br/rest/v3/markets").get("data", [])
        selected = [
            row
            for row in rows
            if str((row.get("quote") or {}).get("symbol", "")).upper() in quotes
            and "MARKET" in (row.get("order_type") or [])
        ]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("symbol", "")).lower()
            ticker_rows = fetch_json(f"https://api.foxbit.com.br/rest/v3/markets/{urllib.parse.quote(symbol)}/ticker/24hr").get("data", [])
            ticker = ticker_rows[0] if ticker_rows else {}
            best = ticker.get("best") or {}
            rolling_24h = ticker.get("rolling_24h") or {}
            taker = dec((row.get("default_fees") or {}).get("taker"))
            taker_bps = taker * Decimal("10000") if taker is not None else DEFAULT_TAKER_BPS[self.name]
            return make_market(
                self.name,
                symbol,
                str((row.get("base") or {}).get("symbol", "")).upper(),
                str((row.get("quote") or {}).get("symbol", "")).upper(),
                (best.get("bid") or {}).get("price"),
                (best.get("ask") or {}).get("price"),
                rolling_24h.get("quote_volume"),
                taker_bps,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_FOXBIT_WORKERS", 8, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.foxbit.com.br/rest/v3/markets/{urllib.parse.quote(symbol.lower())}/orderbook?depth=100")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class MercadoBitcoinAdapter(ExchangeAdapter):
    name = "mercadobitcoin"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_data = fetch_json("https://api.mercadobitcoin.net/api/v4/symbols")
        symbols = symbol_data.get("symbol", [])
        eligible: dict[str, dict[str, Any]] = {}
        for index, symbol_value in enumerate(symbols):
            symbol = str(symbol_value).upper()
            base = self._column(symbol_data, "base-currency", index).upper()
            quote = self._column(symbol_data, "currency", index).upper()
            asset_type = self._column(symbol_data, "type", index).upper()
            listed = self._column_bool(symbol_data, "exchange-listed", index)
            traded = self._column_bool(symbol_data, "exchange-traded", index)
            if not symbol or not base or quote != "BRL" or quote not in quotes:
                continue
            if base == quote or not listed or not traded or asset_type != "CRYPTO":
                continue
            eligible[symbol] = {"base": base, "quote": quote}

        tickers: dict[str, dict[str, Any]] = {}
        chunk_size = env_int("PROFIT_MONITOR_MERCADOBITCOIN_CHUNK_SIZE", 80)

        def fetch_chunk(chunk: list[str]) -> list[dict[str, Any]]:
            symbols_param = urllib.parse.quote(",".join(chunk), safe=",-")
            return fetch_json(f"https://api.mercadobitcoin.net/api/v4/tickers?symbols={symbols_param}")

        for rows in fetch_many(list(chunks(list(eligible.keys()), chunk_size)), "PROFIT_MONITOR_MERCADOBITCOIN_WORKERS", 4, fetch_chunk):
            for row in rows:
                tickers[str(row.get("pair", "")).upper()] = row

        markets: list[Market] = []
        for symbol, meta in eligible.items():
            row = tickers.get(symbol)
            if not row:
                continue
            market = make_market(
                self.name,
                symbol,
                meta["base"],
                meta["quote"],
                row.get("buy"),
                row.get("sell"),
                quote_volume_from_base_volume(row.get("vol"), row.get("last")),
                exchange_ts_ms=int(row["date"]) * 1000 if str(row.get("date", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        base = symbol.split("-", 1)[0].upper()
        data = fetch_json(f"https://www.mercadobitcoin.net/api/{urllib.parse.quote(base)}/orderbook/")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))

    @staticmethod
    def _column(data: dict[str, Any], key: str, index: int) -> str:
        values = data.get(key, [])
        if isinstance(values, list) and index < len(values):
            return str(values[index] or "")
        return ""

    @staticmethod
    def _column_bool(data: dict[str, Any], key: str, index: int) -> bool:
        values = data.get(key, [])
        if isinstance(values, list) and index < len(values):
            return bool(values[index])
        return False


class BitvavoAdapter(ExchangeAdapter):
    name = "bitvavo"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        market_rows = fetch_json("https://api.bitvavo.com/v2/markets")
        metadata = {
            str(row.get("market", "")).upper(): row
            for row in market_rows
            if str(row.get("quote", "")).upper() in quotes
            and str(row.get("status", "")).lower() == "trading"
        }
        ticker_rows = fetch_json("https://api.bitvavo.com/v2/ticker/24h")
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("market", "")).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("base", "")).upper(),
                str(meta.get("quote", "")).upper(),
                row.get("bid"),
                row.get("ask"),
                row.get("volumeQuote"),
                exchange_ts_ms=int(row["timestamp"]) if str(row.get("timestamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bitvavo.com/v2/{urllib.parse.quote(symbol.upper())}/book?depth=100")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class LunoAdapter(ExchangeAdapter):
    name = "luno"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        market_rows = fetch_json("https://api.luno.com/api/exchange/1/markets").get("markets", [])
        metadata = {
            str(row.get("market_id", "")).upper(): row
            for row in market_rows
            if self._asset(row.get("counter_currency")) in quotes
            and str(row.get("trading_status", "")).upper() == "ACTIVE"
        }
        ticker_rows = fetch_json("https://api.luno.com/api/1/tickers").get("tickers", [])
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("pair", "")).upper()
            meta = metadata.get(symbol)
            if not meta or str(row.get("status", "")).upper() != "ACTIVE":
                continue
            market = make_market(
                self.name,
                symbol,
                self._asset(meta.get("base_currency")),
                self._asset(meta.get("counter_currency")),
                row.get("bid"),
                row.get("ask"),
                quote_volume_from_base_volume(row.get("rolling_24_hour_volume"), row.get("last_trade")),
                exchange_ts_ms=int(row["timestamp"]) if str(row.get("timestamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.luno.com/api/1/orderbook?{urllib.parse.urlencode({'pair': symbol})}")
        return dict_pairs(data.get("bids", []), "price", "volume"), dict_pairs(data.get("asks", []), "price", "volume")

    @staticmethod
    def _asset(value: Any) -> str:
        asset = str(value or "").upper()
        return "BTC" if asset == "XBT" else asset


class ValrAdapter(ExchangeAdapter):
    name = "valr"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        pair_rows = fetch_json("https://api.valr.com/v1/public/pairs")
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in pair_rows
            if bool(row.get("active"))
            and str(row.get("currencyPairType", "")).upper() == "SPOT"
            and str(row.get("quoteCurrency", "")).upper() in quotes
        }
        ticker_rows = fetch_json("https://api.valr.com/v1/public/marketsummary")
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("currencyPair", "")).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("baseCurrency", "")).upper(),
                str(meta.get("quoteCurrency", "")).upper(),
                row.get("bidPrice"),
                row.get("askPrice"),
                row.get("quoteVolume"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.valr.com/v1/public/{urllib.parse.quote(symbol.upper())}/orderbook")
        return (
            dict_pairs(data.get("Bids", []), "price", "quantity"),
            dict_pairs(data.get("Asks", []), "price", "quantity"),
        )


class BitkubAdapter(ExchangeAdapter):
    name = "bitkub"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://api.bitkub.com/api/market/symbols").get("result", [])
        symbols = {str(row.get("symbol", "")).upper() for row in symbol_rows}
        ticker_rows = fetch_json("https://api.bitkub.com/api/market/ticker")
        markets: list[Market] = []
        for symbol, row in ticker_rows.items():
            symbol = str(symbol).upper()
            if symbol not in symbols or "_" not in symbol:
                continue
            quote, base = symbol.split("_", 1)
            if quote not in quotes or int(row.get("isFrozen") or 0):
                continue
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("highestBid"),
                row.get("lowestAsk"),
                row.get("quoteVolume"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"sym": symbol.upper(), "lmt": 100})
        data = fetch_json(f"https://api.bitkub.com/api/market/books?{query}").get("result", {})
        return bitkub_pairs(data.get("bids", [])), bitkub_pairs(data.get("asks", []))


class BitflyerAdapter(ExchangeAdapter):
    name = "bitflyer"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.bitflyer.com/v1/markets")
        selected = []
        for row in rows:
            symbol = str(row.get("product_code", "")).upper()
            if str(row.get("market_type", "")).lower() != "spot" or "_" not in symbol:
                continue
            base, quote = symbol.split("_", 1)
            if quote in quotes:
                selected.append((symbol, base, quote))

        def fetch_market(item: tuple[str, str, str]) -> Market | None:
            symbol, base, quote = item
            ticker = fetch_json(f"https://api.bitflyer.com/v1/getticker?{urllib.parse.urlencode({'product_code': symbol})}")
            if str(ticker.get("state", "")).upper() != "RUNNING":
                return None
            return make_market(
                self.name,
                symbol,
                base,
                quote,
                ticker.get("best_bid"),
                ticker.get("best_ask"),
                quote_volume_from_base_volume(ticker.get("volume_by_product") or ticker.get("volume"), ticker.get("ltp")),
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BITFLYER_WORKERS", 6, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bitflyer.com/v1/getboard?{urllib.parse.urlencode({'product_code': symbol})}")
        return dict_pairs(data.get("bids", []), "price", "size"), dict_pairs(data.get("asks", []), "price", "size")


class BithumbAdapter(ExchangeAdapter):
    name = "bithumb"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        if "KRW" not in quotes:
            return []
        tickers = fetch_json("https://api.bithumb.com/public/ticker/ALL_KRW").get("data", {})
        books = fetch_json("https://api.bithumb.com/public/orderbook/ALL_KRW?count=100").get("data", {})
        markets: list[Market] = []
        for base, book in books.items():
            if base in {"timestamp", "payment_currency"} or not isinstance(book, dict):
                continue
            ticker = tickers.get(base, {}) if isinstance(tickers, dict) else {}
            bids = dict_pairs(book.get("bids", []), "price", "quantity")
            asks = dict_pairs(book.get("asks", []), "price", "quantity")
            if not bids or not asks:
                continue
            market = make_market(
                self.name,
                f"{base}_KRW",
                str(base).upper(),
                "KRW",
                bids[0][0],
                asks[0][0],
                ticker.get("acc_trade_value_24H") or ticker.get("acc_trade_value"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bithumb.com/public/orderbook/{urllib.parse.quote(symbol.upper())}?count=100").get("data", {})
        return dict_pairs(data.get("bids", []), "price", "quantity"), dict_pairs(data.get("asks", []), "price", "quantity")


class BitbankAdapter(ExchangeAdapter):
    name = "bitbank"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://public.bitbank.cc/tickers").get("data", [])
        markets: list[Market] = []
        for row in rows:
            symbol = str(row.get("pair", "")).lower()
            if "_" not in symbol:
                continue
            base, quote = [part.upper() for part in symbol.split("_", 1)]
            if quote not in quotes:
                continue
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("buy"),
                row.get("sell"),
                quote_volume_from_base_volume(row.get("vol"), row.get("last")),
                exchange_ts_ms=int(row["timestamp"]) if str(row.get("timestamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://public.bitbank.cc/{urllib.parse.quote(symbol.lower())}/depth").get("data", {})
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class CoincheckAdapter(ExchangeAdapter):
    name = "coincheck"
    candidate_pairs = [
        "btc_jpy",
        "eth_jpy",
        "etc_jpy",
        "lsk_jpy",
        "xrp_jpy",
        "xem_jpy",
        "bch_jpy",
        "mona_jpy",
        "iost_jpy",
        "fnct_jpy",
        "chz_jpy",
        "dai_jpy",
        "imx_jpy",
        "wbtc_jpy",
        "shib_jpy",
        "avax_jpy",
        "bril_jpy",
        "bc_jpy",
        "doge_jpy",
        "pepe_jpy",
        "mask_jpy",
        "mana_jpy",
        "grt_jpy",
        "ltc_jpy",
        "xlm_jpy",
        "qtum_jpy",
        "bat_jpy",
        "enj_jpy",
        "plt_jpy",
        "sand_jpy",
        "dot_jpy",
        "link_jpy",
        "matic_jpy",
        "ape_jpy",
        "axs_jpy",
    ]

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        selected = [pair for pair in self.candidate_pairs if self._split(pair)[1] in quotes]

        def fetch_market(pair: str) -> Market | None:
            base, quote = self._split(pair)
            row = fetch_json(f"https://coincheck.com/api/ticker?{urllib.parse.urlencode({'pair': pair})}")
            timestamp = row.get("timestamp")
            return make_market(
                self.name,
                pair,
                base,
                quote,
                row.get("bid"),
                row.get("ask"),
                quote_volume_from_base_volume(row.get("volume"), row.get("last")),
                exchange_ts_ms=int(timestamp) * 1000 if str(timestamp).isdigit() else None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_COINCHECK_WORKERS", 8, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://coincheck.com/api/order_books?{urllib.parse.urlencode({'pair': symbol.lower()})}")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))

    @staticmethod
    def _split(pair: str) -> tuple[str, str]:
        base, quote = pair.upper().split("_", 1)
        return base, quote


class BitrueAdapter(ExchangeAdapter):
    name = "bitrue"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        exchange_rows = fetch_json("https://openapi.bitrue.com/api/v1/exchangeInfo").get("symbols", [])
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in exchange_rows
            if str(row.get("quoteAsset", "")).upper() in quotes
            and str(row.get("status", "")).upper() == "TRADING"
        }
        ticker_rows = fetch_json("https://openapi.bitrue.com/api/v1/ticker/24hr")
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).upper()
            meta = metadata.get(symbol)
            if not meta:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("baseAsset", "")).upper(),
                str(meta.get("quoteAsset", "")).upper(),
                row.get("bidPrice"),
                row.get("askPrice"),
                row.get("quoteVolume"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "limit": 100})
        data = fetch_json(f"https://openapi.bitrue.com/api/v1/depth?{query}")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class CoinoneAdapter(ExchangeAdapter):
    name = "coinone"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        markets: list[Market] = []
        for quote in sorted(quotes & {"KRW"}):
            market_rows = fetch_json(f"https://api.coinone.co.kr/public/v2/markets/{quote}").get("markets", [])
            metadata = {
                str(row.get("target_currency", "")).upper(): row
                for row in market_rows
                if int(row.get("maintenance_status") or 0) == 0
                and int(row.get("trade_status") or 0) == 1
            }
            ticker_rows = fetch_json(f"https://api.coinone.co.kr/public/v2/ticker_new/{quote}").get("tickers", [])
            for row in ticker_rows:
                base = str(row.get("target_currency", "")).upper()
                meta = metadata.get(base)
                if not meta:
                    continue
                bids = row.get("best_bids") or []
                asks = row.get("best_asks") or []
                if not bids or not asks:
                    continue
                market = make_market(
                    self.name,
                    f"{base}_{quote}",
                    base,
                    quote,
                    bids[0].get("price"),
                    asks[0].get("price"),
                    row.get("quote_volume"),
                    exchange_ts_ms=int(row["timestamp"]) if str(row.get("timestamp", "")).isdigit() else None,
                )
                if market:
                    markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        base, quote = symbol.upper().split("_", 1)
        data = fetch_json(f"https://api.coinone.co.kr/public/v2/orderbook/{urllib.parse.quote(quote)}/{urllib.parse.quote(base)}")
        return dict_pairs(data.get("bids", []), "price", "qty"), dict_pairs(data.get("asks", []), "price", "qty")


class KorbitAdapter(ExchangeAdapter):
    name = "korbit"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        pair_rows = fetch_json("https://api.korbit.co.kr/v2/currencyPairs").get("data", [])
        eligible = {
            str(row.get("symbol", "")).lower()
            for row in pair_rows
            if str(row.get("status", "")).lower() == "launched"
        }
        ticker_rows = fetch_json("https://api.korbit.co.kr/v2/tickers").get("data", [])
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).lower()
            if symbol not in eligible or "_" not in symbol:
                continue
            base, quote = [part.upper() for part in symbol.split("_", 1)]
            if quote not in quotes:
                continue
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("bestBidPrice"),
                row.get("bestAskPrice"),
                row.get("quoteVolume"),
                exchange_ts_ms=int(row["lastTradedAt"]) if str(row.get("lastTradedAt", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.korbit.co.kr/v2/orderbook?{urllib.parse.urlencode({'symbol': symbol.lower()})}").get("data", {})
        return dict_pairs(data.get("bids", []), "price", "qty"), dict_pairs(data.get("asks", []), "price", "qty")


class GmoCoinAdapter(ExchangeAdapter):
    name = "gmocoin"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        if "JPY" not in quotes:
            return []
        status = fetch_json("https://api.coin.z.com/public/v1/status").get("data", {}).get("status")
        if str(status).upper() != "OPEN":
            return []
        symbol_rows = fetch_json("https://api.coin.z.com/public/v1/symbols").get("data", [])
        metadata = {str(row.get("symbol", "")).upper(): row for row in symbol_rows}
        ticker_rows = fetch_json("https://api.coin.z.com/public/v1/ticker").get("data", [])
        markets: list[Market] = []
        for row in ticker_rows:
            base = str(row.get("symbol", "")).upper()
            meta = metadata.get(base)
            if not meta:
                continue
            taker = dec(meta.get("takerFee"))
            taker_bps = taker * Decimal("10000") if taker is not None else DEFAULT_TAKER_BPS[self.name]
            market = make_market(
                self.name,
                base,
                base,
                "JPY",
                row.get("bid"),
                row.get("ask"),
                quote_volume_from_base_volume(row.get("volume"), row.get("last")),
                taker_bps,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.coin.z.com/public/v1/orderbooks?{urllib.parse.urlencode({'symbol': symbol.upper()})}").get("data", {})
        return dict_pairs(data.get("bids", []), "price", "size"), dict_pairs(data.get("asks", []), "price", "size")


class IndependentReserveAdapter(ExchangeAdapter):
    name = "independentreserve"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        primary_rows = fetch_json("https://api.independentreserve.com/Public/GetValidPrimaryCurrencyCodes")
        secondary_rows = fetch_json("https://api.independentreserve.com/Public/GetValidSecondaryCurrencyCodes")
        timeout = env_float("PROFIT_MONITOR_INDEPENDENTRESERVE_TIMEOUT", 4.0)
        combos: list[tuple[str, str]] = []
        for primary in primary_rows:
            for secondary in secondary_rows:
                quote = str(secondary).upper()
                if quote in quotes:
                    combos.append((str(primary), str(secondary)))

        def fetch_summary(combo: tuple[str, str]) -> Market | None:
            primary, secondary = combo
            query = urllib.parse.urlencode({"primaryCurrencyCode": primary.lower(), "secondaryCurrencyCode": secondary.lower()})
            row = fetch_json(f"https://api.independentreserve.com/Public/GetMarketSummary?{query}", timeout=timeout)
            return make_market(
                self.name,
                f"{self._asset(primary)}-{str(secondary).upper()}",
                self._asset(primary),
                str(secondary).upper(),
                row.get("CurrentHighestBidPrice"),
                row.get("CurrentLowestOfferPrice"),
                quote_volume_from_base_volume(row.get("DayVolumeXbt"), row.get("LastPrice")),
            )

        return [market for market in fetch_many(combos, "PROFIT_MONITOR_INDEPENDENTRESERVE_WORKERS", 16, fetch_summary) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        base, quote = symbol.split("-", 1)
        query = urllib.parse.urlencode({"primaryCurrencyCode": self._code(base), "secondaryCurrencyCode": quote.lower()})
        data = fetch_json(f"https://api.independentreserve.com/Public/GetOrderBook?{query}")
        return dict_pairs(data.get("BuyOrders", []), "Price", "Volume"), dict_pairs(data.get("SellOrders", []), "Price", "Volume")

    @staticmethod
    def _asset(value: Any) -> str:
        asset = str(value or "").upper()
        return "BTC" if asset == "XBT" else asset

    @staticmethod
    def _code(asset: str) -> str:
        return "xbt" if asset.upper() == "BTC" else asset.lower()


class BtcMarketsAdapter(ExchangeAdapter):
    name = "btcmarkets"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.btcmarkets.net/v3/markets")
        selected = [
            row for row in rows
            if str(row.get("quoteAssetName", "")).upper() in quotes
            and str(row.get("status", "")).lower() == "online"
        ]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("marketId", "")).upper()
            ticker = fetch_json(f"https://api.btcmarkets.net/v3/markets/{urllib.parse.quote(symbol)}/ticker")
            return make_market(
                self.name,
                symbol,
                str(row.get("baseAssetName", "")).upper(),
                str(row.get("quoteAssetName", "")).upper(),
                ticker.get("bestBid"),
                ticker.get("bestAsk"),
                ticker.get("volumeQte24h"),
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BTCMARKETS_WORKERS", 8, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.btcmarkets.net/v3/markets/{urllib.parse.quote(symbol.upper())}/orderbook?level=2")
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class NdaxAdapter(ExchangeAdapter):
    name = "ndax"

    def __init__(self) -> None:
        self.instrument_by_symbol: dict[str, dict[str, Any]] = {}

    def load_instruments(self) -> dict[str, dict[str, Any]]:
        if not self.instrument_by_symbol:
            rows = post_json("https://api.ndax.io:8443/AP/GetInstruments", {"OMSId": 1})
            self.instrument_by_symbol = {
                str(row.get("Symbol", "")).upper(): row
                for row in rows
                if str(row.get("InstrumentType", "")).lower() == "standard"
                and str(row.get("SessionStatus", "")).lower() == "running"
                and not bool(row.get("IsDisable"))
            }
        return self.instrument_by_symbol

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        instruments = self.load_instruments()
        summary_rows = post_json("https://api.ndax.io:8443/AP/GetLevel1Summary", {"OMSId": 1})
        markets: list[Market] = []
        for raw_row in summary_rows:
            row = json.loads(raw_row) if isinstance(raw_row, str) else raw_row
            symbol = ""
            for candidate in instruments.values():
                if int(candidate.get("InstrumentId") or -1) == int(row.get("InstrumentId") or -2):
                    symbol = str(candidate.get("Symbol", "")).upper()
                    meta = candidate
                    break
            else:
                continue
            quote = str(meta.get("Product2Symbol", "")).upper()
            if quote not in quotes:
                continue
            market = make_market(
                self.name,
                symbol,
                str(meta.get("Product1Symbol", "")).upper(),
                quote,
                row.get("BestBid"),
                row.get("BestOffer"),
                row.get("Rolling24HrNotional"),
                exchange_ts_ms=int(row["TimeStamp"]) if str(row.get("TimeStamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        meta = self.load_instruments().get(symbol.upper())
        if not meta:
            return [], []
        query = urllib.parse.urlencode({"OMSId": 1, "InstrumentId": int(meta.get("InstrumentId")), "Depth": 100})
        rows = fetch_json(f"https://api.ndax.io:8443/AP/GetL2Snapshot?{query}")
        bids: list[tuple[Decimal, Decimal]] = []
        asks: list[tuple[Decimal, Decimal]] = []
        for row in rows:
            if not isinstance(row, list) or len(row) < 10:
                continue
            price = dec(row[6])
            qty = dec(row[8])
            if price is None or qty is None:
                continue
            if int(row[9]) == 0:
                bids.append((price, qty))
            elif int(row[9]) == 1:
                asks.append((price, qty))
        return sorted_book(bids, asks)


class BitoProAdapter(ExchangeAdapter):
    name = "bitopro"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.bitopro.com/v3/provisioning/trading-pairs").get("data", [])
        selected = [
            row for row in rows
            if str(row.get("quote", "")).upper() in quotes
            and not bool(row.get("maintain"))
            and row.get("pair")
        ]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("pair", "")).lower()
            bids, asks = self.fetch_depth(symbol)
            if not bids or not asks:
                return None
            try:
                ticker = fetch_json(f"https://api.bitopro.com/v3/tickers/{urllib.parse.quote(symbol)}").get("data", {})
            except Exception:
                ticker = {}
            quote_volume = quote_volume_from_base_volume(ticker.get("volume24hr"), ticker.get("lastPrice"))
            return make_market(
                self.name,
                symbol,
                str(row.get("base", "")).upper(),
                str(row.get("quote", "")).upper(),
                bids[0][0],
                asks[0][0],
                quote_volume,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BITOPRO_WORKERS", 8, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.bitopro.com/v3/order-book/{urllib.parse.quote(symbol.lower())}?limit=50")
        return dict_pairs(data.get("bids", []), "price", "amount"), dict_pairs(data.get("asks", []), "price", "amount")


class LatokenAdapter(ExchangeAdapter):
    name = "latoken"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        currency_rows = fetch_json("https://api.latoken.com/v2/currency")
        currency_by_id = {
            str(row.get("id", "")): str(row.get("tag", "")).upper()
            for row in currency_rows
            if row.get("id") and row.get("tag")
        }
        pair_rows = fetch_json("https://api.latoken.com/v2/pair")
        active_pairs: set[tuple[str, str]] = set()
        for row in pair_rows:
            if str(row.get("status", "")).upper() != "PAIR_STATUS_ACTIVE":
                continue
            base = currency_by_id.get(str(row.get("baseCurrency", "")))
            quote = currency_by_id.get(str(row.get("quoteCurrency", "")))
            if base and quote in quotes:
                active_pairs.add((base, quote))

        ticker_rows = fetch_json("https://api.latoken.com/v2/ticker")
        max_age_ms = env_int("PROFIT_MONITOR_LATOKEN_MAX_TICKER_AGE_MS", 60000)
        current_ms = now_ms()
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).upper()
            if "/" not in symbol:
                continue
            base, quote = symbol.split("/", 1)
            if (base, quote) not in active_pairs:
                continue
            timestamp = int(row["updateTimestamp"]) if str(row.get("updateTimestamp", "")).isdigit() else None
            if timestamp is not None and current_ms - timestamp > max_age_ms:
                continue
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("bestBid"),
                row.get("bestAsk"),
                row.get("volume24h"),
                exchange_ts_ms=timestamp,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        if "/" not in symbol:
            return [], []
        base, quote = symbol.upper().split("/", 1)
        url = (
            "https://api.latoken.com/v2/book/"
            f"{urllib.parse.quote(base)}/{urllib.parse.quote(quote)}?limit=100"
        )
        try:
            data = fetch_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 404, 429, 500, 503}:
                return [], []
            raise
        return sorted_book(
            dict_pairs(data.get("bid", []), "price", "quantity"),
            dict_pairs(data.get("ask", []), "price", "quantity"),
        )


class PionexAdapter(ExchangeAdapter):
    name = "pionex"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://api.pionex.com/api/v1/common/symbols").get("data", {}).get("symbols", [])
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in symbol_rows
            if str(row.get("type", "")).upper() == "SPOT"
            and bool(row.get("enable"))
            and str(row.get("quoteCurrency", "")).upper() in quotes
        }
        ticker_rows = fetch_json("https://api.pionex.com/api/v1/market/tickers").get("data", {}).get("tickers", [])
        tickers = {str(row.get("symbol", "")).upper(): row for row in ticker_rows}

        def fetch_market(item: tuple[str, dict[str, Any]]) -> Market | None:
            symbol, row = item
            bids, asks = self.fetch_depth(symbol)
            if not bids or not asks:
                return None
            ticker = tickers.get(symbol, {})
            timestamp = int(ticker["time"]) if str(ticker.get("time", "")).isdigit() else None
            return make_market(
                self.name,
                symbol,
                str(row.get("baseCurrency", "")).upper(),
                str(row.get("quoteCurrency", "")).upper(),
                bids[0][0],
                asks[0][0],
                ticker.get("amount"),
                exchange_ts_ms=timestamp,
            )

        return [market for market in fetch_many(list(metadata.items()), "PROFIT_MONITOR_PIONEX_WORKERS", 12, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "limit": 100})
        data = fetch_json(f"https://api.pionex.com/api/v1/market/depth?{query}").get("data", {})
        timestamp = data.get("updateTime")
        if str(timestamp or "").isdigit():
            max_age_ms = env_int("PROFIT_MONITOR_PIONEX_MAX_BOOK_AGE_MS", 60000)
            if now_ms() - int(timestamp) > max_age_ms:
                return [], []
        return sorted_book(pairs(data.get("bids", [])), pairs(data.get("asks", [])))


class HyperliquidAdapter(ExchangeAdapter):
    name = "hyperliquid"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        meta, contexts = post_json("https://api.hyperliquid.xyz/info", {"type": "spotMetaAndAssetCtxs"})
        tokens = {
            int(row.get("index")): str(row.get("name", "")).upper()
            for row in meta.get("tokens", [])
            if row.get("index") is not None and row.get("name")
        }
        context_by_coin = {str(row.get("coin", "")): row for row in contexts if row.get("coin")}
        selected: list[tuple[dict[str, Any], str, str, dict[str, Any]]] = []
        for row in meta.get("universe", []):
            token_indexes = row.get("tokens", [])
            if not isinstance(token_indexes, list) or len(token_indexes) != 2:
                continue
            base = tokens.get(int(token_indexes[0]))
            quote = tokens.get(int(token_indexes[1]))
            coin = str(row.get("name", ""))
            if not base or not quote or quote not in quotes or not coin:
                continue
            context = context_by_coin.get(coin, {})
            selected.append((row, base, quote, context))

        def fetch_market(item: tuple[dict[str, Any], str, str, dict[str, Any]]) -> Market | None:
            row, base, quote, context = item
            coin = str(row.get("name", ""))
            bids, asks = self.fetch_depth(coin)
            if not bids or not asks:
                return None
            return make_market(
                self.name,
                coin,
                base,
                quote,
                bids[0][0],
                asks[0][0],
                context.get("dayNtlVlm"),
                exchange_ts_ms=None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_HYPERLIQUID_WORKERS", 12, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = post_json("https://api.hyperliquid.xyz/info", {"type": "l2Book", "coin": symbol})
        timestamp = data.get("time")
        if str(timestamp or "").isdigit():
            max_age_ms = env_int("PROFIT_MONITOR_HYPERLIQUID_MAX_BOOK_AGE_MS", 60000)
            if now_ms() - int(timestamp) > max_age_ms:
                return [], []

        def convert(rows: Iterable[Any]) -> list[tuple[Decimal, Decimal]]:
            out: list[tuple[Decimal, Decimal]] = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                price = dec(row.get("px"))
                qty = dec(row.get("sz"))
                if price is not None and qty is not None:
                    out.append((price, qty))
            return out

        levels = data.get("levels", [[], []])
        bids = levels[0] if isinstance(levels, list) and len(levels) > 0 else []
        asks = levels[1] if isinstance(levels, list) and len(levels) > 1 else []
        return sorted_book(convert(bids), convert(asks))


class DigiFinexAdapter(ExchangeAdapter):
    name = "digifinex"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://openapi.digifinex.com/v3/spot/symbols").get("symbol_list", [])
        metadata = {
            str(row.get("symbol", "")).lower(): row
            for row in symbol_rows
            if str(row.get("quote_asset", "")).upper() in quotes
            and str(row.get("status", "")).upper() == "TRADING"
        }
        ticker_rows = fetch_json("https://openapi.digifinex.com/v3/ticker").get("ticker", [])
        tickers = {str(row.get("symbol", "")).lower(): row for row in ticker_rows}
        markets: list[Market] = []
        for symbol, row in metadata.items():
            ticker = tickers.get(symbol)
            if not ticker:
                continue
            market = make_market(
                self.name,
                symbol,
                str(row.get("base_asset", "")).upper(),
                str(row.get("quote_asset", "")).upper(),
                ticker.get("buy"),
                ticker.get("sell"),
                ticker.get("base_vol"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.lower(), "limit": 100})
        data = fetch_json(f"https://openapi.digifinex.com/v3/order_book?{query}")
        return sorted_book(pairs(data.get("bids", [])), pairs(data.get("asks", [])))


class ToobitAdapter(ExchangeAdapter):
    name = "toobit"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://api.toobit.com/api/v1/exchangeInfo", timeout=25.0).get("symbols", [])
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in symbol_rows
            if str(row.get("quoteAsset", "")).upper() in quotes
            and str(row.get("status", "")).upper() == "TRADING"
        }
        book_rows = fetch_json("https://api.toobit.com/quote/v1/ticker/bookTicker")
        ticker_rows = fetch_json("https://api.toobit.com/quote/v1/ticker/24hr")
        tickers = {str(row.get("s", "")).upper(): row for row in ticker_rows if isinstance(row, dict)}
        max_age_ms = env_int("PROFIT_MONITOR_TOOBIT_MAX_BOOK_AGE_MS", 60000)
        current_ms = now_ms()
        markets: list[Market] = []
        for book in book_rows if isinstance(book_rows, list) else []:
            symbol = str(book.get("s", "")).upper()
            row = metadata.get(symbol)
            if not row:
                continue
            timestamp = int(book["t"]) if str(book.get("t", "")).isdigit() else None
            if timestamp is not None and current_ms - timestamp > max_age_ms:
                continue
            bid = dec(book.get("b"))
            ask = dec(book.get("a"))
            if bid is None or ask is None or bid <= 0 or ask <= 0:
                continue
            ticker = tickers.get(symbol, {})
            market = make_market(
                self.name,
                symbol,
                str(row.get("baseAsset", "")).upper(),
                str(row.get("quoteAsset", "")).upper(),
                bid,
                ask,
                ticker.get("qv"),
                exchange_ts_ms=timestamp,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "limit": 100})
        data = fetch_json(f"https://api.toobit.com/quote/v1/depth?{query}")
        timestamp = data.get("t")
        if str(timestamp or "").isdigit():
            max_age_ms = env_int("PROFIT_MONITOR_TOOBIT_MAX_BOOK_AGE_MS", 60000)
            if now_ms() - int(timestamp) > max_age_ms:
                return [], []
        return sorted_book(pairs(data.get("b", [])), pairs(data.get("a", [])))


class XtAdapter(ExchangeAdapter):
    name = "xt"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://sapi.xt.com/v4/public/symbol").get("result", {}).get("symbols", [])
        metadata = {
            str(row.get("symbol", "")).lower(): row
            for row in symbol_rows
            if str(row.get("quoteCurrency", "")).upper() in quotes
            and str(row.get("state", "")).upper() == "ONLINE"
            and bool(row.get("tradingEnabled"))
            and bool(row.get("openapiEnabled"))
        }
        book_rows = fetch_json("https://sapi.xt.com/v4/public/ticker/book").get("result", [])
        ticker_rows = fetch_json("https://sapi.xt.com/v4/public/ticker/24h").get("result", [])
        tickers = {str(row.get("s", "")).lower(): row for row in ticker_rows}
        max_age_ms = env_int("PROFIT_MONITOR_XT_MAX_BOOK_AGE_MS", 60000)
        current_ms = now_ms()
        markets: list[Market] = []
        for book in book_rows:
            symbol = str(book.get("s", "")).lower()
            row = metadata.get(symbol)
            if not row:
                continue
            timestamp = int(book["t"]) if str(book.get("t", "")).isdigit() else None
            if timestamp is not None and current_ms - timestamp > max_age_ms:
                continue
            taker_fee = dec(row.get("takerFeeRate"))
            ticker = tickers.get(symbol, {})
            market = make_market(
                self.name,
                symbol,
                str(row.get("baseCurrency", "")).upper(),
                str(row.get("quoteCurrency", "")).upper(),
                book.get("bp"),
                book.get("ap"),
                ticker.get("v"),
                taker_bps=taker_fee * Decimal("10000") if taker_fee is not None else None,
                exchange_ts_ms=timestamp,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.lower(), "limit": 100})
        data = fetch_json(f"https://sapi.xt.com/v4/public/depth?{query}").get("result", {})
        timestamp = data.get("timestamp")
        if str(timestamp or "").isdigit():
            max_age_ms = env_int("PROFIT_MONITOR_XT_MAX_BOOK_AGE_MS", 60000)
            if now_ms() - int(timestamp) > max_age_ms:
                return [], []
        return pairs(data.get("bids", [])), pairs(data.get("asks", []))


class HashKeyAdapter(ExchangeAdapter):
    name = "hashkey"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        info = fetch_json("https://api-glb.hashkey.com/api/v1/exchangeInfo")
        ticker_rows = fetch_json("https://api-glb.hashkey.com/quote/v1/ticker/24hr")
        tickers = {str(row.get("s", "")).upper(): row for row in ticker_rows if isinstance(row, dict)}
        selected = [
            row for row in info.get("symbols", [])
            if str(row.get("quoteAsset", "")).upper() in quotes
            and str(row.get("status", "")).upper() == "TRADING"
            and str(row.get("tradeStatus", "")).upper() == "TRADABLE"
        ]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("symbol", "")).upper()
            book_rows = fetch_json(
                f"https://api-glb.hashkey.com/quote/v1/ticker/bookTicker?{urllib.parse.urlencode({'symbol': symbol})}"
            )
            book = book_rows[0] if isinstance(book_rows, list) and book_rows else {}
            ticker = tickers.get(symbol, {})
            return make_market(
                self.name,
                symbol,
                str(row.get("baseAsset", "")).upper(),
                str(row.get("quoteAsset", "")).upper(),
                book.get("b"),
                book.get("a"),
                ticker.get("qv"),
                exchange_ts_ms=int(book["t"]) if str(book.get("t", "")).isdigit() else None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_HASHKEY_WORKERS", 8, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "limit": 100})
        data = fetch_json(f"https://api-glb.hashkey.com/quote/v1/depth?{query}")
        return pairs(data.get("b", [])), pairs(data.get("a", []))


class BingXAdapter(ExchangeAdapter):
    name = "bingx"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        symbol_rows = fetch_json("https://open-api.bingx.com/openApi/spot/v1/common/symbols").get("data", {}).get("symbols", [])
        metadata = {
            str(row.get("symbol", "")).upper(): row
            for row in symbol_rows
            if split_symbol(str(row.get("symbol", "")).upper(), quotes)
            and int(row.get("status") or 0) == 1
            and bool(row.get("apiStateBuy"))
            and bool(row.get("apiStateSell"))
        }
        ticker_rows = fetch_json("https://open-api.bingx.com/openApi/spot/v1/ticker/24hr").get("data", [])
        markets: list[Market] = []
        for row in ticker_rows:
            symbol = str(row.get("symbol", "")).upper()
            meta = metadata.get(symbol)
            split = split_symbol(symbol, quotes)
            if not meta or not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                symbol,
                base,
                quote,
                row.get("bidPrice"),
                row.get("askPrice"),
                row.get("quoteVolume"),
                exchange_ts_ms=int(row["closeTime"]) if str(row.get("closeTime", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"symbol": symbol.upper(), "limit": 100})
        data = fetch_json(f"https://open-api.bingx.com/openApi/spot/v1/market/depth?{query}").get("data", {})
        return sorted_book(pairs(data.get("bids", [])), pairs(data.get("asks", [])))


class BackpackAdapter(ExchangeAdapter):
    name = "backpack"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        market_rows = fetch_json("https://api.backpack.exchange/api/v1/markets")
        ticker_rows = fetch_json("https://api.backpack.exchange/api/v1/tickers")
        tickers = {str(row.get("symbol", "")).upper(): row for row in ticker_rows}
        selected = [
            row for row in market_rows
            if str(row.get("marketType", "")).upper() == "SPOT"
            and str(row.get("orderBookState", "")).lower() == "open"
            and bool(row.get("visible", True))
            and str(row.get("quoteSymbol", "")).upper() in quotes
        ]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("symbol", "")).upper()
            book = fetch_json(f"https://api.backpack.exchange/api/v1/depth?{urllib.parse.urlencode({'symbol': symbol})}")
            bids, asks = sorted_book(pairs(book.get("bids", [])), pairs(book.get("asks", [])))
            if not bids or not asks:
                return None
            ticker = tickers.get(symbol, {})
            return make_market(
                self.name,
                symbol,
                str(row.get("baseSymbol", "")).upper(),
                str(row.get("quoteSymbol", "")).upper(),
                bids[0][0],
                asks[0][0],
                ticker.get("quoteVolume"),
                exchange_ts_ms=int(book["timestamp"]) if str(book.get("timestamp", "")).isdigit() else None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BACKPACK_WORKERS", 10, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.backpack.exchange/api/v1/depth?{urllib.parse.urlencode({'symbol': symbol.upper()})}")
        return sorted_book(pairs(data.get("bids", [])), pairs(data.get("asks", [])))


class PhemexAdapter(ExchangeAdapter):
    name = "phemex"

    def __init__(self) -> None:
        self.products: dict[str, dict[str, Any]] = {}
        self.currency_scales: dict[str, int] = {}

    def load_products(self) -> None:
        if self.products:
            return
        data = fetch_json("https://api.phemex.com/public/products").get("data", {})
        self.currency_scales = {
            str(row.get("currency", "")).upper(): int(row.get("valueScale", 8) or 8)
            for row in data.get("currencies", [])
            if row.get("currency")
        }
        self.products = {
            str(row.get("symbol", "")).upper(): row
            for row in data.get("products", [])
            if str(row.get("type", "")).lower() == "spot"
            and str(row.get("status", "")).lower() == "listed"
            and row.get("symbol")
        }

    @staticmethod
    def scaled(value: Any, scale: int) -> Decimal | None:
        parsed = dec(value)
        if parsed is None:
            return None
        return parsed / (Decimal(10) ** scale)

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        self.load_products()
        ticker_rows = fetch_json("https://api.phemex.com/md/spot/ticker/24hr/all").get("result", [])
        tickers = {str(row.get("symbol", "")).upper(): row for row in ticker_rows}
        markets: list[Market] = []
        for symbol, product in self.products.items():
            quote = str(product.get("quoteCurrency", "")).upper()
            if quote not in quotes:
                continue
            ticker = tickers.get(symbol)
            if not ticker:
                continue
            price_scale = int(product.get("priceScale", 8) or 8)
            quote_scale = self.currency_scales.get(quote, 8)
            taker_fee = dec(product.get("defaultTakerFee"))
            market = make_market(
                self.name,
                symbol,
                str(product.get("baseCurrency", "")).upper(),
                quote,
                self.scaled(ticker.get("bidEp"), price_scale),
                self.scaled(ticker.get("askEp"), price_scale),
                self.scaled(ticker.get("turnoverEv"), quote_scale),
                taker_bps=taker_fee * Decimal("10000") if taker_fee is not None else None,
                exchange_ts_ms=int(int(ticker["timestamp"]) / 1_000_000) if str(ticker.get("timestamp", "")).isdigit() else None,
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        self.load_products()
        product = self.products.get(symbol.upper())
        if not product:
            raise MonitorError(f"unknown phemex spot symbol: {symbol}")
        price_scale = int(product.get("priceScale", 8) or 8)
        base_scale = self.currency_scales.get(str(product.get("baseCurrency", "")).upper(), 8)
        try:
            data = fetch_json(f"https://api.phemex.com/md/orderbook?{urllib.parse.urlencode({'symbol': symbol})}")
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 404, 500}:
                return [], []
            raise
        book = data.get("result", {}).get("book", {})

        def convert(rows: Iterable[Any]) -> list[tuple[Decimal, Decimal]]:
            out: list[tuple[Decimal, Decimal]] = []
            for row in rows:
                if not isinstance(row, (list, tuple)) or len(row) < 2:
                    continue
                price = self.scaled(row[0], price_scale)
                qty = self.scaled(row[1], base_scale)
                if price is not None and qty is not None:
                    out.append((price, qty))
            return out

        return sorted_book(convert(book.get("bids", [])), convert(book.get("asks", [])))


class BullishAdapter(ExchangeAdapter):
    name = "bullish"
    base_url = "https://api.exchange.bullish.com/trading-api/v1"
    quote_priority = ("USDC", "USD", "USDT", "EUR", "BTC", "ETH", "RLUSD", "PYUSD")

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json(f"{self.base_url}/markets")
        selected = [
            row for row in rows
            if row.get("symbol")
            and bool(row.get("spotTradingEnabled"))
            and bool(row.get("marketEnabled"))
            and bool(row.get("createOrderEnabled"))
            and str(row.get("quoteSymbol", "")).upper() in quotes
        ]
        selected.sort(key=self._rank_market)
        max_ticks = env_int("PROFIT_MONITOR_BULLISH_MAX_TICKS", 40)
        if max_ticks > 0:
            selected = selected[:max_ticks]

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("symbol", "")).upper()
            tick = fetch_json(f"{self.base_url}/markets/{urllib.parse.quote(symbol)}/tick", timeout=8.0)
            timestamp = tick.get("publishedAtTimestamp") or tick.get("createdAtTimestamp")
            return make_market(
                self.name,
                symbol,
                str(row.get("baseSymbol", "")).upper(),
                str(row.get("quoteSymbol", "")).upper(),
                tick.get("bestBid"),
                tick.get("bestAsk"),
                tick.get("quoteVolume"),
                exchange_ts_ms=int(timestamp) if str(timestamp or "").isdigit() else None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_BULLISH_WORKERS", 4, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        query = urllib.parse.urlencode({"depth": 100})
        data = fetch_json(f"{self.base_url}/markets/{urllib.parse.quote(symbol.upper())}/orderbook/hybrid?{query}")
        return sorted_book(
            dict_pairs(data.get("bids", []), "price", "priceLevelQuantity"),
            dict_pairs(data.get("asks", []), "price", "priceLevelQuantity"),
        )

    @classmethod
    def _rank_market(cls, row: dict[str, Any]) -> tuple[int, int, str]:
        base = str(row.get("baseSymbol", "")).upper()
        quote = str(row.get("quoteSymbol", "")).upper()
        base_rank = 0 if base in PRIORITY_BASES else 1
        try:
            quote_rank = cls.quote_priority.index(quote)
        except ValueError:
            quote_rank = len(cls.quote_priority)
        return base_rank, quote_rank, str(row.get("symbol", "")).upper()


class WooXAdapter(ExchangeAdapter):
    name = "woox"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        rows = fetch_json("https://api.woo.org/v1/public/info").get("rows", [])
        selected: list[dict[str, Any]] = []
        for row in rows:
            symbol = str(row.get("symbol", "")).upper()
            if not symbol.startswith("SPOT_"):
                continue
            parts = symbol.split("_")
            if len(parts) != 3 or parts[2] not in quotes:
                continue
            if str(row.get("status", "")).upper() != "TRADING" or int(row.get("is_trading") or 0) != 1:
                continue
            selected.append(row)

        def fetch_market(row: dict[str, Any]) -> Market | None:
            symbol = str(row.get("symbol", "")).upper()
            _spot, base, quote = symbol.split("_", 2)
            bids, asks = self.fetch_depth(symbol)
            if not bids or not asks:
                return None
            return make_market(
                self.name,
                symbol,
                base,
                quote,
                bids[0][0],
                asks[0][0],
                None,
                exchange_ts_ms=None,
            )

        return [market for market in fetch_many(selected, "PROFIT_MONITOR_WOOX_WORKERS", 10, fetch_market) if market]

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        try:
            data = fetch_json(f"https://api.woo.org/v1/public/orderbook/{urllib.parse.quote(symbol.upper())}")
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 404, 429, 500, 503}:
                return [], []
            raise
        timestamp = data.get("timestamp")
        if str(timestamp or "").isdigit():
            max_age_ms = env_int("PROFIT_MONITOR_WOOX_MAX_BOOK_AGE_MS", 60000)
            if now_ms() - int(timestamp) > max_age_ms:
                return [], []
        return sorted_book(dict_pairs(data.get("bids", [])), dict_pairs(data.get("asks", [])))


class LBankAdapter(ExchangeAdapter):
    name = "lbank"

    def fetch_markets(self, quotes: set[str]) -> list[Market]:
        data = fetch_json("https://api.lbkex.com/v2/ticker/24hr.do?symbol=all")
        rows = data.get("data", []) if isinstance(data, dict) else []
        markets: list[Market] = []
        for row in rows:
            symbol = str(row.get("symbol", "")).upper()
            split = split_symbol(symbol, quotes)
            if not split:
                continue
            base, quote = split
            market = make_market(
                self.name,
                row.get("symbol", symbol),
                base,
                quote,
                row.get("ticker", {}).get("buy"),
                row.get("ticker", {}).get("sell"),
                row.get("ticker", {}).get("turnover"),
            )
            if market:
                markets.append(market)
        return markets

    def fetch_depth(self, symbol: str) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
        data = fetch_json(f"https://api.lbkex.com/v2/depth.do?{urllib.parse.urlencode({'symbol': symbol, 'size': 100})}")
        return pairs(data.get("data", {}).get("bids", [])), pairs(data.get("data", {}).get("asks", []))


def build_adapters() -> dict[str, ExchangeAdapter]:
    adapters: list[ExchangeAdapter] = [
        BackpackAdapter(),
        BinanceAdapter("binance", "https://api.binance.com", Decimal("10")),
        BinanceAdapter("binanceus", "https://api.binance.us", Decimal("2")),
        BingXAdapter(),
        PhemexAdapter(),
        BullishAdapter(),
        WooXAdapter(),
        BybitAdapter(),
        OkxAdapter(),
        GateAdapter(),
        KuCoinAdapter(),
        MexcAdapter(),
        BitgetAdapter(),
        CoinTrAdapter(),
        CoinWAdapter(),
        DeribitAdapter(),
        HitBtcAdapter(),
        BitMexAdapter(),
        CoinsPhAdapter(),
        CryptoComAdapter(),
        BitfinexAdapter(),
        BitbankAdapter(),
        BitflyerAdapter(),
        CoinbaseAdapter(),
        BitstampAdapter(),
        BitsoAdapter(),
        BithumbAdapter(),
        CoincheckAdapter(),
        BitrueAdapter(),
        BtcMarketsAdapter(),
        NdaxAdapter(),
        BitoProAdapter(),
        LatokenAdapter(),
        PionexAdapter(),
        HyperliquidAdapter(),
        DigiFinexAdapter(),
        ToobitAdapter(),
        XtAdapter(),
        HashKeyAdapter(),
        CoinExAdapter(),
        CoinoneAdapter(),
        HtxAdapter(),
        BitMartAdapter(),
        GmoCoinAdapter(),
        KrakenAdapter(),
        KorbitAdapter(),
        GeminiAdapter(),
        PoloniexAdapter(),
        AscendExAdapter(),
        ExmoAdapter(),
        BtcTurkAdapter(),
        CexIoAdapter(),
        WhiteBitAdapter(),
        UpbitAdapter(),
        IndodaxAdapter(),
        BudaAdapter(),
        NovaDaxAdapter(),
        FoxbitAdapter(),
        MercadoBitcoinAdapter(),
        BitvavoAdapter(),
        IndependentReserveAdapter(),
        LunoAdapter(),
        ValrAdapter(),
        BitkubAdapter(),
        LBankAdapter(),
    ]
    return {adapter.name: adapter for adapter in adapters}


def collect_markets(adapters: list[ExchangeAdapter], quotes: set[str]) -> tuple[list[Market], list[dict[str, str]]]:
    markets: list[Market] = []
    errors: list[dict[str, str]] = []
    workers = max(1, min(len(adapters), int(os.getenv("PROFIT_MONITOR_FETCH_WORKERS", "8"))))

    def fetch_adapter(adapter: ExchangeAdapter) -> tuple[ExchangeAdapter, list[Market], float]:
        started = time.time()
        rows = adapter.fetch_markets(quotes)
        return adapter, rows, time.time() - started

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_adapter = {executor.submit(fetch_adapter, adapter): adapter for adapter in adapters}
        for future in concurrent.futures.as_completed(future_to_adapter):
            adapter = future_to_adapter[future]
            try:
                adapter, rows, elapsed = future.result()
            except (urllib.error.URLError, OSError, TimeoutError, KeyError, IndexError, json.JSONDecodeError, ValueError, MonitorError) as exc:
                errors.append({"exchange": adapter.name, "error": str(exc)})
                print(f"[ERR] {adapter.name}: {exc}", file=sys.stderr)
                continue

            markets.extend(rows)
            print(f"[OK] {adapter.name}: {len(rows)} markets in {elapsed:.1f}s", file=sys.stderr)

    return markets, errors


def rank_routes(
    markets: list[Market],
    *,
    min_volume_quote: Decimal,
    quote_min_volume: dict[str, Decimal],
    min_top_net_bps: Decimal,
    max_gross_bps: Decimal,
    latency_bps: Decimal,
) -> list[RouteCandidate]:
    grouped: dict[tuple[str, str], list[Market]] = {}
    for market in markets:
        grouped.setdefault(market.key, []).append(market)

    candidates: list[RouteCandidate] = []
    for (base, quote), venues in grouped.items():
        min_volume = quote_min_volume.get(quote, min_volume_quote)
        if len({market.exchange for market in venues}) < 2:
            continue
        for buy in venues:
            for sell in venues:
                if buy.exchange == sell.exchange:
                    continue
                if sell.bid <= buy.ask:
                    continue
                gross_bps = (sell.bid - buy.ask) / buy.ask * Decimal("10000")
                fee_bps = buy.taker_bps + sell.taker_bps
                top_net_bps = gross_bps - fee_bps - latency_bps
                depth_proxy = None
                if buy.quote_volume is not None and sell.quote_volume is not None:
                    depth_proxy = min(buy.quote_volume, sell.quote_volume)
                if top_net_bps < min_top_net_bps:
                    continue
                if gross_bps > max_gross_bps:
                    continue
                if depth_proxy is not None and depth_proxy < min_volume:
                    continue
                candidates.append(
                    RouteCandidate(
                        base=base,
                        quote=quote,
                        buy_exchange=buy.exchange,
                        sell_exchange=sell.exchange,
                        buy_symbol=buy.symbol,
                        sell_symbol=sell.symbol,
                        buy_ask=buy.ask,
                        sell_bid=sell.bid,
                        buy_taker_bps=buy.taker_bps,
                        sell_taker_bps=sell.taker_bps,
                        gross_bps=gross_bps,
                        fee_bps=fee_bps,
                        latency_bps=latency_bps,
                        top_net_bps=top_net_bps,
                        depth_proxy_quote=depth_proxy,
                    )
                )
    return sorted(candidates, key=lambda item: item.top_net_bps, reverse=True)


def depth_check_candidate(
    candidate: RouteCandidate,
    adapters_by_name: dict[str, ExchangeAdapter],
    notionals: list[Decimal],
    min_depth_net_bps: Decimal,
) -> tuple[Opportunity | None, dict[str, Any]]:
    buy_adapter = adapters_by_name[candidate.buy_exchange]
    sell_adapter = adapters_by_name[candidate.sell_exchange]
    buy_bids, buy_asks = buy_adapter.fetch_depth(candidate.buy_symbol)
    sell_bids, sell_asks = sell_adapter.fetch_depth(candidate.sell_symbol)
    if not buy_asks or not sell_bids:
        return None, {"error": "empty_depth"}

    best_opportunity: Opportunity | None = None
    bucket_results: list[dict[str, Any]] = []
    for notional in notionals:
        buy_fill = buy_with_quote(buy_asks, notional)
        if not buy_fill.full or buy_fill.avg_price is None:
            bucket_results.append({"notional": notional, "status": "buy_depth_insufficient"})
            continue
        sell_fill = sell_base(sell_bids, buy_fill.base)
        if not sell_fill.full or sell_fill.avg_price is None:
            bucket_results.append({"notional": notional, "status": "sell_depth_insufficient"})
            continue

        buy_fee_quote = buy_fill.quote * candidate.buy_taker_bps / Decimal("10000")
        sell_fee_quote = sell_fill.quote * candidate.sell_taker_bps / Decimal("10000")
        latency_haircut_quote = buy_fill.quote * candidate.latency_bps / Decimal("10000")
        net_profit = sell_fill.quote - buy_fill.quote - buy_fee_quote - sell_fee_quote - latency_haircut_quote
        net_bps = net_profit / buy_fill.quote * Decimal("10000")
        gross_bps = (sell_fill.avg_price - buy_fill.avg_price) / buy_fill.avg_price * Decimal("10000")
        row = {
            "notional": notional,
            "status": "ok",
            "buy_avg": buy_fill.avg_price,
            "sell_avg": sell_fill.avg_price,
            "base_size": buy_fill.base,
            "buy_quote": buy_fill.quote,
            "sell_quote": sell_fill.quote,
            "buy_fee_quote": buy_fee_quote,
            "sell_fee_quote": sell_fee_quote,
            "latency_haircut_quote": latency_haircut_quote,
            "net_profit_quote": net_profit,
            "net_bps": net_bps,
            "gross_bps": gross_bps,
            "buy_levels": buy_fill.levels,
            "sell_levels": sell_fill.levels,
        }
        bucket_results.append(row)
        if net_bps >= min_depth_net_bps:
            opportunity = Opportunity(
                detected_at_ms=now_ms(),
                mode="inventory_based_public_books_no_transfer",
                base=candidate.base,
                quote=candidate.quote,
                buy_exchange=candidate.buy_exchange,
                sell_exchange=candidate.sell_exchange,
                buy_symbol=candidate.buy_symbol,
                sell_symbol=candidate.sell_symbol,
                notional_quote=notional,
                base_size=buy_fill.base,
                buy_avg=buy_fill.avg_price,
                sell_avg=sell_fill.avg_price,
                buy_quote=buy_fill.quote,
                sell_quote=sell_fill.quote,
                buy_fee_quote=buy_fee_quote,
                sell_fee_quote=sell_fee_quote,
                latency_haircut_quote=latency_haircut_quote,
                net_profit_quote=net_profit,
                net_bps=net_bps,
                gross_bps=gross_bps,
                top_net_bps=candidate.top_net_bps,
                buy_levels=buy_fill.levels,
                sell_levels=sell_fill.levels,
                depth_proxy_quote=candidate.depth_proxy_quote,
                evidence_json=json.dumps(
                    {
                        "candidate": asdict(candidate),
                        "bucket_results": bucket_results,
                        "depth_top": {
                            "buy_best_ask": buy_asks[0][0],
                            "sell_best_bid": sell_bids[0][0],
                        },
                    },
                    default=json_decimal_default,
                    sort_keys=True,
                ),
            )
            if best_opportunity is None or opportunity.net_profit_quote > best_opportunity.net_profit_quote:
                best_opportunity = opportunity
    return best_opportunity, {"bucket_results": bucket_results}


def init_sqlite(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at_ms INTEGER NOT NULL,
            route_key TEXT NOT NULL,
            mode TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            notional_quote TEXT NOT NULL,
            base_size TEXT NOT NULL,
            buy_avg TEXT NOT NULL,
            sell_avg TEXT NOT NULL,
            buy_quote TEXT NOT NULL,
            sell_quote TEXT NOT NULL,
            buy_fee_quote TEXT NOT NULL,
            sell_fee_quote TEXT NOT NULL,
            latency_haircut_quote TEXT NOT NULL,
            net_profit_quote TEXT NOT NULL,
            net_bps TEXT NOT NULL,
            gross_bps TEXT NOT NULL,
            top_net_bps TEXT NOT NULL,
            buy_levels INTEGER NOT NULL,
            sell_levels INTEGER NOT NULL,
            depth_proxy_quote TEXT,
            evidence_json TEXT NOT NULL,
            operational_grade TEXT NOT NULL DEFAULT 'status_unavailable',
            status_hint TEXT NOT NULL DEFAULT '',
            status_json TEXT NOT NULL DEFAULT '{}'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS monitor_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at_ms INTEGER NOT NULL,
            elapsed_ms INTEGER NOT NULL,
            markets_total INTEGER NOT NULL,
            candidates_total INTEGER NOT NULL,
            depth_checked INTEGER NOT NULL,
            opportunities_saved INTEGER NOT NULL,
            errors_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunity_cases (
            route_key TEXT PRIMARY KEY,
            mode TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            first_seen_ms INTEGER NOT NULL,
            last_seen_ms INTEGER NOT NULL,
            seen_count INTEGER NOT NULL,
            max_net_bps TEXT NOT NULL,
            max_net_profit_quote TEXT NOT NULL,
            max_notional_quote TEXT NOT NULL,
            last_net_bps TEXT NOT NULL,
            last_net_profit_quote TEXT NOT NULL,
            last_notional_quote TEXT NOT NULL,
            last_operational_grade TEXT NOT NULL,
            last_status_hint TEXT NOT NULL,
            last_status_json TEXT NOT NULL
        )
        """
    )
    ensure_column(conn, "opportunities", "operational_grade", "TEXT NOT NULL DEFAULT 'status_unavailable'")
    ensure_column(conn, "opportunities", "status_hint", "TEXT NOT NULL DEFAULT ''")
    ensure_column(conn, "opportunities", "status_json", "TEXT NOT NULL DEFAULT '{}'")
    conn.commit()
    return conn


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def opportunity_to_json(opportunity: Opportunity) -> dict[str, Any]:
    row = asdict(opportunity)
    row["route_key"] = opportunity.route_key
    return row


def update_opportunity_case(conn: sqlite3.Connection, opportunity: Opportunity) -> None:
    existing = conn.execute(
        """
        SELECT seen_count, max_net_bps, max_net_profit_quote, max_notional_quote
        FROM opportunity_cases
        WHERE route_key = ?
        """,
        (opportunity.route_key,),
    ).fetchone()
    if existing is None:
        conn.execute(
            """
            INSERT INTO opportunity_cases (
                route_key, mode, base, quote, buy_exchange, sell_exchange,
                buy_symbol, sell_symbol, first_seen_ms, last_seen_ms, seen_count,
                max_net_bps, max_net_profit_quote, max_notional_quote,
                last_net_bps, last_net_profit_quote, last_notional_quote,
                last_operational_grade, last_status_hint, last_status_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                opportunity.route_key,
                opportunity.mode,
                opportunity.base,
                opportunity.quote,
                opportunity.buy_exchange,
                opportunity.sell_exchange,
                opportunity.buy_symbol,
                opportunity.sell_symbol,
                opportunity.detected_at_ms,
                opportunity.detected_at_ms,
                1,
                quant(opportunity.net_bps),
                quant(opportunity.net_profit_quote),
                quant(opportunity.notional_quote),
                quant(opportunity.net_bps),
                quant(opportunity.net_profit_quote),
                quant(opportunity.notional_quote),
                opportunity.operational_grade,
                opportunity.status_hint,
                opportunity.status_json,
            ),
        )
        return

    seen_count, max_net_bps, max_net_profit_quote, max_notional_quote = existing
    is_new_max = opportunity.net_bps > Decimal(str(max_net_bps))
    conn.execute(
        """
        UPDATE opportunity_cases
        SET
            last_seen_ms = ?,
            seen_count = ?,
            max_net_bps = ?,
            max_net_profit_quote = ?,
            max_notional_quote = ?,
            last_net_bps = ?,
            last_net_profit_quote = ?,
            last_notional_quote = ?,
            last_operational_grade = ?,
            last_status_hint = ?,
            last_status_json = ?
        WHERE route_key = ?
        """,
        (
            opportunity.detected_at_ms,
            int(seen_count) + 1,
            quant(opportunity.net_bps) if is_new_max else max_net_bps,
            quant(opportunity.net_profit_quote) if is_new_max else max_net_profit_quote,
            quant(opportunity.notional_quote) if is_new_max else max_notional_quote,
            quant(opportunity.net_bps),
            quant(opportunity.net_profit_quote),
            quant(opportunity.notional_quote),
            opportunity.operational_grade,
            opportunity.status_hint,
            opportunity.status_json,
            opportunity.route_key,
        ),
    )


def save_opportunity(conn: sqlite3.Connection, jsonl_path: Path, opportunity: Opportunity) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(opportunity_to_json(opportunity), default=json_decimal_default, sort_keys=True) + "\n")

    conn.execute(
        """
        INSERT INTO opportunities (
            detected_at_ms, route_key, mode, base, quote, buy_exchange, sell_exchange,
            buy_symbol, sell_symbol, notional_quote, base_size, buy_avg, sell_avg,
            buy_quote, sell_quote, buy_fee_quote, sell_fee_quote, latency_haircut_quote,
            net_profit_quote, net_bps, gross_bps, top_net_bps, buy_levels, sell_levels,
            depth_proxy_quote, evidence_json, operational_grade, status_hint, status_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            opportunity.detected_at_ms,
            opportunity.route_key,
            opportunity.mode,
            opportunity.base,
            opportunity.quote,
            opportunity.buy_exchange,
            opportunity.sell_exchange,
            opportunity.buy_symbol,
            opportunity.sell_symbol,
            quant(opportunity.notional_quote),
            quant(opportunity.base_size),
            quant(opportunity.buy_avg),
            quant(opportunity.sell_avg),
            quant(opportunity.buy_quote),
            quant(opportunity.sell_quote),
            quant(opportunity.buy_fee_quote),
            quant(opportunity.sell_fee_quote),
            quant(opportunity.latency_haircut_quote),
            quant(opportunity.net_profit_quote),
            quant(opportunity.net_bps),
            quant(opportunity.gross_bps),
            quant(opportunity.top_net_bps),
            opportunity.buy_levels,
            opportunity.sell_levels,
            quant(opportunity.depth_proxy_quote),
            opportunity.evidence_json,
            opportunity.operational_grade,
            opportunity.status_hint,
            opportunity.status_json,
        ),
    )
    update_opportunity_case(conn, opportunity)
    conn.commit()


def save_cycle(
    conn: sqlite3.Connection,
    *,
    started_at_ms: int,
    elapsed_ms: int,
    markets_total: int,
    candidates_total: int,
    depth_checked: int,
    opportunities_saved: int,
    errors: list[dict[str, str]],
) -> None:
    conn.execute(
        """
        INSERT INTO monitor_cycles (
            started_at_ms, elapsed_ms, markets_total, candidates_total,
            depth_checked, opportunities_saved, errors_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            started_at_ms,
            elapsed_ms,
            markets_total,
            candidates_total,
            depth_checked,
            opportunities_saved,
            json.dumps(errors, sort_keys=True),
        ),
    )
    conn.commit()


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_decimal_csv(value: str) -> list[Decimal]:
    return [Decimal(item.strip()) for item in value.split(",") if item.strip()]


def parse_quote_decimal_lists(value: str) -> dict[str, list[Decimal]]:
    out: dict[str, list[Decimal]] = {}
    for chunk in value.split(";"):
        if not chunk.strip():
            continue
        quote, _, raw_values = chunk.partition(":")
        if not quote or not raw_values:
            continue
        values = [Decimal(item.strip()) for item in raw_values.replace("|", ",").split(",") if item.strip()]
        if values:
            out[quote.strip().upper()] = values
    return out


def parse_quote_decimal_map(value: str) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for chunk in value.split(";"):
        if not chunk.strip():
            continue
        quote, _, raw_value = chunk.partition(":")
        if quote and raw_value:
            out[quote.strip().upper()] = Decimal(raw_value.strip())
    return out


def format_quote_decimal_lists(rows: dict[str, list[Decimal]]) -> str:
    return ";".join(f"{quote}:{'|'.join(map(str, values))}" for quote, values in sorted(rows.items()))


def run_cycle(
    *,
    adapters: list[ExchangeAdapter],
    adapters_by_name: dict[str, ExchangeAdapter],
    conn: sqlite3.Connection,
    jsonl_path: Path,
    status_conn: sqlite3.Connection | None,
    quotes: set[str],
    notionals: list[Decimal],
    quote_notionals: dict[str, list[Decimal]],
    min_volume_quote: Decimal,
    quote_min_volume: dict[str, Decimal],
    min_top_net_bps: Decimal,
    min_depth_net_bps: Decimal,
    max_gross_bps: Decimal,
    latency_bps: Decimal,
    max_candidates: int,
    dedupe_window_secs: int,
    last_saved_by_route: dict[str, tuple[int, Decimal]],
) -> None:
    started = now_ms()
    markets, errors = collect_markets(adapters, quotes)
    candidates = rank_routes(
        markets,
        min_volume_quote=min_volume_quote,
        quote_min_volume=quote_min_volume,
        min_top_net_bps=min_top_net_bps,
        max_gross_bps=max_gross_bps,
        latency_bps=latency_bps,
    )
    checked = 0
    saved = 0
    selected_candidates = candidates[:max_candidates]
    depth_workers = max(1, min(len(selected_candidates), int(os.getenv("PROFIT_MONITOR_DEPTH_WORKERS", "8"))))

    def check_candidate(candidate: RouteCandidate) -> tuple[RouteCandidate, Opportunity | None]:
        opportunity, _evidence = depth_check_candidate(
            candidate,
            adapters_by_name,
            quote_notionals.get(candidate.quote, notionals),
            min_depth_net_bps,
        )
        return candidate, opportunity

    with concurrent.futures.ThreadPoolExecutor(max_workers=depth_workers) as executor:
        future_to_candidate = {
            executor.submit(check_candidate, candidate): candidate for candidate in selected_candidates
        }
        for future in concurrent.futures.as_completed(future_to_candidate):
            candidate = future_to_candidate[future]
            checked += 1
            try:
                _candidate, opportunity = future.result()
            except Exception as exc:
                errors.append({"exchange": f"{candidate.buy_exchange}->{candidate.sell_exchange}", "error": str(exc)})
                continue
            if opportunity is None:
                continue
            route_key = opportunity.route_key
            previous = last_saved_by_route.get(route_key)
            if previous:
                previous_ms, previous_net = previous
                inside_window = opportunity.detected_at_ms - previous_ms < dedupe_window_secs * 1000
                materially_better = opportunity.net_bps > previous_net + Decimal("10")
                if inside_window and not materially_better:
                    continue
            opportunity = attach_operational_status(opportunity, status_conn)
            save_opportunity(conn, jsonl_path, opportunity)
            last_saved_by_route[route_key] = (opportunity.detected_at_ms, opportunity.net_bps)
            saved += 1
            print(
                "[PROFIT] "
                f"{opportunity.route_key} notional={opportunity.notional_quote} "
                f"net={opportunity.net_profit_quote:.8f} {opportunity.quote} "
                f"net_bps={opportunity.net_bps:.3f} "
                f"grade={opportunity.operational_grade}",
                flush=True,
            )
    elapsed = now_ms() - started
    save_cycle(
        conn,
        started_at_ms=started,
        elapsed_ms=elapsed,
        markets_total=len(markets),
        candidates_total=len(candidates),
        depth_checked=checked,
        opportunities_saved=saved,
        errors=errors,
    )
    print(
        "[CYCLE] "
        f"markets={len(markets)} candidates={len(candidates)} "
        f"depth_checked={checked} saved={saved} errors={len(errors)} "
        f"elapsed_ms={elapsed}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="24/7 public-market arbitrage monitor")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--interval-sec", type=float, default=float(os.getenv("PROFIT_MONITOR_INTERVAL_SEC", "30")))
    parser.add_argument("--out-dir", default=os.getenv("PROFIT_MONITOR_OUT_DIR", "data"))
    parser.add_argument("--quotes", default=os.getenv("PROFIT_MONITOR_QUOTES", ",".join(sorted(DEFAULT_QUOTES))))
    parser.add_argument("--exchanges", default=os.getenv("PROFIT_MONITOR_EXCHANGES", ",".join(sorted(DEFAULT_EXCHANGE_NAMES))))
    parser.add_argument("--exclude-exchanges", default=os.getenv("PROFIT_MONITOR_EXCLUDE_EXCHANGES", ""))
    parser.add_argument("--notionals", default=os.getenv("PROFIT_MONITOR_NOTIONALS", "100,500,1000,2500,5000,10000"))
    parser.add_argument(
        "--quote-notionals",
        default=os.getenv("PROFIT_MONITOR_QUOTE_NOTIONALS", format_quote_decimal_lists({k: parse_decimal_csv(v) for k, v in DEFAULT_QUOTE_NOTIONALS.items()})),
        help="Quote-specific notionals, e.g. BTC:0.001|0.005;MXN:1000|5000",
    )
    parser.add_argument("--min-volume-quote", default=os.getenv("PROFIT_MONITOR_MIN_VOLUME_QUOTE", "100000"))
    parser.add_argument(
        "--quote-min-volume",
        default=os.getenv("PROFIT_MONITOR_QUOTE_MIN_VOLUME", ";".join(f"{k}:{v}" for k, v in sorted(DEFAULT_MIN_VOLUME_BY_QUOTE.items()))),
        help="Quote-specific 24h volume floors, e.g. BTC:1;ETH:25",
    )
    parser.add_argument("--min-top-net-bps", default=os.getenv("PROFIT_MONITOR_MIN_TOP_NET_BPS", "1"))
    parser.add_argument("--min-depth-net-bps", default=os.getenv("PROFIT_MONITOR_MIN_DEPTH_NET_BPS", "1"))
    parser.add_argument("--max-gross-bps", default=os.getenv("PROFIT_MONITOR_MAX_GROSS_BPS", "1000"))
    parser.add_argument("--latency-bps", default=os.getenv("PROFIT_MONITOR_LATENCY_BPS", "2"))
    parser.add_argument("--max-candidates", type=int, default=int(os.getenv("PROFIT_MONITOR_MAX_CANDIDATES", "40")))
    parser.add_argument("--dedupe-window-sec", type=int, default=int(os.getenv("PROFIT_MONITOR_DEDUPE_WINDOW_SEC", "60")))
    parser.add_argument("--status-db", default=os.getenv("PROFIT_MONITOR_STATUS_DB", str(DEFAULT_STATUS_DB)))
    args = parser.parse_args()

    quotes = {item.upper() for item in parse_csv(args.quotes)}
    notionals = parse_decimal_csv(args.notionals)
    quote_notionals = parse_quote_decimal_lists(args.quote_notionals)
    quote_min_volume = parse_quote_decimal_map(args.quote_min_volume)
    adapters_by_name = build_adapters()
    selected_names = set(parse_csv(args.exchanges)) if args.exchanges else set(DEFAULT_EXCHANGE_NAMES)
    excluded_names = set(parse_csv(args.exclude_exchanges))
    adapter_names = [name for name in sorted(selected_names) if name in adapters_by_name and name not in excluded_names]
    adapters = [adapters_by_name[name] for name in adapter_names]
    if not adapters:
        raise SystemExit("No valid exchanges selected")

    out_dir = Path(args.out_dir)
    sqlite_path = out_dir / "profitable_cases.sqlite"
    jsonl_path = out_dir / "profitable_cases.jsonl"
    conn = init_sqlite(sqlite_path)
    status_conn = open_status_db(Path(args.status_db).expanduser())
    last_saved_by_route: dict[str, tuple[int, Decimal]] = {}

    print("profit-monitor public scanner")
    print(f"mode=inventory_based_public_books_no_transfer exchanges={','.join(adapter_names)}")
    print(f"quotes={','.join(sorted(quotes))} notionals={','.join(map(str, notionals))}")
    if quote_notionals:
        enabled_quote_notionals = {quote: values for quote, values in quote_notionals.items() if quote in quotes}
        print(f"quote_notionals={format_quote_decimal_lists(enabled_quote_notionals)}")
    print(f"outputs={jsonl_path} {sqlite_path}")
    print(f"status_db={args.status_db} enabled={status_conn is not None}")
    print("risk=no private keys, no orders, transfer/deposit status is not proven by this monitor\n")

    while True:
        run_cycle(
            adapters=adapters,
            adapters_by_name=adapters_by_name,
            conn=conn,
            jsonl_path=jsonl_path,
            status_conn=status_conn,
            quotes=quotes,
            notionals=notionals,
            quote_notionals=quote_notionals,
            min_volume_quote=Decimal(args.min_volume_quote),
            quote_min_volume=quote_min_volume,
            min_top_net_bps=Decimal(args.min_top_net_bps),
            min_depth_net_bps=Decimal(args.min_depth_net_bps),
            max_gross_bps=Decimal(args.max_gross_bps),
            latency_bps=Decimal(args.latency_bps),
            max_candidates=args.max_candidates,
            dedupe_window_secs=args.dedupe_window_sec,
            last_saved_by_route=last_saved_by_route,
        )
        if args.once:
            break
        time.sleep(max(args.interval_sec, 1.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
