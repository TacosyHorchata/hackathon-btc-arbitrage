# Agent 2 Opportunity Candidates

Updated: 2026-05-29 12:16 CST

## Candidate A2-001 - XMR/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy `XMR-USDT` on KuCoin, sell `XMRUSDT` on MEXC
- quote lane: USDT
- why edge might exist: XMR is fragmented and less universally supported than BTC/ETH/SOL; order books can lag across mid-tier venues.
- public data quality: medium. REST depth is available on both venues; needs WebSocket depth before any execution decision.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: long sample average +0.256 bps at 0.5 XMR, -0.648 bps at 1 XMR, -2.512 bps at 2 XMR.
- executable notional estimate: no robust executable notional. Tiny bucket is too noisy and below threshold.
- frequency/duration evidence or proxy: 120 samples over about 11 minutes; 0.5 XMR positive 60.8%, 1 XMR positive 55.0%, 2 XMR positive 25.0%.
- implementation effort: 4-8 hours to add depth adapters and route scoring if generic discovery exists; 8-14 hours if built as a special case.
- inventory/funding requirements: USDT on KuCoin, XMR on MEXC; XMR inventory is regulatory/account-risk heavy and rebalancing can be slow.
- risks: privacy-coin restrictions, exchange availability in Pedro's jurisdiction, thin top bid on MEXC, REST staleness, withdrawal pauses, false positive from short windows.
- confidence: high for rejection.
- verdict: `KILL` as a direct route. Keep the measurement pattern for discovery engine design.

## Candidate A2-002 - Strict Automatic Market Discovery For Long-Tail USDT

- approach type: market discovery / cross-exchange spot
- route/assets/exchanges: all common USDT markets across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com
- quote lane: USDT
- why edge might exist: long-tail markets produce more apparent dislocations than BTC, but most are fake until symbol identity, depth, fees, and transfer/inventory constraints are checked.
- public data quality: medium. Tickers are easy; asset identity and contract-equivalence are the weak point.
- fee assumptions: 5-20 bps per taker side depending exchange; use conservative venue defaults until authenticated fee endpoints are available.
- estimated net bps: naive scanner found huge positives, but many were invalid due same ticker representing different assets or broken market data.
- executable notional estimate: unknown until depth and identity checks are added; current evidence says do not trust top-50 naive routes.
- frequency/duration evidence or proxy: 1 market snapshot showed many apparent dislocations; filtered high-liquidity/sane routes produced only a few candidates.
- implementation effort: 6-10 hours for symbol allowlist + asset metadata validation + depth probes; more if contract-address verification is added for every venue.
- inventory/funding requirements: fragmented quote and base inventory across expansion venues.
- risks: ticker collisions, delisted or halted markets, fake volume, regional restrictions, API quirks.
- confidence: medium.
- verdict: `MEASURE`.

## Candidate A2-003 - Spot-Perp Funding Capture Monitor

- approach type: spot-perp basis and funding capture
- route/assets/exchanges: Binance USD-M, Bybit linear, OKX swaps versus spot inventory for BTC/ETH/SOL/XRP/DOGE
- quote lane: USDT
- why edge might exist: short perp + long spot can collect positive funding while remaining market-neutral if basis and funding cover fees and execution risk.
- public data quality: high for funding/mark/index; private execution and margin risk still need account setup.
- fee assumptions: taker or maker fees on spot and perp open/close; funding currently 0.08-1.00 bps per 8h.
- estimated net bps: currently unattractive for immediate entry. Re-measurement showed perps below index and positive funding too small to overcome entry headwind plus fees quickly.
- executable notional estimate: high on BTC/ETH/SOL if accounts are ready, but capital is locked across spot and perp legs.
- frequency/duration evidence or proxy: public funding snapshots across Binance, Bybit, OKX at 2026-05-29 02:55 CST and 03:45 CST.
- implementation effort: 10-20 hours because it requires perp adapters, margin/funding accounting, liquidation risk controls, and close logic.
- inventory/funding requirements: long spot inventory plus perp margin; collateral management required.
- risks: negative entry basis, funding flips, liquidation/margin risk, regional availability, leverage/account permissions.
- confidence: medium.
- verdict: `LATER`.

## Candidate A2-004 - Bitso MXN/USD/USDT Basis

- approach type: MXN FX basis / same-venue triangular
- route/assets/exchanges: Bitso `btc_mxn`, `btc_usd`, `btc_usdt`, `usd_mxn`, `usdt_mxn`, `usd_usdt`, plus ETH/SOL/XRP checks
- quote lane: MXN/USD/USDT cross-lane
- why edge might exist: local fiat rails and MXN liquidity can create divergence versus USD or USDT implied prices.
- public data quality: medium-high. Bitso public tickers are clean; order book depth still needed for serious sizing.
- fee assumptions: Bitso taker around 50 bps default, plus explicit FX/cross-lane haircut.
- estimated net bps: immediate routes were negative or single-digit gross bps before fees; XRP gross about +7.1 bps still dies after fees.
- executable notional estimate: not relevant for current signal because net is negative after costs.
- frequency/duration evidence or proxy: one public ticker snapshot around 2026-05-29 02:54 CST.
- implementation effort: 4-8 hours to build an explicit FX module, but not worth prioritizing until gross dislocation exceeds fee burden.
- inventory/funding requirements: MXN, USD/USDT, and base asset balances inside Bitso; external comparisons require separate venue inventory.
- risks: cross-lane accounting errors, Bitso fee tier, fiat settlement constraints, stablecoin redemption assumptions.
- confidence: medium-high for rejection.
- verdict: `KILL` for immediate profit; `LATER` for monitoring.

## Candidate A2-005 - AI/USDT Binance -> OKX

- approach type: cross-exchange spot altcoin
- route/assets/exchanges: buy `AIUSDT` on Binance, sell `AI-USDT` on OKX
- quote lane: USDT
- why edge might exist: the naive snapshot showed about +865 bps gross.
- public data quality: high enough to reject after official listing docs.
- fee assumptions: 10 bps taker on each side plus 2 bps latency haircut.
- estimated net bps: invalid. Naive depth showed +640 to +790 bps depending size, but assets are different.
- executable notional estimate: invalid.
- frequency/duration evidence or proxy: official identity check is enough to reject.
- implementation effort: 1-2 hours to verify exchange metadata and depth; do that before any scanner promotion.
- inventory/funding requirements: USDT on Binance, AI token on OKX if real.
- risks: ticker collision confirmed. Binance `AI` is Sleepless AI; OKX `AI` is Gensyn.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-006 - IO/USDT Binance -> Bybit Event Window

- approach type: event-window cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy `IOUSDT` on Binance, sell `IOUSDT` on Bybit
- quote lane: USDT
- why edge might exist: fast repricing/new-listing-style dislocation between high-liquidity venues. The edge can be large but collapses quickly.
- public data quality: medium-high. Binance and Bybit public depth and metadata are clean; still need stronger asset identity and deposit/withdrawal status checks before execution.
- fee assumptions: Binance taker 10 bps, Bybit taker 10 bps, latency haircut 2 bps.
- estimated net bps: first minutes showed roughly +190 to +250 bps at 1,000 USDT, but the 10-minute median was negative.
- executable notional estimate: early window supported 1,000 to 5,000 USDT net-positive; 10,000 USDT failed as depth moved.
- frequency/duration evidence or proxy: 120 samples over about 11 minutes; 1,000 USDT bucket positive 40%, average +26.006 bps, median -9.491 bps.
- implementation effort: 4-8 hours to turn this into an event detector if existing depth adapters are available; more for live execution and inventory reservation.
- inventory/funding requirements: USDT on Binance, IO inventory on Bybit. This is only executable if inventory is pre-positioned before the window appears.
- risks: edge collapse, one-leg fill, Bybit depth disappearing, deposit/withdrawal pauses, regional restrictions, symbol identity mistakes, top-of-book latency.
- confidence: medium that event windows exist; low for manual execution.
- verdict: `MEASURE`. Treat as `DO_NOW` only for scanner/event-detection design, not live trading.

## Candidate A2-007 - DYDX/USDT Binance -> OKX

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: Binance `DYDXUSDT` and OKX `DYDX-USDT`
- quote lane: USDT
- why edge might exist: filtered snapshot showed a small positive top-of-book spread.
- public data quality: medium-high.
- fee assumptions: 10 bps taker on each side plus 2 bps latency haircut.
- estimated net bps: current depth negative in both directions, from about -27 bps at 100 USDT to worse at larger buckets.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: small spreads vanish before depth validation.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-008 - MMT/USDT OKX -> Binance

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: OKX `MMT-USDT` and Binance `MMTUSDT`
- quote lane: USDT
- why edge might exist: filtered snapshot showed a small positive top-of-book spread.
- public data quality: medium-high.
- fee assumptions: 10 bps taker on each side plus 2 bps latency haircut.
- estimated net bps: current depth was negative after costs; about -12.6 bps at 100 USDT and -14.3 bps at 1,000 USDT in the best direction.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: small spreads vanish; venue order books thin.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-009 - ALLO/USDT Gate -> Bitget

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: Gate `ALLO_USDT`, Bitget `ALLOUSDT`
- quote lane: USDT
- why edge might exist: refreshed scan showed a small positive spread across multiple ALLO venues.
- public data quality: medium-high. Gate metadata includes name, trade status, mins, precision, and fee.
- fee assumptions: Gate metadata fee `0.2` (20 bps) plus Bitget assumed 10 bps and latency haircut.
- estimated net bps: current depth negative; about -26.1 bps at 100 USDT in the best direction.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: generic fee assumptions understate Gate cost; small spread vanishes under real fees.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-010 - GENIUS/USDT MEXC/Binance -> Bitget

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: MEXC `GENIUSUSDT`, Binance `GENIUSUSDT`, Bitget `GENIUSUSDT`
- quote lane: USDT
- why edge might exist: refreshed scan showed a modest positive Bitget sell route.
- public data quality: medium-high. MEXC metadata exposes full name, contract address, status, and taker commission.
- fee assumptions: MEXC taker 5 bps, Binance/Bitget assumed 10 bps, latency haircut 2 bps.
- estimated net bps: current depth negative; about -20.9 bps at 100-1,000 USDT for MEXC buy -> Bitget sell.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: spread vanished before depth validation.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-011 - BSB/USDT Bitget -> Bybit

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: Bitget `BSBUSDT`, Bybit `BSBUSDT`
- quote lane: USDT
- why edge might exist: refreshed scan showed a small positive Bitget buy -> Bybit sell spread.
- public data quality: medium-high. Bybit metadata is clean; Bitget ticker/depth are public.
- fee assumptions: Bitget taker 10 bps, Bybit taker 10 bps, latency haircut 2 bps.
- estimated net bps: current depth negative; about -21.6 bps at 50 USDT and -22.3 bps at 100 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: small top-of-book spreads vanish under depth/fees.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-012 - SD/USDT OKX -> Bybit

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: OKX `SD-USDT`, Bybit `SDUSDT`
- quote lane: USDT
- why edge might exist: refreshed scan showed a small positive OKX buy -> Bybit sell spread.
- public data quality: medium. Bybit has `stTag=1`, which is a risk flag.
- fee assumptions: OKX taker 10 bps, Bybit taker 10 bps, latency haircut 2 bps.
- estimated net bps: current depth negative; about -29.3 bps at 50 USDT in the best direction.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: Bybit special-treatment tag, thin bid depth, stale top-of-book signal.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-013 - CTR/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: Gate `CTR_USDT`, MEXC `CTRUSDT`
- quote lane: USDT
- why edge might exist: refreshed scan showed a small positive Gate buy -> MEXC sell spread.
- public data quality: high enough to reject. Gate and MEXC both identify `CTR` as Citrea; MEXC exposes contract address.
- fee assumptions: Gate metadata fee `0.2` (20 bps), MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: current depth negative; Gate buy -> MEXC sell about -66.6 bps at 50 USDT; reverse about -36.3 bps.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: Gate fee makes small spreads unusable.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-014 - BDX/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: KuCoin `BDX-USDT`, MEXC `BDXUSDT`
- quote lane: USDT
- why edge might exist: refreshed scan showed a small positive KuCoin buy -> MEXC sell spread.
- public data quality: medium-high. MEXC identifies full name `Beldex`; KuCoin metadata says trading enabled.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: current depth negative; KuCoin buy -> MEXC sell about -48.3 bps at 50 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live depth validation after refreshed scan.
- implementation effort: no special work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: tiny top-of-book signals vanish; MEXC top bid size was effectively unusable at best price.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-015 - Liquid USDT/USDC Triangular Taker Arb

- approach type: triangular
- route/assets/exchanges: Binance and OKX triangles using `BASE/USDT`, `BASE/USDC`, and `USDC/USDT`; bases BTC, ETH, SOL, XRP, BNB, DOGE, ADA, LINK where available.
- quote lane: USDT/USDC explicit same-venue conversion.
- why edge might exist: stablecoin basis and cross-book latency can occasionally create intra-exchange cycles.
- public data quality: high for top-of-book; depth not needed after top-of-book is already negative.
- fee assumptions: 10 bps taker per leg, 3 legs.
- estimated net bps: all measured cycles negative after fees; most clustered around -29 to -33 bps.
- executable notional estimate: none under taker-only execution.
- frequency/duration evidence or proxy: one public top-of-book sweep across Binance and OKX liquid bases.
- implementation effort: high if implemented correctly, because triangle scanning needs precomputed cycles and per-leg execution logic.
- inventory/funding requirements: balances in USDT, USDC, and base assets if executing without transfer.
- risks: three-leg execution risk, fees, stale books, partial fills.
- confidence: high for taker-only rejection.
- verdict: `KILL` for taker-only. `LATER` for maker/rebate version.

## Candidate A2-016 - Crypto.com -> Bitfinex USD Routes

- approach type: cross-exchange spot / fee-model validation
- route/assets/exchanges: examples from refreshed scan: Crypto.com `XRP_USD`/`SOL_USD` -> Bitfinex `tXRPUSD`/`tSOLUSD`
- quote lane: USD
- why edge might exist: USD books across regional/global venues may differ slightly.
- public data quality: medium. Crypto.com books are public; Bitfinex books are public; fee model is the blocker.
- fee assumptions: current `market_probe.py` uses Bitfinex taker `0.0` bps, which is unsafe. Crypto.com default in repo is 7.5 bps.
- estimated net bps: refreshed gross around 12 bps, which is too small to survive realistic Bitfinex taker fees if not zero.
- executable notional estimate: not evaluated because fee assumption invalidates ranking.
- frequency/duration evidence or proxy: refreshed ticker scan only.
- implementation effort: first fix fee assumptions; then depth sample.
- inventory/funding requirements: USD on Crypto.com, asset inventory on Bitfinex.
- risks: fee assumption bug, regional/account availability, USD rails, Bitfinex tier dependence.
- confidence: medium for rejection until fee model is corrected.
- verdict: `MEASURE_FEE_FIRST`, not a profit candidate.

## Candidate A2-017 - USDT/USD Cross-Exchange Stablecoin Basis

- approach type: cross-lane basis / stablecoin route
- route/assets/exchanges: Coinbase, Bitstamp, Kraken, Bitso USDT/USD-equivalent books
- quote lane: USD/USDT explicit conversion
- why edge might exist: stablecoin depeg, local fiat rails, or venue-specific USD liquidity can create basis.
- public data quality: medium-high. Public books are available; Coinbase fee tier is conservative and expensive.
- fee assumptions: Coinbase 120 bps, Bitstamp 40 bps, Kraken 40 bps, Bitso 50 bps, plus 1 bps latency.
- estimated net bps: best observed gross about +3.5 bps, but net about -87.5 bps.
- executable notional estimate: none under taker execution.
- frequency/duration evidence or proxy: one public depth snapshot across four venues.
- implementation effort: low to monitor, not worth execution work now.
- inventory/funding requirements: USD on buy venue and USDT inventory on sell venue; quote-lane accounting required.
- risks: fiat rails, stablecoin redemption assumptions, fee tiers, lane conversion errors.
- confidence: high for taker-route rejection.
- verdict: `KILL`.

## Candidate A2-018 - USDC/USD Cross-Exchange Stablecoin Basis

- approach type: cross-lane basis / stablecoin route
- route/assets/exchanges: Kraken `USDC/USD` -> Bitstamp `usdcusd`
- quote lane: USD/USDC explicit conversion
- why edge might exist: USDC/USD fiat venue basis can appear during stablecoin stress or local liquidity gaps.
- public data quality: medium. Kraken and Bitstamp books worked; Coinbase exchange endpoint for `USDC-USD` returned 404 in this probe.
- fee assumptions: Kraken 40 bps, Bitstamp 40 bps, plus 1 bps latency.
- estimated net bps: about +0.5 bps gross, about -80.5 bps net.
- executable notional estimate: none under taker execution.
- frequency/duration evidence or proxy: one public depth snapshot.
- implementation effort: low to monitor, not worth execution work now.
- inventory/funding requirements: USD on Kraken and USDC on Bitstamp for the measured direction.
- risks: fiat rails, transfer/rebalance constraints, fee tiers.
- confidence: high for taker-route rejection.
- verdict: `KILL`.

## Candidate A2-019 - Immediate Spot-Perp Funding Capture

- approach type: spot-perp basis / funding capture
- route/assets/exchanges: Binance USD-M, Bybit linear, OKX USDT swaps; BTC, ETH, SOL, XRP, DOGE
- quote lane: USDT
- why edge might exist: positive funding pays shorts while long spot hedges market exposure.
- public data quality: high for mark/index/funding; execution/margin details still private-account dependent.
- fee assumptions: conservative 30 bps round-trip hurdle for spot/perp open and close.
- estimated net bps: negative for the 48h sprint. Current basis is a headwind and funding payback is slow.
- executable notional estimate: not constrained by public liquidity for BTC/ETH/SOL, but not attractive after breakeven math.
- frequency/duration evidence or proxy: one breakeven sweep at 2026-05-29 03:45 CST.
- implementation effort: 10-20 hours minimum with meaningful risk controls.
- inventory/funding requirements: spot inventory, perp margin, collateral management, liquidation buffers.
- risks: funding flip, negative basis, liquidation, account restrictions, borrow/margin assumptions.
- confidence: high for immediate rejection; medium as a future monitor.
- verdict: `KILL` for immediate challenge profit; `LATER` for monitoring.

## Candidate A2-020 - Binance.US Maker/Taker Hybrid

- approach type: maker-taker / low-fee venue expansion
- route/assets/exchanges: Binance.US maker leg versus Binance global, Bybit, or Kraken taker leg on BTC/ETH/SOL/XRP USDT books
- quote lane: USDT
- why edge might exist: Binance.US currently advertises 0 bps maker and 2 bps taker on Advanced Spot pairs, which is materially better than most U.S. retail venues.
- public data quality: high for public books and fee announcement; live account availability still must be confirmed.
- fee assumptions: Binance.US maker 0 bps, Binance.US taker 2 bps, Binance/Bybit taker 10 bps, Kraken taker 40 bps, latency/adverse-selection buffer 2 bps.
- estimated net bps: current major pairs were negative; best measured directions were roughly -9 to -14 bps for Binance.US versus Binance/Bybit and around -40 bps versus Kraken.
- executable notional estimate: not applicable while net is negative; Binance.US BTC top-of-book sizes were also small in the sample.
- frequency/duration evidence or proxy: one public top-of-book sweep across BTC, ETH, SOL, XRP.
- implementation effort: 4-8 hours to add Binance.US public adapter; more for private trading and maker queue/fill modeling.
- inventory/funding requirements: Binance.US account, U.S. availability, USDT/base inventory, and paired inventory on the other venue.
- risks: maker non-fill, adverse selection, queue position, Binance.US liquidity, region/account restrictions, quote-lane separation.
- confidence: medium for venue expansion; high that current static major routes are not profitable.
- verdict: `MEASURE` for venue expansion, `KILL` for immediate static route.

## Candidate A2-021 - WETH/USDC CEX-DEX Route

- approach type: CEX-DEX
- route/assets/exchanges: Ethereum WETH/USDC via ParaSwap public quotes versus Binance `ETHUSDC`
- quote lane: USDC
- why edge might exist: DEX liquidity can lag CEX price during volatility; aggregator quotes expose route/gas quickly without private keys.
- public data quality: medium. ParaSwap quotes are accessible and include gas estimate; execution would require wallet, gas, and MEV/slippage controls.
- fee assumptions: Binance taker 10 bps, ParaSwap quote output, public gasCostUSD from quote, no private API keys.
- estimated net bps: current best measured direction was still negative, roughly -7.4 bps at 5,000 USDC; WETH sell direction was -14 to -22 bps.
- executable notional estimate: none in current snapshot.
- frequency/duration evidence or proxy: one public quote sweep at 0.1, 1, 5, 10 WETH and 1,000/5,000/10,000 USDC.
- implementation effort: 8-16 hours for a safe monitor; much more for execution due wallet, gas, allowance, nonce, MEV, and failed tx handling.
- inventory/funding requirements: on-chain WETH/USDC plus CEX ETH/USDC inventory.
- risks: gas spikes, MEV/sandwich, quote staleness, failed transactions, bridge/rebalance friction, tax/accounting complexity.
- confidence: high for current rejection; medium as a monitor.
- verdict: `KILL` for current route; `MEASURE` as a monitor class.

## Candidate A2-022 - HOOLI/USDT KuCoin -> Gate

- approach type: event-window cross-exchange spot altcoin arbitrage
- route/assets/exchanges: KuCoin `HOOLI-USDT`, Gate `HOOLI_USDT`
- quote lane: USDT
- why edge might exist: fresh hard-filter scan found a positive top-of-book route after excluding previous kills.
- public data quality: medium-high. KuCoin and Gate metadata are public; Gate identifies base name `My Pet Hooligan`.
- fee assumptions: KuCoin taker 10 bps, Gate pair metadata fee `0.2` (20 bps), latency haircut 2 bps.
- estimated net bps: negative after correct fees and depth; about -17.0 bps at 25 USDT, -39.1 bps at 100 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one fresh hard-filter pass plus live depth validation.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: Gate fee was understated by generic discovery model; top-of-book size collapses quickly.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-023 - ULTIMA/USDT MEXC -> KuCoin

