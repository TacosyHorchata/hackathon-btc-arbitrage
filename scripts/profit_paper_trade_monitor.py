#!/usr/bin/env python3
"""Paper-execute saved public-book opportunities after latency.

This is still no-key/no-order. It turns detections into a transaction ledger:
after a minimum age, it re-walks the current public books for the same
route/notional and records the virtual buy leg, sell leg, fees, inventory
requirement, and net P&L that would have resulted from immediate taker fills.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Any

from profit_monitor import (
    DEFAULT_STATUS_DB,
    DEFAULT_TAKER_BPS,
    Opportunity,
    RouteCandidate,
    attach_operational_status,
    build_adapters,
    depth_check_candidate,
    json_decimal_default,
    open_status_db,
    quant,
)

getcontext().prec = 40

DEFAULT_LIVE_DB = Path.home() / "Library/Application Support/hackathon-btc/live/profitable_cases.sqlite"
DEFAULT_BTC_DB = Path.home() / "Library/Application Support/hackathon-btc/btc_hot_path/profitable_cases.sqlite"
DEFAULT_OUT_DIR = Path.home() / "Library/Application Support/hackathon-btc/paper_trades"
DEFAULT_INVENTORY_CONFIG = Path.home() / "Library/Application Support/hackathon-btc/inventory.json"
DEFAULT_ALLOWED_GRADES = {
    "tradable_rebalance_public_ok",
    "tradable_rebalance_unknown",
    "status_unknown",
    "status_unavailable",
}


@dataclass(frozen=True)
class Source:
    name: str
    db_path: Path


@dataclass(frozen=True)
class Inventory:
    path: str
    observed_at_ms: int
    balances: dict[str, dict[str, Decimal]]

    def available(self, exchange: str, asset: str) -> Decimal | None:
        return self.balances.get(exchange.lower(), {}).get(asset.upper())


@dataclass(frozen=True)
class InventoryCheck:
    grade: str
    hint: str
    executable_notional_quote: Decimal | None = None
    executable_base_size: Decimal | None = None
    executable_profit_quote: Decimal | None = None


@dataclass(frozen=True)
class PaperResult:
    source: Source
    source_opportunity: dict[str, Any]
    papered_at_ms: int
    status: str
    opportunity: Opportunity | None
    inventory: InventoryCheck
    evidence: dict[str, Any]
    error: str = ""


def now_ms() -> int:
    return int(time.time() * 1000)


def dec(value: Any) -> Decimal:
    try:
        parsed = Decimal(str(value))
        if not parsed.is_finite():
            raise ValueError(value)
        return parsed
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def optional_dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        parsed = Decimal(str(value))
        if not parsed.is_finite():
            return None
        return parsed
    except (InvalidOperation, ValueError):
        return None


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def balance_decimal(value: Any) -> Decimal:
    if isinstance(value, dict):
        for key in ("available", "free", "balance"):
            if key in value:
                return balance_decimal(value[key])
        raise ValueError(f"balance object needs available/free/balance: {value!r}")
    parsed = dec(value)
    if parsed < 0:
        raise ValueError(f"negative balance is invalid: {value!r}")
    return parsed


def load_inventory(path: Path) -> Inventory | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_balances = data.get("balances", data.get("exchanges", {})) if isinstance(data, dict) else {}
    balances: dict[str, dict[str, Decimal]] = {}

    if isinstance(raw_balances, list):
        for row in raw_balances:
            if not isinstance(row, dict):
                continue
            exchange = str(row.get("exchange", "")).lower()
            asset = str(row.get("asset", "")).upper()
            if not exchange or not asset:
                continue
            balances.setdefault(exchange, {})[asset] = balance_decimal(
                row.get("available", row.get("free", row.get("balance", "0")))
            )
    elif isinstance(raw_balances, dict):
        for exchange, assets in raw_balances.items():
            if not isinstance(assets, dict):
                continue
            exchange_key = str(exchange).lower()
            for asset, value in assets.items():
                balances.setdefault(exchange_key, {})[str(asset).upper()] = balance_decimal(value)

    return Inventory(path=str(path), observed_at_ms=now_ms(), balances=balances)


def check_inventory(opportunity: Opportunity | None, inventory: Inventory | None, inventory_path: Path) -> InventoryCheck:
    if opportunity is None:
        return InventoryCheck("inventory_unchecked", "no_profitable_paper_opportunity")
    if inventory is None:
        return InventoryCheck("inventory_unknown", f"inventory_config_missing path={inventory_path}")

    buy_quote_available = inventory.available(opportunity.buy_exchange, opportunity.quote)
    sell_base_available = inventory.available(opportunity.sell_exchange, opportunity.base)
    quote_required = opportunity.buy_quote + opportunity.buy_fee_quote
    base_required = opportunity.base_size

    if buy_quote_available is None or sell_base_available is None:
        missing: list[str] = []
        if buy_quote_available is None:
            missing.append(f"{opportunity.buy_exchange}.{opportunity.quote}")
        if sell_base_available is None:
            missing.append(f"{opportunity.sell_exchange}.{opportunity.base}")
        return InventoryCheck(
            "inventory_unknown",
            f"inventory={inventory.path} missing={','.join(missing)} "
            f"required_quote={quant(quote_required)} required_base={quant(base_required)}",
        )

    quote_fraction = Decimal("1") if quote_required <= 0 else buy_quote_available / quote_required
    base_fraction = Decimal("1") if base_required <= 0 else sell_base_available / base_required
    executable_fraction = max(Decimal("0"), min(Decimal("1"), quote_fraction, base_fraction))
    executable_notional = opportunity.notional_quote * executable_fraction
    executable_base = opportunity.base_size * executable_fraction
    executable_profit = opportunity.net_profit_quote * executable_fraction

    if executable_fraction >= Decimal("1"):
        grade = "inventory_executable"
    elif executable_fraction > 0:
        grade = "inventory_partial"
    else:
        grade = "inventory_insufficient"

    return InventoryCheck(
        grade=grade,
        hint=(
            f"inventory={inventory.path} "
            f"buy_quote_available={quant(buy_quote_available)} "
            f"quote_required={quant(quote_required)} "
            f"sell_base_available={quant(sell_base_available)} "
            f"base_required={quant(base_required)}"
        ),
        executable_notional_quote=executable_notional,
        executable_base_size=executable_base,
        executable_profit_quote=executable_profit,
    )


def parse_sources(values: list[str] | None) -> list[Source]:
    if not values:
        defaults = [
            Source("broad", DEFAULT_LIVE_DB),
            Source("btc_hot", DEFAULT_BTC_DB),
        ]
        return [source for source in defaults if source.db_path.exists()]

    sources: list[Source] = []
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --source {value!r}; expected name=/path/to/db.sqlite")
        name, path = value.split("=", 1)
        name = name.strip()
        if not name:
            raise SystemExit(f"Invalid --source {value!r}; source name is empty")
        sources.append(Source(name, Path(path).expanduser()))
    return sources


def init_sqlite(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS paper_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            source_db TEXT NOT NULL,
            source_opportunity_id INTEGER NOT NULL,
            source_detected_at_ms INTEGER NOT NULL,
            papered_at_ms INTEGER NOT NULL,
            elapsed_since_detection_ms INTEGER NOT NULL,
            route_key TEXT NOT NULL,
            mode TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            requested_notional_quote TEXT NOT NULL,
            source_net_bps TEXT NOT NULL,
            paper_status TEXT NOT NULL,
            proof_type TEXT NOT NULL,
            notional_quote TEXT,
            base_size TEXT,
            buy_avg TEXT,
            sell_avg TEXT,
            buy_quote TEXT,
            sell_quote TEXT,
            buy_fee_quote TEXT,
            sell_fee_quote TEXT,
            latency_haircut_quote TEXT,
            net_profit_quote TEXT,
            net_bps TEXT,
            gross_bps TEXT,
            buy_levels INTEGER,
            sell_levels INTEGER,
            operational_grade TEXT NOT NULL DEFAULT '',
            status_hint TEXT NOT NULL DEFAULT '',
            inventory_grade TEXT NOT NULL DEFAULT 'inventory_unknown',
            inventory_hint TEXT NOT NULL DEFAULT '',
            executable_notional_quote TEXT,
            executable_base_size TEXT,
            executable_profit_quote TEXT,
            evidence_json TEXT NOT NULL,
            error TEXT NOT NULL DEFAULT '',
            UNIQUE(source_name, source_opportunity_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS paper_trade_cases (
            source_name TEXT NOT NULL,
            route_key TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            first_paper_ms INTEGER NOT NULL,
            last_paper_ms INTEGER NOT NULL,
            attempt_count INTEGER NOT NULL,
            profitable_count INTEGER NOT NULL,
            failed_count INTEGER NOT NULL,
            inventory_executable_count INTEGER NOT NULL,
            max_net_bps TEXT,
            max_net_profit_quote TEXT,
            max_notional_quote TEXT,
            last_paper_status TEXT NOT NULL,
            last_net_bps TEXT,
            last_net_profit_quote TEXT,
            last_notional_quote TEXT,
            last_operational_grade TEXT NOT NULL,
            last_status_hint TEXT NOT NULL,
            last_inventory_grade TEXT NOT NULL,
            last_inventory_hint TEXT NOT NULL,
            PRIMARY KEY(source_name, route_key)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS paper_trade_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at_ms INTEGER NOT NULL,
            elapsed_ms INTEGER NOT NULL,
            sources_json TEXT NOT NULL,
            candidates_total INTEGER NOT NULL,
            papered_total INTEGER NOT NULL,
            profitable_total INTEGER NOT NULL,
            inventory_executable_total INTEGER NOT NULL,
            errors_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_paper_trades_route_time
        ON paper_trades(source_name, route_key, papered_at_ms)
        """
    )
    conn.commit()
    return conn


