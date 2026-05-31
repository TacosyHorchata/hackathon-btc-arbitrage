#!/usr/bin/env python3
"""Public operational status monitor for exchange symbols/assets.

This is a no-key companion to the profit monitors. It records public trading
status for spot symbols and public deposit/withdraw status when a venue exposes
it without authentication.
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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_EXCHANGES = {
    "backpack",
    "binance",
    "binanceus",
    "bingx",
    "bybit",
    "buda",
    "bullish",
    "okx",
    "gate",
    "kucoin",
    "hashkey",
    "hitbtc",
    "hyperliquid",
    "mexc",
    "ndax",
    "bitget",
    "bitbank",
    "bitfinex",
    "bitflyer",
    "bitmex",
    "bitvavo",
    "bithumb",
    "bitrue",
    "btcmarkets",
    "coinbase",
    "cryptocom",
    "digifinex",
    "foxbit",
    "bitstamp",
    "bitso",
    "coincheck",
    "coinex",
    "coinone",
    "cointr",
    "coinw",
    "coinsph",
    "deribit",
    "htx",
    "bitmart",
    "bitopro",
    "gmocoin",
    "kraken",
    "korbit",
    "latoken",
    "luno",
    "independentreserve",
    "gemini",
    "poloniex",
    "phemex",
    "toobit",
    "ascendex",
    "exmo",
    "btcturk",
    "cexio",
    "indodax",
    "bitkub",
    "mercadobitcoin",
    "novadax",
    "upbit",
    "valr",
    "whitebit",
    "xt",
}

DEFAULT_ASSET_FILTER = {
    "BTC",
    "BMEX",
    "ETH",
    "SOL",
    "USDT",
    "XAUT",
    "USDC",
    "TUSD",
    "USD",
    "USDS",
    "MXN",
    "COP",
    "CNYT",
    "CLP",
    "PEN",
    "ARS",
    "IDR",
    "JPY",
    "KRW",
    "ZAR",
    "THB",
    "MYR",
    "NGN",
    "UGX",
    "EUR",
    "BRL",
    "CAD",
    "UAH",
    "TRY",
    "PHP",
    "TWD",
    "USDE",
    "BNB",
    "BUIDL",
    "XRP",
    "DOGE",
    "LTC",
    "ADA",
    "AVAX",
    "LINK",
    "SUI",
    "XLM",
    "PAXG",
    "STETH",
    "USYC",
    "DEXE",
    "DCR",
    "MTL",
    "GUA",
    "ULTIMA",
    "ESPORTS",
    "BRETT",
    "CETUS",
    "STRK",
}

ASSET_FILTER: set[str] = set(DEFAULT_ASSET_FILTER)

BITFINEX_QUOTE_ALIASES = {
    "UST": "USDT",
}

BITFINEX_COMMON_QUOTES = {
    "BTC",
    "ETH",
    "USDT",
    "UST",
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "MXN",
    "XAUT",
    "CNHT",
    "EURQ",
    "EURR",
    "USDR",
    "USDQ",
}


@dataclass(frozen=True)
class SymbolStatus:
    exchange: str
    symbol: str
    base: str
    quote: str
    tradable: bool | None
    status: str
    min_base: str | None = None
    min_quote: str | None = None
    tick_size: str | None = None
    step_size: str | None = None
    raw_json: str = ""


@dataclass(frozen=True)
class AssetStatus:
    exchange: str
    asset: str
    network: str
    deposit_enabled: bool | None
    withdraw_enabled: bool | None
    status: str
    raw_json: str = ""


def now_ms() -> int:
    return int(time.time() * 1000)


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


def fetch_json(url: str, timeout: float = 20.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hackathon-btc-status-monitor/0.1",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict[str, Any], timeout: float = 20.0) -> Any:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "User-Agent": "hackathon-btc-status-monitor/0.1",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def raw(row: Any) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"))[:6000]


def split_symbol(symbol: str, sep: str | None, known_quotes: set[str]) -> tuple[str, str] | None:
    upper = symbol.upper()
    if sep and sep in upper:
        base, quote = upper.split(sep, 1)
        return (base, quote) if base and quote else None
    for quote in sorted(known_quotes, key=len, reverse=True):
        if upper.endswith(quote) and len(upper) > len(quote):
            return upper[: -len(quote)], quote
    return None


def split_bitfinex_pair(pair: str) -> tuple[str, str] | None:
    upper = pair.upper()
    if ":" in upper:
        base, quote = upper.split(":", 1)
        normalized_quote = BITFINEX_QUOTE_ALIASES.get(quote, quote)
        return (base, normalized_quote) if base and normalized_quote else None
    for quote in sorted(BITFINEX_COMMON_QUOTES, key=len, reverse=True):
        if upper.endswith(quote) and len(upper) > len(quote):
            return upper[: -len(quote)], BITFINEX_QUOTE_ALIASES.get(quote, quote)
    return None


def filter_value(rows: list[dict[str, Any]], filter_type: str, *keys: str) -> str | None:
    for row in rows:
        if row.get("filterType") != filter_type:
            continue
        for key in keys:
            value = row.get(key)
            if value is not None:
                return str(value)
    return None


def binance_like(name: str, base_url: str) -> tuple[list[SymbolStatus], list[AssetStatus]]:
    data = fetch_json(f"{base_url}/api/v3/exchangeInfo")
    symbols: list[SymbolStatus] = []
    for row in data.get("symbols", []):
        filters = row.get("filters", [])
        status = str(row.get("status", ""))
        symbols.append(
            SymbolStatus(
                exchange=name,
                symbol=str(row.get("symbol", "")).upper(),
                base=str(row.get("baseAsset", "")).upper(),
                quote=str(row.get("quoteAsset", "")).upper(),
                tradable=status == "TRADING" and bool(row.get("isSpotTradingAllowed", True)),
                status=status,
                min_base=filter_value(filters, "LOT_SIZE", "minQty"),
                min_quote=filter_value(filters, "MIN_NOTIONAL", "minNotional") or filter_value(filters, "NOTIONAL", "minNotional"),
                tick_size=filter_value(filters, "PRICE_FILTER", "tickSize"),
                step_size=filter_value(filters, "LOT_SIZE", "stepSize"),
                raw_json=raw(row),
            )
        )
    return symbols, []


def bybit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows: list[dict[str, Any]] = []
    cursor = ""
    while True:
        params = {"category": "spot", "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        data = fetch_json(f"https://api.bybit.com/v5/market/instruments-info?{urllib.parse.urlencode(params)}")
        result = data.get("result", {})
        rows.extend(result.get("list", []))
        cursor = result.get("nextPageCursor") or ""
        if not cursor:
            break
    symbols = [
        SymbolStatus(
            exchange="bybit",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCoin", "")).upper(),
            quote=str(row.get("quoteCoin", "")).upper(),
            tradable=row.get("status") == "Trading",
            status=str(row.get("status", "")),
            min_base=str(row.get("lotSizeFilter", {}).get("minOrderQty")) if row.get("lotSizeFilter") else None,
            min_quote=str(row.get("lotSizeFilter", {}).get("minOrderAmt")) if row.get("lotSizeFilter") else None,
            tick_size=str(row.get("priceFilter", {}).get("tickSize")) if row.get("priceFilter") else None,
            step_size=str(row.get("lotSizeFilter", {}).get("basePrecision")) if row.get("lotSizeFilter") else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def okx() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://www.okx.com/api/v5/public/instruments?instType=SPOT").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="okx",
            symbol=str(row.get("instId", "")).upper(),
            base=str(row.get("baseCcy", "")).upper(),
            quote=str(row.get("quoteCcy", "")).upper(),
            tradable=row.get("state") == "live",
            status=str(row.get("state", "")),
            min_base=str(row.get("minSz")) if row.get("minSz") is not None else None,
            tick_size=str(row.get("tickSz")) if row.get("tickSz") is not None else None,
            step_size=str(row.get("lotSz")) if row.get("lotSz") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def gate() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    pair_rows = fetch_json("https://api.gateio.ws/api/v4/spot/currency_pairs")
    symbols = [
        SymbolStatus(
            exchange="gate",
            symbol=str(row.get("id", "")).upper(),
            base=str(row.get("base", "")).upper(),
            quote=str(row.get("quote", "")).upper(),
            tradable=row.get("trade_status") == "tradable",
            status=str(row.get("trade_status", "")),
            min_base=str(row.get("min_base_amount")) if row.get("min_base_amount") is not None else None,
            min_quote=str(row.get("min_quote_amount")) if row.get("min_quote_amount") is not None else None,
            tick_size=str(row.get("precision")) if row.get("precision") is not None else None,
            step_size=str(row.get("amount_precision")) if row.get("amount_precision") is not None else None,
            raw_json=raw(row),
        )
        for row in pair_rows
    ]
    assets: list[AssetStatus] = []
    candidate_assets = {s.base for s in symbols} | {s.quote for s in symbols}
    if ASSET_FILTER:
        candidate_assets &= ASSET_FILTER
    timeout = env_float("STATUS_MONITOR_GATE_ASSET_TIMEOUT", 4.0)

    def fetch_asset(asset: str) -> list[AssetStatus]:
        asset_statuses: list[AssetStatus] = []
        try:
            chains = fetch_json(
                f"https://api.gateio.ws/api/v4/wallet/currency_chains?{urllib.parse.urlencode({'currency': asset})}",
                timeout=timeout,
            )
        except Exception:
            return []
        for chain in chains:
            disabled = chain.get("is_disabled") == 1
            deposit_disabled = chain.get("is_deposit_disabled") == 1
            withdraw_disabled = chain.get("is_withdraw_disabled") == 1
            asset_statuses.append(
                AssetStatus(
                    exchange="gate",
                    asset=asset,
                    network=str(chain.get("chain", "")),
                    deposit_enabled=not disabled and not deposit_disabled,
                    withdraw_enabled=not disabled and not withdraw_disabled,
                    status="enabled" if not disabled else "disabled",
                    raw_json=raw(chain),
                )
            )
        return asset_statuses

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, min(len(candidate_assets), env_int("STATUS_MONITOR_GATE_ASSET_WORKERS", 8)))
    ) as executor:
        for asset_statuses in executor.map(fetch_asset, sorted(candidate_assets)):
            assets.extend(asset_statuses)
    return symbols, assets


def kucoin() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.kucoin.com/api/v2/symbols").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="kucoin",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCurrency", "")).upper(),
            quote=str(row.get("quoteCurrency", "")).upper(),
            tradable=bool(row.get("enableTrading")),
            status="enabled" if row.get("enableTrading") else "disabled",
            min_base=str(row.get("baseMinSize")) if row.get("baseMinSize") is not None else None,
            min_quote=str(row.get("quoteMinSize") or row.get("minFunds")) if row.get("quoteMinSize") or row.get("minFunds") else None,
            tick_size=str(row.get("priceIncrement")) if row.get("priceIncrement") is not None else None,
            step_size=str(row.get("baseIncrement")) if row.get("baseIncrement") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    assets: list[AssetStatus] = []
    candidate_assets = {s.base for s in symbols} | {s.quote for s in symbols}
    if ASSET_FILTER:
        candidate_assets &= ASSET_FILTER
    for asset in sorted(candidate_assets):
        try:
            data = fetch_json(f"https://api.kucoin.com/api/v3/currencies/{urllib.parse.quote(asset)}").get("data", {})
        except Exception:
            continue
        for chain in data.get("chains", []) or []:
            assets.append(
                AssetStatus(
                    exchange="kucoin",
                    asset=asset,
                    network=str(chain.get("chainName") or chain.get("chainId") or ""),
                    deposit_enabled=chain.get("isDepositEnabled"),
                    withdraw_enabled=chain.get("isWithdrawEnabled"),
                    status="enabled" if chain.get("isDepositEnabled") or chain.get("isWithdrawEnabled") else "disabled",
                    raw_json=raw(chain),
                )
            )
    return symbols, assets


def mexc() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.mexc.com/api/v3/exchangeInfo").get("symbols", [])
    symbols = [
        SymbolStatus(
            exchange="mexc",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseAsset", "")).upper(),
            quote=str(row.get("quoteAsset", "")).upper(),
            tradable=str(row.get("status")) == "1" and bool(row.get("isSpotTradingAllowed", True)),
            status=str(row.get("status", "")),
            min_base=str(row.get("baseSizePrecision")) if row.get("baseSizePrecision") is not None else None,
            min_quote=str(row.get("quoteAmountPrecision")) if row.get("quoteAmountPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def bitget() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.bitget.com/api/v2/spot/public/symbols").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="bitget",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCoin", "")).upper(),
            quote=str(row.get("quoteCoin", "")).upper(),
            tradable=row.get("status") == "online",
            status=str(row.get("status", "")),
            min_base=str(row.get("minTradeAmount")) if row.get("minTradeAmount") is not None else None,
            min_quote=str(row.get("minTradeUSDT")) if row.get("minTradeUSDT") is not None else None,
            tick_size=str(row.get("pricePrecision")) if row.get("pricePrecision") is not None else None,
            step_size=str(row.get("quantityPrecision")) if row.get("quantityPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def cointr() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.cointr.pro/api/v2/spot/public/symbols").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="cointr",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCoin", "")).upper(),
            quote=str(row.get("quoteCoin", "")).upper(),
            tradable=str(row.get("status", "")).lower() == "online",
            status=str(row.get("status", "")),
            min_base=str(row.get("minTradeAmount")) if row.get("minTradeAmount") is not None else None,
            min_quote=str(row.get("minTradeUSDT")) if row.get("minTradeUSDT") is not None else None,
            tick_size=str(row.get("pricePrecision")) if row.get("pricePrecision") is not None else None,
            step_size=str(row.get("quantityPrecision")) if row.get("quantityPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def coinw() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    symbol_rows = fetch_json(
        f"https://api.coinw.com/api/v1/public?{urllib.parse.urlencode({'command': 'returnSymbol'})}"
    ).get("data", [])
    symbols = [
        SymbolStatus(
            exchange="coinw",
            symbol=str(row.get("currencyPair", "")).upper(),
            base=str(row.get("currencyBase", "")).upper(),
            quote=str(row.get("currencyQuote", "")).upper(),
            tradable=int(row.get("state") or 0) == 1,
            status=str(row.get("state", "")),
            min_base=str(row.get("minBuyCount")) if row.get("minBuyCount") is not None else None,
            min_quote=str(row.get("minBuyAmount")) if row.get("minBuyAmount") is not None else None,
            tick_size=str(row.get("pricePrecision")) if row.get("pricePrecision") is not None else None,
            step_size=str(row.get("countPrecision")) if row.get("countPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in symbol_rows
        if row.get("currencyPair")
    ]

    currency_rows = fetch_json(
        f"https://api.coinw.com/api/v1/public?{urllib.parse.urlencode({'command': 'returnCurrencies'})}"
    ).get("data", {})
    assets: list[AssetStatus] = []
    for row in currency_rows.values():
        asset = str(row.get("symbol", "")).upper()
        if asset not in ASSET_FILTER:
            continue
        assets.append(
            AssetStatus(
                exchange="coinw",
                asset=asset,
                network=str(row.get("chain", "")),
                deposit_enabled=str(row.get("recharge")) == "1",
                withdraw_enabled=str(row.get("withDraw")) == "1",
                status="listed",
                raw_json=raw(row),
            )
        )
    return symbols, assets


def deribit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    base_url = "https://www.deribit.com/api/v2/public"
    currency_rows = fetch_json(f"{base_url}/get_currencies").get("result", [])
    currencies = sorted({str(row.get("currency", "")).upper() for row in currency_rows if row.get("currency")})

    def fetch_currency(currency: str) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode({"currency": currency, "kind": "spot"})
        return fetch_json(f"{base_url}/get_instruments?{query}", timeout=8.0).get("result", [])

    deduped: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(len(currencies), 6))) as executor:
        for rows in executor.map(fetch_currency, currencies):
            for row in rows:
                symbol = str(row.get("instrument_name", "")).upper()
                if symbol:
                    deduped[symbol] = row

    symbols = [
        SymbolStatus(
            exchange="deribit",
            symbol=str(row.get("instrument_name", "")).upper(),
            base=str(row.get("base_currency", "")).upper(),
            quote=str(row.get("quote_currency", "")).upper(),
            tradable=str(row.get("state", "")).lower() == "open" and bool(row.get("is_active")),
            status=str(row.get("state", "")),
            min_base=str(row.get("min_trade_amount")) if row.get("min_trade_amount") is not None else None,
            tick_size=str(row.get("tick_size")) if row.get("tick_size") is not None else None,
            step_size=str(row.get("contract_size")) if row.get("contract_size") is not None else None,
            raw_json=raw(row),
        )
        for row in deduped.values()
    ]

    assets: list[AssetStatus] = []
    for row in currency_rows:
        asset = str(row.get("currency", "")).upper()
        if asset not in ASSET_FILTER:
            continue
        assets.append(
            AssetStatus(
                exchange="deribit",
                asset=asset,
                network=str(row.get("network_currency") or row.get("coin_type") or ""),
                deposit_enabled=None,
                withdraw_enabled=None,
                status=str(row.get("coin_type") or "listed"),
                raw_json=raw(row),
            )
        )
    return symbols, assets


def hitbtc() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    symbol_rows = fetch_json("https://api.hitbtc.com/api/3/public/symbol")
    symbols = [
        SymbolStatus(
            exchange="hitbtc",
            symbol=str(symbol).upper(),
            base=str(row.get("base_currency", "")).upper(),
            quote=str(row.get("quote_currency", "")).upper(),
            tradable=str(row.get("type", "")).lower() == "spot" and str(row.get("status", "")).lower() == "working",
            status=str(row.get("status", "")),
            min_base=str(row.get("quantity_increment")) if row.get("quantity_increment") is not None else None,
            tick_size=str(row.get("tick_size")) if row.get("tick_size") is not None else None,
            step_size=str(row.get("quantity_increment")) if row.get("quantity_increment") is not None else None,
            raw_json=raw(row),
        )
        for symbol, row in symbol_rows.items()
        if row.get("base_currency") and row.get("quote_currency")
    ]

    currency_rows = fetch_json("https://api.hitbtc.com/api/3/public/currency")
    assets: list[AssetStatus] = []
    for asset, row in currency_rows.items():
        asset = str(asset).upper()
        if asset not in ASSET_FILTER:
            continue
        networks = row.get("networks") or []
        if not networks:
            assets.append(
                AssetStatus(
                    exchange="hitbtc",
                    asset=asset,
                    network="",
                    deposit_enabled=bool(row.get("payin_enabled")),
                    withdraw_enabled=bool(row.get("payout_enabled")),
                    status="delisted" if bool(row.get("delisted")) else "listed",
                    raw_json=raw(row),
                )
            )
            continue
        for network in networks:
            assets.append(
                AssetStatus(
                    exchange="hitbtc",
                    asset=asset,
                    network=str(network.get("code") or network.get("network") or ""),
                    deposit_enabled=bool(network.get("payin_enabled")),
                    withdraw_enabled=bool(network.get("payout_enabled")),
                    status="delisted" if bool(row.get("delisted")) else "listed",
                    raw_json=raw({"currency": row, "network": network}),
                )
            )
    return symbols, assets


def bitmex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://www.bitmex.com/api/v1/instrument/active")
    symbols: list[SymbolStatus] = []
    for row in rows:
        if str(row.get("typ", "")) != "IFXXXP" or "_" not in str(row.get("symbol", "")):
            continue
        multiplier = float(row.get("underlyingToPositionMultiplier") or 0)
        lot_size = float(row.get("lotSize") or 0)
        min_base = str(lot_size / multiplier) if multiplier and lot_size else None
        symbols.append(
            SymbolStatus(
                exchange="bitmex",
                symbol=str(row.get("symbol", "")).upper(),
                base=normalize_bitmex_asset(row.get("underlying")),
                quote=normalize_bitmex_asset(row.get("quoteCurrency")),
                tradable=str(row.get("state", "")) == "Open" and bool(row.get("hasLiquidity")),
                status=str(row.get("state", "")),
                min_base=min_base,
                tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
                step_size=min_base,
                raw_json=raw(row),
            )
        )

    assets: list[AssetStatus] = []
    for row in fetch_json("https://www.bitmex.com/api/v1/wallet/assets"):
        asset = normalize_bitmex_asset(row.get("majorCurrency") or row.get("asset") or row.get("currency"))
        if asset not in ASSET_FILTER:
            continue
        networks = row.get("networks") or []
        if not networks:
            assets.append(
                AssetStatus(
                    exchange="bitmex",
                    asset=asset,
                    network="",
                    deposit_enabled=None,
                    withdraw_enabled=None,
                    status="enabled" if bool(row.get("enabled")) else "disabled",
                    raw_json=raw(row),
                )
            )
            continue
        for network in networks:
            assets.append(
                AssetStatus(
                    exchange="bitmex",
                    asset=asset,
                    network=str(network.get("asset", "")),
                    deposit_enabled=bool(network.get("depositEnabled")),
                    withdraw_enabled=bool(network.get("withdrawalEnabled")),
                    status="enabled" if bool(row.get("enabled")) else "disabled",
                    raw_json=raw({"asset": row, "network": network}),
                )
            )
    return symbols, assets


def coinsph() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.pro.coins.ph/openapi/v1/exchangeInfo").get("symbols", [])
    symbols = [
        SymbolStatus(
            exchange="coinsph",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseAsset", "")).upper(),
            quote=str(row.get("quoteAsset", "")).upper(),
            tradable=str(row.get("status", "")).lower() == "trading",
            status=str(row.get("status", "")),
            min_base=filter_value(row.get("filters", []), "LOT_SIZE", "minQty"),
            min_quote=filter_value(row.get("filters", []), "NOTIONAL", "minNotional")
            or filter_value(row.get("filters", []), "MIN_NOTIONAL", "minNotional"),
            tick_size=filter_value(row.get("filters", []), "PRICE_FILTER", "tickSize"),
            step_size=filter_value(row.get("filters", []), "LOT_SIZE", "stepSize"),
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def bitfinex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    detail_rows = fetch_json("https://api.bitfinex.com/v1/symbols_details")
    detail_by_pair = {str(row.get("pair", "")).upper(): row for row in detail_rows}
    pair_groups = fetch_json("https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange")
    pairs = pair_groups[0] if pair_groups and isinstance(pair_groups[0], list) else []
    symbols: list[SymbolStatus] = []
    for pair in pairs:
        split = split_bitfinex_pair(str(pair))
        if not split:
            continue
        base, quote = split
        detail = detail_by_pair.get(str(pair).replace(":", "").upper(), {})
        min_base = detail.get("minimum_order_size")
        symbols.append(
            SymbolStatus(
                exchange="bitfinex",
                symbol=f"t{str(pair).upper()}",
                base=base,
                quote=quote,
                tradable=True,
                status="listed",
                min_base=str(min_base) if min_base is not None else None,
                tick_size=str(detail.get("price_precision")) if detail.get("price_precision") is not None else None,
                raw_json=raw({"pair": pair, "details": detail}),
            )
        )
    return symbols, []


def coinbase() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.exchange.coinbase.com/products")
    symbols = [
        SymbolStatus(
            exchange="coinbase",
            symbol=str(row.get("id", "")).upper(),
            base=str(row.get("base_currency", "")).upper(),
            quote=str(row.get("quote_currency", "")).upper(),
            tradable=row.get("status") == "online" and not bool(row.get("trading_disabled")),
            status=str(row.get("status", "")),
            min_quote=str(row.get("min_market_funds")) if row.get("min_market_funds") is not None else None,
            tick_size=str(row.get("quote_increment")) if row.get("quote_increment") is not None else None,
            step_size=str(row.get("base_increment")) if row.get("base_increment") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def cryptocom() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.crypto.com/exchange/v1/public/get-instruments").get("result", {}).get("data", [])
    symbols = [
        SymbolStatus(
            exchange="cryptocom",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("base_ccy", "")).upper(),
            quote=str(row.get("quote_ccy", "")).upper(),
            tradable=bool(row.get("tradable")) if row.get("inst_type") == "CCY_PAIR" else False,
            status="tradable" if row.get("tradable") else "disabled",
            tick_size=str(row.get("price_tick_size")) if row.get("price_tick_size") is not None else None,
            step_size=str(row.get("qty_tick_size")) if row.get("qty_tick_size") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
        if row.get("inst_type") == "CCY_PAIR"
    ]
    return symbols, []


def bitstamp() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://www.bitstamp.net/api/v2/trading-pairs-info/")
    symbols = []
    for row in rows:
        split = split_symbol(str(row.get("name", "")), "/", set())
        if not split:
            continue
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="bitstamp",
                symbol=str(row.get("url_symbol", "")).lower(),
                base=base,
                quote=quote,
                tradable=row.get("trading") == "Enabled",
                status=str(row.get("trading", "")),
                min_quote=str(row.get("minimum_order")) if row.get("minimum_order") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def bitso() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.bitso.com/v3/available_books/").get("payload", [])
    symbols = []
    for row in rows:
        split = split_symbol(str(row.get("book", "")), "_", set())
        if not split:
            continue
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="bitso",
                symbol=str(row.get("book", "")).lower(),
                base=base,
                quote=quote,
                tradable=True,
                status="available",
                min_base=str(row.get("minimum_amount")) if row.get("minimum_amount") is not None else None,
                min_quote=str(row.get("minimum_value")) if row.get("minimum_value") is not None else None,
                tick_size=str(row.get("tick_size")) if row.get("tick_size") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def coinex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.coinex.com/v2/spot/market").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="coinex",
            symbol=str(row.get("market", "")).upper(),
            base=str(row.get("base_ccy", "")).upper(),
            quote=str(row.get("quote_ccy", "")).upper(),
            tradable=row.get("status") == "online" and bool(row.get("is_api_trading_available", True)),
            status=str(row.get("status", "")),
            min_base=str(row.get("min_amount")) if row.get("min_amount") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def htx() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.huobi.pro/v2/settings/common/symbols").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="htx",
            symbol=str(row.get("sc", "")).lower(),
            base=str(row.get("bc", "")).upper(),
            quote=str(row.get("qc", "")).upper(),
            tradable=row.get("state") == "online",
            status=str(row.get("state", "")),
            min_quote=str(row.get("minov")) if row.get("minov") is not None else None,
            tick_size=str(row.get("pp")) if row.get("pp") is not None else None,
            step_size=str(row.get("ap")) if row.get("ap") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def bitmart() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api-cloud.bitmart.com/spot/v1/symbols/details").get("data", {}).get("symbols", [])
    symbols = [
        SymbolStatus(
            exchange="bitmart",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("base_currency", "")).upper(),
            quote=str(row.get("quote_currency", "")).upper(),
            tradable=row.get("trade_status") == "trading",
            status=str(row.get("trade_status", "")),
            min_base=str(row.get("base_min_size")) if row.get("base_min_size") is not None else None,
            min_quote=str(row.get("min_buy_amount")) if row.get("min_buy_amount") is not None else None,
            tick_size=str(row.get("quote_increment")) if row.get("quote_increment") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def kraken() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.kraken.com/0/public/AssetPairs").get("result", {})
    symbols = []
    for row in rows.values():
        wsname = row.get("wsname") or ""
        split = split_symbol(wsname.replace("XBT", "BTC"), "/", set())
        if not split:
            continue
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="kraken",
                symbol=str(row.get("altname", "")).replace("XBT", "BTC").upper(),
                base=base,
                quote=quote,
                tradable=row.get("status") == "online",
                status=str(row.get("status", "")),
                min_base=str(row.get("ordermin")) if row.get("ordermin") is not None else None,
                min_quote=str(row.get("costmin")) if row.get("costmin") is not None else None,
                tick_size=str(row.get("tick_size")) if row.get("tick_size") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def gemini() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    quote_set = {
        "USD",
        "USDT",
        "USDC",
        "BTC",
        "ETH",
        "EUR",
        "GBP",
        "SGD",
        "DAI",
        "GUSD",
    }
    symbols: list[SymbolStatus] = []
    for symbol in fetch_json("https://api.gemini.com/v1/symbols"):
        split = split_symbol(str(symbol).upper(), None, quote_set)
        if not split:
            continue
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="gemini",
                symbol=str(symbol),
                base=base,
                quote=quote,
                tradable=True,
                status="listed",
                raw_json=raw({"symbol": symbol, "source": "/v1/symbols"}),
            )
        )
    return symbols, []


def poloniex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.poloniex.com/markets")
    symbols = []
    for row in rows:
        split = split_symbol(str(row.get("symbol", "")), "_", set())
        if not split:
            continue
        limit = row.get("symbolTradeLimit") or {}
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="poloniex",
                symbol=str(row.get("symbol", "")).upper(),
                base=base,
                quote=quote,
                tradable=row.get("state") == "NORMAL",
                status=str(row.get("state", "")),
                min_base=str(limit.get("minQuantity")) if limit.get("minQuantity") is not None else None,
                min_quote=str(limit.get("minAmount")) if limit.get("minAmount") is not None else None,
                tick_size=str(limit.get("priceScale")) if limit.get("priceScale") is not None else None,
                step_size=str(limit.get("quantityScale")) if limit.get("quantityScale") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def ascendex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    product_rows = fetch_json("https://ascendex.com/api/pro/v1/products").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="ascendex",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseAsset", "")).upper(),
            quote=str(row.get("quoteAsset", "")).upper(),
            tradable=row.get("status") == "Normal",
            status=str(row.get("status", "")),
            min_quote=str(row.get("minNotional")) if row.get("minNotional") is not None else None,
            tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
            step_size=str(row.get("lotSize")) if row.get("lotSize") is not None else None,
            raw_json=raw(row),
        )
        for row in product_rows
    ]

    assets: list[AssetStatus] = []
    asset_rows = fetch_json("https://ascendex.com/api/pro/v2/assets").get("data", [])
    candidate_assets = {row.base for row in symbols} | {row.quote for row in symbols}
    if ASSET_FILTER:
        candidate_assets &= ASSET_FILTER
    for row in asset_rows:
        asset = str(row.get("assetCode", "")).upper()
        if asset not in candidate_assets:
            continue
        for chain in row.get("blockChain", []) or []:
            assets.append(
                AssetStatus(
                    exchange="ascendex",
                    asset=asset,
                    network=str(chain.get("chainName", "")),
                    deposit_enabled=chain.get("allowDeposit"),
                    withdraw_enabled=chain.get("allowWithdraw"),
                    status="enabled" if chain.get("allowDeposit") or chain.get("allowWithdraw") else "disabled",
                    raw_json=raw(chain),
                )
            )
    return symbols, assets


def exmo() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.exmo.com/v1.1/pair_settings")
    symbols = []
    for symbol, row in rows.items():
        split = split_symbol(symbol, "_", set())
        if not split:
            continue
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="exmo",
                symbol=symbol.upper(),
                base=base,
                quote=quote,
                tradable=True,
                status="available",
                min_base=str(row.get("min_quantity")) if row.get("min_quantity") is not None else None,
                min_quote=str(row.get("min_amount")) if row.get("min_amount") is not None else None,
                tick_size=str(row.get("price_precision")) if row.get("price_precision") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def btcturk() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.btcturk.com/api/v2/server/exchangeinfo").get("data", {}).get("symbols", [])
    symbols = [
        SymbolStatus(
            exchange="btcturk",
            symbol=str(row.get("name", "")).upper(),
            base=str(row.get("numerator", "")).upper(),
            quote=str(row.get("denominator", "")).upper(),
            tradable=row.get("status") == "TRADING",
            status=str(row.get("status", "")),
            min_quote=str((row.get("filters") or [{}])[0].get("minExchangeValue")) if row.get("filters") else None,
            tick_size=str((row.get("filters") or [{}])[0].get("tickSize")) if row.get("filters") else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def cexio() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://cex.io/api/currency_limits").get("data", {}).get("pairs", [])
    symbols = [
        SymbolStatus(
            exchange="cexio",
            symbol=f"{str(row.get('symbol1', '')).upper()}/{str(row.get('symbol2', '')).upper()}",
            base=str(row.get("symbol1", "")).upper(),
            quote=str(row.get("symbol2", "")).upper(),
            tradable=True,
            status="available",
            min_base=str(row.get("minLotSize")) if row.get("minLotSize") is not None else None,
            min_quote=str(row.get("minLotSizeS2")) if row.get("minLotSizeS2") is not None else None,
            tick_size=str(row.get("pricePrecision")) if row.get("pricePrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def whitebit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://whitebit.com/api/v4/public/markets")
    symbols = [
        SymbolStatus(
            exchange="whitebit",
            symbol=str(row.get("name", "")).upper(),
            base=str(row.get("stock", "")).upper(),
            quote=str(row.get("money", "")).upper(),
            tradable=row.get("type") == "spot" and bool(row.get("tradesEnabled")),
            status="trading" if row.get("tradesEnabled") else "disabled",
            min_base=str(row.get("minAmount")) if row.get("minAmount") is not None else None,
            min_quote=str(row.get("minTotal")) if row.get("minTotal") is not None else None,
            tick_size=str(row.get("moneyPrec")) if row.get("moneyPrec") is not None else None,
            step_size=str(row.get("stockPrec")) if row.get("stockPrec") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
        if row.get("type") == "spot"
    ]
    return symbols, []


def upbit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.upbit.com/v1/market/all?isDetails=true")
    symbols: list[SymbolStatus] = []
    for row in rows:
        market_id = str(row.get("market", "")).upper()
        if "-" not in market_id:
            continue
        quote, base = market_id.split("-", 1)
        event = row.get("market_event") or {}
        warning = bool(event.get("warning"))
        symbols.append(
            SymbolStatus(
                exchange="upbit",
                symbol=market_id,
                base=base,
                quote=quote,
                tradable=not warning,
                status="warning" if warning else "listed",
                raw_json=raw(row),
            )
        )
    return symbols, []


def indodax() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://indodax.com/api/pairs")
    symbols: list[SymbolStatus] = []
    assets: list[AssetStatus] = []
    for row in rows:
        base = str(row.get("traded_currency_unit") or row.get("traded_currency", "")).upper()
        quote = str(row.get("base_currency", "")).upper()
        maintenance = int(row.get("is_maintenance") or 0) != 0
        suspended = int(row.get("is_market_suspended") or 0) != 0
        symbols.append(
            SymbolStatus(
                exchange="indodax",
                symbol=str(row.get("id", "")).lower(),
                base=base,
                quote=quote,
                tradable=not maintenance and not suspended,
                status="maintenance" if maintenance else ("suspended" if suspended else "trading"),
                min_base=str(row.get("trade_min_traded_currency")) if row.get("trade_min_traded_currency") is not None else None,
                min_quote=str(row.get("trade_min_base_currency")) if row.get("trade_min_base_currency") is not None else None,
                tick_size=str(row.get("pricescale")) if row.get("pricescale") is not None else None,
                raw_json=raw(row),
            )
        )
        if not ASSET_FILTER or base in ASSET_FILTER:
            deposit_disabled = bool(row.get("disable_deposit"))
            assets.append(
                AssetStatus(
                    exchange="indodax",
                    asset=base,
                    network="",
                    deposit_enabled=not deposit_disabled,
                    withdraw_enabled=None,
                    status="deposit_disabled" if deposit_disabled else "deposit_enabled",
                    raw_json=raw(row),
                )
            )
    return symbols, assets


def buda() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://www.buda.com/api/v2/markets").get("markets", [])
    symbols = [
        SymbolStatus(
            exchange="buda",
            symbol=str(row.get("name") or row.get("id", "")).lower(),
            base=str(row.get("base_currency", "")).upper(),
            quote=str(row.get("quote_currency", "")).upper(),
            tradable=not bool(row.get("disabled")),
            status="disabled" if row.get("disabled") else ("illiquid" if row.get("illiquid") else "trading"),
            min_base=str((row.get("minimum_order_amount") or [None])[0]) if row.get("minimum_order_amount") else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def novadax() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.novadax.com/v1/common/symbols").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="novadax",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCurrency", "")).upper(),
            quote=str(row.get("quoteCurrency", "")).upper(),
            tradable=str(row.get("status", "")).upper() == "ONLINE",
            status=str(row.get("status", "")),
            min_base=str(row.get("minOrderAmount")) if row.get("minOrderAmount") is not None else None,
            min_quote=str(row.get("minOrderValue")) if row.get("minOrderValue") is not None else None,
            tick_size=str(row.get("pricePrecision")) if row.get("pricePrecision") is not None else None,
            step_size=str(row.get("amountPrecision")) if row.get("amountPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def foxbit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.foxbit.com.br/rest/v3/markets").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="foxbit",
            symbol=str(row.get("symbol", "")).lower(),
            base=str((row.get("base") or {}).get("symbol", "")).upper(),
            quote=str((row.get("quote") or {}).get("symbol", "")).upper(),
            tradable="MARKET" in (row.get("order_type") or []),
            status="listed",
            min_base=str(row.get("quantity_min")) if row.get("quantity_min") is not None else None,
            tick_size=str(row.get("price_increment")) if row.get("price_increment") is not None else None,
            step_size=str(row.get("quantity_increment")) if row.get("quantity_increment") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def mercadobitcoin() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    data = fetch_json("https://api.mercadobitcoin.net/api/v4/symbols")
    rows = data.get("symbol", [])
    symbols: list[SymbolStatus] = []
    for index, symbol_value in enumerate(rows):
        listed = column_bool(data, "exchange-listed", index)
        traded = column_bool(data, "exchange-traded", index)
        symbols.append(
            SymbolStatus(
                exchange="mercadobitcoin",
                symbol=str(symbol_value).upper(),
                base=column(data, "base-currency", index).upper(),
                quote=column(data, "currency", index).upper(),
                tradable=listed and traded,
                status="trading" if listed and traded else "disabled",
                min_base=column(data, "min-volume", index) or None,
                min_quote=column(data, "min-cost", index) or None,
                tick_size=column(data, "minmovement", index) or None,
                step_size=column(data, "round-lot", index) or None,
                raw_json=raw({key: value[index] for key, value in data.items() if isinstance(value, list) and index < len(value)}),
            )
        )
    return symbols, []


def bitvavo() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.bitvavo.com/v2/markets")
    symbols = [
        SymbolStatus(
            exchange="bitvavo",
            symbol=str(row.get("market", "")).upper(),
            base=str(row.get("base", "")).upper(),
            quote=str(row.get("quote", "")).upper(),
            tradable=str(row.get("status", "")).lower() == "trading",
            status=str(row.get("status", "")),
            min_base=str(row.get("minOrderInBaseAsset")) if row.get("minOrderInBaseAsset") is not None else None,
            min_quote=str(row.get("minOrderInQuoteAsset")) if row.get("minOrderInQuoteAsset") is not None else None,
            tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
            step_size=str(row.get("quantityDecimals")) if row.get("quantityDecimals") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def luno() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.luno.com/api/exchange/1/markets").get("markets", [])
    symbols = [
        SymbolStatus(
            exchange="luno",
            symbol=str(row.get("market_id", "")).upper(),
            base=normalize_luno_asset(row.get("base_currency")),
            quote=normalize_luno_asset(row.get("counter_currency")),
            tradable=str(row.get("trading_status", "")).upper() == "ACTIVE",
            status=str(row.get("trading_status", "")),
            min_base=str(row.get("min_volume")) if row.get("min_volume") is not None else None,
            tick_size=str(row.get("min_price")) if row.get("min_price") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def bitkub() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    symbol_rows = fetch_json("https://api.bitkub.com/api/market/symbols").get("result", [])
    tickers = fetch_json("https://api.bitkub.com/api/market/ticker")
    symbols: list[SymbolStatus] = []
    for row in symbol_rows:
        symbol = str(row.get("symbol", "")).upper()
        if "_" not in symbol:
            continue
        quote, base = symbol.split("_", 1)
        ticker = tickers.get(symbol, {}) if isinstance(tickers, dict) else {}
        frozen = int(ticker.get("isFrozen") or 0) != 0 if ticker else None
        symbols.append(
            SymbolStatus(
                exchange="bitkub",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=None if frozen is None else not frozen,
                status="frozen" if frozen else "trading",
                raw_json=raw({**row, "ticker": ticker}),
            )
        )
    return symbols, []


def valr() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    pair_rows = fetch_json("https://api.valr.com/v1/public/pairs")
    currency_rows = fetch_json("https://api.valr.com/v1/public/currencies")
    symbols = [
        SymbolStatus(
            exchange="valr",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCurrency", "")).upper(),
            quote=str(row.get("quoteCurrency", "")).upper(),
            tradable=bool(row.get("active")) and str(row.get("currencyPairType", "")).upper() == "SPOT",
            status="active" if bool(row.get("active")) else "disabled",
            min_base=str(row.get("minBaseAmount")) if row.get("minBaseAmount") is not None else None,
            min_quote=str(row.get("minQuoteAmount")) if row.get("minQuoteAmount") is not None else None,
            tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
            step_size=str(row.get("baseDecimalPlaces")) if row.get("baseDecimalPlaces") is not None else None,
            raw_json=raw(row),
        )
        for row in pair_rows
        if str(row.get("currencyPairType", "")).upper() == "SPOT"
    ]
    assets: list[AssetStatus] = []
    for row in currency_rows:
        asset = str(row.get("shortName") or row.get("symbol") or "").upper()
        if asset not in ASSET_FILTER:
            continue
        networks = row.get("supportedNetworks") or []
        if not networks:
            assets.append(
                AssetStatus(
                    exchange="valr",
                    asset=asset,
                    network="default",
                    deposit_enabled=None,
                    withdraw_enabled=None,
                    status="active" if bool(row.get("isActive")) else "disabled",
                    raw_json=raw(row),
                )
            )
            continue
        for network in networks:
            assets.append(
                AssetStatus(
                    exchange="valr",
                    asset=asset,
                    network=str(network.get("networkType", "default")),
                    deposit_enabled=bool(network.get("deposit")),
                    withdraw_enabled=bool(network.get("withdraw")),
                    status="active" if bool(row.get("isActive")) else "disabled",
                    raw_json=raw({**row, "network": network}),
                )
            )
    return symbols, assets


def bitflyer() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.bitflyer.com/v1/markets")
    symbols: list[SymbolStatus] = []
    for row in rows:
        symbol = str(row.get("product_code", "")).upper()
        if str(row.get("market_type", "")).lower() != "spot" or "_" not in symbol:
            continue
        base, quote = symbol.split("_", 1)
        symbols.append(
            SymbolStatus(
                exchange="bitflyer",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=True,
                status=str(row.get("market_type", "")),
                raw_json=raw(row),
            )
        )
    return symbols, []


def bithumb() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    data = fetch_json("https://api.bithumb.com/public/ticker/ALL_KRW").get("data", {})
    symbols: list[SymbolStatus] = []
    for base, row in data.items():
        if base == "date" or not isinstance(row, dict):
            continue
        symbols.append(
            SymbolStatus(
                exchange="bithumb",
                symbol=f"{str(base).upper()}_KRW",
                base=str(base).upper(),
                quote="KRW",
                tradable=True,
                status="trading",
                raw_json=raw(row),
            )
        )
    return symbols, []


def bitbank() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://public.bitbank.cc/tickers").get("data", [])
    symbols: list[SymbolStatus] = []
    for row in rows:
        symbol = str(row.get("pair", "")).lower()
        if "_" not in symbol:
            continue
        base, quote = [part.upper() for part in symbol.split("_", 1)]
        symbols.append(
            SymbolStatus(
                exchange="bitbank",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=True,
                status="trading",
                raw_json=raw(row),
            )
        )
    return symbols, []


COINCHECK_CANDIDATE_PAIRS = [
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


def coincheck() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    def fetch_pair(pair: str) -> SymbolStatus | None:
        try:
            row = fetch_json(f"https://coincheck.com/api/ticker?{urllib.parse.urlencode({'pair': pair})}", timeout=8)
        except Exception:
            return None
        base, quote = pair.upper().split("_", 1)
        return SymbolStatus(
            exchange="coincheck",
            symbol=pair.lower(),
            base=base,
            quote=quote,
            tradable=True,
            status="trading",
            raw_json=raw(row),
        )

    symbols: list[SymbolStatus] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for result in executor.map(fetch_pair, COINCHECK_CANDIDATE_PAIRS):
            if result:
                symbols.append(result)
    return symbols, []


def bitrue() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://openapi.bitrue.com/api/v1/exchangeInfo").get("symbols", [])
    symbols = [
        SymbolStatus(
            exchange="bitrue",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseAsset", "")).upper(),
            quote=str(row.get("quoteAsset", "")).upper(),
            tradable=str(row.get("status", "")).upper() == "TRADING",
            status=str(row.get("status", "")),
            min_base=filter_value(row.get("filters", []), "LOT_SIZE", "minQty"),
            min_quote=filter_value(row.get("filters", []), "LOT_SIZE", "minVal"),
            tick_size=filter_value(row.get("filters", []), "PRICE_FILTER", "tickSize"),
            step_size=filter_value(row.get("filters", []), "LOT_SIZE", "stepSize"),
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def coinone() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.coinone.co.kr/public/v2/markets/KRW").get("markets", [])
    symbols = [
        SymbolStatus(
            exchange="coinone",
            symbol=f"{str(row.get('target_currency', '')).upper()}_KRW",
            base=str(row.get("target_currency", "")).upper(),
            quote=str(row.get("quote_currency", "")).upper(),
            tradable=int(row.get("maintenance_status") or 0) == 0 and int(row.get("trade_status") or 0) == 1,
            status="trading" if int(row.get("trade_status") or 0) == 1 else "disabled",
            min_base=str(row.get("min_qty")) if row.get("min_qty") is not None else None,
            min_quote=str(row.get("min_order_amount")) if row.get("min_order_amount") is not None else None,
            tick_size=str(row.get("price_unit")) if row.get("price_unit") is not None else None,
            step_size=str(row.get("qty_unit")) if row.get("qty_unit") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def korbit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.korbit.co.kr/v2/currencyPairs").get("data", [])
    symbols: list[SymbolStatus] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).lower()
        if "_" not in symbol:
            continue
        base, quote = [part.upper() for part in symbol.split("_", 1)]
        status = str(row.get("status", ""))
        symbols.append(
            SymbolStatus(
                exchange="korbit",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=status.lower() == "launched",
                status=status,
                raw_json=raw(row),
            )
        )
    return symbols, []


def gmocoin() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    exchange_status = str(fetch_json("https://api.coin.z.com/public/v1/status").get("data", {}).get("status", ""))
    rows = fetch_json("https://api.coin.z.com/public/v1/symbols").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="gmocoin",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("symbol", "")).upper(),
            quote="JPY",
            tradable=exchange_status.upper() == "OPEN",
            status=exchange_status,
            min_base=str(row.get("minOrderSize")) if row.get("minOrderSize") is not None else None,
            tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
            step_size=str(row.get("sizeStep")) if row.get("sizeStep") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def independentreserve() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    primary_rows = fetch_json("https://api.independentreserve.com/Public/GetValidPrimaryCurrencyCodes")
    secondary_rows = fetch_json("https://api.independentreserve.com/Public/GetValidSecondaryCurrencyCodes")
    combos = [(str(primary), str(secondary)) for primary in primary_rows for secondary in secondary_rows]
    timeout = env_float("STATUS_MONITOR_INDEPENDENTRESERVE_TIMEOUT", 4.0)

    def fetch_symbol(combo: tuple[str, str]) -> SymbolStatus | None:
        primary, secondary = combo
        query = urllib.parse.urlencode({"primaryCurrencyCode": primary.lower(), "secondaryCurrencyCode": secondary.lower()})
        try:
            row = fetch_json(f"https://api.independentreserve.com/Public/GetMarketSummary?{query}", timeout=timeout)
        except Exception:
            return None
        return SymbolStatus(
            exchange="independentreserve",
            symbol=f"{normalize_luno_asset(primary)}-{str(secondary).upper()}",
            base=normalize_luno_asset(primary),
            quote=str(secondary).upper(),
            tradable=True,
            status="trading",
            raw_json=raw(row),
        )

    symbols: list[SymbolStatus] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(len(combos), env_int("STATUS_MONITOR_INDEPENDENTRESERVE_WORKERS", 16)))) as executor:
        for result in executor.map(fetch_symbol, combos):
            if result:
                symbols.append(result)
    return symbols, []


def btcmarkets() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.btcmarkets.net/v3/markets")
    symbols = [
        SymbolStatus(
            exchange="btcmarkets",
            symbol=str(row.get("marketId", "")).upper(),
            base=str(row.get("baseAssetName", "")).upper(),
            quote=str(row.get("quoteAssetName", "")).upper(),
            tradable=str(row.get("status", "")).lower() == "online",
            status=str(row.get("status", "")),
            min_base=str(row.get("minOrderAmount")) if row.get("minOrderAmount") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
    ]
    return symbols, []


def ndax() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    instrument_rows = post_json("https://api.ndax.io:8443/AP/GetInstruments", {"OMSId": 1})
    product_rows = post_json("https://api.ndax.io:8443/AP/GetProducts", {"OMSId": 1})
    symbols = [
        SymbolStatus(
            exchange="ndax",
            symbol=str(row.get("Symbol", "")).upper(),
            base=str(row.get("Product1Symbol", "")).upper(),
            quote=str(row.get("Product2Symbol", "")).upper(),
            tradable=str(row.get("SessionStatus", "")).lower() == "running" and not bool(row.get("IsDisable")),
            status=str(row.get("SessionStatus", "")),
            min_base=str(row.get("MinimumQuantity")) if row.get("MinimumQuantity") is not None else None,
            tick_size=str(row.get("PriceIncrement")) if row.get("PriceIncrement") is not None else None,
            step_size=str(row.get("QuantityIncrement")) if row.get("QuantityIncrement") is not None else None,
            raw_json=raw(row),
        )
        for row in instrument_rows
        if str(row.get("InstrumentType", "")).lower() == "standard"
    ]
    assets = [
        AssetStatus(
            exchange="ndax",
            asset=str(row.get("Product", "")).upper(),
            network="default",
            deposit_enabled=bool(row.get("DepositEnabled")),
            withdraw_enabled=bool(row.get("WithdrawEnabled")),
            status="enabled" if not bool(row.get("IsDisabled")) else "disabled",
            raw_json=raw(row),
        )
        for row in product_rows
        if str(row.get("Product", "")).upper() in ASSET_FILTER
    ]
    return symbols, assets


def bitopro() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.bitopro.com/v3/provisioning/trading-pairs").get("data", [])
    symbols = [
        SymbolStatus(
            exchange="bitopro",
            symbol=str(row.get("pair", "")).lower(),
            base=str(row.get("base", "")).upper(),
            quote=str(row.get("quote", "")).upper(),
            tradable=not bool(row.get("maintain")),
            status="trading" if not bool(row.get("maintain")) else "maintenance",
            min_base=str(row.get("minLimitBaseAmount")) if row.get("minLimitBaseAmount") is not None else None,
            min_quote=str(row.get("minMarketBuyQuoteAmount")) if row.get("minMarketBuyQuoteAmount") is not None else None,
            tick_size=str(row.get("orderBookQuotePrecision")) if row.get("orderBookQuotePrecision") is not None else None,
            step_size=str(row.get("amountPrecision")) if row.get("amountPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
        if row.get("pair")
    ]
    return symbols, []


def digifinex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    symbol_rows = fetch_json("https://openapi.digifinex.com/v3/spot/symbols").get("symbol_list", [])
    symbols = [
        SymbolStatus(
            exchange="digifinex",
            symbol=str(row.get("symbol", "")).lower(),
            base=str(row.get("base_asset", "")).upper(),
            quote=str(row.get("quote_asset", "")).upper(),
            tradable=str(row.get("status", "")).upper() == "TRADING",
            status=str(row.get("status", "")),
            min_base=str(row.get("minimum_amount")) if row.get("minimum_amount") is not None else None,
            min_quote=str(row.get("minimum_value")) if row.get("minimum_value") is not None else None,
            tick_size=str(row.get("price_precision")) if row.get("price_precision") is not None else None,
            step_size=str(row.get("amount_precision")) if row.get("amount_precision") is not None else None,
            raw_json=raw(row),
        )
        for row in symbol_rows
        if row.get("symbol")
    ]

    asset_rows = fetch_json("https://openapi.digifinex.com/v3/currencies").get("data", [])
    assets = [
        AssetStatus(
            exchange="digifinex",
            asset=str(row.get("currency", "")).upper(),
            network=str(row.get("chain") or "default").upper(),
            deposit_enabled=int(row.get("deposit_status") or 0) == 1,
            withdraw_enabled=int(row.get("withdraw_status") or 0) == 1,
            status=f"deposit={row.get('deposit_status')} withdraw={row.get('withdraw_status')}",
            raw_json=raw(row),
        )
        for row in asset_rows
        if str(row.get("currency", "")).upper() in ASSET_FILTER
    ]
    return symbols, assets


def toobit() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.toobit.com/api/v1/exchangeInfo", timeout=25.0).get("symbols", [])
    symbols: list[SymbolStatus] = []
    for row in rows:
        filters = row.get("filters", [])
        symbols.append(
            SymbolStatus(
                exchange="toobit",
                symbol=str(row.get("symbol", "")).upper(),
                base=str(row.get("baseAsset", "")).upper(),
                quote=str(row.get("quoteAsset", "")).upper(),
                tradable=str(row.get("status", "")).upper() == "TRADING",
                status=str(row.get("status", "")),
                min_base=filter_value(filters, "LOT_SIZE", "minQty"),
                min_quote=filter_value(filters, "MIN_NOTIONAL", "minNotional")
                or filter_value(filters, "TRADE_AMOUNT", "minAmount"),
                tick_size=filter_value(filters, "PRICE_FILTER", "tickSize"),
                step_size=filter_value(filters, "LOT_SIZE", "stepSize"),
                raw_json=raw(row),
            )
        )
    return symbols, []


def latoken() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    currency_rows = fetch_json("https://api.latoken.com/v2/currency")
    currency_by_id = {
        str(row.get("id", "")): str(row.get("tag", "")).upper()
        for row in currency_rows
        if row.get("id") and row.get("tag")
    }
    rows = fetch_json("https://api.latoken.com/v2/pair")
    symbols: list[SymbolStatus] = []
    for row in rows:
        base = currency_by_id.get(str(row.get("baseCurrency", "")), "")
        quote = currency_by_id.get(str(row.get("quoteCurrency", "")), "")
        if not base or not quote:
            continue
        status = str(row.get("status", ""))
        symbols.append(
            SymbolStatus(
                exchange="latoken",
                symbol=f"{base}/{quote}",
                base=base,
                quote=quote,
                tradable=status.upper() == "PAIR_STATUS_ACTIVE",
                status=status,
                min_base=str(row.get("minOrderQuantity")) if row.get("minOrderQuantity") is not None else None,
                min_quote=str(row.get("minOrderCostUsd")) if row.get("minOrderCostUsd") is not None else None,
                tick_size=str(row.get("priceTick")) if row.get("priceTick") is not None else None,
                step_size=str(row.get("quantityTick")) if row.get("quantityTick") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def pionex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.pionex.com/api/v1/common/symbols").get("data", {}).get("symbols", [])
    symbols = [
        SymbolStatus(
            exchange="pionex",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCurrency", "")).upper(),
            quote=str(row.get("quoteCurrency", "")).upper(),
            tradable=str(row.get("type", "")).upper() == "SPOT" and bool(row.get("enable")),
            status="enabled" if bool(row.get("enable")) else "disabled",
            min_base=str(row.get("minTradeSize")) if row.get("minTradeSize") is not None else None,
            min_quote=str(row.get("minAmount")) if row.get("minAmount") is not None else None,
            tick_size=str(row.get("quotePrecision")) if row.get("quotePrecision") is not None else None,
            step_size=str(row.get("basePrecision")) if row.get("basePrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
        if str(row.get("type", "")).upper() == "SPOT" and row.get("symbol")
    ]
    return symbols, []


def hyperliquid() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    meta, _contexts = post_json("https://api.hyperliquid.xyz/info", {"type": "spotMetaAndAssetCtxs"})
    tokens = {
        int(row.get("index")): str(row.get("name", "")).upper()
        for row in meta.get("tokens", [])
        if row.get("index") is not None and row.get("name")
    }
    symbols: list[SymbolStatus] = []
    for row in meta.get("universe", []):
        token_indexes = row.get("tokens", [])
        if not isinstance(token_indexes, list) or len(token_indexes) != 2:
            continue
        base = tokens.get(int(token_indexes[0]), "")
        quote = tokens.get(int(token_indexes[1]), "")
        symbol = str(row.get("name", ""))
        if not base or not quote or not symbol:
            continue
        symbols.append(
            SymbolStatus(
                exchange="hyperliquid",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=True,
                status="listed",
                raw_json=raw(row),
            )
        )
    return symbols, []


def xt() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://sapi.xt.com/v4/public/symbol").get("result", {}).get("symbols", [])
    symbols: list[SymbolStatus] = []
    for row in rows:
        symbols.append(
            SymbolStatus(
                exchange="xt",
                symbol=str(row.get("symbol", "")).lower(),
                base=str(row.get("baseCurrency", "")).upper(),
                quote=str(row.get("quoteCurrency", "")).upper(),
                tradable=str(row.get("state", "")).upper() == "ONLINE"
                and bool(row.get("tradingEnabled"))
                and bool(row.get("openapiEnabled")),
                status=str(row.get("state", "")),
                min_quote=filter_value(row.get("filters", []), "QUOTE_QTY", "min"),
                tick_size=str(row.get("pricePrecision")) if row.get("pricePrecision") is not None else None,
                step_size=str(row.get("quantityPrecision")) if row.get("quantityPrecision") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def hashkey() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api-glb.hashkey.com/api/v1/exchangeInfo").get("symbols", [])
    symbols: list[SymbolStatus] = []
    for row in rows:
        filters = row.get("filters", [])
        symbols.append(
            SymbolStatus(
                exchange="hashkey",
                symbol=str(row.get("symbol", "")).upper(),
                base=str(row.get("baseAsset", "")).upper(),
                quote=str(row.get("quoteAsset", "")).upper(),
                tradable=str(row.get("status", "")).upper() == "TRADING"
                and str(row.get("tradeStatus", "")).upper() == "TRADABLE",
                status=str(row.get("tradeStatus") or row.get("status") or ""),
                min_base=filter_value(filters, "LOT_SIZE", "minQty"),
                min_quote=filter_value(filters, "MIN_NOTIONAL", "minNotional")
                or filter_value(filters, "TRADE_AMOUNT", "minAmount"),
                tick_size=filter_value(filters, "PRICE_FILTER", "tickSize"),
                step_size=filter_value(filters, "LOT_SIZE", "stepSize"),
                raw_json=raw(row),
            )
        )
    return symbols, []


def bingx() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://open-api.bingx.com/openApi/spot/v1/common/symbols").get("data", {}).get("symbols", [])
    symbols: list[SymbolStatus] = []
    known_quotes = DEFAULT_ASSET_FILTER | {"USDT", "USDC", "BTC", "ETH", "BNB"}
    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        split = split_symbol(symbol, "-", known_quotes)
        if not split:
            continue
        base, quote = split
        symbols.append(
            SymbolStatus(
                exchange="bingx",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=int(row.get("status") or 0) == 1 and bool(row.get("apiStateBuy")) and bool(row.get("apiStateSell")),
                status=str(row.get("status", "")),
                min_base=str(row.get("minQty")) if row.get("minQty") is not None else None,
                min_quote=str(row.get("minNotional")) if row.get("minNotional") is not None else None,
                tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
                step_size=str(row.get("stepSize")) if row.get("stepSize") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def backpack() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.backpack.exchange/api/v1/markets")
    symbols = [
        SymbolStatus(
            exchange="backpack",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseSymbol", "")).upper(),
            quote=str(row.get("quoteSymbol", "")).upper(),
            tradable=str(row.get("marketType", "")).upper() == "SPOT"
            and str(row.get("orderBookState", "")).lower() == "open"
            and bool(row.get("visible", True)),
            status=str(row.get("orderBookState", "")),
            min_base=str(((row.get("filters") or {}).get("quantity") or {}).get("minQuantity"))
            if ((row.get("filters") or {}).get("quantity") or {}).get("minQuantity") is not None else None,
            tick_size=str(((row.get("filters") or {}).get("price") or {}).get("tickSize"))
            if ((row.get("filters") or {}).get("price") or {}).get("tickSize") is not None else None,
            step_size=str(((row.get("filters") or {}).get("quantity") or {}).get("stepSize"))
            if ((row.get("filters") or {}).get("quantity") or {}).get("stepSize") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
        if str(row.get("marketType", "")).upper() == "SPOT"
    ]
    return symbols, []


def phemex() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    data = fetch_json("https://api.phemex.com/public/products").get("data", {})
    symbols = [
        SymbolStatus(
            exchange="phemex",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseCurrency", "")).upper(),
            quote=str(row.get("quoteCurrency", "")).upper(),
            tradable=str(row.get("status", "")).lower() == "listed",
            status=str(row.get("status", "")),
            min_quote=str(row.get("minOrderValue")) if row.get("minOrderValue") is not None else None,
            tick_size=str(row.get("quoteTickSize")) if row.get("quoteTickSize") is not None else None,
            step_size=str(row.get("baseTickSize")) if row.get("baseTickSize") is not None else None,
            raw_json=raw(row),
        )
        for row in data.get("products", [])
        if str(row.get("type", "")).lower() == "spot" and row.get("symbol")
    ]
    return symbols, []


def bullish() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    base_url = "https://api.exchange.bullish.com/trading-api/v1"
    rows = fetch_json(f"{base_url}/markets")
    symbols = [
        SymbolStatus(
            exchange="bullish",
            symbol=str(row.get("symbol", "")).upper(),
            base=str(row.get("baseSymbol", "")).upper(),
            quote=str(row.get("quoteSymbol", "")).upper(),
            tradable=bool(row.get("spotTradingEnabled"))
            and bool(row.get("marketEnabled"))
            and bool(row.get("createOrderEnabled")),
            status="enabled" if bool(row.get("marketEnabled")) else "disabled",
            min_base=str(row.get("minQuantityLimit")) if row.get("minQuantityLimit") is not None else None,
            tick_size=str(row.get("tickSize")) if row.get("tickSize") is not None else None,
            step_size=str(row.get("quantityPrecision")) if row.get("quantityPrecision") is not None else None,
            raw_json=raw(row),
        )
        for row in rows
        if row.get("symbol")
    ]

    assets: list[AssetStatus] = []
    for row in fetch_json(f"{base_url}/assets"):
        asset = str(row.get("symbol", "")).upper()
        if asset not in ASSET_FILTER:
            continue
        assets.append(
            AssetStatus(
                exchange="bullish",
                asset=asset,
                network="",
                deposit_enabled=None,
                withdraw_enabled=None,
                status="listed",
                raw_json=raw(row),
            )
        )
    return symbols, assets


def woox() -> tuple[list[SymbolStatus], list[AssetStatus]]:
    rows = fetch_json("https://api.woo.org/v1/public/info").get("rows", [])
    symbols: list[SymbolStatus] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        if not symbol.startswith("SPOT_"):
            continue
        parts = symbol.split("_")
        if len(parts) != 3:
            continue
        _spot, base, quote = parts
        symbols.append(
            SymbolStatus(
                exchange="woox",
                symbol=symbol,
                base=base,
                quote=quote,
                tradable=str(row.get("status", "")).upper() == "TRADING" and int(row.get("is_trading") or 0) == 1,
                status=str(row.get("status", "")),
                min_base=str(row.get("base_min")) if row.get("base_min") is not None else None,
                min_quote=str(row.get("min_notional")) if row.get("min_notional") is not None else None,
                tick_size=str(row.get("quote_tick")) if row.get("quote_tick") is not None else None,
                step_size=str(row.get("base_tick")) if row.get("base_tick") is not None else None,
                raw_json=raw(row),
            )
        )
    return symbols, []


def normalize_luno_asset(value: Any) -> str:
    asset = str(value or "").upper()
    return "BTC" if asset == "XBT" else asset


def normalize_bitmex_asset(value: Any) -> str:
    asset = str(value or "").upper()
    if asset in {"XBT", "XBTM"}:
        return "BTC"
    if asset == "USDT":
        return "USDT"
    return asset


def column(data: dict[str, Any], key: str, index: int) -> str:
    values = data.get(key, [])
    if isinstance(values, list) and index < len(values):
        return str(values[index] or "")
    return ""


def column_bool(data: dict[str, Any], key: str, index: int) -> bool:
    values = data.get(key, [])
    if isinstance(values, list) and index < len(values):
        return bool(values[index])
    return False


FETCHERS: dict[str, Callable[[], tuple[list[SymbolStatus], list[AssetStatus]]]] = {
    "backpack": backpack,
    "binance": lambda: binance_like("binance", "https://api.binance.com"),
    "binanceus": lambda: binance_like("binanceus", "https://api.binance.us"),
    "bingx": bingx,
    "bybit": bybit,
    "buda": buda,
    "okx": okx,
    "gate": gate,
    "hashkey": hashkey,
    "hitbtc": hitbtc,
    "hyperliquid": hyperliquid,
    "kucoin": kucoin,
    "mexc": mexc,
    "bitget": bitget,
    "bitbank": bitbank,
    "bitfinex": bitfinex,
    "bitflyer": bitflyer,
    "bitmex": bitmex,
    "bitvavo": bitvavo,
    "bithumb": bithumb,
    "bitrue": bitrue,
    "btcmarkets": btcmarkets,
    "ndax": ndax,
    "bitopro": bitopro,
    "xt": xt,
    "coinbase": coinbase,
    "cryptocom": cryptocom,
    "foxbit": foxbit,
    "bitstamp": bitstamp,
    "bitso": bitso,
    "coincheck": coincheck,
    "coinex": coinex,
    "coinone": coinone,
    "cointr": cointr,
    "coinw": coinw,
    "coinsph": coinsph,
    "deribit": deribit,
    "digifinex": digifinex,
    "htx": htx,
    "bitmart": bitmart,
    "gmocoin": gmocoin,
    "kraken": kraken,
    "korbit": korbit,
    "latoken": latoken,
    "luno": luno,
    "independentreserve": independentreserve,
    "gemini": gemini,
    "poloniex": poloniex,
    "phemex": phemex,
    "bullish": bullish,
    "pionex": pionex,
    "toobit": toobit,
    "ascendex": ascendex,
    "exmo": exmo,
    "btcturk": btcturk,
    "cexio": cexio,
    "indodax": indodax,
    "bitkub": bitkub,
    "mercadobitcoin": mercadobitcoin,
    "novadax": novadax,
    "upbit": upbit,
    "valr": valr,
    "whitebit": whitebit,
    "woox": woox,
}


def init_sqlite(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS symbol_status (
            exchange TEXT NOT NULL,
            symbol TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            tradable INTEGER,
            status TEXT NOT NULL,
            min_base TEXT,
            min_quote TEXT,
            tick_size TEXT,
            step_size TEXT,
            observed_at_ms INTEGER NOT NULL,
            raw_json TEXT NOT NULL,
            PRIMARY KEY(exchange, symbol)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS asset_status (
            exchange TEXT NOT NULL,
            asset TEXT NOT NULL,
            network TEXT NOT NULL,
            deposit_enabled INTEGER,
            withdraw_enabled INTEGER,
            status TEXT NOT NULL,
            observed_at_ms INTEGER NOT NULL,
            raw_json TEXT NOT NULL,
            PRIMARY KEY(exchange, asset, network)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS status_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at_ms INTEGER NOT NULL,
            elapsed_ms INTEGER NOT NULL,
            exchanges_checked INTEGER NOT NULL,
            symbols_saved INTEGER NOT NULL,
            assets_saved INTEGER NOT NULL,
            errors_json TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def bool_to_int(value: bool | None) -> int | None:
    if value is None:
        return None
    return 1 if value else 0


def save_statuses(conn: sqlite3.Connection, observed_at_ms: int, symbols: list[SymbolStatus], assets: list[AssetStatus]) -> None:
    conn.executemany(
        """
        INSERT INTO symbol_status (
            exchange, symbol, base, quote, tradable, status, min_base, min_quote,
            tick_size, step_size, observed_at_ms, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(exchange, symbol) DO UPDATE SET
            base=excluded.base,
            quote=excluded.quote,
            tradable=excluded.tradable,
            status=excluded.status,
            min_base=excluded.min_base,
            min_quote=excluded.min_quote,
            tick_size=excluded.tick_size,
            step_size=excluded.step_size,
            observed_at_ms=excluded.observed_at_ms,
            raw_json=excluded.raw_json
        """,
        [
            (
                row.exchange,
                row.symbol,
                row.base,
                row.quote,
                bool_to_int(row.tradable),
                row.status,
                row.min_base,
                row.min_quote,
                row.tick_size,
                row.step_size,
                observed_at_ms,
                row.raw_json,
            )
            for row in symbols
        ],
    )
    conn.executemany(
        """
        INSERT INTO asset_status (
            exchange, asset, network, deposit_enabled, withdraw_enabled,
            status, observed_at_ms, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(exchange, asset, network) DO UPDATE SET
            deposit_enabled=excluded.deposit_enabled,
            withdraw_enabled=excluded.withdraw_enabled,
            status=excluded.status,
            observed_at_ms=excluded.observed_at_ms,
            raw_json=excluded.raw_json
        """,
        [
            (
                row.exchange,
                row.asset,
                row.network,
                bool_to_int(row.deposit_enabled),
                bool_to_int(row.withdraw_enabled),
                row.status,
                observed_at_ms,
                row.raw_json,
            )
            for row in assets
        ],
    )
    conn.commit()


def run_cycle(conn: sqlite3.Connection, exchanges: list[str], workers: int) -> None:
    started = now_ms()
    observed_at_ms = started
    symbols: list[SymbolStatus] = []
    assets: list[AssetStatus] = []
    errors: list[dict[str, str]] = []

    def fetch_exchange(exchange: str) -> tuple[str, list[SymbolStatus], list[AssetStatus], float]:
        fetcher = FETCHERS[exchange]
        start = time.time()
        symbol_rows, asset_rows = fetcher()
        return exchange, symbol_rows, asset_rows, time.time() - start

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, len(exchanges)))) as executor:
        future_to_exchange = {executor.submit(fetch_exchange, exchange): exchange for exchange in exchanges}
        for future in concurrent.futures.as_completed(future_to_exchange):
            exchange = future_to_exchange[future]
            try:
                name, symbol_rows, asset_rows, elapsed = future.result()
            except Exception as exc:
                errors.append({"exchange": exchange, "error": str(exc)})
                print(f"[STATUS_ERR] {exchange}: {exc}", file=sys.stderr, flush=True)
                continue
            symbols.extend(symbol_rows)
            assets.extend(asset_rows)
            print(
                f"[STATUS_OK] {name}: symbols={len(symbol_rows)} assets={len(asset_rows)} elapsed={elapsed:.1f}s",
                file=sys.stderr,
                flush=True,
            )

    save_statuses(conn, observed_at_ms, symbols, assets)
    elapsed_ms = now_ms() - started
    conn.execute(
        """
        INSERT INTO status_cycles (
            started_at_ms, elapsed_ms, exchanges_checked, symbols_saved,
            assets_saved, errors_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (started, elapsed_ms, len(exchanges), len(symbols), len(assets), json.dumps(errors, sort_keys=True)),
    )
    conn.commit()
    print(
        "[STATUS_CYCLE] "
        f"exchanges={len(exchanges)} symbols={len(symbols)} assets={len(assets)} "
        f"errors={len(errors)} elapsed_ms={elapsed_ms}",
        flush=True,
    )


def parse_csv(value: str) -> list[str]:
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def parse_asset_csv(value: str) -> set[str]:
    if value.strip().lower() in {"", "none", "off", "false"}:
        return set()
    return {item.strip().upper() for item in value.split(",") if item.strip()}


def main() -> int:
    default_out = Path.home() / "Library/Application Support/hackathon-btc/status"
    parser = argparse.ArgumentParser(description="Public exchange operational status monitor")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval-sec", type=float, default=float(os.getenv("STATUS_MONITOR_INTERVAL_SEC", "300")))
    parser.add_argument("--out-dir", default=os.getenv("STATUS_MONITOR_OUT_DIR", str(default_out)))
    parser.add_argument("--workers", type=int, default=int(os.getenv("STATUS_MONITOR_WORKERS", "8")))
    parser.add_argument("--exchanges", default=os.getenv("STATUS_MONITOR_EXCHANGES", ",".join(sorted(DEFAULT_EXCHANGES))))
    parser.add_argument(
        "--asset-filter",
        default=os.getenv("STATUS_MONITOR_ASSET_FILTER", ",".join(sorted(DEFAULT_ASSET_FILTER))),
        help="Assets for public network/deposit/withdraw checks on venues that expose them. Use 'none' to disable.",
    )
    args = parser.parse_args()

    global ASSET_FILTER
    ASSET_FILTER = parse_asset_csv(args.asset_filter)
    exchanges = [exchange for exchange in parse_csv(args.exchanges) if exchange in FETCHERS]
    if not exchanges:
        raise SystemExit("No valid exchanges selected")

    out_dir = Path(args.out_dir).expanduser()
    conn = init_sqlite(out_dir / "status.sqlite")
    print("public operational status monitor")
    print(f"exchanges={','.join(exchanges)} interval_sec={args.interval_sec} workers={args.workers}")
    print(f"outputs={out_dir / 'status.sqlite'}")
    print("risk=public status only; deposit/withdraw unavailable on many venues without private auth\n")

    while True:
        run_cycle(conn, exchanges, args.workers)
        if args.once:
            break
        time.sleep(args.interval_sec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