- approach type: event-window / cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy `ULTIMAUSDT` on MEXC, sell `ULTIMA-USDT` on KuCoin
- quote lane: USDT
- why edge might exist: persistent venue fragmentation in a lower-liquidity asset; MEXC/Gate pricing was materially below KuCoin for at least 5 minutes.
- public data quality: medium. Public order books and metadata are clean enough to score; chain/rebalance identity needs more due diligence. KuCoin exposes a book timestamp, but local clock skew made absolute age unreliable; MEXC public depth did not expose an exchange timestamp.
- fee assumptions: MEXC taker 5 bps from metadata, KuCoin assumed taker 10 bps from category/coefficient, latency haircut 2 bps.
- estimated net bps: multiple persistence windows confirmed strong edge. Latest targeted 2026-05-29 05:17:36-05:20:05 CST confirmation averaged +300.533 bps at 5,000 USDT and +145.404 bps at 10,000 USDT.
- executable notional estimate: public-book scanner/watch cap can move to 10,000 USDT. Live execution remains blocked until chain/rebalance compatibility and sell-venue inventory are proven.
- frequency/duration evidence or proxy: two 60-sample windows, two 30-sample watch windows, four 20-sample refreshes, and one 30-sample targeted confirmation. Across all windows, 500-5,000 USDT buckets stayed 100% positive. The latest 20-sample refresh had 10,000 USDT 20/20 positive avg +184.409 bps, min +138.382 bps.
- implementation effort: 2-4 hours to add to watchlist if adapters exist; more for identity/chain/rebalance checks.
- inventory/funding requirements: USDT on MEXC and ULTIMA inventory on KuCoin. Hot-path execution requires pre-positioned inventory; do not assume bought MEXC ULTIMA can be transferred to KuCoin immediately.
- risks: chain mismatch/rebalance risk. MEXC metadata gives contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`; Gate also uses SMART `sWd6...` with deposits/withdrawals enabled; KuCoin public currency endpoint shows BEP20 `0x5668a83b46016b494a30dd14066a451e5417a8b8` with deposits/withdrawals enabled. MEXC capital config is key-gated, so public deposit/withdraw status was not verified. Deposits/withdrawals and bridge path must be verified before live execution. Also low liquidity, price-limit rules, regional restrictions, inventory unwind risk.
- confidence: high that the public-book spread existed during the sample; medium-low that it is operationally executable without pre-positioned inventory.
- verdict: `DO_NOW` for scanner/watchlist and due diligence; no live trading. Public-book watch cap: 10,000 USDT.

## Candidate A2-024 - WALLI/USDT KuCoin -> MEXC

- approach type: event-window / cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy `WALLI-USDT` on KuCoin, sell `WALLIUSDT` on MEXC
- quote lane: USDT
- why edge might exist: fee-aware scan showed a large top-of-book spread after excluding Gate/Bitfinex traps.
- public data quality: medium. KuCoin and MEXC metadata are public and aligned enough to measure.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: initial depth showed positive net only at small size, but persistence turned negative.
- executable notional estimate: none. 500 USDT was already 0/30 positive in persistence.
- frequency/duration evidence or proxy: 30 samples over about 2.75 minutes; 50 USDT was only 6/30 positive, 100/250 USDT 3/30 positive, 500 USDT 0/30 positive.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: spread collapsed quickly; small-size-only edge; low liquidity.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-025 - ASSET/USDT KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy `ASSET-USDT` on KuCoin, sell `ASSETUSDT` on MEXC
- quote lane: USDT
- why edge might exist: fee-aware non-Gate scan showed a positive top-of-book route with moderate proxy volume.
- public data quality: medium. KuCoin and MEXC metadata are available; MEXC identifies full name as `REAL`.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: persistence held only in tiny buckets: avg +59.418 bps at 50 USDT and +38.393 bps at 100 USDT; 250 USDT was negative.
- executable notional estimate: 50-100 USDT only, too small to matter.
- frequency/duration evidence or proxy: 20 samples over about 1.8 minutes; 50 and 100 USDT buckets were 20/20 positive, 250 USDT only 2/20 positive.
- implementation effort: no route-specific work warranted beyond using it as a scanner regression case.
- inventory/funding requirements: not worth solving unless a larger bucket appears.
- risks: tiny notional, low liquidity, operational overhead dominates edge.
- confidence: high that the micro-spread existed; high that it is not an execution priority.
- verdict: `LATER` as a micro-route regression case; `KILL` for execution priority.

## Candidate A2-026 - DEUS/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: KuCoin `DEUS-USDT`, MEXC `DEUSUSDT`
- quote lane: USDT
- why edge might exist: fee-aware scan showed a positive top-of-book route before live depth.
- public data quality: weak for identity. MEXC metadata identifies full name `XMAQUINA`, not clearly `DEUS`.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: negative in both directions. Best small bucket was still about -110 bps net.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live depth validation after fee-aware scan.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: possible ticker/branding mismatch, negative depth, low liquidity.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-027 - EUL/USDT Binance <-> KuCoin

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: Binance `EULUSDT`, KuCoin `EUL-USDT`
- quote lane: USDT
- why edge might exist: fee-aware non-Gate scan showed a candidate route after excluding known false positives.
- public data quality: medium-high. Binance and KuCoin symbols are live; KuCoin currency endpoint identifies full name `Euler` and ERC20 contract `0xd9fcd98c322942075a5c3860693e9f4f03aae07b`.
- fee assumptions: Binance taker 10 bps, KuCoin taker 10 bps, latency haircut 2 bps.
- estimated net bps: negative in both directions. Binance buy -> KuCoin sell was about -38.7 bps at 50 USDT and -60.2 bps at 1,000 USDT. KuCoin buy -> Binance sell was about -32.0 bps at 50 USDT and -65.9 bps at 1,000 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata and depth validation after fee-aware scan.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: no positive edge after fees/depth.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-028 - GOMINING/USDT Bitget -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy Bitget `GOMININGUSDT`, sell MEXC `GOMININGUSDT`
- quote lane: USDT
- why edge might exist: Bitget ask was persistently below MEXC bid in small order-book buckets.
- public data quality: medium-high. Bitget symbol is online with taker fee `0.001`; MEXC identifies full name `GoMining`, spot trading allowed, taker commission `0.0005`, and contract `0x7Ddc52c4De30e94Be3A6A0A2b259b2850f421989`.
- fee assumptions: Bitget taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: small buckets persisted: avg +36.898 bps at 50 USDT, +34.570 bps at 100 USDT, +25.229 bps at 250 USDT. The 500 USDT bucket was negative with avg -5.006 bps.
- executable notional estimate: 50-250 USDT only, too small to matter as an execution priority.
- frequency/duration evidence or proxy: 20 samples from 2026-05-29 04:27:43 to 04:29:33 CST; 50/100/250 USDT buckets were 20/20 positive, while 500 USDT was 0/20 positive.
- implementation effort: no route-specific execution work warranted; useful as a scanner regression case for small persistent spreads.
- inventory/funding requirements: not worth solving unless larger buckets appear.
- risks: tiny capacity, inventory overhead, low-book-depth fragility.
- confidence: high that the micro-spread existed; high that it is not a priority.
- verdict: `LATER` as a micro-route regression case; `KILL` as an execution priority.

## Candidate A2-029 - CPOOL/USDT Bybit <-> KuCoin

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: Bybit `CPOOLUSDT`, KuCoin `CPOOL-USDT`
- quote lane: USDT
- why edge might exist: fee-aware non-Gate scan showed a candidate route before live depth validation.
- public data quality: medium-high. Bybit symbol is trading with `stTag=0`; KuCoin currency endpoint identifies full name `Clearpool` and ERC20 contract `0x66761fa41377003622aee3c7675fc7b5c1c2fac5`.
- fee assumptions: Bybit taker 10 bps, KuCoin taker 10 bps, latency haircut 2 bps.
- estimated net bps: negative in both directions. Bybit buy -> KuCoin sell was about -34.4 bps at 50 USDT and -51.9 bps at 100 USDT; reverse was about -95.1 bps at 50 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata and depth validation after fee-aware scan.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: KuCoin fee category `2` may be higher than generic assumptions, but the route is already negative under the base model.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-030 - DAG/USDT MEXC <-> KuCoin

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: MEXC `DAGUSDT`, KuCoin `DAG-USDT`
- quote lane: USDT
- why edge might exist: fee-aware non-Gate scan showed a candidate route before live depth validation.
- public data quality: mixed. Identity aligns as `Constellation`, but MEXC metadata returned `isSpotTradingAllowed=false` despite returning a public depth book. KuCoin reports native DAG chain deposits/withdrawals enabled.
- fee assumptions: MEXC taker 5 bps, KuCoin taker 10 bps, latency haircut 2 bps.
- estimated net bps: deeply negative in both directions. MEXC buy -> KuCoin sell was about -310.0 bps at 50 USDT; KuCoin buy -> MEXC sell was about -161.7 bps at 50 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata and depth validation after fee-aware scan.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: MEXC trading-permission flag, negative depth, low-liquidity book.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-031 - VANRY/USDT MEXC -> Binance / KuCoin

- approach type: event-window / cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `VANRYUSDT`, sell Binance `VANRYUSDT` or KuCoin `VANRY-USDT`
- quote lane: USDT
- why edge might exist: fresh fee-aware discovery found MEXC materially below Binance and KuCoin; live depth and a 30-sample window confirmed the gap persisted beyond top-of-book.
- public data quality: high for market data and sell-venue network metadata, medium for buy-venue withdrawal path. MEXC and Binance spot symbols are trading; MEXC exposes ERC20 contract `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`; KuCoin exposes the same ERC20 contract lowercased and has deposits/withdrawals enabled. Binance public web asset metadata identifies `VANRY` as `Vanar`, old code `TVK`, with ERC20 parent `ETH`, deposits enabled, withdrawals enabled, withdrawal fee `65` VANRY, and withdrawal minimum `130` VANRY. MEXC withdrawal status remains unverified because capital config is key-gated.
- fee assumptions: MEXC taker 5 bps from metadata, Binance taker 10 bps, KuCoin assumed taker 10 bps with fee category `3` risk flag, latency haircut 2 bps.
- estimated net bps: MEXC -> Binance 30-sample averages were +931.414 bps at 500 USDT, +902.229 bps at 1,000 USDT, +779.459 bps at 2,500 USDT, +550.565 bps at 5,000 USDT, and +231.097 bps at 10,000 USDT. MEXC -> KuCoin averaged +902.519 bps at 500 USDT and +255.435 bps at 5,000 USDT, but 10,000 USDT was negative.
- executable notional estimate: initial watch cap 10,000 USDT for MEXC -> Binance. For MEXC -> KuCoin, treat 2,500 USDT as the firm cap and 5,000 USDT as opportunistic only when live depth threshold is positive.
- frequency/duration evidence or proxy: 30-sample persistence plus four later 20-sample refreshes and one 30-sample targeted confirmation. MEXC -> Binance was positive through 10,000 USDT in all windows; latest refresh averaged +242.131 bps at 10,000 USDT with min +155.345 bps. MEXC -> KuCoin had 2,500 USDT 30/30 positive in targeted confirmation; 5,000 USDT was 20/20 positive in the latest refresh but with a thin min of +3.898 bps.
- implementation effort: 2-4 hours to add to watchlist if MEXC/Binance/KuCoin adapters exist; more for venue-network and inventory checks.
- inventory/funding requirements: USDT on MEXC and VANRY inventory already on Binance or KuCoin. Do not assume MEXC-bought VANRY can be sold on the other venue without a verified transfer/rebalance path.
- risks: Binance global account/region availability, MEXC withdrawal status not publicly verified, KuCoin fee category `3`, low price/large base quantity precision, inventory unwind risk if MEXC price normalizes before rebalance.
- confidence: high that the public-book spread existed during the sample; medium that it is operationally executable with pre-positioned inventory; low until account/region and transfer paths are verified.
- verdict: `DO_NOW` for scanner/watchlist and operational due diligence; no live trading.

## Candidate A2-032 - HOOLI/USDT MEXC -> Bitget

- approach type: capped event-window / cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `HOOLIUSDT`, sell Bitget `HOOLIUSDT`
- quote lane: USDT
- why edge might exist: fresh fee-aware discovery found MEXC materially below Bitget; live depth confirmed a persistent pocket through 500 USDT.
- public data quality: high enough to reject operationally. MEXC identifies full name `Hooli` and SOL contract `FPJfY8mMTRwaePD2f46TFLqVov4X9svBaUgR1a8oTwTF`; Bitget public coin metadata reports the same SOL contract, but deposits are disabled.
- fee assumptions: MEXC taker 5 bps from metadata, Bitget taker 10 bps from metadata, latency haircut 2 bps.
- estimated net bps: 20-sample averages were +1,193.131 bps at 50 USDT, +1,032.435 bps at 100 USDT, +903.585 bps at 250 USDT, and +501.616 bps at 500 USDT. The 1,000 USDT bucket was negative, avg -784.990 bps.
- executable notional estimate: none for repeatable arbitrage while Bitget deposits are disabled. Prior depth supported only a 500 USDT inventory-only pocket.
- frequency/duration evidence or proxy: 20 samples from 2026-05-29 04:46:33 to 04:48:22 CST; 50-500 USDT buckets were 20/20 positive, while 1,000 USDT was 0/20 positive.
- implementation effort: low if MEXC/Bitget adapters exist; route-specific execution work not justified before VANRY/ULTIMA.
- inventory/funding requirements: USDT on MEXC and HOOLI inventory already on Bitget. Bitget deposits are disabled, so MEXC-bought HOOLI cannot replenish the sell venue through a public deposit lane.
- risks: low notional ceiling, Bitget deposit-disabled status, MEXC/Bitget account availability, inventory unwind risk, sharp depth cliff at 1,000 USDT.
- confidence: high that the capped public-book spread existed; high that current repeatable-route rejection is correct.
- verdict: `KILL` as a repeatable route; revisit only if Bitget deposits reopen and depth still holds.

## Candidate A2-033 - GUA/USDT MEXC -> Gate

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `GUAUSDT`, sell Gate `GUA_USDT`
- quote lane: USDT
- why edge might exist: fresh fee-aware discovery found MEXC below Gate after loading Gate pair fee metadata.
- public data quality: high enough to reject. MEXC and Gate identify the asset as `SUPERFORTUNE` with matching BSC contract case-insensitively. Gate pair is tradable, but Gate currency metadata reports deposits disabled.
- fee assumptions: MEXC taker 5 bps from metadata, Gate pair fee `0.2` = 20 bps, latency haircut 2 bps.
- estimated net bps: positive through 2,500 USDT in live depth: about +738.2 bps at 50 USDT, +710.4 bps at 500 USDT, +685.3 bps at 1,000 USDT, and +412.7 bps at 2,500 USDT. The 5,000 USDT bucket was negative.
- executable notional estimate: none under current operational constraints because Gate deposits are disabled.
- frequency/duration evidence or proxy: one live metadata and depth validation after corrected fee-aware scan; no persistence window because deposit-disabled status kills the current route.
- implementation effort: no route-specific execution work warranted while Gate deposits are disabled.
- inventory/funding requirements: would require GUA inventory already on Gate; public metadata says deposits are disabled, blocking clean pre-positioning/rebalance.
- risks: deposit-disabled sell venue, low depth beyond 2,500 USDT, Gate operational constraints.
- confidence: high for current operational rejection.
- verdict: `KILL` for current route; revisit only if Gate deposits reopen and depth/persistence still hold.

## Candidate A2-034 - QAIT/USDT MEXC/KuCoin -> Gate

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `QAITUSDT` or KuCoin `QAIT-USDT`, sell Gate `QAIT_USDT`
- quote lane: USDT
- why edge might exist: fresh fee-aware discovery found MEXC/KuCoin below Gate after loading Gate pair fee metadata.
- public data quality: high enough to reject current route. MEXC, KuCoin, and Gate contracts match case-insensitively on BSC/BEP20. Gate deposits are enabled, withdrawals disabled; KuCoin deposits enabled, withdrawals disabled.
- fee assumptions: MEXC taker 5 bps, KuCoin taker 10 bps with fee category `3`, Gate pair fee `0.2` = 20 bps, latency haircut 2 bps.
- estimated net bps: MEXC buy -> Gate sell was positive only in small buckets: about +426.4 bps at 50 USDT, +287.9 bps at 100 USDT, +84.4 bps at 250 USDT, about +0.04 bps at 500 USDT, and negative by 1,000 USDT. KuCoin buy -> Gate sell was negative even at 50 USDT.
- executable notional estimate: none worth prioritizing; practical positive capacity is below 500 USDT.
- frequency/duration evidence or proxy: one live metadata and depth validation after corrected fee-aware scan; no persistence window because the route is already effectively zero by 500 USDT.
- implementation effort: no route-specific execution work warranted.
- inventory/funding requirements: would require QAIT inventory on Gate; not worth solving due tiny depth.
- risks: low capacity, Gate withdrawal disabled, KuCoin withdrawal disabled, fee category risk.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-035 - BTR/USDT MEXC -> Bitget

- approach type: capped event-window / cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `BTRUSDT`, sell Bitget `BTRUSDT`
- quote lane: USDT
- why edge might exist: fresh fee-aware discovery found MEXC below Bitget; live depth and a 30-sample window confirmed positive net through 5,000 USDT.
- public data quality: high enough to reject. MEXC identifies full name `Bitlayer` and ERC20 contract `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`; Bitget public coin metadata reports ERC20 contract `0x6c76de483f1752ac8473e2b4983a873991e70da7` and deposits disabled.
- fee assumptions: MEXC taker 5 bps from metadata, Bitget taker 10 bps from metadata, latency haircut 2 bps.
- estimated net bps: 30-sample averages were +448.966 bps at 500 USDT, +440.080 bps at 1,000 USDT, +332.768 bps at 2,500 USDT, and +123.678 bps at 5,000 USDT. The 10,000 USDT bucket was negative, avg -476.173 bps.
- executable notional estimate: none after identity rejection.
- frequency/duration evidence or proxy: 30-sample persistence plus two later 20-sample refreshes. 500-5,000 USDT buckets stayed 100% positive; newest 20-sample refresh had 5,000 USDT 20/20 positive avg +119.803 bps, min +98.886 bps. 10,000 USDT stayed rejected at 0/20 positive, avg -513.260 bps in the newest refresh.
- implementation effort: low if MEXC/Bitget adapters exist; route-specific execution work comes after VANRY/ULTIMA.
- inventory/funding requirements: not worth solving after public contract mismatch; Bitget deposits are also disabled.
- risks: same ticker maps to a different contract across venues; sell venue deposit-disabled status; stale/fake spread despite positive depth.
- confidence: high for current rejection.
- verdict: `KILL`; do not score MEXC `BTR` against Bitget `BTR` unless contract identity is reconciled.

## Candidate A2-036 - PHB/USDT MEXC -> Gate

- approach type: cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `PHBUSDT`, sell Gate `PHB_USDT`
- quote lane: USDT
- why edge might exist: second corrected scan found MEXC below Gate after venue-specific Gate fee modeling.
- public data quality: high enough to reject. MEXC identifies `Phoenix Global`; Gate identifies `Phoenix`; contracts match case-insensitively on BSC. Gate pair is tradable, but Gate currency metadata reports deposits disabled.
- fee assumptions: MEXC taker 5 bps from metadata, Gate pair fee `0.2` = 20 bps, latency haircut 2 bps.
- estimated net bps: positive through 1,000 USDT in live depth: about +1,076.9 bps at 50 USDT, +728.9 bps at 500 USDT, and +438.7 bps at 1,000 USDT. The 2,500 USDT bucket was negative.
- executable notional estimate: none under current operational constraints because Gate deposits are disabled.
- frequency/duration evidence or proxy: one live metadata and depth validation after corrected fee-aware scan; no persistence window because deposit-disabled status kills the current route.
- implementation effort: no route-specific execution work warranted while Gate deposits are disabled.
- inventory/funding requirements: would require PHB inventory already on Gate; public metadata says deposits are disabled, blocking clean pre-positioning/rebalance.
- risks: deposit-disabled sell venue, low depth beyond 1,000 USDT, Gate operational constraints.
- confidence: high for current operational rejection.
- verdict: `KILL` for current route; revisit only if Gate deposits reopen and depth/persistence still hold.

## Candidate A2-037 - VANRY/USDC MEXC -> Binance

- approach type: same-quote cross-exchange spot altcoin arbitrage
- route/assets/exchanges: buy MEXC `VANRYUSDC`, sell Binance `VANRYUSDC`
- quote lane: USDC
- why edge might exist: the VANRY venue fragmentation also exists in the USDC lane, with MEXC below Binance.
- public data quality: medium-high for market data, medium for operational path. MEXC and Binance spot symbols are trading; MEXC exposes the same VANRY contract used in the USDT route. Binance network/deposit status still needs account-level or official wallet verification.
- fee assumptions: conservative MEXC taker 5 bps, Binance taker 10 bps, latency haircut 2 bps. MEXC symbol metadata returned taker commission `0`, but discovery currently treats zero fees as missing, so the candidate is scored conservatively until fee parsing is fixed.
- estimated net bps: 20-sample averages were +878.561 bps at 1,000 USDC, +787.567 bps at 2,500 USDC, and +498.774 bps at 5,000 USDC. The 10,000 USDC bucket was negative, avg -506.189 bps.
- executable notional estimate: initial watch cap 2,500 USDC. Do not promote 5,000 USDC: it failed tail confirmation again.
- frequency/duration evidence or proxy: 20 samples from 2026-05-29 05:03:03 to 05:04:53 CST, another 20-sample refresh from 05:11:58 to 05:14:34 CST, a 30-sample targeted confirmation from 05:17:36 to 05:20:05 CST, and two later 20-sample refreshes. The latest refresh had 2,500 USDC 20/20 positive avg +702.884 bps and 5,000 USDC 20/20 positive avg +448.729 bps, but prior windows had negative 5,000 USDC tails.
- implementation effort: low if MEXC/Binance adapters support USDC quote lane; must keep USDC lane separate from USDT.
- inventory/funding requirements: USDC on MEXC and VANRY inventory already on Binance.
- risks: quote-lane inventory split, Binance global account/region availability, Binance network/deposit support not verified, MEXC withdrawal status not publicly verified, repeated negative-tail behavior at 5,000 USDC.
- confidence: high that the 1,000-2,500 USDC public-book spread existed; medium-low operational confidence until inventory and network paths are verified.
- verdict: `MEASURE` as a separate USDC-lane route capped at 2,500 USDC.

## Candidate A2-038 - AI/USDT Cross-Venue Routes

- approach type: cross-exchange spot altcoin arbitrage identity gate
- route/assets/exchanges: Gate/Binance `AI` versus MEXC/KuCoin/OKX `AI`
- quote lane: USDT
- why edge might exist: fresh corrected scan repeatedly ranked large `AI/USDT` spreads.
- public data quality: high enough to reject before depth. Gate and Binance identify `AI` as Sleepless AI. MEXC and KuCoin identify `AI` as Gensyn with matching ERC20 contract `0x4d7078ddd6ccfed2f85db5b7d3ff16828d378d48` case-insensitively. OKX public instrument metadata lacks contract, but prior and current context place it on the Gensyn side.
- fee assumptions: not relevant after identity rejection.
- estimated net bps: invalid. Apparent spreads are cross-asset comparisons, not arbitrage.
- executable notional estimate: none.
- frequency/duration evidence or proxy: official/public metadata identity check after fresh scan.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: not relevant after rejection.
- risks: same ticker maps to different assets; scanner must use identity mapping before route scoring.
- confidence: high for rejection of Sleepless/Gensyn crossing routes.
- verdict: `KILL`.

## Candidate A2-039 - ESPORTS/USDT KuCoin -> Bitget

- approach type: cross-exchange spot altcoin arbitrage rejected by transfer gate
- route/assets/exchanges: buy KuCoin `ESPORTS-USDT`, sell Bitget `ESPORTSUSDT`
- quote lane: USDT
- why edge might exist: lower-priority corrected scan leftover showed KuCoin materially below Bitget.
- public data quality: high enough to reject operationally. KuCoin full name is `Yooldo Games`; KuCoin and Bitget both expose BEP20 contract `0xf39e4b21c84e737df08e2c3b32541d856f508e48`. Identity is clean, but both venues report deposits disabled.
- fee assumptions: KuCoin 10 bps using fee category `3` risk assumption, Bitget taker 10 bps from public symbol metadata, latency haircut 2 bps.
- estimated net bps: KuCoin buy -> Bitget sell was strongly positive through 5,000 USDT: about +2,563.8 bps at 50 USDT, +2,191.3 bps at 500 USDT, +1,633.3 bps at 1,000 USDT, +964.6 bps at 2,500 USDT, and +344.7 bps at 5,000 USDT. The 10,000 USDT bucket was negative. Bitget buy -> KuCoin sell was negative at every tested bucket.
- executable notional estimate: none for repeatable arbitrage while deposits are disabled on both venues.
- frequency/duration evidence or proxy: one live metadata/depth validation after corrected scan; no persistence window because the transfer gate already kills the route.
- implementation effort: no route-specific execution work warranted.
- inventory/funding requirements: would require USDT on KuCoin and ESPORTS inventory already on Bitget. Since Bitget deposits are disabled, KuCoin purchases cannot replenish Bitget sell inventory through a venue deposit lane.
- risks: deposit-disabled destination, possible delisting/offline risk despite current symbol status, inventory trapped on the wrong venue, depth cliff at 10,000 USDT.
- confidence: high for current rejection as a repeatable route.
- verdict: `KILL`; treat only as a possible manual liquidation anomaly for pre-existing Bitget inventory, not an Agent 2 route.

## Candidate A2-040 - SWEAT/USDT MEXC/Bitget -> Gate

- approach type: cross-exchange spot altcoin arbitrage rejected by transfer gate
- route/assets/exchanges: buy MEXC `SWEATUSDT` or Bitget `SWEATUSDT`, sell Gate `SWEAT_USDT`
- quote lane: USDT
- why edge might exist: lower-priority leftover scan showed SWEAT materially cheaper on MEXC/Bitget than Gate.
- public data quality: high enough to reject operationally. MEXC and Gate both identify `Sweat Economy` with ERC20 contract `0xB4b9DC1C77bdbb135eA907fd5a08094d98883A35`; Bitget exposes NEAR contract `token.sweat`.
- fee assumptions: MEXC taker 5 bps, Bitget taker 10 bps, Gate pair fee `0.2` = 20 bps, latency haircut 2 bps.
- estimated net bps: top-of-book net was about +434.6 bps for MEXC -> Gate and +430.7 bps for Bitget -> Gate before depth validation.
- executable notional estimate: none while Gate deposits are disabled.
- frequency/duration evidence or proxy: one public top-of-book and metadata validation after lower-priority leftover scan; no persistence because transfer gate already rejects it.
- implementation effort: no route-specific work warranted.
- inventory/funding requirements: would require SWEAT inventory already on Gate; public metadata says Gate deposits are disabled.
- risks: deposit-disabled Gate sell venue, NEAR/ETH chain split, inventory trapped on wrong venue.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-041 - SPARKLET/USDT MEXC -> Gate

- approach type: micro cross-exchange spot altcoin arbitrage rejected by practical economics
- route/assets/exchanges: buy MEXC `SPARKLETUSDT`, sell Gate `SPARKLET_USDT`
- quote lane: USDT
- why edge might exist: lower-priority leftover scan showed MEXC below Gate.
- public data quality: high. MEXC identifies `Upland` with ERC20 contract `0x0bc37BEA9068a86C221B8bd71eA6228260DAD5A2`; Gate exposes the same contract case-insensitively, deposits and withdrawals enabled.
- fee assumptions: MEXC taker 5 bps, Gate pair fee `0.2` = 20 bps, latency haircut 2 bps.
- estimated net bps: 20-sample persistence averaged +73.683 bps at 250 USDT and +38.332 bps at 500 USDT. The 1,000 USDT bucket averaged -5.949 bps.
- executable notional estimate: none worth prioritizing. The route is technically positive only at micro size, and the 500 USDT edge is too small before withdrawal/rebalance/inventory overhead.
- frequency/duration evidence or proxy: 20 samples from 2026-05-29 05:27:39 to 05:28:59 CST; 250 and 500 USDT were 20/20 positive, 1,000 USDT was 0/20 positive.
- implementation effort: no execution work warranted.
- inventory/funding requirements: would require USDT on MEXC and SPARKLET inventory on Gate; repeated use needs a rebalance path whose cost likely dominates the small edge.
- risks: low notional ceiling, Gate 20 bps taker fee, withdrawal/rebalance cost, rapid depth cliff.
- confidence: high that the micro spread existed; high that rejection as an execution candidate is correct.
- verdict: `KILL`.

## Candidate A2-042 - SNEK/USDT KuCoin/MEXC -> Bitget/Gate

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth and transfer economics
- route/assets/exchanges: best observed route was buy KuCoin `SNEK-USDT`, sell Bitget `SNEKUSDT`
- quote lane: USDT
- why edge might exist: lower-priority leftover scan showed KuCoin/MEXC below Bitget/Gate.
- public data quality: medium-high. KuCoin, MEXC, Gate, and Bitget identity/chain metadata aligns sufficiently for SNEK/Cardano testing; deposits are enabled on the relevant public endpoints.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, Bitget taker 10 bps, Gate pair fee 20 bps, latency haircut 2 bps.
- estimated net bps: best route KuCoin -> Bitget measured +80.387 bps at 50 USDT, +72.161 bps at 100 USDT, +21.982 bps at 250 USDT, and -25.252 bps at 500 USDT.
- executable notional estimate: none. KuCoin withdrawal fee is `2,000` SNEK, which already exceeds the tiny 250 USDT edge.
- frequency/duration evidence or proxy: one live metadata and depth validation after lower-priority leftover scan; no persistence because 500 USDT is already negative.
- implementation effort: no execution work warranted.
- inventory/funding requirements: would require SNEK inventory on Bitget or Gate; repeated strategy is uneconomic at observed depth.
- risks: shallow depth, transfer fees, Cardano-chain settlement/rebalance latency.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-043 - COQ/USDT KuCoin -> MEXC/Gate

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `COQ-USDT`, sell MEXC `COQUSDT` or Gate `COQ_USDT`
- quote lane: USDT
- why edge might exist: lower-priority leftover scan showed KuCoin below MEXC/Gate top-of-book.
- public data quality: high for identity. KuCoin, MEXC, and Gate align on AVAX C-Chain contract `0x420FcA0121DC28039145009570975747295f2329`.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, Gate pair fee 20 bps, latency haircut 2 bps.
- estimated net bps: KuCoin -> MEXC was negative at every tested bucket, including about -122.153 bps at 50 USDT and -152.209 bps at 100 USDT. KuCoin -> Gate was also negative at every tested bucket.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata and depth validation after lower-priority leftover scan.
- implementation effort: no execution work warranted.
- inventory/funding requirements: not relevant after negative depth.
- risks: stale/top-of-book false positive.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-044 - VOOI/USDT MEXC/KuCoin/Gate -> Bybit

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth and unverified sell-venue transfer status
- route/assets/exchanges: buy MEXC `VOOIUSDT`, KuCoin `VOOI-USDT`, or Gate `VOOI_USDT`; sell Bybit `VOOIUSDT`
- quote lane: USDT
- why edge might exist: lower-priority leftover scan showed Bybit bid above MEXC/KuCoin/Gate asks.
- public data quality: medium. MEXC, KuCoin, Gate, and Bitget expose matching ERC20 contract `0xb31561f0e2aac72406103b1926356d756f07a481` where metadata is public. Bybit asset/network endpoint is key-gated, and Bybit was the apparent sell venue.
- fee assumptions: MEXC taker 5 bps, KuCoin/Bybit taker 10 bps, Gate pair fee 20 bps, latency haircut 2 bps.
- estimated net bps: best route MEXC -> Bybit measured +75.311 bps at 50 USDT and +30.578 bps at 100 USDT, but -41.734 bps at 250 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata and depth validation after lower-priority leftover scan.
- implementation effort: no execution work warranted.
- inventory/funding requirements: would require VOOI inventory on Bybit; Bybit network/deposit status was not publicly verified.
- risks: tiny depth, unverified Bybit transfer lane, inventory overhead.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-045 - RAVE/USDT Bitget -> Gate/KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by transfer gate
- route/assets/exchanges: buy Bitget `RAVEUSDT`, sell Gate `RAVE_USDT` or KuCoin `RAVE-USDT`
- quote lane: USDT
- why edge might exist: new corrected discovery pass ranked RAVE as the largest top-of-book spread.
- public data quality: high enough to reject operationally. Bitget, Gate, and KuCoin align on ERC20 contract `0x17205fab260a7a6383a81452ce6315a39370db97`.
- fee assumptions: Bitget taker 10 bps, Gate pair fee 20 bps, KuCoin taker 10 bps, latency haircut 2 bps.
- estimated net bps: top-of-book net was about +2,962.6 bps for Bitget -> Gate and +1,477.2 bps for Bitget -> KuCoin before depth validation.
- executable notional estimate: none while sell venue deposits are disabled.
- frequency/duration evidence or proxy: one public metadata validation after corrected discovery; no depth persistence because transfer gate rejects it.
- implementation effort: no work warranted.
- inventory/funding requirements: would require RAVE inventory already on Gate/KuCoin; deposits are disabled.
- risks: deposit-disabled sell venue, inventory-only anomaly.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-046 - UPC/USDT MEXC -> Bitget

- approach type: cross-exchange spot altcoin arbitrage rejected by transfer gate
- route/assets/exchanges: buy MEXC `UPCUSDT`, sell Bitget `UPCUSDT`
- quote lane: USDT
- why edge might exist: corrected discovery found MEXC below Bitget.
- public data quality: high enough to reject operationally. MEXC and Bitget match on ERC20 contract `0x487d62468282bd04ddf976631c23128a425555ee`, but Bitget deposits are disabled.
- fee assumptions: MEXC taker 5 bps, Bitget taker 10 bps, latency haircut 2 bps.
- estimated net bps: top-of-book net was about +2,767.9 bps before depth validation.
- executable notional estimate: none while Bitget deposits are disabled.
- frequency/duration evidence or proxy: one public metadata validation after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: would require UPC inventory already on Bitget.
- risks: deposit-disabled sell venue.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-047 - RWA/USDT Gate/MEXC -> KuCoin

- approach type: identity-gate rejection
- route/assets/exchanges: Gate `RWA_USDT` or MEXC `RWAUSDT` versus KuCoin `RWA-USDT`
- quote lane: USDT
- why edge might exist: corrected discovery found Gate/MEXC below KuCoin.
- public data quality: high enough to reject before depth. MEXC and Gate list `Allo` on BSC contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`; KuCoin lists `RWA Inc` on Base contract `0xe2b1dc2d4a3b4e59fdf0c47b71a7a86391a8b35a`.
- fee assumptions: not relevant after identity rejection.
- estimated net bps: invalid because the compared assets are different.
- executable notional estimate: none.
- frequency/duration evidence or proxy: public metadata identity check after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not relevant after identity rejection.
- risks: same ticker collision.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-048 - TOWER/USDT MEXC -> KuCoin

- approach type: identity-gate rejection
- route/assets/exchanges: buy MEXC `TOWERUSDT`, sell KuCoin `TOWER-USDT`
- quote lane: USDT
- why edge might exist: corrected discovery found MEXC below KuCoin.
- public data quality: high enough to reject before depth. MEXC exposes contract `0xf7C1CEfCf7E1dd8161e00099facD3E1Db9e528ee`; KuCoin exposes ERC20 contract `0x1c9922314ed1415c95b9fd453c3818fd41867d0b`.
- fee assumptions: not relevant after identity rejection.
- estimated net bps: invalid after contract mismatch.
- executable notional estimate: none.
- frequency/duration evidence or proxy: public metadata identity check after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not relevant after identity rejection.
- risks: same ticker maps to different contracts.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-049 - ARRR/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `ARRR_USDT`, sell MEXC `ARRRUSDT`
- quote lane: USDT
- why edge might exist: corrected discovery found Gate below MEXC.
- public data quality: medium-high. Gate and MEXC both identify `ARRR` as Pirate Chain; Gate deposits and withdrawals are enabled. MEXC deposit status remains key-gated.
- fee assumptions: Gate pair fee 20 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: +42.654 bps at 50 USDT, but -1.100 bps at 100 USDT and negative at all larger tested buckets.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata and depth validation after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not relevant after negative depth.
- risks: tiny top-of-book pocket, MEXC transfer status key-gated.
- confidence: high for current rejection.
- verdict: `KILL`.

## Candidate A2-050 - XMN/USDT MEXC -> KuCoin

- approach type: low-priority micro cross-exchange spot altcoin arbitrage measurement
- route/assets/exchanges: buy MEXC `XMNUSDT`, sell KuCoin `XMN-USDT`
- quote lane: USDT
- why edge might exist: corrected discovery found MEXC below KuCoin, and depth persistence confirmed a 500 USDT pocket.
- public data quality: medium. MEXC and KuCoin both identify `xMoney` on SUI contract `0x97c7571f4406cdd7a95f3027075ab80d3e9c937c2a567690d31e14ab1872ccee::xmn::XMN`; KuCoin deposits/withdrawals are enabled. MEXC withdrawal status remains key-gated.
- fee assumptions: MEXC taker 5 bps, KuCoin taker 10 bps, latency haircut 2 bps.
- estimated net bps: 20-sample persistence averaged +103.767 bps at 250 USDT and +67.794 bps at 500 USDT. The 1,000 USDT bucket averaged -144.453 bps.
- executable notional estimate: not execution-ready. Measurement cap 500 USDT, pending MEXC withdrawal status and fee.
- frequency/duration evidence or proxy: 20 samples from 2026-05-29 05:39:53 to 05:41:04 CST; 250 and 500 USDT buckets were 20/20 positive, 1,000 USDT was 0/20 positive.
- implementation effort: low if MEXC/KuCoin adapters exist, but not worth prioritizing before VANRY/ULTIMA.
- inventory/funding requirements: USDT on MEXC and XMN inventory on KuCoin. Repeated strategy needs MEXC SUI-chain withdrawal status/fee verification.
- risks: micro notional cap, MEXC withdrawal status unavailable publicly, SUI-chain settlement/rebalance overhead.
- confidence: high that the 500 USDT public-book pocket existed; medium-low operational confidence.
- verdict: `LATER` / low-priority `MEASURE`, capped at 500 USDT.