def open_source_db(path: Path) -> sqlite3.Connection | None:
    if not path.exists():
        return None
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def already_papered(conn: sqlite3.Connection, source_name: str, source_opportunity_id: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM paper_trades WHERE source_name = ? AND source_opportunity_id = ?",
        (source_name, source_opportunity_id),
    ).fetchone()
    return row is not None


def fetch_source_candidates(
    out_conn: sqlite3.Connection,
    source: Source,
    *,
    limit: int,
    min_age_sec: float,
    max_age_sec: float,
    allowed_grades: set[str],
    quote: str | None,
    base: str | None,
) -> list[dict[str, Any]]:
    conn = open_source_db(source.db_path)
    if conn is None:
        return []
    try:
        current_ms = now_ms()
        newest_ms = current_ms - int(min_age_sec * 1000)
        oldest_ms = current_ms - int(max_age_sec * 1000)
        where = [
            "detected_at_ms <= ?",
            "detected_at_ms >= ?",
        ]
        params: list[Any] = [newest_ms, oldest_ms]
        if allowed_grades:
            where.append(f"operational_grade IN ({','.join('?' for _ in allowed_grades)})")
            params.extend(sorted(allowed_grades))
        if quote:
            where.append("quote = ?")
            params.append(quote.upper())
        if base:
            where.append("base = ?")
            params.append(base.upper())

        params.append(limit * 3)
        rows = conn.execute(
            f"""
            SELECT
                id, detected_at_ms, route_key, mode, base, quote,
                buy_exchange, sell_exchange, buy_symbol, sell_symbol,
                notional_quote, base_size, buy_avg, sell_avg,
                buy_quote, sell_quote, buy_fee_quote, sell_fee_quote,
                latency_haircut_quote, net_bps, net_profit_quote, gross_bps,
                top_net_bps, operational_grade, status_hint, status_json,
                evidence_json
            FROM opportunities
            WHERE {' AND '.join(where)}
            ORDER BY detected_at_ms DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
    finally:
        conn.close()

    candidates: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if already_papered(out_conn, source.name, int(item["id"])):
            continue
        candidates.append(item)
        if len(candidates) >= limit:
            break
    return candidates


def candidate_from_source(source: dict[str, Any], default_latency_bps: Decimal) -> RouteCandidate:
    evidence = json.loads(source.get("evidence_json") or "{}")
    raw_candidate = evidence.get("candidate", {}) if isinstance(evidence, dict) else {}
    if not isinstance(raw_candidate, dict):
        raw_candidate = {}

    buy_taker_bps = optional_dec(raw_candidate.get("buy_taker_bps"))
    if buy_taker_bps is None:
        buy_taker_bps = DEFAULT_TAKER_BPS.get(source["buy_exchange"], Decimal("10"))
    sell_taker_bps = optional_dec(raw_candidate.get("sell_taker_bps"))
    if sell_taker_bps is None:
        sell_taker_bps = DEFAULT_TAKER_BPS.get(source["sell_exchange"], Decimal("10"))

    gross_bps = optional_dec(raw_candidate.get("gross_bps")) or dec(source["gross_bps"])
    latency_bps = optional_dec(raw_candidate.get("latency_bps")) or default_latency_bps
    fee_bps = optional_dec(raw_candidate.get("fee_bps")) or (buy_taker_bps + sell_taker_bps)
    top_net_bps = optional_dec(raw_candidate.get("top_net_bps")) or dec(source["top_net_bps"])

    return RouteCandidate(
        base=source["base"],
        quote=source["quote"],
        buy_exchange=source["buy_exchange"],
        sell_exchange=source["sell_exchange"],
        buy_symbol=source["buy_symbol"],
        sell_symbol=source["sell_symbol"],
        buy_ask=optional_dec(raw_candidate.get("buy_ask")) or dec(source["buy_avg"]),
        sell_bid=optional_dec(raw_candidate.get("sell_bid")) or dec(source["sell_avg"]),
        buy_taker_bps=buy_taker_bps,
        sell_taker_bps=sell_taker_bps,
        gross_bps=gross_bps,
        fee_bps=fee_bps,
        latency_bps=latency_bps,
        top_net_bps=top_net_bps,
        depth_proxy_quote=optional_dec(raw_candidate.get("depth_proxy_quote")),
    )


def paper_source(
    source: Source,
    source_opportunity: dict[str, Any],
    *,
    adapters_by_name: dict[str, Any],
    inventory: Inventory | None,
    inventory_path: Path,
    min_paper_net_bps: Decimal,
    default_latency_bps: Decimal,
    require_inventory: bool,
) -> PaperResult:
    papered_at_ms = now_ms()
    try:
        if source_opportunity["buy_exchange"] not in adapters_by_name or source_opportunity["sell_exchange"] not in adapters_by_name:
            missing = [
                name
                for name in (source_opportunity["buy_exchange"], source_opportunity["sell_exchange"])
                if name not in adapters_by_name
            ]
            return PaperResult(
                source=source,
                source_opportunity=source_opportunity,
                papered_at_ms=papered_at_ms,
                status="adapter_missing",
                opportunity=None,
                inventory=InventoryCheck("inventory_unchecked", "adapter_missing"),
                evidence={"missing_adapters": missing},
                error="adapter_missing",
            )

        candidate = candidate_from_source(source_opportunity, default_latency_bps)
        opportunity, evidence = depth_check_candidate(
            candidate,
            adapters_by_name,
            [dec(source_opportunity["notional_quote"])],
            min_paper_net_bps,
        )
        if opportunity is not None:
            # Operational status is attached in the main thread because sqlite
            # connections are thread-affine by default.
            pass
        inventory_check = check_inventory(opportunity, inventory, inventory_path)

        if opportunity is None:
            status = "not_profitable"
            if isinstance(evidence, dict) and evidence.get("error"):
                status = str(evidence["error"])
        elif require_inventory and inventory_check.grade != "inventory_executable":
            status = "inventory_not_executable"
        else:
            status = "paper_profitable"

        return PaperResult(
            source=source,
            source_opportunity=source_opportunity,
            papered_at_ms=opportunity.detected_at_ms if opportunity else now_ms(),
            status=status,
            opportunity=opportunity,
            inventory=inventory_check,
            evidence=evidence if isinstance(evidence, dict) else {},
        )
    except Exception as exc:
        return PaperResult(
            source=source,
            source_opportunity=source_opportunity,
            papered_at_ms=now_ms(),
            status="error",
            opportunity=None,
            inventory=InventoryCheck("inventory_unchecked", "error"),
            evidence={},
            error=str(exc),
        )


def update_case(conn: sqlite3.Connection, result: PaperResult) -> None:
    source = result.source_opportunity
    opportunity = result.opportunity
    profitable = result.status == "paper_profitable"
    inventory_executable = result.inventory.grade == "inventory_executable"
    existing = conn.execute(
        """
        SELECT attempt_count, profitable_count, failed_count, inventory_executable_count,
               max_net_bps, max_net_profit_quote, max_notional_quote
        FROM paper_trade_cases
        WHERE source_name = ? AND route_key = ?
        """,
        (result.source.name, source["route_key"]),
    ).fetchone()

    last_net_bps = quant(opportunity.net_bps) if opportunity else None
    last_profit = quant(opportunity.net_profit_quote) if opportunity else None
    last_notional = quant(opportunity.notional_quote) if opportunity else None
    last_grade = opportunity.operational_grade if opportunity else ""
    last_hint = opportunity.status_hint if opportunity else ""

    if existing is None:
        conn.execute(
            """
            INSERT INTO paper_trade_cases (
                source_name, route_key, base, quote, buy_exchange, sell_exchange,
                buy_symbol, sell_symbol, first_paper_ms, last_paper_ms,
                attempt_count, profitable_count, failed_count,
                inventory_executable_count, max_net_bps, max_net_profit_quote,
                max_notional_quote, last_paper_status, last_net_bps,
                last_net_profit_quote, last_notional_quote, last_operational_grade,
                last_status_hint, last_inventory_grade, last_inventory_hint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.source.name,
                source["route_key"],
                source["base"],
                source["quote"],
                source["buy_exchange"],
                source["sell_exchange"],
                source["buy_symbol"],
                source["sell_symbol"],
                result.papered_at_ms,
                result.papered_at_ms,
                1,
                1 if profitable else 0,
                0 if profitable else 1,
                1 if inventory_executable else 0,
                last_net_bps,
                last_profit,
                last_notional,
                result.status,
                last_net_bps,
                last_profit,
                last_notional,
                last_grade,
                last_hint,
                result.inventory.grade,
                result.inventory.hint,
            ),
        )
        return

    (
        attempt_count,
        profitable_count,
        failed_count,
        inventory_executable_count,
        max_net_bps,
        max_profit,
        max_notional,
    ) = existing
    is_new_max = False
    if profitable and opportunity is not None:
        is_new_max = max_net_bps is None or opportunity.net_bps > dec(max_net_bps)

    conn.execute(
        """
        UPDATE paper_trade_cases
        SET
            last_paper_ms = ?,
            attempt_count = ?,
            profitable_count = ?,
            failed_count = ?,
            inventory_executable_count = ?,
            max_net_bps = ?,
            max_net_profit_quote = ?,
            max_notional_quote = ?,
            last_paper_status = ?,
            last_net_bps = ?,
            last_net_profit_quote = ?,
            last_notional_quote = ?,
            last_operational_grade = ?,
            last_status_hint = ?,
            last_inventory_grade = ?,
            last_inventory_hint = ?
        WHERE source_name = ? AND route_key = ?
        """,
        (
            result.papered_at_ms,
            int(attempt_count) + 1,
            int(profitable_count) + (1 if profitable else 0),
            int(failed_count) + (0 if profitable else 1),
            int(inventory_executable_count) + (1 if inventory_executable else 0),
            quant(opportunity.net_bps) if is_new_max and opportunity else max_net_bps,
            quant(opportunity.net_profit_quote) if is_new_max and opportunity else max_profit,
            quant(opportunity.notional_quote) if is_new_max and opportunity else max_notional,
            result.status,
            last_net_bps,
            last_profit,
            last_notional,
            last_grade,
            last_hint,
            result.inventory.grade,
            result.inventory.hint,
            result.source.name,
            source["route_key"],
        ),
    )


