# Implementation Queue

Checked: 2026-05-29.

Ordered by impact, not by neatness.

## P0 - Measurement That Prevents Fake Profit

- [ ] Persist discovery samples to `data/market-samples/*.jsonl`.
  - Acceptance: one command records timestamped route samples with gross/net bps, fees, executable notional, and source age.
- [ ] Add depth validation to `scripts/market_probe.py`.
  - Acceptance: top route ranking uses direct order book VWAP at `$100`, `$500`, `$1k`, `$5k`, not ticker bid/ask only.
- [ ] Add edge-duration tracking.
  - Acceptance: route is promoted only if positive net survives at least N consecutive samples or M milliseconds.
- [ ] Add symbol metadata filters.
  - Acceptance: delisted/offline/restricted markets and absurd price-ratio anomalies are excluded before ranking.
- [ ] Add venue min-notional/tick/step metadata to discovery output.
  - Acceptance: route output includes `minNotional`, `priceTick`, `sizeStep`, and `status` where public APIs provide it.

## P0 - Expand Public Scanner Coverage

- [ ] Add Bitfinex adapter.
  - Acceptance: Rust scanner receives live `BTC/USD`, `ETH/USD`, `XRP/USD`, `XLM/USD` Bitfinex books and applies 0 bps fee model.
- [ ] Add MEXC adapter.
  - Acceptance: scanner can subscribe/poll priority `USDT` books and uses MEXC fee assumptions from docs.
- [ ] Add Gate adapter.
  - Acceptance: scanner can validate XLM/HBAR/SUI-style routes with live depth and stale rejection.
- [ ] Add Bitso adapter.
  - Acceptance: scanner emits `btc_mxn`, `btc_usd`, `btc_usdt`, `usd_mxn`, `usdt_mxn` with MXN/USD/USDT lanes separated.
- [ ] Add config-driven asset list.
  - Acceptance: assets are loaded from config/discovery output, not hardcoded in `src/feeds.rs`.

## P0 - Funding / Spot-Perp Measurement

- [x] Create `scripts/funding_probe.py`.
  - Acceptance: pulls Binance, Bybit, OKX funding/mark data and spot books for priority assets.
- [x] Add Coinbase INTX public funding/instrument probe.
  - Acceptance: records BTC/ETH/DOGE USDC spot/perp basis, predicted funding, notional, and fee assumptions without private keys.
- [ ] Implement funding route scoring.
  - Acceptance: output evaluates positive funding and negative funding directions separately with entry/exit cost and margin risk flags.
- [ ] Add stop-condition logic for funding flip.
  - Acceptance: route is downgraded if recent funding sign is unstable or next funding is too far away.

## P1 - Engine Correctness

- [ ] Add fee currency modeling.
  - Acceptance: buy-side fees charged in base asset reduce received base inventory; quote-equivalent P&L is explicit.
- [ ] Add venue-specific min order and rounding.
  - Acceptance: decisions reject if rounded size/notional fails either venue minimum.
- [ ] Add rejection logging for all candidates.
  - Acceptance: rejected opportunities include `negative_after_fees`, `stale_book`, `insufficient_depth`, `fee_unknown`, `cross_lane_unmodeled`.
- [ ] Add CSV/JSONL opportunity recorder to Rust scanner.
  - Acceptance: `ARB_RECORD_PATH=data/opportunities.jsonl` records best/rejected routes without blocking scanner.
- [ ] Add tests for per-exchange fees and fractional bps.
  - Acceptance: tests cover Bitfinex 0 bps, MEXC 5 bps, Bitso 78 bps, and existing Tier A defaults.

## P1 - Ranking And UI

- [ ] Create route ranking dashboard data endpoint.
  - Acceptance: UI can show top 20 routes by measured net bps, executable notional, duration, and confidence.
- [ ] Add "killed ideas" panel.
  - Acceptance: UI shows why opportunities are rejected, not only best positive edge.
- [ ] Add funding/basis panel.
  - Acceptance: dashboard displays funding rates, spot/perp basis, and next funding time.
- [ ] Add MXN basis panel.
  - Acceptance: dashboard displays Bitso `BTC/MXN`, implied MXN via `USD/MXN` and `USDT/MXN`, and net after fees.

## P2 - Live Readiness

- [ ] Add account-specific fee fetchers.
  - Acceptance: optional private adapters fetch exact fee tiers without withdrawal permissions.
- [ ] Add inventory model per asset/venue.
  - Acceptance: scanner can reject routes lacking quote/base inventory before simulated execution.
- [ ] Add IOC/FOK order simulator.
  - Acceptance: modeled execution uses rounded tight limits and handles partial fills.
- [ ] Add kill switch/circuit breaker.
  - Acceptance: abnormal stale feeds, crossed books, or consecutive negative simulations pause execution.
- [ ] Add live tiny-size checklist.
  - Acceptance: README lists required KYC/API permissions/IP whitelist/funding for each live venue.

## P2 - Research Backlog

- [ ] Measure Binance.US fee/availability separately.
  - Acceptance: official source and API feasibility documented; do not assume Binance global availability.
- [ ] Measure Bitfinex funding/margin costs.
  - Acceptance: zero trading fees are not conflated with borrow/funding costs.
- [ ] Measure CEX-DEX Base `cbBTC/USDC` read-only.
  - Acceptance: output includes gas, pool fee, price impact, aggregator fee, quote TTL, and edge duration.
- [ ] Revisit maker/rebate strategy.
  - Acceptance: only after queue/fill probability model exists.