## Candidate A2-051 - SWCH/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by tradability gate
- route/assets/exchanges: buy Gate `SWCH_USDT`, sell MEXC `SWCHUSDT`
- quote lane: USDT
- why edge might exist: corrected discovery found Gate below MEXC.
- public data quality: high enough to reject. Gate and MEXC contracts match for SwissCheese on Polygon, but MEXC reports `isSpotTradingAllowed=false`.
- fee assumptions: not relevant after tradability rejection.
- estimated net bps: invalid because MEXC spot trading is not allowed.
- executable notional estimate: none.
- frequency/duration evidence or proxy: public metadata check after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not relevant after tradability rejection.
- risks: public ticker exists despite disabled spot trading flag.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-052 - CWEB/USDT KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth and transfer economics
- route/assets/exchanges: buy KuCoin `CWEB-USDT`, sell MEXC `CWEBUSDT`
- quote lane: USDT
- why edge might exist: corrected discovery found KuCoin below MEXC.
- public data quality: medium-high. KuCoin and MEXC match on ERC20 `0x505b5eda5e25a67e1c24a2bf1a527ed9eb88bf04`; KuCoin deposits/withdrawals are enabled. MEXC deposit status remains key-gated.
- fee assumptions: KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: +99.862 bps at 50 USDT, +81.814 bps at 100 USDT, +32.442 bps at 250 USDT, and -32.541 bps at 500 USDT.
- executable notional estimate: none. KuCoin withdrawal fee `1,200` CWEB is larger than the 250 USDT edge.
- frequency/duration evidence or proxy: one live metadata/depth validation after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not worth solving after depth/fee rejection.
- risks: shallow depth, withdrawal fee, MEXC transfer status key-gated.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-053 - GHX/USDT Gate/KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `GHX_USDT` or KuCoin `GHX-USDT`, sell MEXC `GHXUSDT`
- quote lane: USDT
- why edge might exist: corrected discovery found Gate/KuCoin below MEXC.
- public data quality: medium-high. Gate, KuCoin, and MEXC match on ERC20 `0x728f30fa2f100742c7949d1961804fa8e0b1387d`; MEXC deposit status remains key-gated.
- fee assumptions: Gate pair fee 20 bps, KuCoin taker 10 bps, MEXC taker 5 bps, latency haircut 2 bps.
- estimated net bps: Gate -> MEXC was positive at 50-100 USDT but negative by 250 USDT. KuCoin -> MEXC was +204.424 bps at 50 USDT, +131.280 bps at 100 USDT, about +0.915 bps at 250 USDT, and negative by 500 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one live metadata/depth validation after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not worth solving after depth rejection.
- risks: shallow MEXC bid depth, transfer overhead.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-054 - BBT/USDT MEXC -> Gate

- approach type: cross-exchange spot altcoin arbitrage rejected by tradability gate
- route/assets/exchanges: buy MEXC `BBTUSDT`, sell Gate `BBT_USDT`
- quote lane: USDT
- why edge might exist: corrected discovery found MEXC below Gate.
- public data quality: high enough to reject. Gate lists BabyBoomToken with matching BSC contract, but MEXC reports `isSpotTradingAllowed=false`.
- fee assumptions: not relevant after tradability rejection.
- estimated net bps: invalid because MEXC spot trading is not allowed.
- executable notional estimate: none.
- frequency/duration evidence or proxy: public metadata check after corrected discovery.
- implementation effort: no work warranted.
- inventory/funding requirements: not relevant after tradability rejection.
- risks: public ticker exists despite disabled spot trading flag.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-055 - IMT/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `IMT_USDT`, sell MEXC `IMTUSDT`
- quote lane: USDT
- public data quality: high enough to test. Gate and MEXC identity matches for Immortal Rising 2 on ERC20.
- estimated net bps: live depth was negative even at 50 USDT, about -119.271 bps.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-056 - SIX/USDT MEXC -> Gate

- approach type: identity-gate rejection
- route/assets/exchanges: buy MEXC `SIXUSDT`, sell Gate `SIX_USDT`
- quote lane: USDT
- public data quality: high enough to reject. MEXC contract `0x070a9867Ea49CE7AFc4505817204860e823489fE` does not match Gate contract `0x61c6ebf443ad613c9648762585b3cfd3ba1f3fa8`.
- estimated net bps: invalid after contract mismatch.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-057 - REACT/USDT KuCoin -> Gate

- approach type: transfer-gate rejection
- route/assets/exchanges: buy KuCoin `REACT-USDT`, sell Gate `REACT_USDT`
- quote lane: USDT
- public data quality: high enough to reject operationally. KuCoin and Gate match on ETH contract, but KuCoin ERC20 withdrawals are disabled; only native `react` withdrawals are enabled while Gate supports ETH.
- estimated net bps: not depth-tested after transfer gate rejection.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-058 - PYBOBO/USDT MEXC -> Bybit

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `PYBOBOUSDT`, sell Bybit `PYBOBOUSDT`
- quote lane: USDT
- public data quality: medium. Bybit network status was not publicly verified.
- estimated net bps: +46.954 bps at 50 USDT and +35.622 bps at 100 USDT, but -5.160 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-059 - WBAI/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `WBAI-USDT`, sell MEXC `WBAIUSDT`
- quote lane: USDT
- public data quality: high enough to test. KuCoin and MEXC identity matches on BSC contract `0x635d44f246156ed1080cb470877256c847673f19`.
- estimated net bps: negative even at 50 USDT, about -397.012 bps.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-060 - MAPO/USDT MEXC/KuCoin -> Bitget

- approach type: transfer-gate rejection
- route/assets/exchanges: buy MEXC `MAPOUSDT` or KuCoin `MAPO-USDT`, sell Bitget `MAPOUSDT`
- quote lane: USDT
- public data quality: high enough to reject operationally. Bitget reports MAPO deposits and withdrawals disabled; KuCoin deposits are also disabled.
- estimated net bps: not depth-tested after transfer gate rejection.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-061 - CTA/USDT Bybit -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bybit `CTAUSDT`, sell KuCoin `CTA-USDT`
- quote lane: USDT
- public data quality: medium. KuCoin identity is available; Bybit network status is key-gated.
- estimated net bps: negative even at 50 USDT, about -55.773 bps.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-062 - ALEX/USDT KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `ALEX-USDT`, sell MEXC `ALEXUSDT`
- quote lane: USDT
- public data quality: medium-high. KuCoin and MEXC identity matches on STX token metadata.
- estimated net bps: +70.420 bps at 50 USDT and +9.502 bps at 100 USDT, but -149.428 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-063 - DEVVE/USDT Gate -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `DEVVE_USDT`, sell MEXC `DEVVEUSDT`
- quote lane: USDT
- public data quality: high enough to test. Gate and MEXC identity matches on ERC20 `0x8248270620aa532e4d64316017be5e873e37cc09`.
- estimated net bps: +25.116 bps at 50 USDT, but -2.606 bps at 100 USDT and worse beyond.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-064 - TYCOON/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by tradability gate
- route/assets/exchanges: buy Gate `TYCOON_USDT`, sell MEXC `TYCOONUSDT`
- quote lane: USDT
- public data quality: high enough to reject. Gate and MEXC contracts match for Dino Tycoon on BSC, but MEXC reports `isSpotTradingAllowed=false`.
- estimated net bps: invalid because MEXC spot trading is not allowed.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-065 - EPIC/USDT Gate -> MEXC/Binance

- approach type: cross-exchange spot altcoin arbitrage rejected by executable depth
- route/assets/exchanges: buy Gate `EPIC_USDT`, sell MEXC `EPICUSDT` or Binance `EPICUSDT`
- quote lane: USDT
- why edge might exist: corrected discovery found Gate below MEXC/Binance on headline prices.
- public data quality: high enough to test. Gate, MEXC, and Binance metadata point to the same EPIC ERC20 contract; Gate and Binance public transfer lanes were enabled.
- fee assumptions: Gate taker 20 bps, MEXC taker 5 bps, Binance taker 10 bps, latency haircut 2 bps.
- estimated net bps:
  - Gate -> MEXC: -84.759 bps at 50 USDT, -95.402 bps at 100 USDT, -128.681 bps at 250 USDT, -168.242 bps at 500 USDT.
  - Gate -> Binance: -90.461 bps at 50 USDT, -100.728 bps at 100 USDT, -131.868 bps at 250 USDT, -169.987 bps at 500 USDT.
- executable notional estimate: none.
- risks: top-of-book discovery signal was not executable after fee/depth math.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-066 - SXT/USDT Bybit -> MEXC/Binance/KuCoin/Bitget/Gate

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bybit `SXTUSDT`, sell MEXC `SXTUSDT`, Binance `SXTUSDT`, KuCoin `SXT-USDT`, Bitget `SXTUSDT`, or Gate `SXT_USDT`
- quote lane: USDT
- why edge might exist: corrected discovery found Bybit below multiple SXT venues.
- public data quality: medium-high. Public metadata aligns SXT on ERC20 across MEXC, Binance, KuCoin, and Bitget; KuCoin and Bitget ERC20 deposits/withdrawals were enabled. Bybit transfer status was not publicly verified.
- fee assumptions: Bybit taker 10 bps; sell taker MEXC 5 bps, Binance/KuCoin/Bitget 10 bps, Gate 20 bps; latency haircut 2 bps.
- estimated net bps:
  - Bybit -> MEXC: +42.895 bps at 50 USDT and +42.793 bps at 100 USDT, but -53.151 bps at 250 USDT and -94.948 bps at 500 USDT.
  - Bybit -> Binance: -21.980 bps at 50-500 USDT, then worse.
  - Bybit -> KuCoin: -89.424 bps at 50 USDT and worse; sell depth exhausted by 5,000 USDT.
  - Bybit -> Bitget: -14.499 bps at 50 USDT and worse.
  - Bybit -> Gate: -48.282 bps at 50 USDT and worse.
- executable notional estimate: none; the only positive route dies before 250 USDT.
- risks: Bybit transfer status remains unverified, but depth rejection is already decisive.
- confidence: high for rejection.
- verdict: `KILL`.

## Candidate A2-067 - CHIRP/USDT MEXC -> KuCoin

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `CHIRPUSDT`, sell KuCoin `CHIRP-USDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify Chirp on SUI contract `0x1ef4c0b20340b8c6a59438204467ca71e1e7cbe918526f9c2c6c5444517cd5ca::chirp::CHIRP`; KuCoin deposits/withdrawals enabled with 60 CHIRP fee and 120 CHIRP minimum.
- estimated net bps: +46.613 bps at 50 USDT, -11.259 bps at 100 USDT, -103.365 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-068 - GAMEVIRTUAL/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `GAMEVIRTUAL_USDT`, sell MEXC `GAMEVIRTUALUSDT`
- quote lane: USDT
- public data quality: high enough to test. Gate and MEXC identify GAME by Virtuals on Base contract `0x1c4cca7c5db003824208adda61bd749e55f463a3`; Gate deposits/withdrawals enabled.
- estimated net bps: -25.473 bps at 50 USDT, -32.551 bps at 100 USDT, -45.805 bps at 250 USDT, -63.087 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-069 - AFC/USDT MEXC -> Bybit

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `AFCUSDT`, sell Bybit `AFCUSDT`
- quote lane: USDT
- public data quality: medium. MEXC identifies Arsenal Fan Token with contract `0x76088F3eD5dC655De9295D93868ec1EeC654A615`; Bybit spot trading is enabled but public transfer metadata was not verified.
- estimated net bps: -38.595 bps at 50 USDT, -53.771 bps at 100 USDT, -76.666 bps at 250 USDT, -110.978 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-070 - LKI/USDT MEXC -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `LKIUSDT`, sell KuCoin `LKI-USDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify Laika AI on BEP20 contract `0x1865dc79a9e4b5751531099057d7ee801033d268`; KuCoin deposits/withdrawals enabled with 1,700 LKI fee and 3,400 LKI minimum.
- estimated net bps: -367.978 bps at 50 USDT, -440.512 bps at 100 USDT, -1101.485 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-071 - LYX/USDT Gate -> KuCoin

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy Gate `LYX_USDT`, sell KuCoin `LYX-USDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify LUKSO on native LYX/LUKSO chain; deposits/withdrawals are enabled on both public endpoints.
- estimated net bps: +85.079 bps at 50 USDT, +74.534 bps at 100 USDT, -47.256 bps at 250 USDT, -151.602 bps at 500 USDT.
- executable notional estimate: none; positive pocket dies before 250 USDT.
- verdict: `KILL`.

## Candidate A2-072 - NOS/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `NOS_USDT`, sell MEXC `NOSUSDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify Nosana on Solana address `nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7`; Gate deposits/withdrawals enabled.
- estimated net bps: -26.207 bps at 50 USDT, -28.670 bps at 100 USDT, -31.441 bps at 250 USDT, -55.598 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-073 - ID/USDT MEXC -> Bybit

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `IDUSDT`, sell Bybit `IDUSDT`
- quote lane: USDT
- public data quality: medium. MEXC identifies SPACE ID with contract `0x2dfF88A56767223A5529eA5960Da7A3F5f766406`; Bybit spot trading is enabled but public transfer metadata was not verified.
- estimated net bps: -41.238 bps at 50 USDT, -50.749 bps at 100 USDT, -70.661 bps at 250 USDT, -89.955 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-074 - SOUL/USDT Gate -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth and chain ambiguity
- route/assets/exchanges: buy Gate `SOUL_USDT`, sell KuCoin `SOUL-USDT`
- quote lane: USDT
- public data quality: medium. Both venues name Phantasma/SOUL, but Gate reports chain `KCALP` while KuCoin reports `PHANTASMA`; deposits/withdrawals are enabled on both public endpoints.
- estimated net bps: -14.308 bps at 50 USDT, -76.727 bps at 100 USDT, -145.485 bps at 250 USDT, -354.098 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-075 - RIO/USDT KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity and identity ambiguity
- route/assets/exchanges: buy KuCoin `RIO-USDT`, sell MEXC `RIOUSDT`
- quote lane: USDT
- public data quality: medium-low. KuCoin reports Realio Network on BEP20 contract `0x94a8b4ee5cd64c79d0ee816f467ea73009f51aa0`; MEXC reports `Realio` with contract/address field `2751733`.
- estimated net bps: +41.221 bps at 50 USDT, +30.083 bps at 100 USDT, -5.050 bps at 250 USDT, -58.774 bps at 500 USDT.
- executable notional estimate: none; positive pocket dies before 250 USDT and transfer identity is not clean.
- verdict: `KILL`.

## Live Refresh Update - 2026-05-29 06:09 CST

Top promoted/measured routes were refreshed over 20 samples from 06:06:31 to 06:09:33 CST with zero endpoint errors.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive, avg +307.750 bps, median +297.130 bps, min +164.289 bps.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 10,000 USDT remains 20/20 positive, avg +237.999 bps, median +236.777 bps, min +174.346 bps. Operational blocker unchanged: SMART/BEP20 or inventory/rebalance proof.
- `A2-031` VANRY MEXC -> KuCoin USDT: 5,000 USDT improved to 20/20 positive, avg +325.173 bps, median +318.016 bps, min +205.403 bps. Keep 2,500 USDT as firm cap until a second robust window confirms this is not a temporary depth refill.
- `A2-037` VANRY MEXC -> Binance USDC: MEXC taker fee is now treated as a real 0 bps value. 5,000 USDC measured 20/20 positive, avg +620.881 bps, median +662.076 bps, min +193.250 bps. Keep 2,500 USDC as formal cap until another robust window clears the prior negative-tail history.

## Candidate A2-076 - DMTR/USDT MEXC -> KuCoin

- approach type: micro cross-exchange spot altcoin arbitrage rejected by transfer fee and capacity
- route/assets/exchanges: buy MEXC `DMTRUSDT`, sell KuCoin `DMTR-USDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify Dimitra on ERC20 contract `0x51cb253744189f11241becb29bedd3f1b5384fdb`; KuCoin deposits/withdrawals enabled with 170 DMTR fee and 340 DMTR minimum.
- estimated net bps: +85.181 bps at 50 USDT, +66.286 bps at 100 USDT, +35.714 bps at 250 USDT, +13.262 bps at 500 USDT, -14.643 bps at 1,000 USDT.
- executable notional estimate: none; transfer fee wipes the only positive pocket.
- verdict: `KILL`.

## Candidate A2-077 - WARD/USDT Bitget/MEXC/KuCoin -> Gate

- approach type: transfer-identity rejection
- route/assets/exchanges: buy Bitget `WARDUSDT`, MEXC `WARDUSDT`, or KuCoin `WARD-USDT`; sell Gate `WARD_USDT`
- quote lane: USDT
- public data quality: high enough to reject. Gate exposes WARD on BSC contract `0x6dc200b21894af4660b549b678ea8df22bf7cfac`; KuCoin and Bitget expose native Warden; MEXC reports no contract field.
- estimated net bps: invalid until chain/bridge compatibility is proven.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-078 - INSP/USDT MEXC -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `INSPUSDT`, sell KuCoin `INSP-USDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify Inspect on ERC20 contract `0x186ef81fd8e77eec8bffc3039e7ec41d5fc0b457`; KuCoin deposits/withdrawals enabled.
- estimated net bps: -93.174 bps at 50 USDT, -120.797 bps at 100 USDT, -176.628 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-079 - TX/USDT Gate -> Bitget

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `TX_USDT`, sell Bitget `TXUSDT`
- quote lane: USDT
- public data quality: medium-high. Both public endpoints show native TX-style metadata and deposits/withdrawals available for the relevant direction.
- estimated net bps: -11.922 bps at 50 USDT, -38.500 bps at 100 USDT, -71.398 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-080 - SIN/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `SIN-USDT`, sell MEXC `SINUSDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify SinVerse on BEP20 contract `0x6397de0f9aedc0f7a8fa8b438dde883b9c201010`; KuCoin deposits/withdrawals enabled.
- estimated net bps: -58.243 bps at 50 USDT, -1159.213 bps at 100 USDT, -2377.841 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-081 - STAY/USDT MEXC -> KuCoin

- approach type: micro cross-exchange spot altcoin arbitrage rejected by transfer fee and capacity
- route/assets/exchanges: buy MEXC `STAYUSDT`, sell KuCoin `STAY-USDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify STAYNEX on BEP20 contract `0x30c0ef9361645ec56a7e640cd05ce6abdfce8422`; KuCoin deposits/withdrawals enabled with 14,000 STAY fee and 28,000 STAY minimum.
- estimated net bps: +24.016 bps at 50 USDT, -12.943 bps at 100 USDT, -49.267 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-082 - ASSET/USDT KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy KuCoin `ASSET-USDT`, sell MEXC `ASSETUSDT`
- quote lane: USDT
- public data quality: high enough to test. Both venues identify REAL/ASSET on ERC20 contract `0x99e980265bf36516c442be982df1772a6ccb3233`; KuCoin deposits/withdrawals enabled with 8 ASSET fee and 16 ASSET minimum.
- estimated net bps: +125.450 bps at 50 USDT and 100 USDT, +74.015 bps at 250 USDT, -24.887 bps at 500 USDT.
- executable notional estimate: none; positive pocket dies before 500 USDT and fee consumes most edge.
- verdict: `KILL`.

## Candidate A2-083 - PIN/USDT MEXC -> Gate

- approach type: tradability-gate rejection
- route/assets/exchanges: buy MEXC `PINUSDT`, sell Gate `PIN_USDT`
- quote lane: USDT
- public data quality: high enough to reject. MEXC and Gate identity matches on ERC20 contract `0x2e44f3f609ff5aa4819b323fd74690f07c3607c4`, but MEXC reports `isSpotTradingAllowed=false`.
- estimated net bps: invalid because the MEXC buy leg is disabled.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-084 - GAIB/USDT Bybit -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bybit `GAIBUSDT`, sell MEXC `GAIBUSDT`
- quote lane: USDT
- public data quality: medium. Bybit spot trading is enabled and MEXC reports GAIB contract `0xC19D38925F9F645337B1D1f37bAf3C0647A48E50`, but Bybit transfer metadata was not publicly verified.
- estimated net bps: +6.180 bps at 50 USDT, +0.835 bps at 100 USDT, -32.099 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-085 - HEART/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `HEART-USDT`, sell MEXC `HEARTUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -61.743 bps at 50 USDT, -142.304 bps at 100 USDT, -326.484 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-086 - BNKR/USDT KuCoin/Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `BNKR-USDT` or Gate `BNKR_USDT`, sell MEXC `BNKRUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps:
  - KuCoin -> MEXC: -21.546 bps at 50 USDT, -22.020 bps at 100 USDT, -22.305 bps at 250 USDT.
  - Gate -> MEXC: -5.769 bps at 50 USDT, -6.243 bps at 100 USDT, -6.527 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-087 - ESE/USDT MEXC -> Bybit/KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `ESEUSDT`, sell Bybit `ESEUSDT` or KuCoin `ESE-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps:
  - MEXC -> Bybit: -51.950 bps at 50 USDT, -63.773 bps at 100 USDT, -135.020 bps at 250 USDT.
  - MEXC -> KuCoin: -44.139 bps at 50 USDT, -55.127 bps at 100 USDT, -122.638 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-088 - RVV/USDT Bitget -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bitget `RVVUSDT`, sell MEXC `RVVUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -93.739 bps at 50 USDT, -137.182 bps at 100 USDT, -232.521 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-089 - HEI/USDT Binance -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Binance `HEIUSDT`, sell MEXC `HEIUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -58.784 bps at 50 USDT, -61.402 bps at 100 USDT, -62.973 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-090 - ROOBEE/USDT Gate -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `ROOBEE_USDT`, sell KuCoin `ROOBEE-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -12.568 bps at 50 USDT, -53.789 bps at 100 USDT, -84.087 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-091 - LAVA/USDT Bybit -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bybit `LAVAUSDT`, sell MEXC `LAVAUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -16.877 bps at 50 USDT, -16.931 bps at 100 USDT, -31.434 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-092 - RMV/USDT MEXC -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `RMVUSDT`, sell KuCoin `RMV-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -60.613 bps at 50 USDT, -117.706 bps at 100 USDT, -224.034 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-093 - XELS/USDT Gate -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy Gate `XELS_USDT`, sell MEXC `XELSUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps: +41.341 bps at 50 USDT, +22.754 bps at 100 USDT, -17.004 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-094 - IOTX/USDT MEXC/Binance -> Gate

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy MEXC `IOTXUSDT` or Binance `IOTXUSDT`, sell Gate `IOTX_USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps:
  - MEXC -> Gate: +53.357 bps at 50 USDT, +51.726 bps at 100 USDT, -21.289 bps at 250 USDT.
  - Binance -> Gate: +50.761 bps at 50 USDT, +49.131 bps at 100 USDT, -15.490 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-095 - HAI/USDT KuCoin -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy KuCoin `HAI-USDT`, sell MEXC `HAIUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -13.334 bps at 50 USDT, -76.247 bps at 100 USDT, -153.900 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-096 - LL/USDT MEXC -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `LLUSDT`, sell KuCoin `LL-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -70.149 bps at 50 USDT, -88.613 bps at 100 USDT, -154.945 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-097 - MCRT/USDT Bybit -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bybit `MCRTUSDT`, sell MEXC `MCRTUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -77.408 bps at 50 USDT, -128.837 bps at 100 USDT, -348.693 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-098 - MSFTON/USDT MEXC -> Bitget

- approach type: tokenized-stock spot arbitrage rejected by transfer/rebalance economics
- route/assets/exchanges: buy MEXC `MSFTONUSDT`, sell Bitget `MSFTONUSDT`
- quote lane: USDT
- public data quality: medium-high. MEXC and Bitget both identify Microsoft/MSFTON on ERC20 contract `0xb812837b81a3a6b81d7cd74cfb19a7f2784555e5`; Bitget ERC20 deposits/withdrawals enabled. MEXC withdrawal status/fee remains unverified publicly.
- estimated net bps: +21.032 bps at 50 USDT, +20.877 bps at 250 USDT, +14.885 bps at 1,000 USDT, +0.290 bps at 2,500 USDT, -55.853 bps at 5,000 USDT.
- executable notional estimate: none; edge is too small for ERC20 withdrawal/rebalance costs and disappears by 5,000 USDT.
- verdict: `KILL`.

## Candidate A2-099 - GXE/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `GXE_USDT`, sell MEXC `GXEUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -695.109 bps at 50 USDT, -1302.759 bps at 100 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-100 - IAUON/USDT MEXC -> Gate

- approach type: tokenized-asset spot arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `IAUONUSDT`, sell Gate `IAUON_USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -14.321 bps at 50 USDT, -14.780 bps at 100 USDT, -15.056 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-101 - ZENT/USDT Bybit -> OKX

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bybit `ZENTUSDT`, sell OKX `ZENT-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -45.187 bps at 50 USDT, -61.318 bps at 100 USDT, -73.938 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-102 - HMSTR/USDT Bitget -> Binance

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Bitget `HMSTRUSDT`, sell Binance `HMSTRUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -11.695 bps at 50 USDT, -13.683 bps at 100 USDT, -14.876 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-103 - SWFTC/USDT MEXC -> OKX

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `SWFTCUSDT`, sell OKX `SWFTC-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -144.766 bps at 50 USDT, -172.257 bps at 100 USDT, -197.683 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-104 - ERG/USDT Gate -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `ERG_USDT`, sell KuCoin `ERG-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -57.741 bps at 50 USDT, -68.958 bps at 100 USDT, -110.344 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Live Refresh Update - 2026-05-29 06:26 CST

Top promoted/measured routes were refreshed over 20 samples from 06:23:09 to 06:26:10 CST with zero endpoint errors.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive, avg +337.641 bps, median +325.747 bps, min +222.469 bps. Public-book cap remains 10,000 USDT.
- `A2-031` VANRY MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +320.221 bps, median +314.789 bps, min +171.396 bps. Promote public-book cap to 5,000 USDT.
- `A2-037` VANRY MEXC -> Binance USDC: 5,000 USDC remains 20/20 positive, avg +679.794 bps, median +757.039 bps, min +342.530 bps. Promote measurement cap to 5,000 USDC.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +413.193 bps, median +444.004 bps, min +248.627 bps. 10,000 USDT degraded to 18/20 positive with min -134.628 bps, so downgrade firm public-book cap to 5,000 USDT and keep 10,000 USDT live-threshold-only.

## Operational Metadata Update - 2026-05-29 06:30 CST

- `A2-031` VANRY: MEXC public web coin metadata reports chain type `ETH` and Etherscan token `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`, matching Binance/KuCoin ERC20 identity. MEXC deposit/withdraw status and fee remain unverified publicly.
- `A2-023` ULTIMA: MEXC public web coin metadata reports chain type `SMART` and primary UltimaChain explorer, but also lists BSC explorer links for `0x5668a83B46016B494A30Dd14066A451E5417A8B8`, matching KuCoin BEP20. This reduces identity ambiguity but does not prove transfer compatibility.

Official announcement cross-check:

- `A2-031` VANRY: MEXC's Dec 1, 2023 swap announcement says VANRY withdrawals opened Dec 2, 2023 15:00 UTC and lists the same ERC20 contract.
- `A2-023` ULTIMA: MEXC's Apr 28, 2025 announcement says ULTIMA Mainnet deposits/withdrawals would be available starting Apr 29, 2025 14:00 UTC. This supports MEXC mainnet availability, but it does not prove compatibility with KuCoin's BEP20 lane.

MEXC current fee-page API:

- `A2-031` VANRY: MEXC public fee endpoint lists ETH/ERC20 with deposit fee `0`, withdrawal minimum `200` VANRY, and withdrawal fee `80` VANRY. It also lists native Vanar with withdrawal minimum `0.02` and fee `0.01`.
- `A2-023` ULTIMA: MEXC public fee endpoint lists `ULTIMA` and `SMART BLOCKCHAIN` rows only: ULTIMA min `0.0001`/fee `0.000025`, SMART min `0.006`/fee `0.003`. It does not list BEP20, so KuCoin BEP20 compatibility remains unproven.

Transfer-fee haircut check for `A2-031` VANRY:

- MEXC -> Binance USDT at 10,000 USDT remains +367.811 bps after subtracting the 80 VANRY MEXC ERC20 withdrawal fee.
- MEXC -> KuCoin USDT at 5,000 USDT remains +294.741 bps after subtracting the 80 VANRY MEXC ERC20 withdrawal fee.
- MEXC -> Binance USDC at 5,000 USDC remains +800.832 bps after subtracting the 80 VANRY MEXC ERC20 withdrawal fee.

## Candidate A2-105 - BOS/USDT KuCoin -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy KuCoin `BOS-USDT`, sell MEXC `BOSUSDT`
- quote lane: USDT
- public data quality: medium-high. Both venues identify BitcoinOS on ERC20 contract `0x13239c268beddd88ad0cb02050d3ff6a9d00de6d`; KuCoin withdrawals are enabled with 2,500 BOS fee and 5,000 BOS minimum.
- estimated net bps: +82.508 bps at 50 USDT, -20.759 bps at 100 USDT, -541.567 bps at 250 USDT, -949.086 bps at 500 USDT.
- executable notional estimate: none; positive pocket is below actionable size and transfer fee makes it worse.
- verdict: `KILL`.

## Candidate A2-106 - EGL1/USDT KuCoin -> Bitget / Gate

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy KuCoin `EGL1-USDT`, sell Bitget `EGL1USDT` or Gate `EGL1_USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps:
  - KuCoin -> Bitget: +11.796 bps at 50 USDT, -6.711 bps at 100 USDT, -67.337 bps at 250 USDT, -336.894 bps at 500 USDT.
  - KuCoin -> Gate: +6.456 bps at 50 USDT, -19.056 bps at 100 USDT, -99.017 bps at 250 USDT, -383.632 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-107 - GROK/USDT Gate -> MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy Gate `GROK_USDT`, sell MEXC `GROKUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps: +53.697 bps at 50 USDT, +48.305 bps at 100 USDT, -39.564 bps at 250 USDT, -108.346 bps at 500 USDT, -187.650 bps at 1,000 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-108 - ETN/USDT MEXC -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `ETNUSDT`, sell KuCoin `ETN-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -56.036 bps at 50 USDT, -58.605 bps at 100 USDT, -83.149 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-109 - QKC/USDT Binance/Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Binance `QKCUSDT` or Gate `QKC_USDT`, sell MEXC `QKCUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps:
  - Binance -> MEXC: -94.098 bps at 50 USDT, -103.037 bps at 100 USDT.
  - Gate -> MEXC: -181.385 bps at 50 USDT, -192.843 bps at 100 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-110 - UNION/USDT MEXC -> Gate

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `UNIONUSDT`, sell Gate `UNION_USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -54.049 bps at 50 USDT, -82.252 bps at 100 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-111 - JASMY/USDT Binance/Bitget/Bybit/Crypto.com -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by persistence
- route/assets/exchanges: buy Binance `JASMYUSDT`, Bitget `JASMYUSDT`, Bybit `JASMYUSDT`, or Crypto.com `JASMY_USDT`; sell MEXC `JASMYUSDT`
- quote lane: USDT
- public data quality: medium-high for identity. MEXC reports ETH/ERC20 contract `0x7420B4b9a0110cdC71fB720908340C03F9Bc03EC`; MEXC fee-page API lists ETH/ERC20 withdrawal minimum 364.8 JASMY and fee 60 JASMY; Bitget reports the same ERC20 contract with deposits/withdrawals enabled and 129.87013 JASMY withdrawal fee. Binance public market metadata confirms trading, but public network-fee row was not found. Bybit network status remains key-gated.
- estimated net bps:
  - Initial batch: Binance -> MEXC was positive through 10,000 USDT (+7.017 bps at 10,000); Bitget -> MEXC positive through 5,000 USDT (+15.541 bps at 5,000); Bybit -> MEXC positive through 5,000 USDT (+2.881 bps at 5,000); Crypto.com -> MEXC negative from 50 USDT.
  - 20-sample retest, 2026-05-29 06:41:16-06:45:00 CST, zero errors: all tested routes and sizes were 0/20 positive before transfer fees. Binance -> MEXC averaged -40.157 bps at 1,000 and -55.418 bps at 10,000; Bitget -> MEXC averaged -42.384 bps at 1,000 and -73.319 bps at 10,000; Bybit -> MEXC averaged -44.426 bps at 1,000 and -86.021 bps at 10,000.
