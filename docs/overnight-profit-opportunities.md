# Overnight Profit Opportunities

Checked: 2026-05-29.

Verdict: there is no trustworthy taker-taker spot trade ready to execute yet. The most promising profit path is **measurement-first**, with spot-perp/funding and Bitfinex zero-fee expansion at the top. Simple spot-taker across retail USD venues is dead.

## Top 3 To Pursue First Tomorrow

1. **Build depth + duration discovery recorder**
   - Why first: every apparent spot edge so far dies unless depth/duration validates it.
   - Code: upgrade `scripts/market_probe.py`, add JSONL recorder, then feed top routes into Rust scanner config.
   - Success: produce top 20 routes with net bps, executable notional, duration, and confidence.

2. **Measure spot-perp / funding carry**
   - Why second: funding is the strongest non-fake signal found, but the latest conservative public probe is still negative after round-trip fees.
   - Code: `scripts/funding_probe.py`, then a Rust funding panel/strategy module.
   - Success: identify routes where funding until next payment exceeds entry/exit costs with margin safety and survives duration checks.

3. **Add Bitfinex zero-fee scanner**
   - Why third: official 0 bps maker/taker is the biggest spot fee exception found.
   - Code: add Bitfinex public order book adapter and fee model.
   - Success: find whether USD spot routes can survive depth after fee hurdle is reduced.

## Ranking Formula

```text
expected_value_score =
  positive_net_bps_after_costs
  * executable_notional_usd
  * frequency_per_hour
  * confidence_multiplier
  / implementation_hours
```

Confidence multipliers:

- high: `1.0`
- medium: `0.5`
- low: `0.2`

For opportunities with negative measured net, score is `0` as an execution trade, even if they are useful measurement work.

## Top 10 Opportunities

| Rank | Verdict | Approach | Route / Pair | Net After Costs | Executable Notional | Frequency Proxy | Confidence | Impl Hours | EV Score | Why |
|---:|---|---|---|---:|---:|---:|---|---:|---:|---|
| 1 | DO_NOW | discovery | all same-lane spot routes | unknown | many | continuous | high | 4 | n/a | Necessary to avoid fake edges; broad probe found 10,240 markets. |
| 2 | MEASURE | funding-inventory | Coinbase INTX `BTC/ETH/DOGE` spot/perp USDC | current public proxy negative, best routes around `-6` to `-8 bps` | high | hourly funding | medium | 6 | 0 trade / high measure | Low fees, hourly funding, and high notional make it the best funding venue to keep measuring. |
| 3 | MEASURE | funding-inventory | BCH/TRX/WLD perps vs spot on Binance/Bybit/OKX | funding `4-8 bps/period`; current round-trip proxy negative | medium-high | per funding period | medium | 5 | 0 trade / high measure | Strong funding signal, but needs better entry, maker leg, or more extreme funding. |
| 4 | DO_NOW | cross-exchange spot | Bitfinex zero-fee USD vs Crypto.com/OKX/others | ticker near-positive, depth negative so far | $100-$5k tested | continuous | medium | 4 | 0 trade / high measure | 0 bps fee lowers hurdle; depth validation is still killing candidates. |
| 5 | MEASURE | cross-exchange altcoin | MEXC low-fee USDT alts vs Binance/Gate/Bybit/OKX | mostly negative after depth | $100-$1k target | continuous | medium | 4 | 0 trade / medium measure | Low taker fee and many markets; likely best spot expansion after Bitfinex. |
| 6 | MEASURE | cross-lane FX | Bitso MXN basis (`btc_mxn`, `usd_mxn`, `usdt_mxn`) | taker net around `-180 bps` | MXN liquidity exists | continuous | high | 3 | 0 trade / medium measure | Not executable as taker, useful local basis/rebalance signal. |
| 7 | LATER | maker-taker | post-only on one leg, taker hedge on other | unknown | route-dependent | route-dependent | low | 10 | unknown | Can beat taker fees, but needs fill probability/queue model. |
| 8 | MEASURE | triangular | MEXC `USDT -> BTC/ETH -> USDC -> USDT` | about `-13` to `-15 bps` in sample | $100-$1k | continuous | high | 4 | 0 | Useful rejection benchmark, not profit today. |
| 9 | LATER | CEX-DEX | Base `cbBTC/USDC` vs Coinbase/Binance.US | unknown; aggregator fees can kill | pool liquidity high | route-dependent | low | 12 | 0 today | Read-only panel only; execution too complex for 48h. |
| 10 | LATER | account-fee arbitrage | Binance.US / VIP / BNB-discount fee route | unknown | high if account exists | continuous | low | 6 | unknown | Fee tier can change hurdle materially; needs official account availability. |

