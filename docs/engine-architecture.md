# Arbitrage Engine Architecture

Checked: 2026-05-29.

## Decision

Build the trading/scanner engine first. UI is secondary.

For a performance-first engine, use Rust for the core hot path:

- WebSocket market data ingestion.
- Local L2 order book maintenance.
- Event-driven arbitrage scanning.
- Fixed-point P&L calculation.
- Paper/live execution state machine.

C/C++ can be marginally faster in expert hands, but they add too much accidental risk for JSON/WebSocket/API-heavy trading in 48 hours. Rust is close to C/C++ performance with memory safety and no garbage collector. Go is the pragmatic fallback if implementation speed beats deterministic latency, but the serious core target is Rust.

## Real Bottleneck

The bottleneck is not CPU arithmetic. It is:

- Exchange WebSocket cadence.
- Network RTT to each venue.
- JSON parsing and order book correctness.
- Exchange matching latency.
- Private order endpoint latency.
- Inventory placement and fills.

Therefore the engine must optimize data correctness, freshness, and affected-route scanning before micro-optimizing CPU.

## Hot Path

```text
exchange websocket tasks
  -> normalized book events
  -> bounded channel
  -> single-thread strategy core
  -> opportunity decisions
  -> paper/live executor
  -> append-only ledger
```

The strategy core owns books and balances. Keep it single-threaded to avoid locks in the calculation path.

## Data Model

Use fixed-point integers. No floats in P&L.

```rust
type PriceTicks = i64; // price / venue tick size
type QtyLots = i64;    // quantity / venue lot size
type Money = i128;

struct Level {
    price: PriceTicks,
    qty: QtyLots,
}

struct BookSide {
    levels: Vec<Level>, // bids desc, asks asc, cap top K
}

struct VenueBook {
    exchange_id: u16,
    lane: QuoteLane,
    bids: BookSide,
    asks: BookSide,
    received_mono_ns: u64,
    exchange_ts_ms: Option<u64>,
    seq: Option<u64>,
    status: BookStatus,
}
```

For `K <= 200`, sorted `Vec<Level>` is the default. It is cache-friendly and simpler than tree structures. Use binary search/update or small linear scans depending on the venue update shape.

## Algorithm

Do not rescan every route on every tick. If exchange `E` updates, only routes involving `E` changed:

```text
buy E -> sell every other same-lane venue
buy every other same-lane venue -> sell E
```

Complexity per update:

```text
O(2 * (N_lane - 1) * VWAP_K)
```

With 20 venues and top 50 levels, this is trivial in Rust.

Fast reject first:

```text
if sell.best_bid <= buy.best_ask:
    reject

gross_bps = (sell.best_bid - buy.best_ask) / buy.best_ask

if gross_bps < min_required_bps:
    reject
```

Only after passing the cheap check, compute depth-aware VWAP.

## Executable Profit

Executable size is:

```text
min(
  buy_depth_available,
  sell_depth_available,
  quote_balance_on_buy_exchange / buy_avg,
  btc_balance_on_sell_exchange
)
```

Net profit:

```text
net =
  sell_proceeds
  - buy_cost
  - buy_fee
  - sell_fee
  - latency_haircut
  - slippage_buffer
```

If `net <= min_profit`, reject. The engine should be ruthless: no trade is better than fake yield.

## Inventory Model

Cross-exchange arbitrage needs pre-positioned inventory:

- Buy venue needs quote currency (`USD`, `USDT`, `MXN`, etc.).
- Sell venue needs BTC.

Transfers between exchanges are not hot-path arbitrage. They are slow rebalance operations.

## Stale Data

Use a monotonic clock internally:

```text
if now_mono - book.received_mono_ns > stale_threshold:
    reject all routes involving this book
```

Initial thresholds:

- Binance/Bybit/OKX: 500-1500 ms.
- Coinbase/Kraken/Gemini: 1000-2500 ms.
- Bitso/MXN: 2000-5000 ms.

## Live Execution

Live trading should use tight IOC/FOK limit orders, not naked market orders:

```text
buy_limit = buy_avg * (1 + max_slippage_bps)
sell_limit = sell_avg * (1 - max_slippage_bps)
```

Execution state:

```text
detect
  -> reserve balances
  -> submit both legs concurrently
  -> confirm fills via private stream/rest
  -> reconcile ledger
  -> release/hedge residuals
```

## Triangular Arbitrage

Do not start with Bellman-Ford for cross-exchange BTC. It is overkill.

Use Bellman-Ford or negative-log cycle detection only for triangular/multi-asset arbitrage inside one exchange. For hot path, precompute liquid triangles and rescan only triangles affected by the updated pair.

## Sources

- Tokio async networking runtime: https://tokio.rs/
- Rust vs C++ benchmark paper: https://arxiv.org/abs/2209.09127
- Binance Spot WebSocket depth/local-book docs: https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
- Bybit V5 orderbook docs: https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook
- Coinbase Advanced Trade WebSocket docs: https://docs.cdp.coinbase.com/coinbase-business/advanced-trade-apis/websocket/websocket-overview
- Kraken WebSocket v2 L2 book docs: https://docs.kraken.com/api/docs/websocket-v2/book/
- Low-latency networking survey: https://arxiv.org/abs/1808.02079

