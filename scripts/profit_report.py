#!/usr/bin/env python3
"""Read saved public-book profitable cases from the 24/7 monitor."""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_DB = Path.home() / "Library/Application Support/hackathon-btc/live/profitable_cases.sqlite"
DEFAULT_STATUS_DB = Path.home() / "Library/Application Support/hackathon-btc/status/status.sqlite"
DEFAULT_PAPER_DB = Path.home() / "Library/Application Support/hackathon-btc/paper_trades/paper_trades.sqlite"


def ms_to_local(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S")


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def build_query(args: argparse.Namespace, columns: set[str]) -> tuple[str, list[Any]]:
    where: list[str] = []
    params: list[Any] = []
    if args.since_min is not None:
        where.append("detected_at_ms >= ?")
        params.append(int((time.time() - args.since_min * 60) * 1000))
    if args.quote:
        where.append("quote = ?")
        params.append(args.quote.upper())
    if args.base:
        where.append("base = ?")
        params.append(args.base.upper())
    if args.buy_exchange:
        where.append("buy_exchange = ?")
        params.append(args.buy_exchange.lower())
    if args.sell_exchange:
        where.append("sell_exchange = ?")
        params.append(args.sell_exchange.lower())
    if args.min_net_bps is not None:
        where.append("CAST(net_bps AS REAL) >= ?")
        params.append(args.min_net_bps)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    selected = [
        "detected_at_ms",
        "base",
        "quote",
        "buy_exchange",
        "sell_exchange",
        "buy_symbol",
        "sell_symbol",
        "notional_quote",
        "net_profit_quote",
        "net_bps",
        "gross_bps",
        "buy_levels",
        "sell_levels",
        "mode",
    ]
    for optional in ("operational_grade", "status_hint", "status_json"):
        if optional in columns:
            selected.append(optional)
    sql = f"""
        SELECT {', '.join(selected)}
        FROM opportunities
        {where_sql}
        ORDER BY detected_at_ms DESC
        LIMIT ?
    """
    params.append(args.limit)
    return sql, params


def build_cases_query(args: argparse.Namespace) -> tuple[str, list[Any]]:
    where: list[str] = []
    params: list[Any] = []
    if args.since_min is not None:
        where.append("last_seen_ms >= ?")
        params.append(int((time.time() - args.since_min * 60) * 1000))
    if args.quote:
        where.append("quote = ?")
        params.append(args.quote.upper())
    if args.base:
        where.append("base = ?")
        params.append(args.base.upper())
    if args.buy_exchange:
        where.append("buy_exchange = ?")
        params.append(args.buy_exchange.lower())
    if args.sell_exchange:
        where.append("sell_exchange = ?")
        params.append(args.sell_exchange.lower())
    if args.min_net_bps is not None:
        where.append("CAST(max_net_bps AS REAL) >= ?")
        params.append(args.min_net_bps)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT
            route_key, base, quote, buy_exchange, sell_exchange, buy_symbol, sell_symbol,
            first_seen_ms, last_seen_ms, seen_count, max_net_bps,
            max_net_profit_quote, max_notional_quote, last_net_bps,
            last_net_profit_quote, last_notional_quote, last_operational_grade,
            last_status_hint
        FROM opportunity_cases
        {where_sql}
        ORDER BY last_seen_ms DESC
        LIMIT ?
    """
    params.append(args.limit)
    return sql, params


def build_rechecks_query(args: argparse.Namespace) -> tuple[str, list[Any]]:
    where: list[str] = []
    params: list[Any] = []
    if args.since_min is not None:
        where.append("last_rechecked_ms >= ?")
        params.append(int((time.time() - args.since_min * 60) * 1000))
    if args.quote:
        where.append("quote = ?")
        params.append(args.quote.upper())
    if args.base:
        where.append("base = ?")
        params.append(args.base.upper())
    if args.buy_exchange:
        where.append("buy_exchange = ?")
        params.append(args.buy_exchange.lower())
    if args.sell_exchange:
        where.append("sell_exchange = ?")
        params.append(args.sell_exchange.lower())
    if args.min_net_bps is not None:
        where.append("CAST(max_recheck_net_bps AS REAL) >= ?")
        params.append(args.min_net_bps)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT
            route_key, base, quote, buy_exchange, sell_exchange, buy_symbol, sell_symbol,
            first_rechecked_ms, last_rechecked_ms, recheck_count, survived_count,
            failed_count, max_recheck_net_bps, max_recheck_net_profit_quote,
            max_recheck_notional_quote, last_recheck_status, last_recheck_net_bps,
            last_recheck_net_profit_quote, last_recheck_notional_quote,
            last_operational_grade, last_status_hint
        FROM opportunity_recheck_cases
        {where_sql}
        ORDER BY last_rechecked_ms DESC
        LIMIT ?
    """
    params.append(args.limit)
    return sql, params


def build_paper_query(args: argparse.Namespace) -> tuple[str, list[Any]]:
    where: list[str] = []
    params: list[Any] = []
    if args.since_min is not None:
        where.append("papered_at_ms >= ?")
        params.append(int((time.time() - args.since_min * 60) * 1000))
    if args.quote:
        where.append("quote = ?")
        params.append(args.quote.upper())
    if args.base:
        where.append("base = ?")
        params.append(args.base.upper())
    if args.buy_exchange:
        where.append("buy_exchange = ?")
        params.append(args.buy_exchange.lower())
    if args.sell_exchange:
        where.append("sell_exchange = ?")
        params.append(args.sell_exchange.lower())
    if args.min_net_bps is not None:
        where.append("CAST(net_bps AS REAL) >= ?")
        params.append(args.min_net_bps)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT
            source_name, source_opportunity_id, source_detected_at_ms,
            papered_at_ms, elapsed_since_detection_ms, route_key, mode,
            base, quote, buy_exchange, sell_exchange, buy_symbol, sell_symbol,
            requested_notional_quote, source_net_bps, paper_status, proof_type,
            notional_quote, base_size, buy_avg, sell_avg, buy_quote, sell_quote,
            buy_fee_quote, sell_fee_quote, latency_haircut_quote,
            net_profit_quote, net_bps, gross_bps, buy_levels, sell_levels,
            operational_grade, status_hint, inventory_grade, inventory_hint,
            executable_notional_quote, executable_base_size, executable_profit_quote,
            error
        FROM paper_trades
        {where_sql}
        ORDER BY papered_at_ms DESC
        LIMIT ?
    """
    params.append(args.limit)
    return sql, params


def build_paper_cases_query(args: argparse.Namespace) -> tuple[str, list[Any]]:
    where: list[str] = []
    params: list[Any] = []
    if args.since_min is not None:
        where.append("last_paper_ms >= ?")
        params.append(int((time.time() - args.since_min * 60) * 1000))
    if args.quote:
        where.append("quote = ?")
        params.append(args.quote.upper())
    if args.base:
        where.append("base = ?")
        params.append(args.base.upper())
    if args.buy_exchange:
        where.append("buy_exchange = ?")
        params.append(args.buy_exchange.lower())
    if args.sell_exchange:
        where.append("sell_exchange = ?")
        params.append(args.sell_exchange.lower())
    if args.min_net_bps is not None:
        where.append("CAST(max_net_bps AS REAL) >= ?")
        params.append(args.min_net_bps)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT
            source_name, route_key, base, quote, buy_exchange, sell_exchange,
            buy_symbol, sell_symbol, first_paper_ms, last_paper_ms,
            attempt_count, profitable_count, failed_count,
            inventory_executable_count, max_net_bps, max_net_profit_quote,
            max_notional_quote, last_paper_status, last_net_bps,
            last_net_profit_quote, last_notional_quote, last_operational_grade,
            last_status_hint, last_inventory_grade, last_inventory_hint
        FROM paper_trade_cases
        {where_sql}
        ORDER BY last_paper_ms DESC
        LIMIT ?
    """
    params.append(args.limit)
    return sql, params


def print_table(rows: list[sqlite3.Row]) -> None:
    if not rows:
        print("No saved opportunities matched.")
        return

    headers = ["time", "pair", "route", "notional", "net", "net_bps", "levels"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        print(
            " | ".join(
                [
                    ms_to_local(row["detected_at_ms"]),
                    f"{row['base']}/{row['quote']}",
                    f"{row['buy_exchange']}->{row['sell_exchange']}",
                    f"{row['notional_quote']} {row['quote']}",
                    f"{row['net_profit_quote']} {row['quote']}",
                    row["net_bps"],
                    f"{row['buy_levels']}/{row['sell_levels']}",
                ]
            )
        )


def status_symbol(conn: sqlite3.Connection, exchange: str, symbol: str) -> str:
    row = conn.execute(
        """
        SELECT tradable, status
        FROM symbol_status
        WHERE exchange = ? AND (symbol = ? OR UPPER(symbol) = UPPER(?))
        LIMIT 1
        """,
        (exchange, symbol, symbol),
    ).fetchone()
    if row is None:
        return "?"
    if row["tradable"] == 1:
        return "T"
    if row["tradable"] == 0:
        return f"BLOCKED:{row['status']}"
    return f"?:{row['status']}"


def status_asset(conn: sqlite3.Connection, exchange: str, asset: str, field: str) -> str:
    rows = conn.execute(
        f"""
        SELECT {field}
        FROM asset_status
        WHERE exchange = ? AND asset = ?
        """,
        (exchange, asset),
    ).fetchall()
    if not rows:
        return "?"
    values = [row[field] for row in rows if row[field] is not None]
    if not values:
        return "?"
    return "Y" if any(value == 1 for value in values) else "N"


def annotate_rows(rows: list[sqlite3.Row], status_conn: sqlite3.Connection | None) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if item.get("operational_grade") and item.get("operational_grade") != "status_unavailable" and item.get("status_hint"):
            item["grade"] = item["operational_grade"]
            item["status_hint"] = item.get("status_hint") or ""
        elif status_conn is not None:
            buy_trade = status_symbol(status_conn, row["buy_exchange"], row["buy_symbol"])
            sell_trade = status_symbol(status_conn, row["sell_exchange"], row["sell_symbol"])
            quote_deposit = status_asset(status_conn, row["buy_exchange"], row["quote"], "deposit_enabled")
            base_withdraw = status_asset(status_conn, row["sell_exchange"], row["base"], "withdraw_enabled")
            item["status_hint"] = f"trade={buy_trade}/{sell_trade} quote_dep={quote_deposit} base_wd={base_withdraw}"
            if "BLOCKED:" in item["status_hint"] or "quote_dep=N" in item["status_hint"] or "base_wd=N" in item["status_hint"]:
                item["grade"] = "blocked_or_rebalance_blocked"
            elif "trade=T/T" in item["status_hint"]:
                item["grade"] = "tradable_rebalance_unknown"
            else:
                item["grade"] = "status_unknown"
        else:
            item["status_hint"] = ""
            item["grade"] = ""
        annotated.append(item)
    return annotated


def print_status_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("No saved opportunities matched.")
        return

    headers = ["time", "pair", "route", "grade", "status", "notional", "net", "net_bps", "levels"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        print(
            " | ".join(
                [
                    ms_to_local(row["detected_at_ms"]),
                    f"{row['base']}/{row['quote']}",
                    f"{row['buy_exchange']}->{row['sell_exchange']}",
                    row["grade"],
                    row["status_hint"],
                    f"{row['notional_quote']} {row['quote']}",
                    f"{row['net_profit_quote']} {row['quote']}",
                    row["net_bps"],
                    f"{row['buy_levels']}/{row['sell_levels']}",
                ]
            )
        )


def print_cases(rows: list[sqlite3.Row]) -> None:
    if not rows:
        print("No saved cases matched.")
        return
    headers = ["last_seen", "pair", "route", "grade", "seen", "duration_s", "max_bps", "last_bps", "status"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        duration_s = int((row["last_seen_ms"] - row["first_seen_ms"]) / 1000)
        print(
            " | ".join(
                [
                    ms_to_local(row["last_seen_ms"]),
                    f"{row['base']}/{row['quote']}",
                    f"{row['buy_exchange']}->{row['sell_exchange']}",
                    row["last_operational_grade"],
                    str(row["seen_count"]),
                    str(duration_s),
                    row["max_net_bps"],
                    row["last_net_bps"],
                    row["last_status_hint"],
                ]
            )
        )


def print_rechecks(rows: list[sqlite3.Row]) -> None:
    if not rows:
        print("No rechecked cases matched.")
        return
    headers = ["last_recheck", "pair", "route", "survival", "last", "max_bps", "last_bps", "grade", "status"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        total = int(row["recheck_count"])
        survived = int(row["survived_count"])
        survival = f"{survived}/{total}"
        print(
            " | ".join(
                [
                    ms_to_local(row["last_rechecked_ms"]),
                    f"{row['base']}/{row['quote']}",
                    f"{row['buy_exchange']}->{row['sell_exchange']}",
                    survival,
                    row["last_recheck_status"],
                    row["max_recheck_net_bps"] or "",
                    row["last_recheck_net_bps"] or "",
                    row["last_operational_grade"] or "",
                    row["last_status_hint"] or "",
                ]
            )
        )


def print_paper(rows: list[sqlite3.Row]) -> None:
    if not rows:
        print("No paper trades matched.")
        return
    headers = ["papered", "source", "pair", "route", "status", "net", "net_bps", "source_bps", "inventory", "elapsed_s"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        elapsed_s = int(row["elapsed_since_detection_ms"] / 1000)
        print(
            " | ".join(
                [
                    ms_to_local(row["papered_at_ms"]),
                    row["source_name"],
                    f"{row['base']}/{row['quote']}",
                    f"{row['buy_exchange']}->{row['sell_exchange']}",
                    row["paper_status"],
                    f"{row['net_profit_quote'] or ''} {row['quote']}",
                    row["net_bps"] or "",
                    row["source_net_bps"],
                    row["inventory_grade"],
                    str(elapsed_s),
                ]
            )
        )


def print_paper_cases(rows: list[sqlite3.Row]) -> None:
    if not rows:
        print("No paper trade cases matched.")
        return
    headers = ["last_paper", "source", "pair", "route", "profit", "attempts", "inv_exec", "max_bps", "last_bps", "last_net", "inventory"]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        attempts = int(row["attempt_count"])
        profitable = int(row["profitable_count"])
        print(
            " | ".join(
                [
                    ms_to_local(row["last_paper_ms"]),
                    row["source_name"],
                    f"{row['base']}/{row['quote']}",
                    f"{row['buy_exchange']}->{row['sell_exchange']}",
                    f"{profitable}/{attempts}",
                    str(attempts),
                    str(row["inventory_executable_count"]),
                    row["max_net_bps"] or "",
                    row["last_net_bps"] or "",
                    f"{row['last_net_profit_quote'] or ''} {row['quote']}",
                    row["last_inventory_grade"],
                ]
            )
        )


def print_csv(rows: list[sqlite3.Row]) -> None:
    writer = csv.writer(sys.stdout)
    if not rows:
        return
    writer.writerow(rows[0].keys())
    for row in rows:
        writer.writerow([row[key] for key in row.keys()])


def print_summary(conn: sqlite3.Connection) -> None:
    cycles = conn.execute("SELECT COUNT(*) FROM monitor_cycles").fetchone()[0]
    opportunities = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    rechecks = None
    if "opportunity_rechecks" in tables:
        rechecks = conn.execute("SELECT COUNT(*) FROM opportunity_rechecks").fetchone()[0]
    last_cycle = conn.execute(
        """
        SELECT started_at_ms, elapsed_ms, markets_total, candidates_total,
               depth_checked, opportunities_saved, errors_json
        FROM monitor_cycles
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    summary = f"cycles={cycles} opportunities={opportunities}"
    if rechecks is not None:
        summary += f" rechecks={rechecks}"
    print(summary)
    if last_cycle:
        print(
            "last_cycle="
            f"{ms_to_local(last_cycle['started_at_ms'])} "
            f"elapsed_ms={last_cycle['elapsed_ms']} "
            f"markets={last_cycle['markets_total']} "
            f"candidates={last_cycle['candidates_total']} "
            f"depth_checked={last_cycle['depth_checked']} "
            f"saved={last_cycle['opportunities_saved']} "
            f"errors={last_cycle['errors_json']}"
        )


def print_paper_summary(conn: sqlite3.Connection) -> None:
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "paper_trades" not in tables:
        print("paper_trades=0")
        return
    trades, profitable, inventory_exec = conn.execute(
        """
        SELECT
            COUNT(*),
            SUM(CASE WHEN paper_status = 'paper_profitable' THEN 1 ELSE 0 END),
            SUM(CASE WHEN inventory_grade = 'inventory_executable' THEN 1 ELSE 0 END)
        FROM paper_trades
        """
    ).fetchone()
    cycles = conn.execute("SELECT COUNT(*) FROM paper_trade_cycles").fetchone()[0] if "paper_trade_cycles" in tables else 0
    cases = conn.execute("SELECT COUNT(*) FROM paper_trade_cases").fetchone()[0] if "paper_trade_cases" in tables else 0
    print(f"paper_trades={trades} profitable={profitable or 0} inventory_executable={inventory_exec or 0} cases={cases} cycles={cycles}")
    if "paper_trade_cycles" in tables:
        last_cycle = conn.execute(
            """
            SELECT started_at_ms, elapsed_ms, candidates_total, papered_total,
                   profitable_total, inventory_executable_total, errors_json
            FROM paper_trade_cycles
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        if last_cycle:
            print(
                "last_paper_cycle="
                f"{ms_to_local(last_cycle['started_at_ms'])} "
                f"elapsed_ms={last_cycle['elapsed_ms']} "
                f"candidates={last_cycle['candidates_total']} "
                f"papered={last_cycle['papered_total']} "
                f"profitable={last_cycle['profitable_total']} "
                f"inventory_executable={last_cycle['inventory_executable_total']} "
                f"errors={last_cycle['errors_json']}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Report saved 24/7 profit-monitor opportunities")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--since-min", type=float)
    parser.add_argument("--quote")
    parser.add_argument("--base")
    parser.add_argument("--buy-exchange")
    parser.add_argument("--sell-exchange")
    parser.add_argument("--min-net-bps", type=float)
    parser.add_argument("--status-db", default=str(DEFAULT_STATUS_DB))
    parser.add_argument("--paper", action="store_true", help="Read paper-trade ledger instead of opportunity DB")
    parser.add_argument("--paper-db", default=str(DEFAULT_PAPER_DB))
    parser.add_argument("--no-status", action="store_true")
    parser.add_argument("--cases", action="store_true", help="Show grouped route cases instead of individual events")
    parser.add_argument("--rechecks", action="store_true", help="Show grouped post-latency recheck cases")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--no-summary", action="store_true")
    args = parser.parse_args()

    db_path = Path(args.paper_db if args.paper else args.db).expanduser()
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    if args.paper:
        if not args.no_summary and not args.csv:
            print_paper_summary(conn)
            print()
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if args.cases:
            if "paper_trade_cases" not in tables:
                print("No paper_trade_cases table in this DB yet.")
                return 0
            sql, params = build_paper_cases_query(args)
            rows = conn.execute(sql, params).fetchall()
            if args.csv:
                print_csv(rows)
            else:
                print_paper_cases(rows)
            return 0
        if "paper_trades" not in tables:
            print("No paper_trades table in this DB yet.")
            return 0
        sql, params = build_paper_query(args)
        rows = conn.execute(sql, params).fetchall()
        if args.csv:
            print_csv(rows)
        else:
            print_paper(rows)
        return 0

    if not args.no_summary and not args.csv:
        print_summary(conn)
        print()

    if args.cases:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "opportunity_cases" not in tables:
            print("No opportunity_cases table in this DB yet.")
            return 0
        sql, params = build_cases_query(args)
        rows = conn.execute(sql, params).fetchall()
        if args.csv:
            print_csv(rows)
        else:
            print_cases(rows)
        return 0

    if args.rechecks:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "opportunity_recheck_cases" not in tables:
            print("No opportunity_recheck_cases table in this DB yet.")
            return 0
        sql, params = build_rechecks_query(args)
        rows = conn.execute(sql, params).fetchall()
        if args.csv:
            print_csv(rows)
        else:
            print_rechecks(rows)
        return 0

    columns = table_columns(conn, "opportunities")
    sql, params = build_query(args, columns)
    rows = conn.execute(sql, params).fetchall()
    if args.csv:
        print_csv(rows)
    else:
        status_conn = None
        status_path = Path(args.status_db).expanduser()
        if not args.no_status and status_path.exists():
            status_conn = sqlite3.connect(status_path, timeout=30)
            status_conn.row_factory = sqlite3.Row
            status_conn.execute("PRAGMA busy_timeout = 30000")
        if status_conn is None:
            print_table(rows)
        else:
            print_status_table(annotate_rows(rows, status_conn))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
