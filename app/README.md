# BTC Arbitrage Bot Simulator

Live demo: https://hackathon-btc-arb.fly.dev

Full-stack web deliverable for the **Coding Challenge Mexico: Arbitraje de
Bitcoin**. It monitors public BTC order books, evaluates cross-exchange
arbitrage routes, simulates paired execution, accounts for venue wallets, and
visualizes opportunities, fills, equity, and realized P&L.

## Run Locally

```bash
python3 app/server.py
# open http://localhost:8080

PORT=9000 python3 app/server.py
```

No install step: Python stdlib backend, static HTML/CSS/JS frontend, SQLite
history.

## Judge Flow

1. Open the live demo.
2. Leave `LIVE` selected to see real books and real-cost rejections.
3. Click a rejected route to inspect depth, VWAP, fees, latency, rebalance
   reserve, and net bps.
4. Switch to `STRESS` to see a clearly labeled simulated dislocation execute
   through wallet updates and P&L.
5. Switch back to `LIVE`; the bot resumes honest real-market evaluation.

## Challenge Requirements -> Implementation

| Requirement | Implementation |
|---|---|
| Real-time order books | Concurrent public REST polling over 7 BTC venues every 3s |
| Ask/bid arbitrage detection | Directed route evaluation inside each quote lane |
| Net profitability | Depth-aware VWAP, per-venue taker fees, latency, rebalance reserve |
| Simulated execution | Paired buy/sell ledger with wallet balance updates |
| Realistic costs | Fees + slippage + latency + withdrawal/rebalance reserve |
| Partial orders | Falls back to symmetric partial fill when full bucket cannot execute |
| Wallet balances | Per-venue quote/base wallets, invariant against negative balances |
| History and P&L | SQLite tables plus in-memory rings for live dashboard |
| Web presentation | Browser dashboard with feeds, routes, trades, decisions, chart |

## API

```text
GET  /api/state
GET  /api/opportunities?limit=150
GET  /api/trades
GET  /api/pnl
GET  /api/wallets
GET  /api/decision/<id>
GET  /api/summary
POST /api/config
```

`POST /api/config` supports scenario, fee, latency, rebalance, min-edge, and
notional tuning with bounded validation.

## Architecture

```text
Browser dashboard  <--HTTP/JSON-->  Python stdlib server  --REST-->  Exchanges
index/app/styles                     Engine + wallets + SQLite              L2 books
```

Venues:

- USD lane: Coinbase, Kraken, Gemini, Bitfinex.
- USDT lane: Binance, Bybit, OKX.

USD and USDT are intentionally not compared without an explicit basis model.

## Modes

- `LIVE`: real books, real fees, honest decisions.
- `ZERO-FEE`: real books with taker fees set to zero for sensitivity testing.
- `STRESS`: real books plus labeled simulated sell-side dislocation to prove
  execution, P&L accounting, and inventory drift.

## Verification

```bash
python3 -m py_compile app/server.py
python3 -m unittest tests/test_app_server.py
cargo test
```

The Rust scanner under `src/` provides the event-driven/WebSocket hot path and
fixed-point tests. The Python app is the deployed web deliverable.
