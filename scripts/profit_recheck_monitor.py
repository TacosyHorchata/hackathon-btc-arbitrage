#!/usr/bin/env python3
"""Recheck saved public-book opportunities after real elapsed latency.

The broad scanner records routes that were profitable at detection time. This
companion process turns those detections into stronger evidence: it waits until
an opportunity is old enough, walks both public order books again, and records
whether the same route/notional was still profitable.
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
    RouteCandidate,
    Opportunity,
    attach_operational_status,
    build_adapters,
    depth_check_candidate,
    json_decimal_default,
    open_status_db,
    quant,
)

getcontext().prec = 40

DEFAULT_DB = Path.home() / "Library/Application Support/hackathon-btc/live/profitable_cases.sqlite"
DEFAULT_JSONL = Path.home() / "Library/Application Support/hackathon-btc/live/profit_rechecks.jsonl"
DEFAULT_ALLOWED_GRADES = {
    "tradable_rebalance_public_ok",
    "tradable_rebalance_unknown",
    "status_unknown",
    "status_unavailable",
}


@dataclass(frozen=True)
class RecheckResult:
    source: dict[str, Any]
    rechecked_at_ms: int
    status: str
    opportunity: Opportunity | None
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


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def init_sqlite(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise SystemExit(f"DB not found: {path}")
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunity_rechecks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_opportunity_id INTEGER NOT NULL UNIQUE,
            source_detected_at_ms INTEGER NOT NULL,
            rechecked_at_ms INTEGER NOT NULL,
            elapsed_since_detection_ms INTEGER NOT NULL,
            route_key TEXT NOT NULL,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            source_notional_quote TEXT NOT NULL,
            source_net_bps TEXT NOT NULL,
            source_net_profit_quote TEXT NOT NULL,
            recheck_status TEXT NOT NULL,
            recheck_notional_quote TEXT,
            recheck_net_bps TEXT,
            recheck_net_profit_quote TEXT,
            recheck_operational_grade TEXT NOT NULL DEFAULT '',
            recheck_status_hint TEXT NOT NULL DEFAULT '',
            evidence_json TEXT NOT NULL,
            error TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunity_recheck_cases (
            route_key TEXT PRIMARY KEY,
            base TEXT NOT NULL,
            quote TEXT NOT NULL,
            buy_exchange TEXT NOT NULL,
            sell_exchange TEXT NOT NULL,
            buy_symbol TEXT NOT NULL,
            sell_symbol TEXT NOT NULL,
            first_rechecked_ms INTEGER NOT NULL,
            last_rechecked_ms INTEGER NOT NULL,
            recheck_count INTEGER NOT NULL,
            survived_count INTEGER NOT NULL,
            failed_count INTEGER NOT NULL,
            max_recheck_net_bps TEXT,
            max_recheck_net_profit_quote TEXT,
            max_recheck_notional_quote TEXT,
            last_recheck_status TEXT NOT NULL,
            last_recheck_net_bps TEXT,
            last_recheck_net_profit_quote TEXT,
            last_recheck_notional_quote TEXT,
            last_operational_grade TEXT NOT NULL,
            last_status_hint TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS recheck_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at_ms INTEGER NOT NULL,
            elapsed_ms INTEGER NOT NULL,
            candidates_total INTEGER NOT NULL,
            rechecked_total INTEGER NOT NULL,
            survived_total INTEGER NOT NULL,
            errors_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_opportunity_rechecks_route_time
        ON opportunity_rechecks(route_key, rechecked_at_ms)
        """
    )
    conn.commit()
    return conn


def fetch_pending(
    conn: sqlite3.Connection,
    *,
    limit: int,
    min_age_sec: float,
    max_age_sec: float,
    allowed_grades: set[str],
    quote: str | None,
    base: str | None,
) -> list[dict[str, Any]]:
    current_ms = now_ms()
    newest_ms = current_ms - int(min_age_sec * 1000)
    oldest_ms = current_ms - int(max_age_sec * 1000)
    where = [
        "o.detected_at_ms <= ?",
        "o.detected_at_ms >= ?",
        "r.id IS NULL",
    ]
    params: list[Any] = [newest_ms, oldest_ms]
    if allowed_grades:
        where.append(f"o.operational_grade IN ({','.join('?' for _ in allowed_grades)})")
        params.extend(sorted(allowed_grades))
    if quote:
        where.append("o.quote = ?")
        params.append(quote.upper())
    if base:
        where.append("o.base = ?")
        params.append(base.upper())

    params.append(limit)
    rows = conn.execute(
        f"""
        SELECT
            o.id, o.detected_at_ms, o.route_key, o.mode, o.base, o.quote,
            o.buy_exchange, o.sell_exchange, o.buy_symbol, o.sell_symbol,
            o.notional_quote, o.base_size, o.buy_avg, o.sell_avg,
            o.net_bps, o.net_profit_quote, o.gross_bps, o.top_net_bps,
            o.operational_grade, o.status_hint, o.evidence_json
        FROM opportunities o
        LEFT JOIN opportunity_rechecks r
            ON r.source_opportunity_id = o.id
            AND r.recheck_status != 'error'
        WHERE {' AND '.join(where)}
        ORDER BY o.detected_at_ms DESC
        LIMIT ?
        """,
        params,
    ).fetchall()
    return [dict(row) for row in rows]


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

    gross_bps = optional_dec(raw_candidate.get("gross_bps"))
    if gross_bps is None:
        gross_bps = dec(source["gross_bps"])
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