- executable notional estimate: none; current books are negative before withdrawal fees.
- verdict: `KILL`.

## Candidate A2-112 - NYM/USDT Bitget -> Bybit

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy Bitget `NYMUSDT`, sell Bybit `NYMUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps: +31.969 bps at 50 USDT, +14.428 bps at 100 USDT, -1.333 bps at 250 USDT, -32.463 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-113 - POKT/USDT Gate -> KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `POKT_USDT`, sell KuCoin `POKT-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -430.804 bps at 50 USDT and worse.
- executable notional estimate: none.
- verdict: `KILL`.

## Live Refresh Update - 2026-05-29 06:51 CST

Top promoted/measured routes were refreshed over 20 samples from 06:48:35 to 06:50:59 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +288.674 bps, median +295.158 bps, min +186.532 bps. Public-book cap remains 10,000 USDT.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +424.332 bps, median +433.713 bps, min +326.369 bps. 10,000 USDT improved to 20/20 positive, avg +188.336 bps, median +192.750 bps, min +111.057 bps, but keep 10,000 USDT live-threshold-only until a second robust window and chain/rebalance proof exist.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +531.164 bps, median +531.664 bps, min +389.500 bps. 5,000 USDT degraded to 19/20 positive after withdrawal fee with min -6.995 bps, so downgrade firm cap to 2,500 USDT and keep 5,000 USDT live-threshold-only.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +840.004 bps, median +832.210 bps, min +628.647 bps. 5,000 USDC degraded to 19/20 positive after withdrawal fee with min -39.902 bps, so downgrade firm measurement cap to 2,500 USDC and keep 5,000 USDC live-threshold-only.

## Operational Metadata Update - 2026-05-29 06:55 CST

- `A2-031` VANRY: MEXC asset-page JavaScript exposes deposit/withdraw status endpoints, including `/api/platform/asset/api/asset/deposit/currency/query`, `/api/platform/asset/api/asset/withdraw/currency/query`, `/api/platform/asset/api/deposit/query/deposit/config`, and `/api/platform/asset/api/withdraw/query/config/v3`.
- VANRY public MEXC coin id is `5e1d77a033064e60bfdbac3c93a9579f`.
- Unauthenticated calls to the status/config endpoints returned `401 Unauthorized`. The chain matcher `/api/platform/asset/api/withdraw/match/chains?coinId=...&address=...` returned `400` without an address and `401` with dummy addresses.
- Operational read: public evidence now tops out at MEXC fee-page rows plus official/historical announcements. Current MEXC VANRY deposit/withdraw enabled flags require logged-in account-level verification.

## Funding Monitor Update - 2026-05-29 06:56 CST

- `A2-003` / `A2-019` spot-perp funding capture: refreshed with `scripts/funding_probe.py`.
- Scope: 47 public spot/perp proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International; zero endpoint errors.
- Best proxies remained negative: Coinbase INTX BTC -7.336 bps, Coinbase INTX DOGE -7.782 bps, Coinbase INTX ETH -9.216 bps, Coinbase INTX SOL -9.463 bps, Binance TRX negative-funding route -10.180 bps, Bybit TRX -10.515 bps, OKX TRX -12.073 bps.
- Verdict: keep as `LATER` monitor only. No funding route is close to VANRY spot-route EV after entry basis, fees, margin, borrow/inventory, and liquidation complexity.

## Bitso MXN/Stables Update - 2026-05-29 06:59 CST

- `A2-004` Bitso MXN/USD/stablecoin same-venue arbitrage: refreshed current public books.
- Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, `tusd_mxn`; zero endpoint errors.
- Best net results after conservative Bitso taker fees: PYUSD/MXN sell-vs-USD/MXN -60.914 bps; USDT/MXN buy-vs-USD/MXN -92.891 bps; RLUSD/MXN sell-vs-USD/MXN -102.606 bps; MXN -> USD -> USDT -> MXN -149.901 bps; MXN -> USDT -> USD -> MXN -151.290 bps.
- Verdict: remains `KILL` for immediate execution and `LATER` as a monitor only.

## Candidate A2-114 - ACA/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `ACA_USDT`, sell MEXC `ACAUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps: ticker snapshot ranked +55.210 bps, but live depth was -81.599 bps at 50 USDT, -106.138 bps at 100 USDT, -137.052 bps at 250 USDT, and -327.046 bps at 500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-115 - ES/USDT Gate -> KuCoin / MEXC

- approach type: micro cross-exchange spot altcoin arbitrage rejected by capacity
- route/assets/exchanges: buy Gate `ES_USDT`, sell KuCoin `ES-USDT` or MEXC `ESUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps:
  - Gate -> KuCoin: +30.512 bps at 50 USDT, +17.567 bps at 100 USDT, +6.684 bps at 250 USDT, -6.480 bps at 500 USDT.
  - Gate -> MEXC: -6.296 bps at 50 USDT, -23.145 bps at 100 USDT, -37.951 bps at 250 USDT.
- executable notional estimate: none; positive pocket is below actionable size.
- verdict: `KILL`.

## Candidate A2-116 - IN/USDT MEXC -> Bitget / KuCoin

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy MEXC `INUSDT`, sell Bitget `INUSDT` or KuCoin `IN-USDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps:
  - MEXC -> Bitget: -13.249 bps at 50 USDT, -14.749 bps at 100 USDT, -22.678 bps at 250 USDT.
  - MEXC -> KuCoin: -2.014 bps at 50 USDT, -3.970 bps at 100 USDT, -12.185 bps at 250 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-117 - OBOL/USDT Gate -> MEXC

- approach type: cross-exchange spot altcoin arbitrage rejected by depth
- route/assets/exchanges: buy Gate `OBOL_USDT`, sell MEXC `OBOLUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made transfer metadata unnecessary.
- estimated net bps: -28.665 bps at 50 USDT, -66.967 bps at 100 USDT, -146.257 bps at 250 USDT, -244.359 bps at 500 USDT; sell depth exhausted by 2,500 USDT.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-118 - SBUXON/USDT Gate -> MEXC

- approach type: tokenized-stock spot arbitrage rejected by capacity
- route/assets/exchanges: buy Gate `SBUXON_USDT`, sell MEXC `SBUXONUSDT`
- quote lane: USDT
- public data quality: medium; depth rejection made deeper transfer metadata unnecessary.
- estimated net bps: +15.004 bps at 50-250 USDT, -4.230 bps at 500 USDT, -36.209 bps at 1,000 USDT, -98.423 bps at 2,500 USDT.
- executable notional estimate: none; tiny positive pocket below actionable size and tokenized-stock transfer/rebalance overhead would dominate.
- verdict: `KILL`.

## Live Refresh Update - 2026-05-29 07:06 CST

Top promoted/measured routes were refreshed over 20 samples from 07:03:53 to 07:06:17 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +247.835 bps, median +245.205 bps, min +166.938 bps. Public-book cap remains 10,000 USDT.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 10,000 USDT now has two consecutive 20/20 positive book windows after the 06:23 negative-tail window. Latest 10,000 USDT: avg +156.310 bps, median +165.056 bps, min +87.097 bps. Promote public-book watch cap back to 10,000 USDT, but keep operational verdict pre-positioned-inventory-only until chain/rebalance proof exists.
- `A2-031` VANRY MEXC -> KuCoin USDT: 5,000 USDT recovered to 20/20 positive after withdrawal fee, avg +199.854 bps, median +206.638 bps, min +98.752 bps. Keep firm cap at 2,500 USDT and 5,000 USDT live-threshold-only because the prior window had a negative tail.
- `A2-037` VANRY MEXC -> Binance USDC: 5,000 USDC recovered to 20/20 positive after withdrawal fee, avg +446.982 bps, median +492.423 bps, min +35.959 bps. Keep firm measurement cap at 2,500 USDC and 5,000 USDC live-threshold-only because the prior window had a negative tail and this minimum is thin.

## Live Refresh Update - 2026-05-29 07:21 CST

Top promoted/measured routes were refreshed over 20 samples from 07:17:53 to 07:20:54 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut. Average REST RTT was 342 ms, max 761 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +335.844 bps, median +332.767 bps, min +302.966 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +571.989 bps, median +565.842 bps, min +549.809 bps. 5,000 USDT also stayed 20/20 positive, avg +200.446 bps, median +190.123 bps, min +167.040 bps. Promote public-book watch cap back to 5,000 USDT after two consecutive clean windows, subject to account/region and inventory gates.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +858.697 bps, median +848.734 bps, min +826.696 bps. 5,000 USDC also stayed 20/20 positive, avg +659.351 bps, median +679.419 bps, min +395.431 bps. Promote measurement cap back to 5,000 USDC, subject to account/region gate.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +452.052 bps, median +457.158 bps, min +322.974 bps. 10,000 USDT slipped to 19/20 positive, avg +210.970 bps, median +226.221 bps, min -9.418 bps. Downgrade public-book cap back to 5,000 USDT and keep 10,000 USDT live-threshold-only.

## Operational Region Gate Update - 2026-05-29 07:21 CST

- MEXC official restricted-jurisdiction page, updated Apr 17, 2026, lists the United States among prohibited jurisdictions and says MEXC does not accept user registrations or trading applications from those areas: `https://www.mexc.com/learn/article/mexc-restricted-countries-complete-list-of-prohibited-limited-regions/1?handleDefaultLocale=keep`.
- KuCoin Terms of Use, last updated Jan 29, 2026, require users to not be residents of or registered in restricted locations, and the restricted list includes the United States and U.S. territories: `https://www.kucoin.com/legal/terms-of-use`.
- Binance.US is not a VANRY fallback: `https://api.binance.us/api/v3/exchangeInfo?symbol=VANRYUSDT` and `VANRYUSDC` returned `{"code":-1121,"msg":"Invalid symbol."}`, the full Binance.US `exchangeInfo` response had 623 symbols and no `VANRY`, and the official Binance.US supported-crypto page contains no `VANRY`: `https://support.binance.us/hc/en-us/articles/360049417674-List-of-supported-cryptocurrencies`.
- Candidate impact: `A2-031`, `A2-037`, and `A2-023` stay valuable as scanner/watchlist candidates, but they are not execution-ready for a U.S.-resident account. Execution work only makes sense after Pedro confirms compliant non-U.S.-restricted account access, sell-venue inventory, and logged-in MEXC withdrawal status.

## U.S.-Available Venue Substitution Scan - 2026-05-29 07:29 CST

Scanned public top-of-book data for Binance.US, Coinbase Exchange, Kraken, Gemini, and Bitstamp.

- Markets scanned: 1,971.
- Common USD/USDT/USDC market keys: 378.
- Endpoint errors: 0.
- Fee assumptions were conservative: Binance.US 10 bps, Coinbase 120 bps, Kraken 40 bps, Gemini 120 bps, Bitstamp 40 bps, plus 2-4 bps latency haircut.
- Result: no promotion. Liquid major routes were negative after fees; positive long-tail rows were either ticker collisions or failed depth.

## Candidate A2-119 - LIT/USD Kraken -> Bitstamp

- approach type: U.S.-available cross-exchange spot arbitrage rejected by identity
- route/assets/exchanges: buy Kraken `LITUSD`, sell Bitstamp `LITUSD`
- quote lane: USD
- public data quality: high enough to reject. Kraken public pages identify `LIT` as Litentry; Bitstamp trading-pair info describes `LIT/USD` as Lighter / U.S. dollar.
- estimated net bps: live depth looked hugely positive through 1,000 USD because these are different assets: +104,331 bps at 50 USD, +103,488 bps at 500 USD, +102,334 bps at 1,000 USD.
- executable notional estimate: invalid.
- verdict: `KILL`.

## Candidate A2-120 - VELO/USD Kraken -> Coinbase

- approach type: U.S.-available cross-exchange spot arbitrage rejected by identity
- route/assets/exchanges: buy Kraken `VELOUSD`, sell Coinbase `VELO-USD`
- quote lane: USD
- public data quality: high enough to reject. Kraken lists `VELO` as Velo and separately lists Velodrome Finance under `VELODROME`; Coinbase Exchange currency metadata identifies `VELO` as Velodrome Finance on Optimism contract `0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db`.
- estimated net bps: live depth appeared hugely positive through 5,000 USD because of ticker collision: +27,044 bps at 50 USD, +26,862 bps at 1,000 USD, +26,607 bps at 5,000 USD.
- executable notional estimate: invalid.
- verdict: `KILL`.

## Candidate A2-121 - SUP/USD Kraken -> Coinbase

- approach type: U.S.-available cross-exchange spot arbitrage rejected by identity
- route/assets/exchanges: buy Kraken `SUPUSD`, sell Coinbase `SUP-USD`
- quote lane: USD
- public data quality: high enough to reject. Kraken public pages identify `SUP` as Superp; Coinbase Exchange currency metadata identifies `SUP` as Superfluid on Base contract `0xa69f80524381275A7fFdb3AE01c54150644c8792`.
- estimated net bps: live depth appeared hugely positive through 5,000 USD because of ticker collision: +22,223 bps at 50 USD, +21,825 bps at 1,000 USD, +19,028 bps at 5,000 USD.
- executable notional estimate: invalid.
- verdict: `KILL`.

## Candidate A2-122 - GWEI/USD Kraken -> Coinbase

- approach type: U.S.-available cross-exchange spot arbitrage rejected by depth
- route/assets/exchanges: buy Kraken `GWEIUSD`, sell Coinbase `GWEI-USD`
- quote lane: USD
- public data quality: medium-high. Coinbase Exchange currency metadata identifies `GWEI` as Ethgas on Ethereum contract `0x2798b1cC5A993085E8A9D46e80499F1B63f42204`; Kraken public asset metadata only confirms ticker status, so full identity still needs stronger confirmation.
- estimated net bps: top-of-book scan showed only +14.403 bps after conservative fees; live depth was negative from 50 USD: -223.485 bps at 50 USD, -238.590 bps at 1,000 USD, -304.427 bps at 5,000 USD.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-123 - TRAC/USD Kraken -> Bitstamp

- approach type: U.S.-available cross-exchange spot arbitrage rejected by depth
- route/assets/exchanges: buy Kraken `TRACUSD`, sell Bitstamp `TRACUSD`
- quote lane: USD
- public data quality: medium-high. Bitstamp describes `TRAC/USD` as OriginTrail / U.S. dollar; Kraken exposes enabled `TRAC` asset and `TRACUSD` market.
- estimated net bps: top-of-book scan showed only +1.337 bps after conservative fees; live depth was negative from 50 USD: -77.963 bps at 50 USD, -143.309 bps at 500 USD, -204.804 bps at 5,000 USD.
- executable notional estimate: none.
- verdict: `KILL`.

## Candidate A2-124 - U.S.-Available Maker/Rebate Rescue

- approach type: maker/rebate or maker-taker cross-exchange strategy
- route/assets/exchanges: Binance.US, Coinbase Exchange, Kraken, Gemini, Bitstamp USD/USDT/USDC routes
- quote lane: USD/USDT/USDC, kept separate
- why edge might exist: if one leg can rest as maker at zero or rebate fee, the fee hurdle drops versus taker-taker static arbitrage.
- public data quality: medium-high for fee schedules, low for fill probability. Binance.US says Advanced Spot fees are 0% maker and 0.02% taker for every user; Kraken publishes a spot maker-rebate table, but rebate starts only at high 30-day volume on selected pairs; Coinbase Advanced VIP best public spot tier is 0 bps maker / 3.5 bps taker at institutional-scale VIP 6.
- fee assumptions: Binance.US 0 maker / 2 bps taker; Kraken low-tier spot still 25 maker / 40 taker unless account volume qualifies; Coinbase retail still high unless VIP-qualified; Gemini/Bitstamp no public retail rebate found.
- estimated net bps: not enough for immediate static routes. The 07:29 U.S.-venue static scan had liquid major routes around -43 to -51 bps after conservative taker fees; replacing one Binance.US leg with 0 maker improves the hurdle but does not create a clear positive route without fill-probability edge, queue priority, or lower sell-venue fees.
- executable notional estimate: none without a queue/fill model and account-specific fee proof.
- implementation effort: medium-high. Requires post-only order management, cancel/replace logic, queue/slippage model, inventory reservation, and adverse-selection controls.
- inventory/funding requirements: base and quote inventory on both venues; post-only leg may sit unfilled or get adversely selected.
- risks: one-leg fill, queue loss, adverse selection, stale books, no guaranteed rebate, account tier mismatch, API post-only behavior differences.
- confidence: high for killing immediate execution; medium for keeping as a later scanner feature.
- verdict: `KILL` for immediate profit; `LATER` as an event-window/maker-queue research path.

Sources:

- Binance.US zero-fee announcement: `https://blog.binance.us/zero-fee-trading/`
- Binance.US Market Maker Program: `https://support.binance.us/en/articles/9842933-what-is-the-binance-us-market-maker-program`
- Kraken fee schedule: `https://www.kraken.com/features/fee-schedule`
- Coinbase Advanced VIP: `https://www.coinbase.com/advanced-vip`

## Live Refresh Update - 2026-05-29 07:39 CST

Top promoted/measured routes were refreshed over 20 samples from 07:36:10 to 07:39:15 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut. Average REST RTT was 367 ms, max 939 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +383.266 bps, median +383.912 bps, min +313.524 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +613.227 bps, median +603.401 bps, min +549.855 bps. 5,000 USDT also stayed 20/20 positive, avg +264.939 bps, median +275.924 bps, min +127.310 bps. Public-book cap remains 5,000 USDT, subject to account/region and inventory gates.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +903.328 bps, median +908.837 bps, min +806.101 bps. 5,000 USDC also stayed 20/20 positive, avg +458.736 bps, median +486.921 bps, min +52.608 bps. Measurement cap remains 5,000 USDC, subject to account/region gate.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +427.839 bps, median +453.916 bps, min +329.718 bps. 10,000 USDT recovered to 20/20 positive, avg +159.973 bps, median +190.413 bps, min +36.634 bps. Keep firm public-book cap at 5,000 USDT and 10,000 USDT live-threshold-only until another clean window follows the prior negative tail.

## Funding Monitor Update - 2026-05-29 07:42 CST

- `A2-003` / `A2-019` spot-perp funding capture: refreshed with `scripts/funding_probe.py`.
- Scope: 47 public spot/perp proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International; zero endpoint errors; elapsed 23.245 seconds.
- Best proxies remained negative after entry basis and round-trip fees:
  - Coinbase INTX BTC USDC: -6.535 bps over 1h proxy.
  - Coinbase INTX ETH USDC: -8.212 bps over 1h proxy.
  - Coinbase INTX XRP USDC: -10.401 bps over 1h proxy.
  - Coinbase INTX SOL USDC: -10.444 bps over 1h proxy.
  - Coinbase INTX DOGE USDC: -10.832 bps over 1h proxy.
  - Best USDT negative-funding route was Bybit TRX at -18.189 bps over 8h proxy.
- Verdict: keep as `LATER` monitor only. Coinbase INTX BTC improved versus the prior -7.336 bps reading, but it is still negative and materially lower EV than the VANRY public-book route.

## Bitso MXN/Stables Update - 2026-05-29 07:43 CST

- `A2-004` Bitso MXN/USD/stablecoin same-venue arbitrage: refreshed current public books.
- Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`; zero endpoint errors.
- Current top-of-book reference: `usd_mxn` 17.347/17.350, `usdt_mxn` 17.326/17.330, `usd_usdt` 1.0009/1.0011.
- Best net results after conservative Bitso taker fees:
  - PYUSD/MXN sell bid vs USD/MXN ask: -61.841 bps.
  - USDT/MXN buy ask vs USD/MXN bid: -89.791 bps.
  - RLUSD/MXN sell bid vs USD/MXN ask: -101.785 bps.
  - MXN -> USDT -> USD -> MXN: -130.714 bps.
  - MXN -> USD -> USDT -> MXN: -173.687 bps.
- Verdict: remains `KILL` for immediate execution and `LATER` as a monitor only.

## Fresh Global Probe Update - 2026-05-29 07:48 CST

- Scope: 10,216 public spot markets across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso.
- Filtered top-of-book watch rows: 99.
- Endpoint errors: 0.
- Top new depth-checked routes: `TBC`, `YFII`, `DCK`, `DN`, `AO`, `HONEY`, `AVL`, and `QAIT`.
- Result: no execution promotion.

## Candidate A2-125 - TBC/USDT MEXC -> Gate

- approach type: cross-exchange spot altcoin arbitrage, pre-positioned-only watch
- route/assets/exchanges: buy MEXC `TBCUSDT`, sell Gate `TBC_USDT`
- quote lane: USDT
- why edge might exist: MEXC ask was materially below Gate bid in the fresh top-of-book scan, and live depth stayed positive through the 5,000 USDT bucket.
- public data quality: medium-high for identity and sell-venue status. MEXC identifies `TBC` as Turingbitchain with chain type `TBC`, website `https://tbc.top/`, and explorer `https://explorer.turingbitchain.io/`. Gate identifies `TBC` as TuringBitChain on chain `TBC`.
- fee assumptions: MEXC taker 5 bps from symbol metadata; Gate pair fee 20 bps from `GET /api/v4/spot/currency_pairs/TBC_USDT`.
- estimated net bps: after venue fees and live depth, +530.107 bps at 50 USDT, +496.723 bps at 500 USDT, +444.676 bps at 1,000 USDT, +361.165 bps at 2,500 USDT, +196.087 bps at 5,000 USDT.
- executable notional estimate: public book supports up to 5,000 USDT in the sampled snapshot, but not repeatably executable via transfer because Gate deposits are disabled.
- frequency/duration evidence or proxy: one fresh top-of-book scan plus live depth validation at 2026-05-29 07:48 CST, then a 10-sample persistence check from 07:48:32 to 07:49:30 CST. The persistence check was 10/10 positive at 1,000, 2,500, and 5,000 USDT; 5,000 USDT avg +198.175 bps, median +198.175 bps, min +196.087 bps.
- implementation effort: low for scanner watch, high for live execution because it requires existing TBC inventory on Gate and a rebalance plan.
- inventory/funding requirements: USDT on MEXC and TBC already pre-positioned on Gate. MEXC -> Gate rebalance is blocked by Gate `deposit_disabled=true`.
- risks: Gate deposits disabled, MEXC public fee-page returned no TBC withdrawal-fee row, long-tail book can vanish, and repeatability is structurally blocked without sell-venue inventory.
- confidence: high for killing repeatable transfer-dependent execution; medium that a one-shot pre-positioned inventory liquidation could exist.
- verdict: `LATER` / pre-positioned-inventory-only. `KILL` as a repeatable direct route.

## Candidate A2-126 - Fresh 07:48 Non-TBC Watch Rows

- approach type: cross-exchange spot altcoin arbitrage rejected by depth/capacity
- route/assets/exchanges: `YFII` MEXC -> Gate, `DCK` Gate -> MEXC, `DN` KuCoin -> Gate, `AO` Bybit/MEXC -> Gate, `HONEY` MEXC -> Gate, `AVL` MEXC -> Gate, `QAIT` Gate -> KuCoin
- quote lane: USDT
- public data quality: enough to reject on depth before transfer metadata.
- estimated net bps:
  - `YFII` MEXC -> Gate: negative from 50 USDT (-232.151 bps).
  - `DCK` Gate -> MEXC: positive only at 50 USDT (+128.051 bps), negative by 100 USDT.
  - `DN` KuCoin -> Gate: negative from 50 USDT (-104.113 bps).
  - `AO` Bybit -> Gate: positive through 1,000 USDT (+125.928 bps), negative by 2,500 USDT; below current actionability threshold and requires Gate transfer/status work.
  - `AO` MEXC -> Gate: positive only through 500 USDT (+30.972 bps), negative by 1,000 USDT.
  - `HONEY` MEXC -> Gate: negative from 50 USDT (-50.480 bps).
  - `AVL` MEXC -> Gate: negative from 50 USDT (-92.154 bps).
  - `QAIT` Gate -> KuCoin: positive through 250 USDT (+45.167 bps), negative by 500 USDT.
- executable notional estimate: none for current execution queue.
- verdict: `KILL`.

## Live Refresh Update - 2026-05-29 07:54 CST

Top promoted/measured routes were refreshed over 20 samples from 07:50:48 to 07:53:52 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut. Average REST RTT was 365 ms, max 904 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +329.739 bps, median +315.849 bps, min +198.804 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +678.036 bps, median +682.861 bps, min +573.681 bps. 5,000 USDT also stayed 20/20 positive, avg +338.403 bps, median +315.598 bps, min +147.427 bps. Public-book cap remains 5,000 USDT, subject to account/region and inventory gates.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +870.145 bps, median +875.341 bps, min +705.368 bps. 5,000 USDC degraded to 19/20 positive, avg +569.820 bps, median +637.354 bps, min -240.917 bps. Downgrade firm measurement cap back to 2,500 USDC and keep 5,000 USDC live-threshold-only.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +418.842 bps, median +433.213 bps, min +347.424 bps. 10,000 USDT also stayed 20/20 positive, avg +172.344 bps, median +181.786 bps, min +124.205 bps. Promote public-book watch cap back to 10,000 USDT after two clean windows following the prior negative tail, but keep operational verdict pre-positioned-inventory-only until chain/rebalance proof exists.

## U.S.-Available Corrected-Fee Retest - 2026-05-29 08:02 CST

Retested the prior best liquid U.S.-available rows after correcting Binance.US taker from the earlier conservative 10 bps assumption to the official 2 bps public taker fee. This does not change the verdict.

- approach type: U.S.-available static cross-exchange spot arbitrage, targeted retest
- route/assets/exchanges: Bitstamp/Kraken -> Binance.US on BTC/USD, BTC/USDT, SOL/USD, HYPE/USD, and USDT/USD
- quote lane: USD and USDT
- fee assumptions: Binance.US taker 2 bps, Kraken taker 40 bps, Bitstamp taker 40 bps, plus 2-4 bps latency/lane haircut.
- estimated net bps:
  - BTC/USD Bitstamp -> Binance.US: -38.074 bps.
  - BTC/USDT Bitstamp -> Binance.US: -47.772 bps.
  - SOL/USD Bitstamp -> Binance.US: -44.893 bps.
  - HYPE/USD Bitstamp -> Binance.US: -53.955 bps.
  - USDT/USD Kraken -> Binance.US: -42.495 bps.
- executable notional estimate: none while all targeted liquid rows remain negative before depth work.
- verdict: `KILL` for immediate static execution. Binance.US remains useful only for future post-only/event-window monitoring.

## Live Refresh Update - 2026-05-29 08:06 CST

Top promoted/measured routes were refreshed over 20 samples from 08:03:20 to 08:05:55 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut. Average REST RTT was 338 ms, max 766 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +366.562 bps, median +386.150 bps, min +225.977 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +729.932 bps, median +740.520 bps, min +364.676 bps. 5,000 USDT degraded to 19/20 positive, avg +374.543 bps, median +359.060 bps, min -18.398 bps. Downgrade firm cap back to 2,500 USDT and keep 5,000 USDT live-threshold-only.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +980.902 bps, median +990.513 bps, min +923.892 bps. 5,000 USDC recovered to 20/20 positive, avg +765.741 bps, median +794.771 bps, min +231.561 bps. Keep firm measurement cap at 2,500 USDC until another clean 5,000 USDC window follows the prior negative tail.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +364.926 bps, median +393.661 bps, min +213.670 bps. 10,000 USDT degraded to 17/20 positive, avg +132.559 bps, median +168.648 bps, min -59.587 bps. Downgrade public-book cap back to 5,000 USDT and keep operational verdict pre-positioned-inventory-only until chain/rebalance proof exists.

## Candidate A2-127 - Crypto.com USD -> Bitfinex USD Majors

- approach type: cross-exchange spot major-pair arbitrage, USD lane
- route/assets/exchanges: buy Crypto.com `BTC_USD`, `ETH_USD`, `XRP_USD`, or `SOL_USD`; sell Bitfinex `tBTCUSD`, `tETHUSD`, `tXRPUSD`, or `tSOLUSD`
- quote lane: USD
- why edge might exist: the fresh public probe showed small top-of-book positives on Crypto.com -> Bitfinex after treating Bitfinex's current official spot taker fee as 0 bps.
- public data quality: high for market data and Bitfinex fee schedule; medium for account execution because Bitfinex official support says U.S. persons cannot use the platform.
- fee assumptions: Crypto.com 7.5 bps taker, Bitfinex 0 bps taker from `https://www.bitfinex.com/fees/`, plus 4 bps USD-lane latency/staleness haircut.
- estimated net bps:
  - Initial depth snapshot at 08:10 CST: BTC/USD was barely positive through 25,000 USD (+1.651 to +1.839 bps), while ETH/USD, XRP/USD, and SOL/USD were negative from 1,000 USD.
  - BTC/USD 10-sample persistence from 08:10:32 to 08:11:18 CST failed: 1,000 USD 0/10 positive avg -1.738 bps; 5,000 USD 0/10 avg -1.797 bps; 10,000 USD 0/10 avg -1.854 bps; 25,000 USD 0/10 avg -2.063 bps.