## Evidence By Opportunity

### 1. Automatic Market Discovery

- `scripts/market_probe.py` scanned 10 venues and 10,240 markets using public endpoints.
- USDT common high-liquidity bases include BTC, ETH, SOL, XRP, XLM, NEAR, DOGE, SUI, WLD, HBAR, TON, BCH, DOT, AAVE, ONDO, ADA, LINK, SEI, UNI, INJ, FET, LTC.
- Raw ticker routes generated many absurd positives, proving that ticker-only ranking is unsafe.
- Direct depth validation killed the first apparent `XLM/USDT` positive.

Code to touch:

- `scripts/market_probe.py`
- `src/feeds.rs`
- `src/strategy.rs`
- future `src/discovery.rs`

Tests to add:

- symbol normalization
- stale ticker rejection
- depth-adjusted route ranking
- min-notional filtering
- duplicate market dedupe

### 2. Coinbase INTX Spot-Perp Funding

Evidence from sub-agent using official Coinbase INTX docs:

- BTC-PERP/BTC-USDC predicted funding around `0.0010%/h`, basis entry around `+3 bps`, perp notional around `$3.7B`.
- ETH-PERP/ETH-USDC predicted funding around `0.0012%/h`, basis around `+5.3 bps`, perp notional around `$2.4B`.
- DOGE-PERP/DOGE-USDC predicted funding around `0.0017%/h`, basis around `+3 bps`, perp notional around `$95M`.
- Fees: INTX perps `2 bps maker / 4 bps taker`; spot `0 bps maker / 2 bps taker`.

Latest public probe:

- Added `scripts/funding_probe.py`.
- Current conservative one-period round-trip proxy scanned 47 spot/perp routes across Binance, Bybit, OKX, and Coinbase INTX.
- Best INTX candidates were still negative after taker entry + taker exit reserve:
  - `ETH-USDC / ETH-PERP`: about `-6.2 bps`, perp notional about `$2.47B`
  - `BTC-USDC / BTC-PERP`: about `-8.0 bps`
  - `DOGE-USDC / DOGE-PERP`: about `-7.8 bps`
- Decision: MEASURE, not execute. It becomes executable only with maker entry/exit, better funding, or account-specific fee improvement.

Sources:

- Coinbase INTX fees: https://help.coinbase.com/en/international-exchange/trading-deposits-withdrawals/international-exchange-fees
- Coinbase INTX instruments/funding API: https://docs.cdp.coinbase.com/api-reference/international-exchange-api/rest-api/instruments/list-instruments

Code to touch:

- new `scripts/funding_probe.py`
- new `src/funding.rs`
- dashboard funding/basis panel

Tests:

- funding sign/direction
- entry basis after fees
- maker/taker scenario comparison
- stop if funding flips

### 3. BCH/TRX/WLD Funding Carry

Public funding probe found:

- BCH Binance perp funding about `-8.1 bps/period`; perp mark about `-4.7 bps` below spot.
- TRX Bybit funding about `-7.3 bps/period`; perp mark about `-11.8 bps` below spot.
- WLD Binance/Bybit funding about `-4` to `-5 bps/period`; perp mark about `-11` to `-18 bps` below spot.

Latest public probe:

- `scripts/funding_probe.py` still ranked WLD/TRX/BCH near the top among Binance/Bybit/OKX because funding and basis are non-trivial.
- Conservative round-trip proxy remained negative:
  - Bybit `WLD`: about `-13.0 bps`
  - Bybit `TRX`: about `-15.6 bps`
  - Binance `WLD`: about `-15.1 bps`
  - Binance `BCH`: about `-19.3 bps`

Interpretation:

- Negative funding means long perp receives funding, but hedge requires short spot or borrow.
- This can be profitable only if borrow cost + execution + exit risk are less than funding carry.

Sources:

- Binance mark/funding API: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
- Bybit ticker funding fields: https://bybit-exchange.github.io/docs/v5/market/tickers
- OKX funding API: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate

### 4. Bitfinex Zero-Fee Cross-Exchange

Official Bitfinex page says:

- spot and margin trading have zero maker and taker fees,
- all customers are eligible,
- no volume/token/tier requirement.

Source:

- https://www.bitfinex.com/zero-fee-trading/

Probe result:

- Ticker-level `XLM/USD OKX -> Bitfinex` looked slightly positive.
- Direct depth check turned it negative:
  - $100: about `-24 bps`
  - $500: about `-31 bps`
- `XRP/USD Crypto.com -> Bitfinex` was closer, but still negative:
  - $100-$500: about `-3 bps`