def recheck_source(
    source: dict[str, Any],
    adapters_by_name: dict[str, Any],
    min_recheck_net_bps: Decimal,
    default_latency_bps: Decimal,
) -> RecheckResult:
    rechecked_at_ms = now_ms()
    try:
        if source["buy_exchange"] not in adapters_by_name or source["sell_exchange"] not in adapters_by_name:
            missing = [
                name
                for name in (source["buy_exchange"], source["sell_exchange"])
                if name not in adapters_by_name
            ]
            return RecheckResult(
                source=source,
                rechecked_at_ms=rechecked_at_ms,
                status="adapter_missing",
                opportunity=None,
                evidence={"missing_adapters": missing},
                error="adapter_missing",
            )

        candidate = candidate_from_source(source, default_latency_bps)
        opportunity, evidence = depth_check_candidate(
            candidate,
            adapters_by_name,
            [dec(source["notional_quote"])],
            min_recheck_net_bps,
        )
        if opportunity is None:
            status = "not_profitable"
            if evidence.get("error"):
                status = str(evidence["error"])
            return RecheckResult(
                source=source,
                rechecked_at_ms=now_ms(),
                status=status,
                opportunity=None,
                evidence=evidence,
            )

        return RecheckResult(
            source=source,
            rechecked_at_ms=opportunity.detected_at_ms,
            status="survived",
            opportunity=opportunity,
            evidence=evidence,
        )
    except Exception as exc:
        return RecheckResult(
            source=source,
            rechecked_at_ms=now_ms(),
            status="error",
            opportunity=None,
            evidence={},
            error=str(exc),
        )