- executable notional estimate: none for immediate execution; the only initially positive pair failed persistence.
- frequency/duration evidence or proxy: one fresh global top-of-book probe, one live depth snapshot, and one 10-sample BTC persistence check with zero endpoint errors.
- implementation effort: low to keep in scanner; not worth execution work.
- inventory/funding requirements: USD on Crypto.com and base inventory on Bitfinex, or fast rebalance between venues. Bitfinex access requires a non-U.S.-person eligible account.
- risks: tiny edge, rapid decay, fiat/USD balance fragmentation, account-region gate, Bitfinex U.S.-person restriction, and adverse selection on a sub-2 bps signal.
- confidence: high for killing immediate execution; medium for keeping as a generic low-priority monitor.
- verdict: `KILL` for immediate execution. `LATER` only as a scanner regression case for zero-fee Bitfinex majors.

## Funding Monitor Update - 2026-05-29 08:13 CST

- `A2-003` / `A2-019` spot-perp funding capture: refreshed with `scripts/funding_probe.py`.
- Scope: 47 public spot/perp proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International; zero endpoint errors; elapsed 19.436 seconds.
- Best proxies remained negative after entry basis and round-trip fees:
  - Coinbase INTX SOL USDC: -7.982 bps over 1h proxy.
  - Coinbase INTX BTC USDC: -8.168 bps over 1h proxy.
  - Coinbase INTX ETH USDC: -8.759 bps over 1h proxy.
  - Coinbase INTX DOGE USDC: -11.860 bps over 1h proxy.
  - Coinbase INTX XRP USDC: -11.950 bps over 1h proxy.
  - Best USDT negative-funding route was Binance WLD at -12.436 bps over 8h proxy.
- Verdict: keep as `LATER` monitor only. The best proxy worsened versus the 07:42 refresh and remains materially lower EV than the VANRY public-book route.

## Bitso MXN/Stables Update - 2026-05-29 08:14 CST

- `A2-004` Bitso MXN/USD/stablecoin same-venue arbitrage: refreshed current public books.
- Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`; zero endpoint errors.
- Current top-of-book reference: `usd_mxn` 17.357/17.358, `usdt_mxn` 17.341/17.350, `usd_usdt` 1.0006/1.0009.
- Best net results after conservative 50 bps per Bitso taker leg:
  - PYUSD/MXN sell bid vs USD/MXN ask: -59.255 bps.
  - USD/MXN sell bid vs USDT/MXN buy ask: -95.756 bps.
  - RLUSD/MXN sell bid vs USD/MXN ask: -99.180 bps.
  - MXN -> USD -> USDT -> MXN: -152.994 bps.
  - MXN -> USDT -> USD -> MXN: -154.138 bps.
- Verdict: remains `KILL` for immediate execution and `LATER` as a monitor only.

## Live Refresh Update - 2026-05-29 08:19 CST

Top promoted/measured routes were refreshed over 20 samples from 08:16:13 to 08:18:47 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut. Average REST RTT was 334 ms, max 838 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +333.599 bps, median +338.015 bps, min +103.743 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +719.753 bps, median +706.190 bps, min +598.177 bps. 5,000 USDT recovered to 20/20 positive, avg +332.214 bps, median +324.395 bps, min +63.884 bps. Keep firm cap at 2,500 USDT and 5,000 USDT live-threshold-only until another clean window follows the 08:06 negative tail.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +938.581 bps, median +969.931 bps, min +619.614 bps. 5,000 USDC degraded again to 18/20 positive, avg +694.238 bps, median +852.114 bps, min -240.586 bps. Firm measurement cap remains 2,500 USDC.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +421.490 bps, median +429.266 bps, min +348.127 bps. 10,000 USDT recovered to 20/20 positive, avg +182.428 bps, median +178.313 bps, min +115.511 bps. Keep public-book cap at 5,000 USDT until another clean 10,000 USDT window follows the 08:06 negative tail; operational verdict remains pre-positioned-inventory-only until chain/rebalance proof exists.

## Candidate A2-128 - ESPORTS/RAVE Pre-Positioned Inventory Watches

- approach type: cross-exchange spot long-tail arbitrage, pre-positioned-only watch
- route/assets/exchanges: buy MEXC `ESPORTSUSDT`, sell Gate `ESPORTS_USDT`; buy Bitget `RAVEUSDT`, sell KuCoin `RAVE-USDT` or Gate `RAVE_USDT`
- quote lane: USDT
- why edge might exist: fresh hard-filter discovery found large, depth-surviving price fragmentation on matching public symbols.
- public data quality: high for market data and sell-venue deposit status; medium for MEXC public wallet status because account-gated checks are still required.
- identity/status evidence:
  - ESPORTS: MEXC `exchangeInfo` identifies `Yooldo Games`, BSC contract `0xF39e4b21c84e737Df08e2C3b32541d856f508E48`; Gate identifies `Yooldo` on BSC with the same contract, but `deposit_disabled=true`.
  - RAVE: MEXC `exchangeInfo` identifies `RaveDAO`, ERC20 contract `0x17205fab260a7a6383a81452cE6315A39370Db97`; Bitget, KuCoin ERC20, and Gate ETH metadata point to the same contract. KuCoin and Gate deposits are disabled; Bitget also reports `rechargeable=false`.
- fee assumptions: MEXC taker 5 bps, Bitget taker 10 bps, KuCoin taker 10 bps, Gate pair fee treated as 20 bps.
- estimated net bps:
  - ESPORTS MEXC -> Gate depth snapshot: positive through 5,000 USDT, from +3861.479 bps at 50 USDT to +2349.071 bps at 5,000 USDT.
  - RAVE Bitget -> KuCoin depth snapshot: positive through 5,000 USDT, from +1616.779 bps at 50 USDT to +1478.349 bps at 5,000 USDT.
  - RAVE Bitget -> Gate depth snapshot: positive through 5,000 USDT, from +2153.920 bps at 50 USDT to +260.905 bps at 5,000 USDT.
  - 10-sample persistence from 08:23:41 to 08:24:29 CST: ESPORTS MEXC -> Gate 5,000 USDT 10/10 positive, avg +2400.213 bps, min +2361.826 bps; RAVE Bitget -> KuCoin 5,000 USDT 10/10 positive, avg +1482.521 bps, min +1465.754 bps; RAVE Bitget -> Gate 5,000 USDT 10/10 positive, avg +194.290 bps, min +171.865 bps.
- executable notional estimate: up to 5,000 USDT in public-book samples for one-shot pre-positioned-inventory liquidation only.
- frequency/duration evidence or proxy: one fresh hard-filter scan, one depth snapshot, and one 10-sample persistence check; zero endpoint errors.
- implementation effort: low for scanner watch, high for execution because it requires existing sell-venue inventory and a rebalance plan outside disabled deposits.
- inventory/funding requirements: quote inventory on the buy venue and existing ESPORTS/RAVE inventory on the sell venue. Repeatable MEXC/Bitget -> Gate/KuCoin transfer is blocked while sell-venue deposits are disabled.
- risks: sell-venue deposits disabled, long-tail books can vanish, account/region restrictions, MEXC current withdrawal status remains unverified publicly, and pre-positioned inventory may be impossible to replenish.
- confidence: high that the public books show real pre-positioned liquidation pockets; high that transfer-dependent repeatable execution is blocked.
- verdict: `LATER` / pre-positioned-inventory-only. `KILL` as repeatable direct transfer routes.

## Candidate A2-129 - Fresh 08:22 Non-ESPORTS/RAVE Watch Rows

- approach type: cross-exchange spot long-tail arbitrage rejected by identity, deposit status, or depth capacity
- route/assets/exchanges: `RWA`, `ARTFI`, `UPC`, `PHB`, `GUA`, `POWER`, `NERO`, and related top rows from the 08:21 hard-filter scan
- quote lane: USDT
- public data quality: high enough to reject before execution work.
- rejection evidence:
  - `RWA` is a same-ticker collision: MEXC/Gate/Bitget identify BSC Allo contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`, while KuCoin identifies Base RWA Inc contract `0xe2b1dc2d4a3b4e59fdf0c47b71a7a86391a8b35a`.
  - `ARTFI` contracts match on SUI, but Gate, KuCoin, and Bitget public metadata all show deposits disabled or withdrawals disabled; depth also turns negative by 500-1,000 USDT depending on sell venue.
  - `UPC`, `PHB`, `GUA`, `POWER`, and `NERO` had positive pockets, but the relevant sell venues reported deposits disabled, and most failed capacity before or around the 2,500-5,000 USDT bucket.
- executable notional estimate: none for repeatable direct transfer execution.
- verdict: `KILL` for direct execution. Revisit only if deposits reopen and identity/contract status remains clean.

## Candidate A2-130 - Deposit-Enabled Long-Tail Follow-Up

- approach type: cross-exchange spot long-tail arbitrage rejected by identity/depth
- route/assets/exchanges: `AI`, `ALEX`, `PUSH`, `SAMO`, `SNEK`, `OGPU`, `REACT`, `AFC`, and `ROUTE` rows from the 08:28 deposit-enabled filter
- quote lane: USDT
- why edge might exist: after removing disabled-deposit sell venues, a smaller set still showed positive top-of-book spreads.
- public data quality: high enough to reject. Sell-venue deposit metadata came from official Gate, KuCoin, and Bitget public endpoints; MEXC deposit flags remain account-gated.
- rejection evidence:
  - `AI` Gate -> KuCoin/MEXC was a same-ticker collision. Gate identifies `AI` as Sleepless AI on BSC contract `0xBDA011D7F8EC00F66C1923B049B94c67d148d8b2`; KuCoin and MEXC identify `AI` as Gensyn on ERC20 contract `0x4d7078ddd6ccfed2f85db5b7d3ff16828d378d48`.
  - `ALEX` KuCoin -> Gate was positive only at 50 USDT (+39.357 bps) and negative by 100 USDT.
  - `PUSH` MEXC -> KuCoin was positive only at 50-100 USDT and negative by 250 USDT.
  - `SNEK` MEXC/Gate -> Bitget was positive only below 500 USDT and negative by 500 USDT.
  - `REACT` KuCoin -> Gate was positive only at 50-100 USDT and negative by 250 USDT.
  - `AFC`, `SAMO`, `OGPU`, and `ROUTE` were negative from the first tested bucket.
- executable notional estimate: none for current execution queue.
- verdict: `KILL`.

## Live Refresh Update - 2026-05-29 08:36 CST

Top promoted/measured routes were refreshed over 20 samples from 08:33:56 to 08:35:42 CST with zero endpoint errors. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as a haircut. Average REST RTT was 555 ms, max 757 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after withdrawal fee, avg +411.982 bps, median +392.735 bps, min +279.530 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 2,500 USDT remains 20/20 positive after withdrawal fee, avg +767.151 bps, median +788.295 bps, min +629.933 bps. 5,000 USDT also stayed 20/20 positive, avg +314.227 bps, median +327.305 bps, min +90.449 bps. Restore firm public-book cap to 5,000 USDT for non-U.S. compliant setups, with live threshold checks.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC remains 20/20 positive after withdrawal fee, avg +1036.801 bps, median +1051.977 bps, min +951.777 bps. 5,000 USDC recovered to 20/20 positive, avg +735.275 bps, median +846.203 bps, min +265.036 bps. Keep firm measurement cap at 2,500 USDC until another clean 5,000 USDC window follows the 08:19 negative tail.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT remains 20/20 positive, avg +434.868 bps, median +446.588 bps, min +316.276 bps. 10,000 USDT also stayed 20/20 positive, avg +187.755 bps, median +210.437 bps, min +1.226 bps. Keep public-book cap at 5,000 USDT because the 10,000 USDT tail is too thin and the route still lacks MEXC SMART/BEP20 rebalance proof.

## Candidate A2-131 - Fresh 08:39 Processed-Base Exclusion Cluster

- approach type: cross-exchange spot long-tail arbitrage rejected by live depth
- route/assets/exchanges: `SHR`, `LKI`, `BNKR`, `GHX`, `CWEB`, `WOJAK`, `PYBOBO`, `KEKIUS`, `DEVVE`, and `ASSET` from the 08:39 filtered scan
- quote lane: USDT
- why edge might exist: a fresh processed-base exclusion scan covered 10,213 public markets with zero endpoint errors and found 58 filtered long-tail rows with top-of-book net spreads above 25 bps after known-fee assumptions.
- public data quality: high enough to reject on optimistic live depth before transfer fees. Many top rows sold into MEXC, where current deposit status remains account-gated, but the depth failure happens before that operational gate matters.
- rejection evidence:
  - `SHR` KuCoin -> MEXC was negative from 50 USDT (-11.371 bps).
  - `LKI` KuCoin -> MEXC was negative from 50 USDT (-513.408 bps).
  - `BNKR` Gate/KuCoin -> MEXC stayed positive through 500 USDT but was negative by 1,000 USDT (-9.392 bps from Gate, -10.959 bps from KuCoin) before transfer fees.
  - `GHX` KuCoin/Gate -> MEXC was positive only below 250 USDT and negative by 250 USDT.
  - `CWEB` KuCoin -> MEXC was positive only through 250 USDT and negative by 500 USDT.
  - `WOJAK` MEXC -> Gate was negative from 50 USDT (-115.496 bps).
  - `PYBOBO` MEXC -> Bybit was positive only at 50-100 USDT and negative by 250 USDT.
  - `KEKIUS`, `DEVVE`, and `ASSET` were positive only at tiny buckets and negative by 100-1,000 USDT.
- executable notional estimate: none for current execution queue.
- verdict: `KILL`.

## Candidate A2-132 - SPX Bybit/MEXC -> KuCoin Event-Window Watch

- approach type: cross-exchange spot altcoin arbitrage, measured watch
- route/assets/exchanges: buy Bybit `SPXUSDT` or MEXC `SPXUSDT`; sell KuCoin `SPX-USDT`
- quote lane: USDT
- why edge might exist: the 08:41-08:44 event-window sampler found `SPX` as the only depth-surviving row after repeated top-of-book sampling and live depth checks.
- public data quality: medium. MEXC, Gate, and KuCoin metadata align on SPX6900 ERC20 contract `0xe0f63a424a4439cbe457d80e4f4b51ad25b2c56c`; KuCoin ERC20 deposits/withdrawals are enabled. Bybit confirms `SPXUSDT` is trading, but Bybit coin/withdrawal metadata requires an API key, so Bybit transfer status and contract identity are not publicly proven. MEXC current wallet status remains account-gated.
- fee assumptions:
  - Bybit taker 10 bps, KuCoin taker 10 bps; Bybit withdrawal fee/status not included because the public endpoint is account-gated.
  - MEXC taker 5 bps, KuCoin taker 10 bps, and the MEXC public fee API lists an SPX ERC20 withdrawal fee of 3 SPX with minimum withdrawal 21.6 SPX.
- estimated net bps:
  - SPX Bybit -> KuCoin, no transfer-fee haircut: 10-sample persistence from 08:46:31 to 08:47:27 CST had 1,000 USDT 10/10 positive avg +54.558 bps, min +50.381; 2,500 USDT 10/10 avg +40.231, min +36.333; 5,000 USDT 10/10 avg +18.703, min +14.532; 10,000 USDT 0/10 avg -11.459.
  - SPX MEXC -> KuCoin after 3 SPX fee: 1,000 USDT 10/10 positive avg +30.325 bps, min +25.687; 2,500 USDT 10/10 avg +12.974, min +4.044; 5,000 USDT 0/10 avg -33.411.
- executable notional estimate: Bybit -> KuCoin up to 5,000 USDT only as an optimistic public-book measurement until logged-in Bybit withdrawal status/fee/contract is confirmed. MEXC -> KuCoin firm measurement cap is 1,000 USDT; 2,500 USDT is too thin and requires live thresholding.
- frequency/duration evidence or proxy: 8-sample event-window top-of-book sampler with zero endpoint errors, one live depth snapshot across persistent rows, and one 10-sample SPX-focused depth persistence check with zero endpoint errors.
- implementation effort: low for scanner/watchlist; medium for execution because it needs Bybit/MEXC logged-in wallet proof, KuCoin receiving-chain selection, and region/account proof.
- inventory/funding requirements: USDT on Bybit or MEXC and SPX sell inventory or fast transfer into KuCoin ERC20. KuCoin ERC20 deposit is enabled with deposit minimum 0.3 SPX; KuCoin ERC20 withdrawal fee is 4 SPX if rebalancing out.
- risks: thin edge, Bybit transfer metadata account-gated, MEXC wallet status account-gated, MEXC/KuCoin U.S.-resident restrictions, long-tail liquidity decay, and transfer latency against a 15-55 bps signal.
- confidence: medium for real same-asset SPX on MEXC/KuCoin/Gate; low-medium for Bybit leg until wallet metadata is proven.
- verdict: `MEASURE`, below VANRY/ULTIMA. Not execution-ready.

## Live Refresh Update - 2026-05-29 08:53 CST

Top watch routes were refreshed over 20 samples from 08:50:00 to 08:52:30 CST. There were seven public endpoint errors, all on KuCoin books: `VANRY`, `ULTIMA`, or `SPX` timeouts and one `SPX` 502. Average REST RTT was 2,739 ms, max 8,150 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT remains 20/20 positive after the 80 VANRY withdrawal fee, avg +371.033 bps, median +357.132 bps, min +82.331 bps. Public-book cap remains 10,000 USDT for non-U.S. compliant setups.
- `A2-031` VANRY MEXC -> KuCoin USDT: 5,000 USDT was 18/18 valid positive after the 80 VANRY withdrawal fee, avg +388.312 bps, median +380.583 bps, min +160.503 bps. Public-book cap remains 5,000 USDT, but KuCoin endpoint reliability must be part of live thresholding.
- `A2-037` VANRY MEXC -> Binance USDC: 5,000 USDC degraded again to 19/20 positive after the 80 VANRY withdrawal fee, avg +806.221 bps, median +898.570 bps, min -232.492 bps. Firm measurement cap stays 2,500 USDC.
- `A2-023` ULTIMA MEXC -> KuCoin USDT: 5,000 USDT was 18/18 valid positive, avg +470.913 bps, median +469.285 bps, min +463.343 bps. 10,000 USDT was 18/18 valid positive, avg +243.884 bps, median +242.807 bps, min +238.556 bps. Keep cap at 5,000 USDT until chain/rebalance proof and a no-error 10,000 USDT window exist.
- `A2-132` SPX Bybit/MEXC -> KuCoin: Bybit -> KuCoin 5,000 USDT was 17/17 valid positive before Bybit transfer-fee haircut, avg +19.402 bps, min +10.671 bps. MEXC -> KuCoin 1,000 USDT after 3 SPX fee was 17/17 valid positive, avg +32.404 bps, min +25.278 bps; 2,500 USDT after fee had a thin +1.590 bps min. Keep SPX as `MEASURE`.

## Funding and Bitso Monitor Update - 2026-05-29 08:55 CST

- `A2-003` / `A2-019` spot-perp funding capture: refreshed with `scripts/funding_probe.py`. Scope was 47 public proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International; zero endpoint errors; elapsed 19.977 seconds.
- Best funding/basis proxies remained negative after entry basis and round-trip fees:
  - Coinbase INTX SOL USDC: -7.842 bps over 1h proxy.
  - Coinbase INTX BTC USDC: -9.243 bps over 1h proxy.
  - Coinbase INTX XRP USDC: -11.183 bps over 1h proxy.
  - Binance WLD USDT negative-funding route: -12.422 bps over 8h proxy.
- `A2-004` Bitso MXN/USD/stablecoin same-venue arbitrage: refreshed current public books. Best net results after conservative 50 bps per Bitso taker leg were PYUSD/MXN sell bid vs USD/MXN ask -51.857 bps, USD/MXN sell bid vs USDT/MXN ask -91.759 bps, RLUSD/MXN sell bid vs USD/MXN ask -104.881 bps, MXN -> USDT -> USD -> MXN -131.442 bps, and MXN -> USD -> USDT -> MXN -172.542 bps.
- Verdict: both remain `KILL` for immediate execution and `LATER` as monitors only.

## Candidate A2-133 - Binance.US Same-Venue Triangular Taker Scan

- approach type: same-venue triangular arbitrage, U.S.-available venue
- route/assets/exchanges: Binance.US 3-leg cycles starting in USD, USDT, or USDC
- quote lane: USD, USDT, USDC
- why edge might exist: same-venue triangles avoid cross-exchange transfer latency and Binance.US has a low public taker fee assumption from the earlier official fee check.
- public data quality: high for top-of-book. Scan used Binance.US `exchangeInfo` and `ticker/bookTicker`.
- fee assumptions: 2 bps taker per leg.
- estimated net bps: 261 tradable symbols produced 264 3-leg cycles. Best cycle was USDT -> USD -> USDC -> USDT at -6.710 bps after fees. Best ETH/USD/USDT bridge was -7.185 bps; best USD -> USDT -> BTC -> USD was -7.553 bps.
- executable notional estimate: none, because all cycles were negative before depth beyond top-of-book.
- frequency/duration evidence or proxy: one fresh public scan at 08:56 CST.
- implementation effort: low to keep as a monitor; not worth execution work.
- inventory/funding requirements: same-venue balances only, but no current positive taker cycle.
- risks: top-of-book quantities were small on some legs; maker/post-only could differ but requires queue/fill modeling.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` for immediate taker triangles. `LATER` only for maker/rebate/event-window variants.

## Candidate A2-134 - MEXC Same-Venue Triangular Taker Scan

- approach type: same-venue triangular arbitrage, non-U.S.-compliant account gated
- route/assets/exchanges: MEXC 3-leg cycles starting in USDT, USDC, BTC, or ETH
- quote lane: USDT, USDC, BTC, ETH
- why edge might exist: MEXC has low public taker fees and many long-tail cross-quote pairs; same-venue triangles avoid transfer latency.
- public data quality: high for top-of-book. Scan used MEXC `exchangeInfo` and `ticker/bookTicker`, preserving symbol-level taker commissions where exposed.
- fee assumptions: symbol-level MEXC taker commission from `exchangeInfo`, falling back to 5 bps when missing.
- estimated net bps: 2,323 tradable symbols produced 1,810 3-leg cycles. Three cycles were top-of-book positive: USDT -> USD1 -> AWF -> USDT at +26.767 bps, USDT -> EUR -> ADA -> USDT at +6.204 bps, and USDC -> EUR -> ADA -> USDC at +5.913 bps.
- executable notional estimate: none. The positive cycles were dust-constrained: AWF sell leg had only 0.01 AWF at top bid, and ADAEUR ask depth constrained the ADA/EUR cycles to roughly 0.006 EUR. The best non-dust stable/EUR loops were already negative.
- frequency/duration evidence or proxy: one fresh public scan at 08:57 CST.
- implementation effort: low to keep as a monitor; not worth execution work.
- inventory/funding requirements: same-venue balances only, but no actionable positive taker cycle.
- risks: MEXC account/region gate, dust top-of-book traps, symbol-level zero-fee promotions can create misleading headline bps, and actual executable depth is required before any triangle ranking.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` for immediate taker triangles. Keep same-venue triangles as a scanner feature only if dust/capacity gates are built in.

## Candidate A2-135 - KuCoin Same-Venue Triangular Taker Scan

- approach type: same-venue triangular arbitrage, non-U.S.-compliant account gated
- route/assets/exchanges: KuCoin 3-leg cycles starting in USDT, USDC, BTC, or ETH
- quote lane: USDT, USDC, BTC, ETH
- why edge might exist: KuCoin has many cross-quote pairs and same-venue triangles avoid transfer latency.
- public data quality: high for top-of-book. Scan used KuCoin `api/v2/symbols` and `api/v1/market/allTickers`.
- fee assumptions: 10 bps taker per leg.
- estimated net bps: 1,082 tradable symbols produced 982 3-leg cycles. Zero cycles were positive after fees. Best cycle was USDT -> VSYS -> BTC -> USDT at -6.389 bps. Best USDC/ETH/TEL cycle was -16.413 bps.
- executable notional estimate: none, because all cycles were negative before depth sizing.
- frequency/duration evidence or proxy: one fresh public scan at 08:58 CST.
- implementation effort: low to keep as a monitor; not worth execution work.
- inventory/funding requirements: same-venue balances only, but no current positive taker cycle.
- risks: KuCoin account/region gate, fee tier variability, and top-of-book quantities not included in this scan.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` for immediate taker triangles. `LATER` only for maker/rebate/event-window variants.

## Candidate A2-136 - Gate Same-Venue Triangular Taker Scan

- approach type: same-venue triangular arbitrage, non-U.S.-compliant account gated
- route/assets/exchanges: Gate 3-leg cycles starting in USDT, USDC, BTC, or ETH
- quote lane: USDT, USDC, BTC, ETH
- why edge might exist: Gate has many long-tail cross-quote pairs, and same-venue triangles avoid transfer latency and cross-exchange withdrawal risk.
- public data quality: high for current order-book depth. Scan used Gate `spot/currency_pairs`, `spot/tickers`, and `spot/order_book`.
- fee assumptions: corrected all-symbol scan converted Gate `fee` from percent to fraction, treating normal pairs as 20 bps taker and USDC/USDT as 10 bps. Follow-up depth used a conservative 20 bps per leg for all legs.
- estimated net bps: 2,206 tradable symbols produced 710 3-leg cycles. Ten cycles were positive at top-of-book, led by USDT -> ETH -> GALA -> USDT at +230.696 bps, USDC -> ETH -> GALA -> USDC at +213.410 bps, USDT -> LIKE -> ETH -> USDT at +22.791 bps, USDT -> XRD -> ETH -> USDT at +12.137 bps, and USDT -> USDC -> REZ -> USDT at +4.027 bps.
- executable notional estimate: none. Immediate order-book simulation turned every headline positive negative at the smallest tested bucket: GALA USDT -130.644 bps at 10 USDT, GALA USDC -160.048 bps at 10 USDC, LIKE -244.170 bps at 10 USDT, XRD -123.478 bps at 10 USDT, and REZ -134.798 bps at 10 USDT.
- frequency/duration evidence or proxy: one corrected all-symbol scan plus immediate executable-book depth check and a second 10-USDT spot recheck at 09:04 CST.
- implementation effort: low to keep as a monitor; medium if converted into a capacity-aware same-venue triangle scanner.
- inventory/funding requirements: same-venue Gate balances only, but no current executable taker cycle.
- risks: Gate account/region gate, fee-tier variability, top-of-book dislocations that vanish under executable book walking, and thin long-tail cross books.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` for immediate taker triangles. Keep Gate triangles only as a scanner feature with mandatory depth/capacity gating before ranking.

## Candidate A2-137 - Hyperliquid Same-Venue Spot/Perp Funding

- approach type: same-venue spot/perp funding capture
- route/assets/exchanges: Hyperliquid spot + Hyperliquid perps for common USDC-quoted pairs
- quote lane: USDC
- why edge might exist: same-venue carry avoids cross-exchange transfer latency and uses unified Hyperliquid spot/perp infrastructure; hourly funding could pay enough to overcome a favorable entry basis during dislocations.
- public data quality: high for public market data. Probe used official Hyperliquid `metaAndAssetCtxs`, `spotMetaAndAssetCtxs`, and `l2Book` endpoints.
- fee assumptions: official tier-0 fees of 7.0 bps spot taker and 4.5 bps perps taker, modeled on both entry and exit for 23.0 bps round-trip.
- estimated net bps: 19 raw common spot/perp candidates, 12 sane same-asset pairs after rejecting spot/perp mids more than 200 bps apart. Best one-hour proxy was ETH at -10.934 bps, followed by BTC -15.658 bps, SOL -16.395 bps, wrapped PUMP -18.746 bps, and HYPE -29.235 bps.
- executable notional estimate: no immediate positive notional. Best clean top-level notionals were about 1,809 USDC for ETH, 981 USDC for SOL, 1,333 USDC for HYPE, and only 84 USDC for BTC in the sampled book.
- frequency/duration evidence or proxy: one public scan at 09:08 CST. Current common-pair hourly funding was small, typically +0.125 bps/hour on the best positive-funding rows.
- implementation effort: low to keep as a monitor; medium for real execution because it needs maker/post-only logic, funding persistence windows, position sizing, margin risk, and exit basis modeling.
- inventory/funding requirements: USDC on Hyperliquid plus spot inventory and perp margin. Negative-funding rows would require shorting/selling spot inventory or borrowing spot, which is operationally harder.
- risks: stale/remapped spot symbols, hourly funding decay, basis reversal before exit, spot/perp book depth mismatch, account-specific fee tier, maker fill uncertainty, and Hyperliquid account/on-chain operational risk.
- confidence: high for killing immediate taker execution; medium for keeping maker/multi-hour carry as a monitor branch.
- verdict: `KILL` immediate taker funding capture. `LATER` for maker/post-only or multi-hour funding persistence only.

## Candidate A2-138 - HTX ULTIMA Expansion Route

