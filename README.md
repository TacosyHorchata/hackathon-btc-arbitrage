# BTC Arbitrage Simulator

Live app: https://hackathon-btc-arb.fly.dev
Source deliverable: [`app/`](app/README.md)

This is a full-stack simulator for the Coding Challenge Mexico arbitrage prompt.
It monitors real public BTC order books, evaluates cross-exchange routes, and
simulates paired buy/sell execution only when the route survives realistic costs.

The core idea: **most visible arbitrage is fake once you include depth, fees,
latency, stale books, and inventory. This engine rejects those trades explicitly
instead of printing fake P&L.**

## Judge In 60 Seconds

1. Open the live app.
2. Stay in `LIVE`: see real order books and rejected routes.
3. Click any rejected opportunity: inspect the depth waterfall and net bps.
4. Switch to `STRESS`: a clearly labeled simulated dislocation proves the full
   execution path, wallet drift, and P&L accounting.
5. Switch back to `LIVE`: the real mode stays honest.

## What Wins

- Real public market data, no API keys.
- Depth-aware VWAP instead of top-of-book fantasy.
- Per-exchange taker fees before profit.
- Latency haircut before profit.
- USD and USDT lanes are not mixed.
- Stale/crossed/thin books are rejected.
- Wallet inventory is enforced per venue.
- Every accept/reject has an inspectable reason.
- Simulated scenarios are clearly labeled.

## Web App

```bash
python3 app/server.py
# open http://localhost:8080
```

No install step. Backend is Python stdlib. Frontend is static HTML/CSS/JS.

Deploy targets included:

- `Dockerfile`
- `fly.toml`
- `render.yaml`
- `Procfile`

## API

```text
GET  /api/state
GET  /api/opportunities
GET  /api/trades
GET  /api/pnl
GET  /api/wallets
GET  /api/decision/<id>
GET  /api/summary
POST /api/config
```

## Engine Logic

For each directed route:

```text
buy_cost   = spent * (1 + taker_fee_buy)
sell_value = recv  * (1 - taker_fee_sell)
haircut    = spent * latency_bps
net_profit = sell_value - buy_cost - haircut
net_bps    = net_profit / buy_cost * 10000
```

`spent` and `recv` come from walking the real L2 order book through increasing
notional buckets. Larger orders pay deeper levels. If the book cannot fill the
bucket, the route is rejected as thin.

Decision states:

- `ENTER_SIM`: net-positive after depth, fees, latency, and inventory checks.
- `SKIP_NEGATIVE`: raw edge exists but dies after real costs.
- `SKIP_CROSSED`: buy ask is not below sell bid.
- `SKIP_THIN`: insufficient depth.
- `SKIP_STALE`: book is too old.
- `SKIP_INVENTORY`: prefunded wallet cannot execute both legs.

## Scenarios

- `LIVE`: real books, real fees, honest result.
- `ZERO-FEE`: real books with taker fees forced to zero for sensitivity testing.
- `STRESS`: real books plus a labeled simulated sell-side dislocation to show
  execution, realized P&L, and inventory drift.

## Venues

USD lane:

- Coinbase
- Kraken
- Gemini
- Bitfinex

USDT lane:

- Binance
- Bybit
- OKX

Some datacenters geo-block Binance or Bybit. The app degrades gracefully and
continues with the reachable venues.

## Rust Scanner

The repo also includes a Rust public-market scanner with WebSocket feeds and
multi-pair support.

```bash
cargo run
cargo test
```

Current scanner scope:

- BTC, ETH, SOL where supported on USD venues.
- BTC, ETH, SOL, XRP, DOGE, LTC on USDT venues.
- Event-driven affected-route scanning.
- Fixed-point money math.
- Depth-aware VWAP.
- Fee and latency buffers.

## Why This Is Honest

The project started by probing broad public markets across many exchanges. The
pattern was clear: giant apparent spreads often come from tiny depth, blocked
venues, ticker collisions, stale books, or assets that are hard to move.

So the deliverable optimizes for the thing a real arbitrage system needs first:
**refusing bad trades with evidence.**

## Files

- [`app/server.py`](app/server.py): simulator backend, engine, API.
- [`app/static/app.js`](app/static/app.js): dashboard behavior.
- [`app/static/index.html`](app/static/index.html): dashboard layout.
- [`app/static/styles.css`](app/static/styles.css): dashboard styling.
- [`docs/`](docs/): research notes, engine specs, rejected approaches.
- [`src/`](src/): Rust scanner.