def save_result(conn: sqlite3.Connection, jsonl_path: Path, result: PaperResult) -> None:
    source = result.source_opportunity
    opportunity = result.opportunity
    elapsed_ms = result.papered_at_ms - int(source["detected_at_ms"])
    evidence = {
        "source": {
            "name": result.source.name,
            "db": str(result.source.db_path),
            "opportunity": source,
        },
        "paper": {
            "status": result.status,
            "proof_type": "post_latency_public_depth_walk",
            "opportunity": asdict(opportunity) if opportunity else None,
            "inventory": asdict(result.inventory),
            "evidence": result.evidence,
            "error": result.error,
        },
    }

    row = {
        "source_name": result.source.name,
        "source_db": str(result.source.db_path),
        "source_opportunity_id": source["id"],
        "source_detected_at_ms": source["detected_at_ms"],
        "papered_at_ms": result.papered_at_ms,
        "elapsed_since_detection_ms": elapsed_ms,
        "route_key": source["route_key"],
        "paper_status": result.status,
        "net_profit_quote": quant(opportunity.net_profit_quote) if opportunity else None,
        "net_bps": quant(opportunity.net_bps) if opportunity else None,
        "inventory_grade": result.inventory.grade,
        "error": result.error,
    }

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, default=json_decimal_default, sort_keys=True) + "\n")

    conn.execute(
        """
        INSERT OR IGNORE INTO paper_trades (
            source_name, source_db, source_opportunity_id, source_detected_at_ms,
            papered_at_ms, elapsed_since_detection_ms, route_key, mode, base,
            quote, buy_exchange, sell_exchange, buy_symbol, sell_symbol,
            requested_notional_quote, source_net_bps, paper_status, proof_type,
            notional_quote, base_size, buy_avg, sell_avg, buy_quote, sell_quote,
            buy_fee_quote, sell_fee_quote, latency_haircut_quote, net_profit_quote,
            net_bps, gross_bps, buy_levels, sell_levels, operational_grade,
            status_hint, inventory_grade, inventory_hint, executable_notional_quote,
            executable_base_size, executable_profit_quote, evidence_json, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.source.name,
            str(result.source.db_path),
            int(source["id"]),
            int(source["detected_at_ms"]),
            result.papered_at_ms,
            elapsed_ms,
            source["route_key"],
            source["mode"],
            source["base"],
            source["quote"],
            source["buy_exchange"],
            source["sell_exchange"],
            source["buy_symbol"],
            source["sell_symbol"],
            source["notional_quote"],
            source["net_bps"],
            result.status,
            "post_latency_public_depth_walk",
            quant(opportunity.notional_quote) if opportunity else None,
            quant(opportunity.base_size) if opportunity else None,
            quant(opportunity.buy_avg) if opportunity else None,
            quant(opportunity.sell_avg) if opportunity else None,
            quant(opportunity.buy_quote) if opportunity else None,
            quant(opportunity.sell_quote) if opportunity else None,
            quant(opportunity.buy_fee_quote) if opportunity else None,
            quant(opportunity.sell_fee_quote) if opportunity else None,
            quant(opportunity.latency_haircut_quote) if opportunity else None,
            quant(opportunity.net_profit_quote) if opportunity else None,
            quant(opportunity.net_bps) if opportunity else None,
            quant(opportunity.gross_bps) if opportunity else None,
            opportunity.buy_levels if opportunity else None,
            opportunity.sell_levels if opportunity else None,
            opportunity.operational_grade if opportunity else "",
            opportunity.status_hint if opportunity else "",
            result.inventory.grade,
            result.inventory.hint,
            quant(result.inventory.executable_notional_quote),
            quant(result.inventory.executable_base_size),
            quant(result.inventory.executable_profit_quote),
            json.dumps(evidence, default=json_decimal_default, sort_keys=True),
            result.error,
        ),
    )
    update_case(conn, result)
    conn.commit()


def save_cycle(
    conn: sqlite3.Connection,
    *,
    started_at_ms: int,
    sources: list[Source],
    candidates_total: int,
    papered_total: int,
    profitable_total: int,
    inventory_executable_total: int,
    errors: list[dict[str, str]],
) -> None:
    conn.execute(
        """
        INSERT INTO paper_trade_cycles (
            started_at_ms, elapsed_ms, sources_json, candidates_total,
            papered_total, profitable_total, inventory_executable_total,
            errors_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            started_at_ms,
            now_ms() - started_at_ms,
            json.dumps({source.name: str(source.db_path) for source in sources}, sort_keys=True),
            candidates_total,
            papered_total,
            profitable_total,
            inventory_executable_total,
            json.dumps(errors, sort_keys=True),
        ),
    )
    conn.commit()