- approach type: cross-exchange spot arbitrage, expansion venue
- route/assets/exchanges: buy ULTIMA/USDT on HTX, sell ULTIMA/USDT on KuCoin
- quote lane: USDT
- why edge might exist: HTX appears to have a materially lower ULTIMA ask than KuCoin while KuCoin has enough bid depth to absorb a 5,000 USDT public-book bucket.
- public data quality: medium-high for books and venue metadata. Used HTX `market/depth` and KuCoin `level2_100` for executable book walking, plus HTX/KuCoin public currency endpoints for transfer metadata.
- fee assumptions: HTX 20 bps taker buy fee and KuCoin 10 bps taker sell fee. Transfer fee not applied because the chain path is unresolved; HTX's public ULTIMA withdrawal fee is negligible at `0.00001` ULTIMA if the chain is usable.
- estimated net bps: in a 10-sample persistence check, 1,000 USDT was 10/10 positive avg +626.009 bps, 2,500 USDT was 10/10 positive avg +547.314 bps, and 5,000 USDT was 10/10 positive avg +398.199 bps before transfer and chain-friction costs.
- executable notional estimate: public-book measurement cap 5,000 USDT before transfer. 10,000 USDT did not have a valid full-depth bucket in the short persistence check.
- frequency/duration evidence or proxy: one integrated HTX expansion scan plus one 10-sample ULTIMA depth persistence check at 09:13-09:14 CST.
- implementation effort: low for scanner inclusion; high for execution because ULTIMA chain compatibility must be solved before repeatable transfer routing.
- inventory/funding requirements: USDT on HTX and ULTIMA sell inventory or deposit path into KuCoin. Direct transfer is not proven: HTX exposes `ULTIMA`/`ultima1` with no contract, while KuCoin exposes only BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
- risks: chain mismatch, bridge/rebalance risk, HTX/KuCoin regional eligibility, endpoint staleness, ULTIMA liquidity cliffs above 5,000 USDT, and one-way inventory imbalance if using pre-positioned inventory.
- confidence: high that the public price dislocation existed during the measured window; low for repeatable transfer execution until chain compatibility is proven.
- verdict: `LATER` / pre-positioned-or-bridge-only. Do not promote to `DO_NOW` execution unless HTX can withdraw to KuCoin's BEP20 ULTIMA path or a reliable bridge/rebalance path is proven.

## Candidate A2-139 - HTX Expansion Long-Tail Cluster

- approach type: cross-exchange spot arbitrage, expansion venue
- route/assets/exchanges: HTX-involved USDT routes across US, SWEAT, ONE, MTL, ICX, ZK, WALLI, CARV, CETUS, RONIN, ZEC, KAS and related top rows
- quote lane: USDT
- why edge might exist: HTX has stale or isolated long-tail prices that diverge from Binance, KuCoin, OKX, MEXC, Bitget, and Bybit.
- public data quality: medium. Top-of-book scan was broad, but route validity depends heavily on executable depth and public deposit/withdraw status.
- fee assumptions: HTX 20 bps taker, MEXC 5 bps taker, Binance/Bybit/OKX/KuCoin/Bitget/Gate 10 bps taker, plus 2 bps latency buffer.
- estimated net bps: many headline positives. Depth killed most at meaningful size; ZEC HTX -> OKX remained +106.560 bps at 10,000 USDT before transfer, but HTX ZEC withdrawals are prohibited.
- executable notional estimate: none for immediate repeatable transfer. Several pockets are positive only below 500-1,000 USDT; strong ZEC depth is operationally blocked.
- frequency/duration evidence or proxy: one integrated scan plus depth check across 15 HTX-involved liquid rows at 09:11-09:12 CST.
- implementation effort: low to keep HTX in discovery; medium for per-asset transfer-status mapping.
- inventory/funding requirements: varies by asset. ZEC requires HTX withdrawal, currently prohibited. SWEAT requires Bitget deposit, currently disabled. ONE/MTL/ICX/CARV/CETUS/RONIN require HTX withdrawals, currently prohibited in public metadata.
- risks: ticker collisions, transfer-disabled assets, chain mismatch, stale HTX books, shallow sell-side depth, and HTX account/region restrictions.
- confidence: high for killing immediate repeatable-transfer execution outside ULTIMA pre-positioned/bridge monitoring.
- verdict: `KILL` for immediate execution. Keep HTX in discovery because it surfaced a real ULTIMA dislocation and useful transfer-status edge cases.

## Candidate A2-140 - BitMart Expansion Scan

- approach type: cross-exchange spot arbitrage, expansion venue
- route/assets/exchanges: BitMart-involved USDT routes, mainly ULTIMA BitMart -> KuCoin, QAIT KuCoin/MEXC -> BitMart, and BTR BitMart -> Bitget
- quote lane: USDT
- why edge might exist: BitMart has broad long-tail coverage and can expose stale or isolated long-tail books that diverge from KuCoin, MEXC, and Bitget.
- public data quality: medium. BitMart ticker and depth endpoints were usable, but one metadata-backed attempt returned a transient 502 before a lighter parser succeeded.
- fee assumptions: conservative 25 bps BitMart taker, 5 bps MEXC taker, 10 bps KuCoin/Bitget taker, plus 2 bps latency buffer in top-of-book ranking.
- estimated net bps: top sane liquid rows were ULTIMA BitMart -> KuCoin +837.734 bps after fees/latency, QAIT KuCoin -> BitMart +336.347 bps, QAIT MEXC -> BitMart +270.081 bps, and BTR BitMart -> Bitget +225.009 bps.
- executable notional estimate: none for repeatable execution. ULTIMA was positive through 2,500 USDT but negative by 5,000 USDT and chain-blocked to KuCoin; QAIT turned negative by 1,000 USDT; BTR stayed positive through 1,000 USDT but had no 2,500 bucket and no compatible Bitget deposit path.
- frequency/duration evidence or proxy: one successful BitMart integrated scan plus immediate depth and transfer-metadata checks at 09:18-09:20 CST.
- implementation effort: low to keep as public discovery; medium to add robust symbol metadata, transfer-status mapping, and retry handling.
- inventory/funding requirements: BitMart and destination inventory. ULTIMA would need BEP20 delivery into KuCoin, but BitMart exposes SMART ULTIMA, not BEP20. BTR would need a compatible Bitget deposit path, currently absent.
- risks: ticker collisions, BitMart metadata reliability, chain mismatch, disabled deposits, shallow long-tail depth, and regional/account eligibility.
- confidence: high for killing immediate execution; medium for keeping BitMart as a discovery source.
- verdict: `KILL` immediate execution. Keep BitMart as discovery-only, mainly to monitor the ULTIMA chain-split premium.

## Live Refresh Update - 2026-05-29 09:25 CST

Top watch routes were refreshed over 12 public-book samples with six-second spacing. The run had one KuCoin `502 Bad Gateway` on ULTIMA MEXC -> KuCoin 10,000 USDT and poor public REST latency: avg 10,762 ms, max 19,123 ms.

- `A2-031` VANRY MEXC -> Binance USDT: 10,000 USDT after 80 VANRY withdrawal fee stayed 12/12 positive, avg +310.346 bps, median +312.777, min +289.750. Cap remains 10,000 USDT for non-U.S. compliant accounts.
- `A2-031` VANRY MEXC -> KuCoin USDT: 5,000 USDT after fee stayed 12/12 positive, avg +192.664 bps, median +188.456, min +153.914. Cap remains 5,000 USDT, with KuCoin staleness handling required.
- `A2-037` VANRY MEXC -> Binance USDC: 2,500 USDC after fee stayed 12/12 positive, avg +840.599 bps, min +653.161. The 5,000 USDC bucket was only 9/12 positive with min -207.212, so firm cap remains 2,500 USDC.
- `A2-023` ULTIMA MEXC -> KuCoin: 5,000 USDT stayed 12/12 positive before chain-transfer proof, avg +410.174 bps, min +318.532. 10,000 USDT was 10/11 valid positive with min -30.868 and one KuCoin 502, so 10,000 remains thin-watch only.
- `A2-138` ULTIMA HTX -> KuCoin: 5,000 USDT stayed 12/12 positive before chain-transfer proof, avg +392.967 bps, min +307.767. Still `LATER` / pre-positioned-or-bridge-only because of ULTIMA chain split.
- `A2-132` SPX Bybit/MEXC -> KuCoin: current route failed. Bybit -> KuCoin 5,000 was 0/12 positive avg -35.773 bps; MEXC -> KuCoin 1,000 after 3 SPX fee was 0/12 avg -38.325; 2,500 was 0/12 avg -44.030. Remove from active `MEASURE` until a fresh event-window sampler re-detects it.

## Candidate A2-141 - ULTIMA SMART-to-BEP20 Compatibility Check

- approach type: transfer-path validation for ULTIMA cross-exchange spot arbitrage
- route/assets/exchanges: ULTIMA buy venues on SMART/native representations (MEXC, Gate, HTX, BitMart) into KuCoin ULTIMA BEP20
- quote lane: USDT
- why edge might exist: KuCoin's BEP20 ULTIMA book is persistently priced far above SMART/native-cluster venues, creating strong public-book spreads if the asset can move between representations.
- public data quality: medium-high for exchange metadata and official listing docs; low for actual bridge execution because no official bridge cost/time proof was found.
- fee assumptions: venue taker fees as modeled in route refreshes; transfer/bridge fee not modeled because the required path is unverified.
- estimated net bps: ULTIMA MEXC -> KuCoin 5,000 was +410.174 bps avg in the 09:25 refresh before chain-transfer costs; ULTIMA HTX -> KuCoin 5,000 was +392.967 bps avg before chain-transfer costs; BitMart -> KuCoin was positive through 2,500 but negative by 5,000.
- executable notional estimate: zero for repeatable direct transfer until chain compatibility is proven. Pre-positioned inventory can monetize a one-way imbalance, but not a repeatable route.
- frequency/duration evidence or proxy: multiple route refreshes and expansion scans show the KuCoin BEP20 premium persists, but source checks show the path is representation-split.
- implementation effort: high for execution because it requires logged-in withdrawal-path proof or an official bridge with measurable cost/time.
- inventory/funding requirements: ULTIMA sell inventory on KuCoin or a verified BEP20 deposit path. Without that, trades strand ULTIMA on SMART/native venues and USDT on KuCoin.
- risks: chain mismatch, bridge custody/smart-contract risk, transfer latency, KuCoin-only premium collapse, withdrawal suspensions, and one-way inventory imbalance.
- confidence: high that direct SMART/native-to-KuCoin BEP20 transfer is not publicly proven; medium that a private/logged-in venue path could still exist but must be verified manually.
- verdict: `KILL` for direct repeatable transfer today; `LATER` for pre-positioned inventory or verified bridge/BEP20 withdrawal path.

## Candidate A2-142 - Expanded Event-Window GUA and HTX Survivors

- approach type: cross-exchange spot arbitrage, event-window discovery
- route/assets/exchanges: strongest survivor was GUA/USDT MEXC -> Gate; secondary survivor was ORDI/USDT HTX -> Bitget/Bybit; weaker HTX rows included GOMINING, STRK, RACA, TST, BLAST, STETH, NEXO, and AWE.
- quote lane: USDT
- why edge might exist: short-lived venue fragmentation on long-tail books; HTX and Gate can show isolated asks/bids that diverge from MEXC, Bitget, Bybit, Binance, KuCoin, and BitMart.
- public data quality: medium-high for order-book depth and Gate/HTX/Bitget public transfer metadata. MEXC GUA metadata was not publicly readable from this environment because the unauthenticated MEXC web endpoint returned `Access Denied`; Bybit ORDI asset metadata required an API key.
- fee assumptions: MEXC 5 bps taker, Gate/Binance/Bybit/Bitget/KuCoin 10 bps taker, HTX 20 bps taker, BitMart 25 bps taker. Transfer fees were checked after depth rather than included in the first depth table.
- estimated net bps: GUA MEXC -> Gate was +780.754 bps at 50 USDT, +604.611 at 500, +500.314 at 1,000, +209.824 at 2,500, and -29.459 at 5,000 before transfer. ORDI HTX -> Bybit was +140.902 bps at 1,000 and -35.586 at 2,500 before transfer; ORDI HTX -> Bitget was +143.342 at 1,000 and -31.037 at 2,500.
- executable notional estimate: zero for repeatable transfer today. GUA has public-book capacity through 2,500 USDT only if Gate sell inventory is already pre-positioned; Gate public metadata has GUA deposits disabled. ORDI has no positive executable bucket after HTX's `5.004459` ORDI withdrawal fee.
- frequency/duration evidence or proxy: the expanded top-of-book sampler found GUA and the HTX cluster persistent across 6/6 samples. The follow-up depth pass at 09:31-09:38 CST showed only GUA surviving through 2,500 USDT before transfer, while ORDI survived only through 1,000 USDT before transfer and was killed by withdrawal fee.
- implementation effort: low to keep GUA in the pre-positioned watchlist; medium to add automatic deposit-disabled/pre-positioned tagging to the event-window scanner.
- inventory/funding requirements: GUA requires sell inventory already on Gate plus USDT on MEXC; without Gate deposits, repeated cycles strand GUA on MEXC and USDT on Gate. ORDI would require accepting a large HTX BRC20 withdrawal fee, which is not supported by the measured edge.
- risks: Gate deposit-disabled status, pre-positioned one-way inventory depletion, long-tail book cliffs above 2,500 USDT, stale event-window spreads, HTX withdrawal fee drag, Bybit public metadata gate, and regional/account restrictions.
- confidence: high for killing repeatable GUA/ORDI transfer execution from public evidence; medium for keeping GUA as a pre-positioned-only watch because the depth was strong in this snapshot but not yet persisted beyond the six-sample window.
- verdict: `KILL` for repeatable transfer execution. `LATER` for GUA pre-positioned inventory only, capped at 2,500 USDT until Gate deposits reopen and a fresh persistence pass remains positive.

## Candidate A2-143 - Liquid Static Gate-Buy Refresh

- approach type: cross-exchange spot arbitrage, liquid static refresh
- route/assets/exchanges: XLM/USDT Gate -> Bybit/MEXC/KuCoin/Bitget and INJ/USDT Gate -> MEXC/Bybit
- quote lane: USDT
- why edge might exist: Gate showed slightly cheaper XLM and INJ asks than other liquid USDT venues in the fresh public market probe, with enough 24h volume to avoid obvious dust traps.
- public data quality: high for public top-of-book and immediate depth. Used `scripts/market_probe.py` across 10,204 markets, then direct public order-book depth from Gate, Bybit, MEXC, KuCoin, and Bitget.
- fee assumptions: Gate 10 bps taker, Bybit/KuCoin/Bitget 10 bps taker, MEXC 5 bps taker. No transfer fee applied because the route failed before transfer/rebalance costs.
- estimated net bps: top-of-book probe showed only small positives: XLM Gate -> Bybit +6.559 bps, INJ Gate -> MEXC +3.952 bps, XLM Gate -> MEXC +2.196 bps, and XLM Gate -> KuCoin/Bitget +1.878 bps after fees/latency.
- executable notional estimate: none. Depth check was negative at every tested bucket from 1,000 to 25,000 USDT. Best row was INJ Gate -> Bybit at -31.541 bps for 1,000 USDT; XLM Gate -> Bybit was -48.359 bps for 1,000 USDT.
- frequency/duration evidence or proxy: one fresh 09:41-09:42 CST market probe plus immediate depth check. No persistence run was needed because the first executable-depth pass was already negative at the smallest tested bucket.
- implementation effort: low to keep as a regression gate; no execution work justified.
- inventory/funding requirements: would require USDT on Gate and XLM/INJ sell inventory on destination venues for inventory-based arbitrage, or transfer/rebalance after execution. The edge is negative before either operational path matters.
- risks: tiny top-of-book spreads, Gate book cliffs, endpoint timing skew, and transfer/rebalance costs larger than the entire headline edge.
- confidence: high for killing immediate static taker execution.
- verdict: `KILL`. Liquid static top-of-book positives below roughly 10 bps should not be ranked without immediate book-walk confirmation.

## Candidate A2-144 - CoinEx Expansion Venue Scan

- approach type: new exchange expansion, cross-exchange spot arbitrage
- route/assets/exchanges: CoinEx USDT/USDC/USD/EUR spot markets versus Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, and Bitfinex
- quote lane: USDT, USDC, USD, EUR
- why edge might exist: CoinEx has broad long-tail spot coverage and per-market public fee metadata; adding another venue could surface fragmented books missed by the existing scanner set.
- public data quality: medium-high for static discovery. CoinEx public `v2/spot/market` exposed online market metadata and taker fees; `v1/market/ticker/all` exposed bid/ask. No depth check was needed because no sane positive top-of-book routes survived fees.
- fee assumptions: CoinEx per-market taker rates from public metadata, typically 20-30 bps; existing venue assumptions from Agent 2 scans.
- estimated net bps: zero positive sane routes after filters. Near misses were already negative after fees/latency: BABYDOGE OKX -> CoinEx -6.160 bps, NEAR MEXC -> CoinEx -7.716, BCH MEXC -> CoinEx -11.314, TON MEXC -> CoinEx -14.086, and PEPE CoinEx -> KuCoin/Bitget -15.920.
- executable notional estimate: none. The scan filtered for 100,000+ quote-volume depth proxy and gross spread <=1,000 bps; no route had positive net before actual order-book walking.
- frequency/duration evidence or proxy: one fresh 09:43-09:45 CST expansion scan over 11,202 total markets including 1,080 CoinEx markets, with zero endpoint errors.
- implementation effort: low to add as a discovery adapter; not justified for execution work until the top-of-book scan shows persistent positive net after CoinEx's fee tier.
- inventory/funding requirements: CoinEx inventory plus destination inventory for any future inventory-based route. No current route justifies funding.
- risks: high public taker fees versus other venues, long-tail ticker collisions, volume inflation, account/region gating, and lack of demonstrated depth-positive edge.
- confidence: high for killing immediate static taker execution; medium for keeping CoinEx as a low-priority discovery venue.
- verdict: `KILL` for current execution. `LATER` only as a scanner expansion source with strict fee-first filtering.

## Candidate A2-145 - Spot/Perp Funding Refresh

- approach type: spot/perp basis and funding capture
- route/assets/exchanges: Binance, Bybit, OKX, and Coinbase International Exchange spot/perp proxies across BTC, ETH, DOGE, SOL, XRP, WLD, TRX, LINK, BCH, AVAX, ADA, SUI, LTC, ARB, and related configured assets
- quote lane: USDT and USDC
- why edge might exist: scheduled funding can temporarily exceed spot/perp entry basis and taker round-trip fees, especially around negative-funding dislocations or one-hour Coinbase INTX funding windows.
- public data quality: medium. Binance, Bybit, and Coinbase INTX returned public data; OKX returned one `502 Bad Gateway`, so OKX is inconclusive for this refresh.
- fee assumptions: script assumptions: Binance spot 10 bps/perp 5 bps, Bybit spot 10/perp 5.5, OKX spot 10/perp 5, Coinbase INTX spot 2/perp 4. Round trip modeled as `2 * (spot_taker + perp_taker)`.
- estimated net bps: no positive proxy. Best rows were Coinbase INTX DOGE -7.896 bps over one hour, Coinbase INTX BTC -10.628, Coinbase INTX XRP -11.183, Bybit WLD negative-funding route -13.020 over 8h, Coinbase INTX ETH -14.936, and Binance WLD -15.320.
- executable notional estimate: none because every proxy was negative before depth, borrow, margin, and exit-basis risk.
- frequency/duration evidence or proxy: fresh 09:46 CST run produced 14 Binance routes, 14 Bybit routes, 5 Coinbase INTX routes, and 0 OKX routes due to one 502 error.
- implementation effort: low to keep scheduled monitor; medium for execution because it needs account fee tier, margin, borrow/shorting ability for negative-funding routes, exit basis, and liquidation-risk controls.
- inventory/funding requirements: USDT/USDC spot inventory plus perp margin for positive-funding long spot/short perp routes; borrowable or pre-owned spot inventory for negative-funding long perp/short spot routes.
- risks: funding decay before execution, basis reversal, borrow unavailability, taker fee drag, account-level fee differences, margin/liquidation risk, and endpoint errors.
- confidence: high for killing immediate taker funding capture from the venues that returned data; low for OKX because this refresh hit a 502.
- verdict: `KILL` immediate taker carry. Keep `LATER` scheduled funding monitor; retry OKX on the next funding loop.

## Candidate A2-146 - Bitso MXN Stable/BTC Basis Refresh

- approach type: MXN fiat/stablecoin basis and BTC implied FX basis
- route/assets/exchanges: Bitso `usd_mxn`, `usdt_mxn`, `pyusd_mxn`, `btc_mxn`, and `btc_usd`
- quote lane: MXN and USD
- why edge might exist: Bitso's local MXN order books can diverge from USD/stablecoin books, creating local FX or BTC/MXN implied-basis opportunities if the spread exceeds Bitso fees.
- public data quality: high for public Bitso tickers; medium for execution because actual account fee tier, fiat rails, and inventory settlement are not modeled.
- fee assumptions: conservative 50 bps per Bitso leg. Stable-vs-USD comparisons used two legs; BTC/MXN implied comparison used three legs.
- estimated net bps: no positive route. Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -64.852 bps net. USDT/MXN buy ask vs USD/MXN bid was -91.925 bps; USDT/MXN sell bid vs USD/MXN ask was -114.405. BTC/MXN implied USD comparisons were -156.047 and -173.774 bps after three fees.
- executable notional estimate: none because every proxy is negative before order-book walking and settlement/fiat friction.
- frequency/duration evidence or proxy: one 09:48 CST refresh. Relevant public tickers: USD/MXN bid/ask 17.351/17.355, USDT/MXN 17.330/17.337, PYUSD/MXN 17.416/17.452, BTC/MXN 1,278,290/1,281,190, BTC/USD 73,664/73,700.
- implementation effort: low to keep monitoring; medium if adding actual order-book depth, fee-tier, and fiat settlement modeling.
- inventory/funding requirements: MXN, USD/stablecoin, and/or BTC balances on Bitso; no cross-exchange transfer needed for same-venue basis, but fiat settlement and internal inventory are required.
- risks: Bitso fee tier variance, fiat rail latency, stablecoin liquidity, ticker-only depth overstatement, MXN funding constraints, and tax/accounting overhead.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` current MXN/stable/BTC basis. Keep `LATER` monitor; only promote if gross dislocation exceeds fees by a wide margin before depth.

## Candidate A2-147 - Active Watch Route Refresh

- approach type: cross-exchange spot arbitrage watchlist refresh
- route/assets/exchanges: VANRY MEXC -> Binance/KuCoin, VANRY USDC MEXC -> Binance, ULTIMA MEXC/HTX -> KuCoin, and GUA MEXC -> Gate
- quote lane: USDT and USDC
- why edge might exist: these are the only current routes with repeated prior public-book edge or pre-positioned-inventory potential after the broad discovery and venue-expansion passes.
- public data quality: high for current order-book depth from public REST. HTX `depth=150` failed in the first watch script, but a follow-up valid `depth=20` check confirmed current ULTIMA HTX -> KuCoin collapses by 1,000 USDT.
- fee assumptions: MEXC 5 bps, Binance/KuCoin/Gate 10 bps, HTX 20 bps. VANRY includes the 80 VANRY MEXC withdrawal fee. ULTIMA and GUA figures exclude transfer fees because ULTIMA chain compatibility is unresolved and GUA is pre-positioned-only while Gate deposits are disabled.
- estimated net bps: VANRY MEXC -> Binance USDT 10,000 stayed 8/8 positive avg +275.623 bps, min +79.560. VANRY MEXC -> KuCoin USDT 2,500 stayed 8/8 positive avg +584.783, min +154.962, but 5,000 was only 7/8 positive with min -130.747. VANRY MEXC -> Binance USDC 2,500 stayed 8/8 positive avg +911.620, min +590.155, but 5,000 was 7/8 with min -253.295. GUA 2,500 pre-positioned-only stayed 8/8 positive avg +254.447, min +208.167. ULTIMA was positive only through 500 USDT in a follow-up small-bucket check and negative at 1,000+.
- executable notional estimate: VANRY Binance USDT cap remains 10,000 USDT; VANRY KuCoin cap drops to 2,500 USDT; VANRY Binance USDC remains 2,500 USDC; GUA remains 2,500 USDT pre-positioned-only; ULTIMA active 5,000/10,000 cap is killed.
- frequency/duration evidence or proxy: eight samples with six-second spacing at 09:52-09:54 CST, plus immediate ULTIMA small-bucket follow-up. Public REST RTT averaged 472.8 ms with max 1,125.0 ms.
- implementation effort: low for scanner/watchlist updates; high for execution because account/region, live withdrawal status, inventory, and chain compatibility still gate the top routes.
- inventory/funding requirements: VANRY requires USDT/USDC on MEXC and sell inventory or transfer/rebalance to Binance/KuCoin; GUA requires Gate sell inventory already pre-positioned; ULTIMA would require verified KuCoin BEP20 delivery or pre-positioned KuCoin inventory.
- risks: account/region restrictions, MEXC withdrawal status not publicly proven live, KuCoin book cliffs, VANRY negative tails at larger buckets, GUA Gate deposit-disabled status, and ULTIMA chain/depth collapse.
- confidence: high for current cap changes; medium for execution readiness because operational account checks remain unresolved.
- verdict: `DO_NOW` monitor VANRY Binance 10,000 USDT and VANRY KuCoin 2,500 USDT for non-U.S.-compliant setups; `MEASURE` VANRY Binance USDC 2,500; `LATER` GUA pre-positioned-only 2,500; `KILL_CURRENT` ULTIMA 5,000/10,000.

## Candidate A2-148 - OKX Funding Retry

- approach type: spot/perp basis and funding capture
- route/assets/exchanges: Binance, Bybit, OKX, and Coinbase International Exchange spot/perp proxies
- quote lane: USDT and USDC
- why edge might exist: the 09:46 funding refresh had an OKX `502 Bad Gateway`, so the funding branch needed a clean retry before dismissing OKX.
- public data quality: high for this retry. Binance, Bybit, OKX, and Coinbase INTX all returned public data with zero endpoint errors.
- fee assumptions: same as `scripts/funding_probe.py`: Binance spot 10 bps/perp 5 bps, Bybit spot 10/perp 5.5, OKX spot 10/perp 5, Coinbase INTX spot 2/perp 4. Round trip is `2 * (spot_taker + perp_taker)`.
- estimated net bps: no positive proxy. Best rows were Coinbase INTX XRP -7.391 bps, Coinbase INTX BTC -9.247, Coinbase INTX SOL -9.705, Coinbase INTX ETH -10.006, OKX WLD -10.614, Coinbase INTX DOGE -11.880, Binance WLD -12.038, and Bybit WLD -16.121.
- executable notional estimate: none because every proxy is negative before depth, borrow/margin, and exit-basis modeling.
- frequency/duration evidence or proxy: one clean 09:57 CST retry: Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, zero errors.
- implementation effort: low to keep scheduled monitor; no execution work justified.
- inventory/funding requirements: same as other spot/perp candidates: spot inventory or quote balance plus perp margin; negative-funding rows need borrowable or pre-owned spot to short.
- risks: funding decay, basis reversal, borrow unavailability, margin/liquidation risk, and account-level fees.
- confidence: high for killing immediate taker funding capture across the returned venues.
- verdict: `KILL` immediate taker carry. Keep scheduled monitor only.

## Candidate A2-149 - Fresh Event-Window ATLA Micro Survivor

- approach type: cross-exchange spot arbitrage, event-window discovery
- route/assets/exchanges: ATLA/USDT MEXC -> BitMart
- quote lane: USDT
- why edge might exist: the fresh exclusion sampler surfaced a small persistent MEXC-vs-BitMart bid/ask dislocation after excluding the current watchlist and most recently killed bases.
- public data quality: medium-high for current books and BitMart deposit metadata. MEXC public trading metadata confirms ATLA spot trading is allowed, and MEXC's official initial-listing article said ATLA deposits were opened with withdrawals scheduled for 2025-08-18 08:00 UTC: `https://www.mexc.com/en-GB/support/articles/17827791529014`. MEXC public coin/fee pages returned `Access Denied`, so current withdrawal status and fee are still not proven.
- fee assumptions: MEXC 5 bps taker and BitMart 25 bps taker. Transfer fee not applied because MEXC withdrawal fee/status is unknown from public data.
- estimated net bps: one depth retry showed +122.885 bps at 50 USDT, +121.883 at 100, +117.920 at 250, +92.750 at 500, +51.331 at 1,000, and -68.297 at 2,500 before transfer. Six-sample persistence then showed 500 USDT 6/6 positive avg +54.386 bps, median +53.719, min +44.291; 1,000 USDT only 5/6 positive with min -3.222; 2,500 was 0/6 positive.
- executable notional estimate: 500 USDT measurement cap before transfer. Do not promote 1,000 because it already printed a negative tail before transfer costs.
- frequency/duration evidence or proxy: four-sample top-of-book event-window hit plus a six-sample depth persistence check at 09:59-10:04 CST. Persistence RTT avg 819.1 ms, max 3,231.0 ms.
- implementation effort: low to keep on scanner watch; medium for execution because MEXC withdrawal status/fee and native ATLA chain compatibility must be verified.
- inventory/funding requirements: USDT on MEXC and ATLA sell inventory or deposit path into BitMart. BitMart public metadata exposes `ATLA-ATLA` deposits/withdrawals enabled on native `ATLA`, withdrawal fee `0.01`; MEXC exchange metadata has empty contract address and spot trading allowed, and official historical listing text supports ATLA deposit/withdraw rollout, but current public withdrawal-fee/status metadata was blocked.
- risks: MEXC withdrawal status unknown, MEXC access denied on fee/status endpoint, BitMart liquidity cap below 1,000 USDT, 1,000 USDT negative tail, BitMart account/region risk, and transfer latency.
- confidence: medium for a real 500 USDT public-book pocket; low for repeatable execution until MEXC withdrawal fee/status is proven.
- verdict: `MEASURE` at 500 USDT only. `KILL` 1,000+ and do not spend execution work before MEXC withdrawal status/fee is verified.

## Candidate A2-150 - U.S.-Available Core Venue Refresh

- approach type: U.S.-available cross-exchange spot arbitrage
- route/assets/exchanges: core USD/USDT/USDC assets across Binance.US, Coinbase, Kraken, Gemini, and Bitstamp
- quote lane: USD, USDT, USDC
- why edge might exist: current top routes are gated by MEXC/KuCoin/Binance-global account restrictions; a U.S.-available substitute would be much more actionable if it survived fees and depth.
- public data quality: medium-high. Bounded scan used public top-of-book tickers for 110 core markets, then direct public depth for the only positive top-of-book candidate.
- fee assumptions: Binance.US 2 bps taker, Kraken 40 bps, Bitstamp 40 bps, Coinbase/Gemini 120 bps, plus 4 bps USD latency/staleness buffer in top-of-book ranking. Depth check used venue taker fees but not transfer/rebalance costs.
- estimated net bps: top-of-book scan found two positive after-fee rows: XLM/USD Kraken -> Binance.US +21.089 bps and XLM/USD Bitstamp -> Binance.US +19.488 bps. Depth killed both: Kraken -> Binance.US was -124.181 bps at 100 USD and -126.155 at 1,000; Bitstamp -> Binance.US was -124.981 bps at 100 and -128.270 at 1,000.
- executable notional estimate: none. Both XLM routes were negative from the smallest tested 100 USD bucket.
- frequency/duration evidence or proxy: one 10:15-10:19 CST bounded U.S.-venue refresh plus immediate depth check.
- implementation effort: low to keep as scheduled compliance-friendly monitor; no execution work justified.
- inventory/funding requirements: USD on Kraken/Bitstamp and XLM inventory or transfer path to Binance.US for the measured direction, but depth is negative before inventory matters.
- risks: top-of-book timing skew, high fee drag on U.S. venues, Binance.US book cliff, lower venue coverage, and limited asset availability.
- confidence: high for killing current U.S.-available taker execution.
- verdict: `KILL` current U.S.-available core taker routes. Keep U.S.-venue scan as a periodic fallback monitor only.

