# Overnight Profit Checkpoints

Started: 2026-05-29 America/Merida.

## Checkpoint 1 - Baseline And Broad Market Probe

### Findings

- The current Rust scanner is correct as an MVP, but too narrow for discovery. It only covers Tier A venues and a small curated asset list.
- Added `scripts/market_probe.py`, a no-key public REST probe that normalizes spot tickers across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com Exchange, Bitfinex, and Bitso.
- Probe snapshot covered `10,240` public markets:
  - Binance `1,722`
  - MEXC `2,343`
  - Gate `2,124`
  - OKX `1,111`
  - KuCoin `962`
  - Bitget `662`
  - Crypto.com `570`
  - Bybit `556`
  - Bitfinex `108`
  - Bitso `82`
- High-coverage same-lane assets in USDT include BTC, ETH, SOL, XRP, XLM, NEAR, DOGE, SUI, WLD, HBAR, TON, BCH, DOT, AAVE, ONDO, ADA, LINK, SEI, UNI, INJ, FET, LTC, FIL, PEPE, RENDER.

### Top Candidates Current

- **Spot-perp / funding carry**: strongest non-fake signal. BCH/TRX/WLD showed funding magnitudes around `4-8 bps` per period on Binance/Bybit/OKX. Requires inventory/margin and borrow/short-spot path.
- **Coinbase INTX spot-perp basis/funding**: sub-agent found low fees and large notional on BTC/ETH/DOGE USDC perps. Needs availability confirmation and dedicated scanner.
- **Bitfinex zero-fee expansion**: official Bitfinex page says 0 maker/taker for all customers. This lowers the same-lane cross-exchange break-even dramatically, but first XLM/XRP USD depth checks were still negative.

### Ideas Discarded Or Downgraded

- **XLM/USDT top-of-book REST edge**: initial ticker probe showed XLM/USDT Gate/Binance/Bybit -> OKX/MEXC net positive after estimated fees. Direct depth validation killed it; $500 routes were negative.
- **MXN/Bitso taker-taker arbitrage**: sub-agent measured Bitso MXN routes and found gross spreads around `-8` to `+10 bps`, while taker fees require roughly `166-192 bps` just to break even.
- **Triangular taker-only majors**: sub-agent found liquid majors usually between `-2` and `+2 bps` raw, far below 3-leg taker fee hurdle.
- **CEX-DEX execution**: killed as primary 48h route. Without wallet/signature/inventory/on-chain execution, it is only a price monitor.

### Risks / Blockers

- Public ticker endpoints can be stale or symbol-inconsistent. Every candidate must be validated with depth snapshots/streams and edge duration.
- Real execution needs account-specific fee tiers, inventory, API trade permissions, and fill reconciliation.
- Funding carry needs short spot/borrow or perp + spot inventory; it is not a pure no-inventory arbitrage.

## Checkpoint 2 - Depth And Funding Validation

### Findings

- Depth validation for `XLM/USD OKX -> Bitfinex` turned a positive ticker signal into negative VWAP:
  - $100: about `-24 bps`
  - $500: about `-31 bps`
- Depth validation for `XRP/USD Crypto.com/OKX -> Bitfinex` also turned ticker-positive into negative after fee/latency:
  - Crypto.com -> Bitfinex around `-3 bps` at $100-$500
  - OKX -> Bitfinex around `-7 bps` at $100-$500
- Funding/basis probe found:
  - BCH Binance perp funding about `-8.1 bps/period`, perp mark below spot by about `-4.7 bps`.
  - TRX Bybit funding about `-7.3 bps/period`, perp mark below spot by about `-11.8 bps`.
  - WLD Binance/Bybit funding around `-4-5 bps/period`, perp mark below spot by `-11` to `-18 bps`.

### Current Top Candidates

1. Coinbase INTX BTC/ETH/DOGE USDC spot-perp funding/basis measurement.
2. BCH/TRX/WLD negative-funding carry scanner across Binance/Bybit/OKX.
3. Bitfinex zero-fee same-lane depth/duration scanner.
4. MEXC low-fee spot + triangular benchmark scanner.
5. Bitso MXN basis dashboard, not execution.

### Current Decision

The best answer is not "execute tomorrow morning." The best answer is:

> Build measurement that separates persistent executable edge from stale ticker artifacts, then pursue spot-perp/funding and Bitfinex zero-fee routes first.

## Checkpoint 3 - Reproducible Probes And Final Ranking Sanity Check

### Findings

- Added `scripts/funding_probe.py` so funding/basis measurement is reproducible without private keys.
- `scripts/market_probe.py` completed another broad scan:
  - `10,240` spot markets.
  - Quotes: `USDT 7,115`, `USD 1,547`, `USDC 1,143`, `EUR 412`, `MXN 23`.
  - Venues: Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, Bitso.
- Latest ticker-level top sane spot route was `SOL/USD Crypto.com -> Bitfinex`, only about `+0.4 bps` after simple fee/latency assumptions.
- Direct order book validation killed that `SOL/USD` route:
  - $100: about `-4.4 bps`
  - $500: about `-4.7 bps`
  - $1k: about `-4.8 bps`
  - $5k: about `-5.9 bps`
- `scripts/funding_probe.py` scanned `47` spot/perp routes. All were negative under conservative one-period round-trip taker assumptions.
- Best funding candidates were still the least bad:
  - Coinbase INTX `ETH`: about `-6.2 bps`
  - Coinbase INTX `DOGE`: about `-7.8 bps`
  - Coinbase INTX `BTC`: about `-8.0 bps`
  - Bybit `WLD`: about `-13.0 bps`
  - Bybit `TRX`: about `-15.6 bps`

### Current Top Candidates

1. Depth + duration discovery recorder. This is still the highest leverage because every ticker edge has failed depth validation.
2. Funding carry monitor with maker/fee-tier scenarios. Taker round trip is negative, but funding is the only recurring signal large enough to monitor.
3. Bitfinex zero-fee USD scanner. Zero fee matters, but all measured examples need depth/duration before promotion.
4. MEXC/Gate/Bitget low-fee alt scanner. Useful only after direct depth validation.
5. Bitso MXN basis monitor. Useful for signal/rebalance, not taker execution.

### Ideas Discarded Or Downgraded

- `SOL/USD Crypto.com -> Bitfinex` as immediate spot trade: killed by depth and fee/latency.
- Current Coinbase INTX taker funding carry: downgraded from possible execute to MEASURE until maker/fee-tier or stronger funding window appears.
- Current BCH/TRX/WLD funding windows: MEASURE only; round-trip proxy is negative.

### Final Decision

No realistic immediate execution trade is proven yet. The correct next move is a measurement engine that records depth, duration, and funding windows, then only promotes routes that stay net-positive after costs.
