# Profit Approach Playbook

Checked: 2026-05-29.

## Playbook 1 - Automatic Depth + Duration Discovery

### Hypothesis

The main bottleneck is not strategy math; it is finding routes whose edge survives depth, fees, and time. Public ticker edges are noisy. A discovery engine that samples depth and duration across many venues will reveal the few routes worth implementing live.

### Why It Can Print

More venues and assets create more edges, but only depth-validated persistent edges count. The probe found 10k+ public markets and many shared quote lanes. Most are fake, but the search space is large enough that a systematic filter can surface real anomalies faster than hand-picking assets.

### How To Measure

- Pull spot market metadata from Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, Bitso.
- Keep `USDT`, `USDC`, `USD`, `MXN`.
- Build same-lane routes for bases listed on 2+ venues.
- For each route, sample top-20/top-50 depth at $100, $500, $1k, $5k.
- Record `gross_bps`, `net_bps_after_fees`, `executable_notional`, `edge_duration_ms`, stale rate, and frequency/hour.

### Execution

Not an execution strategy by itself. It promotes routes into dedicated WebSocket scanners and kills fake edges.

### Risks

- REST tickers stale.
- Symbol normalization errors.
- Some venues have regional restrictions or poor API stability.

### Stop Conditions

- If after 2-4 hours no route has positive depth-adjusted net bps for at least $100 and >2 seconds duration, do not build live execution yet.

## Playbook 2 - Spot-Perp Funding Carry

### Hypothesis

Funding can generate yield even when spot-taker arbitrage does not. When funding is sufficiently positive or negative, a hedged spot/perp position can earn carry.

### Why It Can Print

Funding rates observed on BCH/TRX/WLD reached about `4-8 bps` per period on Binance/Bybit/OKX. Coinbase INTX appears especially promising from sub-agent research because fees are low and BTC/ETH/DOGE USDC perps have large notional.

### How To Measure

- For each asset, collect spot bid/ask, perp bid/ask/mark, predicted funding, next funding timestamp, and 24h perp notional.
- Use `scripts/funding_probe.py` for public no-key measurement across Binance, Bybit, OKX, and Coinbase INTX.
- Evaluate both directions:
  - Positive funding: long spot + short perp.
  - Negative funding: long perp + short spot/borrow.
- Include spot fees, perp fees, spread, basis, borrow cost, liquidation margin, and exit cost.
- Track funding persistence and reversal frequency.

Latest result:

- Current public probe found no route positive under conservative taker entry + taker exit assumptions.
- Best candidates were Coinbase INTX `ETH/DOGE/BTC` around `-6` to `-8 bps`, and Bybit `WLD/TRX` around `-13` to `-16 bps`.
- This remains a high-priority measurement path, not an execution path, until funding widens or maker/fee-tier assumptions are real.

### Execution

- Start paper-only.
- For live later, use small isolated margin and strict leverage caps.
- Prefer same-venue spot/perp if the exchange supports it, because transfers are not needed.

### Risks

- Short spot/borrow may be unavailable or expensive.
- Funding can flip before payment.
- Basis can move against the hedge.
- Perp liquidation/margin risk exists even with delta hedge.

### Stop Conditions

- Kill a route if expected funding until next payment does not cover entry + exit fees/spread + 2x safety haircut.
- Kill if borrow is unavailable or funding flips sign frequently.

## Playbook 3 - Bitfinex Zero-Fee Cross-Exchange

### Hypothesis

Bitfinex's public zero maker/taker fee policy materially lowers break-even and can make USD spot cross-exchange routes viable where Coinbase/Gemini/Kraken cannot.

### Why It Can Print

With one leg at 0 bps, the hurdle drops from `20+ bps` to as low as the other venue's fee plus latency. This is the biggest spot fee exception found.

### How To Measure

- Add Bitfinex depth WebSocket/REST for `BTC/USD`, `ETH/USD`, `XRP/USD`, `XLM/USD`, `SOL/USD`, `ADA/USD`, `SUI/USD`.
- Compare against OKX USD, Crypto.com USD, Coinbase USD, Kraken USD.
- Use depth at $100, $500, $1k, $5k.
- Record edge duration and stale rate.

Latest result:

- `SOL/USD Crypto.com -> Bitfinex` briefly looked marginally positive at ticker level, about `+0.4 bps` after simple fee/latency.
- Direct depth killed it: about `-4.4` to `-5.9 bps` from $100 to $5k notional.

### Execution

Only after account/KYC/API availability is confirmed. The scanner can be public-only.

### Risks

- First depth checks for XLM/XRP turned negative despite ticker positives.
- Bitfinex availability and deposit/funding path must be confirmed.
- Zero trading fee does not remove spread, slippage, withdrawal, or funding constraints.

### Stop Conditions

- Kill any Bitfinex route that fails depth-adjusted net bps at $500 for 30+ minutes of sampling.

## Playbook 4 - MEXC Low-Fee Altcoin Measurement

### Hypothesis

MEXC has low spot taker fees and broad altcoin coverage. Fragmented alt markets may show persistent same-lane spreads unavailable in majors.

### Why It Can Print

The fee hurdle is lower than standard 10 bps/leg venues. Broad market coverage means more possible edges.

### How To Measure

- Focus on priority liquid alts: `XLM`, `HBAR`, `SUI`, `BCH`, `INJ`, `FET`, `WLD`, `TRX`, `XRP`.
- Validate every ticker edge with MEXC depth plus counterparty depth.
- Require $100-$500 executable notional and >2s duration.

### Execution

Later. First build scanner evidence and confirm account/counterparty risk.

### Risks

- Regional/account restrictions.
- Altcoin withdrawal/funding issues.
- Stale tickers and shallow books.

### Stop Conditions

- Kill if all MEXC routes remain negative after fees for one hour of depth sampling.

## Playbook 5 - Bitso MXN Basis Dashboard

### Hypothesis

Mexican fiat/stablecoin basis can become large enough to matter, but taker-taker Bitso execution is too expensive at low volume.

### Why It Can Print

MXN markets are less globally efficient than BTC/USDT majors. Bitso gives local `btc_mxn`, `usd_mxn`, `usdt_mxn`, `btc_usd`, and `btc_usdt`.

### How To Measure

- Track `BTC/MXN` vs `BTC/USD * USD/MXN`.
- Track `BTC/MXN` vs `BTC/USDT * USDT/MXN`.
- Track `USDT/MXN` premium vs `USD/MXN` and Banxico FIX as non-executable context.
- Use Bitso depth and Bitso fee tiers from `available_books`.

### Execution

Not as taker-taker. Possible future execution only if:

- maker orders are used,
- fee tier is lower,
- basis is >200 bps,
- or route is used for inventory/funding decisions rather than hot arbitrage.

### Risks

- High taker fees.
- FX basis and settlement risk.
- MXN funding/inventory constraints.

### Stop Conditions

- Kill execution until net after fees is positive by at least 30 bps buffer.
