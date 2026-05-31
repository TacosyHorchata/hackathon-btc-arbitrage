#!/usr/bin/env python3
"""Promote saved opportunities into persistent operational signals.

The broad and BTC monitors save every public-book route that is positive after
fees, depth walking, and latency haircut. This process is stricter: it reads
their route rollups and persists only cases that are recent, repeated, not
publicly blocked, and still net-positive enough to deserve attention.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 40

DEFAULT_LIVE_DB = Path.home() / "Library/Application Support/hackathon-btc/live/profitable_cases.sqlite"
DEFAULT_BTC_DB = Path.home() / "Library/Application Support/hackathon-btc/btc_hot_path/profitable_cases.sqlite"
DEFAULT_OUT_DIR = Path.home() / "Library/Application Support/hackathon-btc/signals"
DEFAULT_INVENTORY_CONFIG = Path.home() / "Library/Application Support/hackathon-btc/inventory.json"

DEFAULT_ALLOWED_GRADES = {
    "tradable_rebalance_public_ok",
    "tradable_rebalance_unknown",
}


@dataclass(frozen=True)
class Source:
    name: str
    db_path: Path


@dataclass(frozen=True)
class QualifiedCase:
    source_name: str
    source_db: str
    route_key: str
    mode: str
    base: str
    quote: str
    buy_exchange: str
    sell_exchange: str
    buy_symbol: str
    sell_symbol: str
    first_seen_ms: int
    last_seen_ms: int
    seen_count: int
    duration_sec: int
    max_net_bps: Decimal
    max_net_profit_quote: Decimal
    max_notional_quote: Decimal
    last_net_bps: Decimal
    last_net_profit_quote: Decimal
    last_notional_quote: Decimal
    operational_grade: str
    status_hint: str
    status_json: str
    last_base_size: Decimal | None = None
    inventory_grade: str = "inventory_unknown"
    inventory_hint: str = "inventory=unconfigured"
    executable_notional_quote: Decimal | None = None
    executable_base_size: Decimal | None = None
    executable_profit_quote: Decimal | None = None

    @property
    def signal_key(self) -> str:
        return f"{self.source_name}:{self.route_key}"

    @property
    def pair(self) -> str:
        return f"{self.base}/{self.quote}"

    @property
    def route(self) -> str:
        return f"{self.buy_exchange}->{self.sell_exchange}"


@dataclass(frozen=True)
class Inventory:
    path: str
    observed_at_ms: int
    balances: dict[str, dict[str, Decimal]]

    def available(self, exchange: str, asset: str) -> Decimal | None:
        return self.balances.get(exchange.lower(), {}).get(asset.upper())


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


def quant(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


def json_decimal_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return quant(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


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
            balances.setdefault(exchange, {})[asset] = balance_decimal(row.get("available", row.get("free", row.get("balance", "0"))))
    elif isinstance(raw_balances, dict):
        for exchange, assets in raw_balances.items():
            exchange_key = str(exchange).lower()
            if not isinstance(assets, dict):
                continue
            for asset, value in assets.items():
                balances.setdefault(exchange_key, {})[str(asset).upper()] = balance_decimal(value)

    return Inventory(path=str(path), observed_at_ms=now_ms(), balances=balances)


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


def parse_grades(value: str, allow_status_unknown: bool) -> set[str]:
    grades = {item.strip() for item in value.split(",") if item.strip()}
    if allow_status_unknown:
        grades.add("status_unknown")
    return grades


def has_table(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def init_sqlite(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS signal_cases (
            signal_key TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_db TEXT NOT NULL,
            route_key TEXT NOT NULL,
            mode TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            first_source_seen_ms INTEGER NOT NULL,
            last_source_seen_ms INTEGER NOT NULL,
            source_seen_count INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            max_net_bps TEXT NOT NULL,
            max_net_profit_quote TEXT NOT NULL,
            max_notional_quote TEXT NOT NULL,
            last_net_bps TEXT NOT NULL,
            last_net_profit_quote TEXT NOT NULL,
            last_notional_quote TEXT NOT NULL,
            last_base_size TEXT,
            operational_grade TEXT NOT NULL,
            status_hint TEXT NOT NULL,
            status_json TEXT NOT NULL,
            inventory_grade TEXT NOT NULL DEFAULT 'inventory_unknown',
            inventory_hint TEXT NOT NULL DEFAULT '',
            executable_notional_quote TEXT,
            executable_base_size TEXT,
            executable_profit_quote TEXT,
            first_signal_ms INTEGER NOT NULL,
            last_signal_ms INTEGER NOT NULL,
            signal_count INTEGER NOT NULL,
            last_reason TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS signal_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emitted_at_ms INTEGER NOT NULL,
            signal_key TEXT NOT NULL,
            source_name TEXT NOT NULL,
            route_key TEXT NOT NULL,
            pair TEXT NOT NULL,
            route TEXT NOT NULL,
            reason TEXT NOT NULL,
            source_last_seen_ms INTEGER NOT NULL,
            source_seen_count INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            max_net_bps TEXT NOT NULL,
            last_net_bps TEXT NOT NULL,
            operational_grade TEXT NOT NULL,
            status_hint TEXT NOT NULL,
            inventory_grade TEXT NOT NULL DEFAULT 'inventory_unknown',
            inventory_hint TEXT NOT NULL DEFAULT '',
            executable_notional_quote TEXT,
            executable_base_size TEXT,
            executable_profit_quote TEXT,
            payload_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS signal_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at_ms INTEGER NOT NULL,
            elapsed_ms INTEGER NOT NULL,
            sources_checked INTEGER NOT NULL,
            cases_scanned INTEGER NOT NULL,
            qualified_cases INTEGER NOT NULL,
            events_saved INTEGER NOT NULL,
            errors_json TEXT NOT NULL
        )
        """
    )
    ensure_column(conn, "signal_cases", "last_base_size", "TEXT")
    ensure_column(conn, "signal_cases", "inventory_grade", "TEXT NOT NULL DEFAULT 'inventory_unknown'")
    ensure_column(conn, "signal_cases", "inventory_hint", "TEXT NOT NULL DEFAULT ''")
    ensure_column(conn, "signal_cases", "executable_notional_quote", "TEXT")
    ensure_column(conn, "signal_cases", "executable_base_size", "TEXT")
    ensure_column(conn, "signal_cases", "executable_profit_quote", "TEXT")
    ensure_column(conn, "signal_events", "inventory_grade", "TEXT NOT NULL DEFAULT 'inventory_unknown'")
    ensure_column(conn, "signal_events", "inventory_hint", "TEXT NOT NULL DEFAULT ''")
    ensure_column(conn, "signal_events", "executable_notional_quote", "TEXT")
    ensure_column(conn, "signal_events", "executable_base_size", "TEXT")
    ensure_column(conn, "signal_events", "executable_profit_quote", "TEXT")
    conn.commit()
    return conn


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def latest_opportunity_details(conn: sqlite3.Connection, route_keys: list[str]) -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    if not has_table(conn, "opportunities"):
        return details
    for route_key in route_keys:
        row = conn.execute(
            """
            SELECT base_size, notional_quote, net_profit_quote
            FROM opportunities
            WHERE route_key = ?
            ORDER BY detected_at_ms DESC, id DESC
            LIMIT 1
            """,
            (route_key,),
        ).fetchone()
        if row is not None:
            details[route_key] = dict(row)
    return details


