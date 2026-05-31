# Crypto Arbitrage Engine MVP

> ## Coding Challenge Mexico deliverable: the full-stack web app is in [`app/`](app/README.md)
>
> ```bash
> python3 app/server.py     # open http://localhost:8080
> ```
>
> A deployable web dashboard with live order-book monitoring, net-profit
> arbitrage detection (depth-aware VWAP, fees, slippage, latency), simulated
> execution, wallet accounting, a decision inspector, and live P&L visualization.
> Stdlib-only Python backend + zero-build static frontend. Deploy via the
> included `Dockerfile` / `render.yaml` / `Procfile`. See [app/README.md](app/README.md).

---

Rust public-market scanner for cross-exchange spot arbitrage.

Current scope:

- Public WebSocket feeds only, no private keys.
- USD lane: Coinbase/Kraken/Gemini for `BTC`, `ETH`, `SOL` where supported.
- USDT lane: Binance/Bybit/OKX for `BTC`, `ETH`, `SOL`, `XRP`, `DOGE`, `LTC`.
- Fixed-point math: quote price and notional at `1e-8`, base size at `1e-8`.
- Event-driven affected-route scanning.
- Depth-aware VWAP for executable size.
- Per-exchange taker fees and latency buffer applied before net profit.
- Stale/crossed book rejection.

## Run

```bash
cargo run
```

Optional quieter run:

```bash
RUST_LOG=btc_arb_engine=info cargo run
```

Fee/latency sensitivity run:

```bash
ARB_FEE_BPS_X100=200 ARB_LATENCY_BPS=1 ARB_MAX_NOTIONAL=500 cargo run
```

Tests:

```bash
cargo test
```

## Output

The scanner prints:

- `[STATUS]`: live feeds, routes evaluated, positive edges.
- `[FEED]`: exchange, symbol, lane, best bid/ask, data age, sequence/timestamp.
- `[BEST]`: best current candidate per market, even if net is negative.
- `[EDGE]`: printed only when net profit is positive after per-exchange taker fees and latency buffer.

## Current Defaults

- Max notional per route: `500` quote units.
- Fee assumption: real public default taker fee per exchange.
- Latency buffer: `2 bps`.
- Minimum gross spread: `1 bps`.
- USD stale threshold: `2500 ms`.
- USDT stale threshold: `1500 ms`.

Current public fee model: [`docs/exchange-fees.md`](docs/exchange-fees.md).

Environment overrides:

- `ARB_MAX_NOTIONAL`
- `ARB_MIN_PRINT_PROFIT`
- `ARB_MIN_GROSS_BPS`
- `ARB_FEE_BPS` for integer-bps all-exchange sensitivity override
- `ARB_FEE_BPS_X100` for fractional-bps all-exchange sensitivity override
- `ARB_LATENCY_BPS`

## 24/7 Broad Profit Monitor

For broad public-market discovery across many exchanges and quote lanes, run:

```bash
python3 scripts/profit_monitor.py
```

This monitor is public-data only: no private keys, no orders, no withdrawals.
It dynamically discovers all supported spot markets for the selected exchanges,
depth-checks same-quote opportunities, and saves profitable inventory-based
cases to:

- `data/profitable_cases.jsonl`
- `data/profitable_cases.sqlite`

One-cycle smoke run:

```bash
python3 scripts/profit_monitor.py --once --max-candidates 10
```

Run locally in the background:

```bash
mkdir -p data/live
PROFIT_MONITOR_INTERVAL_SEC=30 \
PROFIT_MONITOR_COINBASE_MARKET_LIMIT=80 \
nohup python3 scripts/profit_monitor.py --out-dir data/live \
  > data/live/profit_monitor.log 2>&1 &
echo $! > data/live/profit_monitor.pid
```

Check/stop:

```bash
tail -f data/live/profit_monitor.log
kill "$(cat data/live/profit_monitor.pid)"
```

Install as a macOS LaunchAgent for 24/7 local monitoring:

```bash
chmod +x ops/install-profit-monitor-launchagent.sh
ops/install-profit-monitor-launchagent.sh
```

The LaunchAgent runs from `~/Library/Application Support/hackathon-btc` and
writes logs to `~/Library/Logs/hackathon-btc/` so macOS privacy controls do not
block it from reading/writing under `Desktop`.

Check/stop the LaunchAgent:

```bash
launchctl print gui/$(id -u)/com.pedro.hackathonbtc.profit-monitor
tail -f "$HOME/Library/Logs/hackathon-btc/profit_monitor.log"
launchctl bootout gui/$(id -u)/com.pedro.hackathonbtc.profit-monitor
```

Query saved profitable cases:

```bash
python3 scripts/profit_report.py --limit 20
python3 scripts/profit_report.py --since-min 60 --quote USDT --min-net-bps 100
python3 scripts/profit_report.py --cases --limit 20
```

Install the fast BTC hot-path monitor:

```bash
chmod +x ops/install-btc-hot-path-launchagent.sh
ops/install-btc-hot-path-launchagent.sh
```

This is a separate 24/7 LaunchAgent that watches BTC order books directly
instead of waiting for the broad all-market cycle. It runs every 5 seconds by
default across 51 BTC venue/quote books (`USDT`, `USDC`, `USD`, `EUR`, `GBP`,
`MXN`, `TRY`) and writes to:

- `~/Library/Application Support/hackathon-btc/btc_hot_path/profitable_cases.jsonl`
- `~/Library/Application Support/hackathon-btc/btc_hot_path/profitable_cases.sqlite`

Check/query BTC hot-path cases:

```bash
launchctl print gui/$(id -u)/com.pedro.hackathonbtc.btc-hot-path
tail -f "$HOME/Library/Logs/hackathon-btc/btc_hot_path.log"
python3 scripts/profit_report.py \
  --db "$HOME/Library/Application Support/hackathon-btc/btc_hot_path/profitable_cases.sqlite" \
  --limit 20
```

Install the post-latency recheck monitor:

```bash
chmod +x ops/install-recheck-monitor-launchagent.sh
ops/install-recheck-monitor-launchagent.sh
```

This companion process reads newly saved broad opportunities, waits at least 5
seconds, re-walks the same public order books for the same notional, and records
whether the route was still profitable after real elapsed latency. It writes
into the same broad SQLite DB:

- `opportunity_rechecks`: one row per source opportunity recheck.
- `opportunity_recheck_cases`: route-level survival rollup.
- `recheck_cycles`: monitor health metrics.
- `~/Library/Application Support/hackathon-btc/live/profit_rechecks.jsonl`

Query post-latency survivors:

```bash
launchctl print gui/$(id -u)/com.pedro.hackathonbtc.recheck-monitor
tail -f "$HOME/Library/Logs/hackathon-btc/profit_recheck_monitor.log"
python3 scripts/profit_report.py --rechecks --limit 20
```

Install the paper-trade monitor:

```bash
chmod +x ops/install-paper-trade-monitor-launchagent.sh
ops/install-paper-trade-monitor-launchagent.sh
```

This process reads saved broad and BTC hot-path opportunities, waits at least
5 seconds, re-walks the current public books for the same route/notional, and
saves the virtual taker buy+sell transaction. It writes:

- `~/Library/Application Support/hackathon-btc/paper_trades/paper_trades.jsonl`
- `~/Library/Application Support/hackathon-btc/paper_trades/paper_trades.sqlite`

The paper ledger records requested notional, base size, VWAP buy/sell prices,
fees, latency haircut, net P&L, net bps, operational status hints, and optional
inventory executability from `inventory.json`.

Query paper trades:

```bash
launchctl print gui/$(id -u)/com.pedro.hackathonbtc.paper-trade-monitor
tail -f "$HOME/Library/Logs/hackathon-btc/paper_trade_monitor.log"
python3 scripts/profit_report.py --paper --limit 20
python3 scripts/profit_report.py --paper --cases --limit 20
python3 scripts/profit_report.py --paper --base BTC --quote USD --limit 20
```

Install the signal monitor:

```bash
chmod +x ops/install-signal-monitor-launchagent.sh
ops/install-signal-monitor-launchagent.sh
```

This process reads the broad and BTC hot-path `opportunity_cases` tables
and promotes only recent, repeated, non-blocked profitable routes into:

- `~/Library/Application Support/hackathon-btc/signals/profit_signals.jsonl`
- `~/Library/Application Support/hackathon-btc/signals/profit_signals.sqlite`

Default signal gates are: seen at least 3 times, active for at least 60 seconds,
seen within the last 120 minutes, max net at least 3 bps, last net at least
1 bps, and operational grade in `tradable_rebalance_public_ok` or
`tradable_rebalance_unknown`.

