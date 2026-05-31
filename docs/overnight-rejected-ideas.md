# Overnight Rejected Ideas

Checked: 2026-05-29.

This file is intentionally brutal. A killed idea can still be useful as a dashboard rejection proof, but it should not consume implementation time as a primary profit path.

## KILL - Retail USD Spot Taker Arbitrage

- **Idea**: Coinbase/Kraken/Gemini USD spot cross-exchange taker arbitrage.
- **Reason**: negative after fees.
- **Evidence**: real-fee scanner run showed Coinbase/Gemini routes deeply negative. Coinbase Intro 1 and Gemini ActiveTrader low-volume taker fees are `120 bps`; Kraken low-volume taker is `40 bps`.
- **Decision**: KILL for execution. Keep as rejected-opportunity demo only.

## KILL - Bitso MXN Taker-Taker Arbitrage

- **Idea**: Bitso `BTC/MXN`, `BTC/USD`, `BTC/USDT`, `USD/MXN`, `USDT/MXN` cycles as aggressive taker trades.
- **Reason**: negative after fees.
- **Evidence**: snapshot found gross spreads only around `-8` to `+10 bps`, while Bitso low-volume taker fee is about `78 bps` per leg. Cycles need roughly `166-192 bps` before they break even.
- **Decision**: KILL as immediate execution. MEASURE as basis dashboard.

## KILL - Triangular Taker-Only On Liquid Majors

- **Idea**: intra-exchange triangles like `USDT -> BTC/ETH/SOL -> USDC -> USDT` on Binance/OKX/Bybit/KuCoin/MEXC.
- **Reason**: 3 taker legs create a fee hurdle too large for liquid majors.
- **Evidence**: sub-agent measured liquid triangles around `-2` to `+2 bps` raw. Break-even is about `30 bps` at `10 bps/leg`, `15 bps` at `5 bps/leg`, and `6 bps` at `2 bps/leg`.
- **Decision**: KILL as executor. DO_NOW as rejection benchmark only.

## KILL - Top-Of-Book Ticker Edges Without Depth

- **Idea**: route off public all-ticker/bookTicker best bid/ask.
- **Reason**: fake edge from stale tickers, mismatched symbols, shallow depth, or partial top-of-book.
- **Evidence**:
  - `XLM/USDT` initially appeared `+6` to `+18 bps` net in broad probe.
  - Direct depth check turned it negative for $500 notional.
  - `SOL/USD Crypto.com -> Bitfinex` later appeared about `+0.4 bps` net at ticker level, but direct depth validation was about `-4.4` to `-5.9 bps` from $100 to $5k notional.
  - Many absurd routes were symbol mismatches or stale tickers (`TROLL`, `ELON`, `VON`, etc.).
- **Decision**: KILL raw ticker-only ranking. Require depth + duration.

## KILL - Current Taker Round-Trip Funding Windows

- **Idea**: open spot/perp funding carry immediately using taker entry and taker exit assumptions.
- **Reason**: negative after fees and exit reserve in the current public probe.
- **Evidence**: `scripts/funding_probe.py` scanned 47 public routes across Binance, Bybit, OKX, and Coinbase INTX. Best routes were still negative under conservative round-trip assumptions:
  - Coinbase INTX `ETH`: about `-6.2 bps`
  - Coinbase INTX `DOGE`: about `-7.8 bps`
  - Coinbase INTX `BTC`: about `-8.0 bps`
  - Bybit `WLD`: about `-13.0 bps`
  - Bybit `TRX`: about `-15.6 bps`
- **Decision**: KILL immediate taker execution. MEASURE for maker/fee-tier/stronger-funding windows.

## KILL - CEX-DEX As 48h Primary Execution

- **Idea**: arbitrage CEX books versus Base/Ethereum DEX pools.
- **Reason**: too slow and too execution-heavy for this challenge window.
- **Evidence**: on-chain routes require wallet approvals, signed transactions, gas, inclusion latency, MEV/slippage protection, and inventory. Aggregator quotes can include fees and expire quickly.
- **Decision**: KILL execution. LATER add read-only CEX-DEX panel for rejection proof.

## KILL - Bridge Arbitrage As Hot Path

- **Idea**: bridge USDC/USDT/BTC wrappers between chains and CEXes to close price gaps.
- **Reason**: settlement and bridge latency make it rebalance, not hot-path arbitrage.
- **Decision**: KILL for 48h. LATER as inventory movement/rebalance research.

## KILL - Treating USD, USDT, USDC, MXN As Equivalent

- **Idea**: compare USD and USDT or MXN implied prices directly.
- **Reason**: cross-lane basis, custody, redemption, and FX spread create real risk.
- **Evidence**: Bitso `USD/MXN` and `USDT/MXN` had different premiums versus Banxico FIX; USDT/USD deviations can move enough to erase small spreads.
- **Decision**: KILL unless explicit basis/haircut module is active.

## KILL - Maker/Rebate As Primary Without Fill Model

- **Idea**: assume maker fees, rebates, or post-only fills without modeling queue and adverse selection.
- **Reason**: maker P&L depends on fill probability, queue position, cancellation latency, and being picked off.
- **Decision**: LATER. It can become high EV, but not before a maker-fill simulator exists.

## KILL - Micro-Alt "Profits" Below $100 Depth

- **Idea**: execute huge percentage discrepancies in obscure assets.
- **Reason**: low liquidity, bad symbol normalization, halted/isolated books, min-notional and withdrawal issues.
- **Evidence**: broad probe surfaced giant fake net bps on tiny/stale markets; these are not executable.
- **Decision**: KILL unless depth supports at least $100-$500 and edge persists.

## KILL - Banxico FIX As Executable FX

- **Idea**: use Banxico FIX directly as execution price for MXN/USD comparison.
- **Reason**: official reference rate, not executable liquidity.
- **Decision**: Use FIX only as context. Executable FX must come from Bitso `usd_mxn`, `usdt_mxn`, or real FX venue.
