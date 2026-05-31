#!/usr/bin/env python3
"""Fast public BTC order-book monitor.

This process complements the broad scanner. It watches only BTC spot books
across many venues and quote lanes, then saves inventory-based cross-venue
opportunities that remain profitable after walking depth, taker fees, and a
latency haircut.

No private keys, no orders, no withdrawals.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Any, Callable, Iterable

getcontext().prec = 40


DEFAULT_TAKER_BPS = {
    "binance": Decimal("10"),
    "binanceus": Decimal("2"),
    "bybit": Decimal("10"),
    "okx": Decimal("10"),
    "gate": Decimal("10"),
    "kucoin": Decimal("10"),
    "mexc": Decimal("5"),
    "bitget": Decimal("10"),
    "coinbase": Decimal("60"),
    "cryptocom": Decimal("7.5"),
    "bitfinex": Decimal("0"),
    "bitstamp": Decimal("40"),
    "bitso": Decimal("50"),
    "coinex": Decimal("20"),
    "htx": Decimal("20"),
    "bitmart": Decimal("25"),
    "kraken": Decimal("40"),
    "gemini": Decimal("120"),
    "poloniex": Decimal("14.5"),
    "ascendex": Decimal("10"),
    "exmo": Decimal("30"),
    "btcturk": Decimal("20"),
    "cexio": Decimal("25"),
}

DEFAULT_NOTIONALS_BY_QUOTE = {
    "USDT": "100,500,1000,2500,5000,10000",
    "USDC": "100,500,1000,2500,5000,10000",
    "USD": "100,500,1000,2500,5000,10000",
    "EUR": "100,500,1000,2500,5000",
    "GBP": "100,500,1000,2500,5000",
    "MXN": "1000,5000,10000,50000,100000,200000",
    "TRY": "5000,25000,50000,100000,250000",
}

DEFAULT_STATUS_DB = Path.home() / "Library/Application Support/hackathon-btc/status/status.sqlite"


@dataclass(frozen=True)
class VenuePair:
    exchange: str
    symbol: str
    quote: str
    fetcher: str
    taker_bps: Decimal


@dataclass(frozen=True)
class Book:
    exchange: str
    symbol: str
    quote: str
    bids: list[tuple[Decimal, Decimal]]
    asks: list[tuple[Decimal, Decimal]]
    taker_bps: Decimal
    fetched_at_ms: int
    elapsed_ms: int

    @property
    def best_bid(self) -> Decimal:
        return self.bids[0][0]

    @property
    def best_ask(self) -> Decimal:
        return self.asks[0][0]


@dataclass(frozen=True)
class Fill:
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
        return f"BTC/{self.quote}:{self.buy_exchange}:{self.buy_symbol}->{self.sell_exchange}:{self.sell_symbol}"


def now_ms() -> int:
    return int(time.time() * 1000)


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


def fetch_json(url: str, timeout: float = 8.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hackathon-btc-hot-path/0.1",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


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


def flat_pairs(values: Iterable[Any]) -> list[tuple[Decimal, Decimal]]:
    rows = list(values)
    out: list[tuple[Decimal, Decimal]] = []
    for index in range(0, len(rows) - 1, 2):
        price = dec(rows[index])
        qty = dec(rows[index + 1])
        if price is not None and qty is not None:
            out.append((price, qty))
    return out


def bitfinex_levels(rows: Iterable[Any]) -> tuple[list[tuple[Decimal, Decimal]], list[tuple[Decimal, Decimal]]]:
    bids: list[tuple[Decimal, Decimal]] = []
    asks: list[tuple[Decimal, Decimal]] = []
    for row in rows:
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
    bids.sort(key=lambda item: item[0], reverse=True)
    asks.sort(key=lambda item: item[0])
    return bids, asks


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
    return Fill(base=base, quote=spent, avg_price=(spent / base if base > 0 else None), full=remaining == 0, levels=levels)


def sell_base(bids: list[tuple[Decimal, Decimal]], base_amount: Decimal) -> Fill:
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
    return Fill(base=sold, quote=got, avg_price=(got / sold if sold > 0 else None), full=remaining == 0, levels=levels)


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
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
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


def parse_decimal_csv(value: str) -> list[Decimal]:
    return [Decimal(item.strip()) for item in value.split(",") if item.strip()]


def parse_quote_notionals(value: str) -> dict[str, list[Decimal]]:
    out: dict[str, list[Decimal]] = {}
    for chunk in value.split(";"):
        if not chunk.strip():
            continue
        quote, _, values = chunk.partition(":")
        if quote and values:
            out[quote.strip().upper()] = parse_decimal_csv(values.replace("|", ","))
    return out


def format_quote_notionals(rows: dict[str, str]) -> str:
    return ";".join(f"{quote}:{values}" for quote, values in sorted(rows.items()))


def make_book(pair: VenuePair, bids: list[tuple[Decimal, Decimal]], asks: list[tuple[Decimal, Decimal]], started_ms: int) -> Book | None:
    bids = sorted([(p, q) for p, q in bids if p > 0 and q > 0], key=lambda item: item[0], reverse=True)
    asks = sorted([(p, q) for p, q in asks if p > 0 and q > 0], key=lambda item: item[0])
    if not bids or not asks or bids[0][0] >= asks[0][0]:
        return None
    finished_ms = now_ms()
    return Book(
        exchange=pair.exchange,
        symbol=pair.symbol,
        quote=pair.quote,
        bids=bids,
        asks=asks,
        taker_bps=pair.taker_bps,
        fetched_at_ms=finished_ms,
        elapsed_ms=finished_ms - started_ms,
    )


def fetch_book(pair: VenuePair) -> Book | None:
    started_ms = now_ms()
    symbol = pair.symbol
    if pair.fetcher == "binance":
        data = fetch_json(f"https://api.binance.com/api/v3/depth?{urllib.parse.urlencode({'symbol': symbol, 'limit': 100})}")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "binanceus":
        data = fetch_json(f"https://api.binance.us/api/v3/depth?{urllib.parse.urlencode({'symbol': symbol, 'limit': 100})}")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "bybit":
        data = fetch_json(f"https://api.bybit.com/v5/market/orderbook?{urllib.parse.urlencode({'category': 'spot', 'symbol': symbol, 'limit': 50})}")
        result = data.get("result", {})
        return make_book(pair, pairs(result.get("b", [])), pairs(result.get("a", [])), started_ms)
    if pair.fetcher == "okx":
        data = fetch_json(f"https://www.okx.com/api/v5/market/books?{urllib.parse.urlencode({'instId': symbol, 'sz': 100})}")
        book = (data.get("data") or [{}])[0]
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "gate":
        data = fetch_json(f"https://api.gateio.ws/api/v4/spot/order_book?{urllib.parse.urlencode({'currency_pair': symbol, 'limit': 100})}")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "kucoin":
        data = fetch_json(f"https://api.kucoin.com/api/v1/market/orderbook/level2_100?{urllib.parse.urlencode({'symbol': symbol})}")
        book = data.get("data", {})
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "mexc":
        data = fetch_json(f"https://api.mexc.com/api/v3/depth?{urllib.parse.urlencode({'symbol': symbol, 'limit': 100})}")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "bitget":
        data = fetch_json(f"https://api.bitget.com/api/v2/spot/market/orderbook?{urllib.parse.urlencode({'symbol': symbol, 'type': 'step0', 'limit': 100})}")
        book = data.get("data", {})
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "coinbase":
        data = fetch_json(f"https://api.exchange.coinbase.com/products/{urllib.parse.quote(symbol)}/book?level=2")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "cryptocom":
        data = fetch_json(f"https://api.crypto.com/exchange/v1/public/get-book?{urllib.parse.urlencode({'instrument_name': symbol, 'depth': 50})}")
        book = (data.get("result", {}).get("data") or [{}])[0]
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "bitfinex":
        rows = fetch_json(f"https://api-pub.bitfinex.com/v2/book/{symbol}/P0?len=100")
        bids, asks = bitfinex_levels(rows)
        return make_book(pair, bids, asks, started_ms)
    if pair.fetcher == "bitstamp":
        data = fetch_json(f"https://www.bitstamp.net/api/v2/order_book/{symbol}/")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "bitso":
        data = fetch_json(f"https://api.bitso.com/v3/order_book/?{urllib.parse.urlencode({'book': symbol, 'aggregate': 'false'})}")
        book = data.get("payload", {})
        bids = [(dec(item.get("price")), dec(item.get("amount"))) for item in book.get("bids", [])]
        asks = [(dec(item.get("price")), dec(item.get("amount"))) for item in book.get("asks", [])]
        return make_book(pair, [(p, q) for p, q in bids if p and q], [(p, q) for p, q in asks if p and q], started_ms)
    if pair.fetcher == "coinex":
        data = fetch_json(f"https://api.coinex.com/v2/spot/depth?{urllib.parse.urlencode({'market': symbol, 'limit': 50, 'interval': '0'})}")
        book = data.get("data", {})
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "htx":
        data = fetch_json(f"https://api.huobi.pro/market/depth?{urllib.parse.urlencode({'symbol': symbol, 'type': 'step0', 'depth': 100})}")
        tick = data.get("tick", {})
        return make_book(pair, pairs(tick.get("bids", [])), pairs(tick.get("asks", [])), started_ms)
    if pair.fetcher == "bitmart":
        data = fetch_json(f"https://api-cloud.bitmart.com/spot/quotation/v3/books?{urllib.parse.urlencode({'symbol': symbol, 'limit': 50})}")
        return make_book(pair, pairs(data.get("data", {}).get("bids", [])), pairs(data.get("data", {}).get("asks", [])), started_ms)
    if pair.fetcher == "kraken":
        data = fetch_json(f"https://api.kraken.com/0/public/Depth?{urllib.parse.urlencode({'pair': symbol, 'count': 100})}")
        result = data.get("result", {})
        book = next(iter(result.values()))
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "gemini":
        data = fetch_json(f"https://api.gemini.com/v1/book/{symbol}?limit_bids=100&limit_asks=100")
        bids = [(dec(item.get("price")), dec(item.get("amount"))) for item in data.get("bids", [])]
        asks = [(dec(item.get("price")), dec(item.get("amount"))) for item in data.get("asks", [])]
        return make_book(pair, [(p, q) for p, q in bids if p and q], [(p, q) for p, q in asks if p and q], started_ms)
    if pair.fetcher == "poloniex":
        data = fetch_json(f"https://api.poloniex.com/markets/{urllib.parse.quote(symbol)}/orderBook?limit=100")
        return make_book(pair, flat_pairs(data.get("bids", [])), flat_pairs(data.get("asks", [])), started_ms)
    if pair.fetcher == "ascendex":
        data = fetch_json(f"https://ascendex.com/api/pro/v1/depth?{urllib.parse.urlencode({'symbol': symbol})}")
        book = data.get("data", {}).get("data", {})
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "exmo":
        data = fetch_json(f"https://api.exmo.com/v1.1/order_book?{urllib.parse.urlencode({'pair': symbol, 'limit': 100})}")
        book = data.get(symbol, {})
        return make_book(pair, pairs(book.get("bid", [])), pairs(book.get("ask", [])), started_ms)
    if pair.fetcher == "btcturk":
        data = fetch_json(f"https://api.btcturk.com/api/v2/orderbook?{urllib.parse.urlencode({'pairSymbol': symbol, 'limit': 100})}")
        book = data.get("data", {})
        return make_book(pair, pairs(book.get("bids", [])), pairs(book.get("asks", [])), started_ms)
    if pair.fetcher == "cexio":
        data = fetch_json(f"https://cex.io/api/order_book/{urllib.parse.quote(symbol, safe='/')}?depth=100")
        return make_book(pair, pairs(data.get("bids", [])), pairs(data.get("asks", [])), started_ms)
    raise ValueError(f"unknown fetcher: {pair.fetcher}")


def default_pairs() -> list[VenuePair]:
    rows = [
        ("binance", "BTCUSDT", "USDT", "binance"),
        ("binance", "BTCUSDC", "USDC", "binance"),
        ("binanceus", "BTCUSDT", "USDT", "binanceus"),
        ("binanceus", "BTCUSD", "USD", "binanceus"),
        ("bybit", "BTCUSDT", "USDT", "bybit"),
        ("bybit", "BTCUSDC", "USDC", "bybit"),
        ("okx", "BTC-USDT", "USDT", "okx"),
        ("okx", "BTC-USDC", "USDC", "okx"),
        ("gate", "BTC_USDT", "USDT", "gate"),
        ("gate", "BTC_USDC", "USDC", "gate"),
        ("kucoin", "BTC-USDT", "USDT", "kucoin"),
        ("kucoin", "BTC-USDC", "USDC", "kucoin"),
        ("mexc", "BTCUSDT", "USDT", "mexc"),
        ("mexc", "BTCUSDC", "USDC", "mexc"),
        ("bitget", "BTCUSDT", "USDT", "bitget"),
        ("bitget", "BTCUSDC", "USDC", "bitget"),
        ("coinbase", "BTC-USD", "USD", "coinbase"),
        ("cryptocom", "BTC_USDT", "USDT", "cryptocom"),
        ("bitfinex", "tBTCUSD", "USD", "bitfinex"),
        ("bitfinex", "tBTCUST", "USDT", "bitfinex"),
        ("bitfinex", "tBTCEUR", "EUR", "bitfinex"),
        ("bitfinex", "tBTCGBP", "GBP", "bitfinex"),
        ("bitstamp", "btcusd", "USD", "bitstamp"),
        ("bitstamp", "btceur", "EUR", "bitstamp"),
        ("bitstamp", "btcgbp", "GBP", "bitstamp"),
        ("bitso", "btc_mxn", "MXN", "bitso"),
        ("bitso", "btc_usd", "USD", "bitso"),
        ("coinex", "BTCUSDT", "USDT", "coinex"),
        ("coinex", "BTCUSDC", "USDC", "coinex"),
        ("htx", "btcusdt", "USDT", "htx"),
        ("htx", "btcusdc", "USDC", "htx"),
        ("bitmart", "BTC_USDT", "USDT", "bitmart"),
        ("bitmart", "BTC_USDC", "USDC", "bitmart"),
        ("kraken", "XBTUSD", "USD", "kraken"),
        ("kraken", "XBTUSDT", "USDT", "kraken"),
        ("kraken", "XBTUSDC", "USDC", "kraken"),
        ("kraken", "XBTEUR", "EUR", "kraken"),
        ("gemini", "btcusd", "USD", "gemini"),
        ("poloniex", "BTC_USDT", "USDT", "poloniex"),
        ("poloniex", "BTC_USDC", "USDC", "poloniex"),
        ("ascendex", "BTC/USDT", "USDT", "ascendex"),
        ("ascendex", "BTC/USD", "USD", "ascendex"),
        ("exmo", "BTC_USDT", "USDT", "exmo"),
        ("exmo", "BTC_USD", "USD", "exmo"),
        ("exmo", "BTC_EUR", "EUR", "exmo"),
        ("exmo", "BTC_UAH", "UAH", "exmo"),
        ("btcturk", "BTCTRY", "TRY", "btcturk"),
        ("btcturk", "BTCUSDT", "USDT", "btcturk"),
        ("cexio", "BTC/USD", "USD", "cexio"),
        ("cexio", "BTC/EUR", "EUR", "cexio"),
        ("cexio", "BTC/GBP", "GBP", "cexio"),
        ("cexio", "BTC/USDT", "USDT", "cexio"),
    ]
    return [
        VenuePair(exchange, symbol, quote, fetcher, DEFAULT_TAKER_BPS.get(exchange, Decimal("20")))
        for exchange, symbol, quote, fetcher in rows
    ]


def collect_books(pairs_to_fetch: list[VenuePair], workers: int) -> tuple[list[Book], list[dict[str, str]]]:
    books: list[Book] = []
    errors: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, len(pairs_to_fetch)))) as executor:
        future_to_pair = {executor.submit(fetch_book, pair): pair for pair in pairs_to_fetch}
        for future in concurrent.futures.as_completed(future_to_pair):
            pair = future_to_pair[future]
            try:
                book = future.result()
            except Exception as exc:
                errors.append({"exchange": pair.exchange, "symbol": pair.symbol, "error": str(exc)})
                continue
            if book is not None:
                books.append(book)
    return books, errors


def rank_routes(books: list[Book], min_top_net_bps: Decimal, max_gross_bps: Decimal, latency_bps: Decimal) -> list[tuple[Book, Book, Decimal, Decimal]]:
    candidates: list[tuple[Book, Book, Decimal, Decimal]] = []
    for buy in books:
        for sell in books:
            if buy.exchange == sell.exchange or buy.quote != sell.quote:
                continue
            if sell.best_bid <= buy.best_ask:
                continue
            gross_bps = (sell.best_bid - buy.best_ask) / buy.best_ask * Decimal("10000")
            top_net_bps = gross_bps - buy.taker_bps - sell.taker_bps - latency_bps
            if top_net_bps < min_top_net_bps or gross_bps > max_gross_bps:
                continue
            candidates.append((buy, sell, gross_bps, top_net_bps))
    return sorted(candidates, key=lambda row: row[3], reverse=True)


def evaluate_route(
    buy: Book,
    sell: Book,
    gross_top_bps: Decimal,
    top_net_bps: Decimal,
    notionals: list[Decimal],
    min_depth_net_bps: Decimal,
    latency_bps: Decimal,
) -> Opportunity | None:
    best: Opportunity | None = None
    bucket_results: list[dict[str, Any]] = []
    for notional in notionals:
        buy_fill = buy_with_quote(buy.asks, notional)
        if not buy_fill.full or buy_fill.avg_price is None:
            bucket_results.append({"notional": notional, "status": "buy_depth_insufficient"})
            continue
        sell_fill = sell_base(sell.bids, buy_fill.base)
        if not sell_fill.full or sell_fill.avg_price is None:
            bucket_results.append({"notional": notional, "status": "sell_depth_insufficient"})
            continue

        buy_fee_quote = buy_fill.quote * buy.taker_bps / Decimal("10000")
        sell_fee_quote = sell_fill.quote * sell.taker_bps / Decimal("10000")
        latency_haircut_quote = buy_fill.quote * latency_bps / Decimal("10000")
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
        if net_bps < min_depth_net_bps:
            continue
        opportunity = Opportunity(
            detected_at_ms=now_ms(),
            mode="btc_hot_path_inventory_based_public_books_no_transfer",
            base="BTC",
            quote=buy.quote,
            buy_exchange=buy.exchange,
            sell_exchange=sell.exchange,
            buy_symbol=buy.symbol,
            sell_symbol=sell.symbol,
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
            top_net_bps=top_net_bps,
            buy_levels=buy_fill.levels,
            sell_levels=sell_fill.levels,
            depth_proxy_quote=None,
            evidence_json=json.dumps(
                {
                    "bucket_results": bucket_results,
                    "top": {
                        "gross_top_bps": gross_top_bps,
                        "top_net_bps": top_net_bps,
                        "buy_best_ask": buy.best_ask,
                        "sell_best_bid": sell.best_bid,
                    },
                    "books": {
                        "buy": asdict(buy),
                        "sell": asdict(sell),
                    },
                },
                default=json_decimal_default,
                sort_keys=True,
            ),
        )
        if best is None or opportunity.net_profit_quote > best.net_profit_quote:
            best = opportunity
    return best


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
    row = asdict(opportunity)
    row["route_key"] = opportunity.route_key
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, default=json_decimal_default, sort_keys=True) + "\n")
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


def run_cycle(
    *,
    pairs_to_fetch: list[VenuePair],
    conn: sqlite3.Connection,
    jsonl_path: Path,
    status_conn: sqlite3.Connection | None,
    notionals_by_quote: dict[str, list[Decimal]],
    min_top_net_bps: Decimal,
    min_depth_net_bps: Decimal,
    max_gross_bps: Decimal,
    latency_bps: Decimal,
    max_candidates: int,
    workers: int,
    dedupe_window_sec: int,
    last_saved_by_route: dict[str, tuple[int, Decimal]],
) -> None:
    started = now_ms()
    books, errors = collect_books(pairs_to_fetch, workers)
    candidates = rank_routes(books, min_top_net_bps, max_gross_bps, latency_bps)
    checked = 0
    saved = 0
    for buy, sell, gross_top_bps, top_net_bps in candidates[:max_candidates]:
        checked += 1
        opportunity = evaluate_route(
            buy,
            sell,
            gross_top_bps,
            top_net_bps,
            notionals_by_quote.get(buy.quote, parse_decimal_csv("100,500,1000")),
            min_depth_net_bps,
            latency_bps,
        )
        if opportunity is None:
            continue
        previous = last_saved_by_route.get(opportunity.route_key)
        if previous:
            previous_ms, previous_net = previous
            inside_window = opportunity.detected_at_ms - previous_ms < dedupe_window_sec * 1000
            materially_better = opportunity.net_bps > previous_net + Decimal("5")
            if inside_window and not materially_better:
                continue
        opportunity = attach_operational_status(opportunity, status_conn)
        save_opportunity(conn, jsonl_path, opportunity)
        last_saved_by_route[opportunity.route_key] = (opportunity.detected_at_ms, opportunity.net_bps)
        saved += 1
        print(
            "[BTC_PROFIT] "
            f"{opportunity.route_key} notional={opportunity.notional_quote} "
            f"net={opportunity.net_profit_quote:.8f} {opportunity.quote} "
            f"net_bps={opportunity.net_bps:.3f} "
            f"grade={opportunity.operational_grade}",
            flush=True,
        )
    elapsed = now_ms() - started
    save_cycle(conn, started, elapsed, len(books), len(candidates), checked, saved, errors)
    print(
        "[BTC_CYCLE] "
        f"books={len(books)} candidates={len(candidates)} "
        f"checked={checked} saved={saved} errors={len(errors)} elapsed_ms={elapsed}",
        flush=True,
    )


def main() -> int:
    default_out = Path.home() / "Library/Application Support/hackathon-btc/btc_hot_path"
    parser = argparse.ArgumentParser(description="Fast public BTC order-book arbitrage monitor")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval-sec", type=float, default=float(os.getenv("BTC_HOT_INTERVAL_SEC", "5")))
    parser.add_argument("--out-dir", default=os.getenv("BTC_HOT_OUT_DIR", str(default_out)))
    parser.add_argument("--workers", type=int, default=int(os.getenv("BTC_HOT_WORKERS", "20")))
    parser.add_argument("--quotes", default=os.getenv("BTC_HOT_QUOTES", "USDT,USDC,USD,EUR,GBP,MXN,TRY"))
    parser.add_argument("--notionals", default=os.getenv("BTC_HOT_NOTIONALS", format_quote_notionals(DEFAULT_NOTIONALS_BY_QUOTE)))
    parser.add_argument("--min-top-net-bps", default=os.getenv("BTC_HOT_MIN_TOP_NET_BPS", "1"))
    parser.add_argument("--min-depth-net-bps", default=os.getenv("BTC_HOT_MIN_DEPTH_NET_BPS", "1"))
    parser.add_argument("--max-gross-bps", default=os.getenv("BTC_HOT_MAX_GROSS_BPS", "250"))
    parser.add_argument("--latency-bps", default=os.getenv("BTC_HOT_LATENCY_BPS", "2"))
    parser.add_argument("--max-candidates", type=int, default=int(os.getenv("BTC_HOT_MAX_CANDIDATES", "30")))
    parser.add_argument("--dedupe-window-sec", type=int, default=int(os.getenv("BTC_HOT_DEDUPE_WINDOW_SEC", "30")))
    parser.add_argument("--status-db", default=os.getenv("BTC_HOT_STATUS_DB", str(DEFAULT_STATUS_DB)))
    args = parser.parse_args()

    enabled_quotes = {quote.strip().upper() for quote in args.quotes.split(",") if quote.strip()}
    pairs_to_fetch = [pair for pair in default_pairs() if pair.quote in enabled_quotes]
    notionals_by_quote = parse_quote_notionals(args.notionals)
    out_dir = Path(args.out_dir).expanduser()
    conn = init_sqlite(out_dir / "profitable_cases.sqlite")
    status_conn = open_status_db(Path(args.status_db).expanduser())
    jsonl_path = out_dir / "profitable_cases.jsonl"
    last_saved_by_route: dict[str, tuple[int, Decimal]] = {}

    print("btc-hot-path public order-book scanner")
    print(f"mode=btc_hot_path_inventory_based_public_books_no_transfer pairs={len(pairs_to_fetch)}")
    print(f"quotes={','.join(sorted(enabled_quotes))} interval_sec={args.interval_sec} workers={args.workers}")
    print(f"outputs={jsonl_path} {out_dir / 'profitable_cases.sqlite'}")
    print(f"status_db={args.status_db} enabled={status_conn is not None}")
    print("risk=no private keys, no orders, transfer/deposit status is not proven by this monitor\n")

    while True:
        run_cycle(
            pairs_to_fetch=pairs_to_fetch,
            conn=conn,
            jsonl_path=jsonl_path,
            status_conn=status_conn,
            notionals_by_quote=notionals_by_quote,
            min_top_net_bps=Decimal(args.min_top_net_bps),
            min_depth_net_bps=Decimal(args.min_depth_net_bps),
            max_gross_bps=Decimal(args.max_gross_bps),
            latency_bps=Decimal(args.latency_bps),
            max_candidates=args.max_candidates,
            workers=args.workers,
            dedupe_window_sec=args.dedupe_window_sec,
            last_saved_by_route=last_saved_by_route,
        )
        if args.once:
            break
        time.sleep(args.interval_sec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