Signals can also be inventory-aware without API keys. Copy the example file and
edit available balances per exchange/asset:

```bash
cp config/inventory.example.json "$HOME/Library/Application Support/hackathon-btc/inventory.json"
```

With that file present, `profit_signal_monitor.py` annotates every signal:

- `inventory_executable`: enough quote balance on the buy venue and enough base
  balance on the sell venue for the saved opportunity size.
- `inventory_partial`: some prefunded inventory exists, but not enough for the
  full saved size.
- `inventory_insufficient`: relevant balances are present but zero/too small.
- `inventory_unknown`: no config, no matching exchange/asset balance, or missing
  latest base-size evidence.

To emit only executable-with-inventory signals:

```bash
python3 scripts/profit_signal_monitor.py --once --require-inventory
```

One-shot signal pass:

```bash
python3 scripts/profit_signal_monitor.py --once
sqlite3 "$HOME/Library/Application Support/hackathon-btc/signals/profit_signals.sqlite" \
  "select pair, route, source_seen_count, duration_sec, last_net_bps, operational_grade, inventory_grade from signal_events order by id desc limit 20;"
sqlite3 "$HOME/Library/Application Support/hackathon-btc/signals/profit_signals.sqlite" \
  "select base||'/'||quote as pair, buy_exchange||'->'||sell_exchange as route, source_seen_count, duration_sec, last_net_bps, operational_grade, inventory_grade from signal_cases order by last_signal_ms desc limit 20;"
```

Install the public operational status monitor:

```bash
chmod +x ops/install-status-monitor-launchagent.sh
ops/install-status-monitor-launchagent.sh
```

This companion process runs every 5 minutes and records public symbol trading
status plus deposit/withdraw status for venues that expose it without private
auth. It writes to:

- `~/Library/Application Support/hackathon-btc/status/status.sqlite`

`profit_report.py` automatically uses that DB when present and annotates rows:

- `trade=T/T`: buy and sell symbols are publicly tradeable.
- `quote_dep=Y/N/?`: public deposit status for the quote asset on the buy venue.
- `base_wd=Y/N/?`: public withdraw status for the base asset on the sell venue.
- `?`: the exchange does not expose that public status, or the asset/network was not in the status snapshot.

New opportunities are also persisted with:

- `operational_grade`: `tradable_rebalance_public_ok`, `tradable_rebalance_unknown`,
  `rebalance_blocked`, `trading_blocked`, `status_unknown`, or `status_unavailable`.
- `status_hint`: compact human-readable status.
- `status_json`: raw structured status evidence used for the grade.

The monitors also maintain `opportunity_cases`, a route-level rollup of saved
profitable events with `first_seen_ms`, `last_seen_ms`, `seen_count`,
`max_net_bps`, and the latest operational grade/status. Use
`profit_report.py --cases` to see recurring opportunities instead of individual
ticks.

Useful knobs:

```bash
PROFIT_MONITOR_INTERVAL_SEC=15 \
PROFIT_MONITOR_FETCH_WORKERS=10 \
PROFIT_MONITOR_DEPTH_WORKERS=8 \
PROFIT_MONITOR_MAX_CANDIDATES=60 \
PROFIT_MONITOR_COINBASE_WORKERS=10 \
PROFIT_MONITOR_BITSO_WORKERS=10 \
PROFIT_MONITOR_GEMINI_WORKERS=12 \
PROFIT_MONITOR_KRAKEN_WORKERS=4 \
PROFIT_MONITOR_UPBIT_WORKERS=3 \
PROFIT_MONITOR_INDEPENDENTRESERVE_TIMEOUT=4 \
PROFIT_MONITOR_INDEPENDENTRESERVE_WORKERS=16 \
PROFIT_MONITOR_QUOTES=BTC,ETH,BNB,USDT,USDC,USD,MXN,COP,EUR,BRL,ARS \
PROFIT_MONITOR_MIN_DEPTH_NET_BPS=5 \
python3 scripts/profit_monitor.py
```

Slow adapters with many per-market calls are internally parallelized. The main
runtime uses worker knobs for Coinbase, Bitso, Gemini, Kraken, Upbit, and Buda;
Independent Reserve uses shorter per-summary timeouts so one slow venue cannot
stall the full loop. Gate status asset-chain probes are also parallelized with
`STATUS_MONITOR_GATE_ASSET_TIMEOUT` and `STATUS_MONITOR_GATE_ASSET_WORKERS`.

