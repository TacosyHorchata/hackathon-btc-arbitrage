# Agent 2 Continuous Scout Report

Agent: Continuous Profit Scout Agent 2  
Repo: `/Users/pedrorios/Desktop/gold/hackathon-btc`  
Started: 2026-05-29 02:48 CST  
Rule: no real trading, no private API keys, no edits outside Agent 2 deliverables.

## Checkpoint - 2026-05-29 02:55 CST

### What I Measured

1. Public spot market discovery across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com Exchange, and Bitso.
   - Probe: `python3 scripts/market_probe.py`
   - Result: 10,132 normalized markets, no fetch errors.
   - Quote coverage: USDT 7,114; USD 1,445; USDC 1,143; EUR 407; MXN 23.

2. Same-lane USDT altcoin cross-exchange hypothesis.
   - The naive top routes were mostly invalid symbol collisions or incomparable tickers.
   - After filtering for liquid, sane top-of-book routes, `XMR/USDT` KuCoin -> MEXC was the best measurable candidate.
   - Depth check: positive only at small size. At 0.5 XMR (~181 USDT), net was about +2.7 to +4.9 bps. At 2 XMR (~726 USDT), net flipped around the threshold.
   - 20 samples over about 71 seconds: 0.5 XMR positive in 20/20 samples; 2 XMR positive in 14/20 samples.
   - Verdict: `MEASURE`, not `DO_NOW`. The edge is real enough to track, but too small to trust without WebSocket depth, min-size verification, account availability, and execution latency measurement.