def run_cycle(
    *,
    conn: sqlite3.Connection,
    jsonl_path: Path,
    sources: list[Source],
    adapters_by_name: dict[str, Any],
    status_conn: sqlite3.Connection | None,
    inventory_config: Path,
    min_age_sec: float,
    max_age_sec: float,
    limit_per_source: int,
    workers: int,
    allowed_grades: set[str],
    quote: str | None,
    base: str | None,
    min_paper_net_bps: Decimal,
    default_latency_bps: Decimal,
    require_inventory: bool,
) -> None:
    started = now_ms()
    errors: list[dict[str, str]] = []
    try:
        inventory = load_inventory(inventory_config)
    except Exception as exc:
        inventory = None
        errors.append({"source": "inventory", "path": str(inventory_config), "error": str(exc)})
        print(f"[PAPER_ERR] inventory: {exc}", file=sys.stderr, flush=True)

    candidates: list[tuple[Source, dict[str, Any]]] = []
    for source in sources:
        try:
            rows = fetch_source_candidates(
                conn,
                source,
                limit=limit_per_source,
                min_age_sec=min_age_sec,
                max_age_sec=max_age_sec,
                allowed_grades=allowed_grades,
                quote=quote,
                base=base,
            )
            candidates.extend((source, row) for row in rows)
        except Exception as exc:
            errors.append({"source": source.name, "error": str(exc)})
            print(f"[PAPER_ERR] {source.name}: {exc}", file=sys.stderr, flush=True)

    papered = 0
    profitable = 0
    inventory_executable = 0
    if candidates:
        max_workers = max(1, min(len(candidates), workers))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    paper_source,
                    source,
                    source_opportunity,
                    adapters_by_name=adapters_by_name,
                    inventory=inventory,
                    inventory_path=inventory_config,
                    min_paper_net_bps=min_paper_net_bps,
                    default_latency_bps=default_latency_bps,
                    require_inventory=require_inventory,
                )
                for source, source_opportunity in candidates
            ]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.opportunity is not None:
                    opportunity = attach_operational_status(result.opportunity, status_conn)
                    status = result.status
                    if status == "paper_profitable" and opportunity.operational_grade in {"rebalance_blocked", "trading_blocked"}:
                        status = opportunity.operational_grade
                    result = replace(result, opportunity=opportunity, status=status)
                papered += 1
                if result.status == "paper_profitable":
                    profitable += 1
                if result.inventory.grade == "inventory_executable":
                    inventory_executable += 1
                if result.error:
                    errors.append(
                        {
                            "source": result.source.name,
                            "route_key": result.source_opportunity["route_key"],
                            "error": result.error,
                        }
                    )
                save_result(conn, jsonl_path, result)
                print(
                    "[PAPER] "
                    f"{result.status} {result.source.name} {result.source_opportunity['route_key']} "
                    f"elapsed_ms={result.papered_at_ms - int(result.source_opportunity['detected_at_ms'])} "
                    f"source_bps={result.source_opportunity['net_bps']} "
                    f"paper_bps={quant(result.opportunity.net_bps) if result.opportunity else ''} "
                    f"inventory={result.inventory.grade}",
                    flush=True,
                )

    save_cycle(
        conn,
        started_at_ms=started,
        sources=sources,
        candidates_total=len(candidates),
        papered_total=papered,
        profitable_total=profitable,
        inventory_executable_total=inventory_executable,
        errors=errors,
    )
    print(
        "[PAPER_CYCLE] "
        f"candidates={len(candidates)} papered={papered} profitable={profitable} "
        f"inventory_executable={inventory_executable} errors={len(errors)} "
        f"elapsed_ms={now_ms() - started}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper-execute saved public arbitrage opportunities.")
    parser.add_argument("--out-dir", default=os.getenv("PAPER_TRADE_OUT_DIR", str(DEFAULT_OUT_DIR)))
    parser.add_argument("--source", action="append", default=None, help="Source DB as name=/path/to/profitable_cases.sqlite. Defaults to broad and btc_hot when present.")
    parser.add_argument("--interval-sec", type=float, default=float(os.getenv("PAPER_TRADE_INTERVAL_SEC", "10")))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--min-age-sec", type=float, default=float(os.getenv("PAPER_TRADE_MIN_AGE_SEC", "5")))
    parser.add_argument("--max-age-sec", type=float, default=float(os.getenv("PAPER_TRADE_MAX_AGE_SEC", "7200")))
    parser.add_argument("--limit-per-source", type=int, default=int(os.getenv("PAPER_TRADE_LIMIT_PER_SOURCE", "20")))
    parser.add_argument("--workers", type=int, default=int(os.getenv("PAPER_TRADE_WORKERS", "6")))
    parser.add_argument("--allowed-grades", default=os.getenv("PAPER_TRADE_ALLOWED_GRADES", ",".join(sorted(DEFAULT_ALLOWED_GRADES))))
    parser.add_argument("--quote", default=os.getenv("PAPER_TRADE_QUOTE"))
    parser.add_argument("--base", default=os.getenv("PAPER_TRADE_BASE"))
    parser.add_argument("--min-paper-net-bps", default=os.getenv("PAPER_TRADE_MIN_NET_BPS", "1"))
    parser.add_argument("--latency-bps", default=os.getenv("PAPER_TRADE_LATENCY_BPS", "2"))
    parser.add_argument("--status-db", default=os.getenv("PAPER_TRADE_STATUS_DB", str(DEFAULT_STATUS_DB)))
    parser.add_argument("--inventory-config", default=os.getenv("PAPER_TRADE_INVENTORY_CONFIG", str(DEFAULT_INVENTORY_CONFIG)))
    parser.add_argument(
        "--require-inventory",
        action="store_true",
        default=env_bool("PAPER_TRADE_REQUIRE_INVENTORY", False),
        help="Mark otherwise-profitable paper trades as not executable unless inventory.json covers both legs.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser()
    db_path = out_dir / "paper_trades.sqlite"
    jsonl_path = out_dir / "paper_trades.jsonl"
    sources = parse_sources(args.source)
    if not sources:
        raise SystemExit("No source DBs found. Pass --source name=/path/to/profitable_cases.sqlite.")

    conn = init_sqlite(db_path)
    adapters_by_name = build_adapters()
    status_conn = open_status_db(Path(args.status_db).expanduser())
    inventory_config = Path(args.inventory_config).expanduser()
    allowed_grades = set(parse_csv(args.allowed_grades))
    min_paper_net_bps = dec(args.min_paper_net_bps)
    default_latency_bps = dec(args.latency_bps)

    print("profit-paper-trade monitor")
    print(f"sources={','.join(f'{source.name}={source.db_path}' for source in sources)}")
    print(f"outputs={jsonl_path} {db_path}")
    print(f"status_db={args.status_db} enabled={status_conn is not None}")
    print(f"inventory_config={inventory_config} exists={inventory_config.exists()} require_inventory={args.require_inventory}")
    print("risk=paper-only public-book emulation; no private keys, no orders, no fills are placed\n")

    while True:
        run_cycle(
            conn=conn,
            jsonl_path=jsonl_path,
            sources=sources,
            adapters_by_name=adapters_by_name,
            status_conn=status_conn,
            inventory_config=inventory_config,
            min_age_sec=args.min_age_sec,
            max_age_sec=args.max_age_sec,
            limit_per_source=args.limit_per_source,
            workers=args.workers,
            allowed_grades=allowed_grades,
            quote=args.quote,
            base=args.base,
            min_paper_net_bps=min_paper_net_bps,
            default_latency_bps=default_latency_bps,
            require_inventory=args.require_inventory,
        )
        if args.once:
            break
        time.sleep(args.interval_sec)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
