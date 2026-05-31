# BTC Arbitrage Simulator

Full-stack Bitcoin arbitrage simulator for the **Coding Challenge Mexico**.
Detects cross-exchange spot arbitrage on real public order books, simulates
execution with realistic costs, accounts for wallet inventory, and visualizes
P&L. No API keys, no real orders.

## Run locally

```bash
python3 app/server.py          # then open http://localhost:8080
# custom port:
PORT=9000 python3 app/server.py
```

No `pip install` needed: the backend and engine use only the Python standard
library (3.9+). The frontend is a single static page (vanilla JS + canvas), no
build step, no CDN.

## Deploy (publicly accessible)

- **Render**: connect the repo; `render.yaml` is included (free plan, no build).
- **Docker / Fly / Railway / Cloud Run**: a `Dockerfile` is included.
  ```bash
  docker build -t arb . && docker run -p 8080:8080 arb
  ```
- **Procfile** included for Heroku-style buildpacks.

## What it does (challenge requirements -> implementation)

| Requirement | Where |
|---|---|
| Real-time order book monitoring | `server.py` adapters, 7 venues, scan loop every 6s |
| Ask/bid comparison | `eval_route()` over every venue pair within a lane |
| Net-profit detection (fees/slippage/latency/liquidity) | `eval_route()` net formula + depth-aware VWAP |
| Simulated buy/sell execution | `Engine._record_trade()` + `Wallets.apply()` |
| Realistic costs | per-venue taker fees + latency haircut (configurable) |
| Partial fills | `walk_buy` / `walk_sell` stop at depth, reject if not fully fillable |
| Wallet balance accounting | `Wallets`, never negative, inventory conservation |
| Opportunity / trade history | SQLite (`sim.sqlite`) + in-memory rings |
| P&L visualization | canvas equity/realized chart, live |
| Decision inspector (why accepted/rejected) | `/api/decision/<id>` + drawer with depth waterfall |

## Architecture

```
Browser (static SPA)  <--HTTP/JSON-->  Python stdlib server  --REST-->  Exchange public APIs
   index.html / app.js / styles.css        server.py (ThreadingHTTPServer)     Binance, Coinbase,
   - live feeds, opportunities table        - scan loop (background thread)      Kraken, Bitfinex,
   - P&L canvas chart                        - eval_route() = the engine          Bybit, OKX, Gemini
   - decision inspector drawer               - Wallets accounting
   - config + scenario controls              - SQLite persistence
```

### Net profit formula (per directed route, quote currency)

```
buy_cost   = spent * (1 + taker_fee_buy)
sell_value = recv  * (1 - taker_fee_sell)
haircut    = spent * latency_bps
net_profit = sell_value - buy_cost - haircut
net_bps    = net_profit / buy_cost * 10000
```

`spent`/`recv` come from walking the **real order book** with VWAP for each
notional bucket (100, 250, 500, 1000, 2500, 5000), so larger sizes correctly
pay deeper levels. The engine promotes the largest bucket that stays net
positive, and rejects everything else with an explicit reason.

### Decision states

`ENTER_SIM` (executed) · `SKIP_NEGATIVE` (edge < min after costs) ·
`SKIP_CROSSED` (no raw edge) · `SKIP_THIN` (insufficient depth) ·
`SKIP_STALE` (book too old) · `SKIP_INVENTORY` (leg underfunded, rebalance needed).

### Quote-lane separation (a correctness decision)

USD and USDT are **different assets**. The engine never compares a USD price
against a USDT price without a basis conversion, so routes are only formed
between venues in the same lane: USD = {Coinbase, Kraken, Gemini, Bitfinex},
USDT = {Binance, Bybit, OKX}.

## Scenarios (top-right selector)

Real BTC cross-exchange spreads almost never clear taker fees + latency. That is
the honest result, and **LIVE** mode shows it: the engine mostly rejects, and the
decision inspector explains why. To demonstrate the full execution + P&L +
inventory-drift path, two clearly-labeled non-live modes are included:

- **LIVE** - real books, real fees. Mostly rejections. The truth.
- **ZERO-FEE** - real books, taker fees forced to 0 (models maker/zero-fee
  venues like Bitfinex). Shows which raw dislocations would clear with no fees.
- **STRESS** - real books plus an *injected* transient dislocation on the sell
  leg (labeled `SIMULATED DISLOCATION`). Demonstrates detection, paired
  execution, realized P&L, and the inventory drift that forces rebalancing.

The badge in the header makes the non-live modes unmistakable. P&L from STRESS
is explicitly simulated, never presented as real captured profit.

## Key findings baked into the design

This simulator was built after measuring ~10,000 markets across ~50 exchanges.
The honest conclusion (documented in `../docs/`): the gigantic "spreads" on
illiquid tokens are illusions (tiny depth, ticker collisions, un-withdrawable
assets), and liquid BTC spreads do not survive fees. The engine encodes that
discipline: it would rather print **no trade** than a fake profit, and it shows
every rejection with the numbers behind it.

## API

```
GET  /api/state              engine + feeds snapshot
GET  /api/opportunities      recent opportunities (?state=, ?limit=)
GET  /api/trades             simulated fills
GET  /api/pnl                equity / realized time series
GET  /api/wallets            per-venue inventory
GET  /api/decision/<id>      full decision waterfall for one opportunity
GET  /api/summary            decision-state counts + top routes
POST /api/config             tune fees, latency, min edge, max notional, scenario
```

## Assumptions & limitations

- Public REST snapshots, polled every 6s (not co-located WebSocket); a latency
  haircut models the gap between observation and fill.
- Each venue is prefunded (50,000 quote + 0.5 BTC). Real rebalancing
  (transfers, withdrawal fees, settlement time) is out of scope for the sim and
  surfaced as `SKIP_INVENTORY` when a leg runs dry.
- Some venues geo-block certain hosts; the scanner degrades gracefully and runs
  on whatever venues are reachable (needs >= 2 in a lane).