## Candidate A2-151 - Strict New-Name Event-Window Refresh

- approach type: cross-exchange spot arbitrage, fresh-basis event-window discovery
- route/assets/exchanges: broad public venue pass, then corrected non-HTX/new-base pass; main depth-tested rows were ARRR Gate -> MEXC, CELL/WEXO BitMart -> MEXC, WPAY BitMart -> Gate, OWL BitMart -> MEXC, MAGA/NAKA MEXC/KuCoin -> BitMart, ESE KuCoin -> Bybit, CHIRP MEXC -> KuCoin, and BEAT/ID/TBK/ORAI rows.
- quote lane: USDT and USDC
- why edge might exist: after excluding the current watchlist and recent traps, BitMart and smaller Gate/MEXC books can show short-lived dislocations that broad static scans miss.
- public data quality: high for books and pair fees used in the kill. First pass had a BitMart ticker parser bug and intentionally served as a regression check; the corrected pass parsed 11,231 markets with zero endpoint errors.
- fee assumptions: venue taker fees by route, with Gate pair fee corrected to `0.2%` = 20 bps for ARRR/WPAY/CELL instead of the generic 10 bps assumption. Transfer fees were not used to rescue any route because book depth already killed actionable size.
- estimated net bps: corrected depth killed all meaningful sizes. ARRR Gate -> MEXC had one promising book walk through 500 USDT, but six-sample persistence after the corrected Gate fee showed only 100 USDT 6/6 positive avg +120.727 bps, while 250 was 1/6 positive avg -14.114 and 500/1,000 were 0/6 positive. CELL/WEXO were positive only through 100, WPAY through 500 but only +16.940 bps before transfer, and OWL/MAGA/NAKA/ORAI/TBK/BEAT/ID failed from 50-250 or worse.
- executable notional estimate: none. ARRR's only persistent positive bucket was 100 USDT, below actionable size after transfer and operational overhead.
- frequency/duration evidence or proxy: three-sample first pass across 11,820 markets, two-sample corrected pass across 11,231 markets, then six ARRR depth-persistence samples with RTT avg 1,497.8 ms and max 1,880.8 ms.
- implementation effort: low to add as scanner regression gates; no execution implementation justified.
- inventory/funding requirements: would require quote inventory on the buy venue and sell/deposit path on the destination. ARRR public metadata looked operationally plausible on native ARRR, but depth persistence failed above dust size.
- risks: stale top-of-book rows, old killed bases reappearing when exclusion sets drift, wrong generic fee assumptions on Gate, BitMart parser/schema variance, thin destination books, and transfer-fee drag on micro buckets.
- confidence: high for killing current execution; medium-high that the scanner needs a persisted killed-base and venue-pair-fee gate.
- verdict: `KILL` current new-name refresh. Add ARRR/CELL/WEXO/WPAY/OWL/MAGA/NAKA/ESE/CHIRP/TBK/BEAT/ID to processed-base exclusions unless they reappear with positive 1,000+ USDT depth after exact venue fees.

## Candidate A2-152 - Active Watch Route Refresh

- approach type: cross-exchange spot arbitrage watchlist refresh
- route/assets/exchanges: VANRY MEXC -> Binance/KuCoin, VANRY USDC MEXC -> Binance, GUA MEXC -> Gate pre-positioned, ATLA MEXC -> BitMart, and ULTIMA MEXC -> KuCoin recovery check.
- quote lane: USDT and USDC
- why edge might exist: the active watchlist has shown repeated fragmentation pockets, but caps have moved quickly with destination book depth; a fresh refresh determines which caps are still live.
- public data quality: high for public order-book depth. Eight samples completed with zero endpoint errors, though REST RTT was slow: avg 4,938.9 ms and max 6,073.4 ms.
- fee assumptions: MEXC 5 bps, Binance/KuCoin 10 bps, BitMart 25 bps, Gate exact pair fee 20 bps for GUA, and 2 bps USDT/USDC latency buffer. VANRY includes the 80 VANRY MEXC withdrawal haircut. GUA/ATLA/ULTIMA figures are before transfer where the route is pre-positioned-only or transfer proof is missing.
- estimated net bps: VANRY Binance USDT 10,000 was 8/8 positive avg +270.132 bps, min +106.909. VANRY KuCoin 5,000 recovered to 8/8 positive avg +238.039, min +76.284. VANRY Binance USDC 5,000 recovered to 8/8 positive avg +595.583, min +197.250. GUA 2,500 pre-positioned-only was 8/8 positive avg +354.473, min +244.780, but 5,000 was only 6/8 with min -50.063. ATLA 500 was 0/8 positive avg -170.470. ULTIMA MEXC -> KuCoin 2,500 was 8/8 positive avg +448.475 before chain proof.
- executable notional estimate: VANRY Binance USDT 10,000, VANRY KuCoin USDT 5,000, VANRY Binance USDC 5,000 as current public-book caps for non-U.S.-compliant account setups. GUA remains 2,500 pre-positioned-only. ULTIMA is 2,500 depth-positive but not repeatable-transfer-ready. ATLA has no current executable cap.
- frequency/duration evidence or proxy: eight samples at 10:34-10:36 CST with six-second spacing.
- implementation effort: low for scanner/watchlist updates; high for execution because account/region, live withdrawal status, and chain proof still gate the top routes.
- inventory/funding requirements: VANRY needs USDT/USDC on MEXC and sell venue inventory or transfer/rebalance path. GUA needs existing Gate inventory while Gate deposits remain disabled. ULTIMA needs KuCoin BEP20 delivery proof or pre-positioned KuCoin inventory. ATLA should not receive inventory work while current books are negative.
- risks: non-U.S. account restriction, MEXC withdrawal status not publicly proven live, slow public REST RTT, VANRY prior negative tails at 5,000 buckets, GUA deposit-disabled status, and ULTIMA chain split.
- confidence: high for current public-book cap changes; medium for execution readiness because operational account checks remain unresolved.
- verdict: `DO_NOW` monitor VANRY Binance 10,000 USDT and restore VANRY KuCoin 5,000 USDT for non-U.S.-compliant setups; `MEASURE` VANRY Binance USDC at 5,000 USDC; `LATER` GUA 2,500 pre-positioned-only; `LATER` ULTIMA 2,500 chain-proof-only; `KILL_CURRENT` ATLA.

## Candidate A2-153 - 10:39 Funding Refresh

- approach type: spot/perp basis and funding capture
- route/assets/exchanges: Binance, Bybit, OKX, and Coinbase International Exchange public spot/perp proxies
- quote lane: USDT and USDC
- why edge might exist: funding and spot/perp basis can move faster than static spot spreads, so scheduled refreshes can catch temporary positive carry windows.
- public data quality: high for this refresh. All four venue fetchers returned data with zero endpoint errors.
- fee assumptions: same as `scripts/funding_probe.py`: Binance spot 10 bps/perp 5 bps, Bybit spot 10/perp 5.5, OKX spot 10/perp 5, Coinbase INTX spot 2/perp 4. Round trip is `2 * (spot_taker + perp_taker)`.
- estimated net bps: no positive proxy. Best rows were Coinbase INTX BTC -9.942 bps, Coinbase INTX SOL -10.943, Coinbase INTX ETH -11.556, Coinbase INTX XRP -12.695, Coinbase INTX DOGE -12.874, Bybit WLD -15.894, OKX WLD -16.737, Bybit TRX -17.936, Binance TRX -18.123, OKX TRX -18.357, and Binance WLD -18.960.
- executable notional estimate: none because every proxy is negative before borrow, margin, exit-basis, and liquidation modeling.
- frequency/duration evidence or proxy: one clean 10:39 CST refresh: Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, zero errors, elapsed 20.469 seconds.
- implementation effort: low to keep scheduled monitor; no execution work justified.
- inventory/funding requirements: spot inventory or quote balance plus perp margin for positive-funding rows; borrowable or pre-owned spot for negative-funding rows.
- risks: funding decay, basis reversal, borrow unavailability, margin/liquidation risk, account-level fees, and exit slippage.
- confidence: high for killing immediate taker funding capture in this window.
- verdict: `KILL` immediate taker carry. Keep scheduled monitor only.

## Candidate A2-154 - 10:40 Bitso MXN Refresh

- approach type: same-venue fiat/stable/crypto basis
- route/assets/exchanges: Bitso USD/MXN, USDT/MXN, PYUSD/MXN, BTC/USD, BTC/MXN, ETH/USD, ETH/MXN, XRP/USD, and XRP/MXN
- quote lane: MXN and USD
- why edge might exist: Bitso's local MXN books can diverge from USD and stablecoin books enough to create local FX or implied crypto/MXN basis opportunities if the spread exceeds Bitso fees.
- public data quality: high for public Bitso tickers; medium for execution because actual account fee tier, order-book depth, fiat settlement, and inventory availability are not modeled.
- fee assumptions: conservative 50 bps per Bitso leg. Stable-vs-USD comparisons used two legs; crypto implied MXN comparisons used three legs.
- estimated net bps: no positive route. Best was PYUSD/MXN sell bid vs USD/MXN buy ask at -63.085 bps net. USDT/MXN buy ask vs USD/MXN sell bid was -92.495 bps; USDT/MXN sell bid vs USD/MXN buy ask was -110.382. Crypto implied routes ranged from XRP/MXN -153.531 bps to BTC/MXN -188.625 bps net.
- executable notional estimate: none because every proxy is negative before order-book walking and settlement friction.
- frequency/duration evidence or proxy: one 10:40 CST public ticker refresh with zero endpoint errors.
- implementation effort: low to keep monitoring; medium if adding order-book depth, fee-tier, and fiat settlement modeling.
- inventory/funding requirements: MXN, USD/stablecoin, and/or BTC/ETH/XRP balances on Bitso; no cross-exchange transfer needed for same-venue basis.
- risks: Bitso fee tier variance, fiat rail latency, ticker-only depth overstatement, MXN funding constraints, stablecoin liquidity, and accounting overhead.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` current MXN/stable/crypto basis. Keep scheduled monitor only.

## Candidate A2-155 - BingX/LBank Expansion And ESPORTS Survivor

- approach type: new-exchange expansion, cross-exchange spot arbitrage
- route/assets/exchanges: BingX and LBank public spot expansion; surviving route is ESPORTS/USDT LBank -> MEXC.
- quote lane: USDT
- why edge might exist: LBank and BingX list long-tail assets with fragmented liquidity and less scanner coverage. LBank's book can be materially below MEXC/BingX on event-style tokens.
- public data quality: medium for execution. BingX ticker/depth APIs exposed bid/ask and books. LBank ticker lacks bid/ask, so all LBank positives were validated with direct order-book depth. LBank public withdrawal config shows ESPORTS BEP20 withdrawals enabled with fee `4.6915`, while MEXC public metadata shows ESPORTS/Yooldo Games on BSC with deposit fee 0; LBank did not expose the contract address in the checked withdrawal config. However, official LBank notice `https://www.lbank.com/fa/support/articles/2058904083074383872` says ESPORTS deposits/withdrawals were suspended at 2026-05-25 13:20 UTC, creating a public-status conflict that requires logged-in verification.
- fee assumptions: conservative LBank 20 bps, MEXC 5 bps, and 2 bps latency. ESPORTS persistence included the LBank `4.6915` ESPORTS BEP20 withdrawal fee.
- estimated net bps: ESPORTS LBank -> MEXC persistence: 1,000 USDT 6/6 positive avg +305.079 bps, min +165.465; 2,500 USDT 6/6 positive avg +177.340, min +41.913; 5,000 USDT only 4/6 positive avg -25.452, min -205.489; 10,000 USDT 0/6 positive avg -2,050.935.
- executable notional estimate: 2,500 USDT measurement cap before final transfer/account proof. Do not promote 5,000 because it had negative tails after withdrawal fee.
- frequency/duration evidence or proxy: one integrated BingX/LBank scan across 12,006 markets with zero endpoint errors, direct depth pass on the top venue-involved rows, then six ESPORTS persistence samples with RTT avg 1,704.6 ms and max 1,900.8 ms.
- implementation effort: medium. BingX adapter is straightforward because tickers include bid/ask. LBank adapter must use order-book-first scoring because all-ticker has latest/turnover but no bid/ask.
- inventory/funding requirements: USDT on LBank and either an ESPORTS deposit path to MEXC or pre-positioned MEXC ESPORTS sell inventory. Repeatable route requires LBank BEP20 withdrawal identity to match MEXC BSC contract, live MEXC deposits to be enabled, and a lawful non-U.S. account setup because LBank's current user agreement excludes U.S.-resident personal and corporate accounts.
- risks: conflicting LBank deposit/withdraw status between official suspension notice and public withdrawal-config API, LBank contract identity not exposed in withdrawal config, live MEXC deposit status still not proven, LBank U.S.-resident account restriction, BingX U.S. restricted-jurisdiction language for any BingX sell/buy variant, LBank ticker cannot be trusted for ranking, destination depth tails at 5,000+, transfer latency, and long-tail token event decay.
- confidence: medium for a real current 2,500 USDT public-book pocket; low for repeatable execution until LBank contract identity, live deposit, fee-tier, and non-U.S. account gates are proven.
- verdict: scanner-only `MEASURE` ESPORTS LBank -> MEXC at 2,500 USDT. Do not treat as execution-ready until the LBank deposit/withdraw conflict, LBank contract identity, live MEXC deposit status, non-U.S. account/region eligibility, and actual fee tier are proven. Keep BingX/LBank venue adapters `LATER`; kill all non-ESPORTS rows from this pass unless they reappear with 1,000+ USDT positive depth and transfer metadata.

## Candidate A2-156 - U.S.-Available ENJ Kraken -> Bitstamp

- approach type: U.S.-available cross-exchange spot altcoin arbitrage / migration-basis watch
- route/assets/exchanges: buy Kraken `ENJUSD`, sell Bitstamp `enjusd`.
- quote lane: USD.
- why edge might exist: ENJ has fragmented legacy ERC-20 vs Enjin Relaychain support. A U.S.-available venue pair can show a large basis when one venue's book prices native/relaychain liquidity and another prices Ethereum ENJ.
- public data quality: medium for book measurement, low for repeatable transfer. Kraken and Bitstamp public depth were available. Bitstamp public currency metadata shows ENJ deposits/withdrawals enabled only on `ethereum`. Kraken's official ENJ support page says ERC-20 ENJ funding was phased out on 2024-12-10 and Kraken continues to support ENJ funding on Enjin Relaychain.
- fee assumptions: Kraken 40 bps taker, Bitstamp 40 bps taker, 2 bps latency. Kraken withdrawal-fee public table currently shows Enjin Relaychain fee/minimum evidence, but the chain mismatch is the larger blocker.
- estimated net bps: three book-walk samples at 10:59-11:03 CST: 100 USD 3/3 positive avg +1,483.057 bps, min +1,471.669; 250 USD 3/3 avg +1,482.196, min +1,471.499; 500 USD 3/3 avg +1,090.153, min +1,081.106; 1,000 USD 2/3 positive avg +131.258, min -8.649; 1,500+ negative.
- executable notional estimate: scanner-only 500 USD cap before transfer. No repeatable-transfer executable cap until Kraken Relaychain ENJ can be bridged or deposited to Bitstamp's Ethereum ENJ path.
- frequency/duration evidence or proxy: one full U.S.-available top-of-book scan across 1,146 markets found the route, followed by three individual depth samples roughly 30 seconds apart.
- implementation effort: low for scanner watch; high for execution because it requires network identity, bridge/migration cost/time, and exchange-account funding proof.
- inventory/funding requirements: USD on Kraken and ENJ sell inventory on Bitstamp if pre-positioned. Repeatable route would require a verified Relaychain-to-Ethereum conversion path or a same-network deposit path, neither proven.
- risks: chain mismatch, bridge/migration delay, old-token/new-token price basis, thin Bitstamp sell depth above 500-1,000 USD, Kraken/Bitstamp fee tier assumptions, and one-leg fill risk.
- confidence: medium that the book pocket exists at 500 USD; low that it is repeatable transfer arbitrage.
- verdict: scanner-only `MEASURE` at 500 USD / `KILL_CURRENT` repeatable transfer execution until chain compatibility or bridge proof is verified.

## Candidate A2-157 - 11:06 Active Watch Refresh

- approach type: active public-book route refresh across current scanner pockets.
- route/assets/exchanges: VANRY MEXC -> Binance/KuCoin, GUA MEXC -> Gate, ULTIMA MEXC -> KuCoin, ESPORTS LBank -> MEXC, and ENJ Kraken -> Bitstamp.
- quote lane: USDT, USDC, and USD.
- why edge might exist: current watch routes are event-window or representation-basis pockets with fast-changing depth; caps must be refreshed frequently because the tail risk changes within minutes.
- public data quality: medium. Public REST books returned with zero endpoint errors, but slow route-wide sampling means these are measurement caps, not execution guarantees.
- fee assumptions: MEXC 5 bps, Binance 10, KuCoin 10, Gate 20, LBank 20, Kraken 40, Bitstamp 40, plus 2 bps latency. VANRY includes 80 VANRY MEXC withdrawal fee. ESPORTS includes 4.6915 ESPORTS LBank withdrawal fee. ULTIMA and ENJ exclude transfer because both are chain-blocked.
- estimated net bps: VANRY Binance USDT 10,000 4/4 avg +279.010, min +209.416; VANRY KuCoin 5,000 4/4 avg +240.279, min +134.193; VANRY Binance USDC 5,000 3/4 avg +228.828, min -32.644; GUA 2,500 3/4 avg +168.507, min -64.011; ULTIMA 5,000 4/4 avg +322.931, min +162.210 before chain proof; ESPORTS 2,500 4/4 avg +243.315, min +221.900; ENJ 500 4/4 avg +1,095.851, min +1,088.802.
- executable notional estimate: VANRY Binance USDT 10,000 and VANRY KuCoin 5,000 remain current public-book caps for non-U.S. compliant setups. ESPORTS 2,500 and ENJ 500 are scanner-only. ULTIMA 5,000 is chain-proof-only. VANRY USDC 5,000 and GUA 2,500/5,000 are killed-current pending lower-bucket retest.
- frequency/duration evidence or proxy: four active samples with six-second spacing at 11:06-11:09 CST.
- implementation effort: no new implementation until account/region proof; scanner config should update caps and killed buckets.
- inventory/funding requirements: route-specific inventory remains unchanged; blocked routes need lawful account and chain/deposit proof before execution.
- risks: public REST staleness, thin destination depth, account/region restrictions, transfer-status conflicts, and chain-representation mismatch.
- confidence: high for VANRY USDT cap persistence; medium for scanner-only ESPORTS/ENJ pockets; high for killing current VANRY USDC 5,000 and GUA 2,500 firm caps.
- verdict: `DO_NOW` keep VANRY USDT caps; `MEASURE` ESPORTS 2,500 and ENJ 500 scanner-only; `LATER` ULTIMA 5,000 chain-proof-only; `KILL_CURRENT` VANRY USDC 5,000 and GUA firm caps.

## Candidate A2-158 - 11:12 Funding Refresh

- approach type: spot/perp basis and funding capture.
- route/assets/exchanges: Binance, Bybit, OKX, and Coinbase International Exchange public spot/perp proxies.
- quote lane: USDT and USDC.
- why edge might exist: funding/basis windows can appear independently of spot-spot event windows, especially around negative-funding WLD/TRX-style rows or Coinbase INTX one-hour funding.
- public data quality: high for the proxy. All fetchers returned data with zero endpoint errors.
- fee assumptions: `scripts/funding_probe.py` defaults: Binance spot 10 bps/perp 5, Bybit spot 10/perp 5.5, OKX spot 10/perp 5, Coinbase INTX spot 2/perp 4; round trip is `2 * (spot_taker + perp_taker)`.
- estimated net bps: no positive proxy. Best rows were Coinbase INTX XRP -7.416 bps, ETH -8.661, BTC -8.846, DOGE -9.890, SOL -10.583, OKX WLD -16.845, Binance TRX -17.161, Bybit WLD -17.283, Bybit TRX -18.487, and OKX TRX -18.669.
- executable notional estimate: none because every proxy is negative before borrow, margin, exit-basis, and liquidation modeling.
- frequency/duration evidence or proxy: one 11:12 CST refresh; Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, zero endpoint errors.
- implementation effort: low to keep monitor; no execution work justified.
- inventory/funding requirements: spot inventory or quote balance plus perp margin for positive-funding rows; borrowable or pre-owned spot for negative-funding rows.
- risks: funding decay, basis reversal, borrow availability, margin/liquidation risk, account-level fees, and exit slippage.
- confidence: high for killing immediate taker funding capture.
- verdict: `KILL` immediate funding capture; keep scheduled monitor only.

## Candidate A2-159 - 11:12 Bitso MXN Refresh