3. Bitso MXN / FX basis hypothesis.
   - Bitso public tickers checked: `btc_mxn`, `btc_usd`, `btc_usdt`, `usd_mxn`, `usdt_mxn`, `usd_usdt`, `eth_mxn`, `eth_usd`, `sol_mxn`, `sol_usd`, `xrp_mxn`, `xrp_usd`.
   - BTC/ETH/SOL MXN vs USD-implied basis was negative or single-digit bps.
   - XRP showed about +7.1 bps gross on one direction before fees, but Bitso taker fees alone kill it.
   - Stablecoin MXN books (`usdt_mxn`, `usd_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, `tusd_mxn`) do not show a net-positive triangle after spread and fees.
   - Verdict: `KILL` for immediate arbitrage; keep Bitso as `LATER` for market discovery because liquidity in USDT/MXN and USD/MXN is useful.

4. Spot-perp funding capture hypothesis.
   - Public funding endpoints checked for Binance USD-M, Bybit linear, and OKX swaps on BTC, ETH, SOL, XRP, DOGE.
   - Funding was positive but small: roughly 0.08 to 1.00 bps per 8h.
   - Perp marks were below index by about 2 to 6 bps on Binance/Bybit. That entry basis consumes multiple funding intervals before becoming attractive.
   - Verdict: `LATER`. It is a viable strategy class, but not the highest-EV 48h path unless funding spikes or account/API readiness is already solved.

### Current Ranking

1. `MEASURE` - XMR/USDT KuCoin -> MEXC micro-edge.
2. `MEASURE` - Automatic market discovery with strict symbol-identity validation and depth sampling.
3. `LATER` - Spot-perp funding capture monitor.
4. `KILL` - Bitso same-venue MXN/USD/stablecoin immediate triangles.
5. `KILL` - Naive long-tail ticker arbitrage without asset identity verification.

### Sources / Public Endpoints Used

- Binance spot tickers: `https://api.binance.com/api/v3/ticker/24hr`
- Binance spot book ticker: `https://api.binance.com/api/v3/ticker/bookTicker`
- Binance USD-M premium/funding: `https://fapi.binance.com/fapi/v1/premiumIndex`
- Bybit spot tickers: `https://api.bybit.com/v5/market/tickers?category=spot`
- Bybit linear tickers/funding: `https://api.bybit.com/v5/market/tickers?category=linear`
- OKX spot tickers: `https://www.okx.com/api/v5/market/tickers?instType=SPOT`
- OKX funding: `https://www.okx.com/api/v5/public/funding-rate`
- Gate spot tickers: `https://api.gateio.ws/api/v4/spot/tickers`
- KuCoin all tickers: `https://api.kucoin.com/api/v1/market/allTickers`
- KuCoin XMR order book: `https://api.kucoin.com/api/v1/market/orderbook/level2_100?symbol=XMR-USDT`
- MEXC all tickers: `https://api.mexc.com/api/v3/ticker/24hr`
- MEXC XMR order book: `https://api.mexc.com/api/v3/depth?symbol=XMRUSDT&limit=100`
- Bitget spot tickers: `https://api.bitget.com/api/v2/spot/market/tickers`
- Crypto.com tickers: `https://api.crypto.com/exchange/v1/public/get-tickers`
- Bitso books/tickers: `https://api.bitso.com/v3/available_books/`, `https://api.bitso.com/v3/ticker/`

### Next Loop

Next hypothesis: validate whether the XMR edge is specific to KuCoin/MEXC or part of a broader privacy-coin fragmentation cluster (`XMR`, `ZEC`, `DASH`, if listed), then measure exact min order sizes and withdrawal/account constraints. If XMR is jurisdictionally blocked or min sizes/fees erase it, kill quickly and move to sane high-liquidity alternatives (`DYDX`, `MMT`) with asset-identity verification.

## Checkpoint - 2026-05-29 03:10 CST

### XMR Follow-Up Result

Longer sample on `XMR/USDT` KuCoin -> MEXC killed the direct route.

- Public metadata:
  - KuCoin `XMR-USDT`: trading enabled, base min size `0.001`, quote min size `1`, base increment `0.001`, price increment `0.01`.
  - MEXC `XMRUSDT`: spot trading allowed, base size precision `0.001`, quote amount precision `1`, full name `Monero`, taker commission `0.0005`.
- Persistence sample:
  - Window: 2026-05-29 02:57:52 to 03:09:12 CST.
  - Samples: 120, every 5 seconds, zero fetch errors.
  - 0.5 XMR bucket: 73/120 positive, positive ratio 60.8%, average +0.256 bps, min -10.633 bps, max +5.392 bps.
  - 1.0 XMR bucket: 66/120 positive, positive ratio 55.0%, average -0.648 bps.
  - 2.0 XMR bucket: 30/120 positive, positive ratio 25.0%, average -2.512 bps.
- Stop condition triggered: 0.5 XMR failed both thresholds: under 70% positive and under +2 bps average net.
- Verdict change: `MEASURE` -> `KILL` as a direct route.

### Updated Ranking

1. `MEASURE` - Suspicious `AI/USDT` Binance -> OKX identity/depth validation.
2. `MEASURE` - Automatic market discovery with strict symbol-identity validation.
3. `LATER` - Spot-perp funding capture monitor.
4. `KILL` - XMR/USDT KuCoin -> MEXC direct arbitrage.
5. `KILL` - Bitso same-venue MXN/USD/stablecoin immediate triangles.

### Next Loop

Validate `AI/USDT` identity and depth. If it is a ticker collision or disappears under depth, kill it and move to lower-spread candidates (`DYDX`, `MMT`) only after confirming asset identity.

## Checkpoint - 2026-05-29 03:13 CST

### AI/USDT Identity Result

`AI/USDT` Binance -> OKX is a ticker collision, not an arbitrage route.

- Binance official listing announcement identifies `AI` as Sleepless AI and says Binance opened `AI/USDT` trading on 2024-01-04.
- OKX official listing announcement identifies `AI/USDT` as Gensyn and says OKX opened spot trading on 2026-05-22.
- Public depth made the route look extremely profitable: Binance ask around `0.0284`, OKX bid around `0.03071`, and depth stayed positive into 25,000 USDT notional under naive math.
- But the assets are not the same. This is not executable arbitrage.
- Verdict change: `MEASURE` -> `KILL`.

Sources:

- Binance: `https://www.binance.com/en/support/announcement/detail/1c5f644e22b44e0f90404e0aea216525`
- OKX: `https://www.okx.com/help/okx-to-list-ai-usdt-gensyn-for-spot-trading`

### Updated Ranking

1. `MEASURE` - `DYDX/USDT` Binance -> OKX identity/depth validation.
2. `MEASURE` - Automatic market discovery with strict symbol-identity validation.
3. `LATER` - Spot-perp funding capture monitor.
4. `KILL` - AI/USDT Binance -> OKX due ticker collision.
5. `KILL` - XMR/USDT KuCoin -> MEXC direct arbitrage.

### Next Loop

Measure `DYDX/USDT` Binance -> OKX. It had a smaller but more plausible top-of-book signal in the filtered scan, so it deserves a quick depth and persistence check.

## Checkpoint - 2026-05-29 03:28 CST

### DYDX / MMT / IO Follow-Up

Refreshed discovery after the AI and XMR kills.

#### DYDX/USDT Binance -> OKX

- Metadata: Binance `DYDXUSDT` and OKX `DYDX-USDT` both live.
- Current depth: negative in both directions at 100 to 25,000 USDT buckets.
- Verdict: `KILL` for current direct route. The earlier ticker signal disappeared before depth validation.

#### MMT/USDT OKX -> Binance

- Metadata: Binance `MMTUSDT` and OKX `MMT-USDT` both live.
- Current depth: best direction was OKX buy -> Binance sell, but net was negative after 10 bps + 10 bps + 2 bps costs.
- At 100 USDT bucket: about -12.6 bps net.
- At 1,000 USDT bucket: about -14.3 bps net.
- Verdict: `KILL` for current direct route.

#### IO/USDT Binance -> Bybit

- Metadata: Binance `IOUSDT` and Bybit `IOUSDT` both live; Bybit metadata identifies base `IO`, quote `USDT`, min order amount `5`.
- Initial depth looked very strong:
  - 1,000 USDT: about +193 to +202 bps net.
  - 2,500 USDT: about +172 to +186 bps net.
  - 5,000 USDT: about +119 to +145 bps net.
  - 10,000 USDT: started positive, later failed as Bybit depth moved.
- Persistence sample:
  - Window: 2026-05-29 03:15:37 to 03:26:56 CST.
  - Samples: 120, every 5 seconds, zero fetch errors.
  - 1,000 USDT bucket: 48/120 positive, average +26.006 bps, median -9.491 bps, max +249.266 bps.
  - 2,500 USDT bucket: 34/120 positive, average +11.317 bps, median -19.860 bps.
  - 5,000 USDT bucket: 29/120 positive, average -10.704 bps.
  - 10,000 USDT bucket: 27/120 positive, average -54.457 bps.
- Interpretation: this was a real event window, not a stable standing route. The edge was huge for the first few minutes and then collapsed/inverted.
- Verdict: `MEASURE` for an event-window/new-listing dislocation detector. `KILL` as a manual/static route.

### Updated Ranking

1. `MEASURE` - Event-window cross-exchange altcoin dislocations, led by `IO/USDT` Binance -> Bybit evidence.
2. `MEASURE` - Automatic market discovery with asset identity + depth + persistence gates.
3. `LATER` - Spot-perp funding monitor.
4. `KILL` - DYDX/USDT current route.
5. `KILL` - MMT/USDT current route.

### Next Loop

Shift from standing-spread scouting to event-window detection:

- Look for other current high-gross routes from the refreshed scan: `ALLO`, `GENIUS`, `BSB`.
- For each, run the same identity -> depth -> persistence waterfall.
- Promote only the approach if multiple routes show short-lived windows; do not promote a single stale symbol.

## Checkpoint - 2026-05-29 03:32 CST

### ALLO / GENIUS Follow-Up

#### ALLO/USDT Gate -> Bitget

- Gate metadata identifies `ALLO_USDT` as Allora, tradable, min quote `3`, min base `1`.
- Gate metadata reports pair fee `0.2`, which is 20 bps and worse than the generic 10 bps assumption used in the first scan.
- Current depth was negative in both directions:
  - Gate buy -> Bitget sell: about -26.1 bps net at 100 USDT, worsening with size.
  - Bitget buy -> Gate sell: about -47.7 bps net at 100 USDT, worsening with size.
- Verdict: `KILL`.

#### GENIUS/USDT MEXC/Binance -> Bitget

- MEXC metadata identifies full name `Genius`, spot trading allowed, taker commission `0.0005`, contract address `0x1F12B85aAC097E43Aa1555b2881E98a51090e9A6`.
- Binance, MEXC, and Bitget books were all tight around `0.540`.
- Current depth was negative:
  - MEXC buy -> Bitget sell: about -20.9 bps net at 100 to 1,000 USDT.
  - Binance buy -> Bitget sell: about -28.1 bps net at 100 to 1,000 USDT.
- Verdict: `KILL`.

### Current Frontier

The strongest evidence so far is not a persistent route. It is the IO event-window pattern:

- A high, real-looking spread can exist for minutes.
- It can collapse before manual action.
- Positive average can be misleading if median and positive ratio are negative.
- Therefore the highest-EV build is an automated event detector with identity, depth, persistence, and notional-bucket gates.

### Next Loop

Continue with `BSB/USDT` and then refresh candidates again. If no new route survives, shift to specifying exact scanner gates from these failures.

## Checkpoint - 2026-05-29 03:35 CST

### BSB / SD / CTR / BDX Follow-Up

I tested the remaining refreshed candidates from the event-window scan. None survived live depth.

#### BSB/USDT Bitget -> Bybit

- Bybit metadata: base `BSB`, quote `USDT`, trading, min order amount `5`, tick size `0.0001`.
- Current best direction: Bitget buy -> Bybit sell.
- Depth result:
  - 50 USDT: about -21.6 bps net.
  - 100 USDT: about -22.3 bps net.
  - 1,000 USDT: about -32.8 bps net.
- Verdict: `KILL`.

#### SD/USDT OKX -> Bybit

- OKX metadata: `SD-USDT` live, min size `1`, tick size `0.0001`.
- Bybit metadata: `SDUSDT` trading, but `stTag=1`.
- Current depth was negative in both directions:
  - OKX buy -> Bybit sell: about -29.3 bps at 50 USDT.
  - Bybit buy -> OKX sell: about -96.9 bps at 50 USDT.
- Verdict: `KILL`.

#### CTR/USDT Gate -> MEXC

- Gate metadata: `CTR_USDT`, base name `Citrea`, tradable, fee `0.2`, min quote `3`.
- MEXC metadata: `CTRUSDT`, full name `Citrea`, spot trading allowed, taker commission `0.0005`, contract `0x11030f79109269d796fd0FB956D6244e502757f7`.
- Current depth was negative in both directions:
  - Gate buy -> MEXC sell: about -66.6 bps at 50 USDT.
  - MEXC buy -> Gate sell: about -36.3 bps at 50 USDT.
- Verdict: `KILL`.

#### BDX/USDT KuCoin -> MEXC

- KuCoin metadata: `BDX-USDT`, trading enabled, base min size `10`, fee category `3`.
- MEXC metadata: `BDXUSDT`, full name `Beldex`, taker commission `0.0005`.
- Current depth was negative in both directions:
  - KuCoin buy -> MEXC sell: about -48.3 bps at 50 USDT.
  - MEXC buy -> KuCoin sell: about -54.9 bps at 50 USDT.
- Verdict: `KILL`.

### Triangular Arbitrage Follow-Up

Measured liquid USDT/USDC triangles on Binance and OKX with public top-of-book:

- Binance bases: BTC, ETH, SOL, XRP, BNB, DOGE, ADA, LINK.
- OKX bases: BTC, ETH, SOL, XRP, LINK; DOGE request timed out once.
- Fee assumption: 10 bps taker per leg, 3 legs.
- Result: all measured cycles were negative after fees.
  - Binance examples: BTC about -29.4 / -30.7 bps depending direction; ETH about -29.2 / -30.9 bps; SOL about -30.1 / -32.4 bps.
  - OKX examples: BTC about -31.8 / -29.2 bps; ETH about -31.5 / -29.6 bps; SOL about -31.9 / -31.5 bps.
- Verdict: `KILL` for liquid taker triangular arbitrage.
- Keep as `LATER` only if maker/rebate logic is implemented; taker-only triangular is structurally fee-negative unless gross dislocation is unusually large.

### Fee Model Issue Found

The refreshed scan showed Crypto.com -> Bitfinex USD edges for XRP/SOL with about 12 bps gross. This is not actionable because `scripts/market_probe.py` currently assigns Bitfinex taker fee as `0.0` bps. Public Bitfinex fee sources are tier/account dependent and not safely represented by zero for this challenge. Until that fee assumption is fixed in the scanner, Crypto.com -> Bitfinex USD routes should be treated as `MEASURE_FEE_FIRST`, not profit candidates.

### Updated Ranking

1. `DO_NOW` - Build/require event-window detector gates: identity, real fees, top-100 depth, positive ratio, median net, and bucketed notional.
2. `MEASURE` - Re-run market discovery after correcting venue-specific fee assumptions, especially Bitfinex and Gate.
3. `MEASURE` - Watch IO-like new-listing/event dislocations; do not manually chase stale spread docs.
4. `LATER` - Maker/rebate triangular or maker/taker hybrid strategies.
5. `KILL` - Liquid taker-only triangular arbitrage.

### Next Loop

Shift to stablecoin/cross-lane basis with explicit fees and same-venue paths:

- Binance/OKX/Bybit USDT-USDC basis against BTC/ETH/SOL books already looks fee-negative as taker triangular.
- Next measure cross-exchange stablecoin routes and USD/USDT basis where public books exist, but require explicit lane conversion and fee haircuts.

## Checkpoint - 2026-05-29 03:40 CST

### Stablecoin/USD Basis Follow-Up

Measured cross-exchange stablecoin/USD basis using public order books. Normalization: price is USD received/paid for 1 stablecoin. This assumes pre-positioned inventory and does not rely on transfers.

#### USDT/USD

Venues sampled:

- Coinbase `USDT-USD`, fee assumption 120 bps taker.
- Bitstamp `usdtusd`, fee assumption 40 bps taker.
- Kraken `USDT/USD`, fee assumption 40 bps taker.
- Bitso `usd_usdt` inverted into USDT/USD, fee assumption 50 bps taker.

Top-of-book:

- Coinbase: bid `0.9986`, ask `0.99861`.
- Bitstamp: bid `0.99858`, ask `0.99859`.
- Kraken: bid `0.99854`, ask `0.99855`.
- Bitso inverted: bid about `0.998901`, ask about `0.999101`.

Best gross routes were still fee-negative:

- Kraken buy -> Bitso sell: about +3.5 bps gross, about -87.5 bps net.
- Bitstamp buy -> Bitso sell: about +3.1 bps gross, about -87.9 bps net.
- Kraken buy -> Bitstamp sell: about +0.3 bps gross, about -80.7 bps net.

Verdict: `KILL` for taker cross-exchange USDT/USD basis.

#### USDC/USD

Venues sampled:

- Bitstamp `usdcusd`, fee assumption 40 bps.
- Kraken `USDC/USD`, fee assumption 40 bps.
- Coinbase `USDC-USD` public book returned 404 on the exchange endpoint used.

Top-of-book:

- Bitstamp: bid `0.99955`, ask `0.99957`.
- Kraken: bid `0.9994`, ask `0.9995`.

Best gross route:

- Kraken buy -> Bitstamp sell: about +0.5 bps gross, about -80.5 bps net.

Verdict: `KILL` for taker cross-exchange USDC/USD basis.

### Updated Ranking

1. `DO_NOW` - Event-window detector/scanner gates; all manual static route candidates keep failing after depth/persistence.
2. `MEASURE` - Correct fee model in discovery before trusting rankings, especially Gate and Bitfinex.
3. `MEASURE` - Funding/basis monitor for perp dislocations only when funding materially exceeds entry basis + fees.
4. `LATER` - Maker/rebate stablecoin or triangular strategies.
5. `KILL` - Taker stablecoin/USD cross-exchange basis.

### Next Loop

Measure spot-perp basis again, but with a stricter rule: calculate breakeven funding intervals from current mark-index basis and not just raw funding rate. If no route clears fees within a short holding period, keep it `LATER`.

## Checkpoint - 2026-05-29 03:45 CST

### Spot-Perp Funding Breakeven Follow-Up

Re-measured Binance USD-M, Bybit linear, and OKX USDT swaps using public funding/mark/index endpoints. Assumption: positive funding means short perp receives funding. Conservative round-trip fee hurdle: 30 bps total for spot/perp open and close before borrow, margin, and operational costs.

Current market structure was unfavorable for quick funding capture:

- Perps were trading below index on every sampled route.
- That creates entry headwind for a short-perp / long-spot funding capture.
- Funding was positive but small, so payback horizons are far too long for a 48h profit sprint.

Sample breakeven results:

- Binance:
  - BTC: basis -4.478 bps, funding +0.382 bps/8h, breakeven about 90 intervals / 30.1 days.
  - ETH: basis -3.405 bps, funding +0.621 bps/8h, breakeven about 53.8 intervals / 17.9 days.
  - DOGE: basis -3.717 bps, funding +0.955 bps/8h, breakeven about 35.3 intervals / 11.8 days.
- Bybit:
  - ETH: basis -3.728 bps, funding +1.000 bps/8h, breakeven about 33.7 intervals / 11.2 days.
  - DOGE: basis -1.003 bps, funding +1.000 bps/8h, breakeven about 31.0 intervals / 10.3 days.
- OKX:
  - ETH: basis -5.268 bps, funding +0.691 bps/interval, breakeven about 51.1 intervals / 17.0 days assuming 8h.
  - DOGE: basis -5.014 bps, funding +0.883 bps/interval, breakeven about 39.7 intervals / 13.2 days.

Verdict:

- `KILL` as immediate challenge profit.
- `LATER` as a monitor: promote only when funding spikes enough to pay back entry basis and fees in a short, explicit horizon.

### Current Best Thesis

The route-by-route scout has now killed most obvious taker approaches. The highest-EV next move is not another hand-picked pair. It is to harden market discovery so the system automatically catches IO-like event windows and rejects the common traps:

- same-symbol/different-asset collisions,
- wrong fee assumptions,
- tiny top-of-book spreads,
- negative median despite positive average,
- and route decay before manual action.

### Next Loop

Turn the empirical failures into scanner gates/backlog inside Agent 2 docs, then run one more fresh discovery pass to see whether any new event-window candidate appears.

## Checkpoint - 2026-05-29 03:45 CST

### Maker/Rebate Follow-Up

The only current retail-access fee schedule found that materially changes the economics is Binance.US. Official Binance.US blog says spot fees are 0% maker and 0.02% taker for every user on Advanced Spot pairs, published 2026-04-22:

- Source: `https://blog.binance.us/zero-fee-trading/`

I measured Binance.US as a separate venue against Binance global, Bybit, and Kraken on liquid USDT pairs. Assumption for hybrid model:

- maker leg on Binance.US at current best bid/ask: 0 bps maker.
- taker leg on other venue: 10 bps for Binance global/Bybit, 40 bps for Kraken.
- latency/adverse-selection buffer: 2 bps.

Current results:

- BTC/USDT:
  - Binance.US maker buy -> Binance global taker sell: about -14.3 bps net.
  - Binance global taker buy -> Binance.US maker sell: about -9.3 bps net.
- ETH/USDT:
  - Binance.US maker buy -> Bybit taker sell: about -12.9 bps net.
  - Bybit taker buy -> Binance.US maker sell: about -9.7 bps net.
- SOL/USDT:
  - Binance.US maker buy -> Binance global/Bybit taker sell: about -12.0 bps net.
  - Binance global/Bybit taker buy -> Binance.US maker sell: about -9.6 bps net.
- XRP/USDT:
  - Best measured direction around -10.5 bps net.

Verdict:

- `KILL` for immediate major-asset maker/taker arbitrage.
- `MEASURE` for adding Binance.US to discovery because its fee schedule is structurally interesting for U.S.-available event windows.
- Do not assume maker fill. The maker side has queue risk and adverse selection; a spread must be much larger than the static calculation.

### CEX-DEX Measurability Follow-Up

Measured Ethereum WETH/USDC through ParaSwap public quotes and compared to Binance `ETHUSDC`.

Public quote source:

- `https://api.paraswap.io/prices/`

Result: measurable, but not profitable in current snapshot.

DEX sell WETH -> USDC versus Binance ETH/USDC bid:

- 0.1 WETH: about -22.1 bps net after Binance taker and gas.
- 1 WETH: about -14.6 bps net.
- 5 WETH: about -16.8 bps net.
- 10 WETH: about -17.6 bps net.

DEX buy WETH with USDC, then sell ETH on Binance:

- 1,000 USDC: about -8.4 bps net.
- 5,000 USDC: about -7.4 bps net.
- 10,000 USDC: about -8.4 bps net.

Verdict:

- `KILL` for current WETH/USDC CEX-DEX arbitrage.
- `MEASURE` for CEX-DEX monitor only if the scanner can pull aggregator quotes and gas estimates continuously.
- This is closer than most killed ideas, but still negative and operationally harder than CEX-only event-window detection.

### Updated Ranking

1. `DO_NOW` - Event-window detector with strict gates.
2. `MEASURE` - Add Binance.US as a U.S.-available low-fee venue candidate.
3. `MEASURE` - CEX-DEX quote monitor for WETH/USDC and maybe WBTC/USDC if public quote endpoints stay reliable.
4. `LATER` - Maker/rebate strategies requiring actual maker fill modeling.
5. `KILL` - Current major-asset maker/taker routes and WETH/USDC CEX-DEX route.

### Next Loop

Run one more hard-filter discovery pass. If empty again, focus Agent 2 output on a final prioritized approach: event-window detector + Binance.US low-fee expansion + CEX-DEX monitor as secondary.

## Checkpoint - 2026-05-29 03:47 CST

### Fresh Event-Window Pass

Ran another hard-filter discovery pass after the maker/CEX-DEX work.

Filters:

- Exclude known killed symbols.
- Require top-of-book net over 25 bps after generic fee model.
- Require 24h quote-volume proxy over 500,000.
- Require gross spread under 1,000 bps.
- Skip Bitfinex until fee model is fixed.

Result:

- Markets normalized: 10,240.
- Routes scanned: 2,125.
- Hard-filter candidates: 1.

Candidate: `HOOLI/USDT` KuCoin -> Gate.

Waterfall:

- KuCoin metadata: `HOOLI-USDT`, trading enabled, base min size `10`, fee category `2`.
- Gate metadata: `HOOLI_USDT`, base name `My Pet Hooligan`, tradable, fee `0.2`, min quote `3`.
- Identity: likely aligned enough for measurement.
- Depth:
  - KuCoin buy -> Gate sell:
    - 25 USDT: about +15.0 bps gross, but -17.0 bps net after KuCoin 10 bps, Gate 20 bps, and latency.
    - 100 USDT: about -39.1 bps net.
    - 500 USDT: about -116.9 bps net.
  - Reverse direction was worse.
- Verdict: `KILL`.

Interpretation:

- The hard filter still lets through Gate routes when the generic model understates Gate's 20 bps fee.
- Fee metadata must be loaded before hard-filter ranking, not after.

### Updated Ranking

1. `DO_NOW` - Event-window detector with fee-aware hard filter.
2. `MEASURE` - Binance.US public adapter as a low-fee U.S. venue.
3. `MEASURE` - CEX-DEX quote monitor, starting with WETH/USDC.
4. `MEASURE` - Fix discovery fee model for Gate and Bitfinex before trusting candidate ranking.
5. `KILL` - New `HOOLI/USDT` direct route.

### Next Loop

If continuing, stop probing Gate routes until the market discovery script uses Gate's per-pair `fee` metadata. Next high-EV research is either:

- identify non-Gate event-window candidates from a fee-aware scan, or
- specify the exact fee-aware scanner change in Agent 2 docs for the main implementation queue to consume later without editing primary-agent deliverables.

## Checkpoint - 2026-05-29 03:50 CST

### Fresh Discovery With Harder Gates

Ran a fresh market discovery after all route kills, then applied stricter pre-depth filters:

- Exclude known killed symbols/routes from this Agent 2 session.
- Require `net_bps > 25` on top-of-book after generic fee model.
- Require `depth_proxy_24h_quote > 500,000`.
- Require sane gross spread under 1,000 bps.
- Skip Bitfinex routes until the taker fee assumption is fixed.

Result:

- Markets normalized: 10,240.
- Routes scanned: 2,003.
- Fetch errors: none.
- New hard-filter candidates: 0.

Interpretation:

- The current public market snapshot does not have a fresh candidate worth depth-probing under conservative filters.
- The scout's useful output is now the kill list and the scanner gate design, not another manual pair name.

### Scanner Gates To Promote

Any future discovery/ranking module should enforce these gates before a route appears as actionable:

1. Asset identity gate.
   - Same symbol is insufficient.
   - Need official metadata, full name, contract address where applicable, or curated identity mapping.

2. Venue-specific fee gate.
   - No zero-fee placeholders.
   - Gate and Bitfinex false positives show generic fee assumptions are dangerous.

3. Depth bucket gate.
   - Rank by net bps at concrete notionals, not top-of-book.
   - Minimum buckets: 100, 500, 1,000, 2,500, 5,000, 10,000 USDT/USD depending venue.

4. Persistence gate.
   - Track positive ratio, median net bps, average net bps, min/max, and decay time.
   - IO showed average net can stay positive after the median turns negative.

5. Execution-readiness gate.
   - Needs pre-positioned quote on buy venue and base inventory on sell venue.
   - Routes requiring new deposits/withdrawals during the window are not hot-path arbitrage.

6. Lane separation gate.
   - USD, USDT, USDC, and MXN remain separate unless an explicit conversion module computes fees, FX/basis, and haircut.

### Next Loop

Continue monitoring for fresh event-window candidates. If the next hard-filter pass is also empty, expand beyond spot taker routes into maker/rebate requirements and CEX-DEX measurability without touching non-Agent 2 files.

## Checkpoint - 2026-05-29 03:56 CST

### Fee-Aware Discovery Follow-Up

Ran a fee-aware discovery pass without editing code. Conservative taker assumptions used:

- Binance/Bybit/OKX/KuCoin/Bitget: 10 bps.
- MEXC: 5 bps.
- Gate: 20 bps from pair metadata pattern.
- Bitfinex: 20 bps conservative placeholder instead of the unsafe `0.0`.
- Crypto.com: 50 bps conservative placeholder until official tier is modeled.
- Coinbase/Gemini/Kraken/Bitstamp/Bitso: existing conservative defaults.

Result:

- Markets normalized: 10,240.
- Routes scanned: 1,910.
- Fetch errors: none.
- Hard-filter candidates with `net_bps > 25`, `depth_proxy > 500k`, sane gross spread, excluding previous kills: 0.
- Lower-liquidity positive candidates existed; the strongest was `ULTIMA/USDT`.

### ULTIMA/USDT Discovery

Candidate: buy `ULTIMAUSDT` on MEXC, sell `ULTIMA-USDT` on KuCoin.

Public metadata:

- MEXC:
  - symbol `ULTIMAUSDT`, full name `ULTIMA`, spot trading allowed.
  - taker commission `0.0005`.
  - contract address `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.
- KuCoin:
  - symbol `ULTIMA-USDT`, full name `Ultima`, trading enabled.
  - fee category `3`, base min size `0.0001`.
  - public currency endpoint shows only BEP20 chain enabled for deposits/withdrawals, contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
- Gate:
  - `ULTIMA_USDT`, base name `Ultima`, tradable.
  - chain `SMART`, address `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.

Important risk:

- MEXC/Gate point to `sWd6...` on SMART.
- KuCoin points to BEP20 `0x5668...`.
- This may still represent the same bridged asset, but direct exchange-to-exchange rebalance may not be available or may require an external bridge.
- Therefore this is a scanner/watchlist candidate, not permission to trade.

Depth and persistence:

- Initial depth MEXC buy -> KuCoin sell was strongly positive from 100 to 10,000 USDT.
- 5-minute persistence sample:
  - Window: 2026-05-29 03:50:26 to 03:56:04 CST.
  - Samples: 60, every 5 seconds, zero fetch errors.
  - 500 USDT bucket: 60/60 positive, avg +451.956 bps, median +465.831 bps.
  - 1,000 USDT bucket: 60/60 positive, avg +416.428 bps, median +425.642 bps.
  - 2,500 USDT bucket: 60/60 positive, avg +345.644 bps, median +363.751 bps.
  - 5,000 USDT bucket: 60/60 positive, avg +233.093 bps, median +256.832 bps.
  - 10,000 USDT bucket: 55/60 positive, avg +86.428 bps, median +118.780 bps, min -164.927 bps.

Verdict:

- `DO_NOW` for scanner/watchlist and operational due diligence.
- Do not execute until identity, chain compatibility, deposits/withdrawals, account availability, and inventory placement are verified.

### Updated Ranking

1. `DO_NOW` - Add `ULTIMA/USDT` MEXC -> KuCoin to high-priority scanner/watchlist with chain/rebalance warning.
2. `DO_NOW` - Event-window detector with fee-aware hard filter.
3. `MEASURE` - Verify ULTIMA identity and transfer/rebalance path across MEXC, KuCoin, and possibly Gate.
4. `MEASURE` - Binance.US public adapter as low-fee venue expansion.
5. `MEASURE` - CEX-DEX WETH/USDC monitor.

### Next Loop

Continue with ULTIMA operational risk:

- verify whether MEXC deposits/withdrawals support the same chain as KuCoin or a bridgeable path,
- watch ULTIMA persistence for another window,
- and search for other non-Gate, fee-aware lower-liquidity candidates if ULTIMA remains the only survivor.

## Checkpoint - 2026-05-29 04:10 CST

### ULTIMA Second Persistence Window

Re-ran ULTIMA persistence after the initial discovery window.

Route: buy `ULTIMAUSDT` on MEXC, sell `ULTIMA-USDT` on KuCoin.  
Fees: MEXC taker 5 bps, KuCoin taker 10 bps, latency haircut 2 bps.

Window:

- Started: 2026-05-29 04:04:04 CST.
- Ended: 2026-05-29 04:09:43 CST.
- Samples: 60, every 5 seconds.
- Fetch errors: 0.

Results:

- 500 USDT bucket: 60/60 positive, avg +486.528 bps, median +487.312 bps, min +438.750 bps.
- 1,000 USDT bucket: 60/60 positive, avg +447.664 bps, median +451.215 bps, min +408.457 bps.
- 2,500 USDT bucket: 60/60 positive, avg +374.618 bps, median +388.598 bps, min +291.865 bps.
- 5,000 USDT bucket: 60/60 positive, avg +252.130 bps, median +285.889 bps, min +29.119 bps.
- 10,000 USDT bucket: 50/60 positive, avg +55.034 bps, median +83.984 bps, min -159.393 bps.

Interpretation:

- This is no longer a one-window anomaly. ULTIMA stayed positive across two separate 60-sample windows.
- The practical initial cap should be 5,000 USDT, not 10,000 USDT. The 10,000 bucket is too unstable.
- The real blocker is operational: inventory and chain compatibility, not public-book edge.

### ULTIMA Chain/Rebalance Evidence

Public endpoint evidence:

- KuCoin `api/v3/currencies/ULTIMA`:
  - deposits enabled, withdrawals enabled.
  - chain `BEP20` / `bsc`.
  - contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
  - withdrawal min fee `0.0002` ULTIMA.
- Gate `spot/currencies/ULTIMA` and `wallet/currency_chains?currency=ULTIMA`:
  - deposits enabled, withdrawals enabled.
  - chain `SMART`.
  - contract/address `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.
- MEXC public exchangeInfo:
  - contract address `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.
  - public deposit/withdraw status was not verified; MEXC capital config endpoint is not available without signed/private access in this run.

Endpoint URLs:

- `https://api.kucoin.com/api/v3/currencies/ULTIMA`
- `https://api.gateio.ws/api/v4/spot/currencies/ULTIMA`
- `https://api.gateio.ws/api/v4/wallet/currency_chains?currency=ULTIMA`
- `https://api.mexc.com/api/v3/exchangeInfo?symbol=ULTIMAUSDT`

Public web evidence:

- Third-party BNB-chain token pages identify `0x5668a83b46016b494a30dd14066a451e5417a8b8` as ULTIMA on BNB Smart Chain.
- Smart explorer references identify `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi` as a SMART-chain ULTIMA token.
- Official/public Ultima material discusses Smart Blockchain and also references future cross-chain bridge work; this does not prove immediate bridgeability for the MEXC -> KuCoin rebalance path.

Reference URLs:

- `https://tradingstrategy.ai/trading-view/binance/tokens/0x5668a83b46016b494a30dd14066a451e5417a8b8`
- `https://smartexplorer.com/token20/sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`
- `https://blog.ultima.io/smart-blockchain-comparison-with-popular-blockchains/`
- `https://ultima.io/documents/de/WhitePaperUT.pdf`

Conclusion:

- Treat MEXC/Gate SMART ULTIMA and KuCoin BEP20 ULTIMA as economically related but operationally non-fungible until proven otherwise.
- Hot-path arbitrage is only executable with pre-positioned inventory: USDT on MEXC and ULTIMA already on KuCoin.
- Post-trade rebalance must be solved separately. Do not assume direct transfer from MEXC to KuCoin.

### Updated Ranking

1. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, capped initially at 5,000 USDT notional.
2. `DO_NOW` - ULTIMA operational due diligence: account availability, deposits/withdrawals, chain bridge/rebalance, and inventory plan.
3. `DO_NOW` - Event-window detector with fee-aware hard filter.
4. `MEASURE` - Binance.US low-fee venue expansion.
5. `MEASURE` - CEX-DEX WETH/USDC monitor.

### Next Loop

Run a third, shorter ULTIMA watch check later and continue searching for non-Gate fee-aware candidates. If ULTIMA persists, Agent 2 should refine an execution-readiness checklist rather than keep looking for weaker routes.

## Checkpoint - 2026-05-29 04:19 CST

### ULTIMA Third Watch Check

Ran a shorter third watch window for `ULTIMA/USDT` MEXC -> KuCoin.

Window:

- Started: 2026-05-29 04:12:45 CST.
- Ended: 2026-05-29 04:15:31 CST.
- Samples: 30, every 5 seconds.
- Fetch errors: 0.

Results:

- 500 USDT bucket: 30/30 positive, avg +500.435 bps, median +506.497 bps, min +420.179 bps.
- 1,000 USDT bucket: 30/30 positive, avg +453.603 bps, median +456.182 bps, min +391.756 bps.
- 2,500 USDT bucket: 30/30 positive, avg +357.452 bps, median +375.624 bps, min +249.431 bps.
- 5,000 USDT bucket: 30/30 positive, avg +233.694 bps, median +251.710 bps, min +146.929 bps.
- 10,000 USDT bucket: 22/30 positive, avg +67.667 bps, median +110.582 bps, min -87.046 bps.

Interpretation:

- ULTIMA has now survived three independent watch windows.
- 5,000 USDT remains the right initial cap; 10,000 USDT remains too unstable.
- This should be the primary Agent 2 route for scanner/watchlist implementation and operational due diligence.

### Fee-Aware Non-Gate Scan

Ran a fee-aware scan excluding prior killed symbols, Gate, and Bitfinex.

Filters:

- net top-of-book > 15 bps.
- 24h quote-volume proxy > 100,000.
- sane gross spread under 1,000 bps.

Candidates found:

- `WALLI/USDT` KuCoin -> MEXC.
- `ASSET/USDT` KuCoin -> MEXC.
- `DEUS/USDT` KuCoin -> MEXC.
- `EUL/USDT` Binance -> KuCoin.
- `GOMINING/USDT` Bitget -> MEXC.
- `CPOOL/USDT` Bybit -> KuCoin.
- `DAG/USDT` MEXC -> KuCoin.

I probed the strongest non-Gate candidate, `WALLI/USDT`.

### WALLI/USDT Follow-Up

Route: buy `WALLI-USDT` on KuCoin, sell `WALLIUSDT` on MEXC.

Public metadata:

- KuCoin `WALLI-USDT`: trading enabled, fee category `3`, base min size `10`.
- MEXC `WALLIUSDT`: full name `Wallitelli`, spot trading allowed, taker commission `0.0005`, contract `0xc6A031fd206C72c614dB391590F48a5Ed9B2f9dC`.

Initial depth:

- 50 USDT bucket: about +126.6 bps net.
- 100 USDT bucket: about +121.6 bps net.
- 250 USDT bucket: about +111.9 bps net.
- 500 USDT bucket: about +47.7 bps net.
- 1,000 USDT bucket: negative.

Persistence:

- Window: 2026-05-29 04:16:19 to 04:19:04 CST.
- Samples: 30, every 5 seconds.
- 50 USDT bucket: 6/30 positive, avg -68.821 bps, median -70.923 bps.
- 100 USDT bucket: 3/30 positive, avg -151.935 bps.
- 250 USDT bucket: 3/30 positive, avg -325.849 bps.
- 500 USDT bucket: 0/30 positive, avg -549.741 bps.

Verdict: `KILL` as a direct route. The initial spread collapsed too quickly and did not survive persistence.

### Updated Ranking

1. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, cap at 5,000 USDT.
2. `DO_NOW` - ULTIMA operational due diligence: account access, inventory, chain/rebalance.
3. `DO_NOW` - Fee-aware event-window detector.
4. `MEASURE` - Continue non-Gate fee-aware scans, but require persistence before promotion.
5. `KILL` - WALLI direct route.

### Next Loop

Probe the next non-Gate candidate only if it has enough public liquidity and no obvious identity problem. Current queue: `ASSET`, `DEUS`, `EUL`, `GOMINING`, `CPOOL`, `DAG`. Keep ULTIMA as the main actionable watch route.

## Checkpoint - 2026-05-29 04:23 CST

### ASSET / WALLI Follow-Up

Continued probing the fee-aware non-Gate queue after ULTIMA.

#### WALLI/USDT KuCoin -> MEXC

- KuCoin metadata: `WALLI-USDT`, trading enabled, fee category `3`.
- MEXC metadata: `WALLIUSDT`, full name `Wallitelli`, spot trading allowed, taker commission `0.0005`, contract `0xc6A031fd206C72c614dB391590F48a5Ed9B2f9dC`.
- Initial depth was positive up to about 500 USDT, then negative at 1,000 USDT.
- Persistence window:
  - 2026-05-29 04:16:19 to 04:19:04 CST.
  - 30 samples, zero fetch errors.
  - 50 USDT: 6/30 positive, avg -68.821 bps, median -70.923 bps.
  - 100 USDT: 3/30 positive, avg -151.935 bps.
  - 250 USDT: 3/30 positive, avg -325.849 bps.
  - 500 USDT: 0/30 positive, avg -549.741 bps.
- Verdict: `KILL`.

#### ASSET/USDT KuCoin -> MEXC

- KuCoin metadata: `ASSET-USDT`, trading enabled, fee category `3`.
- MEXC metadata: `ASSETUSDT`, full name `REAL`, spot trading allowed, taker commission `0.0005`, contract `0x99E980265Bf36516C442be982df1772a6cCb3233`.
- Initial depth:
  - 50 USDT: about +52.7 bps net.
  - 100 USDT: about +33.0 bps net.
  - 250 USDT and above: negative.
- Persistence window:
  - 2026-05-29 04:20:56 to 04:22:45 CST.
  - 20 samples, zero fetch errors.
  - 50 USDT: 20/20 positive, avg +59.418 bps, median +52.761 bps.
  - 100 USDT: 20/20 positive, avg +38.393 bps, median +33.025 bps.
  - 250 USDT: 2/20 positive, avg -21.009 bps.
- Verdict: `LATER` as a micro-route/regression case; `KILL` as an execution priority. The notional is too small to matter and likely not worth operational complexity.

### Current Frontier

- ULTIMA is still the only route found by Agent 2 with meaningful size and persistence.
- ASSET proves there are small persistent micro-spreads, but the notional ceiling is too low.
- WALLI proves that top-of-book event windows can decay within minutes.

### Updated Ranking

1. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, cap at 5,000 USDT.
2. `DO_NOW` - ULTIMA execution-readiness checklist, especially chain/rebalance.
3. `DO_NOW` - Fee-aware event-window detector.
4. `LATER` - ASSET micro-route regression case.
5. `KILL` - WALLI direct route.

### Next Loop

Continue down the non-Gate queue only if time allows: `DEUS`, `EUL`, `GOMINING`, `CPOOL`, `DAG`. Do not let those distract from ULTIMA operational diligence, because ULTIMA is the only route with meaningful observed notional.

## Checkpoint - 2026-05-29 04:24 CST

### DEUS/USDT Follow-Up

Probed the next non-Gate candidate from the queue.

Route tested: KuCoin `DEUS-USDT` <-> MEXC `DEUSUSDT`.

Metadata:

- KuCoin: `DEUS-USDT`, trading enabled, fee category `3`.
- MEXC: `DEUSUSDT`, spot trading allowed, taker commission `0.0005`, contract `0x940A319B75861014A220D9c6c144d108552B089B`, full name `XMAQUINA`.

Identity risk:

- Symbol match is not sufficient. MEXC full name `XMAQUINA` does not match the `DEUS` branding implied by KuCoin symbol.
- This alone makes it unsafe to promote without deeper identity mapping.

Depth:

- KuCoin buy -> MEXC sell:
  - 50 USDT: about -117.5 bps net.
  - 100 USDT: about -131.1 bps net.
  - Larger buckets worsen quickly.
- MEXC buy -> KuCoin sell:
  - 50 USDT: about -110.4 bps net.
  - 100 USDT: about -112.6 bps net.
  - Larger buckets worsen quickly.

Verdict: `KILL`.

### Updated Ranking

1. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, cap at 5,000 USDT.
2. `DO_NOW` - ULTIMA execution-readiness checklist.
3. `DO_NOW` - Fee-aware event-window detector.
4. `LATER` - ASSET micro-route regression case.
5. `KILL` - DEUS direct route.

### Next Loop

Remaining non-Gate queue: `EUL`, `GOMINING`, `CPOOL`, `DAG`. Continue only if ULTIMA operational diligence is not being neglected.

## Checkpoint - 2026-05-29 04:34 CST

### Remaining Non-Gate Queue Follow-Up

Finished the remaining fee-aware non-Gate queue from the prior scan: `EUL`, `GOMINING`, `CPOOL`, and `DAG`.

#### EUL/USDT Binance <-> KuCoin

- Binance metadata: `EULUSDT`, status `TRADING`, spot trading allowed.
- KuCoin metadata: `EUL-USDT`, trading enabled, fee category `1`; currency endpoint identifies full name `Euler`, ERC20 contract `0xd9fcd98c322942075a5c3860693e9f4f03aae07b`, deposits/withdrawals enabled.
- Binance buy -> KuCoin sell:
  - 50 USDT: about -38.7 bps net.
  - 1,000 USDT: about -60.2 bps net.
- KuCoin buy -> Binance sell:
  - 50 USDT: about -32.0 bps net.
  - 1,000 USDT: about -65.9 bps net.
- Verdict: `KILL`.

#### GOMINING/USDT Bitget -> MEXC

- Bitget metadata: `GOMININGUSDT`, status `online`, taker fee `0.001`.
- MEXC metadata: `GOMININGUSDT`, full name `GoMining`, spot trading allowed, taker commission `0.0005`, contract `0x7Ddc52c4De30e94Be3A6A0A2b259b2850f421989`.
- Initial depth was positive only at small size:
  - 50 USDT: about +36.9 bps net.
  - 100 USDT: about +34.6 bps net.
  - 250 USDT: about +24.3 bps net.
  - 500 USDT: about -6.5 bps net.
- Persistence window:
  - 2026-05-29 04:27:43 to 04:29:33 CST.
  - 20 samples, zero fetch errors.
  - 50 USDT: 20/20 positive, avg +36.898 bps, median +36.898 bps.
  - 100 USDT: 20/20 positive, avg +34.570 bps, median +34.570 bps.
  - 250 USDT: 20/20 positive, avg +25.229 bps, median +25.531 bps.
  - 500 USDT: 0/20 positive, avg -5.006 bps, median -4.334 bps.
- Verdict: `LATER` as a micro-route/regression case; `KILL` as an execution priority. The notional ceiling is too low.

#### CPOOL/USDT Bybit <-> KuCoin

- Bybit metadata: `CPOOLUSDT`, status `Trading`, `stTag=0`, min order amount 5 USDT.
- KuCoin metadata: `CPOOL-USDT`, trading enabled, fee category `2`; currency endpoint identifies full name `Clearpool`, ERC20 contract `0x66761fa41377003622aee3c7675fc7b5c1c2fac5`, deposits/withdrawals enabled.
- Bybit buy -> KuCoin sell:
  - 50 USDT: about -34.4 bps net.
  - 100 USDT: about -51.9 bps net.
- KuCoin buy -> Bybit sell:
  - 50 USDT: about -95.1 bps net.
  - 100 USDT: about -97.9 bps net.
- Verdict: `KILL`.

#### DAG/USDT MEXC <-> KuCoin

- MEXC metadata: `DAGUSDT`, full name `Constellation`, taker commission `0.0005`, but `isSpotTradingAllowed=false`.
- KuCoin metadata: `DAG-USDT`, trading enabled, fee category `3`; currency endpoint identifies full name `Constellation`, native `DAG` chain deposits/withdrawals enabled.
- MEXC buy -> KuCoin sell:
  - 50 USDT: about -310.0 bps net.
  - 100 USDT: about -339.4 bps net.
- KuCoin buy -> MEXC sell:
  - 50 USDT: about -161.7 bps net.
  - 100 USDT: about -175.2 bps net.
- Verdict: `KILL`.

### ULTIMA Fourth Watch Window

Re-ran the only meaningful-size route: buy MEXC `ULTIMAUSDT`, sell KuCoin `ULTIMA-USDT`.

Persistence:

- Window: 2026-05-29 04:31:05 to 04:33:52 CST.
- Samples: 30, every 5 seconds.
- Errors: 0.
- 500 USDT: 30/30 positive, avg +499.267 bps, median +501.947 bps.
- 1,000 USDT: 30/30 positive, avg +450.103 bps, median +448.878 bps.
- 2,500 USDT: 30/30 positive, avg +367.551 bps, median +362.409 bps.
- 5,000 USDT: 30/30 positive, avg +239.005 bps, median +230.190 bps.
- 10,000 USDT: 30/30 positive, avg +120.181 bps, median +119.440 bps, min +22.537 bps.

Staleness notes:

- KuCoin level2 endpoint exposes a book timestamp, but raw local age averaged about -159 ms, which indicates local clock skew rather than a reliable absolute age.
- MEXC public depth response did not expose an exchange timestamp.
- Measured REST round-trip time: MEXC avg about 398 ms, max about 827 ms; KuCoin avg about 315 ms, max about 389 ms.

Verdict: keep `ULTIMA/USDT` as the only `DO_NOW` route from Agent 2. Even though the 10,000 USDT bucket was positive in this window, keep the initial execution/watch cap at 5,000 USDT until chain/rebalance and inventory feasibility are proven.

### Updated Ranking

1. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
2. `DO_NOW` - ULTIMA operational due diligence: MEXC withdrawal path, SMART/BEP20 bridge/rebalance, pre-positioned KuCoin inventory.
3. `DO_NOW` - Fee-aware event-window detector with identity, depth, persistence, and staleness/RTT fields.
4. `LATER` - ASSET and GOMINING micro-route regression cases.
5. `KILL` - EUL, CPOOL, DAG, and GOMINING as execution-priority routes.

### Next Loop

The prior non-Gate queue is exhausted. Next highest-leverage work is not another hand-picked ticker; it is either ULTIMA operational feasibility or a fresh fee-aware discovery pass with the corrected Gate/Bitfinex/KuCoin fee logic.

## Checkpoint - 2026-05-29 04:44 CST

### Fresh Fee-Aware Discovery Pass

Ran a fresh public discovery pass with corrected fee handling:

- Markets fetched: 10,216.
- Gross-positive same-lane routes: 2,052.
- Metadata loaded:
  - Gate pair fee rows: 2,209.
  - KuCoin symbols/fee categories: 987.
  - MEXC symbol/trading flags: 2,476.
  - Bitget symbols/fees: 661.
- Candidate filter: net bps > 25, 24h quote depth proxy >= 50,000, gross bps <= 1,200, Gate/MEXC/Bitget venue-specific fees, Bitfinex conservative 20 bps.

Top new ticker-level signal was `VANRY/USDT`, with MEXC materially below Binance and KuCoin. This survived live depth validation, so it became the next measured route.

### VANRY/USDT MEXC -> Binance / KuCoin

Metadata:

- MEXC: `VANRYUSDT`, spot trading allowed, taker commission `0.0005`, full name `VANRY`, contract `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`.
- Binance: `VANRYUSDT`, status `TRADING`, spot trading allowed. Binance public web asset metadata identifies `VANRY` as `Vanar`, trading enabled, old asset code `TVK`.
- KuCoin: `VANRY-USDT`, trading enabled, fee category `3`; currency endpoint identifies ERC20 contract `0x8de5b80a0c1b02fe4976851d030b36122dbb8624`, deposits/withdrawals enabled.

Initial depth:

- MEXC buy -> Binance sell:
  - 500 USDT: about +981.8 bps net.
  - 5,000 USDT: about +518.5 bps net.
  - 10,000 USDT: about +199.7 bps net.
- MEXC buy -> KuCoin sell:
  - 500 USDT: about +964.3 bps net.
  - 5,000 USDT: about +234.8 bps net.
  - 10,000 USDT: about -535.2 bps net.

Persistence:

- Window: 2026-05-29 04:40:29 to 04:43:25 CST.
- Samples: 30, every 5 seconds.
- Errors: 0.

MEXC -> Binance:

- 500 USDT: 30/30 positive, avg +931.414 bps, median +940.516 bps.
- 1,000 USDT: 30/30 positive, avg +902.229 bps, median +921.145 bps.
- 2,500 USDT: 30/30 positive, avg +779.459 bps, median +774.371 bps.
- 5,000 USDT: 30/30 positive, avg +550.565 bps, median +524.167 bps.
- 10,000 USDT: 30/30 positive, avg +231.097 bps, median +219.586 bps, min +62.701 bps.

MEXC -> KuCoin:

- 500 USDT: 30/30 positive, avg +902.519 bps, median +909.209 bps.
- 1,000 USDT: 30/30 positive, avg +833.806 bps, median +846.317 bps.
- 2,500 USDT: 30/30 positive, avg +607.842 bps, median +602.230 bps.
- 5,000 USDT: 30/30 positive, avg +255.435 bps, median +238.322 bps, min +49.297 bps.
- 10,000 USDT: 0/30 positive, avg -533.208 bps.

Verdict: `DO_NOW` for scanner/watchlist and operational due diligence. This is now the strongest Agent 2 public-book route by measured net bps and notional. No live trading: hot-path execution requires USDT on MEXC and pre-positioned VANRY inventory on Binance or KuCoin; repeated execution requires verified withdrawal/deposit/rebalance paths. Initial watch caps: 10,000 USDT for MEXC -> Binance, 5,000 USDT for MEXC -> KuCoin.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance scanner/watchlist, initial cap 10,000 USDT.
2. `DO_NOW` - VANRY MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
3. `DO_NOW` - VANRY operational due diligence: Binance network/deposit support, MEXC withdrawal status, inventory on sell venue.
4. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
5. `DO_NOW` - Fee-aware event-window detector with venue-specific fees, identity, depth, persistence, and staleness/RTT fields.

### Next Loop

Do not let weaker fresh-scan candidates distract from VANRY and ULTIMA. If continuing discovery, probe the next fresh candidates one at a time: `HOOLI` MEXC -> Bitget, `GUA` MEXC -> Gate, `QAIT` MEXC/KuCoin -> Gate, and `BTR` MEXC/Gate -> Bitget. Each must pass identity, live depth, and persistence before promotion.

## Checkpoint - 2026-05-29 04:49 CST

### HOOLI/USDT MEXC -> Bitget Follow-Up

Probed the next fresh-scan candidate after VANRY.

Metadata:

- MEXC: `HOOLIUSDT`, spot trading allowed, taker commission `0.0005`, full name `Hooli`, contract `FPJfY8mMTRwaePD2f46TFLqVov4X9svBaUgR1a8oTwTF`.
- Bitget: `HOOLIUSDT`, status `online`, taker fee `0.001`, quote `USDT`.

Initial depth:

- MEXC buy -> Bitget sell:
  - 50 USDT: about +1,278.4 bps net.
  - 250 USDT: about +921.3 bps net.
  - 500 USDT: about +527.5 bps net.
  - 1,000 USDT: about -751.0 bps net.
- Reverse route was deeply negative.

Persistence:

- Window: 2026-05-29 04:46:33 to 04:48:22 CST.
- Samples: 20, every 5 seconds.
- Errors: 0.
- 50 USDT: 20/20 positive, avg +1,193.131 bps, median +1,167.908 bps.
- 100 USDT: 20/20 positive, avg +1,032.435 bps, median +1,017.266 bps.
- 250 USDT: 20/20 positive, avg +903.585 bps, median +897.422 bps.
- 500 USDT: 20/20 positive, avg +501.616 bps, median +494.602 bps.
- 1,000 USDT: 0/20 positive, avg -784.990 bps.

Verdict: `MEASURE` as a capped micro-route, not a top execution priority. Initial cap: 500 USDT. It is materially stronger than ASSET/GOMINING on bps, but the hard break at 1,000 USDT means it should not distract from VANRY or ULTIMA.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance scanner/watchlist, initial cap 10,000 USDT.
2. `DO_NOW` - VANRY MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
3. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
4. `MEASURE` - HOOLI MEXC -> Bitget capped at 500 USDT.
5. `DO_NOW` - Operational due diligence for VANRY and ULTIMA before any live assumptions.

### Next Loop

Continue fresh queue only after preserving focus on VANRY/ULTIMA. Next candidates: `GUA` MEXC -> Gate, then `QAIT` MEXC/KuCoin -> Gate, then `BTR` MEXC/Gate -> Bitget.

## Checkpoint - 2026-05-29 04:51 CST

### GUA/USDT MEXC -> Gate Follow-Up

Probed the next fresh-scan candidate.

Metadata:

- MEXC: `GUAUSDT`, spot trading allowed, taker commission `0.0005`, full name `SUPERFORTUNE`, contract `0xA5C8e1513B6A08334b479fe4D71F1253259469BE`.
- Gate pair: `GUA_USDT`, trade status `tradable`, pair fee `0.2` = 20 bps, min quote amount 3 USDT.
- Gate currency endpoint: name `SUPERFORTUNE`, BSC contract `0xa5c8e1513b6a08334b479fe4d71f1253259469be`, withdrawals enabled, deposits disabled.

Depth:

- MEXC buy -> Gate sell:
  - 50 USDT: about +738.2 bps net.
  - 500 USDT: about +710.4 bps net.
  - 1,000 USDT: about +685.3 bps net.
  - 2,500 USDT: about +412.7 bps net.
  - 5,000 USDT: about -145.5 bps net.
- Gate buy -> MEXC sell was deeply negative.

Verdict: `KILL` for the current executable route despite positive depth. Gate deposits are disabled, so there is no clean way to pre-position or replenish GUA inventory on the sell venue. Revisit only if Gate deposits reopen and the route still survives depth/persistence.

### Next Loop

Continue fresh queue with `QAIT` MEXC/KuCoin -> Gate, then `BTR` MEXC/Gate -> Bitget.

## Checkpoint - 2026-05-29 04:55 CST

### QAIT/USDT MEXC/KuCoin -> Gate Follow-Up

Probed `QAIT` from the fresh queue.

Metadata:

- MEXC: `QAITUSDT`, spot trading allowed, taker commission `0.0005`, contract `0x4d41A5d412f4Ef44A35b9f53b06DB65edE249493`.
- KuCoin: `QAIT-USDT`, trading enabled, fee category `3`; BEP20 contract matches MEXC case-insensitively; deposits enabled, withdrawals disabled.
- Gate: `QAIT_USDT`, tradable, pair fee `0.2` = 20 bps; BSC contract matches; deposits enabled, withdrawals disabled.

Depth:

- MEXC buy -> Gate sell:
  - 50 USDT: about +426.4 bps net.
  - 100 USDT: about +287.9 bps net.
  - 250 USDT: about +84.4 bps net.
  - 500 USDT: about +0.04 bps net.
  - 1,000 USDT: about -45.2 bps net.
- KuCoin buy -> Gate sell was already negative at 50 USDT.

Verdict: `KILL` as a current route. The positive edge has no meaningful depth; by 500 USDT it is essentially zero and 1,000 USDT is negative. No persistence window warranted.

### BTR/USDT MEXC -> Bitget Follow-Up

Probed `BTR` from the fresh queue.

Metadata:

- MEXC: `BTRUSDT`, spot trading allowed, taker commission `0.0005`, full name `Bitlayer`, contract `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`.
- Gate: `BTR_USDT`, tradable, pair fee `0.2` = 20 bps; deposits/withdrawals enabled on `BTRBTC` and BSC chains.
- Bitget: `BTRUSDT`, status `online`, taker fee `0.001`.

Initial depth:

- MEXC buy -> Bitget sell:
  - 500 USDT: about +437.3 bps net.
  - 1,000 USDT: about +429.4 bps net.
  - 2,500 USDT: about +313.5 bps net.
  - 5,000 USDT: about +106.8 bps net.
  - 10,000 USDT: about -739.0 bps net.
- Gate buy -> Bitget sell was positive through 2,500 USDT but weaker than the MEXC route.

Persistence:

- Window: 2026-05-29 04:52:11 to 04:54:58 CST.
- Samples: 30, every 5 seconds.
- Errors: 0.
- 500 USDT: 30/30 positive, avg +448.966 bps, median +451.671 bps.
- 1,000 USDT: 30/30 positive, avg +440.080 bps, median +444.219 bps.
- 2,500 USDT: 30/30 positive, avg +332.768 bps, median +345.423 bps.
- 5,000 USDT: 30/30 positive, avg +123.678 bps, median +129.572 bps, min +64.840 bps.
- 10,000 USDT: 0/30 positive, avg -476.173 bps.

Verdict: `MEASURE` as a capped route. Initial cap: 5,000 USDT. It is stronger and deeper than HOOLI, but still below VANRY and ULTIMA until Bitget asset identity/network and inventory feasibility are verified.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance scanner/watchlist, initial cap 10,000 USDT.
2. `DO_NOW` - VANRY MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
3. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, initial cap 5,000 USDT.
4. `MEASURE` - BTR MEXC -> Bitget capped at 5,000 USDT.
5. `MEASURE` - HOOLI MEXC -> Bitget capped at 500 USDT.

### Next Loop

The fresh queue from the corrected scan is exhausted. Next highest-leverage work is operational due diligence and watchlist implementation for VANRY/ULTIMA, with BTR/HOOLI kept as lower-priority measurement routes.

## Checkpoint - 2026-05-29 05:00 CST

### Promoted Route Refresh

Ran a compact 20-sample refresh on the current promoted/capped routes.

Window:

- 2026-05-29 04:56:56 to 04:59:19 CST.
- 20 samples, every 5 seconds.
- Errors: 0.

Results:

- VANRY MEXC -> Binance, 5,000 USDT: 20/20 positive, avg +474.938 bps, median +474.665 bps, min +358.587 bps.
- VANRY MEXC -> Binance, 10,000 USDT: 20/20 positive, avg +276.935 bps, median +271.048 bps, min +211.850 bps.
- VANRY MEXC -> KuCoin, 5,000 USDT: 20/20 positive, avg +167.085 bps, median +162.885 bps, min +42.953 bps.
- ULTIMA MEXC -> KuCoin, 5,000 USDT: 20/20 positive, avg +225.097 bps, median +255.530 bps, min +99.368 bps.
- ULTIMA MEXC -> KuCoin, 10,000 USDT: 15/20 positive, avg +26.957 bps, median +71.339 bps, min -146.025 bps.
- BTR MEXC -> Bitget, 5,000 USDT: 20/20 positive, avg +128.988 bps, median +132.971 bps, min +103.881 bps.
- BTR MEXC -> Bitget, 10,000 USDT: 0/20 positive, avg -643.328 bps.

Verdict: ranking holds. VANRY -> Binance remains the best measured route; ULTIMA remains capped at 5,000 USDT; BTR remains capped at 5,000 USDT. Do not raise ULTIMA or BTR to 10,000 USDT.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance scanner/watchlist, cap 10,000 USDT.
2. `DO_NOW` - VANRY MEXC -> KuCoin scanner/watchlist, cap 5,000 USDT.
3. `DO_NOW` - ULTIMA MEXC -> KuCoin scanner/watchlist, cap 5,000 USDT.
4. `MEASURE` - BTR MEXC -> Bitget capped at 5,000 USDT.
5. `MEASURE` - HOOLI MEXC -> Bitget capped at 500 USDT.

### Next Loop

Operational feasibility is now the main blocker, not public-book spread discovery. If continuing without private/account access, run another corrected discovery scan later and periodically refresh VANRY/ULTIMA/BTR caps.

## Checkpoint - 2026-05-29 05:05 CST

### Second Corrected Scan Follow-Up

Ran another corrected discovery scan after excluding the newly promoted/killed routes. Top new candidates were `PHB` MEXC -> Gate and `VANRY/USDC` MEXC -> Binance.

#### PHB/USDT MEXC -> Gate

Metadata:

- MEXC: `PHBUSDT`, spot trading allowed, taker commission `0.0005`, full name `Phoenix Global`, contract `0x0409633A72D846fc5BBe2f98D88564D35987904D`.
- Gate: `PHB_USDT`, tradable, pair fee `0.2` = 20 bps; currency name `Phoenix`, BSC contract matches case-insensitively, withdrawals enabled, deposits disabled.

Depth:

- MEXC buy -> Gate sell:
  - 50 USDT: about +1,076.9 bps net.
  - 500 USDT: about +728.9 bps net.
  - 1,000 USDT: about +438.7 bps net.
  - 2,500 USDT: about -684.1 bps net.

Verdict: `KILL` for current executable route. Same failure mode as GUA: Gate deposits are disabled, so there is no clean sell-inventory/rebalance path.

#### VANRY/USDC MEXC -> Binance

This is a same-quote USDC lane, not a USDT/USDC cross-lane comparison.

Metadata:

- MEXC: `VANRYUSDC`, spot trading allowed, symbol taker commission `0`, contract `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`.
- Binance: `VANRYUSDC`, status `TRADING`, spot trading allowed.
- Conservative measurement still used 5 bps MEXC taker fee because the discovery parser currently treats zero fee as missing.

Initial depth:

- MEXC buy -> Binance sell:
  - 1,000 USDC: about +825.3 bps net.
  - 2,500 USDC: about +755.3 bps net.
  - 5,000 USDC: about +526.4 bps net.
  - 10,000 USDC: about -576.4 bps net.

Persistence:

- Window: 2026-05-29 05:03:03 to 05:04:53 CST.
- Samples: 20, every 5 seconds.
- Errors: 0.
- 1,000 USDC: 20/20 positive, avg +878.561 bps, median +873.486 bps.
- 2,500 USDC: 20/20 positive, avg +787.567 bps, median +790.906 bps.
- 5,000 USDC: 18/20 positive, avg +498.774 bps, median +658.790 bps, min -367.762 bps.
- 10,000 USDC: 3/20 positive, avg -506.189 bps.

Verdict: `MEASURE` as a separate VANRY USDC lane capped at 2,500 USDC. Do not raise to 5,000 USDC until the negative-tail behavior disappears. Also fix discovery fee parsing so true zero bps venue fees are preserved instead of falling back to defaults.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance USDT, cap 10,000 USDT.
2. `DO_NOW` - VANRY MEXC -> KuCoin USDT, cap 5,000 USDT.
3. `DO_NOW` - ULTIMA MEXC -> KuCoin USDT, cap 5,000 USDT.
4. `MEASURE` - VANRY MEXC -> Binance USDC, cap 2,500 USDC.
5. `MEASURE` - BTR MEXC -> Bitget USDT, cap 5,000 USDT.

### Next Loop

Next fresh-scan candidates after PHB/VANRY-USDC were AI routes, but AI already has known ticker-collision risk across venues. Any AI probe must verify asset identity before depth.

## Checkpoint - 2026-05-29 05:06 CST

### AI/USDT Identity Follow-Up

Fresh scan surfaced multiple high-ranked `AI/USDT` routes. Per the identity gate, checked metadata before depth.

Identity split:

- Gate `AI`: `Sleepless AI`, BSC contract `0xBDA011D7F8EC00F66C1923B049B94c67d148d8b2`.
- Binance `AI`: public asset metadata identifies `Sleepless AI`.
- MEXC `AI`: full name `Gensyn`, contract `0x4d7078DDd6cCFED2F85dB5B7D3Ff16828d378d48`.
- KuCoin `AI`: full name `Gensyn`, ERC20 contract `0x4d7078ddd6ccfed2f85db5b7d3ff16828d378d48`; also exposes Gensyn chain.
- OKX `AI-USDT`: current listing is on the Gensyn side per prior identity work and current listing context; OKX public instrument endpoint does not expose contract.

Verdict: `KILL` all AI routes that cross the Sleepless/Gensyn boundary. Do not depth-probe Gate/Binance vs MEXC/KuCoin/OKX `AI` as a same-asset route.

### Next Loop

After removing AI identity traps, the next fresh candidates are lower priority (`ESPORTS`, `COQ`, `SNEK`, `SPARKLET`, `SWEAT`, `VOOI`) and must still pass identity/depth/persistence. None should distract from VANRY/ULTIMA/BTR operational feasibility.

## Checkpoint - 2026-05-29 05:09 CST

### ESPORTS/USDT KuCoin -> Bitget

Probed the next lower-priority leftover from the corrected scan.

Metadata:

- KuCoin: `ESPORTS-USDT`, trading enabled, fee category `3`, full name `Yooldo Games`, BEP20 contract `0xf39e4b21c84e737df08e2c3b32541d856f508e48`.
- Bitget: `ESPORTSUSDT`, online, taker fee `0.001`, BEP20 contract `0xf39e4b21c84e737df08e2c3b32541d856f508e48`.
- Both venues expose the same BEP20 contract, so identity is clean.
- KuCoin reports BEP20 withdrawals enabled but deposits disabled.
- Bitget reports BEP20 withdrawals enabled but deposits disabled.

Depth:

- KuCoin buy -> Bitget sell:
  - 50 USDT: about +2,563.8 bps net.
  - 100 USDT: about +2,471.8 bps net.
  - 250 USDT: about +2,371.7 bps net.
  - 500 USDT: about +2,191.3 bps net.
  - 1,000 USDT: about +1,633.3 bps net.
  - 2,500 USDT: about +964.6 bps net.
  - 5,000 USDT: about +344.7 bps net.
  - 10,000 USDT: about -905.3 bps net.
- Bitget buy -> KuCoin sell was negative at every tested bucket.

Verdict: `KILL` as a repeatable arbitrage route despite huge positive public-book spread. The transfer path is broken because both venues have deposits disabled. This is at best an inventory-liquidation oddity for pre-existing Bitget inventory, not a route Agent 2 should promote.

### Next Loop

Continue lower-priority leftover probes only after refreshed checks on the promoted VANRY/ULTIMA/BTR set. Remaining leftovers from the same scan are `COQ`, `SNEK`, `SPARKLET`, `SWEAT`, and `VOOI`.

## Checkpoint - 2026-05-29 05:14 CST

### Promoted Route Refresh

Ran a 20-sample public-depth refresh from 2026-05-29 05:11:58 to 05:14:34 CST. Sample set had zero endpoint errors.

Results:

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT: 20/20 positive, avg +424.049 bps, median +426.269 bps, min +294.078 bps.
  - 10,000 USDT: 20/20 positive, avg +220.249 bps, median +219.969 bps, min +111.804 bps.
- VANRY MEXC -> KuCoin USDT:
  - 5,000 USDT: 19/20 positive, avg +117.878 bps, median +116.334 bps, min -22.662 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +280.773 bps, median +280.292 bps, min +274.943 bps.
  - 10,000 USDT: 20/20 positive, avg +129.771 bps, median +129.673 bps, min +125.464 bps.
- BTR MEXC -> Bitget USDT:
  - 5,000 USDT: 20/20 positive, avg +119.803 bps, median +121.028 bps, min +98.886 bps.
  - 10,000 USDT: 0/20 positive, avg -513.260 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC: 20/20 positive, avg +747.947 bps, median +758.481 bps, min +551.253 bps.
  - 5,000 USDC: 20/20 positive, avg +514.622 bps, median +546.455 bps, min +50.598 bps.

Verdict:

- VANRY -> Binance USDT remains the strongest measured public-book route at 10,000 USDT.
- ULTIMA 10,000 USDT recovered strongly in this window, but do not raise the execution assumption above 5,000 USDT until another refresh confirms because the prior window had a negative tail at 10,000 USDT.
- VANRY -> KuCoin USDT should stay below VANRY -> Binance and ULTIMA in priority because 5,000 USDT now had one negative sample.
- VANRY -> Binance USDC 5,000 USDC is now a cap-expansion candidate, but keep the formal cap at 2,500 USDC until one more positive-tail refresh confirms the earlier negative-tail behavior is gone.
- BTR remains capped at 5,000 USDT; 10,000 USDT stays rejected.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance USDT scanner/watchlist, cap 10,000 USDT.
2. `DO_NOW` - ULTIMA MEXC -> KuCoin USDT scanner/watchlist, cap 5,000 USDT; measure 10,000 USDT expansion.
3. `DO_NOW` - VANRY operational due diligence: Binance network/deposit support, MEXC withdrawal status, and pre-positioned VANRY inventory.
4. `DO_NOW` - VANRY MEXC -> KuCoin USDT scanner/watchlist, cap 5,000 USDT with stricter live thresholding.
5. `MEASURE` - VANRY MEXC -> Binance USDC, cap 2,500 USDC; measure 5,000 USDC expansion.
6. `MEASURE` - BTR MEXC -> Bitget USDT, cap 5,000 USDT.

### Next Loop

Run one more confirmation refresh for the ULTIMA 10,000 USDT and VANRY USDC 5,000 USDC expansion buckets before changing formal caps. Continue to avoid lower-priority leftovers unless promoted-route operational feasibility is exhausted.

## Checkpoint - 2026-05-29 05:20 CST

### Targeted Cap-Expansion Confirmation

Ran a targeted 30-sample public-depth confirmation from 2026-05-29 05:17:36 to 05:20:05 CST. Sample set had zero endpoint errors.

Results:

- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 30/30 positive, avg +300.533 bps, median +299.264 bps, min +294.818 bps.
  - 10,000 USDT: 30/30 positive, avg +145.404 bps, median +144.542 bps, min +140.081 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC: 30/30 positive, avg +731.160 bps, median +780.396 bps, min +270.968 bps.
  - 5,000 USDC: 26/30 positive, avg +394.488 bps, median +532.192 bps, min -464.123 bps.
  - 10,000 USDC: 2/30 positive, avg -717.807 bps, median -637.419 bps, min -2,088.290 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT: 30/30 positive, avg +507.283 bps, median +507.700 bps, min +318.907 bps.
  - 5,000 USDT: 29/30 positive, avg +171.561 bps, median +160.022 bps, min -1.653 bps.

Verdict:

- Promote ULTIMA public-book scanner/watch cap to 10,000 USDT. This is not live-trading approval: chain/rebalance feasibility remains unresolved and still requires pre-positioned ULTIMA on KuCoin.
- Keep VANRY USDC formal cap at 2,500 USDC. The 5,000 USDC bucket failed tail confirmation again and 10,000 USDC remains rejected.
- For VANRY -> KuCoin USDT, treat 2,500 USDT as the firm bucket and 5,000 USDT as opportunistic only when live depth threshold is positive. VANRY -> Binance USDT remains the better VANRY leg.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance USDT scanner/watchlist, cap 10,000 USDT.
2. `DO_NOW` - ULTIMA MEXC -> KuCoin USDT scanner/watchlist, public-book cap 10,000 USDT; operational execution still blocked by chain/rebalance proof.
3. `DO_NOW` - VANRY operational due diligence: Binance network/deposit support, MEXC withdrawal status, and pre-positioned VANRY inventory.
4. `DO_NOW` - VANRY MEXC -> KuCoin USDT scanner/watchlist, firm cap 2,500 USDT; opportunistic 5,000 USDT only with live threshold.
5. `MEASURE` - VANRY MEXC -> Binance USDC, cap 2,500 USDC.
6. `MEASURE` - BTR MEXC -> Bitget USDT, cap 5,000 USDT.

### Next Loop

Operational feasibility is the bottleneck for the top routes. Without private/account access, continue public-only due diligence and periodic refreshes; lower-priority leftovers (`COQ`, `SNEK`, `SPARKLET`, `SWEAT`, `VOOI`) remain below the promoted-route work.

## Checkpoint - 2026-05-29 05:23 CST

### Public Operational Due Diligence

Checked public/web asset endpoints for the promoted VANRY and ULTIMA routes.

VANRY:

- MEXC exchange info confirms `VANRYUSDT` is spot tradable, taker commission `0.0005`, ERC20 contract `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`, max market quote `200,000` USDT.
- MEXC `/api/v3/capital/config/getall` is key-gated and returned `api key required`; MEXC withdrawal/deposit status remains unverified publicly.
- Binance web asset endpoint confirms `VANRY` / `Vanar`, old asset code `TVK`, trading enabled.
- Binance web asset endpoint also exposes ERC20 parent `ETH`, deposits enabled, withdrawals enabled, withdrawal fee `65` VANRY, minimum withdrawal `130` VANRY, address regex `0x...`.
- KuCoin confirms ERC20 contract `0x8de5b80a0c1b02fe4976851d030b36122dbb8624`, deposits and withdrawals enabled, withdrawal fee `167` VANRY, withdrawal minimum `334` VANRY, deposit minimum `15` VANRY.

ULTIMA:

- MEXC exchange info confirms `ULTIMAUSDT` is spot tradable, taker commission `0.0005`, contract/address `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`, max market quote `100,000` USDT.
- MEXC `/api/v3/capital/config/getall` is key-gated, so MEXC ULTIMA withdrawal/deposit status remains unverified publicly.
- KuCoin confirms ULTIMA BEP20 contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`, deposits and withdrawals enabled, withdrawal fee `0.0002` ULTIMA.
- Gate confirms ULTIMA SMART chain address `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`, deposits and withdrawals enabled.

Verdict:

- VANRY -> Binance is now materially stronger operationally: the sell venue deposit/withdraw network is publicly verified on ERC20. The remaining hard blocker is MEXC withdrawal status or already having VANRY inventory pre-positioned on Binance.
- VANRY -> KuCoin remains viable but less attractive than Binance on public withdrawal fees and recent 5,000 USDT tail behavior.
- ULTIMA still has the best newly confirmed 10,000 USDT book window, but operational confidence remains lower than VANRY because MEXC/Gate evidence points to SMART while KuCoin uses BEP20. Treat as pre-positioned-inventory only until bridge/chain compatibility is proven.

### Updated Operational Ranking

1. `DO_NOW` - VANRY MEXC -> Binance USDT, cap 10,000 USDT; Binance ERC20 deposit/withdraw verified, MEXC withdrawal still unverified.
2. `DO_NOW` - ULTIMA MEXC -> KuCoin USDT, public-book cap 10,000 USDT; operationally pre-positioned-inventory only until SMART/BEP20 bridge proof exists.
3. `DO_NOW` - VANRY MEXC -> KuCoin USDT, firm cap 2,500 USDT; opportunistic 5,000 USDT only with live threshold.
4. `MEASURE` - VANRY MEXC -> Binance USDC, cap 2,500 USDC.
5. `MEASURE` - BTR MEXC -> Bitget USDT, cap 5,000 USDT.

## Checkpoint - 2026-05-29 05:24 CST

### Bitget Identity/Deposit Follow-Up

Used Bitget's public coin endpoint to close the open identity/rebalance risk for BTR and HOOLI.

BTR:

- MEXC `BTRUSDT`: full name `Bitlayer`, ERC20 contract `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`, spot tradable.
- Bitget `BTR`: ERC20 contract `0x6c76de483f1752ac8473e2b4983a873991e70da7`, withdrawals enabled, deposits disabled.
- The contracts do not match, and the Bitget destination deposit lane is disabled.

HOOLI:

- MEXC `HOOLIUSDT`: full name `Hooli`, SOL contract `FPJfY8mMTRwaePD2f46TFLqVov4X9svBaUgR1a8oTwTF`, spot tradable.
- Bitget `HOOLI`: SOL contract `FPJfY8mMTRwaePD2f46TFLqVov4X9svBaUgR1a8oTwTF`, withdrawals enabled, deposits disabled.
- Identity matches, but the sell venue deposit lane is disabled.

Verdict:

- `KILL` BTR MEXC -> Bitget. The spread cannot be treated as same-asset arbitrage after public contract mismatch, and Bitget deposits are disabled anyway.
- `KILL` HOOLI MEXC -> Bitget as a repeatable route. Identity is clean, but Bitget deposits are disabled and the route only had a 500 USDT cap.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance USDT, cap 10,000 USDT.
2. `DO_NOW` - ULTIMA MEXC -> KuCoin USDT, public-book cap 10,000 USDT but operationally pre-positioned-inventory only.
3. `DO_NOW` - VANRY MEXC -> KuCoin USDT, firm cap 2,500 USDT; opportunistic 5,000 USDT only with live threshold.
4. `MEASURE` - VANRY MEXC -> Binance USDC, cap 2,500 USDC.

## Checkpoint - 2026-05-29 05:29 CST

### Lower-Priority Leftovers: SWEAT and SPARKLET

Ran a targeted top-of-book pass over the remaining lower-priority leftovers (`COQ`, `SNEK`, `SPARKLET`, `SWEAT`, `VOOI`). The best top-of-book leftovers were SWEAT MEXC/Bitget -> Gate and SPARKLET MEXC -> Gate.

SWEAT:

- MEXC `SWEATUSDT`: full name `Sweat Economy`, ERC20 contract `0xB4b9DC1C77bdbb135eA907fd5a08094d98883A35`, spot tradable.
- Gate `SWEAT`: same ERC20 contract on ETH, but deposits disabled on both ETH and NEAR; ETH withdrawals disabled and NEAR withdrawals enabled.
- Bitget `SWEAT`: NEAR contract `token.sweat`, withdrawals enabled, deposits disabled.
- Top-of-book net was about +434.6 bps for MEXC -> Gate and +430.7 bps for Bitget -> Gate, but the sell venue cannot be replenished through public deposit lanes.

Verdict: `KILL` SWEAT as a repeatable route. It is another deposit-disabled sell-venue trap.

SPARKLET:

- MEXC `SPARKLETUSDT`: full name `Upland`, ERC20 contract `0x0bc37BEA9068a86C221B8bd71eA6228260DAD5A2`, spot tradable.
- Gate `SPARKLET`: matching ERC20 contract, deposits and withdrawals enabled, pair fee `0.2` = 20 bps.
- Initial depth for MEXC buy -> Gate sell was positive only through 500 USDT and negative by 1,000 USDT.
- Persistence window: 2026-05-29 05:27:39 to 05:28:59 CST, 20 samples, zero errors.
  - 250 USDT: 20/20 positive, avg +73.683 bps, min +70.416 bps.
  - 500 USDT: 20/20 positive, avg +38.332 bps, min +35.302 bps.
  - 1,000 USDT: 0/20 positive, avg -5.949 bps.

Verdict: `KILL` SPARKLET as an execution candidate despite valid identity and transfers. The 500 USDT edge is only about 38 bps before withdrawal/rebalance overhead, and 1,000 USDT is consistently negative. This is too small to matter relative to VANRY/ULTIMA.

### Next Loop

Remaining lower-priority leftovers are `COQ`, `SNEK`, and `VOOI`. Probe only if the loop needs more discovery after VANRY/ULTIMA refreshes and public operational diligence.

## Checkpoint - 2026-05-29 05:32 CST

### Lower-Priority Leftovers Exhausted: SNEK, COQ, VOOI

Finished the remaining lower-priority leftover queue.

SNEK:

- Identity/transfer status was good enough to test: KuCoin, MEXC, Gate, and Bitget all align on SNEK/Cardano-style identity where exposed; KuCoin, Gate, and Bitget deposits are enabled.
- Best live depth route was KuCoin buy -> Bitget sell.
- Depth:
  - 50 USDT: +80.387 bps.
  - 100 USDT: +72.161 bps.
  - 250 USDT: +21.982 bps.
  - 500 USDT: -25.252 bps.
- KuCoin withdrawal fee is `2,000` SNEK, which already exceeds the tiny 250 USDT edge.
- Verdict: `KILL`; too small after depth and transfer/rebalance overhead.

COQ:

- Identity aligns across KuCoin, MEXC, and Gate on AVAX C-Chain contract `0x420FcA0121DC28039145009570975747295f2329`.
- Live depth killed the route despite positive top-of-book.
- KuCoin buy -> MEXC sell was negative at every tested bucket: about -122.153 bps at 50 USDT and -152.209 bps at 100 USDT.
- KuCoin buy -> Gate sell was also negative at every tested bucket.
- Verdict: `KILL`; stale/top-of-book signal failed depth.

VOOI:

- MEXC, KuCoin, Gate, and Bitget expose matching ERC20 contract `0xb31561f0e2aac72406103b1926356d756f07a481` where public metadata is available.
- Bybit asset/network endpoint is key-gated, and Bybit was the sell venue in the apparent route.
- Live depth for MEXC/KuCoin/Gate buy -> Bybit sell was positive only at 50-100 USDT and negative by 250 USDT.
- Best route, MEXC buy -> Bybit sell:
  - 50 USDT: +75.311 bps.
  - 100 USDT: +30.578 bps.
  - 250 USDT: -41.734 bps.
- Verdict: `KILL`; no meaningful notional depth, and sell-venue network status is not publicly verified.

### Queue Status

The corrected fresh-scan queue is exhausted. Current live priorities are only:

1. VANRY MEXC -> Binance USDT, cap 10,000 USDT, operationally strongest public evidence.
2. ULTIMA MEXC -> KuCoin USDT, public-book cap 10,000 USDT, operational chain/rebalance still unresolved.
3. VANRY MEXC -> KuCoin USDT, firm cap 2,500 USDT with 5,000 USDT opportunistic threshold.
4. VANRY MEXC -> Binance USDC, cap 2,500 USDC.

## Checkpoint - 2026-05-29 05:36 CST

### Top-Route Refresh After Queue Exhaustion

Ran a 20-sample public-depth refresh from 2026-05-29 05:33:43 to 05:36:14 CST. There was one KuCoin `VANRY-USDT` timeout on sample 18; affected VANRY -> KuCoin buckets have 19 valid samples.

Results:

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT: 20/20 positive, avg +430.447 bps, median +444.985 bps, min +295.034 bps.
  - 10,000 USDT: 20/20 positive, avg +199.935 bps, median +212.975 bps, min +100.148 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +351.241 bps, median +356.106 bps, min +289.655 bps.
  - 10,000 USDT: 20/20 positive, avg +175.212 bps, median +182.930 bps, min +104.929 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT: 19/19 positive, avg +389.112 bps, median +385.662 bps, min +303.105 bps.
  - 5,000 USDT: 19/19 positive, avg +88.318 bps, median +86.291 bps, min +3.113 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC: 20/20 positive, avg +705.950 bps, median +706.801 bps, min +542.378 bps.
  - 5,000 USDC: 18/20 positive, avg +330.534 bps, median +349.601 bps, min -127.744 bps.

Verdict:

- VANRY -> Binance USDT and ULTIMA -> KuCoin USDT remain the only high-cap public-book routes.
- ULTIMA 10,000 USDT now has two consecutive strong confirmation windows after the earlier negative-tail window, but operational chain proof is still the blocker.
- VANRY -> KuCoin 5,000 USDT was positive in this refresh but the min is only +3.113 bps, so keep 2,500 USDT as firm and 5,000 USDT as opportunistic.
- VANRY USDC 5,000 USDC again failed tail confirmation. Keep 2,500 USDC cap.

### Next Loop

With the corrected queue exhausted, the next useful work is either a new corrected fee-aware discovery pass or continued periodic refresh/operational due diligence for VANRY and ULTIMA. Do not revive BTR/HOOLI/SWEAT/SPARKLET/SNEK/COQ/VOOI without materially different public metadata or depth.

## Checkpoint - 2026-05-29 05:41 CST

### New Corrected Discovery Pass

Ran a new corrected top-of-book discovery pass at 2026-05-29 05:38:03 CST across 7,660 public USDT/USDC markets. Fees were conservative: Gate 20 bps, Bitfinex excluded from this focused pass, MEXC 5 bps, KuCoin/Bybit/Bitget/Binance/OKX 10 bps, plus 2 bps latency.

Immediate metadata/depth outcomes from top ranked fresh routes:

- `RAVE` Bitget -> Gate/KuCoin: `KILL`. Bitget, Gate, and KuCoin align on ERC20 contract `0x17205fab260a7a6383a81452ce6315a39370db97`, but all relevant public endpoints report deposits disabled on the sell venues.
- `UPC` MEXC -> Bitget: `KILL`. Contracts match on ERC20 `0x487d62468282bd04ddf976631c23128a425555ee`, but Bitget deposits are disabled.
- `RWA` Gate/MEXC -> KuCoin: `KILL`. Ticker collision: MEXC/Gate list `Allo` on BSC contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`; KuCoin lists `RWA Inc` on Base contract `0xe2b1dc2d4a3b4e59fdf0c47b71a7a86391a8b35a`.
- `TOWER` MEXC -> KuCoin: `KILL`. MEXC contract `0xf7C1CEfCf7E1dd8161e00099facD3E1Db9e528ee` does not match KuCoin ERC20 contract `0x1c9922314ed1415c95b9fd453c3818fd41867d0b`.
- `ARRR` Gate -> MEXC: `KILL`. Identity aligns as Pirate Chain and Gate deposits are enabled, but live depth was positive only at 50 USDT and negative by 100 USDT.

XMN:

- Route: buy MEXC `XMNUSDT`, sell KuCoin `XMN-USDT`.
- Identity: MEXC and KuCoin both identify `xMoney` on SUI contract `0x97c7571f4406cdd7a95f3027075ab80d3e9c937c2a567690d31e14ab1872ccee::xmn::XMN`.
- KuCoin deposits/withdrawals enabled; withdrawal fee `100` XMN, withdrawal minimum `200` XMN.
- MEXC deposit/withdraw status remains key-gated.
- Initial depth was positive through 500 USDT and negative at 1,000 USDT.
- Persistence window: 2026-05-29 05:39:53 to 05:41:04 CST, 20 samples, zero errors.
  - 250 USDT: 20/20 positive, avg +103.767 bps.
  - 500 USDT: 20/20 positive, avg +67.794 bps, min +66.131 bps.
  - 1,000 USDT: 0/20 positive, avg -144.453 bps.

Verdict: `MEASURE` as a low-priority micro-route capped at 500 USDT, not an execution opportunity. It needs MEXC withdrawal status/fee verification and is far below VANRY/ULTIMA on capacity.

### Updated Ranking

1. `DO_NOW` - VANRY MEXC -> Binance USDT, cap 10,000 USDT.
2. `DO_NOW` - ULTIMA MEXC -> KuCoin USDT, public-book cap 10,000 USDT but operationally pre-positioned-inventory only.
3. `DO_NOW` - VANRY MEXC -> KuCoin USDT, firm cap 2,500 USDT; opportunistic 5,000 USDT only with live threshold.
4. `MEASURE` - VANRY MEXC -> Binance USDC, cap 2,500 USDC.
5. `LATER` - XMN MEXC -> KuCoin USDT, micro cap 500 USDT pending MEXC withdrawal status/fee.

## Checkpoint - 2026-05-29 05:44 CST

### New Discovery Follow-Ups: SWCH, CWEB, GHX, BBT

Continued processing the corrected discovery pass.

- `SWCH` Gate -> MEXC: `KILL` before depth. MEXC and Gate contracts match for SwissCheese on Polygon, but MEXC reports `isSpotTradingAllowed=false`.
- `CWEB` KuCoin -> MEXC: `KILL`. Identity matches on ERC20 `0x505b5eda5e25a67e1c24a2bf1a527ed9eb88bf04`, but live depth was positive only through 250 USDT and negative at 500 USDT. KuCoin withdrawal fee `1,200` CWEB is larger than the 250 USDT edge.
- `GHX` Gate/KuCoin -> MEXC: `KILL`. Identity matches on ERC20 `0x728f30fa2f100742c7949d1961804fa8e0b1387d`, but depth was only positive at 50-100 USDT and negative by 250-500 USDT.
- `TYCOON` Gate -> MEXC: `KILL` before depth. MEXC reports `isSpotTradingAllowed=false`.
- `BBT` MEXC -> Gate: `KILL` before depth. MEXC reports `isSpotTradingAllowed=false`.

Verdict: no promotion. The new discovery pass has produced one low-priority micro survivor (`XMN`) and a series of identity/deposit/tradability/depth kills.

## Checkpoint - 2026-05-29 05:48 CST

### New Discovery First Page Exhausted

Finished the remaining near-threshold names from the 05:38 corrected discovery pass.

Kills:

- `IMT` Gate -> MEXC: identity and deposits were fine, but live depth was negative even at 50 USDT.
- `SIX` MEXC -> Gate: contract mismatch. MEXC reports `0x070a9867Ea49CE7AFc4505817204860e823489fE`; Gate reports `0x61c6ebf443ad613c9648762585b3cfd3ba1f3fa8`.
- `REACT` KuCoin -> Gate: contract matches on ETH, but KuCoin ERC20 withdrawals are disabled; only native `react` withdrawals are enabled while Gate supports ETH.
- `PYBOBO` MEXC -> Bybit: live depth was positive only at 50-100 USDT and negative by 250 USDT.
- `WBAI` KuCoin -> MEXC: identity matched, but live depth was negative even at 50 USDT.
- `MAPO` MEXC/KuCoin -> Bitget: Bitget deposits and withdrawals are disabled; KuCoin deposits are disabled.
- `CTA` Bybit -> KuCoin: live depth was negative even at 50 USDT.
- `ALEX` KuCoin -> MEXC: identity matched on STX, but live depth was positive only at 50-100 USDT and negative by 250 USDT.
- `DEVVE` Gate -> MEXC: identity matched, but live depth was positive only at 50 USDT and negative by 100 USDT.

Verdict: the first page of the new corrected discovery pass is exhausted. Only `XMN` survived, and only as a `LATER` micro-route capped at 500 USDT pending MEXC withdrawal status/fee. The strategic focus remains VANRY and ULTIMA.

## Checkpoint - 2026-05-29 05:52 CST

### Periodic Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 05:50:09 to 05:52:31 CST. Zero endpoint errors.

Results:

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT: 20/20 positive, avg +471.916 bps, median +472.314 bps, min +331.254 bps.
  - 10,000 USDT: 20/20 positive, avg +242.131 bps, median +242.889 bps, min +155.345 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +374.835 bps, median +375.240 bps, min +333.203 bps.
  - 10,000 USDT: 20/20 positive, avg +184.409 bps, median +181.924 bps, min +138.382 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT: 20/20 positive, avg +465.614 bps, median +452.913 bps, min +330.614 bps.
  - 5,000 USDT: 20/20 positive, avg +118.634 bps, median +105.780 bps, min +3.898 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC: 20/20 positive, avg +702.884 bps, median +674.202 bps, min +541.989 bps.
  - 5,000 USDC: 20/20 positive, avg +448.729 bps, median +440.645 bps, min +74.765 bps.

Verdict:

- VANRY -> Binance USDT remains the strongest operationally plausible public route: 10,000 USDT is still 20/20 positive with a healthy min.
- ULTIMA -> KuCoin 10,000 USDT remains strong on books, but operational chain/rebalance proof remains unresolved.
- VANRY -> KuCoin 5,000 USDT remains positive but thin at the minimum, so keep 2,500 USDT as the firm bucket.
- VANRY USDC 5,000 USDC recovered in this window, but prior windows had negative tails. Keep formal cap at 2,500 USDC and treat 5,000 USDC as a watch bucket only.

## Checkpoint - 2026-05-29 05:59 CST

### Second-Page Discovery Follow-Ups: EPIC, SXT

Started processing the next corrected discovery page.

- `EPIC` Gate -> MEXC/Binance: `KILL`. Identity and transfer metadata were clean enough to depth-test: Gate, MEXC, and Binance point to the same EPIC ERC20 contract, and Gate/Binance public transfer lanes were enabled. Live executable depth was negative even at 50 USDT after fees and latency.
  - Gate -> MEXC: -84.759 bps at 50 USDT, -95.402 bps at 100 USDT, -128.681 bps at 250 USDT, -168.242 bps at 500 USDT.
  - Gate -> Binance: -90.461 bps at 50 USDT, -100.728 bps at 100 USDT, -131.868 bps at 250 USDT, -169.987 bps at 500 USDT.
- `SXT` Bybit -> MEXC/Binance/KuCoin/Bitget/Gate: `KILL`. Public metadata aligns SXT on ERC20 across MEXC, Binance, KuCoin, and Bitget, with KuCoin/Bitget ERC20 deposits and withdrawals enabled. Bybit transfer status remains not publicly verified, but depth already failed.
  - Bybit -> MEXC: +42.895 bps at 50 USDT and +42.793 bps at 100 USDT, then -53.151 bps at 250 USDT and -94.948 bps at 500 USDT.
  - Bybit -> Binance: -21.980 bps at 50-500 USDT, then worse at larger buckets.
  - Bybit -> KuCoin: -89.424 bps at 50 USDT and worse; sell depth exhausted by 5,000 USDT.
  - Bybit -> Bitget: -14.499 bps at 50 USDT and worse.
  - Bybit -> Gate: -48.282 bps at 50 USDT and worse.

Verdict: no promotion. `EPIC` failed immediately on executable depth despite clean identity. `SXT` had only a tiny 50-100 USDT MEXC sell pocket and is not worth persistence sampling. Continue the second-page queue with `CHIRP`, `GAMEVIRTUAL`, `AFC`, `LKI`, `LYX`, `NOS`, `ID`, `SOUL`, and `RIO`.

## Checkpoint - 2026-05-29 06:04 CST

### Second-Page Discovery Queue Exhausted

Finished the remaining names from the corrected second-page discovery queue.

Kills:

- `CHIRP` MEXC -> KuCoin: identity matches on SUI and KuCoin deposits/withdrawals are enabled, but live depth was only +46.613 bps at 50 USDT, then -11.259 bps at 100 USDT and -103.365 bps at 250 USDT.
- `GAMEVIRTUAL` Gate -> MEXC: identity matches on Base and Gate transfers are enabled, but live depth was negative from 50 USDT: -25.473 bps at 50 USDT, -32.551 bps at 100 USDT, -45.805 bps at 250 USDT.
- `AFC` MEXC -> Bybit: Bybit trading is live and MEXC identifies Arsenal Fan Token, but live depth was negative from 50 USDT: -38.595 bps at 50 USDT, -53.771 bps at 100 USDT, -76.666 bps at 250 USDT.
- `LKI` MEXC -> KuCoin: identity matches on BEP20 and KuCoin transfers are enabled, but live depth was deeply negative from 50 USDT: -367.978 bps at 50 USDT and worse.
- `LYX` Gate -> KuCoin: LUKSO identity and transfer lanes look aligned, but the route is only positive at 50-100 USDT and negative by 250 USDT: +85.079 bps at 50 USDT, +74.534 bps at 100 USDT, -47.256 bps at 250 USDT.
- `NOS` Gate -> MEXC: identity matches on Solana, but live depth was negative from 50 USDT: -26.207 bps at 50 USDT, -28.670 bps at 100 USDT, -31.441 bps at 250 USDT.
- `ID` MEXC -> Bybit: MEXC identifies SPACE ID and Bybit trading is live, but live depth was negative from 50 USDT: -41.238 bps at 50 USDT, -50.749 bps at 100 USDT, -70.661 bps at 250 USDT.
- `SOUL` Gate -> KuCoin: Phantasma metadata appears directionally aligned but chain labels differ (`KCALP` vs `PHANTASMA`), and depth was already negative from 50 USDT: -14.308 bps at 50 USDT and -76.727 bps at 100 USDT.
- `RIO` KuCoin -> MEXC: identity/transfer lane is not clean because KuCoin reports BEP20 contract `0x94a8b4ee5cd64c79d0ee816f467ea73009f51aa0` while MEXC reports `2751733`; depth was only positive at 50-100 USDT and negative by 250 USDT.

Verdict: no promotion from this page. The repeated pattern is the same as the first page: top-of-book dislocations exist, but actionable depth disappears before 250-500 USDT or the transfer lane is ambiguous. The only current high-cap routes remain VANRY MEXC -> Binance and ULTIMA MEXC -> KuCoin, with VANRY MEXC -> KuCoin and VANRY USDC as secondary monitored lanes.

## Checkpoint - 2026-05-29 06:09 CST

### Periodic Top-Route Refresh

Ran a fresh 20-sample refresh from 2026-05-29 06:06:31 to 06:09:33 CST. Zero endpoint errors. This refresh used actual MEXC fee metadata, including `VANRYUSDC` taker `0.0` bps instead of the earlier conservative 5 bps fallback.

Results:

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT: 20/20 positive, avg +669.399 bps, median +654.982 bps, min +539.321 bps.
  - 10,000 USDT: 20/20 positive, avg +307.750 bps, median +297.130 bps, min +164.289 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +481.657 bps, median +480.710 bps, min +418.940 bps.
  - 10,000 USDT: 20/20 positive, avg +237.999 bps, median +236.777 bps, min +174.346 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT: 20/20 positive, avg +637.136 bps, median +620.006 bps, min +563.553 bps.
  - 5,000 USDT: 20/20 positive, avg +325.173 bps, median +318.016 bps, min +205.403 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC: 20/20 positive, avg +912.309 bps, median +921.825 bps, min +781.821 bps.
  - 5,000 USDC: 20/20 positive, avg +620.881 bps, median +662.076 bps, min +193.250 bps.

Verdict:

- VANRY -> Binance 10,000 USDT remains the top public-book route and strengthened in this window.
- ULTIMA -> KuCoin 10,000 USDT remains strong on books, but still requires chain/rebalance proof before it is operational.
- VANRY -> KuCoin 5,000 USDT improved materially, but prior windows had thin minimums near zero; require one more robust window before promoting 5,000 USDT to a firm cap.
- VANRY USDC 5,000 USDC also improved with the corrected zero MEXC fee, but prior negative-tail windows still argue for keeping the formal cap at 2,500 USDC until another robust window confirms stability.

## Checkpoint - 2026-05-29 06:16 CST

### Fresh Corrected Discovery Pass

Ran a fresh corrected top-of-book discovery pass with Gate taker corrected to 20 bps, Bitfinex no longer treated as zero-fee, same-quote USDT/USDC lanes only, and already-processed bases excluded.

Scan summary:

- Markets: 10,216.
- Same-lane routes scored: 2,081.
- New filtered top-of-book candidates: 34.
- Endpoint errors: 0.

Processed the first fresh-scan tranche:

- `DMTR` MEXC -> KuCoin: identity matches on ERC20 and KuCoin transfers are enabled, but positive depth ends before 1,000 USDT and the 170 DMTR KuCoin withdrawal fee wipes the 250-500 USDT pocket. Depth: +85.181 bps at 50 USDT, +66.286 bps at 100 USDT, +35.714 bps at 250 USDT, +13.262 bps at 500 USDT, -14.643 bps at 1,000 USDT.
- `WARD` Bitget/MEXC/KuCoin -> Gate: `KILL` at transfer gate. Gate exposes a BSC contract `0x6dc200b21894af4660b549b678ea8df22bf7cfac`; KuCoin/Bitget expose native Warden, and MEXC has no contract field. No repeatable transfer lane without bridge proof.
- `INSP` MEXC -> KuCoin: identity matches on ERC20 and KuCoin transfers are enabled, but depth is negative from 50 USDT: -93.174 bps at 50 USDT, -120.797 bps at 100 USDT.
- `TX` Gate -> Bitget: compatible-looking native TX metadata, but depth is negative from 50 USDT: -11.922 bps at 50 USDT, -38.500 bps at 100 USDT.
- `SIN` KuCoin -> MEXC: identity matches on BEP20, but depth is negative from 50 USDT: -58.243 bps at 50 USDT and worse.
- `STAY` MEXC -> KuCoin: identity matches on BEP20 and KuCoin transfers are enabled, but only 50 USDT was positive and the 14,000 STAY withdrawal fee wipes it. Depth: +24.016 bps at 50 USDT, -12.943 bps at 100 USDT.
- `ASSET` KuCoin -> MEXC: identity matches on ERC20, but positive depth ends before 500 USDT and the 8 ASSET withdrawal fee consumes most of the only positive pocket. Depth: +125.450 bps at 50-100 USDT, +74.015 bps at 250 USDT, -24.887 bps at 500 USDT.
- `PIN` MEXC -> Gate: `KILL` before depth. MEXC reports `isSpotTradingAllowed=false`.
- `GAIB` Bybit -> MEXC: barely positive at 50-100 USDT, negative by 250 USDT, and Bybit transfer status remains unverified. Depth: +6.180 bps at 50 USDT, +0.835 bps at 100 USDT, -32.099 bps at 250 USDT.

Verdict: no promotion. The new scan confirms the same distribution: lots of 25-125 bps top-of-book edges, but they die below actionable size, fail transfer identity, or are wiped by withdrawal fees. Continue only until the next meaningful survivor appears; do not let tail-candidate work distract from VANRY/ULTIMA operational proof.

## Checkpoint - 2026-05-29 06:19 CST

### Fresh Scan Batch-Depth Follow-Up

Batch-tested the next fresh-scan tranche. All routes were negative from 50 USDT onward, so no identity/transfer chase was warranted.

- `HEART` KuCoin -> MEXC: -61.743 bps at 50 USDT, -142.304 bps at 100 USDT, -326.484 bps at 250 USDT.
- `BNKR` KuCoin/Gate -> MEXC:
  - KuCoin -> MEXC: -21.546 bps at 50 USDT, -22.020 bps at 100 USDT, -22.305 bps at 250 USDT.
  - Gate -> MEXC: -5.769 bps at 50 USDT, -6.243 bps at 100 USDT, -6.527 bps at 250 USDT.
- `ESE` MEXC -> Bybit/KuCoin:
  - MEXC -> Bybit: -51.950 bps at 50 USDT, -63.773 bps at 100 USDT.
  - MEXC -> KuCoin: -44.139 bps at 50 USDT, -55.127 bps at 100 USDT.
- `RVV` Bitget -> MEXC: -93.739 bps at 50 USDT, -137.182 bps at 100 USDT.
- `HEI` Binance -> MEXC: -58.784 bps at 50 USDT, -61.402 bps at 100 USDT.
- `ROOBEE` Gate -> KuCoin: -12.568 bps at 50 USDT, -53.789 bps at 100 USDT.
- `LAVA` Bybit -> MEXC: -16.877 bps at 50 USDT, -16.931 bps at 100 USDT.
- `RMV` MEXC -> KuCoin: -60.613 bps at 50 USDT, -117.706 bps at 100 USDT.

Verdict: no promotion. Continue the remaining fresh-scan queue, but the scan is now mostly confirming that modest top-of-book spreads are noise after depth.

## Checkpoint - 2026-05-29 06:21 CST

### Fresh Corrected Scan Exhausted

Finished the remaining fresh-scan names.

- `XELS` Gate -> MEXC: positive only at 50-100 USDT, negative by 250 USDT. Depth: +41.341 bps at 50 USDT, +22.754 bps at 100 USDT, -17.004 bps at 250 USDT.
- `IOTX` MEXC/Binance -> Gate: positive only at 50-100 USDT, negative by 250 USDT on both buy venues.
- `HAI` KuCoin -> MEXC: negative from 50 USDT, -13.334 bps at 50 USDT and worse.
- `LL` MEXC -> KuCoin: negative from 50 USDT, -70.149 bps at 50 USDT and worse.
- `MCRT` Bybit -> MEXC: negative from 50 USDT, -77.408 bps at 50 USDT and worse.
- `MSFTON` MEXC -> Bitget: identity matches on ERC20 `0xb812837b81a3a6b81d7cd74cfb19a7f2784555e5`, and Bitget deposits/withdrawals are enabled. However, live edge is tiny and decays: +21.032 bps at 50 USDT, +14.885 bps at 1,000 USDT, +0.290 bps at 2,500 USDT, then -55.853 bps at 5,000 USDT. MEXC withdrawal status/fee remains unverified, and any ERC20 withdrawal/rebalance cost likely wipes this route.
- `GXE` Gate -> MEXC: negative from 50 USDT, -695.109 bps at 50 USDT.
- `IAUON` MEXC -> Gate: negative from 50 USDT, -14.321 bps at 50 USDT and worse.
- `ZENT` Bybit -> OKX: negative from 50 USDT, -45.187 bps at 50 USDT and worse.
- `HMSTR` Bitget -> Binance: negative from 50 USDT, -11.695 bps at 50 USDT and worse.
- `SWFTC` MEXC -> OKX: negative from 50 USDT, -144.766 bps at 50 USDT and worse.
- `ERG` Gate -> KuCoin: negative from 50 USDT, -57.741 bps at 50 USDT and worse.

Verdict: the fresh corrected scan is exhausted with no new promoted route. `MSFTON` is the only technically interesting identity-clean route, but its public-book edge is far below transfer/rebalance reality. The 100x move is not more tail-candidate grinding; it is operational proof and scanner automation around VANRY/ULTIMA.

## Checkpoint - 2026-05-29 06:26 CST

### Cap-Decision Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 06:23:09 to 06:26:10 CST. Zero endpoint errors. MEXC fee metadata was preserved, including `VANRYUSDC` taker `0.0` bps.

Results:

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT: 20/20 positive, avg +683.899 bps, median +668.313 bps, min +520.124 bps.
  - 10,000 USDT: 20/20 positive, avg +337.641 bps, median +325.747 bps, min +222.469 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +413.193 bps, median +444.004 bps, min +248.627 bps.
  - 10,000 USDT: 18/20 positive, avg +148.167 bps, median +189.125 bps, min -134.628 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT: 20/20 positive, avg +657.433 bps, median +647.869 bps, min +538.793 bps.
  - 5,000 USDT: 20/20 positive, avg +320.221 bps, median +314.789 bps, min +171.396 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC: 20/20 positive, avg +914.962 bps, median +938.087 bps, min +792.176 bps.
  - 5,000 USDC: 20/20 positive, avg +679.794 bps, median +757.039 bps, min +342.530 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT public-book cap at 10,000 USDT.
- Promote VANRY MEXC -> KuCoin USDT public-book cap to 5,000 USDT. This is now two consecutive robust 20-sample windows after the earlier thin-tail periods.
- Promote VANRY MEXC -> Binance USDC measurement cap to 5,000 USDC. This is now two consecutive robust windows using the corrected zero MEXC fee, but keep it below the USDT Binance lane operationally.
- Downgrade ULTIMA firm public-book cap to 5,000 USDT. Keep 10,000 USDT as live-threshold-only/watch because this window had negative tails at 10,000 USDT. Operational chain/rebalance blocker remains unchanged.

## Checkpoint - 2026-05-29 06:30 CST

### MEXC Public Operational Metadata Probe

Checked MEXC public web coin metadata for the two main operational blockers.

- VANRY:
  - `https://www.mexc.com/api/platform/spot/market-v2/web/coin/introduce?coinName=VANRY`
  - MEXC web metadata reports `ct="ETH"` and explorer `https://etherscan.io/token/0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`.
  - This matches Binance/KuCoin ERC20 identity already verified.
  - The endpoint does not expose deposit/withdraw enabled flags or MEXC withdrawal fee/minimum.
- ULTIMA:
  - `https://www.mexc.com/api/platform/spot/market-v2/web/coin/introduce?coinName=ULTIMA`
  - MEXC web metadata reports `ct="SMART"` and primary explorer `https://ultimachain.info/`.
  - The same metadata also lists BSC/Nansen/BscScan explorer links for `0x5668a83B46016B494A30Dd14066A451E5417A8B8`, matching KuCoin's BEP20 contract.
  - This reduces identity ambiguity but does not prove deposit/withdraw compatibility or a working MEXC SMART/BEP20 withdrawal lane.

Verdict: VANRY operational feasibility improved on identity because MEXC web metadata explicitly confirms ETH/ERC20, but MEXC withdrawal status remains unverified. ULTIMA remains operationally blocked: MEXC acknowledges both SMART and BSC explorer context, but that is not enough to prove a transferable route.

### Official Announcement Cross-Check

- VANRY: MEXC's Dec 1, 2023 token-swap announcement says VANRY deposits/trading opened Dec 1, 2023 15:40 UTC and withdrawals opened Dec 2, 2023 15:00 UTC. It also lists the ERC20 contract `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`.
  - Source: `https://www.mexc.com/announcements/article/mexc-completes-the-virtua-tvk-token-swap-and-rebranding-to-vanar-vanry-17827791511861`
- ULTIMA: MEXC's Apr 28, 2025 mainnet announcement says deposits and withdrawals for ULTIMA on the ULTIMA Mainnet would be available starting Apr 29, 2025 14:00 UTC.
  - Source: `https://www.mexc.com/announcements/article/mexc-will-support-the-ultima-mainnet-17827791523648`

Operational read:

- VANRY has stronger public support evidence now: historical MEXC withdrawal opening plus current MEXC web ETH metadata plus Binance/KuCoin ERC20 transfer support. The remaining blocker is current MEXC withdrawal status/fee/minimum, not identity.
- ULTIMA is more clearly a chain/rebalance problem: MEXC publicly supports ULTIMA Mainnet, while KuCoin's public transfer lane is BEP20. Do not treat MEXC -> KuCoin as repeatable until a bridge or pre-positioned inventory plan exists.

### MEXC Current Fee-Page API

Found and queried MEXC's public fee-page API used by the MEXC frontend:

- Endpoint: `https://www.mexc.com/api/platform/asset/api/coin/fee/rate/query`
- Source page: `https://www.mexc.com/en-GB/fee`

Current relevant rows:

- VANRY:
  - `walletType="VANRY"`, transfer chain `Vanar`, deposit fee `0`, withdrawal minimum `0.02`, withdrawal fee `0.01`.
  - `walletType="ETH"`, transfer chain `Ethereum(ERC20)`, deposit fee `0`, withdrawal minimum `200`, withdrawal fee `80`.
- ULTIMA:
  - `walletType="ULTIMA"`, transfer chain `ULTIMA`, deposit fee `0`, withdrawal minimum `0.0001`, withdrawal fee `0.000025`.
  - `walletType="SMART"`, transfer chain `SMART BLOCKCHAIN`, deposit fee `0`, withdrawal minimum `0.006`, withdrawal fee `0.003`.

Operational read:

- VANRY is now the first route with public end-to-end network economics: MEXC ETH/ERC20 withdrawal fee 80 VANRY and min 200, Binance ERC20 deposits/withdrawals enabled, and KuCoin ERC20 deposits/withdrawals enabled. At current edge sizes this fee is negligible.
- ULTIMA still has no public common MEXC -> KuCoin network. MEXC fee rows are ULTIMA/SMART; KuCoin public row is BEP20. This reinforces the pre-positioned-inventory-only verdict for ULTIMA.

### VANRY Transfer-Fee Haircut Check

Applied the MEXC ETH/ERC20 withdrawal fee of 80 VANRY directly to live VANRY depth:

- VANRY MEXC -> Binance USDT at 10,000 USDT:
  - No-transfer-fee net: +368.148 bps.
  - After 80 VANRY withdrawal fee: +367.811 bps.
  - Fee haircut: 0.337 bps.
- VANRY MEXC -> KuCoin USDT at 5,000 USDT:
  - No-transfer-fee net: +295.351 bps.
  - After 80 VANRY withdrawal fee: +294.741 bps.
  - Fee haircut: 0.610 bps.
- VANRY MEXC -> Binance USDC at 5,000 USDC:
  - No-transfer-fee net: +801.504 bps.
  - After 80 VANRY withdrawal fee: +800.832 bps.
  - Fee haircut: 0.672 bps.

Verdict: VANRY withdrawal cost does not threaten the current public-book edge. Remaining VANRY blockers are account/region access, order-size compliance, inventory placement, and live execution automation; not public network economics.

## Checkpoint - 2026-05-29 06:45 CST

### Tail Exclusion Scan Result

Ran another corrected discovery pass after excluding all previously processed names.

- Markets scanned: 10,216.
- Same-lane routes scored: 2,048.
- Filtered top-of-book route candidates: 14.
- Endpoint errors: 0.

Batch depth and follow-up decisions:

- `BOS` KuCoin -> MEXC: `KILL`. Identity matches on ERC20 contract `0x13239c268beddd88ad0cb02050d3ff6a9d00de6d`, and KuCoin withdrawals are enabled with 2,500 BOS fee / 5,000 BOS minimum, but depth was positive only at 50 USDT: +82.508 bps at 50, -20.759 bps at 100, -541.567 bps at 250.
- `EGL1` KuCoin -> Bitget/Gate: `KILL`. Positive only at 50 USDT, then negative by 100-250 USDT. KuCoin -> Bitget: +11.796 bps at 50, -6.711 at 100. KuCoin -> Gate: +6.456 bps at 50, -19.056 at 100.
- `GROK` Gate -> MEXC: `KILL`. Positive at 50-100 USDT but negative by 250 USDT: +53.697 bps at 50, +48.305 at 100, -39.564 at 250.
- `ETN` MEXC -> KuCoin: `KILL`. Negative from 50 USDT: -56.036 bps at 50, -58.605 at 100.
- `QKC` Binance/Gate -> MEXC: `KILL`. Negative from 50 USDT on both routes. Binance -> MEXC: -94.098 bps at 50. Gate -> MEXC: -181.385 bps at 50.
- `UNION` MEXC -> Gate: `KILL`. Negative from 50 USDT: -54.049 bps at 50, -82.252 at 100.
- `NYM` Bitget -> Bybit: `KILL`. Positive at 50-100 USDT but negative by 250 USDT: +31.969 bps at 50, +14.428 at 100, -1.333 at 250.
- `POKT` Gate -> KuCoin: `KILL`. Deeply negative from 50 USDT: -430.804 bps at 50.

### JASMY Follow-Up

`JASMY` was the only tail candidate worth an extra persistence check because initial batch depth showed a small positive pocket at meaningful notional:

- Bybit -> MEXC: +29.054 bps through 250 USDT, +28.722 at 500, +23.860 at 1,000, +13.723 at 2,500, +2.881 at 5,000, then negative by 10,000.
- Binance -> MEXC: +32.756 bps through 1,000 USDT, +25.204 at 2,500, +19.740 at 5,000, +7.017 at 10,000.
- Bitget -> MEXC: +32.756 bps through 500 USDT, +26.713 at 1,000, +19.250 at 2,500, +15.541 at 5,000, then negative by 10,000.
- Crypto.com -> MEXC: negative from 50 USDT.

Public metadata was directionally clean: MEXC reports JASMY on ETH/ERC20 contract `0x7420B4b9a0110cdC71fB720908340C03F9Bc03EC`, MEXC fee-page API lists ETH/ERC20 withdrawal minimum 364.8 JASMY and fee 60 JASMY, and Bitget reports the same ERC20 contract with deposits/withdrawals enabled and withdrawal fee 129.87013 JASMY. Binance public market metadata confirms `JASMYUSDT` trading, but I did not find a current public Binance network-fee row.

Ran a 20-sample persistence retest from 2026-05-29 06:41:16 to 06:45:00 CST with zero endpoint errors. The signal disappeared before transfer costs:

- Binance -> MEXC:
  - 1,000 USDT: 0/20 positive, avg -40.157 bps, median -41.621, min -41.865.
  - 2,500 USDT: 0/20 positive, avg -47.784 bps, median -48.669, min -48.776.
  - 5,000 USDT: 0/20 positive, avg -50.698 bps, median -51.140, min -51.193.
  - 10,000 USDT: 0/20 positive, avg -55.418 bps, median -55.083, min -57.354.
- Bitget -> MEXC:
  - 1,000 USDT: 0/20 positive, avg -42.384 bps before withdrawal fee; avg -49.418 bps after Bitget's 129.87013 JASMY withdrawal fee.
  - 2,500 USDT: 0/20 positive, avg -58.328 bps before withdrawal fee; avg -61.140 bps after withdrawal fee.
  - 5,000 USDT: 0/20 positive, avg -65.086 bps before withdrawal fee; avg -66.492 bps after withdrawal fee.
  - 10,000 USDT: 0/20 positive, avg -73.319 bps before withdrawal fee; avg -74.022 bps after withdrawal fee.
- Bybit -> MEXC:
  - 1,000 USDT: 0/20 positive, avg -44.426 bps.
  - 2,500 USDT: 0/20 positive, avg -63.839 bps.
  - 5,000 USDT: 0/20 positive, avg -75.030 bps.
  - 10,000 USDT: 0/20 positive, avg -86.021 bps.

Verdict: no promotion. `JASMY` was a stale or short-lived book state, not a persistent route. The exclusion scan added no actionable candidate. The current 100x move is still VANRY operational proof and scanner automation, not more low-cap tail grinding.

## Checkpoint - 2026-05-29 06:51 CST

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 06:48:35 to 06:50:59 CST. Zero endpoint errors. VANRY rows include the current MEXC ETH/ERC20 withdrawal fee of 80 VANRY as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +557.372 bps, median +574.813 bps, min +397.553 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +288.674 bps, median +295.158 bps, min +186.532 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +424.332 bps, median +433.713 bps, min +326.369 bps.
  - 10,000 USDT: 20/20 positive, avg +188.336 bps, median +192.750 bps, min +111.057 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +531.164 bps, median +531.664 bps, min +389.500 bps.
  - 5,000 USDT after 80 VANRY fee: 19/20 positive, avg +176.951 bps, median +198.782 bps, min -6.995 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +840.004 bps, median +832.210 bps, min +628.647 bps.
  - 5,000 USDC after 80 VANRY fee: 19/20 positive, avg +624.451 bps, median +610.621 bps, min -39.902 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT as the top route with firm public-book cap 10,000 USDT.
- Keep ULTIMA firm cap at 5,000 USDT. The 10,000 USDT book improved to 20/20 positive in this refresh, but do not promote yet because the previous window had negative tails and the route is still operationally blocked by chain/rebalance proof.
- Downgrade VANRY MEXC -> KuCoin USDT firm cap back to 2,500 USDT. Keep 5,000 USDT as live-threshold-only because this window had a negative tail after transfer fee.
- Downgrade VANRY MEXC -> Binance USDC firm measurement cap back to 2,500 USDC. Keep 5,000 USDC as live-threshold-only because this window had a negative tail after transfer fee.

### MEXC VANRY Status Endpoint Audit

Inspected MEXC asset-page JavaScript for current deposit/withdraw status endpoints. The web app uses these relevant endpoints:

- Deposit token list: `/api/platform/asset/api/asset/deposit/currency/query`
- Withdraw token list: `/api/platform/asset/api/asset/withdraw/currency/query`
- Deposit config: `/api/platform/asset/api/deposit/query/deposit/config`
- Withdraw config: `/api/platform/asset/api/withdraw/query/config/v3`
- Deposit account support check: `/api/platform/asset/api/deposit/check/support/config/accountType/v2?coinId=...`
- Withdrawal chain matcher: `/api/platform/asset/api/withdraw/match/chains?coinId=...&address=...`

Public result:

- VANRY public coin id from `coin/introduce?coinName=VANRY`: `5e1d77a033064e60bfdbac3c93a9579f`.
- Unauthenticated calls to the deposit/withdraw token-list and config endpoints returned `401 Unauthorized`.
- `withdraw/match/chains` returns `400 param address is missing` without an address, but returns `401 Unauthorized` once a dummy address is supplied.

Verdict: current MEXC deposit/withdraw enabled flags remain account-gated. Public evidence is now bounded: current MEXC fee-page rows prove network fee/minimum data exists for VANRY ETH/ERC20, but they do not prove current account-level withdrawal availability. The next proof requires a logged-in browser/API read from Pedro's MEXC account or a manual UI screenshot; do not spend more public-only cycles on this blocker.

### Funding/Basis Refresh

Ran `python3 scripts/funding_probe.py` at 2026-05-29 06:56 CST.

- Routes scanned: 47 public spot/perp proxies.
- Venues: Binance USD-M, Bybit linear, OKX swaps, Coinbase International.
- Endpoint errors: 0.
- Elapsed: 19.8 seconds.

Best one-period proxies were still negative after fees and entry basis:

- Coinbase INTX BTC USDC: -7.336 bps over 1h proxy.
- Coinbase INTX DOGE USDC: -7.782 bps over 1h proxy.
- Coinbase INTX ETH USDC: -9.216 bps over 1h proxy.
- Coinbase INTX SOL USDC: -9.463 bps over 1h proxy.
- Binance TRX USDT negative-funding route: -10.180 bps over 8h proxy.
- Bybit TRX USDT negative-funding route: -10.515 bps over 8h proxy.
- OKX TRX USDT negative-funding route: -12.073 bps over 8h proxy.

Verdict: keep spot-perp funding as a monitor only. The funding/basis strategy class still does not beat the current VANRY spot route, and it adds margin, liquidation, borrow/inventory, and account-region complexity.

### Bitso MXN/Stables Refresh

Ran a corrected Bitso same-venue MXN/USD/USDT/stablecoin basis check at 2026-05-29 06:59 CST. Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`.

Best net results after conservative Bitso taker fees:

- PYUSD/MXN sell bid vs USD/MXN ask after two fees: -60.914 bps.
- USDT/MXN buy ask vs USD/MXN bid after two fees: -92.891 bps.
- RLUSD/MXN sell bid vs USD/MXN ask after two fees: -102.606 bps.
- MXN -> USD -> USDT -> MXN: -149.901 bps.
- MXN -> USDT -> USD -> MXN: -151.290 bps.

Verdict: Bitso same-venue stablecoin/FX triangles remain `KILL` for immediate execution. Keep Bitso as a `LATER` market monitor only.

## Checkpoint - 2026-05-29 07:02 CST

### Processed-Base Exclusion Scan

Ran a broad corrected top-of-book scan with already processed bases excluded.

- Markets scanned: 10,216.
- Same-lane USDT/USDC market keys: 3,500.
- Processed bases excluded: 110.
- New filtered top-of-book routes: 7.
- Endpoint errors: 0.

Depth results:

- `ACA` Gate -> MEXC: ticker snapshot ranked +55.210 bps net, but live depth was negative from 50 USDT: -81.599 bps at 50, -106.138 at 100, -137.052 at 250.
- `ES` Gate -> KuCoin/MEXC: Gate -> KuCoin was positive only at tiny size, then negative by 500 USDT: +30.512 bps at 50, +17.567 at 100, +6.684 at 250, -6.480 at 500. Gate -> MEXC was negative from 50 USDT.
- `IN` MEXC -> Bitget/KuCoin: both routes were negative from 50 USDT. MEXC -> Bitget: -13.249 bps at 50. MEXC -> KuCoin: -2.014 bps at 50.
- `OBOL` Gate -> MEXC: negative from 50 USDT and sell depth exhausted by 2,500 USDT: -28.665 bps at 50, -66.967 at 100, -146.257 at 250.
- `SBUXON` Gate -> MEXC: tiny tokenized-stock pocket only below 500 USDT: +15.004 bps at 50-250, -4.230 bps at 500.

Verdict: no promotion. Current broad-scan false positives are still stale ticker/depth artifacts, not actionable routes.

## Checkpoint - 2026-05-29 07:06 CST

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 07:03:53 to 07:06:17 CST. Zero endpoint errors. VANRY rows include the current MEXC ETH/ERC20 withdrawal fee of 80 VANRY as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +510.965 bps, median +514.638 bps, min +418.117 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +247.835 bps, median +245.205 bps, min +166.938 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +386.570 bps, median +394.375 bps, min +319.192 bps.
  - 10,000 USDT: 20/20 positive, avg +156.310 bps, median +165.056 bps, min +87.097 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +497.716 bps, median +502.362 bps, min +418.315 bps.
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +199.854 bps, median +206.638 bps, min +98.752 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +777.271 bps, median +746.580 bps, min +696.118 bps.
  - 5,000 USDC after 80 VANRY fee: 20/20 positive, avg +446.982 bps, median +492.423 bps, min +35.959 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT.
- Promote ULTIMA MEXC -> KuCoin USDT public-book watch cap back to 10,000 USDT after two consecutive 20/20 positive windows. This is not an operational promotion: execution remains pre-positioned-inventory-only until MEXC SMART/BEP20 rebalance proof exists.
- Keep VANRY MEXC -> KuCoin USDT firm cap at 2,500 USDT and 5,000 USDT live-threshold-only. The 5,000 bucket recovered, but the prior window had a negative tail.
- Keep VANRY MEXC -> Binance USDC firm measurement cap at 2,500 USDC and 5,000 USDC live-threshold-only. The 5,000 bucket recovered, but the minimum was only +35.959 bps after fee and the prior window had a negative tail.

## Checkpoint - 2026-05-29 07:21 CST

### Account/Region Gate

The route work hit a more important blocker than book depth: current official regional evidence makes the promoted MEXC/KuCoin routes non-executable for a U.S.-resident account.

- MEXC official restricted-jurisdiction page, updated Apr 17, 2026, lists the United States among prohibited jurisdictions and says MEXC does not accept user registrations or trading applications from those areas: `https://www.mexc.com/learn/article/mexc-restricted-countries-complete-list-of-prohibited-limited-regions/1?handleDefaultLocale=keep`.
- KuCoin Terms of Use, last updated Jan 29, 2026, require users to not be residents of or registered in restricted locations, and the restricted list includes the United States and U.S. territories: `https://www.kucoin.com/legal/terms-of-use`.
- Binance.US is not a VANRY fallback. `https://api.binance.us/api/v3/exchangeInfo?symbol=VANRYUSDT` and `VANRYUSDC` returned `{"code":-1121,"msg":"Invalid symbol."}`; full Binance.US `exchangeInfo` returned 623 symbols with no `VANRY`; the official supported-crypto page also contains no `VANRY`: `https://support.binance.us/hc/en-us/articles/360049417674-List-of-supported-cryptocurrencies`.

Verdict: the scanner should keep watching VANRY and ULTIMA, but execution work is blocked until Pedro confirms compliant, non-U.S.-restricted account access and logged-in MEXC withdrawal status. If the only available account path is U.S.-resident, kill the current MEXC/KuCoin execution path and do not build trading automation around it.

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 07:17:53 to 07:20:54 CST. Zero endpoint errors. Average REST RTT was 342 ms; max RTT was 761 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +608.895 bps, median +604.037 bps, min +590.043 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +335.844 bps, median +332.767 bps, min +302.966 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +571.989 bps, median +565.842 bps, min +549.809 bps.
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +200.446 bps, median +190.123 bps, min +167.040 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +858.697 bps, median +848.734 bps, min +826.696 bps.
  - 5,000 USDC after 80 VANRY fee: 20/20 positive, avg +659.351 bps, median +679.419 bps, min +395.431 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +452.052 bps, median +457.158 bps, min +322.974 bps.
  - 10,000 USDT: 19/20 positive, avg +210.970 bps, median +226.221 bps, min -9.418 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Promote VANRY MEXC -> KuCoin USDT public-book cap back to 5,000 USDT after two consecutive clean windows; still account/region and inventory gated.
- Promote VANRY MEXC -> Binance USDC measurement cap back to 5,000 USDC after two consecutive clean windows; still account/region gated.
- Downgrade ULTIMA MEXC -> KuCoin USDT public-book cap back to 5,000 USDT. The 10,000 USDT bucket is live-threshold-only again, and operational execution remains blocked by the MEXC SMART/BEP20 rebalance question.

## Checkpoint - 2026-05-29 07:29 CST

### U.S.-Available Venue Substitution Scan

Ran a public top-of-book substitution scan after the MEXC/KuCoin regional gate. Scope: Binance.US, Coinbase Exchange, Kraken, Gemini, and Bitstamp.

- Markets scanned: 1,971.
- Common USD/USDT/USDC market keys: 378.
- Endpoint errors: 0.
- Conservative fee assumptions: Binance.US 10 bps, Coinbase 120 bps, Kraken 40 bps, Gemini 120 bps, Bitstamp 40 bps, plus 2-4 bps latency.

Result: no promotion.

Liquid majors were negative after fees:

- BTC/USD Bitstamp -> Binance.US: -43.075 bps.
- BTC/USDT Bitstamp -> Binance.US: -46.248 bps.
- SOL/USD Bitstamp -> Binance.US: -47.106 bps.
- HYPE/USD Bitstamp -> Binance.US: -47.374 bps.
- USDT/USD Kraken -> Binance.US: -50.795 bps.

Long-tail positives were false positives:

- `LIT` Kraken -> Bitstamp: live depth looked positive through 1,000 USD, but Kraken public pages identify `LIT` as Litentry while Bitstamp trading-pair info describes `LIT/USD` as Lighter / U.S. dollar. `KILL`.
- `VELO` Kraken -> Coinbase: live depth looked positive through 5,000 USD, but Kraken lists `VELO` as Velo and separately lists Velodrome Finance as `VELODROME`; Coinbase Exchange currency metadata identifies `VELO` as Velodrome Finance on Optimism contract `0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db`. `KILL`.
- `SUP` Kraken -> Coinbase: live depth looked positive through 5,000 USD, but Kraken public pages identify `SUP` as Superp while Coinbase Exchange currency metadata identifies `SUP` as Superfluid on Base contract `0xa69f80524381275A7fFdb3AE01c54150644c8792`. `KILL`.
- `GWEI` Kraken -> Coinbase: top-of-book net was only +14.403 bps and live depth was negative from 50 USD (-223.485 bps). `KILL`.
- `TRAC` Kraken -> Bitstamp: top-of-book net was only +1.337 bps and live depth was negative from 50 USD (-77.963 bps). `KILL`.

Verdict: no U.S.-available static taker route currently substitutes for VANRY. If Pedro is limited to U.S.-resident accounts, the next viable angle is not static cross-CEX taker arb; it is maker/rebate/event-window monitoring on U.S.-available venues or a completely different strategy class.

### Maker/Rebate Fee Check

Checked whether U.S.-available maker/rebate economics can rescue the killed static scan.

- Binance.US is the only strong public retail-fee improvement found: its Apr 22, 2026 announcement says Advanced Spot fees are 0% maker and 0.02% taker for every user: `https://blog.binance.us/zero-fee-trading/`.
- Binance.US also has a Market Maker Program with possible rebates, but that is a programmatic eligibility path, not a default public fee assumption: `https://support.binance.us/en/articles/9842933-what-is-the-binance-us-market-maker-program`.
- Kraken publishes a spot maker-rebate table, but public rebate starts only at high 30-day volume on selected lower-liquidity pairs; low-tier spot remains 25 bps maker / 40 bps taker: `https://www.kraken.com/features/fee-schedule`.
- Coinbase Advanced VIP's best public spot tier shows 0 bps maker / 3.5 bps taker at VIP 6, but that requires institutional-scale qualification: `https://www.coinbase.com/advanced-vip`.

Verdict: `KILL` immediate U.S.-available maker/rebate rescue. Binance.US 0 maker is useful for a future post-only scanner, but it does not flip the 07:29 liquid static routes by itself. Any maker strategy now requires queue/fill probability, cancel/replace, adverse-selection controls, and account-specific fee proof.

## Checkpoint - 2026-05-29 07:39 CST

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 07:36:10 to 07:39:15 CST. Zero endpoint errors. Average REST RTT was 367 ms; max RTT was 939 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +631.078 bps, median +635.498 bps, min +537.922 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +383.266 bps, median +383.912 bps, min +313.524 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +613.227 bps, median +603.401 bps, min +549.855 bps.
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +264.939 bps, median +275.924 bps, min +127.310 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +903.328 bps, median +908.837 bps, min +806.101 bps.
  - 5,000 USDC after 80 VANRY fee: 20/20 positive, avg +458.736 bps, median +486.921 bps, min +52.608 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +427.839 bps, median +453.916 bps, min +329.718 bps.
  - 10,000 USDT: 20/20 positive, avg +159.973 bps, median +190.413 bps, min +36.634 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Keep VANRY MEXC -> KuCoin USDT public-book cap at 5,000 USDT; still account/region and inventory gated.
- Keep VANRY MEXC -> Binance USDC measurement cap at 5,000 USDC; still account/region gated. The 5,000 USDC minimum is positive but thin, so keep it below the USDT Binance route in priority.
- Keep ULTIMA MEXC -> KuCoin USDT firm public-book cap at 5,000 USDT. The 10,000 USDT bucket recovered to 20/20 positive, but keep it live-threshold-only until another clean window follows the prior negative tail, and do not treat it as operational while the MEXC SMART/BEP20 rebalance question is unresolved.

### Funding/Basis Refresh

Ran `python3 scripts/funding_probe.py` at 2026-05-29 07:42 CST.

- Routes scanned: 47 public spot/perp proxies.
- Venues: Binance USD-M, Bybit linear, OKX swaps, Coinbase International.
- Endpoint errors: 0.
- Elapsed: 23.245 seconds.

Best one-period proxies remained negative after entry basis and round-trip fees:

- Coinbase INTX BTC USDC: -6.535 bps over 1h proxy.
- Coinbase INTX ETH USDC: -8.212 bps over 1h proxy.
- Coinbase INTX XRP USDC: -10.401 bps over 1h proxy.
- Coinbase INTX SOL USDC: -10.444 bps over 1h proxy.
- Coinbase INTX DOGE USDC: -10.832 bps over 1h proxy.
- Bybit TRX USDT negative-funding route: -18.189 bps over 8h proxy.

Verdict: keep spot-perp funding as a monitor only. Coinbase INTX BTC improved from the prior -7.336 bps reading, but no route is positive and the strategy still adds margin, liquidation, borrow/inventory, and account-region complexity.

### Bitso MXN/Stables Refresh

Ran a corrected Bitso same-venue MXN/USD/USDT/stablecoin basis check at 2026-05-29 07:43 CST. Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`. Endpoint errors: 0.

Top-of-book reference:

- `usd_mxn`: bid 17.347, ask 17.350.
- `usdt_mxn`: bid 17.326, ask 17.330.
- `usd_usdt`: bid 1.0009, ask 1.0011.

Best net results after conservative Bitso taker fees:

- PYUSD/MXN sell bid vs USD/MXN ask after two fees: -61.841 bps.
- USDT/MXN buy ask vs USD/MXN bid after two fees: -89.791 bps.
- RLUSD/MXN sell bid vs USD/MXN ask after two fees: -101.785 bps.
- MXN -> USDT -> USD -> MXN: -130.714 bps.
- MXN -> USD -> USDT -> MXN: -173.687 bps.

Verdict: Bitso same-venue stablecoin/FX triangles remain `KILL` for immediate execution. Keep Bitso as a `LATER` market monitor only.

## Checkpoint - 2026-05-29 07:48 CST

### Fresh Global Public Probe

Ran a fresh public market probe for event-window candidates.

- Markets scanned: 10,216.
- Filtered top-of-book watch rows: 99.
- Endpoint errors: 0.
- Venues: Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, Bitso.

Depth-checked the highest new rows not already handled by the current VANRY/ULTIMA queue:

- `TBC` MEXC -> Gate:
  - Live depth after MEXC 5 bps taker and Gate 20 bps fee was positive through 5,000 USDT: +530.107 bps at 50, +496.723 bps at 500, +444.676 bps at 1,000, +361.165 bps at 2,500, +196.087 bps at 5,000.
  - Identity matched directionally: MEXC identifies TBC as Turingbitchain on chain `TBC`; Gate identifies TBC as TuringBitChain on chain `TBC`.
  - Gate public currency endpoint reports `deposit_disabled=true`, so MEXC -> Gate transfer/rebalance is blocked. MEXC public fee page returned no TBC withdrawal-fee row.
  - Verdict: `KILL` as a repeatable direct route; `LATER` only as a pre-positioned Gate inventory liquidation watch.
- `YFII` MEXC -> Gate: negative from 50 USDT (-232.151 bps). `KILL`.
- `DCK` Gate -> MEXC: positive only at 50 USDT (+128.051 bps), negative by 100 USDT. `KILL`.
- `DN` KuCoin -> Gate: negative from 50 USDT (-104.113 bps). `KILL`.
- `AO` Bybit -> Gate: positive through 1,000 USDT (+125.928 bps) but negative by 2,500 USDT. `KILL` for current queue.
- `AO` MEXC -> Gate: positive only through 500 USDT (+30.972 bps), negative by 1,000 USDT. `KILL`.
- `HONEY` MEXC -> Gate: negative from 50 USDT (-50.480 bps). `KILL`.
- `AVL` MEXC -> Gate: negative from 50 USDT (-92.154 bps). `KILL`.
- `QAIT` Gate -> KuCoin: positive through 250 USDT (+45.167 bps), negative by 500 USDT. `KILL`.

Verdict: no new promotion. `TBC` is the only fresh public-book route worth keeping as a pre-positioned-inventory watch, but the actual compounding move remains VANRY account/region proof and scanner automation.

### TBC Short Persistence Check

Ran a 10-sample TBC-only persistence check from 2026-05-29 07:48:32 to 07:49:30 CST. Zero endpoint errors. Average REST RTT was 634 ms; max RTT was 927 ms.

- 1,000 USDT: 10/10 positive, avg +448.317 bps, median +448.317 bps, min +444.676 bps.
- 2,500 USDT: 10/10 positive, avg +365.364 bps, median +365.364 bps, min +361.165 bps.
- 5,000 USDT: 10/10 positive, avg +198.175 bps, median +198.175 bps, min +196.087 bps.

Verdict unchanged: TBC remains `LATER` / pre-positioned-inventory-only and `KILL` as a repeatable direct route because Gate deposits are disabled.

## Checkpoint - 2026-05-29 07:54 CST

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 07:50:48 to 07:53:52 CST. Zero endpoint errors. Average REST RTT was 365 ms; max RTT was 904 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +670.417 bps, median +640.592 bps, min +494.415 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +329.739 bps, median +315.849 bps, min +198.804 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +678.036 bps, median +682.861 bps, min +573.681 bps.
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +338.403 bps, median +315.598 bps, min +147.427 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +870.145 bps, median +875.341 bps, min +705.368 bps.
  - 5,000 USDC after 80 VANRY fee: 19/20 positive, avg +569.820 bps, median +637.354 bps, min -240.917 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +418.842 bps, median +433.213 bps, min +347.424 bps.
  - 10,000 USDT: 20/20 positive, avg +172.344 bps, median +181.786 bps, min +124.205 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Keep VANRY MEXC -> KuCoin USDT public-book cap at 5,000 USDT; still account/region and inventory gated.
- Downgrade VANRY MEXC -> Binance USDC firm measurement cap back to 2,500 USDC. Keep 5,000 USDC live-threshold-only after the latest negative-tail sample.
- Promote ULTIMA MEXC -> KuCoin USDT public-book watch cap back to 10,000 USDT after two clean windows following the prior negative tail. This is not an operational promotion; execution remains blocked by the MEXC SMART/BEP20 rebalance question.

## Checkpoint - 2026-05-29 08:06 CST

### U.S.-Available Corrected-Fee Retest

Retested the prior best liquid U.S.-available rows after correcting Binance.US public taker fee from the earlier conservative 10 bps assumption to 2 bps. This does not rescue the U.S. static substitution path.

- BTC/USD Bitstamp -> Binance.US: -38.074 bps.
- BTC/USDT Bitstamp -> Binance.US: -47.772 bps.
- SOL/USD Bitstamp -> Binance.US: -44.893 bps.
- HYPE/USD Bitstamp -> Binance.US: -53.955 bps.
- USDT/USD Kraken -> Binance.US: -42.495 bps.

Verdict: keep U.S.-available static taker substitution killed. Binance.US stays useful for future post-only/event-window monitoring, not immediate static arb.

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 08:03:20 to 08:05:55 CST. Zero endpoint errors. Average REST RTT was 338 ms; max RTT was 766 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +734.388 bps, median +706.358 bps, min +387.645 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +366.562 bps, median +386.150 bps, min +225.977 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +729.932 bps, median +740.520 bps, min +364.676 bps.
  - 5,000 USDT after 80 VANRY fee: 19/20 positive, avg +374.543 bps, median +359.060 bps, min -18.398 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +980.902 bps, median +990.513 bps, min +923.892 bps.
  - 5,000 USDC after 80 VANRY fee: 20/20 positive, avg +765.741 bps, median +794.771 bps, min +231.561 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +364.926 bps, median +393.661 bps, min +213.670 bps.
  - 10,000 USDT: 17/20 positive, avg +132.559 bps, median +168.648 bps, min -59.587 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Downgrade VANRY MEXC -> KuCoin USDT firm cap back to 2,500 USDT. Keep 5,000 USDT live-threshold-only after the latest negative-tail sample.
- Keep VANRY MEXC -> Binance USDC firm measurement cap at 2,500 USDC. The 5,000 USDC bucket recovered to 20/20 positive, but it needs another clean window after the prior negative tail.
- Downgrade ULTIMA MEXC -> KuCoin USDT public-book watch cap back to 5,000 USDT. Operational execution remains blocked by the MEXC SMART/BEP20 rebalance question.

## Checkpoint - 2026-05-29 08:12 CST

### Fresh Probe: Crypto.com -> Bitfinex USD Majors

Ran a fresh public market probe at 2026-05-29 08:09 CST across the existing 10-venue adapter set. It returned 10,216 public markets with zero endpoint errors. The only sane top-of-book positives outside the existing VANRY queue were Crypto.com USD buy -> Bitfinex USD sell on majors.

Current official Bitfinex fee evidence changes the old fee-blocked assumption: the Bitfinex fee page lists spot maker/taker fees as zero. Official Bitfinex support also says U.S. persons cannot use the platform, so the route is account-gated for U.S.-resident execution.

Live depth after Crypto.com 7.5 bps taker, Bitfinex 0 bps taker, and a 4 bps USD-lane latency haircut:

- BTC/USD Crypto.com -> Bitfinex: +1.839 bps at 1,000 USD, +1.800 at 5,000, +1.795 at 10,000, +1.651 at 25,000.
- ETH/USD Crypto.com -> Bitfinex: negative from 1,000 USD (-4.548 bps).
- XRP/USD Crypto.com -> Bitfinex: negative from 1,000 USD (-8.011 bps).
- SOL/USD Crypto.com -> Bitfinex: negative from 1,000 USD (-3.494 bps).

Ran a 10-sample BTC-only persistence check from 08:10:32 to 08:11:18 CST. Zero endpoint errors. Average REST RTT was 690 ms; max RTT was 933 ms.

- 1,000 USD: 0/10 positive, avg -1.738 bps, median -1.475 bps, min -4.783 bps.
- 5,000 USD: 0/10 positive, avg -1.797 bps, median -1.531 bps, min -4.893 bps.
- 10,000 USD: 0/10 positive, avg -1.854 bps, median -1.613 bps, min -4.946 bps.
- 25,000 USD: 0/10 positive, avg -2.063 bps, median -1.837 bps, min -5.095 bps.

Verdict: `KILL` immediate Crypto.com -> Bitfinex execution. The top-of-book pocket was too small and failed persistence before operational work, and Bitfinex access is not available to U.S. persons.

## Checkpoint - 2026-05-29 08:13 CST

### Funding/Basis Refresh

Ran `python3 scripts/funding_probe.py` at 2026-05-29 08:13 CST.

- Routes scanned: 47 public spot/perp proxies.
- Venues: Binance USD-M, Bybit linear, OKX swaps, Coinbase International.
- Endpoint errors: 0.
- Elapsed: 19.436 seconds.

Best one-period proxies remained negative after entry basis and round-trip fees:

- Coinbase INTX SOL USDC: -7.982 bps over 1h proxy.
- Coinbase INTX BTC USDC: -8.168 bps over 1h proxy.
- Coinbase INTX ETH USDC: -8.759 bps over 1h proxy.
- Coinbase INTX DOGE USDC: -11.860 bps over 1h proxy.
- Coinbase INTX XRP USDC: -11.950 bps over 1h proxy.
- Binance WLD USDT negative-funding route: -12.436 bps over 8h proxy.

Verdict: keep spot-perp funding as a monitor only. No route is positive, and the best proxy worsened versus the 07:42 refresh.

## Checkpoint - 2026-05-29 08:15 CST

### Bitso MXN/Stables Refresh

Ran a corrected Bitso same-venue MXN/USD/USDT/stablecoin basis check at 2026-05-29 08:14 CST. Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`. Endpoint errors: 0.

Top-of-book reference:

- `usd_mxn`: bid 17.357, ask 17.358.
- `usdt_mxn`: bid 17.341, ask 17.350.
- `usd_usdt`: bid 1.0006, ask 1.0009.

Best net results after conservative 50 bps per Bitso taker leg:

- PYUSD/MXN sell bid vs USD/MXN ask after two fees: -59.255 bps.
- USD/MXN sell bid vs USDT/MXN buy ask after two fees: -95.756 bps.
- RLUSD/MXN sell bid vs USD/MXN ask after two fees: -99.180 bps.
- MXN -> USD -> USDT -> MXN: -152.994 bps.
- MXN -> USDT -> USD -> MXN: -154.138 bps.

Verdict: Bitso same-venue stablecoin/FX triangles remain `KILL` for immediate execution. Keep Bitso as a `LATER` market monitor only.

## Checkpoint - 2026-05-29 08:19 CST

### Top-Route Refresh

Ran another 20-sample refresh from 2026-05-29 08:16:13 to 08:18:47 CST. Zero endpoint errors. Average REST RTT was 334 ms; max RTT was 838 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +714.478 bps, median +707.131 bps, min +498.381 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +333.599 bps, median +338.015 bps, min +103.743 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +719.753 bps, median +706.190 bps, min +598.177 bps.
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +332.214 bps, median +324.395 bps, min +63.884 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +938.581 bps, median +969.931 bps, min +619.614 bps.
  - 5,000 USDC after 80 VANRY fee: 18/20 positive, avg +694.238 bps, median +852.114 bps, min -240.586 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +421.490 bps, median +429.266 bps, min +348.127 bps.
  - 10,000 USDT: 20/20 positive, avg +182.428 bps, median +178.313 bps, min +115.511 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Keep VANRY MEXC -> KuCoin USDT firm cap at 2,500 USDT; the 5,000 USDT bucket recovered but needs another clean window after the 08:06 negative tail.
- Keep VANRY MEXC -> Binance USDC firm measurement cap at 2,500 USDC after another 5,000 USDC negative-tail sample.
- Keep ULTIMA MEXC -> KuCoin USDT public-book watch cap at 5,000 USDT. The 10,000 USDT bucket recovered but needs another clean window after the 08:06 negative tail, and operational execution remains blocked by the MEXC SMART/BEP20 rebalance question.

## Checkpoint - 2026-05-29 08:25 CST

### Hard-Filter Discovery: ESPORTS/RAVE Pre-Positioned Pockets

Ran a hard-filter public discovery pass at 2026-05-29 08:21 CST. Scope was the existing 10-venue adapter set: 10,216 markets, zero endpoint errors. Filter retained 148 plausible-range top-of-book rows after excluding already processed bases and absurd same-ticker spreads.

Depth snapshot highlights:

- ESPORTS MEXC -> Gate: positive through 5,000 USDT, from +3861.479 bps at 50 USDT to +2349.071 bps at 5,000 USDT.
- RAVE Bitget -> KuCoin: positive through 5,000 USDT, from +1616.779 bps at 50 USDT to +1478.349 bps at 5,000 USDT.
- RAVE Bitget -> Gate: positive through 5,000 USDT, from +2153.920 bps at 50 USDT to +260.905 bps at 5,000 USDT.
- RWA MEXC/Gate/Bitget -> KuCoin looked positive in depth, but metadata killed it as a same-ticker collision.
- ARTFI, UPC, PHB, GUA, POWER, and NERO were rejected by deposit status, depth capacity, or both.

Identity and status checks:

- ESPORTS: MEXC `exchangeInfo` identifies `Yooldo Games`, BSC contract `0xF39e4b21c84e737Df08e2C3b32541d856f508E48`; Gate identifies `Yooldo` on the same BSC contract. Gate, KuCoin, and Bitget all report ESPORTS deposits disabled.
- RAVE: MEXC `exchangeInfo` identifies `RaveDAO`, ERC20 contract `0x17205fab260a7a6383a81452cE6315A39370Db97`; Bitget, KuCoin ERC20, and Gate ETH metadata point to the same contract. KuCoin and Gate deposits are disabled, and Bitget reports `rechargeable=false`.
- RWA: MEXC/Gate/Bitget identify BSC Allo contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`; KuCoin identifies Base RWA Inc contract `0xe2b1dc2d4a3b4e59fdf0c47b71a7a86391a8b35a`. `KILL`.

Ran a 10-sample ESPORTS/RAVE persistence check from 08:23:41 to 08:24:29 CST. Zero endpoint errors. Average REST RTT was 554 ms; max RTT was 1,014 ms.

- ESPORTS MEXC -> Gate:
  - 1,000 USDT: 10/10 positive, avg +3744.739 bps, median +3746.033 bps, min +3716.412 bps.
  - 2,500 USDT: 10/10 positive, avg +3527.508 bps, median +3526.280 bps, min +3486.537 bps.
  - 5,000 USDT: 10/10 positive, avg +2400.213 bps, median +2404.579 bps, min +2361.826 bps.
- RAVE Bitget -> KuCoin:
  - 1,000 USDT: 10/10 positive, avg +1582.946 bps, median +1584.722 bps, min +1563.853 bps.
  - 2,500 USDT: 10/10 positive, avg +1530.014 bps, median +1531.274 bps, min +1508.977 bps.
  - 5,000 USDT: 10/10 positive, avg +1482.521 bps, median +1482.790 bps, min +1465.754 bps.
- RAVE Bitget -> Gate:
  - 1,000 USDT: 10/10 positive, avg +1529.861 bps, median +1526.263 bps, min +1467.518 bps.
  - 2,500 USDT: 10/10 positive, avg +562.168 bps, median +558.281 bps, min +526.629 bps.
  - 5,000 USDT: 10/10 positive, avg +194.290 bps, median +191.007 bps, min +171.865 bps.

Verdict: ESPORTS and RAVE are `LATER` / pre-positioned-inventory-only watch cases. `KILL` repeatable direct transfer execution while sell-venue deposits are disabled. RWA is killed as a same-ticker different-contract route.

## Checkpoint - 2026-05-29 08:30 CST

### Deposit-Enabled Follow-Up

Ran a deposit-enabled follow-up on the 08:21 hard-filter output at 08:28-08:30 CST. Scope was a fresh `scripts/market_probe.py` import with 10,215 markets, zero endpoint errors, and the top 80 filtered rows inspected. The goal was to separate blocked-deposit pockets from rows where sell deposits were enabled or MEXC status was unknown.

The largest apparent row was invalid:

- Gate `AI` metadata identifies Sleepless AI on BSC contract `0xBDA011D7F8EC00F66C1923B049B94c67d148d8b2`, with deposits and withdrawals enabled.
- KuCoin `AI` metadata identifies Gensyn on ERC20 contract `0x4d7078ddd6ccfed2f85db5b7d3ff16828d378d48`, with deposits and withdrawals enabled.
- MEXC `AIUSDT` metadata identifies Gensyn with ERC20 contract `0x4d7078DDd6cCFED2F85dB5B7D3Ff16828d378d48`, spot allowed, taker fee 5 bps.
- Gate AI -> KuCoin AI still measured +1463.338 bps at 50 USDT and +727.423 bps at 5,000 USDT.
- Gate AI -> MEXC AI still measured +1502.245 bps at 50 USDT and +795.461 bps at 5,000 USDT.
- Verdict: `KILL` Gate AI -> KuCoin/MEXC AI as a Sleepless AI vs Gensyn same-ticker collision.

Deposit-enabled live-depth rows also failed:

- ALEX KuCoin -> Gate: +39.357 bps at 50 USDT, -111.608 bps at 100 USDT, -339.981 bps at 250 USDT.
- PUSH MEXC -> KuCoin: +85.498 bps at 50 USDT, +40.074 bps at 100 USDT, -14.456 bps at 250 USDT.
- SAMO MEXC -> Gate: negative from 50 USDT (-595.703 bps).
- SNEK MEXC -> Bitget: +77.946 bps at 50 USDT, +51.783 bps at 100 USDT, +22.013 bps at 250 USDT, -9.314 bps at 500 USDT.
- SNEK Gate -> Bitget: +84.522 bps at 50 USDT, +42.965 bps at 100 USDT, -41.524 bps at 250 USDT.
- OGPU MEXC -> Gate: negative from 50 USDT (-69.934 bps).
- REACT KuCoin -> Gate: +99.878 bps at 50 USDT, +68.902 bps at 100 USDT, -7.317 bps at 250 USDT.
- AFC MEXC -> Bitget: negative from 50 USDT (-4.707 bps).
- ROUTE KuCoin -> Gate: negative from 50 USDT (-295.323 bps).

Verdict: no direct promotion from the deposit-enabled follow-up. The only large positive row was a same-ticker collision, and the real same-asset rows either turned negative by 250-500 USDT or were negative from the first bucket.

## Checkpoint - 2026-05-29 08:36 CST

### Top-Route Refresh

Ran another 20-sample public depth refresh from 2026-05-29 08:33:56 to 08:35:42 CST. Zero endpoint errors. Average REST RTT was 555 ms; max RTT was 757 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +776.240 bps, median +750.199 bps, min +544.820 bps.
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +411.982 bps, median +392.735 bps, min +279.530 bps.
- VANRY MEXC -> KuCoin USDT:
  - 2,500 USDT after 80 VANRY fee: 20/20 positive, avg +767.151 bps, median +788.295 bps, min +629.933 bps.
  - 5,000 USDT after 80 VANRY fee: 20/20 positive, avg +314.227 bps, median +327.305 bps, min +90.449 bps.
- VANRY MEXC -> Binance USDC:
  - 2,500 USDC after 80 VANRY fee: 20/20 positive, avg +1036.801 bps, median +1051.977 bps, min +951.777 bps.
  - 5,000 USDC after 80 VANRY fee: 20/20 positive, avg +735.275 bps, median +846.203 bps, min +265.036 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 20/20 positive, avg +434.868 bps, median +446.588 bps, min +316.276 bps.
  - 10,000 USDT: 20/20 positive, avg +187.755 bps, median +210.437 bps, min +1.226 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Restore VANRY MEXC -> KuCoin USDT firm public-book cap to 5,000 USDT for non-U.S. compliant setups, with a live threshold check before action. This is the second clean 20/20 window after the 08:06 negative-tail sample.
- Keep VANRY MEXC -> Binance USDC firm measurement cap at 2,500 USDC. The 5,000 USDC bucket recovered, but it needs another clean window after the 08:19 negative tail.
- Keep ULTIMA MEXC -> KuCoin USDT public-book watch cap at 5,000 USDT. The 10,000 USDT bucket was 20/20 positive but had a near-zero +1.226 bps tail and still lacks MEXC SMART/BEP20 rebalance proof.

## Checkpoint - 2026-05-29 08:40 CST

### Processed-Base Exclusion Discovery

Ran a fresh processed-base exclusion scan at 08:39 CST. Scope: 10,213 public markets across the existing 10-venue adapter set, zero endpoint errors, and 58 filtered long-tail rows after excluding already processed bases and requiring positive top-of-book net spread.

Top filtered rows were mostly KuCoin/Gate -> MEXC sell routes: `SHR`, `LKI`, `BNKR`, `GHX`, `CWEB`, plus `WOJAK`, `PYBOBO`, `KEKIUS`, `DEVVE`, and `ASSET`.

Optimistic live depth before transfer fees:

- SHR KuCoin -> MEXC: negative from 50 USDT (-11.371 bps).
- LKI KuCoin -> MEXC: negative from 50 USDT (-513.408 bps).
- BNKR Gate -> MEXC: +198.980 bps at 50 USDT, +77.996 bps at 500 USDT, -9.392 bps at 1,000 USDT.
- BNKR KuCoin -> MEXC: +202.815 bps at 50-250 USDT, +78.430 bps at 500 USDT, -10.959 bps at 1,000 USDT.
- GHX KuCoin/Gate -> MEXC: positive only below 250 USDT and negative by 250 USDT.
- CWEB KuCoin -> MEXC: positive only through 250 USDT and negative by 500 USDT.
- WOJAK MEXC -> Gate: negative from 50 USDT (-115.496 bps).
- PYBOBO MEXC -> Bybit: positive only at 50-100 USDT and negative by 250 USDT.
- KEKIUS, DEVVE, and ASSET: positive only at tiny buckets and negative by 100-1,000 USDT.

Verdict: no promotion. The latest broad scan reinforces the same failure pattern: top-of-book long-tail positives collapse under depth before they can cover transfer and operational overhead. Keep focus on VANRY operational proof and automated event-window detection.

## Checkpoint - 2026-05-29 08:48 CST

### Event-Window Sampler and SPX Follow-Up

Ran an 8-sample event-window top-of-book sampler from 08:41:27 to 08:44:02 CST across the main public venues, excluding Bitso and already processed bases. Endpoint errors: zero. The sampler retained rows with repeated positive top-of-book net spread, then live-depth checked the persistent set.

Most persistent rows failed depth:

- TYCOON Gate -> MEXC appeared in 8/8 samples with median top-of-book net +248.570 bps, but live depth was negative from 50 USDT (-206.686 bps).
- NOS Gate -> MEXC appeared in 8/8 samples and was positive through 1,000 USDT (+12.984 bps), but negative by 2,500 USDT before transfer fees.
- VOOI KuCoin/MEXC/Bitget -> Bybit appeared in 8/8 samples but was negative by 250-1,000 USDT depending on buy venue.
- SMURFCAT, SIX, ATR, MAPO, GAIB, BXN, XELS, WMTX, RMV, WARD, and IDEX failed live depth by 50-1,000 USDT.

SPX was the only measured survivor.

Identity/status evidence:

- KuCoin `SPX` full name is SPX6900. ERC20 contract `0xe0f63a424a4439cbe457d80e4f4b51ad25b2c56c` has deposits and withdrawals enabled; KuCoin also lists a SOL chain contract with deposits/withdrawals disabled.
- Gate `SPX` identifies SPX6900 on ETH with the same ERC20 contract and deposits/withdrawals enabled.
- MEXC `SPXUSDT` identifies SPX6900 with the same ERC20 contract, spot trading allowed, and 5 bps taker fee. MEXC coin metadata reports `ct="ETH"`.
- MEXC public fee API lists SPX ERC20 withdrawal fee `3` SPX, minimum withdrawal `21.6` SPX, deposit fee `0`.
- Bybit public instruments confirm `SPXUSDT` is trading, but Bybit coin/withdrawal metadata returns `apiKey is missing`; Bybit transfer status and contract identity remain account-gated.

Ran a 10-sample SPX depth persistence check from 08:46:31 to 08:47:27 CST. Zero endpoint errors. Average REST RTT was 1,127 ms; max RTT was 1,419 ms.

- SPX Bybit -> KuCoin before any Bybit transfer-fee haircut:
  - 1,000 USDT: 10/10 positive, avg +54.558 bps, median +55.120 bps, min +50.381 bps.
  - 2,500 USDT: 10/10 positive, avg +40.231 bps, median +40.002 bps, min +36.333 bps.
  - 5,000 USDT: 10/10 positive, avg +18.703 bps, median +18.315 bps, min +14.532 bps.
  - 10,000 USDT: 0/10 positive, avg -11.459 bps.
- SPX MEXC -> KuCoin after 3 SPX MEXC withdrawal fee:
  - 1,000 USDT: 10/10 positive, avg +30.325 bps, median +30.137 bps, min +25.687 bps.
  - 2,500 USDT: 10/10 positive, avg +12.974 bps, median +14.253 bps, min +4.044 bps.
  - 5,000 USDT: 0/10 positive, avg -33.411 bps.

Verdict: promote SPX to `MEASURE` only. It is below VANRY/ULTIMA because the edge is small, Bybit transfer metadata is account-gated, MEXC wallet status is account-gated, and MEXC/KuCoin remain region-gated. Practical watch caps: Bybit -> KuCoin 5,000 USDT optimistic before transfer-fee proof; MEXC -> KuCoin 1,000 USDT firm measurement cap, with 2,500 USDT live-threshold-only.

## Checkpoint - 2026-05-29 08:53 CST

### Watch-Route Refresh

Ran a 20-sample watch-route refresh from 08:50:00 to 08:52:30 CST across VANRY, ULTIMA, and SPX. There were seven public endpoint errors, all on KuCoin books: `VANRY`, `ULTIMA`, or `SPX` timeouts and one `SPX` 502. Average REST RTT was 2,739 ms; max RTT was 8,150 ms. VANRY rows include the current 80 VANRY MEXC ETH/ERC20 withdrawal fee as an explicit haircut.

- VANRY MEXC -> Binance USDT:
  - 10,000 USDT after 80 VANRY fee: 20/20 positive, avg +371.033 bps, median +357.132 bps, min +82.331 bps.
- VANRY MEXC -> KuCoin USDT:
  - 5,000 USDT after 80 VANRY fee: 18/18 valid positive, avg +388.312 bps, median +380.583 bps, min +160.503 bps; two KuCoin timeouts.
- VANRY MEXC -> Binance USDC:
  - 5,000 USDC after 80 VANRY fee: 19/20 positive, avg +806.221 bps, median +898.570 bps, min -232.492 bps.
- ULTIMA MEXC -> KuCoin USDT:
  - 5,000 USDT: 18/18 valid positive, avg +470.913 bps, median +469.285 bps, min +463.343 bps.
  - 10,000 USDT: 18/18 valid positive, avg +243.884 bps, median +242.807 bps, min +238.556 bps.
- SPX Bybit -> KuCoin:
  - 5,000 USDT before Bybit transfer-fee haircut: 17/17 valid positive, avg +19.402 bps, median +19.802 bps, min +10.671 bps.
- SPX MEXC -> KuCoin:
  - 1,000 USDT after 3 SPX MEXC fee: 17/17 valid positive, avg +32.404 bps, median +31.541 bps, min +25.278 bps.
  - 2,500 USDT after 3 SPX MEXC fee: 17/17 valid positive, avg +18.440 bps, median +19.216 bps, min +1.590 bps.

Cap decisions:

- Keep VANRY MEXC -> Binance USDT firm public-book cap at 10,000 USDT for non-U.S. compliant setups.
- Keep VANRY MEXC -> KuCoin USDT firm public-book cap at 5,000 USDT, but include KuCoin endpoint reliability in live thresholding.
- Keep VANRY MEXC -> Binance USDC firm measurement cap at 2,500 USDC. The 5,000 USDC bucket printed another negative tail.
- Keep ULTIMA MEXC -> KuCoin USDT public-book cap at 5,000 USDT until chain/rebalance proof and a no-error 10,000 USDT window exist.
- Keep SPX as `MEASURE`; the edge is too small and metadata-gated for execution.

## Checkpoint - 2026-05-29 08:55 CST

### Funding and Bitso Monitor Refresh

Ran `python3 scripts/funding_probe.py` at 08:54 CST.

- Routes scanned: 47 public spot/perp proxies.
- Venues: Binance USD-M, Bybit linear, OKX swaps, Coinbase International.
- Endpoint errors: 0.
- Elapsed: 19.977 seconds.

Best one-period proxies remained negative after entry basis and round-trip fees:

- Coinbase INTX SOL USDC: -7.842 bps over 1h proxy.
- Coinbase INTX BTC USDC: -9.243 bps over 1h proxy.
- Coinbase INTX XRP USDC: -11.183 bps over 1h proxy.
- Binance WLD USDT negative-funding route: -12.422 bps over 8h proxy.
- Coinbase INTX DOGE USDC: -12.894 bps over 1h proxy.
- Coinbase INTX ETH USDC: -12.922 bps over 1h proxy.

Ran a Bitso same-venue MXN/USD/USDT/stablecoin basis check at 08:54 CST. Endpoint errors: 0.

Top-of-book reference:

- `usd_mxn`: bid 17.359, ask 17.364.
- `usdt_mxn`: bid 17.342, ask 17.345.
- `usd_usdt`: bid 1.0010, ask 1.0011.

Best net results after conservative 50 bps per Bitso taker leg:

- PYUSD/MXN sell bid vs USD/MXN ask after two fees: -51.857 bps.
- USD/MXN sell bid vs USDT/MXN buy ask after two fees: -91.759 bps.
- RLUSD/MXN sell bid vs USD/MXN ask after two fees: -104.881 bps.
- MXN -> USDT -> USD -> MXN: -131.442 bps.
- MXN -> USD -> USDT -> MXN: -172.542 bps.

Verdict: no promotion. Keep funding/basis and Bitso as monitor-only branches below the live spot route queue.

## Checkpoint - 2026-05-29 08:56 CST

### Binance.US Same-Venue Triangular Scan

Tested the same-venue triangular-arbitrage hypothesis on Binance.US, because it avoids transfer latency and had the lowest U.S.-available public taker fee from the earlier official fee check.

Scan details:

- Public endpoints: Binance.US `exchangeInfo` and `ticker/bookTicker`.
- Tradable symbols: 261.
- 3-leg cycles starting in USD, USDT, or USDC: 264.
- Fee model: 2 bps taker per leg.

Best cycles after fees:

- USDT -> USD -> USDC -> USDT: -6.710 bps.
- USD -> ETH -> USDT -> USD: -7.185 bps.
- USD -> USDT -> BTC -> USD: -7.553 bps.
- USD -> USDT -> ETH -> USD: -7.565 bps.

Verdict: `KILL` immediate Binance.US taker triangles. Same-venue routing removes transfer risk, but the best top-of-book cycle is still negative before deeper book sizing. Keep maker/post-only variants as a separate `LATER` hypothesis only if account fee tier and queue/fill modeling become available.

## Checkpoint - 2026-05-29 08:58 CST

### MEXC Same-Venue Triangular Scan

Tested same-venue triangular arbitrage on MEXC because MEXC has low public taker fees and many long-tail cross-quote pairs.

Scan details:

- Public endpoints: MEXC `exchangeInfo` and `ticker/bookTicker`.
- Tradable symbols: 2,323.
- 3-leg cycles starting in USDT, USDC, BTC, or ETH: 1,810.
- Fee model: symbol-level taker commission from `exchangeInfo`, falling back to 5 bps when missing.
- Positive top-of-book cycles: 3.

Positive cycles:

- USDT -> USD1 -> AWF -> USDT: +26.767 bps, but capped by 0.01 AWF on the sell leg.
- USDT -> EUR -> ADA -> USDT: +6.204 bps, but capped by about 0.006 EUR on the ADAEUR ask.
- USDC -> EUR -> ADA -> USDC: +5.913 bps, also capped by about 0.006 EUR on the ADAEUR ask.

Best non-dust stable/EUR loops were already negative; for example USDT -> EUR -> USDC -> USDT was -0.284 bps.

Verdict: `KILL` immediate MEXC taker triangles. The positive rows are dust top-of-book traps, not executable profit. Same-venue triangles remain useful as a scanner feature only with capacity-aware gates.

## Checkpoint - 2026-05-29 08:59 CST

### KuCoin Same-Venue Triangular Scan

Tested same-venue triangular arbitrage on KuCoin.

Scan details:

- Public endpoints: KuCoin `api/v2/symbols` and `api/v1/market/allTickers`.
- Tradable symbols: 1,082.
- 3-leg cycles starting in USDT, USDC, BTC, or ETH: 982.
- Fee model: 10 bps taker per leg.
- Positive top-of-book cycles: 0.

Best cycles after fees:

- USDT -> VSYS -> BTC -> USDT: -6.389 bps.
- USDC -> TEL -> ETH -> USDC: -16.413 bps.
- USDT -> TEL -> ETH -> USDT: -21.051 bps.

Verdict: `KILL` immediate KuCoin taker triangles. No positive same-venue cycle exists even before depth sizing. Keep maker/post-only variants as a separate `LATER` hypothesis only if account fee tier and queue/fill modeling become available.

## Checkpoint - 2026-05-29 09:04 CST

### Gate Same-Venue Triangular Scan and Depth Check

Tested same-venue triangular arbitrage on Gate.

Scan details:

- Public endpoints: Gate `spot/currency_pairs`, `spot/tickers`, and `spot/order_book`.
- Tradable symbols in the all-symbol scan: 2,206.
- 3-leg cycles starting in USDT, USDC, BTC, or ETH: 710.
- Fee model: Gate `fee` field converted from percent to fraction; normal pairs treated as 20 bps taker and USDC/USDT as 10 bps in the all-symbol scan. The follow-up depth check used a conservative 20 bps per leg for all legs.
- Positive top-of-book cycles in the all-symbol scan: 10.

Top headline positives from the corrected all-symbol scan:

- USDT -> ETH -> GALA -> USDT: +230.696 bps.
- USDC -> ETH -> GALA -> USDC: +213.410 bps.
- USDT -> LIKE -> ETH -> USDT: +22.791 bps.
- USDT -> XRD -> ETH -> USDT: +12.137 bps.
- USDT -> USDC -> REZ -> USDT: +4.027 bps.

Immediate executable-book depth check invalidated every positive row:

- GALA USDT -> ETH -> GALA -> USDT: -130.644 bps at 10 USDT, -172.217 bps at 1,000 USDT, -793.578 bps at 2,500 USDT.
- GALA USDC -> ETH -> GALA -> USDC: -160.048 bps at 10 USDC, -230.102 bps at 1,000 USDC, -872.444 bps at 2,500 USDC.
- LIKE USDT -> LIKE -> ETH -> USDT: -244.170 bps at 10 USDT, -482.335 bps at 100 USDT, -3,704.718 bps at 1,000 USDT.
- XRD USDT -> XRD -> ETH -> USDT: -123.478 bps at 10 USDT, -185.959 bps at 100 USDT, -2,804.983 bps at 1,000 USDT.
- REZ USDT -> USDC -> REZ -> USDT: -134.798 bps at 10 USDT, -170.171 bps at 1,000 USDT, -2,412.950 bps at 2,500 USDT.

A second immediate 10-USDT order-book spot check also showed all five routes negative: GALA USDT -145.135 bps, GALA USDC -147.499 bps, LIKE -225.921 bps, XRD -121.385 bps, and REZ -132.337 bps.

Verdict: `KILL` immediate Gate taker triangles. The top-of-book positives are not executable under book-walk sizing. Gate triangle scanning should only continue with a depth/capacity gate before any route enters the ranked queue.

## Checkpoint - 2026-05-29 09:08 CST

### Hyperliquid Same-Venue Spot/Perp Funding Probe

Tested whether Hyperliquid offers cleaner same-venue spot/perp carry than the CEX-only funding probe.

Source and fee context:

- Official Hyperliquid docs: `https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals` documents `metaAndAssetCtxs` and `predictedFundings`.
- Official Hyperliquid docs: `https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot` documents `spotMetaAndAssetCtxs`.
- Official Hyperliquid fee docs: `https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees` list tier-0 perps taker at 0.045% and spot taker at 0.070%.

Probe details:

- Public endpoints: Hyperliquid `metaAndAssetCtxs`, `spotMetaAndAssetCtxs`, and `l2Book`.
- Raw common spot/perp candidates: 19.
- Sane same-asset pairs after a 200 bps max spot/perp mid-divergence filter: 12.
- Rejected remap/stale rows: 4 (`TRUMP`, `BERA`, raw `PUMP`, raw `MON`).
- Fee model: 7.0 bps spot taker + 4.5 bps perp taker, charged on entry and exit, for 23.0 bps round-trip.
- Formula: `abs(hourly_funding_bps) + entry_basis_bps - 23.0`.

Best sane one-hour proxies:

- ETH spot/perp: hourly funding +0.125 bps, entry basis +11.941 bps, net one-hour proxy -10.934 bps, top notional about 1,809 USDC.
- BTC spot/perp: hourly funding +0.125 bps, entry basis +7.218 bps, net -15.658 bps, top notional about 84 USDC.
- SOL spot/perp: hourly funding +0.125 bps, entry basis +6.480 bps, net -16.395 bps, top notional about 981 USDC.
- PUMP wrapped spot/perp: hourly funding +0.125 bps, entry basis +4.129 bps, net -18.746 bps, top notional about 185 USDC.
- HYPE spot/perp: hourly funding +0.125 bps, entry basis -6.360 bps, net -29.235 bps, top notional about 1,333 USDC.

Rejected false positives:

- BERA spot/perp printed a mathematically huge positive, but spot mid was about -9,969 bps away from perp mid and top notional was only 0.05 USDC.
- Raw PUMP spot/perp printed a huge positive, but the spot token was about -9,454 bps away from the perp mid; the sane wrapped `UPUMP` pair was negative after fees.
- TRUMP and raw MON had spot mids far away from their perp mids and are not valid same-asset carry routes.

Verdict: `KILL` immediate Hyperliquid same-venue taker funding capture. The clean pairs do not cover round-trip fees in a one-hour window. Keep as `LATER` only for maker/post-only carry or multi-hour funding persistence with account-specific fee tier and exit modeling.

## Checkpoint - 2026-05-29 09:15 CST

### HTX Expansion Scan

Tested HTX as an additional public spot venue.

Scan details:

- Public endpoints: HTX/Huobi `market/tickers`, `v2/settings/common/symbols`, `market/depth`, and `v2/reference/currencies`.
- HTX markets included: 615 online/tradable quote-lane markets.
- Integrated scan scope: 10,819 total public markets after adding HTX to the existing venue set.
- Fee model: HTX 20 bps taker, MEXC 5 bps, Binance/Bybit/OKX/KuCoin/Bitget/Gate 10 bps, plus 2 bps latency buffer for USDT/USDC lanes.

Top HTX-involved depth results before transfer costs:

- ULTIMA HTX -> KuCoin: +805.334 bps at 50 USDT, +684.540 bps at 500, +649.488 bps at 1,000, +588.878 bps at 2,500, and +463.047 bps at 5,000.
- ZEC HTX -> OKX: +282.481 bps at 50 USDT, +195.121 bps at 500, +156.731 bps at 1,000, +133.389 bps at 2,500, +125.604 bps at 5,000, and +106.560 bps at 10,000.
- SWEAT HTX -> Bitget: positive through 1,000 USDT, but no 2,500 bucket.
- ONE/MTL/ICX HTX -> Binance: positive through 1,000-2,500 USDT depending on asset, but HTX public currency metadata shows deposits/withdrawals prohibited for these assets.
- US, ZK, WALLI, CARV, CETUS, RONIN, and KAS either failed depth by 500-1,000 USDT, had prohibited transfer status, or both.

ULTIMA persistence check:

- Ten samples from 09:13-09:14 CST with six-second spacing.
- HTX buy fee 20 bps + KuCoin sell fee 10 bps, no transfer fee applied.
- 1,000 USDT: 10/10 positive, avg +626.009 bps, median +630.842, min +612.618.
- 2,500 USDT: 10/10 positive, avg +547.314 bps, median +550.733, min +524.488.
- 5,000 USDT: 10/10 positive, avg +398.199 bps, median +418.883, min +340.505.
- 10,000 USDT: no valid full-depth bucket.

Transfer metadata:

- HTX `ULTIMA`: deposits and withdrawals allowed on `ultima1`, fee `0.00001`, no public contract address.
- KuCoin `ULTIMA`: deposits and withdrawals enabled only on BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
- This is the same chain problem as the MEXC/Gate SMART-vs-KuCoin BEP20 ULTIMA route: strong price dislocation, but no repeatable public proof that the buy venue can withdraw on the KuCoin receiving chain.
- HTX `ZEC`: depth was strong, but HTX public metadata shows ZEC withdrawals `prohibited`; direct repeatable transfer is killed.

Verdict: HTX is worth adding to discovery as a public scan venue, but not as an execution promotion yet. `ULTIMA` HTX -> KuCoin is `LATER` / pre-positioned-or-bridge-only until ULTIMA chain compatibility is proven. `ZEC` HTX -> OKX is `KILL` for repeatable transfer while HTX ZEC withdrawals are prohibited.

## Checkpoint - 2026-05-29 09:20 CST

### BitMart Expansion Scan

Tested BitMart as another public spot expansion venue.

Scan details:

- Public endpoints: BitMart `spot/v1/ticker`, `spot/quotation/v3/books`, and `account/v1/currencies`.
- BitMart markets parsed from ticker symbols: 1,107.
- Integrated scan scope: 11,229 total public markets after adding BitMart to the existing non-Bitso venue set.
- Fee model: conservative 25 bps BitMart taker, MEXC 5 bps, KuCoin/Bitget and other standard venues 10 bps, plus 2 bps latency buffer for USDT/USDC lanes.
- First metadata-backed attempt hit a transient BitMart `502 Bad Gateway`; a lighter ticker-symbol parser succeeded immediately afterward.

Sane liquid top-of-book positives:

- ULTIMA BitMart -> KuCoin: headline net +837.734 bps after fees/latency, with 124,596 USDT 24h depth proxy.
- QAIT KuCoin -> BitMart: headline net +336.347 bps.
- QAIT MEXC -> BitMart: headline net +270.081 bps.
- BTR BitMart -> Bitget: headline net +225.009 bps.

Executable depth check before transfer costs:

- ULTIMA BitMart -> KuCoin: +741.684 bps at 50 USDT, +643.903 bps at 500, +613.926 bps at 1,000, +553.614 bps at 2,500, but -396.301 bps at 5,000.
- QAIT KuCoin -> BitMart: +356.628 bps at 50, +169.765 bps at 500, -3.012 bps at 1,000, and -219.759 bps at 2,500.
- QAIT MEXC -> BitMart: +186.143 bps at 50, +5.387 bps at 500, and -164.361 bps at 1,000.
- BTR BitMart -> Bitget: +216.079 bps at 50, +136.822 bps at 500, +80.512 bps at 1,000, but no 2,500 bucket.

Transfer metadata:

- BitMart `ULTIMA` supports SMART withdrawals/deposits on contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`; native `ULTIMA` withdrawals are disabled. KuCoin `ULTIMA` remains BEP20-only, so the BitMart -> KuCoin premium is the same SMART/native-vs-BEP20 chain split as the MEXC/Gate/HTX ULTIMA evidence.
- BitMart `QAIT` deposits are enabled on BSC contract `0x4d41A5d412f4Ef44A35b9f53b06DB65edE249493`, but the route failed by 1,000 USDT and prior QAIT metadata showed KuCoin/Gate withdrawal issues.
- BitMart `BTR` withdrawals are enabled on `BTR-BTC` contract `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`, while Bitget `BTR` exposes ERC20 contract `0x6c76de483f1752ac8473e2b4983a873991e70da7` with deposits disabled.

Verdict: `KILL` immediate BitMart expansion routes. Keep BitMart as discovery-only; it is useful for confirming the ULTIMA chain-split premium but did not add a repeatable transfer route.

## Checkpoint - 2026-05-29 09:25 CST

### Watch Route Refresh

Refreshed the current watch shortlist over 12 public-book samples with six-second spacing.

Run quality:

- Scope: VANRY, ULTIMA, and SPX routes across MEXC, Binance, KuCoin, HTX, and Bybit.
- Fees and transfer haircuts: MEXC 5 bps, Binance/KuCoin/Bybit 10 bps, HTX 20 bps; VANRY includes the 80 VANRY MEXC withdrawal haircut; SPX MEXC includes the 3 SPX MEXC withdrawal haircut; ULTIMA routes still exclude transfer fee because chain compatibility is unresolved.
- Errors: one KuCoin `502 Bad Gateway` on ULTIMA MEXC -> KuCoin 10,000 USDT.
- Public REST RTT was poor: avg 10,762 ms, max 19,123 ms. Live thresholds need book staleness and timeout handling.

Results:

- VANRY MEXC -> Binance USDT, 10,000 USDT after 80 VANRY fee: 12/12 positive, avg +310.346 bps, median +312.777, min +289.750. Keep 10,000 USDT public-book cap for non-U.S. compliant accounts.
- VANRY MEXC -> KuCoin USDT, 5,000 USDT after 80 VANRY fee: 12/12 positive, avg +192.664 bps, median +188.456, min +153.914. Keep 5,000 USDT cap, but KuCoin endpoint staleness matters.
- VANRY MEXC -> Binance USDC, 2,500 USDC after 80 VANRY fee: 12/12 positive, avg +840.599 bps, median +858.633, min +653.161. Keep 2,500 USDC firm measurement cap.
- VANRY MEXC -> Binance USDC, 5,000 USDC after 80 VANRY fee: 9/12 positive, avg +236.735 bps, median +290.857, min -207.212. Keep 5,000 USDC rejected for live execution.
- ULTIMA MEXC -> KuCoin, 5,000 USDT before chain-transfer proof: 12/12 positive, avg +410.174 bps, median +423.809, min +318.532. Keep 5,000 USDT watch cap, still chain/rebalance blocked.
- ULTIMA MEXC -> KuCoin, 10,000 USDT before chain-transfer proof: 10/11 valid positive, avg +122.537 bps, median +149.058, min -30.868, plus one KuCoin 502. Keep 10,000 USDT rejected-live-threshold / thin watch only.
- ULTIMA HTX -> KuCoin, 5,000 USDT before chain-transfer proof: 12/12 positive, avg +392.967 bps, median +411.651, min +307.767. Strong pre-positioned/bridge-only watch; not repeatable until the ULTIMA chain split is solved.
- SPX Bybit -> KuCoin, 5,000 USDT before Bybit transfer fee: 0/12 positive, avg -35.773 bps, min -42.156.
- SPX MEXC -> KuCoin, 1,000 USDT after 3 SPX fee: 0/12 positive, avg -38.325 bps, min -45.293.
- SPX MEXC -> KuCoin, 2,500 USDT after 3 SPX fee: 0/12 positive, avg -44.030 bps, min -52.269.

Verdict: VANRY and ULTIMA caps unchanged. SPX is no longer an active `MEASURE` route; move it to `KILL` for current execution and only revisit if a fresh event-window sampler finds a new persistent positive window.

## Checkpoint - 2026-05-29 09:27 CST

### ULTIMA Chain Compatibility Source Check

Checked whether the persistent ULTIMA premium on KuCoin has public proof of bridge compatibility from the SMART/native cluster into KuCoin's BEP20 receiving path.

Evidence found:

- BitMart listing article for ULTIMA classifies the token type as `SMART` and links the SMART explorer contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`: `https://bitmart.zendesk.com/hc/en-us/articles/32179256550427-Ultima-ULTIMA`.
- BitMart public currency API matches this: `ULTIMA-SMART` deposits/withdrawals enabled on `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`; `ULTIMA-ULTIMA` deposits enabled but withdrawals disabled.
- KuCoin listing article says ULTIMA deposits are supported via `BSC-BEP20`: `https://www.kucoin.com/announcement/ua-ultima-ultima-gets-listed-on-kucoin`.
- KuCoin public currency API matches this: only BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8` is exposed with deposits and withdrawals enabled.
- BscScan/BSC token pages identify `0x5668a83b46016b494a30dd14066a451e5417a8b8` as BEP20 ULTIMA, separate from the SMART explorer contract.

No official/public bridge proof was found in the quick source pass. The current ULTIMA premium should be treated as a cross-representation premium, not a repeatable transfer arbitrage.

Verdict: keep ULTIMA MEXC/HTX/BitMart -> KuCoin as `LATER` / pre-positioned-or-bridge-only. Do not promote to execution until a logged-in withdrawal UI/API proves BEP20 withdrawal from the buy venue or an official bridge path with cost/time limits is verified.

## Checkpoint - 2026-05-29 09:38 CST

### Expanded Event-Window Depth Pass

Expanded the event-window sampler beyond the processed-base queue and then depth-checked the persistent rows.

Discovery pass:

- Six repeated top-of-book samples across the expanded venue set, excluding already-processed bases.
- Hard filters: same quote lane, positive after venue taker fees, 24h depth proxy at least 100,000 USDT, gross spread at most 1,000 bps.
- One OKX read timeout occurred in sample 0; the depth pass itself returned zero errors.
- Persistent top rows included `GUA` MEXC -> Gate, `RACA` HTX -> BitMart, `TST` HTX -> Binance/BitMart, `BLAST` HTX -> Bybit/BitMart, `STRK` HTX -> MEXC/KuCoin, `ORDI` HTX -> Bitget/Bybit, `AWE` HTX -> Binance, `STETH` HTX -> Bybit, `NEXO` HTX -> Binance, and `GOMINING` HTX -> MEXC.

Executable depth before transfer costs:

- GUA MEXC -> Gate: +780.754 bps at 50 USDT, +604.611 at 500, +500.314 at 1,000, +209.824 at 2,500, and -29.459 at 5,000.
- ORDI HTX -> Bybit: +151.835 bps at 50, +144.838 at 500, +140.902 at 1,000, and -35.586 at 2,500 before transfer. ORDI HTX -> Bitget was similar: +143.342 at 1,000 and -31.037 at 2,500.
- GOMINING HTX -> MEXC: +88.566 bps at 50, +29.647 at 500, and -48.646 at 1,000.
- STRK HTX -> MEXC/KuCoin: positive through 500 USDT, then about -236 bps at 1,000 and worse at 2,500.
- RACA, TST, BLAST, STETH, NEXO, and AWE either failed by 250-1,000 USDT or were negative from the first tested bucket.

Transfer metadata:

- Gate `GUA` public currency metadata shows BSC contract `0xa5c8e1513b6a08334b479fe4d71f1253259469be`, withdrawals enabled, but deposits disabled. That kills repeatable MEXC -> Gate delivery even though the book depth was strong through 2,500 USDT.
- HTX `ORDI` public metadata shows BRC20 deposits/withdrawals allowed but a fixed withdrawal fee of `5.004459` ORDI. With HTX ORDI around 3.39 USDT during the check, that is about 170 bps of transfer drag on a 1,000 USDT route, larger than the +140-151 bps pre-transfer edge. The 2,500 USDT buckets were already negative before transfer.
- Bitget `ORDI` deposits are enabled on BRC20, but the HTX withdrawal fee alone kills the measured bucket. Bybit public asset metadata required an API key in this environment, so no Bybit deposit-status promotion is possible from public evidence.

Verdict: no new repeatable execution promotion. `GUA` is a `LATER` pre-positioned-inventory watch only, capped at 2,500 USDT public-book size while Gate deposits remain disabled. `ORDI` and the rest of the HTX event-window cluster are `KILL` for current execution because transfer drag or depth collapse removes the edge.

## Checkpoint - 2026-05-29 09:54 CST

### Post-Discovery Refreshes And Active Watch Downgrade

Ran four follow-up loops after the expanded event-window pass.

Liquid static refresh:

- `scripts/market_probe.py` scanned 10,204 public markets across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso with zero endpoint errors.
- Only tiny sane priority positives appeared: XLM Gate -> Bybit +6.559 bps, INJ Gate -> MEXC +3.952 bps, XLM Gate -> MEXC +2.196 bps, and XLM Gate -> KuCoin/Bitget +1.878 bps after fees/latency.
- Immediate depth killed every row at 1,000 USDT: best was INJ Gate -> Bybit -31.541 bps; XLM Gate -> Bybit was -48.359 bps.

CoinEx expansion:

- Added 1,080 online CoinEx spot markets, bringing the integrated static scan to 11,202 markets.
- CoinEx public metadata exposed per-market taker fees, typically 20-30 bps.
- CoinEx-involved sane positives after fees/latency/liquidity filters: 0. Best near miss was BABYDOGE OKX -> CoinEx at -6.160 bps before depth.

Funding and MXN refreshes:

- Spot/perp funding refresh returned Binance 14 routes, Bybit 14, Coinbase INTX 5, and one OKX `502 Bad Gateway`.
- Best funding proxy stayed negative: Coinbase INTX DOGE -7.896 bps over the one-hour model, then Coinbase INTX BTC -10.628 and XRP -11.183.
- Bitso MXN/stable refresh stayed negative. Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -64.852 bps net after two Bitso fees; BTC/MXN implied USD comparisons were -156.047 and -173.774 bps net after three fees.

Active watch refresh:

- Eight samples with six-second spacing across VANRY, ULTIMA, and GUA routes. Public REST RTT improved versus the 09:25 run: avg 472.8 ms, max 1,125.0 ms.
- VANRY MEXC -> Binance USDT after 80 VANRY withdrawal fee: 10,000 USDT stayed 8/8 positive, avg +275.623 bps, median +298.490, min +79.560. Keep 10,000 USDT cap, but the min compressed materially from the 09:25 run.
- VANRY MEXC -> KuCoin USDT after 80 VANRY fee: 2,500 USDT stayed 8/8 positive, avg +584.783 bps, min +154.962. The 5,000 USDT bucket degraded to 7/8 positive with min -130.747, so firm cap drops from 5,000 to 2,500 USDT.
- VANRY MEXC -> Binance USDC after 80 VANRY fee: 2,500 USDC stayed 8/8 positive, avg +911.620 bps, min +590.155. The 5,000 USDC bucket was 7/8 positive with min -253.295, so cap remains 2,500 USDC.
- GUA MEXC -> Gate pre-positioned-only: 1,000 and 2,500 USDT stayed 8/8 positive, with 2,500 avg +254.447 bps and min +208.167. 5,000 USDT was only 1/8 positive, avg -10.755. Keep GUA capped at 2,500 USDT and only for pre-positioned Gate inventory while deposits remain disabled.
- ULTIMA MEXC/HTX -> KuCoin collapsed at actionable size. The eight-sample run showed MEXC -> KuCoin 5,000 and 10,000 deeply negative because KuCoin bid depth fell off after sub-1k size. A follow-up small-bucket check showed MEXC -> KuCoin positive through 500 USDT but -79.862 bps at 1,000; HTX -> KuCoin positive through 500 but -195.713 bps at 1,000. Combined with the unresolved SMART/native-to-BEP20 chain split, ULTIMA is no longer an active 5,000 USDT watch.

Verdict: VANRY Binance USDT remains the top measurable route at 10,000 USDT for non-U.S.-compliant accounts. VANRY KuCoin tightens to 2,500 USDT. VANRY USDC remains 2,500 USDC. GUA is a 2,500 USDT pre-positioned-only watch. ULTIMA 5,000/10,000 is `KILL_CURRENT`; keep only a low-priority 500 USDT micro watch until both KuCoin depth and chain compatibility recover.

## Checkpoint - 2026-05-29 10:21 CST

### Fresh Event-Window And U.S.-Available Follow-Up

Fresh event-window exclusion scan:

- Ran four top-of-book samples across 12,290-12,928 markets, excluding the current watchlist and many processed/killed bases.
- Two early Bitget ticker reads timed out; later samples succeeded.
- Most persistent positives were known HTX transfer-status or depth traps: ONE, MTL, CETUS, US, CARV, ZEC, ETHW, DGB, GENIUS, and ZEN.
- Depth killed plausible non-ATLA survivors at meaningful size: DAG was negative by 250-500 USDT; DGB/ETHW/ZEN were negative by 100-250 or worse; GENIUS was negative by 500-1,000 depending on sell venue.

ATLA result:

- ATLA MEXC -> BitMart survived as a micro route only.
- One depth retry before transfer showed +92.750 bps at 500 USDT, +51.331 at 1,000, and -68.297 at 2,500.
- Six-sample persistence showed 500 USDT 6/6 positive, avg +54.386 bps, median +53.719, min +44.291 before transfer. 1,000 USDT was only 5/6 positive with min -3.222; 2,500 was 0/6 positive.
- BitMart public metadata exposes `ATLA-ATLA` deposits/withdrawals enabled on native `ATLA`, fee `0.01`.
- MEXC exchange metadata shows `ATLAUSDT` spot trading allowed and no contract address. MEXC official listing history says ATLA deposits opened and withdrawals were scheduled for 2025-08-18 08:00 UTC, but current public withdrawal status/fee remains unverified: MEXC capital config returned `api key required`, and web asset config returned `Access Denied`.
- Verdict: `MEASURE` at 500 USDT only, pending logged-in MEXC withdrawal status/fee.

U.S.-available core venue refresh:

- Bounded scan covered 110 core USD/USDT/USDC markets across Binance.US, Coinbase, Kraken, Gemini, and Bitstamp.
- Only positive top-of-book after-fee rows were XLM/USD Kraken -> Binance.US +21.089 bps and XLM/USD Bitstamp -> Binance.US +19.488 bps.
- Depth killed both from the smallest tested bucket: Kraken -> Binance.US was -124.181 bps at 100 USD and -126.155 at 1,000; Bitstamp -> Binance.US was -124.981 at 100 and -128.270 at 1,000.

Verdict: no new repeatable execution route. ATLA is the only new `MEASURE`, capped at 500 USDT and blocked on MEXC withdrawal status/fee. U.S.-available taker substitution remains `KILL`.

### Strict New-Name Exclusion Refresh

Ran a stricter follow-up after the ATLA/U.S. refresh to find genuinely new bases, first including HTX and then correcting the pass to exclude already killed BTR/HOOLI/PHB/MAPO and HTX-stale rows.

First pass:

- Three top-of-book samples across 11,820 parsed markets. BitMart ticker parsing was wrong in this first pass, so BitMart returned zero markets; other venues returned normally.
- The top rows were not new opportunities. HOOLI, BTR, PHB, and MAPO resurfaced despite prior kills, and HTX-led rows such as USTC/DCR/GMX/DEXE/SWEAT had no executable order-book depth.
- Depth confirmed the old lessons: BTR MEXC -> Bitget still had book depth through 5,000 USDT, but it is already killed by Bitget deposit disablement and contract mismatch; HOOLI/PHB/MAPO are also already killed by deposit or depth constraints.

Corrected pass:

- Two top-of-book samples across 11,231 markets with BitMart parsed correctly and zero endpoint errors.
- Best after-fee rows were OWL BitMart -> MEXC, CELL BitMart -> MEXC/Gate, WEXO BitMart -> MEXC USDC, MAGA MEXC -> BitMart, ARRR Gate -> MEXC, MEY BitMart -> MEXC, WPAY BitMart -> Gate, and smaller ESE/CHIRP/TBK/BEAT/ID rows.
- Executable depth killed meaningful size. OWL was negative from 50 USDT; MAGA/NAKA were negative from 50 USDT or lacked sell depth; ORAI/TBK/BEAT/ID were negative by 100-250; CELL and WEXO were positive only through 100; WPAY was positive through 500 but only +16.940 bps at 500 before transfer; ARRR was the only plausible micro survivor in a single book walk.

ARRR follow-up:

- Corrected Gate pair fee is `0.2%` = 20 bps, not the generic 10 bps assumption.
- Gate public currency metadata shows ARRR deposits/withdrawals enabled on native ARRR. MEXC exchange metadata shows `ARRRUSDT` spot trading allowed, full name Pirate Chain, and MEXC fee-page data lists native ARRR with deposit fee 0 and withdrawal fee `2.5` ARRR.
- Six-sample ARRR Gate -> MEXC persistence after Gate 20 bps + MEXC 5 bps + 2 bps latency: 100 USDT was 6/6 positive, avg +120.727 bps, min +107.401; 250 USDT was only 1/6 positive, avg -14.114; 500 and 1,000 USDT were 0/6 positive.

Verdict: no new promotion. ARRR is a dust-only 100 USDT pocket and should be killed for execution. The corrected event-window scanner must retain the old killed-base exclusion and must use venue pair fees before ranking Gate rows.

### Active Watch Refresh

Ran an eight-sample active route refresh with six-second spacing at 10:34-10:36 CST. Public REST RTT was slower than the 09:54 pass: avg 4,938.9 ms, max 6,073.4 ms, but all samples completed with zero endpoint errors.

Current route results:

- VANRY MEXC -> Binance USDT after 80 VANRY withdrawal fee: 10,000 USDT stayed 8/8 positive, avg +270.132 bps, median +298.558, min +106.909. Keep the 10,000 USDT cap for non-U.S.-compliant account setups.
- VANRY MEXC -> KuCoin USDT after 80 VANRY fee: 5,000 USDT recovered to 8/8 positive, avg +238.039 bps, median +261.240, min +76.284. This meets the prior stop condition for restoring the 5,000 USDT cap, but keep tail monitoring because it was negative in the 09:54 pass.
- VANRY MEXC -> Binance USDC after 80 VANRY fee: 5,000 USDC recovered to 8/8 positive, avg +595.583 bps, median +567.803, min +197.250. Promote the measurement cap from 2,500 to 5,000 USDC, still below the USDT Binance route because this lane has shown prior negative tails.
- GUA MEXC -> Gate pre-positioned-only with exact Gate 20 bps pair fee: 2,500 USDT stayed 8/8 positive, avg +354.473 bps, min +244.780. 5,000 USDT was only 6/8 positive with min -50.063, so keep the firm cap at 2,500 and only for pre-positioned Gate inventory while deposits remain disabled.
- ATLA MEXC -> BitMart: current 500 USDT watch failed. 250, 500, and 1,000 USDT were all 0/8 positive; 500 avg -170.470 bps, min -173.274. Demote ATLA from `MEASURE` to `KILL_CURRENT` until a fresh event-window sampler rediscovers it.
- ULTIMA MEXC -> KuCoin depth recovered through 2,500 USDT before chain proof: 2,500 was 8/8 positive, avg +448.475 bps, min +424.615. Do not promote to repeatable execution because the MEXC SMART/native vs KuCoin BEP20 path remains unresolved and 5,000/10,000 were not restored in this pass.

Verdict: main action stays VANRY. Restore VANRY KuCoin 5,000 USDT and VANRY Binance USDC 5,000 USDC as current public-book caps for non-U.S.-compliant accounts. Keep GUA at 2,500 pre-positioned-only. Kill current ATLA. Treat ULTIMA as chain-proof-only despite the recovered 2,500 USDT book depth.

### Funding Refresh

Ran `scripts/funding_probe.py` at 10:39 CST.

- Data returned cleanly: Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, zero endpoint errors.
- Best one-period proxy remained negative: Coinbase INTX BTC -9.942 bps over the one-hour model.
- Next best rows were Coinbase INTX SOL -10.943 bps, Coinbase INTX ETH -11.556, Coinbase INTX XRP -12.695, Coinbase INTX DOGE -12.874, Bybit WLD -15.894, OKX WLD -16.737, Bybit TRX -17.936, Binance TRX -18.123, OKX TRX -18.357, and Binance WLD -18.960.
- Negative-funding WLD/TRX rows still require long perp plus short/borrow spot inventory and are negative even before borrow, exit, and liquidation risk.

Verdict: no funding promotion. Keep spot/perp carry as scheduled monitor only.

### Bitso MXN Refresh

Ran a public Bitso ticker refresh at 10:40 CST across USD/MXN, USDT/MXN, PYUSD/MXN, BTC/USD, BTC/MXN, ETH/USD, ETH/MXN, XRP/USD, and XRP/MXN.

- Best stable comparison: PYUSD/MXN sell bid vs USD/MXN buy ask was +36.915 bps gross but -63.085 bps net after two 50 bps Bitso legs.
- USDT/MXN buy ask vs USD/MXN sell bid was -92.495 bps net; USDT/MXN sell bid vs USD/MXN buy ask was -110.382 bps net.
- Crypto/MXN implied routes were worse after three legs: XRP/MXN buy ask vs implied XRP/USD*USD/MXN sell was -153.531 bps net; ETH/MXN sell bid vs implied buy was -162.577; BTC/MXN buy ask vs implied sell was -168.674; BTC/MXN sell bid vs implied buy was -188.625.
- Tickers: USD/MXN 17.335/17.337, USDT/MXN 17.319/17.322, PYUSD/MXN 17.401/17.412, BTC/MXN 1,277,810/1,284,530, BTC/USD 73,962/73,990.

Verdict: no MXN-lane promotion. Fees still dominate the local FX/stable/crypto basis.

### BingX/LBank Venue Expansion

Ran a BingX/LBank expansion smoke test at 10:41-10:46 CST.

- Public endpoints were usable: BingX returned 883 parsed spot markets with bid/ask and order-book depth; LBank returned 976 parsed spot markets, but its all-ticker endpoint lacks bid/ask, so LBank routes were treated as smoke candidates until direct depth passed.
- Integrated scan size was 12,006 markets across the existing public venues plus BingX and LBank, with zero endpoint errors.
- Top rows included RAVE LBank -> KuCoin/BitMart/BingX, ESPORTS LBank -> MEXC/BingX, KAT -> BingX, CAS MEXC -> LBank, TOWER MEXC -> BingX, and PUSS/YEE/DHN/POD/KELLYCLAUDE/KAIO/AI4 rows.

Depth and metadata:

- RAVE LBank -> KuCoin stayed positive through 5,000 USDT in the book walk, but KuCoin public metadata has RAVE deposits disabled on both BEP20 and ERC20. RAVE LBank -> BitMart was positive through 2,500 but negative by 5,000 and BitMart public currency metadata did not expose a RAVE deposit lane in this check. RAVE -> BingX is capped by BingX `maxMarketNotional` 541 and lacks public deposit-status proof.
- KAT -> BingX was positive only through 250-500 USDT and negative by 1,000; BingX also caps KAT `maxMarketNotional` at 1,817.
- Most other rows failed depth by 100-1,000 USDT.
- ESPORTS LBank -> MEXC survived as the only meaningful new measurement. LBank public withdrawal config shows ESPORTS BEP20 withdrawals enabled with fee `4.6915` ESPORTS. MEXC exchange metadata lists `ESPORTSUSDT` as Yooldo Games with BSC contract `0xF39e4b21c84e737Df08e2C3b32541d856f508E48`, and MEXC fee-page metadata lists ESPORTS on BSC with deposit fee 0.
- Operational caveat: official LBank notice `https://www.lbank.com/fa/support/articles/2058904083074383872` says LBank suspended ESPORTS deposits and withdrawals at 2026-05-25 13:20 UTC. No resume notice was found in the quick official search, so the live public API `canWithDraw=true` conflicts with the support notice and must be verified in a logged-in account before any execution work.
- Account/region caveat added 10:52 CST: official LBank user-agreement material excludes U.S.-resident personal/corporate accounts (`https://www.lbank.com/support/articles/21436496711705`), and BingX's Customer Agreement plus Disclaimer route users away from restricted jurisdictions including the United States (`https://bingx.com/en/support/articles/12803820985231/`, `https://bingx.com/en/support/articles/11263347398927`). Treat both venues as scanner-only unless Pedro proves a lawful non-U.S. account setup.

ESPORTS LBank -> MEXC persistence:

- Six samples with six-second spacing, conservative fee model: LBank 20 bps + MEXC 5 bps + 2 bps latency, plus LBank `4.6915` ESPORTS withdrawal fee.
- 1,000 USDT: 6/6 positive, avg +305.079 bps, min +165.465.
- 2,500 USDT: 6/6 positive, avg +177.340 bps, min +41.913.
- 5,000 USDT: 4/6 positive, avg -25.452, min -205.489.
- 10,000 USDT: 0/6 positive, avg -2,050.935.

Verdict: add `ESPORTS` LBank -> MEXC as a new scanner-only `MEASURE`, capped at 2,500 USDT before final transfer/account proof. Do not promote it to execution until the conflicting LBank deposit/withdraw status is resolved, LBank contract identity is proven, live MEXC deposit status is confirmed, non-U.S. LBank account/region eligibility is checked, and real fee tier is known. Keep BingX/LBank adapters as `LATER` because the endpoints are usable and produced one depth-positive route, but LBank's all-ticker schema needs order-book-first scoring and both venues need hard region gates.

### U.S.-Available Full-Venue Scan

Ran a broader U.S.-available scan at 10:55-11:03 CST after the region gate made global MEXC/KuCoin/LBank routes account-blocked for a U.S.-resident setup.

One-shot public top-of-book pass:

- Venues: Binance.US, Coinbase product probe, Kraken, Bitstamp.
- Markets with usable bid/ask: 1,146 total. Binance.US 256, Bitstamp 137, Kraken 753. Coinbase's no-key all-products endpoint returned products but blank bid/ask fields, so Coinbase was not scored in this pass.
- Positive after-fee top rows: `LIT` Kraken -> Bitstamp, `ENJ` Kraken -> Bitstamp, and `MANA` Kraken -> Bitstamp.

Depth and identity:

- `LIT` was killed as a ticker-collision/asset-migration trap. The gross row was huge, but it is not a clean same-asset transfer candidate across Kraken and Bitstamp.
- `MANA` was killed by executable depth. The first 25 USD book walk was already -1,562.339 bps after fees, and Bitstamp sell depth was exhausted by 500 USD.
- `ENJ` survived as a scanner-only pocket: three individual depth samples showed 500 USD 3/3 positive, avg +1,090.153 bps, min +1,081.106 after Kraken 40 bps, Bitstamp 40 bps, and 2 bps latency. The 1,000 USD bucket was only 2/3 positive with min -8.649; 1,500+ was negative.

Transfer/status check:

- Bitstamp public currency endpoint shows ENJ deposits and withdrawals enabled only on `ethereum`, with withdrawal minimum 10 ENJ.
- Kraken official ENJ support says ERC-20 ENJ deposits/withdrawals were phased out on 2024-12-10 and Kraken continues to support ENJ funding on Enjin Relaychain.
- This likely explains the basis and kills simple repeatable transfer. A pre-positioned Bitstamp ENJ sell leg could capture the book basis once, but rebalancing requires a bridge/migration path and exposes old-token/new-token basis risk.

Verdict: add `ENJ` Kraken -> Bitstamp as U.S.-available scanner-only `MEASURE`, capped at 500 USD before transfer. Kill repeatable execution until a Relaychain-to-Ethereum bridge or same-network deposit path is proven. Kill `LIT` and `MANA` from this pass.

### Active Watch Refresh - 11:06 CST

Ran a compact active refresh across the current watchlist and the two new scanner-only pockets. Four samples with six-second spacing, zero endpoint errors.

Results:

- VANRY MEXC -> Binance USDT after the 80 VANRY withdrawal fee: 10,000 USDT stayed 4/4 positive, avg +279.010 bps, min +209.416. Keep the 10,000 USDT cap for non-U.S.-compliant account setups.
- VANRY MEXC -> KuCoin USDT after the 80 VANRY fee: 5,000 USDT stayed 4/4 positive, avg +240.279 bps, min +134.193. Keep the 5,000 USDT cap.
- VANRY MEXC -> Binance USDC after the 80 VANRY fee: 5,000 USDC was only 3/4 positive, avg +228.828 bps, min -32.644. Kill the current 5,000 USDC measurement cap; retest 2,500 before restoring.
- GUA MEXC -> Gate pre-positioned-only with exact Gate 20 bps pair fee: 2,500 USDT was only 3/4 positive, avg +168.507 bps, min -64.011. 5,000 USDT was 1/4 positive, avg -357.768. Kill the current firm GUA caps until lower buckets are retested.
- ULTIMA MEXC -> KuCoin before chain proof: 2,500 USDT was 4/4 positive, avg +476.124 bps, min +405.653; 5,000 USDT was 4/4 positive, avg +322.931, min +162.210. Keep chain-proof-only; do not promote repeatable execution.
- ESPORTS LBank -> MEXC scanner-only after conservative fees and the `4.6915` ESPORTS withdrawal fee: 1,000 USDT 4/4 avg +344.425 bps, min +325.460; 2,500 4/4 avg +243.315, min +221.900; 5,000 4/4 avg +32.848, min +19.854. Keep firm scanner cap at 2,500 because 5,000 is thin and LBank status/account blockers remain unresolved.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD 4/4 positive, avg +1,095.851 bps, min +1,088.802; 1,000 USD 0/4 positive, avg -169.338. Keep cap at 500 USD and chain-mismatch blocked.

Verdict: main action remains VANRY USDT routes. Demote VANRY USDC 5,000 and GUA firm caps. Add ESPORTS/ENJ to scanner-only watch with hard execution blockers. ULTIMA 5,000 recovered in books but remains chain-proof-only.

### Scheduled Funding And Bitso Refresh - 11:12 CST

Funding:

- `scripts/funding_probe.py` returned Binance 14 routes, Bybit 14, OKX 14, and Coinbase INTX 5 with zero endpoint errors.
- Best one-period proxy was Coinbase INTX XRP at -7.416 bps.
- Next rows were Coinbase INTX ETH -8.661, BTC -8.846, DOGE -9.890, SOL -10.583, OKX WLD -16.845, Binance TRX -17.161, Bybit WLD -17.283, Bybit TRX -18.487, and OKX TRX -18.669.
- Verdict: no funding promotion; all rows remain negative before borrow, margin, exit-basis, and liquidation risk.

Bitso MXN/stable/crypto basis:

- Tickers: USD/MXN 17.326/17.335, USDT/MXN 17.316/17.318, PYUSD/MXN 17.383/17.438, BTC/MXN 1,281,390/1,284,810, BTC/USD 74,068/74,101.
- Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask: +27.690 bps gross, -72.310 bps net after two 50 bps legs.
- USDT/MXN comparisons were -95.381 and -110.960 bps net.
- Crypto/MXN implied routes remained negative after three legs: XRP best -152.816 bps, BTC -161.736, ETH -162.676.
- Verdict: no MXN-lane promotion.

### Liquid Static Refresh - 11:14 CST

Ran `scripts/market_probe.py` across the existing static venue set.

- Markets: 10,204 total. Binance 1,722, MEXC 2,331, Gate 2,124, OKX 1,111, KuCoin 962, Bitget 638, Crypto.com 570, Bybit 556, Bitfinex 108, Bitso 82.
- Endpoint errors: 0.
- Positive sane priority rows after generic top-of-book fees were only single-digit bps: INJ Gate -> MEXC +5.652, XLM Crypto.com -> Bitfinex +5.437, and XLM MEXC -> Binance +1.815.

Direct depth validation with stricter fees:

- INJ Gate -> MEXC using Gate 20 bps + MEXC 5 + 2 latency: -34.493 bps at 100 USDT, -37.994 at 1,000, -45.183 at 5,000.
- XLM Crypto.com -> Bitfinex USD using Crypto.com 7.5 bps + Bitfinex 0 + 4 latency: -15.519 bps at 100 USD, -21.963 at 1,000, -36.184 at 10,000.
- XLM MEXC -> Binance using MEXC 5 + Binance 10 + 2 latency: -12.285 bps at 100 USDT, -16.364 at 1,000, -25.830 at 10,000.

Verdict: no liquid static promotion. Keep this path as a regression monitor only; the live opportunity frontier remains event-window/representation-basis pockets plus account/chain proof.

### Event-Window Sampler - 11:28 CST

Ran a fresh event-window sampler after the static refresh.

Discovery:

- Scope: three top-of-book samples across 10,122 markets per sample, excluding recent watchlist/kill bases and Bitso for speed.
- Endpoint errors: 0.
- Persistent positives included ASSET KuCoin -> MEXC, NIBI MEXC -> KuCoin, TX Bitget -> Gate, TSLAON MEXC -> Bitget, DEXE KuCoin -> MEXC/Binance, HMSTR, NOS, XCX, AR, WALLI, UNION, and smaller rows.

Depth:

- ASSET KuCoin -> MEXC was positive at 50/100/250 USDT but negative by 500 (-42.999 bps) and worse beyond.
- NIBI MEXC -> KuCoin and TX Bitget -> Gate were negative from 50 USDT.
- DEXE KuCoin -> MEXC/Binance was positive only through 100 USDT and negative by 250.
- TSLAON MEXC -> Bitget had the best shape in the first depth walk: positive through 1,000 USDT and only slightly negative by 2,500.

TSLAON metadata and persistence:

- MEXC exchange metadata identifies `TSLAONUSDT` as Tesla with ERC20 contract `0xf6b1117ec07684D3958caD8BEb1b302bfD21103f`, taker 5 bps.
- Bitget symbol metadata shows `TSLAONUSDT` online, and Bitget public coin metadata shows ERC20 deposits/withdrawals enabled on the same contract.
- MEXC fee-page metadata lists TSLAON on Ethereum/ERC20 with withdrawal fee `0.002`, deposit fee 0, and minimum withdrawal `0.013548`.
- Four-sample TSLAON persistence after MEXC 5 bps + Bitget 10 bps + 2 latency + 0.002 TSLAON withdrawal fee: 250 USDT 0/4 avg -15.846 bps; 500 2/4 avg -0.805; 1,000 3/4 avg +3.755 with min -0.066; 1,500 3/4 avg +2.599 with min -1.370; 2,500 1/4 avg -2.256.

Verdict: no promotion. TSLAON is killed current despite good metadata because the edge is too thin and min-negative after transfer fee. Add it to scanner regression cases and revisit only if a future window shows 1,000+ USDT with a materially positive minimum.

### Lower-Cap Retest - 11:31 CST

Retested the two routes downgraded by the 11:06 active refresh.

- VANRY MEXC -> Binance USDC after the 80 VANRY withdrawal fee: 2,500 USDC stayed 4/4 positive, avg +944.584 bps, min +917.416. 5,000 USDC was also 4/4 positive, avg +180.869, min +17.544, but the edge is thin enough to keep 5,000 live-threshold-only after the prior negative tail.
- GUA MEXC -> Gate pre-positioned-only after exact Gate 20 bps pair fee: 500 USDT stayed 4/4 positive, avg +494.485 bps, min +380.031; 1,000 stayed 4/4 positive, avg +331.502, min +139.719; 2,500 stayed unstable at 2/4 positive, avg -11.679, min -132.673.

Verdict: restore VANRY USDC firm measurement cap to 2,500 only. Restore GUA pre-positioned lower cap to 1,000 only. Keep VANRY USDC 5,000 and GUA 2,500 out of firm caps.

### Coinbase-Inclusive U.S. Scan - 11:34 CST

Filled the Coinbase gap from the earlier U.S.-available scan.

- Coinbase broker `best_bid_ask` endpoint returned `Unauthorized`, so the scan used concurrent public Coinbase Exchange `/products/{id}/ticker` calls.
- Markets with usable bid/ask: Coinbase 165, Binance.US 256, Kraken 753, Bitstamp 137, for 1,311 total.
- Positive top-of-book rows after conservative fees: LIT Kraken -> Bitstamp, VELO Kraken -> Coinbase, SUP Kraken -> Coinbase, ENJ Kraken -> Bitstamp, MANA Kraken -> Bitstamp, and MANA Coinbase -> Bitstamp.
- LIT, VELO, and SUP are known ticker-collision/asset-migration traps. ENJ remains the existing 500 USD scanner-only chain-mismatch basis.
- MANA Coinbase -> Bitstamp depth after Coinbase 120 bps + Bitstamp 40 bps + 2 bps latency was negative from the first bucket: 25 USD -1,619.081 bps, 100 -1,805.005, 250 -3,504.835, and Bitstamp bids exhausted by 500.

Verdict: no new U.S.-available promotion. Keep Coinbase Exchange ticker calls available for future U.S. scans, but kill the current Coinbase-inclusive routes.

### U.S. Same-Venue Triangular Scan - 11:36 CST

Tested taker-only USD/USDT/USDC triangular cycles on U.S.-available venues.

- Binance.US: 118 cycles; best was USDT -> ETH -> USDC -> USDT at -5.836 bps after 2 bps per leg.
- Coinbase Exchange: 16 cycles; best was USD -> BTC -> USDT -> USD at -355.317 bps under the conservative 120 bps taker model.
- Kraken: 244 cycles; best was USDT -> USDG -> USD -> USDT at -117.427 bps with 40 bps per leg.
- Bitstamp: 24 cycles; best was USD -> BTC -> USDT -> USD at -119.488 bps with 40 bps per leg.

Verdict: no U.S.-available taker triangular promotion. Revisit only if using maker/rebate or account-specific fee tiers.

### Active Watch Refresh - 11:38 CST

Ran another compact active refresh across current watch routes.

- VANRY MEXC -> Binance USDT after the 80 VANRY withdrawal fee: 10,000 USDT stayed 4/4 positive, avg +301.248 bps, min +256.660. Keep the 10,000 USDT cap.
- VANRY MEXC -> KuCoin USDT after the 80 VANRY fee: 5,000 USDT stayed 4/4 positive, avg +366.447 bps, min +284.561. Keep the 5,000 USDT cap.
- VANRY MEXC -> Binance USDC after the 80 VANRY fee: 2,500 USDC stayed 4/4 positive, avg +821.553 bps, min +632.805. 5,000 USDC was only 2/4 positive, avg -8.320, min -248.499. Keep firm cap at 2,500 and kill 5,000 current.
- ESPORTS LBank -> MEXC scanner-only after LBank withdrawal fee: 2,500 USDT stayed 4/4 positive, avg +200.590 bps, min +182.457. 5,000 USDT was 0/4 positive, avg -18.782. Keep scanner cap at 2,500 and kill 5,000 current.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD stayed 4/4 positive, avg +1,022.532 bps, min +1,015.964; 1,000 USD stayed 0/4 positive, avg -241.402. Keep cap at 500.

Verdict: no ranking promotion, but current caps are cleaner: VANRY USDT 10,000, VANRY KuCoin 5,000, VANRY USDC 2,500, ESPORTS 2,500 scanner-only, ENJ 500 scanner-only.

### Gemini-Inclusive U.S.-Available Scan - 11:44 CST

Ran a corrected U.S.-available public-market scan including full Gemini coverage.

- Scope: Coinbase Exchange, Binance.US, Kraken, Bitstamp, and Gemini across USD/USDT/USDC books.
- Markets: 1,904 usable bid/ask markets. Coinbase 423, Binance.US 256, Kraken 771, Bitstamp 138, Gemini 316.
- Endpoint errors: 4, mostly Coinbase 429 and Gemini metadata misses.
- Positive top-of-book rows after conservative fees: LIT Kraken -> Bitstamp, VELO Kraken -> Coinbase, SUP Kraken -> Coinbase, OPG Gemini -> Coinbase, ENJ Kraken -> Bitstamp, MANA into Bitstamp, and INJ into Gemini.

Depth and identity:

- LIT/VELO/SUP remain ticker-collision or representation traps. The depth is real but the asset identity is not proven same-network/same-asset.
- The new Gemini OPG row is a parser bug, not an edge. Gemini per-symbol details for `opgusd` report base `OP`, quote `GUSD`, and contract price currency `GUSD`; Coinbase `OPG` is Opengradient on Base. Scanner must not suffix-parse Gemini symbols.
- INJ looked positive top-of-book into Gemini, but depth killed it from the first bucket: Bitstamp -> Gemini -118.986 bps from 25-500 USD, Kraken -> Gemini about -130 bps from the first bucket, and Coinbase -> Gemini about -195 bps from the first bucket.
- MANA remains killed by Bitstamp destination depth.
- ENJ remains the existing scanner-only 500 USD chain-mismatch pocket; no new execution path was found.

Verdict: no U.S.-available promotion. Add Gemini per-symbol details and GUSD lane rejection to scanner gates. Keep U.S.-available taker execution killed except the existing ENJ scanner-only watch.

### Scheduled Funding And Bitso Refresh - 11:47 CST

Funding:

- `scripts/funding_probe.py` returned Binance 14 routes, Bybit 14, OKX 14, and Coinbase INTX 5 with zero endpoint errors.
- Best one-period proxy was Coinbase INTX DOGE at -9.898 bps.
- Next rows were Coinbase INTX SOL -10.471, XRP -11.186, BTC -11.980, ETH -14.074, Bybit WLD -14.797, OKX WLD -16.908, OKX TRX -18.330, Binance TRX -18.524, and Binance WLD -19.439.
- Verdict: no funding promotion; all rows remain negative before borrow, margin, exit-basis, and liquidation risk.

Bitso MXN/stable/crypto basis:

- Tickers: USD/MXN 17.309/17.322, USDT/MXN 17.296/17.315, PYUSD/MXN 17.361/17.420, BTC/MXN 1,283,510/1,286,010, BTC/USD 74,052/74,076.
- Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -77.485 bps net after two fees.
- USDT/MXN comparisons were -103.465 and -115.010 bps net.
- Crypto/MXN implied routes remained negative after three fees: BTC best -147.151 bps, XRP -154.263, ETH -155.149.
- Verdict: no MXN-lane promotion.

### Active Watch Refresh - 11:51 CST

Ran a four-sample active refresh across current watch routes. Public REST was slow: samples took 12.4s to 16.2s, and the full pass ran from 11:49:57 to 11:51:10 CST.

- VANRY MEXC -> Binance USDT after the 80 VANRY withdrawal fee: 10,000 USDT stayed 4/4 positive, avg +290.414 bps, min +208.947. Keep the 10,000 USDT cap.
- VANRY MEXC -> KuCoin USDT after the 80 VANRY fee: 5,000 USDT stayed 4/4 positive, avg +225.427 bps, min +123.462. Keep the 5,000 USDT cap.
- VANRY MEXC -> Binance USDC after the 80 VANRY fee: 2,500 USDC stayed 4/4 positive, avg +853.068 bps, min +751.993. 5,000 USDC was 4/4 positive but thin, avg +368.305, min +12.665; do not restore it as a firm cap because prior refreshes printed negative tails.
- ESPORTS LBank -> MEXC scanner-only after the LBank withdrawal fee: 2,500 USDT stayed 4/4 positive, avg +89.088 bps, min +72.064. 5,000 USDT was 0/4 positive, avg -199.662. Keep scanner cap at 2,500 and continue treating execution as blocked by LBank status/account proof.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD stayed 4/4 positive, avg +1,053.865 bps, min +1,049.290. 1,000 USD was 0/4 positive, avg -529.055. Keep cap at 500 and chain-mismatch blocked.
- ULTIMA MEXC -> KuCoin before chain proof: 5,000 USDT stayed 4/4 positive, avg +364.068 bps, min +324.264. Keep chain-proof-only.
- GUA MEXC -> Gate pre-positioned-only: 1,000 USDT stayed 4/4 positive, avg +43.522 bps, min +22.969; 2,500 was 0/4 positive, avg -195.169. Keep only the 1,000 pre-positioned lower cap and monitor decay.

Verdict: ranking unchanged. VANRY USDT routes remain the only strong `DO_NOW` public-book pockets for non-U.S. compliant setups. ESPORTS and GUA are decaying at their small caps; do not expand them.

### Liquid Static Refresh - 11:53 CST

Ran `scripts/market_probe.py` across the existing static venue set.

- Markets: 10,204 total across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso.
- Endpoint errors: 0.
- No positive sane-priority route after generic fees and latency.
- Best rows were already negative before depth: BTC Crypto.com -> Bitfinex USD -2.027 bps, SOL Crypto.com -> Bitfinex -2.317, XRP Crypto.com -> Bitfinex -2.443, ETH Crypto.com -> Bitfinex -2.578, and SUI Crypto.com -> Bitfinex -2.776.
- Best USDT rows were also negative, led by NEAR Bitget -> Binance/Bybit/OKX at -6.615 bps and SUI Gate -> MEXC at -7.184.

Verdict: no liquid static promotion. Skip depth because the first ranking layer is negative; keep static routes as a regression monitor only.

### Event-Window Sampler - 11:58 CST

Ran a fresh event-window sampler after the static refresh.

Discovery:

- Scope: three top-of-book samples across 10,122 markets per sample, excluding Bitso for speed and excluding current watchlist/recent killed bases.
- Endpoint errors: 0.
- Persistent filtered rows: 77.
- Top rows were UPC MEXC -> Bitget, IAG Gate/KuCoin -> Bitget, POWER MEXC/Bitget -> Gate, ARTFI MEXC -> Gate, HYDRA MEXC -> KuCoin, SWEAT Bitget/MEXC -> Gate, and smaller AVT/PVT/VRA/NERO/TOWER/ALKIMI/TTD/TYCOON rows.

Depth and metadata:

- UPC MEXC -> Bitget was the standout book survivor: 50 +3,064.015 bps, 1,000 +2,712.189, 2,500 +2,303.184, 5,000 +2,050.440 after exact fees. MEXC identifies UPC as UPCX on ERC20 contract `0x487d62468282bd04ddf976631c23128a425555ee`; Bitget exposes the same ERC20 contract, but public coin metadata has `rechargeable=false`. Repeatable direct transfer is killed; keep only as pre-positioned Bitget inventory watch.
- POWER Bitget -> Gate stayed positive through 5,000 USDT (+227.138 bps), and POWER MEXC -> Gate stayed positive through 2,500 (+820.137) but was negative by 5,000. Gate reports POWER deposits disabled, so this is pre-positioned Gate inventory only.
- IAG Gate/KuCoin -> Bitget stayed positive through 1,000 but negative by 2,500. Gate and KuCoin ADA lanes are enabled, but Bitget IAG has `rechargeable=false`, killing repeatable transfer.
- HYDRA MEXC -> KuCoin stayed positive through 1,000 but KuCoin HYDRA deposits are disabled.
- SWEAT and VRA into Gate were blocked by Gate deposit-disabled metadata. ARTFI, AVT, PVT, NERO, TOWER, ALKIMI, TTD, and TYCOON either failed by 250-500 USDT or are known identity/status traps.

Verdict: no repeatable-transfer promotion. Add UPC and POWER as `LATER` pre-positioned-inventory watches; everything else from this pass is killed unless deposits reopen and fresh depth survives.

### Deposit Sweep - 12:01 CST

Ran a public deposit-status sweep for the top blocked routes from the event-window and pre-positioned watchlists.

- Gate deposits remain disabled for GUA, TBC, ESPORTS, RAVE, POWER, SWEAT, VRA, and ARTFI.
- KuCoin deposits remain disabled for RAVE and HYDRA. KuCoin deposits are enabled for ULTIMA, IAG, TOWER, and XMN, but those routes remain blocked by other gates: ULTIMA MEXC representation mismatch, IAG Bitget destination deposits disabled, TOWER contract mismatch, and XMN pending MEXC withdrawal status/fee.
- Bitget deposits remain disabled for UPC, IAG, RAVE, BTR, and SUP. Bitget VELO deposits are enabled on BEP20, but the U.S. VELO row is a Kraken/Coinbase identity trap and not a Bitget route.
- Gate TYCOON deposits are enabled on BSC, but TYCOON failed the event-window depth walk by 100-250 USDT.

Verdict: no blocked route became repeatable. Keep UPC/POWER/GUA/RAVE/TBC-style rows pre-positioned-only unless destination deposits reopen and fresh depth still survives.

### XMN Resolution - 12:03 CST

Resolved the stale XMN micro-route.

- Route: MEXC `XMNUSDT` -> KuCoin `XMN-USDT`.
- Identity: MEXC and KuCoin both identify xMoney on SUI contract `0x97c7571f4406cdd7a95f3027075ab80d3e9c937c2a567690d31e14ab1872ccee::xmn::XMN`.
- MEXC public fee endpoint lists XMN SUI withdrawal fee `8`, deposit fee `0`, and withdrawal minimum `20`.
- KuCoin SUI deposits and withdrawals are enabled.
- Fresh depth after MEXC 5 bps, KuCoin 10 bps, 2 bps latency, and 8 XMN withdrawal fee: 50 USDT -124.436 bps, 100 -174.141, 250 -253.750, 500 -326.768, 1,000 -364.574, and 2,500 -1,760.965.

Verdict: kill current XMN. The route is no longer pending metadata; it is simply negative after transfer fee and depth.

### Active Watch Refresh - 12:05 CST

Ran a three-sample active refresh from 12:05:04 to 12:05:40 CST.

- VANRY MEXC -> Binance USDT after the 80 VANRY withdrawal fee: 10,000 USDT stayed 3/3 positive, avg +328.791 bps, min +236.042. Keep the 10,000 USDT cap for non-U.S. compliant setups.
- VANRY MEXC -> KuCoin USDT after the 80 VANRY fee: 5,000 USDT stayed 3/3 positive, avg +290.453 bps, min +229.884. Keep the 5,000 USDT cap.
- VANRY MEXC -> Binance USDC after the 80 VANRY fee: 2,500 USDC stayed 3/3 positive, avg +921.386 bps, min +709.668. 5,000 USDC was only 2/3 positive with min -177.208, so keep 5,000 killed-current.
- ESPORTS LBank -> MEXC scanner-only flipped negative: 2,500 USDT was 0/3 positive, avg -23.699 bps, min -36.068; 5,000 USDT was also 0/3. Kill the current ESPORTS LBank cap until rediscovered.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD stayed 3/3 positive, avg +1,041.487 bps, min +1,038.871. 1,000 USD also printed 3/3 positive, avg +194.732, min +182.584, but prior 1,000 was 0/4 and transfer remains chain-mismatch blocked, so keep firm cap at 500 pending a longer retest.
- ULTIMA MEXC -> KuCoin before chain proof: 5,000 USDT stayed 3/3 positive, avg +439.480 bps, min +432.244. Keep chain-proof-only.
- GUA MEXC -> Gate pre-positioned-only: 1,000 USDT stayed 3/3 positive, avg +159.317 bps, min +108.160; 2,500 was 0/3 positive. Keep only the 1,000 pre-positioned cap while Gate deposits are disabled.
- UPC MEXC -> Bitget active-watch rows errored and are not evidence. Retain the 11:58 direct-depth result until a clean retest.

Verdict: VANRY USDT routes remain the only strong `DO_NOW` public-book pockets, subject to account/region proof. ESPORTS LBank -> MEXC is demoted to `KILL_CURRENT`; ENJ 1,000 needs longer retest before cap restoration.

### UPC Clean Direct Retest - 12:09 CST

Resolved the UPC active-watch error with a direct one-off retest.

- Route: MEXC `UPCUSDT` -> Bitget `UPCUSDT`.
- Direct books fetched cleanly at 12:09:47 CST.
- Net depth after MEXC 5 bps, Bitget 10 bps, and 2 bps latency: 50 USDT +3,071.889 bps, 100 +2,984.681, 250 +2,861.136, 500 +2,814.170, 1,000 +2,681.199, 2,500 +2,279.171, 5,000 +2,038.202, and 10,000 +1,575.217.
- Bitget UPC metadata still shows ERC20 contract `0x487d62468282bd04ddf976631c23128a425555ee` with `withdrawable=true` and `rechargeable=false`.

Verdict: keep UPC as a high-bps `LATER` pre-positioned Bitget inventory watch. Do not promote repeatable transfer while Bitget deposits are disabled.

### Scheduled Funding, Bitso, And Static Refresh - 12:10 CST

Ran the scheduled monitors after the UPC retest.

Funding:

- `scripts/funding_probe.py` returned Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, and zero endpoint errors.
- Best one-period proxy was Coinbase INTX SOL at -7.932 bps.
- Next rows were Coinbase INTX BTC -8.328, DOGE -8.888, ETH -9.443, XRP -9.679, Bybit WLD -14.551, OKX TRX -16.123, OKX WLD -16.725, Bybit TRX -17.725, and Binance TRX -18.480.
- Verdict: no funding promotion.

Bitso MXN/stable/crypto basis:

- Tickers: USD/MXN 17.332/17.333, USDT/MXN 17.317/17.318, PYUSD/MXN 17.365/17.428, BTC/MXN 1,281,470/1,282,320, BTC/USD 73,941/73,975.
- Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -81.472 bps net after two fees.
- USDT/MXN comparisons were -91.747 and -108.889 bps net.
- Crypto implied MXN routes remained negative after three fees: XRP best -152.358 bps, ETH -154.422, BTC -154.926.
- Verdict: no MXN-lane promotion.

Broad liquid static:

- `scripts/market_probe.py` scanned 10,204 markets with zero endpoint errors.
- No sane-priority route was positive after generic fees and latency.
- Best rows were already negative: BTC Crypto.com -> Bitfinex USD -2.237 bps, XRP Crypto.com -> Bitfinex -3.212, SOL Crypto.com -> Bitfinex -4.133, LTC Crypto.com -> Bitfinex -4.200, ETH Crypto.com -> Bitfinex -4.646.
- Best USDT rows were also negative: TON MEXC -> Bitget -11.398 bps, SUI Gate -> MEXC -11.536, APT Bitget -> MEXC -11.715.

Verdict: no scheduled-monitor promotion. Keep focus on VANRY account/region proof, event-window discovery, and pre-positioned-inventory alerts.

### Event-Window Sampler - 12:15 CST

Ran a fresh event-window sampler after the scheduled monitors.

Discovery:

- Scope: three top-of-book samples across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, and Bitfinex; Bitso excluded for speed.
- Markets: 10,122 per sample.
- Endpoint errors: 0.
- Persistent filtered rows: 83 after current watchlist and recent false-positive exclusions.
- Top clusters were not new promotions: RWA Gate/MEXC/Bitget -> KuCoin is the known same-ticker collision, and AI Binance/Gate -> KuCoin/MEXC/OKX is a known identity-conflict cluster.

Depth:

- REACT KuCoin -> Gate: +170.654 bps at 50 USDT, +103.340 at 100, -3.032 at 250, and negative beyond.
- GHX Gate -> MEXC: +207.226 at 50, +168.406 at 100, +96.568 at 250, +34.615 at 500, and -21.417 at 1,000. KuCoin -> MEXC was similar and negative by 1,000.
- LOFI, EQTY, MODE, KARRAT, CTA, ITHACA, and PIN were negative from 50 USDT or failed sell depth. BRISE and LONG were positive only at 50-100.

Verdict: no promotion. The event-window scanner needs a hard rule: do not spend metadata time below 1,000 USDT positive direct depth unless Pedro explicitly wants micro one-shot liquidation alerts.