def update_recheck_case(conn: sqlite3.Connection, result: RecheckResult) -> None:
    source = result.source
    opportunity = result.opportunity
    survived = opportunity is not None and result.status == "survived"
    existing = conn.execute(
        """
        SELECT recheck_count, survived_count, failed_count,
               max_recheck_net_bps, max_recheck_net_profit_quote, max_recheck_notional_quote
        FROM opportunity_recheck_cases
        WHERE route_key = ?
        """,
        (source["route_key"],),
    ).fetchone()

    last_net_bps = quant(opportunity.net_bps) if opportunity else None
    last_profit = quant(opportunity.net_profit_quote) if opportunity else None
    last_notional = quant(opportunity.notional_quote) if opportunity else None
    last_grade = opportunity.operational_grade if opportunity else ""
    last_hint = opportunity.status_hint if opportunity else ""

    if existing is None:
        conn.execute(
            """
            INSERT INTO opportunity_recheck_cases (
                route_key, base, quote, buy_exchange, sell_exchange,
                buy_symbol, sell_symbol, first_rechecked_ms, last_rechecked_ms,
                recheck_count, survived_count, failed_count,
                max_recheck_net_bps, max_recheck_net_profit_quote, max_recheck_notional_quote,
                last_recheck_status, last_recheck_net_bps, last_recheck_net_profit_quote,
                last_recheck_notional_quote, last_operational_grade, last_status_hint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source["route_key"],
                source["base"],
                source["quote"],
                source["buy_exchange"],
                source["sell_exchange"],
                source["buy_symbol"],
                source["sell_symbol"],
                result.rechecked_at_ms,
                result.rechecked_at_ms,
                1,
                1 if survived else 0,
                0 if survived else 1,
                last_net_bps,
                last_profit,
                last_notional,
                result.status,
                last_net_bps,
                last_profit,
                last_notional,
                last_grade,
                last_hint,
            ),
        )
        return

    (
        recheck_count,
        survived_count,
        failed_count,
        max_net_bps,
        max_profit,
        max_notional,
    ) = existing
    is_new_max = False
    if survived:
        is_new_max = max_net_bps is None or opportunity.net_bps > dec(max_net_bps)

    conn.execute(
        """
        UPDATE opportunity_recheck_cases
        SET
            last_rechecked_ms = ?,
            recheck_count = ?,
            survived_count = ?,
            failed_count = ?,
            max_recheck_net_bps = ?,
            max_recheck_net_profit_quote = ?,
            max_recheck_notional_quote = ?,
            last_recheck_status = ?,
            last_recheck_net_bps = ?,
            last_recheck_net_profit_quote = ?,
            last_recheck_notional_quote = ?,
            last_operational_grade = ?,
            last_status_hint = ?
        WHERE route_key = ?
        """,
        (
            result.rechecked_at_ms,
            int(recheck_count) + 1,
            int(survived_count) + (1 if survived else 0),
            int(failed_count) + (0 if survived else 1),
            quant(opportunity.net_bps) if is_new_max and opportunity else max_net_bps,
            quant(opportunity.net_profit_quote) if is_new_max and opportunity else max_profit,
            quant(opportunity.notional_quote) if is_new_max and opportunity else max_notional,
            result.status,
            last_net_bps,
            last_profit,
            last_notional,
            last_grade,
            last_hint,
            source["route_key"],
        ),
    )


def save_result(conn: sqlite3.Connection, jsonl_path: Path, result: RecheckResult) -> None:
    source = result.source
    opportunity = result.opportunity
    elapsed_ms = result.rechecked_at_ms - int(source["detected_at_ms"])
    evidence = {
        "source": source,
        "recheck": {
            "status": result.status,
            "opportunity": asdict(opportunity) if opportunity else None,
            "evidence": result.evidence,
            "error": result.error,
        },
    }
    row = {
        "source_opportunity_id": source["id"],
        "source_detected_at_ms": source["detected_at_ms"],
        "rechecked_at_ms": result.rechecked_at_ms,
        "elapsed_since_detection_ms": elapsed_ms,
        "route_key": source["route_key"],
        "base": source["base"],
        "quote": source["quote"],
        "buy_exchange": source["buy_exchange"],
        "sell_exchange": source["sell_exchange"],
        "source_notional_quote": source["notional_quote"],
        "source_net_bps": source["net_bps"],
        "source_net_profit_quote": source["net_profit_quote"],
        "recheck_status": result.status,
        "recheck_notional_quote": quant(opportunity.notional_quote) if opportunity else None,
        "recheck_net_bps": quant(opportunity.net_bps) if opportunity else None,
        "recheck_net_profit_quote": quant(opportunity.net_profit_quote) if opportunity else None,
        "error": result.error,
    }

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, default=json_decimal_default, sort_keys=True) + "\n")

    conn.execute(
        """
        INSERT OR REPLACE INTO opportunity_rechecks (
            source_opportunity_id, source_detected_at_ms, rechecked_at_ms,
            elapsed_since_detection_ms, route_key, base, quote, buy_exchange,
            sell_exchange, buy_symbol, sell_symbol, source_notional_quote,
            source_net_bps, source_net_profit_quote, recheck_status,
            recheck_notional_quote, recheck_net_bps, recheck_net_profit_quote,
            recheck_operational_grade, recheck_status_hint, evidence_json, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source["id"],
            source["detected_at_ms"],
            result.rechecked_at_ms,
            elapsed_ms,
            source["route_key"],
            source["base"],
            source["quote"],
            source["buy_exchange"],
            source["sell_exchange"],
            source["buy_symbol"],
            source["sell_symbol"],
            source["notional_quote"],
            source["net_bps"],
            source["net_profit_quote"],
            result.status,
            quant(opportunity.notional_quote) if opportunity else None,
            quant(opportunity.net_bps) if opportunity else None,
            quant(opportunity.net_profit_quote) if opportunity else None,
            opportunity.operational_grade if opportunity else "",
            opportunity.status_hint if opportunity else "",
            json.dumps(evidence, default=json_decimal_default, sort_keys=True),
            result.error,
        ),
    )
    if result.status != "error":
        update_recheck_case(conn, result)
    conn.commit()