def fetch_source_cases(
    source: Source,
    *,
    cutoff_ms: int,
    min_seen: int,
    min_duration_sec: int,
    min_max_net_bps: Decimal,
    min_last_net_bps: Decimal,
    allowed_grades: set[str],
) -> tuple[list[QualifiedCase], int]:
    if not source.db_path.exists():
        raise FileNotFoundError(source.db_path)
    conn = sqlite3.connect(source.db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        if not has_table(conn, "opportunity_cases"):
            return [], 0
        rows = conn.execute(
            """
            SELECT
                route_key, mode, base, quote, buy_exchange, sell_exchange,
                buy_symbol, sell_symbol, first_seen_ms, last_seen_ms, seen_count,
                max_net_bps, max_net_profit_quote, max_notional_quote,
                last_net_bps, last_net_profit_quote, last_notional_quote,
                last_operational_grade, last_status_hint, last_status_json
            FROM opportunity_cases
            WHERE last_seen_ms >= ?
            """,
            (cutoff_ms,),
        ).fetchall()
        details_by_route = latest_opportunity_details(conn, [row["route_key"] for row in rows])
    finally:
        conn.close()

    qualified: list[QualifiedCase] = []
    for row in rows:
        duration_sec = int((int(row["last_seen_ms"]) - int(row["first_seen_ms"])) / 1000)
        max_net_bps = dec(row["max_net_bps"])
        last_net_bps = dec(row["last_net_bps"])
        grade = str(row["last_operational_grade"] or "")
        if int(row["seen_count"]) < min_seen:
            continue
        if duration_sec < min_duration_sec:
            continue
        if max_net_bps < min_max_net_bps or last_net_bps < min_last_net_bps:
            continue
        if grade not in allowed_grades:
            continue
        details = details_by_route.get(row["route_key"], {})
        last_base_size = dec(details["base_size"]) if details.get("base_size") is not None else None
        qualified.append(
            QualifiedCase(
                source_name=source.name,
                source_db=str(source.db_path),
                route_key=row["route_key"],
                mode=row["mode"],
                base=row["base"],
                quote=row["quote"],
                buy_exchange=row["buy_exchange"],
                sell_exchange=row["sell_exchange"],
                buy_symbol=row["buy_symbol"],
                sell_symbol=row["sell_symbol"],
                first_seen_ms=int(row["first_seen_ms"]),
                last_seen_ms=int(row["last_seen_ms"]),
                seen_count=int(row["seen_count"]),
                duration_sec=duration_sec,
                max_net_bps=max_net_bps,
                max_net_profit_quote=dec(row["max_net_profit_quote"]),
                max_notional_quote=dec(row["max_notional_quote"]),
                last_net_bps=last_net_bps,
                last_net_profit_quote=dec(row["last_net_profit_quote"]),
                last_notional_quote=dec(row["last_notional_quote"]),
                operational_grade=grade,
                status_hint=row["last_status_hint"],
                status_json=row["last_status_json"],
                last_base_size=last_base_size,
            )
        )
    return qualified, len(rows)


def apply_inventory(case: QualifiedCase, inventory: Inventory | None, inventory_path: Path) -> QualifiedCase:
    if inventory is None:
        return replace(
            case,
            inventory_grade="inventory_unknown",
            inventory_hint=f"inventory_config_missing path={inventory_path}",
        )
    if case.last_base_size is None:
        return replace(
            case,
            inventory_grade="inventory_unknown",
            inventory_hint="latest_base_size_missing",
        )

    buy_quote_available = inventory.available(case.buy_exchange, case.quote)
    sell_base_available = inventory.available(case.sell_exchange, case.base)
    required_quote = case.last_notional_quote
    required_base = case.last_base_size

    if buy_quote_available is None or sell_base_available is None:
        return replace(
            case,
            inventory_grade="inventory_unknown",
            inventory_hint=(
                f"inventory={inventory.path} "
                f"buy_quote_available={quant(buy_quote_available) if buy_quote_available is not None else '?'} "
                f"required_quote={quant(required_quote)} "
                f"sell_base_available={quant(sell_base_available) if sell_base_available is not None else '?'} "
                f"required_base={quant(required_base)}"
            ),
        )

    quote_ratio = Decimal("1") if required_quote <= 0 else buy_quote_available / required_quote
    base_ratio = Decimal("1") if required_base <= 0 else sell_base_available / required_base
    executable_ratio = max(Decimal("0"), min(Decimal("1"), quote_ratio, base_ratio))
    executable_notional = required_quote * executable_ratio
    executable_base = required_base * executable_ratio
    executable_profit = case.last_net_profit_quote * executable_ratio

    if buy_quote_available >= required_quote and sell_base_available >= required_base:
        grade = "inventory_executable"
    elif executable_ratio > 0:
        grade = "inventory_partial"
    else:
        grade = "inventory_insufficient"

    return replace(
        case,
        inventory_grade=grade,
        inventory_hint=(
            f"inventory={inventory.path} "
            f"buy_quote_available={quant(buy_quote_available)} required_quote={quant(required_quote)} "
            f"sell_base_available={quant(sell_base_available)} required_base={quant(required_base)}"
        ),
        executable_notional_quote=executable_notional,
        executable_base_size=executable_base,
        executable_profit_quote=executable_profit,
    )


def event_payload(case: QualifiedCase, emitted_at_ms: int, reason: str) -> dict[str, Any]:
    payload = asdict(case)
    payload.update(
        {
            "signal_key": case.signal_key,
            "pair": case.pair,
            "route": case.route,
            "emitted_at_ms": emitted_at_ms,
            "reason": reason,
        }
    )
    return payload


def save_event(conn: sqlite3.Connection, jsonl_path: Path, case: QualifiedCase, emitted_at_ms: int, reason: str) -> None:
    payload = event_payload(case, emitted_at_ms, reason)
    payload_json = json.dumps(payload, default=json_decimal_default, sort_keys=True)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(payload_json + "\n")
    conn.execute(
        """
        INSERT INTO signal_events (
            emitted_at_ms, signal_key, source_name, route_key, pair, route, reason,
            source_last_seen_ms, source_seen_count, duration_sec, max_net_bps,
            last_net_bps, operational_grade, status_hint, inventory_grade,
            inventory_hint, executable_notional_quote, executable_base_size,
            executable_profit_quote, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            emitted_at_ms,
            case.signal_key,
            case.source_name,
            case.route_key,
            case.pair,
            case.route,
            reason,
            case.last_seen_ms,
            case.seen_count,
            case.duration_sec,
            quant(case.max_net_bps),
            quant(case.last_net_bps),
            case.operational_grade,
            case.status_hint,
            case.inventory_grade,
            case.inventory_hint,
            quant(case.executable_notional_quote),
            quant(case.executable_base_size),
            quant(case.executable_profit_quote),
            payload_json,
        ),
    )


def upsert_signal_case(
    conn: sqlite3.Connection,
    jsonl_path: Path,
    case: QualifiedCase,
    *,
    emitted_at_ms: int,
    dedupe_window_sec: int,
    material_improvement_bps: Decimal,
) -> bool:
    existing = conn.execute(
        """
        SELECT source_seen_count, max_net_bps, operational_grade, last_signal_ms,
               signal_count, last_reason, inventory_grade
        FROM signal_cases
        WHERE signal_key = ?
        """,
        (case.signal_key,),
    ).fetchone()

    reason: str | None = None
    signal_count = 1
    if existing is None:
        reason = "new"
    else:
        prior_seen = int(existing[0])
        prior_max = dec(existing[1])
        prior_grade = str(existing[2] or "")
        prior_last_signal_ms = int(existing[3])
        signal_count = int(existing[4])
        prior_inventory_grade = str(existing[6] or "inventory_unknown")
        if case.inventory_grade != prior_inventory_grade:
            reason = "inventory_change"
        elif case.operational_grade != prior_grade:
            reason = "grade_change"
        elif case.max_net_bps >= prior_max + material_improvement_bps:
            reason = "materially_better"
        elif case.seen_count > prior_seen and emitted_at_ms - prior_last_signal_ms >= dedupe_window_sec * 1000:
            reason = "still_active"

    if reason is not None:
        save_event(conn, jsonl_path, case, emitted_at_ms, reason)
        signal_count += 0 if existing is None else 1
    elif existing is not None:
        signal_count = int(existing[4])

    first_signal_ms = emitted_at_ms if existing is None else None
    conn.execute(
        """
        INSERT INTO signal_cases (
            signal_key, source_name, source_db, route_key, mode, base, quote,
            buy_exchange, sell_exchange, buy_symbol, sell_symbol,
            first_source_seen_ms, last_source_seen_ms, source_seen_count,
            duration_sec, max_net_bps, max_net_profit_quote, max_notional_quote,
            last_net_bps, last_net_profit_quote, last_notional_quote, last_base_size,
            operational_grade, status_hint, status_json, inventory_grade, inventory_hint,
            executable_notional_quote, executable_base_size, executable_profit_quote,
            first_signal_ms, last_signal_ms, signal_count, last_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(signal_key) DO UPDATE SET
            source_db=excluded.source_db,
            first_source_seen_ms=excluded.first_source_seen_ms,
            last_source_seen_ms=excluded.last_source_seen_ms,
            source_seen_count=excluded.source_seen_count,
            duration_sec=excluded.duration_sec,
            max_net_bps=excluded.max_net_bps,
            max_net_profit_quote=excluded.max_net_profit_quote,
            max_notional_quote=excluded.max_notional_quote,
            last_net_bps=excluded.last_net_bps,
            last_net_profit_quote=excluded.last_net_profit_quote,
            last_notional_quote=excluded.last_notional_quote,
            last_base_size=excluded.last_base_size,
            operational_grade=excluded.operational_grade,
            status_hint=excluded.status_hint,
            status_json=excluded.status_json,
            inventory_grade=excluded.inventory_grade,
            inventory_hint=excluded.inventory_hint,
            executable_notional_quote=excluded.executable_notional_quote,
            executable_base_size=excluded.executable_base_size,
            executable_profit_quote=excluded.executable_profit_quote,
            last_signal_ms=excluded.last_signal_ms,
            signal_count=excluded.signal_count,
            last_reason=excluded.last_reason
        """,
        (
            case.signal_key,
            case.source_name,
            case.source_db,
            case.route_key,
            case.mode,
            case.base,
            case.quote,
            case.buy_exchange,
            case.sell_exchange,
            case.buy_symbol,
            case.sell_symbol,
            case.first_seen_ms,
            case.last_seen_ms,
            case.seen_count,
            case.duration_sec,
            quant(case.max_net_bps),
            quant(case.max_net_profit_quote),
            quant(case.max_notional_quote),
            quant(case.last_net_bps),
            quant(case.last_net_profit_quote),
            quant(case.last_notional_quote),
            quant(case.last_base_size),
            case.operational_grade,
            case.status_hint,
            case.status_json,
            case.inventory_grade,
            case.inventory_hint,
            quant(case.executable_notional_quote),
            quant(case.executable_base_size),
            quant(case.executable_profit_quote),
            first_signal_ms or emitted_at_ms,
            emitted_at_ms if reason is not None else (int(existing[3]) if existing is not None else emitted_at_ms),
            signal_count,
            reason or (str(existing[5]) if existing is not None else "seen"),
        ),
    )
    return reason is not None


def run_cycle(
    *,
    conn: sqlite3.Connection,
    jsonl_path: Path,
    sources: list[Source],
    lookback_min: float,
    min_seen: int,
    min_duration_sec: int,
    min_max_net_bps: Decimal,
    min_last_net_bps: Decimal,
    allowed_grades: set[str],
    inventory_config: Path,
    require_inventory: bool,
    dedupe_window_sec: int,
    material_improvement_bps: Decimal,
) -> None:
    started = now_ms()
    cutoff_ms = int((time.time() - lookback_min * 60) * 1000)
    cases_scanned = 0
    qualified_total = 0
    events_saved = 0
    errors: list[dict[str, str]] = []
    try:
        inventory = load_inventory(inventory_config)
    except Exception as exc:
        inventory = None
        errors.append({"source": "inventory", "path": str(inventory_config), "error": str(exc)})
        print(f"[SIGNAL_ERR] inventory: {exc}", file=sys.stderr, flush=True)

    for source in sources:
        try:
            qualified, scanned = fetch_source_cases(
                source,
                cutoff_ms=cutoff_ms,
                min_seen=min_seen,
                min_duration_sec=min_duration_sec,
                min_max_net_bps=min_max_net_bps,
                min_last_net_bps=min_last_net_bps,
                allowed_grades=allowed_grades,
            )
        except Exception as exc:
            errors.append({"source": source.name, "db": str(source.db_path), "error": str(exc)})
            print(f"[SIGNAL_ERR] {source.name}: {exc}", file=sys.stderr, flush=True)
            continue
        cases_scanned += scanned
        for case in qualified:
            case = apply_inventory(case, inventory, inventory_config)
            if require_inventory and case.inventory_grade != "inventory_executable":
                continue
            qualified_total += 1
            if upsert_signal_case(
                conn,
                jsonl_path,
                case,
                emitted_at_ms=started,
                dedupe_window_sec=dedupe_window_sec,
                material_improvement_bps=material_improvement_bps,
            ):
                events_saved += 1
                print(
                    "[SIGNAL] "
                    f"{case.source_name} {case.pair} {case.route} "
                    f"seen={case.seen_count} duration_s={case.duration_sec} "
                    f"last_bps={case.last_net_bps:.3f} max_bps={case.max_net_bps:.3f} "
                    f"grade={case.operational_grade} inventory={case.inventory_grade}",
                    flush=True,
                )

    elapsed_ms = now_ms() - started
    conn.execute(
        """
        INSERT INTO signal_cycles (
            started_at_ms, elapsed_ms, sources_checked, cases_scanned,
            qualified_cases, events_saved, errors_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (started, elapsed_ms, len(sources), cases_scanned, qualified_total, events_saved, json.dumps(errors, sort_keys=True)),
    )
    conn.commit()
    print(
        "[SIGNAL_CYCLE] "
        f"sources={len(sources)} scanned={cases_scanned} qualified={qualified_total} "
        f"events={events_saved} errors={len(errors)} elapsed_ms={elapsed_ms}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote 24/7 profit cases into persistent actionable signals")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval-sec", type=float, default=float(os.getenv("SIGNAL_MONITOR_INTERVAL_SEC", "60")))
    parser.add_argument("--out-dir", default=os.getenv("SIGNAL_MONITOR_OUT_DIR", str(DEFAULT_OUT_DIR)))
    parser.add_argument("--source", action="append", help="Source DB as name=/path/to/profitable_cases.sqlite. Repeatable.")
    parser.add_argument("--lookback-min", type=float, default=float(os.getenv("SIGNAL_MONITOR_LOOKBACK_MIN", "60")))
    parser.add_argument("--min-seen", type=int, default=int(os.getenv("SIGNAL_MONITOR_MIN_SEEN", "3")))
    parser.add_argument("--min-duration-sec", type=int, default=int(os.getenv("SIGNAL_MONITOR_MIN_DURATION_SEC", "60")))
    parser.add_argument("--min-max-net-bps", default=os.getenv("SIGNAL_MONITOR_MIN_MAX_NET_BPS", "3"))
    parser.add_argument("--min-last-net-bps", default=os.getenv("SIGNAL_MONITOR_MIN_LAST_NET_BPS", "1"))
    parser.add_argument(
        "--allowed-grades",
        default=os.getenv("SIGNAL_MONITOR_ALLOWED_GRADES", ",".join(sorted(DEFAULT_ALLOWED_GRADES))),
    )
    parser.add_argument("--allow-status-unknown", action="store_true")
    parser.add_argument("--inventory-config", default=os.getenv("SIGNAL_MONITOR_INVENTORY_CONFIG", str(DEFAULT_INVENTORY_CONFIG)))
    parser.add_argument(
        "--require-inventory",
        action="store_true",
        default=env_bool("SIGNAL_MONITOR_REQUIRE_INVENTORY", False),
        help="Only persist signals that are executable with the configured inventory.",
    )
    parser.add_argument("--dedupe-window-sec", type=int, default=int(os.getenv("SIGNAL_MONITOR_DEDUPE_WINDOW_SEC", "300")))
    parser.add_argument("--material-improvement-bps", default=os.getenv("SIGNAL_MONITOR_MATERIAL_IMPROVEMENT_BPS", "10"))
    args = parser.parse_args()

    sources = parse_sources(args.source)
    if not sources:
        raise SystemExit("No source DBs found. Start the broad/BTC monitors first or pass --source name=/path/db.sqlite")

    out_dir = Path(args.out_dir).expanduser()
    conn = init_sqlite(out_dir / "profit_signals.sqlite")
    jsonl_path = out_dir / "profit_signals.jsonl"
    allowed_grades = parse_grades(args.allowed_grades, args.allow_status_unknown)
    inventory_config = Path(args.inventory_config).expanduser()

    print("profit signal monitor")
    print(f"sources={','.join(f'{source.name}:{source.db_path}' for source in sources)}")
    print(
        "filters="
        f"lookback_min={args.lookback_min} min_seen={args.min_seen} "
        f"min_duration_sec={args.min_duration_sec} "
        f"min_max_net_bps={args.min_max_net_bps} min_last_net_bps={args.min_last_net_bps} "
        f"grades={','.join(sorted(allowed_grades))} "
        f"require_inventory={args.require_inventory}"
    )
    print(f"inventory_config={inventory_config} exists={inventory_config.exists()}")
    print(f"outputs={jsonl_path} {out_dir / 'profit_signals.sqlite'}")
    print("risk=signals are still paper/public-data only; balances and execution are not proven\n")

    while True:
        run_cycle(
            conn=conn,
            jsonl_path=jsonl_path,
            sources=sources,
            lookback_min=args.lookback_min,
            min_seen=args.min_seen,
            min_duration_sec=args.min_duration_sec,
            min_max_net_bps=dec(args.min_max_net_bps),
            min_last_net_bps=dec(args.min_last_net_bps),
            allowed_grades=allowed_grades,
            inventory_config=inventory_config,
            require_inventory=args.require_inventory,
            dedupe_window_sec=args.dedupe_window_sec,
            material_improvement_bps=dec(args.material_improvement_bps),
        )
        if args.once:
            break
        time.sleep(args.interval_sec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