- Latest ticker probe surfaced `SOL/USD Crypto.com -> Bitfinex` at only about `+0.4 bps` after fee/latency assumptions.
- Direct depth check killed it too:
  - $100: about `-4.4 bps`
  - $500: about `-4.7 bps`
  - $1k: about `-4.8 bps`
  - $5k: about `-5.9 bps`

Decision:

- DO_NOW scanner expansion, not immediate trading.

### 5. MEXC Low-Fee Altcoin Measurement

Evidence:

- MEXC has many USDT markets and low advertised spot taker fees in public fee pages.
- Probe found MEXC in many near-top routes for XLM, HBAR, SUI, BCH, INJ, FET, WLD.
- However, depth/stale validation is mandatory.

Sources:

- MEXC fees: https://www.mexc.com/en-US/fee
- MEXC Spot API: https://mexcdevelop.github.io/apidocs/spot_v3_en/

Decision:

- MEASURE. Do not trade until depth + duration are positive.

### 6. Bitso MXN Basis

Evidence from sub-agent:

- Bitso `btc_mxn` vs implied USD/USDT routes showed only about `-8` to `+10 bps` gross.
- Bitso low-volume taker is about `78 bps`, so taker-taker cycles are deeply negative.
- Bitso `usd_mxn` and `usdt_mxn` differ enough to warrant basis monitoring, not execution.

Sources:

- Bitso books/fees from `available_books`: https://api.bitso.com/v3/available_books/
- Bitso fees docs: https://bitso.com/fees
- Banxico FIX reference: https://www.banxico.org.mx/tipcamb/main.do?page=tip&idioma=en

Decision:

- MEASURE for dashboard and future maker/basis; KILL taker execution.

### 7. Maker-Taker Hybrid

Hypothesis:

- Rest one leg as maker, hedge when filled, reducing fee drag.

Why not now:

- Requires queue/fill probability, adverse selection model, cancel/reprice logic, inventory risk, and private order management.

Decision:

- LATER unless no other route survives.

### 8. Triangular MEXC Benchmark

Evidence:

- Sub-agent measured MEXC `USDT -> BTC -> USDC -> USDT` and `USDT -> ETH -> USDC -> USDT`.
- Raw edges around `+1.5` to `+2.1 bps` are far below 3-leg fee hurdle.

Decision:

- MEASURE as rejection proof; not execution.

### 9. CEX-DEX Base `cbBTC/USDC`

Evidence:

- Base `cbBTC/USDC` pools have meaningful liquidity, but aggregator fees, approvals, gas, MEV, quote TTL, and settlement make execution too large for 48h.

Sources:

- 0x Swap API: https://docs.0x.org/docs/0x-swap-api/introduction
- Coinbase cbBTC: https://www.coinbase.com/cbbtc

Decision:

- LATER read-only panel; KILL execution for challenge.

### 10. Account-Specific Fee Opportunity

Hypothesis:

- If Pedro has low-fee account tiers, BNB/BGB/CRO discounts, Binance.US access, or Bitfinex access, the economics change materially.

Decision:

- LATER until account availability is known. Add private fee fetchers after public demo.

## Initial Config Recommended

### Discovery

```text
quotes = USDT, USDC, USD, MXN
min_24h_quote_volume = 100_000
min_executable_notional_usd = 100
preferred_notional_steps = 100, 500, 1000, 5000
min_positive_duration_ms = 2000
latency_haircut_bps = 2 for USDT/USDC, 4 for USD/MXN
```

### Exchanges

```text
DO_NOW spot: Binance, Bybit, OKX, MEXC, Gate, Bitget, Crypto.com, Bitfinex, Bitso
DO_NOW funding: Binance futures, Bybit linear, OKX swap, Coinbase INTX if public access works
LATER: KuCoin live adapter, CEX-DEX Base, maker execution
```

### Pairs / Assets

```text
Core spot: BTC, ETH, SOL, XRP, DOGE, LTC
Expansion: XLM, HBAR, SUI, BCH, TRX, WLD, ONDO, INJ, FET, AAVE, ADA, LINK, SEI, NEAR, TON
Funding: BTC, ETH, DOGE on INTX; BCH, TRX, WLD, ONDO, OP, INJ, AAVE, ARB on Binance/Bybit/OKX
MXN: btc_mxn, eth_mxn, sol_mxn, usd_mxn, usdt_mxn, btc_usd, btc_usdt
```

### Fee Assumptions

- Use exchange taker defaults unless account-specific API says otherwise.
- Bitfinex spot: `0 bps` maker/taker per official zero-fee page.
- MEXC: use `5 bps` taker until official account/pair fee is verified.
- Bitso MXN low-volume: about `78 bps` taker from `available_books`.
- Do not use maker fees unless route is explicitly post-only and fill-probability modeled.