Non-dollar quote lanes use quote-specific notional buckets by default. For
example, BTC quote routes are depth-checked with `0.001,0.005,0.01,0.02,0.05`
BTC instead of the USD-style `100,500,...` buckets.

Supported public adapters in the broad monitor:

- Binance, Binance.US, Coinbase Exchange, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, CoinTR, CoinW, Deribit, HitBTC, Coins.ph
- Crypto.com Exchange, Bitfinex, BitMEX Spot, Bitstamp, Bitso, Coincheck, CoinEx, Poloniex
- HTX, BitMart, Kraken, Gemini, AscendEX, EXMO, BtcTurk, CEX.IO
- WhiteBIT, Upbit, Indodax, Buda, NovaDAX, Foxbit, Mercado Bitcoin, Bitvavo
- Luno, VALR, Bitkub, bitFlyer, Bithumb, Bitbank, Bitrue
- Coinone, Korbit, GMO Coin, Independent Reserve, BTC Markets, NDAX, BitoPro
- DigiFinex, LATOKEN, Hyperliquid, Toobit, XT.com, HashKey Global, BingX, Backpack, Phemex, Bullish

Bitfinex uses `UST` in public symbols for USDT books; the monitor normalizes
those routes to `USDT` so `tBTCUST`, `tETHUST`, etc. compare correctly with
other USDT markets. The BTC hot path also tracks Bitfinex `BTC/USD`,
`BTC/USDT`, `BTC/EUR`, and `BTC/GBP`.

Regional fiat coverage now includes Buda `COP`/`CLP`/`PEN`/`ARS`, NovaDAX
and Foxbit `BRL`, Mercado Bitcoin `BRL`, Bitvavo `EUR`, Indodax `IDR`,
Luno and VALR `ZAR`, Luno `MYR`/`NGN`/`UGX`, Bitkub `THB`, Coincheck/bitFlyer/Bitbank `JPY`,
Bithumb/Upbit/Coinone/Korbit `KRW`, GMO Coin `JPY`, Independent Reserve
`AUD`/`USD`/`NZD`/`SGD`, BTC Markets `AUD`, NDAX `CAD`/`USD`/`USDT`/`USDC`, BitoPro `TWD`, Hyperliquid `USDC`,
CoinTR `TRY`/`USDT`, CoinW `USDT`/`USDC`/`BTC`/`CNYT`, Deribit `BTC`/`ETH`/`USDT`/`USDC`/`USDE`, HitBTC `BTC`/`ETH`/`USDT`/`USDC`/`TUSD`, BitMEX Spot `USDT`/`BTC`, Coins.ph `PHP`/`USDT`/`USDC`, and WhiteBIT/DigiFinex/LATOKEN/Toobit/XT.com
fiat/stable lanes in addition to Bitso `MXN`.

`LBank` has an experimental adapter but is not in the default run because its
global ticker does not expose bid/ask; enable it explicitly with
`--exchanges lbank,...` once a depth-heavy cycle is acceptable.

`WOO X` also has an experimental adapter but is not in the default run because
the public REST order-book endpoint returned stale books during verification,
even while public trades were fresh. Enable it only for targeted tests until a
fresh public book source is wired in.

`Pionex` has an experimental depth-first adapter, but it is not in the default
run because the public REST API rate-limited this environment after smoke
testing. Enable it only for targeted low-frequency runs.

`Bullish` status monitoring is in the default status monitor. Its profit adapter
is available for targeted runs, but is not in the default profit exchange set
because broad per-symbol tick sweeps returned HTTP 429 in this environment.
Use `--exchanges bullish,...` with `PROFIT_MONITOR_BULLISH_MAX_TICKS` for
controlled tests.

The saved cases are **inventory-based** opportunities. They assume quote
inventory is already on the buy venue and base inventory is already on the sell
venue. Transfer/deposit status is intentionally not treated as proven by this
monitor.

## Next Engine Steps

1. Add private read-only balance adapters for inventory-aware routing.
2. Add WebSocket hot paths for the most recurring BTC/USDT, BTC/USD, and BTC/MXN routes.
3. Add per-account fee/min-order/tick-size config from authenticated APIs.
4. Add persistence alerts for routes that survive multiple cycles after status gates.
5. Add tiny-size live executor with IOC limit orders after scanner proves edge.