- approach type: same-venue fiat/stable/crypto basis.
- route/assets/exchanges: Bitso USD/MXN, USDT/MXN, PYUSD/MXN, BTC/USD, BTC/MXN, ETH/USD, ETH/MXN, XRP/USD, and XRP/MXN.
- quote lane: MXN and USD.
- why edge might exist: local MXN books can diverge from USD/stablecoin and crypto-implied FX when fiat or stablecoin liquidity is stressed.
- public data quality: high for ticker proxy; medium for execution because depth, fee tier, and fiat settlement are not modeled.
- fee assumptions: conservative Bitso 50 bps per leg; stable-vs-USD comparisons use two legs, crypto implied routes use three legs.
- estimated net bps: no positive route. Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -72.310 bps net. USDT/MXN was -95.381 and -110.960 bps net. Best crypto implied route was XRP/MXN buy ask vs implied sell at -152.816 bps net, then BTC -161.736 and ETH -162.676.
- executable notional estimate: none because all proxies are negative before order-book walking and fiat settlement friction.
- frequency/duration evidence or proxy: one 11:12 CST public ticker refresh with zero endpoint errors.
- implementation effort: low to keep monitor; no execution work justified.
- inventory/funding requirements: MXN, USD/stablecoin, and/or BTC/ETH/XRP balances on Bitso.
- risks: Bitso fee tier variance, ticker-only depth overstatement, fiat rail latency, MXN funding constraints, and accounting overhead.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` current MXN/stable/crypto basis; keep scheduled monitor only.

## Candidate A2-160 - 11:14 Liquid Static Refresh

- approach type: liquid/static cross-exchange spot arbitrage regression check.
- route/assets/exchanges: `scripts/market_probe.py` across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso; depth-checked INJ Gate -> MEXC, XLM Crypto.com -> Bitfinex, and XLM MEXC -> Binance.
- quote lane: USDT and USD.
- why edge might exist: liquid venues sometimes show small top-of-book divergences; if the first depth walk survives, these would be simpler than long-tail transfer traps.
- public data quality: high for public ticker/depth on tested routes. The scanner still uses generic top-of-book fees for initial ranking, so exact-fee depth validation is mandatory.
- fee assumptions: strict depth check used Gate 20 bps, MEXC 5, Crypto.com 7.5, Bitfinex 0, Binance 10, and 2-4 bps latency depending quote lane.
- estimated net bps: top-of-book positives were tiny: INJ Gate -> MEXC +5.652 bps, XLM Crypto.com -> Bitfinex +5.437, XLM MEXC -> Binance +1.815. Depth killed all from 100 quote: INJ -34.493 bps at 100 USDT; XLM Crypto.com -> Bitfinex -15.519 bps at 100 USD; XLM MEXC -> Binance -12.285 bps at 100 USDT.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one 11:13-11:14 CST static pass across 10,204 markets with zero endpoint errors plus immediate book walks.
- implementation effort: no execution work justified; scanner should keep exact-pair-fee and depth-first gates.
- inventory/funding requirements: not relevant after rejection.
- risks: generic fee assumptions, tiny top-of-book edges, book-walk slippage, and account-gated Bitfinex access.
- confidence: high for killing immediate liquid static taker execution.
- verdict: `KILL`; continue to prioritize event-window and operational feasibility over static liquid taker rows.

## Candidate A2-161 - 11:28 Event-Window Sampler And TSLAON

- approach type: event-window cross-exchange spot arbitrage.
- route/assets/exchanges: three-sample public sampler across the existing no-key venue set; depth-checked ASSET KuCoin -> MEXC, NIBI MEXC -> KuCoin, TX Bitget -> Gate, TSLAON MEXC -> Bitget, and DEXE KuCoin -> MEXC/Binance.
- quote lane: USDT.
- why edge might exist: event-window repricing creates temporary fragmented books, and tokenized-stock or representation-specific assets can drift between venues before books normalize.
- public data quality: medium-high. Books were public and TSLAON metadata was unusually clear: MEXC and Bitget expose the same ERC20 contract, Bitget deposits/withdrawals are enabled, and MEXC fee-page metadata lists a 0.002 TSLAON ERC20 withdrawal fee. MEXC live withdrawal status still needs account-level proof.
- fee assumptions: venue taker fees by route; TSLAON used MEXC 5 bps, Bitget 10 bps, 2 bps latency, and 0.002 TSLAON withdrawal fee.
- estimated net bps: ASSET was positive through 250 USDT but negative by 500; NIBI and TX were negative from 50; DEXE was positive only through 100 and negative by 250. TSLAON four-sample persistence after transfer fee: 250 USDT 0/4 avg -15.846 bps; 500 2/4 avg -0.805; 1,000 3/4 avg +3.755 min -0.066; 1,500 3/4 avg +2.599 min -1.370; 2,500 1/4 avg -2.256.
- executable notional estimate: none. TSLAON's best bucket is too thin and min-negative after transfer fee.
- frequency/duration evidence or proxy: three event-window samples across 10,122 markets, followed by direct depth and a four-sample TSLAON persistence check.
- implementation effort: no execution work justified; add TSLAON to scanner regression examples.
- inventory/funding requirements: none after rejection. If revisited, would require USDT on MEXC, Bitget TSLAON deposit proof, and compliant non-U.S. accounts.
- risks: tiny net edge, destination depth tails, tokenized-stock representation risk, account/region restrictions, and MEXC withdrawal status not exposed publicly.
- confidence: high for killing current execution; medium that TSLAON can occasionally reappear as a very thin event-window basis.
- verdict: `KILL` current event-window pass. Revisit TSLAON only if 1,000+ USDT buckets are 100% positive with a meaningful minimum after transfer fee.

## Candidate A2-162 - 11:31 Lower-Cap Retest

- approach type: active watch cap retest.
- route/assets/exchanges: VANRY MEXC -> Binance USDC and GUA MEXC -> Gate pre-positioned.
- quote lane: USDC and USDT.
- why edge might exist: both routes had negative tails at their prior larger caps, so lower-bucket retesting can preserve useful scanner thresholds without pretending the higher caps are firm.
- public data quality: high for public depth. Four samples completed with zero endpoint errors.
- fee assumptions: VANRY used MEXC 5 bps, Binance 10 bps, 2 bps latency, and 80 VANRY withdrawal fee. GUA used MEXC 5 bps, exact Gate 20 bps, and 2 bps latency with no transfer fee because it is pre-positioned-only while Gate deposits are disabled.
- estimated net bps: VANRY USDC 2,500 4/4 positive avg +944.584 bps, min +917.416; VANRY USDC 5,000 4/4 positive avg +180.869, min +17.544. GUA 500 4/4 avg +494.485, min +380.031; GUA 1,000 4/4 avg +331.502, min +139.719; GUA 2,500 2/4 avg -11.679, min -132.673.
- executable notional estimate: VANRY USDC firm measurement cap restored to 2,500 only; 5,000 remains live-threshold-only. GUA pre-positioned lower cap restored to 1,000 only; 2,500 remains killed-current.
- frequency/duration evidence or proxy: four samples at 11:29-11:31 CST with six-second spacing.
- implementation effort: scanner config update only; no execution work without account/region and deposit proof.
- inventory/funding requirements: VANRY needs non-U.S. compliant MEXC/Binance setup and current MEXC withdrawal status. GUA needs pre-positioned Gate inventory because deposits remain disabled.
- risks: fast-moving destination depth, prior negative tails, account/region restrictions, and disabled Gate deposits for repeatable GUA.
- confidence: high for restoring lower caps; high for keeping higher caps killed-current/live-threshold-only.
- verdict: `MEASURE` VANRY USDC 2,500; `LATER` GUA pre-positioned 1,000; keep VANRY USDC 5,000 and GUA 2,500 out of firm caps.

## Candidate A2-163 - 11:34 Coinbase-Inclusive U.S. Scan

- approach type: U.S.-available cross-exchange spot scan.
- route/assets/exchanges: Coinbase Exchange, Binance.US, Kraken, and Bitstamp across USD/USDT/USDC books.
- quote lane: USD, USDT, USDC.
- why edge might exist: U.S.-available venue fragmentation is more valuable than global-only pockets because it avoids the MEXC/KuCoin/LBank/BingX U.S.-resident blocker.
- public data quality: medium-high. Coinbase broker `best_bid_ask` is authenticated, but no-key Coinbase Exchange ticker calls returned bid/ask for 165 markets.
- fee assumptions: conservative Coinbase 120 bps, Binance.US 2 bps, Kraken 40 bps, Bitstamp 40 bps, and 2 bps latency.
- estimated net bps: positive top-of-book rows were known traps: LIT Kraken -> Bitstamp, VELO/SUP Kraken -> Coinbase ticker collisions, ENJ Kraken -> Bitstamp chain-mismatch basis, and MANA into Bitstamp. MANA Coinbase -> Bitstamp depth was deeply negative: 25 USD -1,619.081 bps, 100 USD -1,805.005, 250 USD -3,504.835; Bitstamp bids exhausted by 500 USD.
- executable notional estimate: none beyond the already-recorded ENJ 500 USD scanner-only chain-mismatch pocket.
- frequency/duration evidence or proxy: one 11:32-11:34 CST public scan, 1,311 usable markets, then direct MANA depth.
- implementation effort: low to keep Coinbase Exchange ticker calls in U.S. scanner; no execution implementation justified.
- inventory/funding requirements: not relevant after rejection.
- risks: Coinbase high taker fee, ticker collisions, thin Bitstamp sell books, and old-token/new-token network basis.
- confidence: high for killing new Coinbase-inclusive execution candidates.
- verdict: `KILL` new Coinbase-inclusive routes. Keep ENJ as existing scanner-only chain-mismatch watch.

## Candidate A2-164 - 11:36 U.S. Same-Venue Triangular Scan

- approach type: same-venue triangular arbitrage.
- route/assets/exchanges: USD/USDT/USDC cycles on Binance.US, Coinbase Exchange, Kraken, and Bitstamp.
- quote lane: USD, USDT, USDC.
- why edge might exist: same-venue cycles avoid transfer/account rebalancing and can be executable if the top-of-book cycle is positive enough to survive three fees and depth.
- public data quality: high for top-of-book rejection. Public ticker/book endpoints returned enough bid/ask data; no depth work is needed because top-of-book was already negative.
- fee assumptions: Binance.US 2 bps, Coinbase 120 bps, Kraken 40 bps, Bitstamp 40 bps per leg.
- estimated net bps: no positive cycles. Binance.US best was USDT -> ETH -> USDC -> USDT at -5.836 bps. Coinbase best was -355.317 bps, Kraken best -117.427, and Bitstamp best -119.488.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one 11:35-11:36 CST top-of-book cycle pass. Cycle counts: Binance.US 118, Coinbase 16, Kraken 244, Bitstamp 24.
- implementation effort: no execution work justified.
- inventory/funding requirements: same-venue balances only, but not relevant after rejection.
- risks: three-leg fill risk, fees, depth, and stale public books.
- confidence: high for killing taker-only U.S. same-venue triangles.
- verdict: `KILL` taker-only U.S. triangular cycles; revisit only for maker/rebate or fee-tier-specific modeling.

## Candidate A2-165 - 11:38 Active Watch Refresh

- approach type: active public-book route refresh.
- route/assets/exchanges: VANRY MEXC -> Binance/KuCoin, ESPORTS LBank -> MEXC, and ENJ Kraken -> Bitstamp.
- quote lane: USDT, USDC, USD.
- why edge might exist: the live watchlist has repeated but fast-moving pockets; frequent refreshes keep caps from drifting upward after a single clean print.
- public data quality: medium. Public books returned cleanly; this is still not execution proof because account, chain, and transfer status remain blockers.
- fee assumptions: MEXC 5 bps, Binance 10, KuCoin 10, LBank 20, Kraken 40, Bitstamp 40, 2 bps latency; VANRY includes 80 VANRY withdrawal fee; ESPORTS includes 4.6915 ESPORTS LBank fee; ENJ excludes transfer because it is chain-mismatch blocked.
- estimated net bps: VANRY Binance USDT 10,000 4/4 avg +301.248, min +256.660; VANRY KuCoin 5,000 4/4 avg +366.447, min +284.561; VANRY USDC 2,500 4/4 avg +821.553, min +632.805; VANRY USDC 5,000 2/4 avg -8.320, min -248.499; ESPORTS 2,500 4/4 avg +200.590, min +182.457; ESPORTS 5,000 0/4 avg -18.782; ENJ 500 4/4 avg +1,022.532, min +1,015.964; ENJ 1,000 0/4 avg -241.402.
- executable notional estimate: VANRY Binance USDT 10,000 and KuCoin 5,000 remain current public-book caps for non-U.S. compliant setups. VANRY USDC firm cap remains 2,500. ESPORTS 2,500 and ENJ 500 remain scanner-only. Kill current 5,000 expansion buckets for VANRY USDC and ESPORTS, and 1,000 ENJ.
- frequency/duration evidence or proxy: four samples at 11:36-11:38 CST with six-second spacing.
- implementation effort: scanner cap update only.
- inventory/funding requirements: unchanged; top routes remain account/region and chain/deposit gated.
- risks: destination depth tails, public REST staleness, account restrictions, LBank status conflict, ENJ chain mismatch.
- confidence: high for current cap confirmations.
- verdict: keep current caps; `KILL_CURRENT` VANRY USDC 5,000, ESPORTS 5,000, and ENJ 1,000.

## Candidate A2-166 - 11:44 Gemini-Inclusive U.S.-Available Scan

- approach type: U.S.-available cross-exchange spot scan and parser/identity gate.
- route/assets/exchanges: Coinbase Exchange, Binance.US, Kraken, Bitstamp, and Gemini across USD/USDT/USDC public books.
- quote lane: USD, USDT, USDC, with a Gemini GUSD parser trap found during the scan.
- why edge might exist: adding Gemini increases the U.S.-available opportunity graph and can surface account-compliant USD routes that avoid the MEXC/KuCoin/LBank/BingX U.S.-resident blocker.
- public data quality: medium-high for books; medium for symbol identity. Corrected scan used 1,904 usable bid/ask markets: Coinbase 423, Binance.US 256, Kraken 771, Bitstamp 138, Gemini 316. Endpoint errors were 4, mostly Coinbase 429 and Gemini metadata misses. Gemini's all-symbol details endpoint returned 404, but per-symbol details worked.
- fee assumptions: Binance.US 2 bps, Coinbase 120 bps, Kraken 40 bps, Bitstamp 40 bps, Gemini 120 bps, plus 2 bps latency.
- estimated net bps: positive top-of-book rows were LIT Kraken -> Bitstamp +91,505.786 bps, VELO Kraken -> Coinbase +28,624.280, SUP Kraken -> Coinbase +24,366.893, OPG Gemini -> Coinbase +5,284.316, ENJ Kraken -> Bitstamp +1,540.997, MANA into Bitstamp +635 to +718, and INJ into Gemini +114 to +183. Depth/identity killed every new route. INJ depth was negative immediately: Bitstamp -> Gemini -118.986 bps from 25-500 USD, Kraken -> Gemini about -130 bps from the first bucket, and Coinbase -> Gemini about -195 bps from the first bucket.
- executable notional estimate: none beyond existing ENJ 500 USD scanner-only chain-mismatch watch.
- frequency/duration evidence or proxy: one corrected 11:44 CST public scan plus direct book-walks for all 11 positive route rows.
- implementation effort: low to add Gemini public tickers; mandatory to add Gemini per-symbol details before any route scoring.
- inventory/funding requirements: none after rejection. Any future U.S.-available route would require USD or stable balances on the buy venue and same-asset sell inventory or transfer proof.
- risks: ticker collisions, Gemini symbol ambiguity, Coinbase high taker fees, Bitstamp thin books, old-token/new-token network basis, and public REST staleness.
- confidence: high for rejecting the current Gemini-inclusive routes. Very high for the parser fix because Gemini per-symbol details for `opgusd` report base `OP`, quote `GUSD`, and contract price currency `GUSD`, while Coinbase `OPG` is Opengradient on Base.
- verdict: `KILL` new Gemini-inclusive U.S. execution candidates. Add scanner gate: never infer Gemini base/quote only by suffix; use per-symbol details and exclude GUSD from USD-lane scoring unless explicitly modeled.

## Candidate A2-167 - 11:47 Funding Refresh

- approach type: spot/perp basis and funding capture.
- route/assets/exchanges: Binance, Bybit, OKX, and Coinbase International Exchange public spot/perp proxies.
- quote lane: USDT and USDC.
- why edge might exist: funding windows can appear independently from spot-spot dislocations, especially around negative-funding WLD/TRX rows or Coinbase INTX one-hour contracts.
- public data quality: high for rejection. Binance 14, Bybit 14, OKX 14, and Coinbase INTX 5 routes returned with zero endpoint errors.
- fee assumptions: `scripts/funding_probe.py` defaults: Binance spot 10 bps/perp 5, Bybit spot 10/perp 5.5, OKX spot 10/perp 5, Coinbase INTX spot 2/perp 4; round trip is `2 * (spot_taker + perp_taker)`.
- estimated net bps: no positive proxy. Best rows were Coinbase INTX DOGE -9.898 bps, SOL -10.471, XRP -11.186, BTC -11.980, ETH -14.074, Bybit WLD -14.797, OKX WLD -16.908, OKX TRX -18.330, Binance TRX -18.524, and Binance WLD -19.439.
- executable notional estimate: none because every proxy is negative before borrow, margin, exit-basis, and liquidation modeling.
- frequency/duration evidence or proxy: one scheduled 11:47 CST refresh.
- implementation effort: low to keep scheduled monitor; no execution work justified.
- inventory/funding requirements: spot inventory or quote balance plus perp margin for positive-funding rows; borrowable or pre-owned spot for negative-funding rows.
- risks: funding decay, basis reversal, borrow availability, margin/liquidation risk, account-level fees, and exit slippage.
- confidence: high for killing immediate taker funding capture.
- verdict: `KILL` immediate funding capture; keep scheduled monitor only.

## Candidate A2-168 - 11:47 Bitso MXN Refresh

- approach type: same-venue fiat/stable/crypto basis.
- route/assets/exchanges: Bitso USD/MXN, USDT/MXN, PYUSD/MXN, BTC/USD, BTC/MXN, ETH/USD, ETH/MXN, XRP/USD, and XRP/MXN.
- quote lane: MXN and USD.
- why edge might exist: local MXN books can diverge from USD/stablecoin and crypto-implied FX when fiat or stablecoin liquidity is stressed.
- public data quality: high for ticker proxy; medium for execution because depth, fee tier, and fiat settlement are not modeled.
- fee assumptions: conservative Bitso 50 bps per leg; stable-vs-USD comparisons use two legs, crypto implied routes use three legs.
- estimated net bps: no positive route. Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -77.485 bps net. USDT/MXN comparisons were -103.465 and -115.010 bps net. Best crypto implied route was BTC/MXN sell bid vs implied buy at -147.151 bps, then XRP -154.263 and ETH -155.149.
- executable notional estimate: none because all proxies are negative before order-book walking and fiat settlement friction.
- frequency/duration evidence or proxy: one 11:47 CST public ticker refresh with zero endpoint errors.
- implementation effort: low to keep monitor; no execution work justified.
- inventory/funding requirements: MXN, USD/stablecoin, and/or BTC/ETH/XRP balances on Bitso.
- risks: Bitso fee tier variance, ticker-only depth overstatement, fiat rail latency, MXN funding constraints, and accounting overhead.
- confidence: high for killing immediate taker execution.
- verdict: `KILL` current MXN/stable/crypto basis; keep scheduled monitor only.

## Candidate A2-169 - 11:51 Active Watch Refresh

- approach type: active public-book route refresh.
- route/assets/exchanges: VANRY MEXC -> Binance/KuCoin, ESPORTS LBank -> MEXC, ENJ Kraken -> Bitstamp, ULTIMA MEXC -> KuCoin, and GUA MEXC -> Gate pre-positioned.
- quote lane: USDT, USDC, USD.
- why edge might exist: current watch routes are fast-moving event-window or representation-basis pockets; frequent refreshes prevent stale caps from becoming false execution assumptions.
- public data quality: medium. Public books returned cleanly, but the route-wide pass was slow: four samples from 11:49:57 to 11:51:10 CST, with per-sample elapsed time from 12.4s to 16.2s.
- fee assumptions: MEXC 5 bps, Binance 10, KuCoin 10, LBank 20, Kraken 40, Bitstamp 40, Gate 20, and 2 bps latency. VANRY includes 80 VANRY withdrawal fee. ESPORTS includes 4.6915 ESPORTS LBank fee. ENJ excludes transfer because it is chain-mismatch blocked. ULTIMA excludes transfer because it is chain-proof-only. GUA excludes transfer because it is pre-positioned-only while Gate deposits are disabled.
- estimated net bps: VANRY Binance USDT 10,000 4/4 avg +290.414, min +208.947; VANRY KuCoin 5,000 4/4 avg +225.427, min +123.462; VANRY Binance USDC 2,500 4/4 avg +853.068, min +751.993; VANRY USDC 5,000 4/4 avg +368.305 but min only +12.665 after prior negative tails; ESPORTS 2,500 4/4 avg +89.088, min +72.064; ESPORTS 5,000 0/4 avg -199.662; ENJ 500 4/4 avg +1,053.865, min +1,049.290; ENJ 1,000 0/4 avg -529.055; ULTIMA 5,000 4/4 avg +364.068, min +324.264 before chain proof; GUA 1,000 4/4 avg +43.522, min +22.969; GUA 2,500 0/4 avg -195.169.
- executable notional estimate: VANRY Binance USDT 10,000 and VANRY KuCoin 5,000 remain current public-book caps for non-U.S. compliant setups. VANRY USDC firm cap remains 2,500. ESPORTS 2,500 and ENJ 500 remain scanner-only. ULTIMA 5,000 remains chain-proof-only. GUA remains only 1,000 pre-positioned and is decaying.
- frequency/duration evidence or proxy: four active samples with six-second spacing plus slow public REST sampling overhead.
- implementation effort: scanner cap update only.
- inventory/funding requirements: unchanged; top routes remain account/region, transfer-status, chain, or pre-positioning gated.
- risks: public REST staleness from slow sampling, destination depth tails, account restrictions, LBank status conflict, ENJ chain mismatch, ULTIMA representation split, and disabled Gate deposits for GUA.
- confidence: high for keeping current VANRY caps; medium for scanner-only ESPORTS because edge is shrinking; high for keeping killed larger buckets out of firm caps.
- verdict: keep ranking unchanged but update caps: `DO_NOW` VANRY USDT routes, `MEASURE` VANRY USDC 2,500 / ESPORTS 2,500 / ENJ 500, `LATER` ULTIMA chain-proof and GUA 1,000 pre-positioned. Do not restore VANRY USDC 5,000 despite the 4/4 print because the minimum is too thin and prior refreshes had negative tails.

## Candidate A2-170 - 11:53 Broad Liquid Static Refresh

- approach type: liquid/static cross-exchange spot arbitrage regression check.
- route/assets/exchanges: `scripts/market_probe.py` across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso.
- quote lane: USD, USDT, USDC, MXN, and EUR in discovery; sane priority review focused on modeled same-lane routes.
- why edge might exist: liquid venues sometimes show small top-of-book divergences, especially Crypto.com/OKX/Bybit USD books versus Bitfinex zero-fee USD.
- public data quality: high for rejection. The probe scanned 10,204 markets with zero endpoint errors.
- fee assumptions: `scripts/market_probe.py` generic taker/latency assumptions, including Crypto.com 7.5 bps and Bitfinex 0 bps for the top USD rows.
- estimated net bps: no positive sane priority route. Best rows were already negative before depth: BTC Crypto.com -> Bitfinex -2.027 bps, SOL Crypto.com -> Bitfinex -2.317, XRP Crypto.com -> Bitfinex -2.443, ETH Crypto.com -> Bitfinex -2.578, SUI Crypto.com -> Bitfinex -2.776. The best USDT rows were also negative, led by NEAR Bitget -> Binance/Bybit/OKX at -6.615 bps and SUI Gate -> MEXC at -7.184.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one 11:53 CST broad static pass.
- implementation effort: no execution work justified; keep exact-depth gate in scanner.
- inventory/funding requirements: not relevant after rejection.
- risks: stale tickers, generic fee assumptions, and raw long-tail ticker collisions; none matter for promotion because the sane-priority set is already negative.
- confidence: high for killing immediate liquid static taker execution.
- verdict: `KILL`; continue using liquid static as a regression monitor, not a priority search path.

## Candidate A2-171 - 11:55 Event-Window Sampler

- approach type: event-window cross-exchange spot arbitrage / pre-positioned-inventory watch.
- route/assets/exchanges: three-sample public sampler across the existing no-key venue set excluding Bitso and recent watchlist/kill bases; depth-checked UPC MEXC -> Bitget, IAG Gate/KuCoin -> Bitget, POWER MEXC/Bitget -> Gate, ARTFI MEXC -> Gate, HYDRA MEXC -> KuCoin, SWEAT Bitget/MEXC -> Gate, AVT, PVT, VRA, NERO, TOWER, ALKIMI, TTD, and TYCOON.
- quote lane: USDT.
- why edge might exist: long-tail books can remain fragmented after listing/transfer events; some routes are real book dislocations but only monetizable with pre-positioned sell inventory when deposits are closed.
- public data quality: medium-high for books and transfer rejection. Three samples each covered 10,122 markets with zero endpoint errors. Transfer metadata was checked for UPC, IAG, POWER, SWEAT, VRA, HYDRA, and TOWER.
- fee assumptions: exact depth pass used MEXC 5 bps, Bitget 10 bps, Gate 20 bps, KuCoin 10 bps, and 2 bps latency. No transfer fee was included for pre-positioned-only blocked routes.
- estimated net bps: UPC MEXC -> Bitget survived through 5,000 USDT with +2,050.440 bps at 5,000. POWER Bitget -> Gate survived through 5,000 at +227.138 bps; POWER MEXC -> Gate survived through 2,500 at +820.137 but was negative by 5,000. IAG Gate/KuCoin -> Bitget survived through 1,000 but was negative by 2,500. HYDRA MEXC -> KuCoin survived through 1,000 but was -16.771 at 2,500. SWEAT Bitget -> Gate survived through 2,500 with +28.152 but was negative by 5,000. VRA survived through 1,000 and failed by 2,500. Other checked rows failed by 250-500 or were exhausted.
- executable notional estimate: no repeatable-transfer cap. Pre-positioned-only watch caps: UPC Bitget inventory up to 5,000 USDT in the latest book; POWER Gate inventory up to 5,000 USDT from Bitget buy or 2,500 from MEXC buy. Treat all as one-shot/inventory-shift only.
- frequency/duration evidence or proxy: three top-of-book samples from 11:55:04 to 11:55:36 CST, followed by single direct depth walk at 11:58 CST.
- implementation effort: no live execution work until inventory exists on the sell venue. Scanner should mark these as pre-positioned-only and avoid repeatable-transfer promotion.
- inventory/funding requirements: UPC inventory already on Bitget, or POWER inventory already on Gate. IAG would require inventory already on Bitget because Bitget deposits are disabled. Repeatability would require destination deposits to reopen.
- risks: destination deposits disabled, one-shot inventory depletion, long-tail book decay, public REST staleness, account/region restrictions, and transfer fee not modeled for blocked routes.
- confidence: high that UPC/POWER books were real in this snapshot; high that repeatable transfer is blocked by current public metadata.
- verdict: `LATER` UPC and POWER pre-positioned-inventory watches only; `KILL` repeatable direct transfer for all rows in this pass.

## Candidate A2-172 - 12:01 Blocked-Route Deposit Sweep

- approach type: operational feasibility sweep for blocked event-window routes.
- route/assets/exchanges: Gate GUA/TBC/ESPORTS/RAVE/POWER/SWEAT/VRA/TYCOON/ARTFI; KuCoin RAVE/ULTIMA/HYDRA/IAG/TOWER/XMN; Bitget UPC/IAG/RAVE/BTR/SUP/VELO.
- quote lane: USDT.
- why edge might exist: several large book dislocations are killed only by destination deposit status; if deposits reopen, the same scanner routes could become repeatable candidates.
- public data quality: high for current public status. Gate, KuCoin, and Bitget public currency endpoints returned current chain-level deposit/withdraw flags.
- fee assumptions: not applicable; this is an operational gate check.
- estimated net bps: no new bps measurement. It rechecks whether existing blocked bps can become actionable.
- executable notional estimate: none promoted. UPC/POWER remain pre-positioned-only. XMN remains pending MEXC withdrawal status/fee, not promoted by this sweep.
- frequency/duration evidence or proxy: one 12:01 CST public metadata sweep.
- implementation effort: low to keep as periodic blocked-route monitor.
- inventory/funding requirements: unchanged; pre-positioned inventory is required on sell venues with deposits disabled.
- risks: public metadata can lag logged-in availability; chain-specific status must still be confirmed in account before execution.
- confidence: high that no blocked high-value route reopened in public metadata.
- verdict: `KILL` repeatable-transfer promotion from this sweep. Keep deposit-status monitor; no ranking promotion.

## Candidate A2-173 - 12:03 XMN Resolution

- approach type: stale micro-route resolution / cross-exchange spot altcoin arbitrage.
- route/assets/exchanges: buy MEXC `XMNUSDT`, sell KuCoin `XMN-USDT`.
- quote lane: USDT.
- why edge might exist: older discovery found a small XMN pocket but left it pending because MEXC withdrawal status/fee was unresolved.
- public data quality: high enough to reject. MEXC exchangeInfo and KuCoin currency metadata both identify xMoney on SUI contract `0x97c7571f4406cdd7a95f3027075ab80d3e9c937c2a567690d31e14ab1872ccee::xmn::XMN`. MEXC public fee endpoint now exposes XMN SUI withdrawal fee `8`, deposit fee `0`, and withdrawal minimum `20`; KuCoin SUI deposits and withdrawals are enabled.
- fee assumptions: MEXC 5 bps, KuCoin 10 bps, 2 bps latency, and 8 XMN MEXC withdrawal fee.
- estimated net bps: fresh 12:03 CST depth after withdrawal fee was negative at every bucket: 50 USDT -124.436 bps, 100 -174.141, 250 -253.750, 500 -326.768, 1,000 -364.574, and 2,500 -1,760.965.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one metadata resolution plus fresh direct book walk.
- implementation effort: no work justified.
- inventory/funding requirements: not relevant after rejection.
- risks: small-cap depth decay and transfer-fee drag.
- confidence: high for current rejection.
- verdict: `KILL_CURRENT` XMN; remove from active `LATER` backlog until rediscovered by event sampler.

## Candidate A2-174 - 12:05 Active Watch Refresh

- approach type: active watchlist cap refresh / cross-exchange spot arbitrage monitor.
- route/assets/exchanges: VANRY MEXC -> Binance/KuCoin, VANRY MEXC -> Binance USDC, ESPORTS LBank -> MEXC, ENJ Kraken -> Bitstamp, ULTIMA MEXC -> KuCoin, GUA MEXC -> Gate, and UPC MEXC -> Bitget.
- quote lane: USDT, USDC, and USD.
- why edge might exist: current watch routes are event-window or representation-basis pockets; frequent compact refreshes keep cap decisions tied to live public depth instead of stale prior wins.
- public data quality: medium. Three samples completed from 12:05:04 to 12:05:40 CST with per-sample elapsed time from 6.9s to 9.4s. UPC errored in the active-watch route code and was not used as evidence.
- fee assumptions: MEXC 5 bps, Binance 10, KuCoin 10, LBank 20, Kraken 40, Bitstamp 40, Gate 20, and 2 bps latency. VANRY includes 80 VANRY withdrawal fee; ESPORTS includes 4.6915 ESPORTS LBank fee; ENJ excludes transfer because it is chain-mismatch blocked; ULTIMA and GUA remain chain/pre-positioning gated.
- estimated net bps: VANRY Binance USDT 10,000 3/3 avg +328.791, min +236.042; VANRY KuCoin 5,000 3/3 avg +290.453, min +229.884; VANRY Binance USDC 2,500 3/3 avg +921.386, min +709.668; VANRY USDC 5,000 only 2/3, min -177.208; ESPORTS 2,500 0/3 avg -23.699, min -36.068; ENJ 500 3/3 avg +1,041.487, min +1,038.871; ENJ 1,000 3/3 avg +194.732, min +182.584; ULTIMA 5,000 3/3 avg +439.480, min +432.244 before chain proof; GUA 1,000 3/3 avg +159.317, min +108.160; GUA 2,500 0/3 avg -198.137.
- executable notional estimate: unchanged for executable candidates: VANRY Binance USDT 10,000 and VANRY KuCoin 5,000 remain the only strong public-book caps for non-U.S. compliant setups. VANRY USDC firm cap remains 2,500. ESPORTS LBank current scanner cap is killed. ENJ 500 remains scanner-only and transfer-killed; do not restore 1,000 until a longer retest confirms the recovery. ULTIMA/GUA remain chain-proof/pre-positioned only.
- frequency/duration evidence or proxy: three active samples with slow public REST overhead, run immediately after XMN resolution.
- implementation effort: scanner cap update and one UPC route-code cleanup/retest.
- inventory/funding requirements: unchanged; account/region proof is still the gating item before any non-U.S. route design.
- risks: public REST staleness, fast depth decay, venue account restrictions, transfer-status conflicts, ENJ chain mismatch, ULTIMA representation split, Gate deposits disabled for GUA, and UPC measurement code error.
- confidence: high for keeping VANRY caps and killing current ESPORTS; medium for ENJ 1,000 recovery because the prior refresh was 0/4.
- verdict: keep `DO_NOW` on VANRY USDT routes; keep VANRY USDC 2,500 and ENJ 500 as `MEASURE`; demote ESPORTS LBank -> MEXC to `KILL_CURRENT`; keep ULTIMA/GUA/UPC as gated `LATER`.

## Candidate A2-175 - 12:09 UPC Clean Direct Retest

- approach type: pre-positioned-inventory cross-exchange spot arbitrage watch.
- route/assets/exchanges: buy MEXC `UPCUSDT`, sell Bitget `UPCUSDT`.
- quote lane: USDT.
- why edge might exist: Bitget sell book remains far above MEXC buy book while deposits are disabled, creating a one-shot inventory liquidation pocket rather than a repeatable transfer route.
- public data quality: high for the current rejection/promotion split. Direct MEXC and Bitget books fetched cleanly at 12:09:47 CST; Bitget public coin metadata also fetched cleanly.
- fee assumptions: MEXC 5 bps taker, Bitget 10 bps taker, and 2 bps latency. No transfer fee included because repeatable transfer is blocked.
- estimated net bps: 50 USDT +3,071.889 bps, 100 +2,984.681, 250 +2,861.136, 500 +2,814.170, 1,000 +2,681.199, 2,500 +2,279.171, 5,000 +2,038.202, and 10,000 +1,575.217.
- executable notional estimate: up to 10,000 USDT only if UPC is already held on Bitget. No direct repeatable buy-transfer-sell execution.
- frequency/duration evidence or proxy: one clean direct depth retest after the 12:05 active-watch route errored.
- implementation effort: low for pre-positioned alerting; no execution work unless Bitget inventory exists.
- inventory/funding requirements: UPC inventory already on Bitget or another valid path into Bitget. MEXC buy inventory alone does not help while Bitget deposits are disabled.
- risks: one-shot inventory depletion, Bitget deposit status, long-tail book spoofing/staleness, and inability to replenish sell inventory.
- confidence: high that the current book pocket exists; high that repeatable transfer is blocked by Bitget `rechargeable=false`.
- verdict: `LATER` pre-positioned-inventory watch only; `KILL` repeatable transfer.

## Candidate A2-176 - 12:10 Scheduled Funding, Bitso, And Liquid Static Refresh

- approach type: scheduled regression sweep across funding, MXN basis, and broad static spot.
- route/assets/exchanges: `scripts/funding_probe.py` across Binance/Bybit/OKX/Coinbase INTX; Bitso MXN/USD/stables/crypto public tickers; `scripts/market_probe.py` across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso.
- quote lane: USDT, USDC, USD, and MXN.
- why edge might exist: funding/basis and liquid static routes can flip during regime changes even when long-tail event windows dominate the current backlog.
- public data quality: high for rejection. Funding returned 47 routes with zero endpoint errors. Broad static scan returned 10,204 markets with zero endpoint errors. Bitso ticker reads completed cleanly.
- fee assumptions: existing script assumptions for funding and static scanner; Bitso modeled with 50 bps taker per leg.
- estimated net bps: funding best was Coinbase INTX SOL -7.932 bps, then BTC -8.328, DOGE -8.888, ETH -9.443, and XRP -9.679. Bitso best stable comparison was PYUSD/MXN sell vs USD/MXN buy at -81.472 bps; best crypto implied route was XRP at -152.358 bps. Broad liquid static had no positive sane-priority row; best was BTC Crypto.com -> Bitfinex -2.237 bps.
- executable notional estimate: none.
- frequency/duration evidence or proxy: one scheduled refresh from 12:10-12:11 CST.
- implementation effort: no execution work justified.
- inventory/funding requirements: not relevant after rejection.
- risks: funding can flip later, Bitso fee tiers could improve with account-specific volume, and static scanner still needs exact-depth validation if a future top layer turns positive.
- confidence: high for no immediate promotion.
- verdict: `KILL` immediate execution for funding, Bitso MXN, and liquid static; keep as scheduled monitors below VANRY and event-window discovery.

## Candidate A2-177 - 12:13 Event-Window Sampler

- approach type: event-window cross-exchange spot arbitrage discovery.
- route/assets/exchanges: three public samples across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, and Bitfinex; direct-depth checks on REACT, GHX, LOFI, EQTY, BRISE, MODE, KARRAT, LONG, CTA, ITHACA, and PIN.
- quote lane: USDT.
- why edge might exist: long-tail venue books can fragment briefly after listing, deposit, or liquidity events.
- public data quality: medium-high for rejection. Three samples each covered 10,122 markets with zero endpoint errors; direct order-book depth fetched cleanly for the checked routes.
- fee assumptions: direct depth used MEXC 5 bps, Gate 20 bps, KuCoin 10 bps, Bybit 10 bps, and 2 bps latency.
- estimated net bps: RWA and AI topped the sampler but are known ticker/identity traps. REACT KuCoin -> Gate was +170.654 bps at 50 USDT, +103.340 at 100, and -3.032 at 250. GHX Gate -> MEXC was +207.226 at 50, +168.406 at 100, +96.568 at 250, +34.615 at 500, and -21.417 at 1,000. GHX KuCoin -> MEXC was similar and negative by 1,000. LOFI, EQTY, MODE, KARRAT, CTA, ITHACA, and PIN were negative from 50 or failed sell depth; BRISE and LONG were micro-only.
- executable notional estimate: none. No checked non-trap row survived 1,000 USDT after exact fees.
- frequency/duration evidence or proxy: three top-of-book samples from 12:13:27 to 12:14:12 CST plus direct depth at 12:14:53-12:15:01.
- implementation effort: no execution work justified; improve processed-base exclusions for RWA, AI, GHX, PYBOBO, and HONEY.
- inventory/funding requirements: none after rejection.
- risks: same-ticker collisions, stale top-of-book, thin sell depth, and dust-scale positives.
- confidence: high for no promotion.
- verdict: `KILL` current event-window pass; keep scanning, but require 1,000+ USDT positive direct depth before metadata work.