def save_cycle(
    conn: sqlite3.Connection,
    *,
    started_at_ms: int,
    elapsed_ms: int,
    candidates_total: int,
    rechecked_total: int,
    survived_total: int,
    errors: list[dict[str, str]],
) -> None:
    conn.execute(
        """
        INSERT INTO recheck_cycles (
            started_at_ms, elapsed_ms, candidates_total,
            rechecked_total, survived_total, errors_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            started_at_ms,
            elapsed_ms,
            candidates_total,
            rechecked_total,
            survived_total,
            json.dumps(errors, sort_keys=True),
        ),
    )
    conn.commit()


def run_cycle(
    *,
    conn: sqlite3.Connection,
    jsonl_path: Path,
    adapters_by_name: dict[str, Any],
    status_conn: sqlite3.Connection | None,
    min_age_sec: float,
    max_age_sec: float,
    limit: int,
    workers: int,
    allowed_grades: set[str],
    quote: str | None,
    base: str | None,
    min_recheck_net_bps: Decimal,
    default_latency_bps: Decimal,
) -> None:
    started = now_ms()
    sources = fetch_pending(
        conn,
        limit=limit,
        min_age_sec=min_age_sec,
        max_age_sec=max_age_sec,
        allowed_grades=allowed_grades,
        quote=quote,
        base=base,
    )
    rechecked = 0
    survived = 0
    errors: list[dict[str, str]] = []

    if sources:
        max_workers = max(1, min(len(sources), workers))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    recheck_source,
                    source,
                    adapters_by_name,
                    min_recheck_net_bps,
                    default_latency_bps,
                )
                for source in sources
            ]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.opportunity is not None:
                    result = replace(
                        result,
                        opportunity=attach_operational_status(result.opportunity, status_conn),
                    )
                rechecked += 1
                if result.error:
                    errors.append({"route_key": result.source["route_key"], "error": result.error})
                if result.status == "survived":
                    survived += 1
                save_result(conn, jsonl_path, result)
                print(
                    "[RECHECK] "
                    f"{result.status} {result.source['route_key']} "
                    f"elapsed_ms={result.rechecked_at_ms - int(result.source['detected_at_ms'])} "
                    f"source_bps={result.source['net_bps']} "
                    f"recheck_bps={quant(result.opportunity.net_bps) if result.opportunity else ''}",
                    flush=True,
                )

    elapsed = now_ms() - started
    save_cycle(
        conn,
        started_at_ms=started,
        elapsed_ms=elapsed,
        candidates_total=len(sources),
        rechecked_total=rechecked,
        survived_total=survived,
        errors=errors,
    )
    print(
        "[RECHECK_CYCLE] "
        f"candidates={len(sources)} rechecked={rechecked} survived={survived} "
        f"errors={len(errors)} elapsed_ms={elapsed}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Recheck saved profit-monitor opportunities after elapsed latency")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--db", default=os.getenv("PROFIT_RECHECK_DB", str(DEFAULT_DB)))
    parser.add_argument("--jsonl", default=os.getenv("PROFIT_RECHECK_JSONL", str(DEFAULT_JSONL)))
    parser.add_argument("--interval-sec", type=float, default=float(os.getenv("PROFIT_RECHECK_INTERVAL_SEC", "10")))
    parser.add_argument("--min-age-sec", type=float, default=float(os.getenv("PROFIT_RECHECK_MIN_AGE_SEC", "5")))
    parser.add_argument("--max-age-sec", type=float, default=float(os.getenv("PROFIT_RECHECK_MAX_AGE_SEC", "3600")))
    parser.add_argument("--limit", type=int, default=env_int("PROFIT_RECHECK_LIMIT", 20))
    parser.add_argument("--workers", type=int, default=env_int("PROFIT_RECHECK_WORKERS", 6))
    parser.add_argument("--min-recheck-net-bps", default=os.getenv("PROFIT_RECHECK_MIN_NET_BPS", "1"))
    parser.add_argument("--latency-bps", default=os.getenv("PROFIT_RECHECK_LATENCY_BPS", "2"))
    parser.add_argument("--allowed-grades", default=os.getenv("PROFIT_RECHECK_ALLOWED_GRADES", ",".join(sorted(DEFAULT_ALLOWED_GRADES))))
    parser.add_argument("--quote")
    parser.add_argument("--base")
    parser.add_argument("--status-db", default=os.getenv("PROFIT_RECHECK_STATUS_DB", str(DEFAULT_STATUS_DB)))
    args = parser.parse_args()

    db_path = Path(args.db).expanduser()
    conn = init_sqlite(db_path)
    jsonl_path = Path(args.jsonl).expanduser()
    status_conn = open_status_db(Path(args.status_db).expanduser())
    adapters_by_name = build_adapters()
    allowed_grades = set(parse_csv(args.allowed_grades))

    print("profit-recheck monitor")
    print(f"db={db_path} jsonl={jsonl_path}")
    print(f"age_window_sec={args.min_age_sec}-{args.max_age_sec} limit={args.limit} workers={args.workers}")
    print(f"allowed_grades={','.join(sorted(allowed_grades)) if allowed_grades else 'all'}")
    print(f"status_db={args.status_db} enabled={status_conn is not None}\n")

    while True:
        run_cycle(
            conn=conn,
            jsonl_path=jsonl_path,
            adapters_by_name=adapters_by_name,
            status_conn=status_conn,
            min_age_sec=args.min_age_sec,
            max_age_sec=args.max_age_sec,
            limit=args.limit,
            workers=args.workers,
            allowed_grades=allowed_grades,
            quote=args.quote,
            base=args.base,
            min_recheck_net_bps=Decimal(args.min_recheck_net_bps),
            default_latency_bps=Decimal(args.latency_bps),
        )
        if args.once:
            break
        time.sleep(max(args.interval_sec, 1.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
