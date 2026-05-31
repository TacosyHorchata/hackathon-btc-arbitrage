# Agent 2 Kill List

Updated: 2026-05-29 12:16 CST

## KILL - 12:13 Event-Window Sampler

- reason: persistent top-of-book rows collapsed under direct depth or were already-known identity traps.
- evidence:
  - Three event-window samples ran from 12:13:27 to 12:14:12 CST across 10,122 markets per sample with zero endpoint errors.
  - RWA Gate/MEXC/Bitget -> KuCoin topped the sampler but remains a known same-ticker collision: MEXC/Gate/Bitget Allo vs KuCoin RWA Inc.
  - AI Binance/Gate -> KuCoin/MEXC/OKX also topped the sampler but remains a known identity-conflict cluster.
  - REACT KuCoin -> Gate was positive only at 50 and 100 USDT, then -3.032 bps at 250 and worse beyond.
  - GHX Gate/KuCoin -> MEXC stayed positive through 500 USDT but flipped negative by 1,000 and had already failed a prior processed-base depth pass.
  - LOFI, EQTY, MODE, KARRAT, CTA, ITHACA, and PIN were negative from 50 USDT or failed sell depth; BRISE and LONG were micro-only.
- exact failure mode: identity traps plus insufficient executable depth.
- stop condition: revisit only if a future pass produces 1,000+ USDT positive direct depth after exact fees and identity metadata is clean.

## KILL - 12:10 Scheduled Funding, Bitso, And Liquid Static

- reason: the scheduled monitors produced no positive executable first-layer signal.
- evidence:
  - Funding refresh returned Binance 14, Bybit 14, OKX 14, Coinbase INTX 5, and zero endpoint errors. Best one-period proxy was Coinbase INTX SOL -7.932 bps, followed by BTC -8.328, DOGE -8.888, ETH -9.443, and XRP -9.679.
  - Bitso public tickers at 12:10 CST showed USD/MXN 17.332/17.333, USDT/MXN 17.317/17.318, and PYUSD/MXN 17.365/17.428. Best stable comparison was PYUSD/MXN sell vs USD/MXN buy at -81.472 bps net after two fees.
  - Bitso crypto implied routes were also negative after three fees: XRP best -152.358 bps, ETH -154.422, and BTC -154.926.
  - Broad static scan covered 10,204 markets with zero endpoint errors. No sane-priority route was positive after generic fees and latency; best row was BTC Crypto.com -> Bitfinex at -2.237 bps.
- exact failure mode: all three monitors fail before order-book walking or operational work.
- stop condition: revisit only on the next scheduled refresh or if a first-layer row becomes materially positive before depth.

## KILL - 12:09 UPC Repeatable Transfer

- reason: the UPC book edge is real in the latest direct retest, but Bitget deposits remain disabled, so the route cannot be replenished by MEXC -> Bitget transfer.
- evidence:
  - 12:09:47 CST direct books fetched cleanly from MEXC and Bitget.
  - UPC MEXC -> Bitget stayed positive through 10,000 USDT after exact fees: 1,000 +2,681.199 bps, 2,500 +2,279.171, 5,000 +2,038.202, and 10,000 +1,575.217.
  - Bitget UPC public metadata reports ERC20 contract `0x487d62468282bd04ddf976631c23128a425555ee`, `withdrawable=true`, but `rechargeable=false`.
- exact failure mode: destination deposit disablement blocks repeatable inventory transfer; this is only actionable if UPC inventory is already on Bitget.
- stop condition: revisit for direct execution only if Bitget UPC deposits reopen and a fresh multi-sample depth pass remains positive after exact fees and transfer fee.

## KILL - 12:05 Active-Watch Cap Failures

- reason: the latest compact active refresh invalidated ESPORTS LBank -> MEXC at its current 2,500 USDT scanner cap and reinforced the killed larger buckets on VANRY USDC and GUA.
- evidence:
  - ESPORTS LBank -> MEXC 2,500 USDT was 0/3 positive from 12:05:04 to 12:05:40 CST, avg -23.699 bps and min -36.068 after conservative fees and the 4.6915 ESPORTS LBank withdrawal fee.
  - ESPORTS 5,000 USDT was also 0/3 positive, avg -318.594 bps and min -333.459.
  - VANRY MEXC -> Binance USDC 5,000 was only 2/3 positive with min -177.208 bps after the 80 VANRY fee, confirming it should not be restored above the 2,500 USDC firm cap.
  - GUA MEXC -> Gate pre-positioned 2,500 remained 0/3 positive, avg -198.137 bps and min -242.965, while Gate deposits remain disabled.
  - UPC MEXC -> Bitget active-watch rows errored and are ignored; the route remains repeatability-killed by Bitget `rechargeable=false`.
- exact failure mode: live depth/cap decay, not only metadata. The current ESPORTS LBank measurement no longer pays after modeled fees, and larger VANRY/GUA buckets retain negative tails.
- stop condition: restore only if a fresh event-window scan redetects the route and a new multi-sample depth pass stays positive at the target cap after exact fees and current transfer/account gates.

## KILL - ESPORTS/RAVE Repeatable Direct Transfer Routes

- reason: live depth and short persistence are strongly positive, but the relevant sell venues have deposits disabled, so MEXC/Bitget -> Gate/KuCoin transfer/rebalance is not repeatable.
- evidence:
  - ESPORTS MEXC -> Gate 10-sample persistence from 08:23:41 to 08:24:29 CST stayed 10/10 positive at 5,000 USDT, avg +2400.213 bps and min +2361.826 bps.
  - ESPORTS identity is clean across MEXC and Gate: Yooldo/Yooldo Games on BSC contract `0xF39e4b21c84e737Df08e2C3b32541d856f508E48`.
  - Gate ESPORTS public currency metadata reports `deposit_disabled=true`; KuCoin and Bitget also report ESPORTS deposits disabled.
  - RAVE Bitget -> KuCoin 10-sample persistence stayed 10/10 positive at 5,000 USDT, avg +1482.521 bps and min +1465.754 bps.
  - RAVE Bitget -> Gate 10-sample persistence stayed 10/10 positive at 5,000 USDT, avg +194.290 bps and min +171.865 bps.
  - RAVE identity is clean across Bitget, KuCoin ERC20, Gate ETH, and MEXC on ERC20 contract `0x17205fab260a7a6383a81452cE6315A39370Db97`.
  - KuCoin and Gate public RAVE metadata report deposits disabled; Bitget reports RAVE `rechargeable=false`.
- exact failure mode: destination deposit disablement blocks repeatable transfer-dependent execution; only one-shot liquidation with pre-positioned sell-venue inventory remains possible.
- stop condition: revisit for direct execution only if sell-venue deposits reopen and a fresh 5,000+ USDT persistence window stays positive after fees.

## KILL - RWA/USDT Same-Ticker Collision

- reason: public metadata identifies different assets under the same `RWA` ticker.
- evidence:
  - MEXC `RWAUSDT` `exchangeInfo` identifies `Allo` on BSC contract `0x9C8B5CA345247396bDfAc0395638ca9045C6586E`.
  - Gate `RWA` public currency metadata also identifies `Allo` on BSC contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`.
  - Bitget `RWA` public coin metadata also uses BEP20 contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`.
  - KuCoin `RWA` public currency metadata identifies `RWA Inc` on Base contract `0xe2b1dc2d4a3b4e59fdf0c47b71a7a86391a8b35a`.
- exact failure mode: same ticker, different asset/contract, so MEXC/Gate/Bitget -> KuCoin RWA routes are invalid.
- stop condition: do not revisit as a direct route unless official metadata changes to a shared asset/contract.

## KILL - Fresh 08:22 Long-Tail Rows Blocked By Deposit/Depth

- reason: the remaining high-bps hard-filter rows failed sell-venue deposit status, depth capacity, or both.
- evidence:
  - `ARTFI` contracts match on SUI, but Gate, KuCoin, and Bitget public metadata all show deposits disabled or withdrawals disabled; depth turns negative by 500-1,000 USDT depending on sell venue.
  - `UPC` MEXC -> Bitget is same ERC20 contract, but Bitget reports `rechargeable=false` and depth was exhausted before 2,500 USDT.
  - `PHB`, `GUA`, `POWER`, and `NERO` MEXC/Bitget -> Gate rows had positive pockets, but Gate deposits are disabled; several also failed before or around 2,500-5,000 USDT.
- exact failure mode: non-repeatable destination inventory and/or insufficient depth.
- stop condition: revisit only if deposits reopen and a fresh persistence check is positive at 2,500+ USDT after fees.

## KILL - Bitso Same-Venue MXN/USD/Stables Refresh 2026-05-29 08:14 CST

- reason: current same-venue stablecoin/FX triangles remain negative after conservative Bitso taker fees.
- evidence:
  - Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`; zero endpoint errors.
  - Current top-of-book reference: `usd_mxn` 17.357/17.358, `usdt_mxn` 17.341/17.350, `usd_usdt` 1.0006/1.0009.
  - Best stablecoin-vs-USD/MXN comparison was PYUSD/MXN sell bid vs USD/MXN ask at -59.255 bps after two fees.
  - Main triangles remained negative: MXN -> USD -> USDT -> MXN at -152.994 bps; MXN -> USDT -> USD -> MXN at -154.138 bps.
- exact failure mode: Bitso spreads and taker fees consume the apparent FX/stablecoin basis.
- stop condition: revisit only if gross dislocation exceeds conservative fees by a wide margin, preferably 150+ bps before any operational work.

## KILL - Immediate Spot-Perp Funding Capture Refresh 2026-05-29 08:13 CST

- reason: one-period funding/basis proxies remain negative after fees and entry basis.
- evidence:
  - 47 public spot/perp proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International; zero endpoint errors; elapsed 19.436 seconds.
  - Best one-hour Coinbase INTX proxies were still negative: SOL -7.982 bps, BTC -8.168 bps, ETH -8.759 bps, DOGE -11.860 bps, XRP -11.950 bps.
  - Best USDT negative-funding route was Binance WLD at -12.436 bps over the 8h proxy; Bybit WLD was -17.141 bps and OKX WLD was -18.750 bps.
- exact failure mode: funding magnitude plus entry basis still does not cover spot/perp open-close fees in the measured holding window.
- stop condition: revisit only if a route shows positive one-period proxy after conservative fees, or if account-specific maker/fee-tier evidence materially lowers the round-trip cost.

## KILL - Crypto.com USD -> Bitfinex USD Majors

- reason: the only initially positive major-pair route, BTC/USD, failed live persistence after fees and latency; ETH/USD, XRP/USD, and SOL/USD were negative from the first depth snapshot.
- evidence:
  - Fresh 08:09 CST public probe found small top-of-book positives on Crypto.com -> Bitfinex USD majors after current Bitfinex zero-fee assumption.
  - Bitfinex official fee schedule currently lists spot maker and taker fees as zero: `https://www.bitfinex.com/fees/`.
  - Bitfinex official U.S.-person FAQ says U.S. citizens/residents cannot use the platform: `https://support.bitfinex.com/hc/en-us/articles/115003461254-U-S-Person-Frequently-Asked-Questions-FAQ`.
  - Depth snapshot after Crypto.com 7.5 bps taker, Bitfinex 0 bps taker, and 4 bps latency had BTC/USD barely positive through 25,000 USD (+1.651 to +1.839 bps), while ETH/USD, XRP/USD, and SOL/USD were negative from 1,000 USD.
  - BTC/USD 10-sample persistence from 08:10:32 to 08:11:18 CST had 0/10 positive at 1,000, 5,000, 10,000, and 25,000 USD; 25,000 USD avg -2.063 bps, min -5.095 bps.
- exact failure mode: sub-2 bps top-of-book pocket decayed before it could survive persistence; account-region gate also blocks U.S.-person execution.
- stop condition: revisit only if Crypto.com -> Bitfinex majors show 10/10 positive persistence above +5 bps at 10,000+ USD after fees/latency and the executor has eligible non-U.S. Bitfinex access.

## KILL - U.S.-Available Static Retest With Corrected Binance.US Fee

- reason: correcting Binance.US public taker from the earlier conservative 10 bps assumption to the official 2 bps taker still leaves the best liquid U.S.-available static routes negative.
- evidence:
  - Targeted retest at 2026-05-29 08:02 CST used Binance.US taker 2 bps, Kraken taker 40 bps, Bitstamp taker 40 bps, and a 2-4 bps latency/lane haircut.
  - BTC/USD Bitstamp -> Binance.US: -38.074 bps.
  - BTC/USDT Bitstamp -> Binance.US: -47.772 bps.
  - SOL/USD Bitstamp -> Binance.US: -44.893 bps.
  - HYPE/USD Bitstamp -> Binance.US: -53.955 bps.
  - USDT/USD Kraken -> Binance.US: -42.495 bps.
- exact failure mode: even low Binance.US taker fees do not overcome the other venue fee burden and live spread on liquid U.S.-available pairs.
- stop condition: revisit only with post-only maker modeling, a materially better account fee tier, or a fresh event-window route that is positive after identity, depth, and adverse-selection checks.

## KILL - TBC/USDT MEXC -> Gate Repeatable Direct Route

- reason: live depth is positive, but Gate deposits are disabled, so MEXC -> Gate transfer/rebalance is not repeatable.
- evidence:
  - MEXC identifies `TBC` as Turingbitchain on chain `TBC`; Gate identifies `TBC` as TuringBitChain on chain `TBC`.
  - Gate public currency endpoint reports `deposit_disabled: true`, `withdraw_disabled: false`, and chain-level `deposit_disabled: true`.
  - MEXC fee-page API returned no TBC withdrawal-fee row in the public query.
  - Live depth after MEXC 5 bps taker and Gate 20 bps fee was positive through 5,000 USDT: +530.107 bps at 50, +444.676 bps at 1,000, +196.087 bps at 5,000.
  - Short persistence check from 07:48:32 to 07:49:30 CST stayed 10/10 positive at 5,000 USDT, avg +198.175 bps and min +196.087 bps.
- exact failure mode: transfer/rebalance blocked by destination deposit disablement.
- stop condition: revisit only if Gate TBC deposits reopen or Pedro already has TBC inventory on Gate and wants a one-shot pre-positioned-inventory liquidation measurement.

## KILL - Fresh 07:48 Non-TBC Watch Rows

- reason: depth/capacity failed before transfer metadata became worth chasing.
- evidence:
  - Fresh global probe scanned 10,216 markets, found 99 filtered top-of-book watch rows, and had zero endpoint errors.
  - `YFII` MEXC -> Gate was negative from 50 USDT (-232.151 bps).
  - `DCK` Gate -> MEXC was positive only at 50 USDT (+128.051 bps) and negative by 100 USDT.
  - `DN` KuCoin -> Gate was negative from 50 USDT (-104.113 bps).
  - `AO` Bybit -> Gate was positive through 1,000 USDT but negative by 2,500 USDT; `AO` MEXC -> Gate was negative by 1,000 USDT.
  - `HONEY` and `AVL` MEXC -> Gate were negative from 50 USDT.
  - `QAIT` Gate -> KuCoin was positive only below 500 USDT.
- exact failure mode: stale top-of-book signal, insufficient capacity, or both.
- stop condition: revisit only if a fresh persistence window shows 2,500+ USDT buckets positive after fees and transfer/deposit status is clean.

## KILL - Bitso Same-Venue MXN/USD/Stables Refresh 2026-05-29 07:43 CST

- reason: current same-venue stablecoin/FX triangles remain negative after conservative Bitso taker fees.
- evidence:
  - Books queried: `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn`; zero endpoint errors.
  - Best stablecoin-vs-USD/MXN comparison was PYUSD/MXN sell bid vs USD/MXN ask at -61.841 bps after two fees.
  - Main triangles remained negative: MXN -> USDT -> USD -> MXN at -130.714 bps; MXN -> USD -> USDT -> MXN at -173.687 bps.
- exact failure mode: Bitso spreads and taker fees consume the apparent FX/stablecoin basis.
- stop condition: revisit only if gross dislocation exceeds conservative fees by a wide margin, preferably 150+ bps before any operational work.

## KILL - Immediate Spot-Perp Funding Capture Refresh 2026-05-29 07:42 CST

- reason: one-period funding/basis proxies are still negative after fees and entry basis.
- evidence:
  - 47 public spot/perp proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International; zero endpoint errors.
  - Best one-hour Coinbase INTX proxies remained negative: BTC -6.535 bps, ETH -8.212 bps, XRP -10.401 bps, SOL -10.444 bps, DOGE -10.832 bps.
  - Best USDT negative-funding route was Bybit TRX, still negative at -18.189 bps over the 8h proxy.
- exact failure mode: funding magnitude and entry basis do not cover spot/perp open-close fees in the measured holding window.
- stop condition: revisit only if a route shows positive one-period proxy after conservative fees, or if maker/account-tier assumptions reduce the explicit round-trip cost with real account evidence.

## KILL - Immediate U.S.-Available Maker/Rebate Rescue

- reason: public fee schedules do not create an immediate static edge without an account-specific fee tier, queue/fill model, and post-only execution engine.
- evidence:
  - Binance.US is useful but not sufficient by itself: official announcement says Advanced Spot fees are 0% maker and 0.02% taker for every user (`https://blog.binance.us/zero-fee-trading/`), but the 07:29 U.S.-venue scan showed liquid static routes around -43 to -51 bps after conservative taker fees.
  - 08:02 targeted retest with Binance.US taker corrected to 2 bps still left prior best liquid rows negative, from -38.074 bps to -53.955 bps.
  - Kraken publishes a spot maker-rebate table, but the public rebate starts at high 30-day volume on selected lower-liquidity pairs, not as a default retail edge: `https://www.kraken.com/features/fee-schedule`.
  - Coinbase Advanced VIP best public spot tier is 0 bps maker / 3.5 bps taker at VIP 6, but the public threshold is institutional-scale: `https://www.coinbase.com/advanced-vip`.
- exact failure mode: fee improvement alone is too small for static taker/maker arb; strategy needs queue priority, fill probability, adverse-selection controls, and account-specific tier proof.
- stop condition: revisit only after account fee tier is known or a live event-window detector finds a route where maker posting has positive expected value after adverse selection.

## KILL - U.S.-Available Venue Substitution Static Scan

- reason: no clean U.S.-available static route survived identity, fees, and depth.
- evidence:
  - Public scan covered Binance.US, Coinbase Exchange, Kraken, Gemini, and Bitstamp: 1,971 markets, 378 common USD/USDT/USDC keys, 0 endpoint errors.
  - Liquid majors were negative after conservative fees. Examples: BTC/USD Bitstamp -> Binance.US -43.075 bps, BTC/USDT Bitstamp -> Binance.US -46.248 bps, SOL/USD Bitstamp -> Binance.US -47.106 bps, USDT/USD Kraken -> Binance.US -50.795 bps.
  - Long-tail positives were ticker collisions or failed depth: Kraken `LIT` is Litentry while Bitstamp `LIT` is Lighter; Kraken `VELO` is Velo while Coinbase `VELO` is Velodrome Finance; Kraken `SUP` is Superp while Coinbase `SUP` is Superfluid.
- exact failure mode: fee burden on liquid pairs; same-ticker different-asset collisions on long-tail pairs.
- stop condition: revisit only with a fee-tier/maker-rebate model, a fresh event-window scan, or a new U.S.-available listing that survives official asset identity and depth.

## KILL - LIT/USD Kraken -> Bitstamp Current Direct Route

- reason: ticker collision.
- evidence: Kraken public pages identify `LIT` as Litentry; Bitstamp trading-pair info describes `LIT/USD` as Lighter / U.S. dollar. Live depth looked +102,334 bps at 1,000 USD only because the assets are different.
- exact failure mode: same ticker, different asset.
- stop condition: do not revisit unless official metadata proves a common asset/network, which current evidence contradicts.

## KILL - VELO/USD Kraken -> Coinbase Current Direct Route

- reason: ticker collision.
- evidence: Kraken lists `VELO` as Velo and separately lists Velodrome Finance under `VELODROME`; Coinbase Exchange currency metadata identifies `VELO` as Velodrome Finance on Optimism contract `0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db`. Live depth looked +26,607 bps at 5,000 USD only because the assets are different.
- exact failure mode: same ticker, different asset.
- stop condition: do not revisit as a direct `VELO` route.

## KILL - SUP/USD Kraken -> Coinbase Current Direct Route

- reason: ticker collision.
- evidence: Kraken public pages identify `SUP` as Superp; Coinbase Exchange currency metadata identifies `SUP` as Superfluid on Base contract `0xa69f80524381275A7fFdb3AE01c54150644c8792`. Live depth looked +19,028 bps at 5,000 USD only because the assets are different.
- exact failure mode: same ticker, different asset.
- stop condition: do not revisit as a direct `SUP` route.

## KILL - GWEI/USD Kraken -> Coinbase Current Direct Route

- reason: live depth is negative after fees.
- evidence: top-of-book scan showed only +14.403 bps after conservative fees, then live depth measured -223.485 bps at 50 USD and worse.
- exact failure mode: top-of-book signal failed executable depth.
- stop condition: revisit only if a fresh persistence window shows 500+ USD buckets positive after fees and identity is fully confirmed.

## KILL - TRAC/USD Kraken -> Bitstamp Current Direct Route

- reason: live depth is negative after fees.
- evidence: top-of-book scan showed only +1.337 bps after conservative fees, then live depth measured -77.963 bps at 50 USD and worse.
- exact failure mode: top-of-book signal failed executable depth.
- stop condition: revisit only if 500+ USD buckets become positive after fees.

## KILL - U.S.-Resident Execution Path For Current MEXC/KuCoin VANRY/ULTIMA Routes

- reason: the best public-book routes require MEXC as buy venue, KuCoin as one sell venue, or Binance global as sell venue; current official regional evidence blocks treating this as executable for a U.S.-resident account.
- evidence:
  - MEXC official restricted-jurisdiction page, updated Apr 17, 2026, lists the United States among prohibited jurisdictions and says MEXC does not accept registrations or trading applications from those areas: `https://www.mexc.com/learn/article/mexc-restricted-countries-complete-list-of-prohibited-limited-regions/1?handleDefaultLocale=keep`.
  - KuCoin Terms of Use, last updated Jan 29, 2026, list the United States and U.S. territories as restricted locations: `https://www.kucoin.com/legal/terms-of-use`.
  - Binance.US is not a VANRY fallback: `exchangeInfo?symbol=VANRYUSDT` and `VANRYUSDC` returned invalid-symbol errors, full Binance.US `exchangeInfo` had 623 symbols and no `VANRY`, and the official supported-crypto page contains no `VANRY`: `https://support.binance.us/hc/en-us/articles/360049417674-List-of-supported-cryptocurrencies`.
- exact failure mode: compliance/account eligibility, not market depth.
- stop condition: revisit only if Pedro confirms a compliant non-U.S.-restricted account setup for MEXC and the relevant sell venue, or if a U.S.-available venue lists the same asset and survives the depth/fee/identity gates.

## KILL - Naive Long-Tail Ticker Arbitrage Without Identity Checks

- examples observed: `VON`, `TROLL`, `ELON`, `HOLD`, `U`, `X`, `EDGE`
- reason: public ticker scan produced impossible spreads from same-symbol assumptions. Same ticker across exchanges is not proof of same asset.
- exact failure mode: symbol collision, redenomination, unsupported market state, wrong base parsing, or stale/broken ticker.
- stop condition: do not rank long-tail routes until market metadata verifies asset identity and current tradability.
- replacement action: add a strict allowlist first (`BTC`, `ETH`, `SOL`, `XRP`, `DOGE`, `LTC`, `XMR`, etc.) or verify token identity per venue before scoring.

## KILL - Bitso Immediate MXN/USD/USDT Triangles

- route checked: `usd_mxn`, `usdt_mxn`, `usd_usdt`
- reason: spread and Bitso taker fee kill the triangle.
- evidence: `usdt_mxn` ask/bid around 17.328/17.326, `usd_mxn` around 17.342/17.341, `usd_usdt` around 1.0011/1.0010 at 2026-05-29 02:54 CST.
- net conclusion: no immediate stablecoin/MXN triangle after fees.
- stop condition: only revisit if gross triangle exceeds 120+ bps or Pedro has a much lower Bitso fee tier.

## KILL - Bitso BTC/ETH/SOL/XRP MXN vs USD-Implied Immediate Arb

- route checked: Bitso MXN books versus Bitso USD books multiplied by `usd_mxn`.
- reason: gross basis was negative or single-digit positive before fees.
- evidence:
  - BTC MXN bid vs USD-implied ask: about -7.1 bps.
  - ETH MXN bid vs USD-implied ask: about -2.3 bps.
  - SOL MXN bid vs USD-implied ask: about -5.5 bps.
  - XRP MXN bid vs USD-implied ask: about +7.1 bps gross, still far below fee burden.
- net conclusion: fake edge for current challenge window.

## KILL - Coinbase/Gemini Retail-Tier Aggressive Arb As First Path

- reason: default taker assumptions are around 120 bps each on Coinbase/Gemini low tiers, so aggressive spot arbitrage needs absurd gross spread.
- source: `docs/exchange-fees.md`.
- net conclusion: useful for data coverage, bad as first execution venue unless Pedro's actual fee tier is much lower.

## KILL - XMR/USDT KuCoin -> MEXC Direct Route

- reason: promising short-window top-of-book/depth signal failed persistence and notional buckets.
- evidence: 120 public depth samples from 2026-05-29 02:57:52 to 03:09:12 CST.
- result:
  - 0.5 XMR: 60.8% positive, average +0.256 bps.
  - 1 XMR: 55.0% positive, average -0.648 bps.
  - 2 XMR: 25.0% positive, average -2.512 bps.
- exact failure mode: too unstable and too thin after fees/latency. The occasional positive ticks are noise, not a route to build first.
- stop condition: killed because 0.5 XMR was below 70% positive and below +2 bps average net.

## KILL - AI/USDT Binance -> OKX

- reason: confirmed ticker collision.
- evidence:
  - Binance official listing: `AI` = Sleepless AI, `AI/USDT` opened in January 2024.
  - OKX official listing: `AI/USDT` = Gensyn, spot opened on May 22, 2026.
- exact failure mode: symbol equality produced a fake cross-exchange route between two different assets.
- why it matters: naive depth math showed hundreds of bps net and large notional, so this would have looked like the best route without identity validation.
- stop condition: kill any cross-exchange route where official listings identify different projects under the same ticker.

## KILL - DYDX/USDT Binance -> OKX Current Direct Route

- reason: filtered top-of-book signal vanished by depth validation.
- evidence: current depth was negative in both directions across 100 to 25,000 USDT buckets.
- exact failure mode: small spreads are stale before they become executable.
- stop condition: no promotion without live depth positivity.

## KILL - MMT/USDT OKX -> Binance Current Direct Route

- reason: best direction was negative after fees and latency haircut.
- evidence: OKX buy -> Binance sell measured about -12.6 bps net at 100 USDT and -14.3 bps net at 1,000 USDT.
- exact failure mode: visible top-of-book spread did not survive taker fees.
- stop condition: no promotion unless net bps remains positive after depth buckets.

## KILL - ALLO/USDT Gate -> Bitget Current Direct Route

- reason: negative after real depth and fees.
- evidence: Gate buy -> Bitget sell measured about -26.1 bps net at 100 USDT and worsened with size.
- exact failure mode: Gate pair fee metadata (`0.2`) is higher than the generic scan assumption, and the book no longer had a positive executable spread.
- stop condition: no promotion without venue-specific fee metadata.

## KILL - GENIUS/USDT MEXC/Binance -> Bitget Current Direct Route

- reason: negative after depth and fees.
- evidence: MEXC buy -> Bitget sell measured about -20.9 bps net at 100 to 1,000 USDT; Binance buy -> Bitget sell measured about -28.1 bps net.
- exact failure mode: modest top-of-book signal vanished before depth validation.
- stop condition: no promotion unless depth validation is positive immediately and remains positive in a persistence window.

## KILL - BSB/USDT Bitget -> Bybit Current Direct Route

- reason: negative after live depth and fees.
- evidence: Bitget buy -> Bybit sell measured about -21.6 bps net at 50 USDT and -22.3 bps at 100 USDT.
- exact failure mode: tiny top-of-book spread did not survive taker fees.
- stop condition: no promotion without positive depth buckets.

## KILL - SD/USDT OKX -> Bybit Current Direct Route

- reason: negative after live depth and fees.
- evidence: OKX buy -> Bybit sell measured about -29.3 bps net at 50 USDT; Bybit buy -> OKX sell was much worse.
- exact failure mode: stale/small top-of-book signal plus Bybit `stTag=1` risk.
- stop condition: avoid special-treatment symbols unless spread is large and persistent after costs.

## KILL - CTR/USDT Gate -> MEXC Current Direct Route

- reason: negative after live depth and real venue fees.
- evidence: Gate buy -> MEXC sell measured about -66.6 bps net at 50 USDT; MEXC buy -> Gate sell about -36.3 bps.
- exact failure mode: Gate fee metadata shows `0.2` (20 bps), so small spreads are fake.
- stop condition: require venue-specific fee metadata before ranking Gate routes.

## KILL - BDX/USDT KuCoin -> MEXC Current Direct Route

- reason: negative after live depth and fees.
- evidence: KuCoin buy -> MEXC sell measured about -48.3 bps net at 50 USDT; reverse about -54.9 bps.
- exact failure mode: top bid depth on MEXC was effectively unusable at best price and VWAP turned negative quickly.
- stop condition: no promotion without positive depth buckets.

## KILL - Liquid Taker-Only Triangular Arb On Binance/OKX

- reason: three taker legs cost roughly 30 bps before slippage; measured liquid cycles were already negative at top-of-book.
- evidence:
  - Binance BTC/ETH/SOL USDT-USDC cycles clustered around -29 to -32 bps.
  - OKX BTC/ETH/SOL USDT-USDC cycles clustered around -29 to -32 bps.
- exact failure mode: fee structure dominates stablecoin basis.
- stop condition: only revisit with maker/rebate logic or unusually large gross dislocation.

## KILL - Taker USDT/USD Cross-Exchange Stablecoin Basis

- reason: gross basis is too small versus taker fees.
- evidence:
  - Kraken buy -> Bitso sell: about +3.5 bps gross, about -87.5 bps net.
  - Bitstamp buy -> Bitso sell: about +3.1 bps gross, about -87.9 bps net.
  - Kraken buy -> Bitstamp sell: about +0.3 bps gross, about -80.7 bps net.
- exact failure mode: stablecoin basis exists but not remotely enough for taker execution.
- stop condition: revisit only if gross basis exceeds conservative fee burden plus haircut by a wide margin.

## KILL - Taker USDC/USD Cross-Exchange Stablecoin Basis

- reason: gross basis is too small versus taker fees.
- evidence: Kraken buy -> Bitstamp sell measured about +0.5 bps gross and about -80.5 bps net.
- exact failure mode: normal stablecoin/USD spreads are much tighter than low-tier taker fees.
- stop condition: revisit only during clear stablecoin stress or with maker/rebate economics.

## KILL - Immediate Spot-Perp Funding Capture For 48h Sprint

- reason: funding is positive but too small relative to negative entry basis and conservative round-trip fees.
- evidence:
  - Binance DOGE was one of the better routes: basis -3.717 bps, funding +0.955 bps/8h, breakeven about 11.8 days.
  - Bybit DOGE: basis -1.003 bps, funding +1.000 bps/8h, breakeven about 10.3 days.
  - OKX ETH: basis -5.268 bps, funding +0.691 bps/interval, breakeven about 17.0 days assuming 8h.
- exact failure mode: payback horizon is longer than the challenge window before adding operational and liquidation risk.
- stop condition: promote only when funding spike gives explicit breakeven inside a short holding window after fees.

## KILL - Static Major-Asset Binance.US Maker/Taker Arb

- reason: 0 bps maker fee is not enough when the other leg is taker and the spread is normal.
- evidence:
  - BTC/USDT Binance.US maker sell after buying Binance global taker was about -9.3 bps net.
  - ETH/USDT best measured direction was about -8.6 to -9.7 bps net.
  - SOL/USDT best measured direction was about -9.6 bps net.
  - Kraken routes were around -40 bps because Kraken taker fees dominate.
- exact failure mode: static major-asset spreads are smaller than taker + latency/adverse-selection costs.
- stop condition: only promote Binance.US routes when event-window spread materially exceeds the other venue's taker fee and maker non-fill risk.

## KILL - Current WETH/USDC CEX-DEX Route

- reason: public aggregator quotes were measurable but negative after CEX taker and gas.
- evidence:
  - WETH -> USDC on DEX vs Binance ETHUSDC bid was about -14 to -22 bps net in tested sizes.
  - USDC -> WETH on DEX then Binance sell was about -7.4 to -8.4 bps net for 1,000-10,000 USDC.
- exact failure mode: normal DEX/CEX basis is not enough after CEX fee and gas.
- stop condition: monitor only; execute only if aggregator quote remains positive after gas, CEX fee, slippage, and MEV buffer.

## KILL - HOOLI/USDT KuCoin -> Gate Current Direct Route

- reason: negative after correct Gate fee and live depth.
- evidence: KuCoin buy -> Gate sell measured about +15.0 bps gross but -17.0 bps net at 25 USDT; about -39.1 bps net at 100 USDT.
- exact failure mode: generic scanner understated Gate fee; once Gate's `0.2` fee is used, the route dies.
- stop condition: stop probing Gate routes from generic-fee rankings until Gate pair fee metadata is loaded before ranking.

## KILL - WALLI/USDT KuCoin -> MEXC Current Direct Route

- reason: initial depth-positive spread collapsed during persistence sampling.
- evidence:
  - Initial depth was positive up to 500 USDT, but negative by 1,000 USDT.
  - Persistence window: 50 USDT bucket was only 6/30 positive with avg -68.821 bps; 500 USDT was 0/30 positive with avg -549.741 bps.
- exact failure mode: low-liquidity event window decayed too quickly and did not survive the persistence gate.
- stop condition: no promotion unless small-size buckets stay at least 70% positive with positive median net.

## KILL - DEUS/USDT KuCoin -> MEXC Current Direct Route

- reason: negative after live depth and identity is weak.
- evidence:
  - KuCoin buy -> MEXC sell measured about -117.5 bps net at 50 USDT.
  - MEXC buy -> KuCoin sell measured about -110.4 bps net at 50 USDT.
  - MEXC metadata full name is `XMAQUINA`, not clearly `DEUS`.
- exact failure mode: stale top-of-book candidate plus possible asset identity mismatch.
- stop condition: no promotion without positive depth and verified identity.

## KILL - EUL/USDT Binance <-> KuCoin Current Direct Route

- reason: negative after live depth and fees in both directions.
- evidence:
  - Binance buy -> KuCoin sell measured about -38.7 bps net at 50 USDT and -60.2 bps at 1,000 USDT.
  - KuCoin buy -> Binance sell measured about -32.0 bps net at 50 USDT and -65.9 bps at 1,000 USDT.
- exact failure mode: normal cross-venue spread is smaller than two taker fees plus latency haircut.
- stop condition: revisit only if a fresh event window produces positive depth buckets after costs.

## KILL - GOMINING/USDT Bitget -> MEXC As Execution Priority

- reason: persistent but too small; capacity dies before 500 USDT.
- evidence:
  - 20-sample persistence window had 50/100/250 USDT buckets 20/20 positive, with averages +36.898, +34.570, and +25.229 bps.
  - 500 USDT bucket was 0/20 positive, avg -5.006 bps.
- exact failure mode: small top-of-book pocket without meaningful notional capacity.
- stop condition: keep only as a regression case unless a future scan shows positive median at 500-1,000 USDT or higher.

## KILL - CPOOL/USDT Bybit <-> KuCoin Current Direct Route

- reason: negative after live depth and fees in both directions.
- evidence:
  - Bybit buy -> KuCoin sell measured about -34.4 bps net at 50 USDT and -51.9 bps at 100 USDT.
  - KuCoin buy -> Bybit sell measured about -95.1 bps net at 50 USDT.
- exact failure mode: apparent scan edge did not survive depth and fee modeling.
- stop condition: no promotion without positive depth buckets after venue-specific fee modeling.

## KILL - DAG/USDT MEXC <-> KuCoin Current Direct Route

- reason: deeply negative after live depth; MEXC also reports spot trading not allowed.
- evidence:
  - MEXC metadata returned `isSpotTradingAllowed=false`.
  - MEXC buy -> KuCoin sell measured about -310.0 bps net at 50 USDT.
  - KuCoin buy -> MEXC sell measured about -161.7 bps net at 50 USDT.
- exact failure mode: stale/fake scan edge plus tradability flag risk.
- stop condition: do not revisit unless MEXC tradability is enabled and fresh depth is positive after costs.

## KILL - GUA/USDT MEXC -> Gate Current Direct Route

- reason: sell venue deposits are disabled, so inventory cannot be cleanly pre-positioned or replenished.
- evidence:
  - Gate currency endpoint reports `deposit_disabled=true` on BSC for `GUA`.
  - Depth was positive through 2,500 USDT after fees, but 5,000 USDT was negative.
  - MEXC and Gate contracts match case-insensitively, so identity is not the blocker; deposits are.
- exact failure mode: operational route blocked despite positive public-book spread.
- stop condition: revisit only if Gate deposits reopen and the route survives live depth plus persistence.

## KILL - QAIT/USDT MEXC/KuCoin -> Gate Current Direct Route

- reason: no meaningful depth after fees; practical edge disappears by 500 USDT.
- evidence:
  - MEXC buy -> Gate sell measured about +426.4 bps at 50 USDT and +84.4 bps at 250 USDT, but only about +0.04 bps at 500 USDT and negative by 1,000 USDT.
  - KuCoin buy -> Gate sell was negative even at 50 USDT.
  - Gate and KuCoin withdrawals for QAIT are disabled, adding operational friction.
- exact failure mode: tiny edge pocket plus operational friction.
- stop condition: revisit only if 500-1,000 USDT buckets become materially positive and transfer status is usable.

## KILL - PHB/USDT MEXC -> Gate Current Direct Route

- reason: sell venue deposits are disabled, so inventory cannot be cleanly pre-positioned or replenished.
- evidence:
  - Gate currency endpoint reports `deposit_disabled=true` on BSC for `PHB`.
  - Depth was positive through 1,000 USDT after fees, but 2,500 USDT was negative.
  - MEXC and Gate contracts match case-insensitively, so identity is not the blocker; deposits are.
- exact failure mode: operational route blocked despite positive public-book spread.
- stop condition: revisit only if Gate deposits reopen and the route survives live depth plus persistence.

## KILL - AI/USDT Sleepless AI vs Gensyn Cross-Venue Routes

- reason: `AI` ticker maps to different assets across venues.
- evidence:
  - Gate and Binance identify `AI` as Sleepless AI.
  - MEXC and KuCoin identify `AI` as Gensyn with matching ERC20 contract `0x4d7078ddd6ccfed2f85db5b7d3ff16828d378d48`.
  - OKX current `AI-USDT` should be treated as Gensyn-side unless contract evidence proves otherwise.
- exact failure mode: cross-asset ticker collision; apparent spread is fake.
- stop condition: no route scoring across the Sleepless/Gensyn boundary. Only compare venues proven to list the same `AI` asset.

## KILL - ESPORTS/USDT KuCoin -> Bitget Current Direct Route

- reason: deposit-disabled transfer path makes the visible spread non-repeatable.
- evidence:
  - KuCoin and Bitget both identify `ESPORTS` as `Yooldo Games` on BEP20 contract `0xf39e4b21c84e737df08e2c3b32541d856f508e48`.
  - KuCoin reports BEP20 withdrawals enabled but deposits disabled.
  - Bitget reports BEP20 withdrawals enabled but deposits disabled.
  - KuCoin buy -> Bitget sell measured positive through 5,000 USDT, including about +2,191.3 bps at 500 USDT and +344.7 bps at 5,000 USDT; 10,000 USDT was negative.
  - Bitget buy -> KuCoin sell was negative at every tested bucket.
- exact failure mode: inventory/rebalance cannot be closed through public venue deposit lanes even though identity is clean and the book spread is large.
- stop condition: revisit only if deposits reopen on the required destination venue and the route survives fresh depth plus persistence.

## KILL - BTR/USDT MEXC -> Bitget Current Direct Route

- reason: public contract identity mismatch plus disabled Bitget deposits.
- evidence:
  - MEXC identifies `BTR` as `Bitlayer` with ERC20 contract `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`.
  - Bitget public coin endpoint reports `BTR` ERC20 contract `0x6c76de483f1752ac8473e2b4983a873991e70da7`.
  - Bitget reports withdrawals enabled but deposits disabled.
  - Depth had been positive through 5,000 USDT, but same-symbol depth is invalid after the contract mismatch.
- exact failure mode: same ticker does not prove same asset; sell venue cannot be replenished through public deposit lane anyway.
- stop condition: revisit only if Bitget contract identity is reconciled with MEXC and Bitget deposits reopen.

## KILL - HOOLI/USDT MEXC -> Bitget Current Direct Route

- reason: sell venue deposits are disabled, making the route non-repeatable.
- evidence:
  - MEXC and Bitget both report SOL contract `FPJfY8mMTRwaePD2f46TFLqVov4X9svBaUgR1a8oTwTF`, so identity is clean.
  - Bitget reports withdrawals enabled but deposits disabled.
  - Depth persistence was positive only through 500 USDT; 1,000 USDT was 0/20 positive.
- exact failure mode: tiny inventory-only sell pocket with no clean replenish path.
- stop condition: revisit only if Bitget deposits reopen and live depth supports at least 500-1,000 USDT after fees.

## KILL - SWEAT/USDT MEXC/Bitget -> Gate Current Direct Route

- reason: sell venue deposits are disabled.
- evidence:
  - MEXC and Gate both identify SWEAT as `Sweat Economy` with ERC20 contract `0xB4b9DC1C77bdbb135eA907fd5a08094d98883A35`.
  - Gate reports deposits disabled on ETH and NEAR for `SWEAT`; ETH withdrawals are also disabled.
  - Bitget reports NEAR contract `token.sweat`, withdrawals enabled, deposits disabled.
  - Top-of-book net appeared positive at about +430 bps, but the sell venue deposit lane is blocked.
- exact failure mode: deposit-disabled sell venue creates a fake repeatable arbitrage signal.
- stop condition: revisit only if Gate deposits reopen and the route survives depth plus persistence.

## KILL - SPARKLET/USDT MEXC -> Gate Current Direct Route

- reason: positive depth is too small to survive practical transfer/rebalance overhead.
- evidence:
  - MEXC and Gate contracts match on ERC20 `0x0bc37bea9068a86c221b8bd71ea6228260dad5a2`.
  - Gate deposits and withdrawals are enabled.
  - 20-sample persistence had 250 USDT 20/20 positive avg +73.683 bps and 500 USDT 20/20 positive avg +38.332 bps.
  - 1,000 USDT was 0/20 positive, avg -5.949 bps.
- exact failure mode: technically valid micro-pocket, but not enough net notional after withdrawal/rebalance/inventory costs.
- stop condition: revisit only if 1,000-2,500 USDT buckets become materially positive after fees.

## KILL - SNEK/USDT KuCoin/MEXC -> Bitget/Gate Current Direct Route

- reason: positive depth exists only below meaningful notional and is wiped by transfer/rebalance overhead.
- evidence:
  - KuCoin, MEXC, Gate, and Bitget identity/chain metadata align sufficiently for SNEK/Cardano testing.
  - Best route, KuCoin buy -> Bitget sell, measured +80.387 bps at 50 USDT, +72.161 bps at 100 USDT, and +21.982 bps at 250 USDT.
  - 500 USDT was negative at -25.252 bps.
  - KuCoin withdrawal fee is `2,000` SNEK, larger than the tiny 250 USDT edge.
- exact failure mode: shallow top-of-book pocket with no economic capacity after transfer costs.
- stop condition: revisit only if 500-1,000 USDT buckets become materially positive after fees.

## KILL - COQ/USDT KuCoin -> MEXC/Gate Current Direct Route

- reason: live depth is negative even at small size.
- evidence:
  - KuCoin, MEXC, and Gate identity metadata aligns on AVAX C-Chain contract `0x420FcA0121DC28039145009570975747295f2329`.
  - KuCoin buy -> MEXC sell measured about -122.153 bps at 50 USDT and -152.209 bps at 100 USDT.
  - KuCoin buy -> Gate sell was also negative at every tested bucket.
- exact failure mode: stale/top-of-book signal failed depth.
- stop condition: revisit only if fresh depth is positive at 500+ USDT after fees.

## KILL - VOOI/USDT MEXC/KuCoin/Gate -> Bybit Current Direct Route

- reason: no meaningful notional depth and Bybit network status is not publicly verified.
- evidence:
  - MEXC, KuCoin, Gate, and Bitget expose matching ERC20 contract `0xb31561f0e2aac72406103b1926356d756f07a481` where public metadata is available.
  - Bybit asset/network endpoint is key-gated.
  - Best route, MEXC buy -> Bybit sell, measured +75.311 bps at 50 USDT and +30.578 bps at 100 USDT, but -41.734 bps at 250 USDT.
- exact failure mode: small top-of-book pocket without actionable depth; sell-venue transfer status remains unverified.
- stop condition: revisit only if 500-1,000 USDT buckets become positive and Bybit network/deposit status is verified.

## KILL - RAVE/USDT Bitget -> Gate/KuCoin Current Direct Route

- reason: sell venue deposits are disabled.
- evidence:
  - Bitget, Gate, and KuCoin align on ERC20 contract `0x17205fab260a7a6383a81452ce6315a39370db97`.
  - Gate reports deposits disabled.
  - KuCoin reports deposits disabled on both BEP20 and ERC20.
  - Bitget also reports deposits disabled.
- exact failure mode: huge top-of-book spread is non-repeatable because destination venue deposits are closed.
- stop condition: revisit only if destination deposits reopen and live depth survives.

## KILL - UPC/USDT MEXC -> Bitget Current Direct Route

- reason: Bitget deposits are disabled.
- evidence:
  - MEXC and Bitget contracts match on ERC20 `0x487d62468282bd04ddf976631c23128a425555ee`.
  - Bitget reports withdrawals enabled but deposits disabled.
- exact failure mode: same-asset route cannot replenish sell venue inventory through a public deposit lane.
- stop condition: revisit only if Bitget deposits reopen and live depth survives.

## KILL - RWA/USDT Gate/MEXC -> KuCoin Current Direct Route

- reason: ticker collision.
- evidence:
  - MEXC and Gate identify `RWA` as `Allo` on BSC contract `0x9c8b5ca345247396bdfac0395638ca9045c6586e`.
  - KuCoin identifies `RWA` as `RWA Inc` on Base contract `0xe2b1dc2d4a3b4e59fdf0c47b71a7a86391a8b35a`.
- exact failure mode: same ticker, different asset.
- stop condition: no route scoring across these identities.

## KILL - TOWER/USDT MEXC -> KuCoin Current Direct Route

- reason: contract identity mismatch.
- evidence:
  - MEXC exposes contract `0xf7C1CEfCf7E1dd8161e00099facD3E1Db9e528ee`.
  - KuCoin exposes ERC20 contract `0x1c9922314ed1415c95b9fd453c3818fd41867d0b`.
- exact failure mode: same ticker, different token contract.
- stop condition: revisit only if metadata reconciles to the same contract.

## KILL - ARRR/USDT Gate -> MEXC Current Direct Route

- reason: live depth is too small; route is negative by 100 USDT.
- evidence:
  - Gate and MEXC both identify ARRR as Pirate Chain.
  - Gate buy -> MEXC sell measured +42.654 bps at 50 USDT but -1.100 bps at 100 USDT and worse at larger buckets.
- exact failure mode: tiny top-of-book pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - SWCH/USDT Gate -> MEXC Current Direct Route

- reason: MEXC reports spot trading not allowed.
- evidence:
  - Gate and MEXC contracts match for SwissCheese on Polygon.
  - MEXC `SWCHUSDT` metadata returns `isSpotTradingAllowed=false`.
- exact failure mode: route cannot be executed on the MEXC sell leg despite public ticker signal.
- stop condition: revisit only if MEXC enables spot trading and depth is positive after fees.

## KILL - CWEB/USDT KuCoin -> MEXC Current Direct Route

- reason: practical depth is too small and transfer fee wipes the pocket.
- evidence:
  - KuCoin and MEXC identity matches on ERC20 `0x505b5eda5e25a67e1c24a2bf1a527ed9eb88bf04`.
  - KuCoin buy -> MEXC sell measured +99.862 bps at 50 USDT, +81.814 bps at 100 USDT, +32.442 bps at 250 USDT, and -32.541 bps at 500 USDT.
  - KuCoin withdrawal fee is `1,200` CWEB, larger than the 250 USDT edge.
- exact failure mode: shallow top-of-book pocket with no economic capacity after transfer costs.
- stop condition: revisit only if 500-1,000 USDT buckets become materially positive.

## KILL - GHX/USDT Gate/KuCoin -> MEXC Current Direct Route

- reason: live depth is only positive at tiny size.
- evidence:
  - Gate, KuCoin, and MEXC identity matches on ERC20 `0x728f30fa2f100742c7949d1961804fa8e0b1387d`.
  - Gate buy -> MEXC sell was positive at 50-100 USDT but negative by 250 USDT.
  - KuCoin buy -> MEXC sell was positive at 50-100 USDT, about +0.915 bps at 250 USDT, and negative by 500 USDT.
- exact failure mode: micro top-of-book pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - BBT/USDT MEXC -> Gate Current Direct Route

- reason: MEXC reports spot trading not allowed.
- evidence:
  - MEXC `BBTUSDT` metadata returns `isSpotTradingAllowed=false`.
  - Gate lists BabyBoomToken with matching BSC contract, but MEXC execution is not allowed.
- exact failure mode: route cannot be executed on the MEXC buy leg despite public ticker signal.
- stop condition: revisit only if MEXC enables spot trading and depth is positive after fees.

## KILL - TYCOON/USDT Gate -> MEXC Current Direct Route

- reason: MEXC reports spot trading not allowed.
- evidence:
  - Gate and MEXC contracts match for Dino Tycoon on BSC.
  - MEXC `TYCOONUSDT` metadata returns `isSpotTradingAllowed=false`.
- exact failure mode: route cannot be executed on the MEXC sell leg despite public ticker signal.
- stop condition: revisit only if MEXC enables spot trading and depth is positive after fees.

## KILL - IMT/USDT Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Gate and MEXC identity matches for Immortal Rising 2 on ERC20.
  - Gate buy -> MEXC sell measured about -119.271 bps at 50 USDT and worse at larger buckets.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - SIX/USDT MEXC -> Gate Current Direct Route

- reason: contract identity mismatch.
- evidence:
  - MEXC reports contract `0x070a9867Ea49CE7AFc4505817204860e823489fE`.
  - Gate reports contract `0x61c6ebf443ad613c9648762585b3cfd3ba1f3fa8`.
- exact failure mode: same ticker, different token contract.
- stop condition: revisit only if metadata reconciles to the same contract.

## KILL - REACT/USDT KuCoin -> Gate Current Direct Route

- reason: withdrawal chain mismatch.
- evidence:
  - KuCoin and Gate match on ETH contract `0x817162975186d4d53dbf5a7377dd45376e2d2fc5`.
  - KuCoin ERC20 withdrawals are disabled; only native `react` withdrawals are enabled.
  - Gate supports ETH for REACT.
- exact failure mode: bought KuCoin inventory cannot replenish Gate through the matching public network.
- stop condition: revisit only if KuCoin ERC20 withdrawals reopen or Gate supports the native REACT network.

## KILL - PYBOBO/USDT MEXC -> Bybit Current Direct Route

- reason: live depth is too small.
- evidence:
  - MEXC buy -> Bybit sell measured +46.954 bps at 50 USDT and +35.622 bps at 100 USDT, but -5.160 bps at 250 USDT.
- exact failure mode: tiny top-of-book pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and Bybit network status is verified.

## KILL - WBAI/USDT KuCoin -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - KuCoin and MEXC identity matches on BSC contract `0x635d44f246156ed1080cb470877256c847673f19`.
  - KuCoin buy -> MEXC sell measured about -397.012 bps at 50 USDT and worse at larger buckets.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if fresh depth is positive at 500+ USDT after fees.

## KILL - MAPO/USDT MEXC/KuCoin -> Bitget Current Direct Route

- reason: destination transfer lanes are disabled.
- evidence:
  - Bitget reports MAPO deposits and withdrawals disabled.
  - KuCoin reports MAPO deposits disabled.
- exact failure mode: cannot replenish sell venue or close a repeatable route through public deposit lanes.
- stop condition: revisit only if destination deposits reopen and live depth survives.

## KILL - CTA/USDT Bybit -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Bybit buy -> KuCoin sell measured about -55.773 bps at 50 USDT and worse at larger buckets.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and Bybit transfer status is verified.

## KILL - ALEX/USDT KuCoin -> MEXC Current Direct Route

- reason: live depth is too small.
- evidence:
  - KuCoin and MEXC identity matches on STX token `SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex`.
  - KuCoin buy -> MEXC sell measured +70.420 bps at 50 USDT and +9.502 bps at 100 USDT, but -149.428 bps at 250 USDT.
- exact failure mode: tiny top-of-book pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - DEVVE/USDT Gate -> MEXC Current Direct Route

- reason: live depth is too small.
- evidence:
  - Gate and MEXC identity matches on ERC20 `0x8248270620aa532e4d64316017be5e873e37cc09`.
  - Gate buy -> MEXC sell measured +25.116 bps at 50 USDT but -2.606 bps at 100 USDT and worse at larger buckets.
- exact failure mode: tiny top-of-book pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - EPIC/USDT Gate -> MEXC/Binance Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Gate, MEXC, and Binance identity metadata points to the same EPIC ERC20 contract.
  - Gate -> MEXC measured -84.759 bps at 50 USDT, -95.402 bps at 100 USDT, and -128.681 bps at 250 USDT.
  - Gate -> Binance measured -90.461 bps at 50 USDT, -100.728 bps at 100 USDT, and -131.868 bps at 250 USDT.
- exact failure mode: clean identity did not survive executable depth after fees and latency.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - SXT/USDT Bybit -> MEXC/Binance/KuCoin/Bitget/Gate Current Direct Route

- reason: only a tiny Bybit -> MEXC pocket exists, and all meaningful buckets are negative.
- evidence:
  - MEXC, Binance, KuCoin, and Bitget public metadata aligns on SXT ERC20 contract `0xe6bfd33f52d82ccb5b37e16d3dd81f9ffdabb195`.
  - KuCoin and Bitget ERC20 deposits/withdrawals are enabled; Bybit transfer status was not publicly verified.
  - Bybit -> MEXC measured +42.895 bps at 50 USDT and +42.793 bps at 100 USDT, but -53.151 bps at 250 USDT and -94.948 bps at 500 USDT.
  - Bybit -> Binance, KuCoin, Bitget, and Gate were negative from 50 USDT onward.
- exact failure mode: micro top-of-book pocket without actionable capacity; no persistence sampling warranted.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and Bybit transfer status can be verified.

## KILL - CHIRP/USDT MEXC -> KuCoin Current Direct Route

- reason: positive only at 50 USDT and negative by 100 USDT.
- evidence:
  - Identity matches on SUI contract `0x1ef4c0b20340b8c6a59438204467ca71e1e7cbe918526f9c2c6c5444517cd5ca::chirp::CHIRP`.
  - KuCoin deposits/withdrawals enabled; withdrawal fee 60 CHIRP, minimum 120 CHIRP.
  - MEXC -> KuCoin measured +46.613 bps at 50 USDT, -11.259 bps at 100 USDT, and -103.365 bps at 250 USDT.
- exact failure mode: micro pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - GAMEVIRTUAL/USDT Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Gate and MEXC identity matches on Base contract `0x1c4cca7c5db003824208adda61bd749e55f463a3`.
  - Gate deposits/withdrawals enabled.
  - Gate -> MEXC measured -25.473 bps at 50 USDT, -32.551 bps at 100 USDT, and -45.805 bps at 250 USDT.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - AFC/USDT MEXC -> Bybit Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - MEXC identifies Arsenal Fan Token with contract `0x76088F3eD5dC655De9295D93868ec1EeC654A615`.
  - Bybit `AFCUSDT` spot trading is enabled, but transfer status was not publicly verified.
  - MEXC -> Bybit measured -38.595 bps at 50 USDT, -53.771 bps at 100 USDT, and -76.666 bps at 250 USDT.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and Bybit transfer status is verified.

## KILL - LKI/USDT MEXC -> KuCoin Current Direct Route

- reason: live depth is deeply negative.
- evidence:
  - Identity matches on BEP20 contract `0x1865dc79a9e4b5751531099057d7ee801033d268`.
  - KuCoin deposits/withdrawals enabled; withdrawal fee 1,700 LKI, minimum 3,400 LKI.
  - MEXC -> KuCoin measured -367.978 bps at 50 USDT, -440.512 bps at 100 USDT, and -1101.485 bps at 250 USDT.
- exact failure mode: apparent spread is not executable at depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - LYX/USDT Gate -> KuCoin Current Direct Route

- reason: positive only below 250 USDT.
- evidence:
  - Gate and KuCoin both identify LUKSO on the native LYX/LUKSO lane with deposits/withdrawals enabled.
  - Gate -> KuCoin measured +85.079 bps at 50 USDT and +74.534 bps at 100 USDT, but -47.256 bps at 250 USDT and -151.602 bps at 500 USDT.
- exact failure mode: tiny top-of-book pocket without actionable capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - NOS/USDT Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Gate and MEXC identity matches on Solana address `nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7`.
  - Gate deposits/withdrawals enabled.
  - Gate -> MEXC measured -26.207 bps at 50 USDT, -28.670 bps at 100 USDT, and -31.441 bps at 250 USDT.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ID/USDT MEXC -> Bybit Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - MEXC identifies SPACE ID with contract `0x2dfF88A56767223A5529eA5960Da7A3F5f766406`.
  - Bybit `IDUSDT` spot trading is enabled, but transfer status was not publicly verified.
  - MEXC -> Bybit measured -41.238 bps at 50 USDT, -50.749 bps at 100 USDT, and -70.661 bps at 250 USDT.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and Bybit transfer status is verified.

## KILL - SOUL/USDT Gate -> KuCoin Current Direct Route

- reason: live depth is negative and chain labels are ambiguous.
- evidence:
  - Both venues name Phantasma/SOUL, but Gate reports chain `KCALP` while KuCoin reports `PHANTASMA`.
  - Gate and KuCoin deposits/withdrawals are enabled on public endpoints.
  - Gate -> KuCoin measured -14.308 bps at 50 USDT, -76.727 bps at 100 USDT, and -145.485 bps at 250 USDT.
- exact failure mode: top-of-book signal failed live depth before chain ambiguity mattered.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and chain compatibility is proven.

## KILL - RIO/USDT KuCoin -> MEXC Current Direct Route

- reason: positive only below 250 USDT and identity is not clean.
- evidence:
  - KuCoin reports Realio Network on BEP20 contract `0x94a8b4ee5cd64c79d0ee816f467ea73009f51aa0`.
  - MEXC reports `Realio` with contract/address field `2751733`.
  - KuCoin -> MEXC measured +41.221 bps at 50 USDT and +30.083 bps at 100 USDT, but -5.050 bps at 250 USDT and -58.774 bps at 500 USDT.
- exact failure mode: micro pocket without actionable capacity; transfer identity is ambiguous.
- stop condition: revisit only if identity is reconciled and 500+ USDT buckets become positive after fees.

## KILL - DMTR/USDT MEXC -> KuCoin Current Direct Route

- reason: positive pocket is too small and transfer fee wipes it.
- evidence:
  - Identity matches on ERC20 contract `0x51cb253744189f11241becb29bedd3f1b5384fdb`.
  - KuCoin withdrawals are enabled with 170 DMTR fee and 340 DMTR minimum.
  - MEXC -> KuCoin measured +35.714 bps at 250 USDT and +13.262 bps at 500 USDT, then -14.643 bps at 1,000 USDT.
- exact failure mode: positive edge exists only below meaningful size and does not survive withdrawal overhead.
- stop condition: revisit only if 1,000+ USDT buckets become positive after fees and transfer overhead.

## KILL - WARD/USDT Bitget/MEXC/KuCoin -> Gate Current Direct Route

- reason: transfer identity mismatch.
- evidence:
  - Gate exposes WARD on BSC contract `0x6dc200b21894af4660b549b678ea8df22bf7cfac`.
  - KuCoin and Bitget expose native Warden, and MEXC reports no contract field.
- exact failure mode: no proven repeatable transfer lane into the Gate sell venue.
- stop condition: revisit only if chain/bridge compatibility is proven and depth survives.

## KILL - INSP/USDT MEXC -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Identity matches on ERC20 contract `0x186ef81fd8e77eec8bffc3039e7ec41d5fc0b457`.
  - MEXC -> KuCoin measured -93.174 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - TX/USDT Gate -> Bitget Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Public metadata is compatible-looking on native TX for the route direction.
  - Gate -> Bitget measured -11.922 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - SIN/USDT KuCoin -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - Identity matches on BEP20 contract `0x6397de0f9aedc0f7a8fa8b438dde883b9c201010`.
  - KuCoin -> MEXC measured -58.243 bps at 50 USDT and much worse beyond.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - STAY/USDT MEXC -> KuCoin Current Direct Route

- reason: positive only at 50 USDT and transfer fee wipes it.
- evidence:
  - Identity matches on BEP20 contract `0x30c0ef9361645ec56a7e640cd05ce6abdfce8422`.
  - KuCoin withdrawals are enabled with 14,000 STAY fee and 28,000 STAY minimum.
  - MEXC -> KuCoin measured +24.016 bps at 50 USDT but -12.943 bps at 100 USDT.
- exact failure mode: microscopic top-of-book pocket below actionable size.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and transfer overhead.

## KILL - ASSET/USDT KuCoin -> MEXC Current Direct Route

- reason: positive pocket dies before 500 USDT and transfer fee consumes most edge.
- evidence:
  - Identity matches on ERC20 contract `0x99e980265bf36516c442be982df1772a6ccb3233`.
  - KuCoin withdrawals are enabled with 8 ASSET fee and 16 ASSET minimum.
  - KuCoin -> MEXC measured +74.015 bps at 250 USDT but -24.887 bps at 500 USDT.
- exact failure mode: sub-actionable capacity and fee drag.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and transfer overhead.

## KILL - PIN/USDT MEXC -> Gate Current Direct Route

- reason: MEXC spot trading is not allowed.
- evidence:
  - MEXC and Gate identity matches on ERC20 contract `0x2e44f3f609ff5aa4819b323fd74690f07c3607c4`.
  - MEXC `PINUSDT` reports `isSpotTradingAllowed=false`.
- exact failure mode: disabled buy leg.
- stop condition: revisit only if MEXC enables spot trading and depth is positive after fees.

## KILL - GAIB/USDT Bybit -> MEXC Current Direct Route

- reason: positive only below 250 USDT and edge is too small.
- evidence:
  - Bybit spot trading is enabled; MEXC reports GAIB contract `0xC19D38925F9F645337B1D1f37bAf3C0647A48E50`.
  - Bybit -> MEXC measured +6.180 bps at 50 USDT, +0.835 bps at 100 USDT, and -32.099 bps at 250 USDT.
- exact failure mode: microscopic top-of-book pocket without capacity; Bybit transfer status was not worth chasing.
- stop condition: revisit only if 500+ USDT buckets become positive after fees and transfer status is verified.

## KILL - HEART/USDT KuCoin -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: KuCoin -> MEXC measured -61.743 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - BNKR/USDT KuCoin/Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - KuCoin -> MEXC measured -21.546 bps at 50 USDT and worse.
  - Gate -> MEXC measured -5.769 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ESE/USDT MEXC -> Bybit/KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence:
  - MEXC -> Bybit measured -51.950 bps at 50 USDT and worse.
  - MEXC -> KuCoin measured -44.139 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - RVV/USDT Bitget -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Bitget -> MEXC measured -93.739 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - HEI/USDT Binance -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Binance -> MEXC measured -58.784 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ROOBEE/USDT Gate -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Gate -> KuCoin measured -12.568 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - LAVA/USDT Bybit -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Bybit -> MEXC measured -16.877 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - RMV/USDT MEXC -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: MEXC -> KuCoin measured -60.613 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - XELS/USDT Gate -> MEXC Current Direct Route

- reason: positive only below 250 USDT.
- evidence: Gate -> MEXC measured +41.341 bps at 50 USDT and +22.754 bps at 100 USDT, but -17.004 bps at 250 USDT.
- exact failure mode: micro top-of-book pocket without capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - IOTX/USDT MEXC/Binance -> Gate Current Direct Route

- reason: positive only below 250 USDT.
- evidence:
  - MEXC -> Gate measured +53.357 bps at 50 USDT and +51.726 bps at 100 USDT, but -21.289 bps at 250 USDT.
  - Binance -> Gate measured +50.761 bps at 50 USDT and +49.131 bps at 100 USDT, but -15.490 bps at 250 USDT.
- exact failure mode: micro top-of-book pocket without capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - HAI/USDT KuCoin -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: KuCoin -> MEXC measured -13.334 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - LL/USDT MEXC -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: MEXC -> KuCoin measured -70.149 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - MCRT/USDT Bybit -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Bybit -> MEXC measured -77.408 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - MSFTON/USDT MEXC -> Bitget Current Direct Route

- reason: edge is too small for ERC20 transfer/rebalance costs and dies by 5,000 USDT.
- evidence:
  - MEXC and Bitget identity matches on ERC20 contract `0xb812837b81a3a6b81d7cd74cfb19a7f2784555e5`.
  - Bitget deposits/withdrawals enabled; MEXC withdrawal status/fee not publicly verified.
  - MEXC -> Bitget measured +14.885 bps at 1,000 USDT, +0.290 bps at 2,500 USDT, and -55.853 bps at 5,000 USDT.
- exact failure mode: thin tokenized-stock basis cannot survive transfer/rebalance overhead.
- stop condition: revisit only if 5,000+ USDT buckets become meaningfully positive after fees and MEXC withdrawal cost/status is verified.

## KILL - GXE/USDT Gate -> MEXC Current Direct Route

- reason: live depth is deeply negative.
- evidence: Gate -> MEXC measured -695.109 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - IAUON/USDT MEXC -> Gate Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: MEXC -> Gate measured -14.321 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ZENT/USDT Bybit -> OKX Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Bybit -> OKX measured -45.187 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - HMSTR/USDT Bitget -> Binance Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Bitget -> Binance measured -11.695 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - SWFTC/USDT MEXC -> OKX Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: MEXC -> OKX measured -144.766 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ERG/USDT Gate -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Gate -> KuCoin measured -57.741 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - BOS/USDT KuCoin -> MEXC Current Direct Route

- reason: positive only at 50 USDT and KuCoin withdrawal fee makes the pocket irrelevant.
- evidence:
  - KuCoin and MEXC both identify BitcoinOS on ERC20 contract `0x13239c268beddd88ad0cb02050d3ff6a9d00de6d`.
  - KuCoin withdrawals are enabled with 2,500 BOS fee and 5,000 BOS minimum.
  - KuCoin -> MEXC measured +82.508 bps at 50 USDT, -20.759 bps at 100 USDT, and -541.567 bps at 250 USDT.
- exact failure mode: sub-actionable top-of-book pocket plus transfer-fee drag.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - EGL1/USDT KuCoin -> Bitget/Gate Current Direct Route

- reason: positive only at 50 USDT and negative by 100-250 USDT.
- evidence:
  - KuCoin -> Bitget measured +11.796 bps at 50 USDT, -6.711 bps at 100 USDT, and -67.337 bps at 250 USDT.
  - KuCoin -> Gate measured +6.456 bps at 50 USDT, -19.056 bps at 100 USDT, and -99.017 bps at 250 USDT.
- exact failure mode: micro top-of-book pocket without capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - GROK/USDT Gate -> MEXC Current Direct Route

- reason: positive only below 250 USDT.
- evidence: Gate -> MEXC measured +53.697 bps at 50 USDT and +48.305 bps at 100 USDT, but -39.564 bps at 250 USDT.
- exact failure mode: micro top-of-book pocket without capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ETN/USDT MEXC -> KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: MEXC -> KuCoin measured -56.036 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - QKC/USDT Binance/Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT on both buy venues.
- evidence:
  - Binance -> MEXC measured -94.098 bps at 50 USDT and -103.037 bps at 100 USDT.
  - Gate -> MEXC measured -181.385 bps at 50 USDT and -192.843 bps at 100 USDT.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - UNION/USDT MEXC -> Gate Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: MEXC -> Gate measured -54.049 bps at 50 USDT and -82.252 bps at 100 USDT.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - JASMY/USDT Binance/Bitget/Bybit/Crypto.com -> MEXC Current Direct Route

- reason: initial positive snapshot did not persist; current books are negative before withdrawal fees.
- evidence:
  - Initial batch had Binance -> MEXC positive through 10,000 USDT, Bitget -> MEXC positive through 5,000 USDT, and Bybit -> MEXC barely positive through 5,000 USDT.
  - MEXC identifies JASMY on ETH/ERC20 contract `0x7420B4b9a0110cdC71fB720908340C03F9Bc03EC`; Bitget reports the same contract and enabled deposits/withdrawals with 129.87013 JASMY withdrawal fee.
  - 20-sample retest from 2026-05-29 06:41:16 to 06:45:00 CST had zero endpoint errors and 0/20 positive on every tested route/size.
  - Binance -> MEXC averaged -40.157 bps at 1,000 USDT and -55.418 bps at 10,000 USDT.
  - Bitget -> MEXC averaged -42.384 bps at 1,000 USDT and -73.319 bps at 10,000 USDT before withdrawal fee; after Bitget withdrawal fee it averaged -49.418 bps at 1,000 and -74.022 bps at 10,000.
  - Bybit -> MEXC averaged -44.426 bps at 1,000 USDT and -86.021 bps at 10,000 USDT.
- exact failure mode: stale/short-lived book state; no current executable edge.
- stop condition: revisit only if a fresh persistence window shows 20/20 positive at 5,000+ USDT after transfer fees.

## KILL - NYM/USDT Bitget -> Bybit Current Direct Route

- reason: positive only below 250 USDT.
- evidence: Bitget -> Bybit measured +31.969 bps at 50 USDT and +14.428 bps at 100 USDT, but -1.333 bps at 250 USDT.
- exact failure mode: micro top-of-book pocket without capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - POKT/USDT Gate -> KuCoin Current Direct Route

- reason: live depth is deeply negative.
- evidence: Gate -> KuCoin measured -430.804 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed live depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - Immediate Spot-Perp Funding Capture Refresh

- reason: one-period funding/basis proxies are still negative after fees, and operational complexity is much higher than the VANRY spot route.
- evidence:
  - 2026-05-29 06:56 CST refresh scanned 47 public spot/perp proxies across Binance USD-M, Bybit linear, OKX swaps, and Coinbase International with zero endpoint errors.
  - Best Coinbase INTX one-hour proxies were still negative: BTC -7.336 bps, DOGE -7.782 bps, ETH -9.216 bps, SOL -9.463 bps.
  - Best USDT negative-funding route was TRX, still negative: Binance -10.180 bps, Bybit -10.515 bps, OKX -12.073 bps.
- exact failure mode: funding magnitude and entry basis do not cover spot/perp open-close fees in a short holding window.
- stop condition: revisit only if a route shows a positive one-period proxy after conservative fees or a clear multi-period breakeven inside a short, explicit holding window.

## KILL - Bitso Same-Venue MXN/USD/Stables Refresh

- reason: current same-venue stablecoin/FX triangles remain negative after conservative Bitso taker fees.
- evidence:
  - 2026-05-29 06:59 CST refresh queried `usd_mxn`, `usdt_mxn`, `usd_usdt`, `pyusd_mxn`, `rlusd_mxn`, and `tusd_mxn` with zero endpoint errors.
  - Best stablecoin-vs-USD/MXN comparison was PYUSD/MXN sell bid vs USD/MXN ask at -60.914 bps after two fees.
  - Main triangles were negative: MXN -> USD -> USDT -> MXN at -149.901 bps; MXN -> USDT -> USD -> MXN at -151.290 bps.
- exact failure mode: Bitso spreads and taker fees consume the apparent FX/stablecoin basis.
- stop condition: revisit only if gross dislocation exceeds conservative fees by a wide margin, preferably 150+ bps before any operational work.

## KILL - ACA/USDT Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT.
- evidence: Gate -> MEXC measured -81.599 bps at 50 USDT, -106.138 bps at 100 USDT, and -137.052 bps at 250 USDT.
- exact failure mode: stale ticker/top-of-book signal failed executable depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - ES/USDT Gate -> KuCoin/MEXC Current Direct Route

- reason: only Gate -> KuCoin has a small positive pocket, and it dies by 500 USDT.
- evidence:
  - Gate -> KuCoin measured +30.512 bps at 50 USDT, +17.567 bps at 100 USDT, +6.684 bps at 250 USDT, and -6.480 bps at 500 USDT.
  - Gate -> MEXC measured -6.296 bps at 50 USDT and worse.
- exact failure mode: micro top-of-book pocket without capacity.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - IN/USDT MEXC -> Bitget/KuCoin Current Direct Route

- reason: live depth is negative even at 50 USDT on both sell venues.
- evidence:
  - MEXC -> Bitget measured -13.249 bps at 50 USDT and worse.
  - MEXC -> KuCoin measured -2.014 bps at 50 USDT and worse.
- exact failure mode: top-of-book signal failed executable depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - OBOL/USDT Gate -> MEXC Current Direct Route

- reason: live depth is negative even at 50 USDT and sell depth exhausts at larger buckets.
- evidence: Gate -> MEXC measured -28.665 bps at 50 USDT, -66.967 bps at 100 USDT, -146.257 bps at 250 USDT, and sell depth exhausted by 2,500 USDT.
- exact failure mode: top-of-book signal failed executable depth.
- stop condition: revisit only if 500+ USDT buckets become positive after fees.

## KILL - SBUXON/USDT Gate -> MEXC Current Direct Route

- reason: tokenized-stock pocket is tiny and dies by 500 USDT.
- evidence: Gate -> MEXC measured +15.004 bps at 50-250 USDT, -4.230 bps at 500 USDT, and -36.209 bps at 1,000 USDT.
- exact failure mode: sub-actionable capacity; tokenized-stock transfer/rebalance overhead would dominate.
- stop condition: revisit only if 1,000+ USDT buckets become meaningfully positive after fees and transfer/rebalance status is verified.

## KILL - AI/USDT Gate -> KuCoin/MEXC Same-Ticker Collision

- reason: same ticker maps to different assets; apparent spread is not executable arbitrage.
- evidence:
  - Gate `AI` metadata identifies Sleepless AI on BSC contract `0xBDA011D7F8EC00F66C1923B049B94c67d148d8b2`, with deposits and withdrawals enabled.
  - KuCoin `AI` metadata identifies Gensyn on ERC20 contract `0x4d7078ddd6ccfed2f85db5b7d3ff16828d378d48`, with deposits and withdrawals enabled.
  - MEXC `AIUSDT` metadata identifies Gensyn with the same ERC20 contract `0x4d7078DDd6cCFED2F85dB5B7D3Ff16828d378d48`.
  - Depth still looked strongly positive through 5,000 USDT, but only because the buy leg and sell legs were different assets.
- exact failure mode: same-symbol collision between Sleepless AI and Gensyn.
- stop condition: never revisit Gate `AI` -> KuCoin/MEXC `AI` unless venue metadata proves all legs share the same contract and chain.

## KILL - Deposit-Enabled 08:29 Long-Tail Rows Failed Depth

- reason: rows with public deposit-enabled sell venues still failed live executable depth before reaching actionable size.
- evidence:
  - ALEX KuCoin -> Gate measured +39.357 bps at 50 USDT, -111.608 bps at 100 USDT, and -339.981 bps at 250 USDT.
  - PUSH MEXC -> KuCoin measured +85.498 bps at 50 USDT, +40.074 bps at 100 USDT, and -14.456 bps at 250 USDT.
  - SAMO MEXC -> Gate measured -595.703 bps at 50 USDT and worse.
  - SNEK MEXC -> Bitget measured +77.946 bps at 50 USDT, +51.783 bps at 100 USDT, +22.013 bps at 250 USDT, and -9.314 bps at 500 USDT.
  - SNEK Gate -> Bitget measured +84.522 bps at 50 USDT, +42.965 bps at 100 USDT, and -41.524 bps at 250 USDT.
  - OGPU MEXC -> Gate measured -69.934 bps at 50 USDT and worse.
  - REACT KuCoin -> Gate measured +99.878 bps at 50 USDT, +68.902 bps at 100 USDT, and -7.317 bps at 250 USDT.
  - AFC MEXC -> Bitget measured -4.707 bps at 50 USDT and worse.
  - ROUTE KuCoin -> Gate measured -295.323 bps at 50 USDT and worse.
- exact failure mode: public deposit status was not enough; executable depth collapsed by 250-500 USDT or was negative immediately.
- stop condition: revisit only if a fresh depth pass shows 500+ USDT positive after venue fees and transfer haircuts.

## KILL - Fresh 08:39 Processed-Base Exclusion Cluster

- reason: fresh filtered top-of-book positives failed optimistic live depth before transfer fees.
- evidence:
  - The 08:39 processed-base exclusion scan covered 10,213 public markets with zero endpoint errors and found 58 filtered rows after excluding already processed bases.
  - `SHR` KuCoin -> MEXC measured -11.371 bps at 50 USDT and worse.
  - `LKI` KuCoin -> MEXC measured -513.408 bps at 50 USDT and worse.
  - `BNKR` Gate -> MEXC measured +198.980 bps at 50 USDT, +77.996 bps at 500 USDT, and -9.392 bps at 1,000 USDT.
  - `BNKR` KuCoin -> MEXC measured +202.815 bps at 50-250 USDT, +78.430 bps at 500 USDT, and -10.959 bps at 1,000 USDT.
  - `GHX` KuCoin/Gate -> MEXC was negative by 250 USDT.
  - `CWEB` KuCoin -> MEXC was negative by 500 USDT.
  - `WOJAK` MEXC -> Gate measured -115.496 bps at 50 USDT and worse.
  - `PYBOBO` MEXC -> Bybit was negative by 250 USDT; `KEKIUS`, `DEVVE`, and `ASSET` failed by 100-1,000 USDT.
- exact failure mode: top-of-book-only long-tail spreads with no actionable depth.
- stop condition: revisit only if a fresh pass shows 1,000+ USDT positive after venue fees and transfer haircuts.

## KILL - 08:41 Event-Window Persistent Rows Except SPX

- reason: repeated top-of-book persistence did not survive live depth at actionable size, except for SPX which remains a separate `MEASURE` watch.
- evidence:
  - The 08:41-08:44 event-window sampler ran 8 repeated public samples across the main venues with zero endpoint errors.
  - `TYCOON` Gate -> MEXC appeared in 8/8 samples with median top-of-book net +248.570 bps, but live depth was negative from 50 USDT (-206.686 bps).
  - `NOS` Gate -> MEXC appeared in 8/8 samples and live depth was positive through 1,000 USDT (+12.984 bps) but negative by 2,500 USDT before transfer fees.
  - `VOOI` KuCoin/MEXC/Bitget -> Bybit appeared in 8/8 samples but was negative by 250-1,000 USDT depending on buy venue.
  - `SMURFCAT`, `SIX`, `ATR`, `MAPO`, `GAIB`, `BXN`, `XELS`, `WMTX`, `RMV`, and `WARD` failed live depth by 50-1,000 USDT.
  - `IDEX` had a large late top-of-book print, but live depth was negative from 50 USDT.
- exact failure mode: persistent top-of-book spread without executable depth after consuming the book.
- stop condition: revisit only if a fresh persistence window plus depth pass shows 2,500+ USDT positive after fees and transfer haircuts.

## KILL - Binance.US Same-Venue Triangular Taker Scan

- reason: every USD/USDT/USDC-starting 3-leg cycle was negative after the low Binance.US taker-fee assumption.
- evidence:
  - 2026-05-29 08:56 CST scan used Binance.US `exchangeInfo` and `ticker/bookTicker`.
  - Scope: 261 tradable symbols, 264 3-leg cycles starting in USD, USDT, or USDC.
  - Fee model: 2 bps taker per leg from the prior official fee check.
  - Best cycle was USDT -> USD -> USDC -> USDT at -6.710 bps.
  - Best ETH/USD/USDT bridge was -7.185 bps; best USD -> USDT -> BTC -> USD was -7.553 bps.
- exact failure mode: same-venue taker fees and spreads exceed any top-of-book triangular dislocation.
- stop condition: revisit only for maker/rebate queue modeling or if a fresh top-of-book scan shows positive net after taker fees.

## KILL - MEXC Same-Venue Triangular Taker Scan

- reason: headline-positive cycles were dust-constrained and non-dust cycles were negative after fees.
- evidence:
  - 2026-05-29 08:57 CST scan used MEXC `exchangeInfo` and `ticker/bookTicker`.
  - Scope: 2,323 tradable symbols, 1,810 3-leg cycles starting in USDT, USDC, BTC, or ETH.
  - Three cycles were top-of-book positive: USDT -> USD1 -> AWF -> USDT at +26.767 bps, USDT -> EUR -> ADA -> USDT at +6.204 bps, and USDC -> EUR -> ADA -> USDC at +5.913 bps.
  - AWF cycle was capped by 0.01 AWF on the sell leg.
  - ADA/EUR cycles were capped by roughly 0.006 EUR on the ADAEUR ask.
  - Best non-dust stable/EUR loops were already negative; USDT -> EUR -> USDC -> USDT was -0.284 bps.
- exact failure mode: dust top-of-book trap, not executable triangular profit.
- stop condition: revisit only if capacity-aware triangle scan shows positive net at meaningful starting notional after all three legs.

## KILL - KuCoin Same-Venue Triangular Taker Scan

- reason: every USDT/USDC/BTC/ETH-starting 3-leg cycle was negative after the standard KuCoin taker-fee assumption.
- evidence:
  - 2026-05-29 08:58 CST scan used KuCoin `api/v2/symbols` and `api/v1/market/allTickers`.
  - Scope: 1,082 tradable symbols, 982 3-leg cycles starting in USDT, USDC, BTC, or ETH.
  - Fee model: 10 bps taker per leg.
  - Positive cycles: 0.
  - Best cycle was USDT -> VSYS -> BTC -> USDT at -6.389 bps.
  - Best USDC/ETH/TEL cycle was -16.413 bps.
- exact failure mode: same-venue taker fees and spreads exceed any top-of-book triangular dislocation.
- stop condition: revisit only for maker/rebate queue modeling or if a fresh top-of-book scan shows positive net after taker fees.

## KILL - Gate Same-Venue Triangular Taker Scan

- reason: corrected top-of-book positives did not survive executable order-book depth even at 10 USDT.
- evidence:
  - 2026-05-29 09:00-09:04 CST scan used Gate `spot/currency_pairs`, `spot/tickers`, and `spot/order_book`.
  - Scope: 2,206 tradable symbols and 710 3-leg cycles starting in USDT, USDC, BTC, or ETH.
  - Corrected all-symbol scan converted Gate `fee` from percent to fraction and found 10 positive top-of-book cycles.
  - Top headline rows were USDT -> ETH -> GALA -> USDT +230.696 bps, USDC -> ETH -> GALA -> USDC +213.410 bps, USDT -> LIKE -> ETH -> USDT +22.791 bps, USDT -> XRD -> ETH -> USDT +12.137 bps, and USDT -> USDC -> REZ -> USDT +4.027 bps.
  - Follow-up executable-book depth with conservative 20 bps per leg returned GALA USDT -130.644 bps at 10 USDT, GALA USDC -160.048 bps at 10 USDC, LIKE -244.170 bps at 10 USDT, XRD -123.478 bps at 10 USDT, and REZ -134.798 bps at 10 USDT.
  - A second immediate 10-USDT spot recheck also showed every route negative.
- exact failure mode: headline top-of-book triangle signal is not executable under book-walk sizing.
- stop condition: revisit only if a capacity-aware Gate triangle scan shows positive net at meaningful starting notional after all three taker legs.

## KILL - Hyperliquid Same-Venue Spot/Perp Taker Funding

- reason: clean same-asset spot/perp pairs did not cover Hyperliquid tier-0 taker round-trip fees in a one-hour funding window.
- evidence:
  - 2026-05-29 09:08 CST scan used Hyperliquid public `metaAndAssetCtxs`, `spotMetaAndAssetCtxs`, and `l2Book`.
  - Fee model: official tier-0 7.0 bps spot taker and 4.5 bps perps taker, modeled on entry and exit for 23.0 bps round-trip.
  - Scope: 19 raw common spot/perp candidates; 12 sane same-asset pairs after rejecting spot/perp mids more than 200 bps apart.
  - Best clean one-hour proxy was ETH at -10.934 bps after fees; BTC was -15.658 bps, SOL -16.395 bps, wrapped PUMP -18.746 bps, and HYPE -29.235 bps.
  - Rejected false positives included BERA, raw PUMP, raw MON, and TRUMP because spot mids were thousands of bps away from perp mids or had trivial top-level notional.
- exact failure mode: hourly funding plus entry basis does not overcome spot/perp taker fees; raw positives were remapped/stale token traps.
- stop condition: revisit only if a persistence scan shows positive multi-hour carry after conservative exit-basis assumptions, or if account-specific maker/post-only fees and fill evidence materially reduce the round-trip fee burden.

## KILL - HTX Expansion Long-Tail Cluster Except ULTIMA Pre-Positioned Watch

- reason: most HTX-involved headline routes failed depth, transfer status, or chain compatibility before becoming repeatable execution candidates.
- evidence:
  - 2026-05-29 09:11-09:15 CST scan added 615 HTX online/tradable quote-lane markets to the public venue set, covering 10,819 total markets.
  - ULTIMA HTX -> KuCoin persisted strongly through 5,000 USDT, but repeatable transfer is blocked by unresolved chain compatibility: HTX exposes `ultima1`/native ULTIMA with no contract, while KuCoin exposes BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
  - ZEC HTX -> OKX was positive through 10,000 USDT before transfer (+106.560 bps), but HTX public metadata shows ZEC withdrawals `prohibited`.
  - SWEAT HTX -> Bitget was positive through 1,000 USDT, but Bitget public metadata shows SWEAT deposits disabled.
  - ONE, MTL, ICX, CARV, CETUS, and RONIN routes had positive depth pockets, but HTX public currency metadata shows withdrawals prohibited for the relevant assets.
  - US, ZK, WALLI, RONIN, and KAS either failed by 500-1,000 USDT, had prohibited transfer status, or both.
- exact failure mode: strong top-of-book or depth edge without a verified repeatable transfer path.
- stop condition: revisit only if public or logged-in metadata proves compatible deposit/withdraw paths and a fresh 5,000+ USDT persistence window stays positive after fees and transfer haircuts.

## KILL - BitMart Expansion Routes

- reason: BitMart surfaced strong-looking long-tail rows, but depth and transfer metadata killed immediate repeatable execution.
- evidence:
  - 2026-05-29 09:18-09:20 CST scan parsed 1,107 BitMart ticker markets and 11,229 total public markets after adding BitMart to the non-Bitso venue set.
  - A metadata-backed BitMart request returned a transient `502 Bad Gateway`; a lighter ticker parser succeeded.
  - ULTIMA BitMart -> KuCoin was positive through 2,500 USDT before transfer (+553.614 bps) but negative by 5,000 USDT and chain-blocked: BitMart exposes SMART ULTIMA contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`, while KuCoin exposes BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
  - QAIT KuCoin -> BitMart was positive through 500 USDT but negative by 1,000 USDT; QAIT MEXC -> BitMart was only +5.387 bps at 500 and negative by 1,000.
  - BTR BitMart -> Bitget was positive through 1,000 USDT, but BitMart withdraws BTR on `BTR-BTC` contract `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`, while Bitget exposes ERC20 contract `0x6c76de483f1752ac8473e2b4983a873991e70da7` and deposits are disabled.
- exact failure mode: ULTIMA chain split, QAIT insufficient depth, and BTR chain/deposit mismatch.
- stop condition: revisit only if BitMart shows 5,000+ USDT positive depth on a route with matching enabled deposit/withdraw chains.

## KILL - SPX Current Event-Window Route

- reason: the prior SPX event-window edge disappeared in the 09:25 CST watch refresh.
- evidence:
  - 12 public-book samples with six-second spacing across Bybit, MEXC, and KuCoin.
  - SPX Bybit -> KuCoin 5,000 USDT, before unknown Bybit transfer fee, was 0/12 positive, avg -35.773 bps, min -42.156.
  - SPX MEXC -> KuCoin 1,000 USDT, after 3 SPX MEXC withdrawal fee, was 0/12 positive, avg -38.325 bps, min -45.293.
  - SPX MEXC -> KuCoin 2,500 USDT, after 3 SPX MEXC withdrawal fee, was 0/12 positive, avg -44.030 bps, min -52.269.
- exact failure mode: event-window spread closed; current executable depth is negative after fees.
- stop condition: revisit only if a fresh event-window sampler shows persistent positive depth again, at minimum 1,000 USDT after fees and transfer haircuts.

## KILL - ULTIMA Direct SMART/Native to KuCoin BEP20 Transfer Assumption

- reason: public and official sources do not prove that SMART/native ULTIMA buy venues can directly withdraw into KuCoin's BEP20 ULTIMA deposit path.
- evidence:
  - BitMart official ULTIMA listing classifies token type as `SMART` and links SMART contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.
  - BitMart public currency API exposes `ULTIMA-SMART` as enabled and `ULTIMA-ULTIMA` withdrawals disabled.
  - KuCoin official listing states ULTIMA deposits use `BSC-BEP20`.
  - KuCoin public currency API exposes only BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
  - No official/public bridge proof was found in the quick source pass.
- exact failure mode: persistent price premium appears to be across ULTIMA representations, not a proven direct transfer arbitrage.
- stop condition: revisit only with logged-in withdrawal UI/API proof of BEP20 withdrawal from the buy venue or official bridge documentation with measurable fee, latency, and minimum/maximum limits.

## KILL - GUA MEXC -> Gate Repeatable Transfer

- reason: the book edge survived depth through 2,500 USDT, but Gate public metadata has GUA deposits disabled.
- evidence:
  - 2026-05-29 09:31-09:38 CST expanded event-window pass found GUA MEXC -> Gate persistent in 6/6 top-of-book samples.
  - Executable depth before transfer costs was +780.754 bps at 50 USDT, +604.611 at 500, +500.314 at 1,000, +209.824 at 2,500, and -29.459 at 5,000.
  - Gate public `GUA` currency metadata shows BSC contract `0xa5c8e1513b6a08334b479fe4d71f1253259469be`, withdrawals enabled, deposits disabled.
- exact failure mode: profitable sell venue cannot receive replenishment deposits, so direct repeatable MEXC -> Gate transfer arbitrage is blocked.
- stop condition: revisit only if Gate GUA deposits reopen and a fresh persistence/depth pass stays positive through at least 2,500 USDT after fees and any MEXC withdrawal haircut.

## KILL - ORDI HTX -> Bitget/Bybit Event-Window Route

- reason: ORDI survived depth only through 1,000 USDT before transfer, and HTX's fixed BRC20 withdrawal fee is larger than the measured edge.
- evidence:
  - ORDI HTX -> Bybit depth before transfer was +151.835 bps at 50 USDT, +144.838 at 500, +140.902 at 1,000, and -35.586 at 2,500.
  - ORDI HTX -> Bitget depth before transfer was +145.874 bps through 500 USDT, +143.342 at 1,000, and -31.037 at 2,500.
  - HTX public metadata shows ORDI BRC20 deposits/withdrawals allowed with fixed withdrawal fee `5.004459` ORDI.
  - HTX ORDI was around 3.39 USDT during the check, making the HTX withdrawal fee roughly 170 bps on a 1,000 USDT transfer before destination costs or latency.
  - Bitget public metadata shows ORDI BRC20 deposits enabled, but that does not rescue the route after HTX fee drag. Bybit asset metadata was API-key-gated in this environment.
- exact failure mode: fixed withdrawal fee wipes the only positive depth bucket; larger buckets are already negative before transfer.
- stop condition: revisit only if HTX ORDI withdrawal fee materially drops or a fresh depth pass shows at least 2,500 USDT positive after the actual withdrawal fee.

## KILL - Expanded HTX Event-Window Micro Cluster

- reason: persistent HTX top-of-book rows collapsed under executable depth before transfer.
- evidence:
  - RACA HTX -> BitMart was +382.649 bps at 50-100 USDT but -166.914 at 500 and -425.976 at 1,000.
  - TST HTX -> Binance was +255.980 bps at 100 but only +4.758 at 250 and -197.422 at 500; TST HTX -> BitMart was negative by 250.
  - BLAST HTX -> Bybit was +71.640 bps at 50 and +56.607 at 100 but -47.574 at 250 and -116.818 at 500; BLAST HTX -> BitMart was negative by 250.
  - STRK HTX -> MEXC/KuCoin stayed positive through 500 USDT but was about -236 bps by 1,000 and worse beyond that.
  - GOMINING HTX -> MEXC was +29.647 bps at 500 but -48.646 at 1,000.
  - AWE was negative from 50 USDT; STETH and NEXO failed by 500-1,000 USDT.
- exact failure mode: top-of-book persistence without enough depth capacity.
- stop condition: revisit only if a fresh event-window pass shows at least 1,000-2,500 USDT positive depth after venue fees and transfer haircuts, not just top-of-book persistence.

## KILL - Liquid Static XLM/INJ Gate-Buy Routes

- reason: the fresh liquid-route probe produced only single-digit top-of-book net bps, and executable depth was negative from the smallest tested 1,000 USDT bucket.
- evidence:
  - 2026-05-29 09:41 CST `scripts/market_probe.py` scanned 10,204 public markets across Binance, Bybit, OKX, Gate, KuCoin, MEXC, Bitget, Crypto.com, Bitfinex, and Bitso with zero endpoint errors.
  - The only positive `sane_priority_routes` were tiny: XLM Gate -> Bybit +6.559 bps, INJ Gate -> MEXC +3.952 bps, XLM Gate -> MEXC +2.196 bps, XLM Gate -> KuCoin +1.878 bps, XLM Gate -> Bitget +1.878 bps, and INJ Gate -> Bybit +0.448 bps.
  - Depth check before transfer costs returned all tested buckets negative from 1,000 to 25,000 USDT.
  - At 1,000 USDT: INJ Gate -> Bybit -31.541 bps, INJ Gate -> MEXC -35.219, XLM Gate -> Bybit -48.359, XLM Gate -> MEXC -52.727, XLM Gate -> Bitget -53.034, and XLM Gate -> KuCoin -56.042.
- exact failure mode: tiny top-of-book edge vanishes under executable book walking before transfer or inventory costs.
- stop condition: revisit liquid static routes only if top-of-book net exceeds a materially wider threshold and the first 1,000/5,000 USDT depth pass is positive after fees.

## KILL - CoinEx Static Taker Expansion Routes

- reason: CoinEx added many markets but produced zero sane positive same-lane routes after public taker fees and basic liquidity filters.
- evidence:
  - 2026-05-29 09:43-09:45 CST scan integrated 1,080 online CoinEx spot markets with the existing public venue set, for 11,202 total markets.
  - Public endpoints used: CoinEx `v2/spot/market` for market metadata and per-market taker fees, `v1/market/ticker/all` for bid/ask, and `v2/spot/ticker` for quote-value proxy.
  - Filters required positive net after fees/latency, 100,000+ quote-volume depth proxy, and gross spread <=1,000 bps.
  - Positive sane routes involving CoinEx: 0.
  - Best near misses were negative before depth: BABYDOGE OKX -> CoinEx -6.160 bps, NEAR MEXC -> CoinEx -7.716, BCH MEXC -> CoinEx -11.314, TON MEXC -> CoinEx -14.086, and PEPE CoinEx -> KuCoin/Bitget -15.920.
- exact failure mode: CoinEx taker fees consume the small liquid same-lane spreads before order-book depth or transfer costs are considered.
- stop condition: revisit only if a fresh CoinEx-inclusive scan shows positive net after per-market CoinEx fees, then depth-check before any metadata or execution work.

## KILL - 09:46 Spot/Perp Funding Refresh

- reason: every returned funding proxy remained negative after conservative taker round-trip fees.
- evidence:
  - `scripts/funding_probe.py` returned 14 Binance routes, 14 Bybit routes, 5 Coinbase INTX routes, and one OKX `502 Bad Gateway`.
  - Best one-period proxy was Coinbase INTX DOGE at -7.896 bps over the one-hour funding proxy.
  - Next best rows were Coinbase INTX BTC -10.628 bps, Coinbase INTX XRP -11.183, Bybit WLD -13.020 over 8h, Coinbase INTX ETH -14.936, and Binance WLD -15.320.
  - Negative-funding WLD routes would require long perp plus short/borrow spot inventory, and were still negative after the proxy.
- exact failure mode: funding plus entry basis does not overcome modeled spot/perp taker round-trip fees; OKX data was unavailable in this run.
- stop condition: revisit on the next scheduled funding refresh, especially if OKX responds or any venue shows a positive proxy with margin/borrow feasibility.

## KILL - 09:49 Bitso MXN Stable/BTC Basis

- reason: stablecoin/MXN, USD/MXN, and BTC implied FX comparisons remain negative after conservative Bitso fees.
- evidence:
  - 2026-05-29 09:48 CST public Bitso ticker refresh checked `usd_mxn`, `usdt_mxn`, `pyusd_mxn`, `btc_mxn`, and `btc_usd`.
  - Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at +35.148 bps gross but -64.852 bps net after two 50 bps legs.
  - USDT/MXN buy ask vs USD/MXN bid was -91.925 bps net; USDT/MXN sell bid vs USD/MXN ask was -114.405 bps net.
  - BTC/MXN bid vs BTC/USD*USD/MXN implied buy was -156.047 bps net after three legs; reverse was -173.774 bps net.
- exact failure mode: Bitso fees exceed current local FX/stable/BTC dislocation.
- stop condition: revisit on scheduled MXN refresh only if gross spread is already above the fee stack by a wide margin before depth.

## KILL - ULTIMA 5,000/10,000 USDT Current Watch Cap

- reason: KuCoin ULTIMA bid depth collapsed; the route is no longer positive at the previously watched 5,000 USDT size even before transfer or chain costs.
- evidence:
  - 2026-05-29 09:52-09:54 CST eight-sample watch refresh showed ULTIMA MEXC -> KuCoin 5,000 USDT 0/8 positive, avg -6,820.807 bps, min -6,926.392; 10,000 USDT 0/8 positive, avg -8,406.928 bps.
  - Follow-up small-bucket check showed ULTIMA MEXC -> KuCoin positive at 50/100/250/500 USDT, but -79.862 bps at 1,000, -5,007.063 at 2,500, and -7,499.987 at 5,000.
  - ULTIMA HTX -> KuCoin follow-up was positive through 500 USDT but -195.713 bps at 1,000 and worse beyond that.
  - KuCoin public book had only thin high bids before dropping to unusable levels, while the ULTIMA chain split remains unresolved.
- exact failure mode: destination bid-depth cliff plus unresolved SMART/native-to-BEP20 transfer path.
- stop condition: revisit only if KuCoin ULTIMA depth recovers to 2,500-5,000 USDT positive after fees and the BEP20 delivery path is proven.

## KILL - VANRY KuCoin 5,000 USDT Firm Cap

- reason: VANRY MEXC -> KuCoin 5,000 USDT printed another negative tail and no longer qualifies as a firm cap.
- evidence:
  - 2026-05-29 09:52-09:54 CST eight-sample watch refresh after the 80 VANRY MEXC withdrawal fee showed 5,000 USDT only 7/8 positive, avg +178.766 bps, median +210.646, min -130.747.
  - The 2,500 USDT bucket remained 8/8 positive, avg +584.783 bps and min +154.962.
- reopened note:
  - 2026-05-29 10:34-10:36 CST eight-sample refresh met the stop condition: 5,000 USDT was 8/8 positive after the 80 VANRY fee, avg +238.039 bps, median +261.240, min +76.284. Current ranking restores the 5,000 USDT cap while retaining this historical tail-risk entry.
- exact failure mode: 5,000 USDT has intermittent sell-depth/price-tail failure; 2,500 USDT remains the current firm bucket.
- stop condition: restore the 5,000 USDT cap only after a fresh multi-sample refresh is 100% positive with a positive minimum after withdrawal fee.

## KILL - 09:58 OKX Funding Retry

- reason: the full spot/perp funding retry returned no positive proxy after OKX recovered.
- evidence:
  - 2026-05-29 09:57 CST retry returned Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, and zero endpoint errors.
  - Best proxy was Coinbase INTX XRP at -7.391 bps over the one-hour model.
  - Next best rows were Coinbase INTX BTC -9.247 bps, Coinbase INTX SOL -9.705, Coinbase INTX ETH -10.006, OKX WLD -10.614, Coinbase INTX DOGE -11.880, Binance WLD -12.038, and Bybit WLD -16.121.
- exact failure mode: funding plus entry basis still does not overcome modeled taker round-trip fees, even with OKX included.
- stop condition: revisit on scheduled funding refresh only if a route turns positive before borrow/margin/exit-basis costs.

## KILL - Fresh Event-Window HTX Transfer-Trap Cluster

- reason: the fresh event-window sampler re-surfaced mostly known HTX transfer-disabled or depth-collapsing routes.
- evidence:
  - 2026-05-29 09:59-10:01 CST exclusion sampler ran four top-of-book samples across 12,290-12,928 markets, excluding the current watchlist and many processed bases.
  - Persistent top rows included ONE, MTL, CETUS, US, CARV, ZEC, ETHW, DGB, GENIUS, and ZEN, mostly from HTX buy legs.
  - ONE, MTL, CETUS, CARV, and ZEC had already been blocked by HTX public transfer metadata in the 09:11-09:15 expansion scan.
  - Depth check killed plausible survivors at meaningful size: DAG was negative by 250-500 USDT, DGB/ETHW/ZEN were negative by 100-250 or worse, and GENIUS was negative by 500-1,000 depending on sell venue.
- exact failure mode: repeated top-of-book persistence without repeatable transfer status or executable depth.
- stop condition: revisit only if the route is not HTX-transfer-blocked and survives a 1,000-2,500 USDT depth pass after fees.

## KILL - ATLA MEXC -> BitMart 1,000+ USDT Cap

- reason: ATLA survives only as a 500 USDT measurement pocket before transfer; 1,000 USDT flickers negative and 2,500 USDT is consistently negative.
- evidence:
  - ATLA MEXC -> BitMart depth retry before transfer showed +92.750 bps at 500 USDT, +51.331 at 1,000, and -68.297 at 2,500.
  - Six-sample persistence showed 500 USDT 6/6 positive, avg +54.386 bps and min +44.291.
  - The same persistence showed 1,000 USDT only 5/6 positive with min -3.222, and 2,500 USDT 0/6 positive avg -102.529.
  - MEXC withdrawal fee/status remains unverified because public MEXC coin/fee endpoints returned `Access Denied`.
- exact failure mode: insufficient depth above 500 USDT plus unverified transfer fee/status.
- stop condition: keep only 500 USDT on watch until MEXC withdrawal fee/status is known and a fresh 1,000 USDT persistence pass is 100% positive after transfer fee.

## KILL - 10:20 U.S.-Available XLM Core Venue Route

- reason: the only positive U.S.-available top-of-book candidate failed executable depth from the smallest tested bucket.
- evidence:
  - 2026-05-29 10:15-10:19 CST bounded scan covered 110 core markets across Binance.US, Coinbase, Kraken, Gemini, and Bitstamp.
  - Top-of-book after fees found XLM/USD Kraken -> Binance.US at +21.089 bps and XLM/USD Bitstamp -> Binance.US at +19.488 bps.
  - Depth check before transfer/inventory costs returned Kraken -> Binance.US -124.181 bps at 100 USD, -126.155 at 1,000, and -153.110 at 10,000.
  - Bitstamp -> Binance.US returned -124.981 bps at 100 USD, -128.270 at 1,000, and -154.177 at 10,000.
- exact failure mode: top-of-book spread disappears under executable book walking.
- stop condition: revisit only if U.S.-available top-of-book net is materially wider and the first 100/1,000 USD depth buckets are positive after fees.

## KILL - 10:33 Strict New-Name Event-Window Refresh

- reason: the corrected fresh-basis pass found no route with actionable executable depth after exact venue fees.
- evidence:
  - First pass ran three samples across 11,820 markets but had a BitMart ticker parser miss; it mostly resurfaced old killed names BTR, HOOLI, PHB, and MAPO plus HTX rows with no executable depth.
  - Corrected pass ran two samples across 11,231 markets with BitMart parsed and zero endpoint errors.
  - Depth killed the corrected candidates at meaningful size: OWL BitMart -> MEXC was negative from 50 USDT; MAGA/NAKA were negative from 50 or lacked sell depth; ORAI/TBK/BEAT/ID failed by 100-250; CELL and WEXO were positive only through 100; WPAY was positive through 500 but only +16.940 bps at 500 before transfer.
  - ARRR Gate -> MEXC was the only plausible micro row, but after correcting Gate's pair fee to 20 bps, six-sample persistence showed 100 USDT 6/6 positive avg +120.727 bps, 250 USDT only 1/6 positive avg -14.114 bps, and 500/1,000 USDT 0/6 positive.
  - Gate public metadata shows ARRR deposits/withdrawals enabled, and MEXC metadata supports native ARRR, so the failure is not primarily identity; it is executable depth and dust-size capacity.
- exact failure mode: stale/old candidates plus depth collapse above dust size once exact Gate fees are applied.
- stop condition: revisit these bases only if a future scan shows positive 1,000+ USDT book-walk depth after exact pair fees and transfer-fee estimates.

## KILL - 10:36 ATLA MEXC -> BitMart Current Watch

- reason: the prior ATLA 500 USDT measurement pocket disappeared in the active watch refresh.
- evidence:
  - 2026-05-29 10:34-10:36 CST eight-sample refresh checked ATLA MEXC -> BitMart at 250, 500, and 1,000 USDT.
  - 250 USDT was 0/8 positive, avg -155.228 bps, min -157.116.
  - 500 USDT was 0/8 positive, avg -170.470 bps, min -173.274.
  - 1,000 USDT was 0/8 positive, avg -199.353 bps, min -202.386.
- exact failure mode: the short-lived MEXC-vs-BitMart bid/ask dislocation fully reverted; current books are negative before transfer.
- stop condition: revisit only if a future event-window sampler rediscovers ATLA with 500 USDT 100% positive over multiple samples and MEXC withdrawal status/fee is proven.

## KILL - 10:36 GUA 5,000 USDT Pre-Positioned Cap

- reason: GUA MEXC -> Gate remains strong at 2,500 USDT but cannot support a firm 5,000 USDT pre-positioned cap.
- evidence:
  - 2026-05-29 10:34-10:36 CST eight-sample refresh used exact Gate 20 bps pair fee and no transfer fee because Gate deposits remain disabled.
  - 2,500 USDT was 8/8 positive, avg +354.473 bps, median +365.543, min +244.780.
  - 5,000 USDT was only 6/8 positive, avg +41.556 bps, median +52.394, min -50.063.
- exact failure mode: 5,000 USDT destination-book tail risk while repeatable deposits are disabled.
- stop condition: keep GUA capped at 2,500 USDT pre-positioned-only until Gate deposits reopen and 5,000 USDT is 100% positive over a fresh multi-sample pass after exact fees.

## KILL - 10:39 Funding Refresh

- reason: the scheduled public spot/perp funding refresh returned no positive one-period proxy.
- evidence:
  - 2026-05-29 10:39 CST `scripts/funding_probe.py` returned Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, and zero endpoint errors.
  - Best one-period proxy was Coinbase INTX BTC at -9.942 bps.
  - Next best rows were Coinbase INTX SOL -10.943 bps, Coinbase INTX ETH -11.556, Coinbase INTX XRP -12.695, Coinbase INTX DOGE -12.874, Bybit WLD -15.894, OKX WLD -16.737, Bybit TRX -17.936, Binance TRX -18.123, OKX TRX -18.357, and Binance WLD -18.960.
  - WLD/TRX negative-funding rows would require long perp plus short/borrow spot inventory and are still negative before borrow and exit-basis costs.
- exact failure mode: funding plus entry basis does not overcome modeled taker round-trip fees.
- stop condition: revisit on scheduled funding refresh only if a route turns positive before borrow/margin/exit-basis costs.

## KILL - 10:40 Bitso MXN Stable/Crypto Basis

- reason: Bitso's current MXN/stable/crypto basis remains negative after conservative taker fees.
- evidence:
  - 2026-05-29 10:40 CST public ticker refresh returned USD/MXN 17.335/17.337, USDT/MXN 17.319/17.322, PYUSD/MXN 17.401/17.412, BTC/MXN 1,277,810/1,284,530, and BTC/USD 73,962/73,990.
  - Best stable comparison was PYUSD/MXN sell bid vs USD/MXN buy ask at +36.915 bps gross but -63.085 bps net after two 50 bps legs.
  - USDT/MXN buy ask vs USD/MXN sell bid was -92.495 bps net; USDT/MXN sell bid vs USD/MXN buy ask was -110.382 bps net.
  - Crypto implied MXN routes were all negative after three legs: XRP/MXN best was -153.531 bps, ETH/MXN best was -162.577, and BTC/MXN best was -168.674.
- exact failure mode: Bitso fee stack exceeds the local FX/stable/crypto dislocation before order-book walking and fiat settlement friction.
- stop condition: revisit on scheduled MXN refresh only if gross spread is above the fee stack by a wide margin before depth.

## KILL - 10:46 BingX/LBank Non-ESPORTS Rows

- reason: the BingX/LBank expansion produced one measurement candidate, but the other top rows failed deposit metadata, exchange limits, or executable depth.
- evidence:
  - 2026-05-29 10:41-10:46 CST expansion parsed 12,006 markets with zero endpoint errors; BingX returned 883 markets with bid/ask, and LBank returned 976 markets but no bid/ask in the all-ticker schema.
  - RAVE LBank -> KuCoin was depth-positive through 5,000 USDT, but KuCoin public metadata reports RAVE deposits disabled on both BEP20 and ERC20.
  - RAVE LBank -> BitMart was positive through 2,500 but negative by 5,000, and BitMart public currency metadata did not expose a RAVE deposit lane in this check.
  - RAVE KuCoin/BitMart -> BingX was positive only through 500-1,000 and BingX public symbol metadata caps RAVE `maxMarketNotional` at 541, with no public deposit-status proof.
  - KAT -> BingX rows were positive only through 250-500 USDT and negative by 1,000; BingX KAT `maxMarketNotional` is 1,817.
  - CAS, TOWER, PUSS, YEE, DHN, POD, KELLYCLAUDE, KAIO, and AI4 failed executable depth by 100-1,000 USDT or lacked enough sell depth.
- exact failure mode: LBank ticker schema overstates top-of-book candidates, while direct depth and transfer/status gates kill the non-ESPORTS rows.
- stop condition: revisit only if a future scan shows 1,000+ USDT positive direct book-walk depth after exact fees plus public deposit/withdraw compatibility.

## KILL - 10:48 ESPORTS LBank -> MEXC Execution Readiness

- reason: ESPORTS LBank -> MEXC has a real 2,500 USDT public-book pocket, but it is not execution-ready because public LBank transfer status conflicts and LBank account-region eligibility is not proven.
- evidence:
  - LBank public withdrawal config returned ESPORTS BEP20 `canWithDraw=true` with fee `4.6915`.
  - Official LBank notice `https://www.lbank.com/fa/support/articles/2058904083074383872` says ESPORTS deposits and withdrawals were suspended at 2026-05-25 13:20 UTC.
  - No official resume notice was found in the quick official search.
  - LBank withdrawal config also did not expose the token contract address, so identity still needs proof against MEXC BSC contract `0xF39e4b21c84e737Df08e2C3b32541d856f508E48`.
  - Official LBank user-agreement material excludes U.S.-resident personal and corporate accounts: `https://www.lbank.com/support/articles/21436496711705`.
  - BingX variants from the same expansion also need hard region gating because BingX's Customer Agreement/Disclaimer restrict residents or passport holders of restricted jurisdictions, including the United States: `https://bingx.com/en/support/articles/12803820985231/` and `https://bingx.com/en/support/articles/11263347398927`.
- exact failure mode: execution readiness is blocked by transfer-status conflict, incomplete identity proof, and unproven non-U.S. account eligibility, even though scanner depth is positive through 2,500 USDT.
- stop condition: promote only after logged-in LBank withdrawal/deposit status, LBank contract identity, live MEXC deposit status, non-U.S. account/region eligibility, and actual fee tier are verified.

## KILL - 11:03 U.S.-Available LIT/MANA Kraken -> Bitstamp

- reason: the broader U.S.-available scan found three positive Kraken -> Bitstamp USD rows, but LIT and MANA are not executable.
- evidence:
  - 2026-05-29 10:55 CST one-shot public scan checked 1,146 usable bid/ask markets across Binance.US, Kraken, and Bitstamp. Coinbase's no-key product endpoint did not expose bid/ask in this pass.
  - `LIT` Kraken -> Bitstamp showed a huge top-of-book spread, but it is a same-ticker/asset-migration trap rather than a proven same-asset transfer route.
  - `MANA` Kraken -> Bitstamp looked positive top-of-book, but direct depth was negative from the first tested bucket: 25 USD was -1,562.339 bps after fees and Bitstamp sell depth was exhausted by 500 USD.
- exact failure mode: ticker identity/migration mismatch for LIT; destination depth collapse for MANA.
- stop condition: revisit only if the asset identity is proven same-chain and a fresh 100/500 USD book walk is positive after fees.

## KILL - 11:05 ENJ Kraken -> Bitstamp Repeatable Transfer Execution

- reason: ENJ Kraken -> Bitstamp has a real 500 USD U.S.-available book pocket, but simple repeatable transfer execution is blocked by network mismatch.
- evidence:
  - Three individual book-walk samples at 10:59-11:03 CST kept 500 USD 3/3 positive, avg +1,090.153 bps, min +1,081.106 after 40 bps Kraken, 40 bps Bitstamp, and 2 bps latency.
  - 1,000 USD was only 2/3 positive with min -8.649, so the scanner cap is 500 USD before transfer.
  - Bitstamp public currency metadata shows ENJ deposits/withdrawals enabled only on `ethereum`.
  - Kraken official ENJ support says ERC-20 ENJ deposits/withdrawals were phased out on 2024-12-10 and Kraken continues to support ENJ funding on Enjin Relaychain.
- exact failure mode: the buy venue and sell venue appear to fund different ENJ network representations, so the spread is likely a migration/bridge basis rather than direct transfer arbitrage.
- stop condition: promote only after a verified Relaychain-to-Ethereum conversion path or same-network account deposit path is proven with cost, latency, minimums, and account eligibility.

## KILL - 11:09 VANRY MEXC -> Binance USDC 5,000 Current Cap

- reason: the restored 5,000 USDC measurement cap printed another negative tail.
- evidence:
  - 2026-05-29 11:06-11:09 CST four-sample refresh included the 80 VANRY MEXC withdrawal fee, MEXC 5 bps, Binance 10 bps, and 2 bps latency.
  - 5,000 USDC was only 3/4 positive, avg +228.828 bps, min -32.644.
- exact failure mode: intermittent destination depth/price-tail failure at 5,000 USDC.
- stop condition: restore only after 2,500 and 5,000 USDC retests are 100% positive with positive minimums after withdrawal fee.

## KILL - 11:09 GUA MEXC -> Gate Current Firm Caps

- reason: even the previously firm 2,500 USDT pre-positioned GUA cap printed a negative tail.
- evidence:
  - 2026-05-29 11:06-11:09 CST four-sample refresh used exact Gate 20 bps pair fee and no transfer fee because Gate deposits remain disabled.
  - 2,500 USDT was only 3/4 positive, avg +168.507 bps, min -64.011.
  - 5,000 USDT was 1/4 positive, avg -357.768 bps, min -679.293.
- partial retest note:
  - 2026-05-29 11:29-11:31 CST lower-bucket retest restored only smaller pre-positioned caps: 500 USDT 4/4 positive avg +494.485 bps, min +380.031; 1,000 USDT 4/4 avg +331.502, min +139.719.
  - 2,500 USDT remained killed-current at 2/4 positive, avg -11.679 bps, min -132.673.
- exact failure mode: destination-book tail risk, with repeatable deposits still disabled.
- stop condition: keep GUA out of firm caps until lower buckets are retested and Gate deposits reopen or a pre-positioned-inventory strategy is explicitly chosen.

## KILL - 11:31 VANRY MEXC -> Binance USDC 5,000 Firm Cap

- reason: the lower-cap retest restored VANRY USDC at 2,500, but the 5,000 bucket remains too thin for a firm cap after the earlier negative tail.
- evidence:
  - 2026-05-29 11:29-11:31 CST lower-bucket retest showed 2,500 USDC 4/4 positive, avg +944.584 bps, min +917.416 after the 80 VANRY withdrawal fee.
  - 5,000 USDC was 4/4 positive in the retest, avg +180.869 bps, but min was only +17.544 after printing -32.644 bps in the 11:06 active refresh.
- exact failure mode: intermittent destination-book tail risk at 5,000 USDC; lower 2,500 bucket remains robust.
- stop condition: restore 5,000 only after a longer fresh refresh is 100% positive with materially positive minimum after withdrawal fee.

## KILL - 11:38 ESPORTS LBank -> MEXC 5,000 Scanner Cap

- reason: the 5,000 USDT ESPORTS scanner bucket failed the latest active refresh.
- evidence:
  - 2026-05-29 11:36-11:38 CST four-sample refresh included conservative LBank 20 bps, MEXC 5 bps, 2 bps latency, and LBank `4.6915` ESPORTS withdrawal fee.
  - 2,500 USDT remained 4/4 positive, avg +200.590 bps, min +182.457.
  - 5,000 USDT was 0/4 positive, avg -18.782 bps, min -40.148.
- exact failure mode: destination depth/tail risk at 5,000 USDT; transfer-status/account blockers remain unresolved.
- stop condition: restore 5,000 only after a fresh multi-sample pass is 100% positive with a materially positive minimum and LBank status/account gates are resolved.

## KILL - 11:38 ENJ Kraken -> Bitstamp 1,000 Scanner Cap

- reason: ENJ remains strong at 500 USD but fails at 1,000 USD.
- evidence:
  - 2026-05-29 11:36-11:38 CST four-sample refresh showed 500 USD 4/4 positive, avg +1,022.532 bps, min +1,015.964.
  - 1,000 USD was 0/4 positive, avg -241.402 bps, min -380.335.
  - Repeatable transfer execution is separately blocked by Kraken Relaychain vs Bitstamp Ethereum ENJ funding paths.
- exact failure mode: Bitstamp sell-depth cliff above 500 USD plus network mismatch for rebalancing.
- stop condition: restore 1,000 only if a future depth pass is 100% positive at 1,000 and ENJ network conversion/deposit proof exists.

## KILL - 11:34 Coinbase-Inclusive U.S. Scan

- reason: adding Coinbase Exchange public tickers to the U.S.-available scan produced no new executable route.
- evidence:
  - Coinbase broker `best_bid_ask` returned `Unauthorized`, so the scan used concurrent public Coinbase Exchange ticker calls and recovered 165 Coinbase markets.
  - Full U.S.-available scan covered 1,311 usable markets across Coinbase Exchange, Binance.US, Kraken, and Bitstamp.
  - Positive rows were LIT Kraken -> Bitstamp, VELO/SUP Kraken -> Coinbase, ENJ Kraken -> Bitstamp, MANA Kraken -> Bitstamp, and MANA Coinbase -> Bitstamp.
  - LIT, VELO, and SUP are known same-ticker/asset-migration traps; ENJ is already chain-mismatch blocked.
  - MANA Coinbase -> Bitstamp depth was negative from 25 USD: -1,619.081 bps at 25 USD, -1,805.005 at 100, -3,504.835 at 250, and Bitstamp bids exhausted by 500.
- exact failure mode: ticker collisions and thin Bitstamp destination depth overwhelm the apparent top-of-book positives.
- stop condition: revisit U.S.-available Coinbase routes only if a route survives 100/500 USD depth after conservative Coinbase fees and identity checks.

## KILL - 11:36 U.S. Same-Venue Triangular Taker Cycles

- reason: every U.S.-available USD/USDT/USDC same-venue taker cycle was negative at top-of-book.
- evidence:
  - Binance.US: 118 cycles, best USDT -> ETH -> USDC -> USDT at -5.836 bps after 2 bps per leg.
  - Coinbase Exchange: 16 cycles, best USD -> BTC -> USDT -> USD at -355.317 bps under the conservative 120 bps taker model.
  - Kraken: 244 cycles, best USDT -> USDG -> USD -> USDT at -117.427 bps.
  - Bitstamp: 24 cycles, best USD -> BTC -> USDT -> USD at -119.488 bps.
- exact failure mode: three fee-paying legs consume the available stable/crypto cross-book basis before depth is considered.
- stop condition: revisit only with account-specific maker/rebate assumptions or if a top-of-book taker cycle is already positive by a material margin.

## KILL - 11:44 Gemini-Inclusive U.S.-Available Scan

- reason: adding full Gemini public coverage produced no new executable U.S.-available route.
- evidence:
  - 2026-05-29 11:42-11:44 CST corrected public scan checked 1,904 usable markets: Coinbase 423, Binance.US 256, Kraken 771, Bitstamp 138, and Gemini 316.
  - Positive top-of-book rows were `LIT` Kraken -> Bitstamp, `VELO` Kraken -> Coinbase, `SUP` Kraken -> Coinbase, `OPG` Gemini -> Coinbase, `ENJ` Kraken -> Bitstamp, `MANA` into Bitstamp, and `INJ` into Gemini.
  - `LIT`, `VELO`, and `SUP` remained identity/ticker-collision traps. Coinbase public currency metadata identifies `VELO` as Velodrome Finance on Optimism and `SUP` as Superfluid on Base, while the Kraken rows expose only ticker-level asset metadata and the price gaps are representation-sized.
  - The new `OPG` Gemini -> Coinbase row was a parser false positive: Gemini per-symbol details for `opgusd` report base `OP`, quote `GUSD`, and contract price currency `GUSD`; Coinbase `OPG` is Opengradient on Base. This is not `OPG/USD`.
  - `INJ` top-of-book rows died on executable depth after fees: Bitstamp -> Gemini was -118.986 bps from 25-500 USD, Kraken -> Gemini was about -130 bps from the first bucket, and Coinbase -> Gemini was about -195 bps from the first bucket.
  - `MANA` remained killed by Bitstamp destination depth, and `ENJ` remains the existing 500 USD scanner-only chain-mismatch case.
- exact failure mode: apparent Gemini and Coinbase/Kraken positives were parser/identity artifacts or failed the first executable book walk.
- stop condition: revisit Gemini U.S. routes only after the scanner uses Gemini per-symbol details, excludes or separately models GUSD quote markets, and a route survives 100/500 USD depth after conservative fees and identity checks.

## KILL - 11:47 Funding Refresh

- reason: the scheduled public spot/perp funding refresh returned no positive one-period proxy.
- evidence:
  - 2026-05-29 11:47 CST `scripts/funding_probe.py` returned Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, and zero endpoint errors.
  - Best one-period proxy was Coinbase INTX DOGE -9.898 bps.
  - Next best rows were Coinbase INTX SOL -10.471 bps, Coinbase INTX XRP -11.186, Coinbase INTX BTC -11.980, Coinbase INTX ETH -14.074, Bybit WLD -14.797, OKX WLD -16.908, OKX TRX -18.330, Binance TRX -18.524, and Binance WLD -19.439.
- exact failure mode: funding plus entry basis does not overcome modeled taker round-trip fees.
- stop condition: revisit on scheduled funding refresh only if a route turns positive before borrow/margin/exit-basis costs.

## KILL - 11:47 Bitso MXN Stable/Crypto Basis

- reason: Bitso's current MXN/stable/crypto basis remains negative after conservative taker fees.
- evidence:
  - 2026-05-29 11:47 CST public ticker refresh returned USD/MXN 17.309/17.322, USDT/MXN 17.296/17.315, PYUSD/MXN 17.361/17.420, BTC/MXN 1,283,510/1,286,010, and BTC/USD 74,052/74,076.
  - Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -77.485 bps net after two 50 bps legs.
  - USDT/MXN comparisons were -103.465 and -115.010 bps net.
  - Crypto implied MXN routes were all negative after three legs: BTC sell-vs-implied-buy was best at -147.151 bps, XRP -154.263, and ETH -155.149.
- exact failure mode: Bitso fee stack exceeds the local FX/stable/crypto dislocation before order-book walking and fiat settlement friction.
- stop condition: revisit on scheduled MXN refresh only if gross spread is above the fee stack by a wide margin before depth.

## KILL - 11:51 Active Watch Larger Buckets

- reason: the latest active refresh confirmed that several larger buckets remain too fragile for firm caps.
- evidence:
  - 2026-05-29 11:49-11:51 CST active watch used four samples with six-second spacing.
  - ESPORTS LBank -> MEXC 2,500 USDT stayed positive at 4/4 avg +89.088 bps, min +72.064, but 5,000 USDT was 0/4 positive, avg -199.662, min -229.905.
  - ENJ Kraken -> Bitstamp 500 USD stayed positive at 4/4 avg +1,053.865 bps, min +1,049.290, but 1,000 USD was 0/4 positive, avg -529.055.
  - GUA MEXC -> Gate pre-positioned 1,000 USDT stayed positive at 4/4 avg +43.522 bps, min +22.969, but 2,500 USDT was 0/4 positive, avg -195.169.
  - VANRY MEXC -> Binance USDC 5,000 was 4/4 positive in this pass but had only +12.665 bps minimum after prior negative tails, so it is not restored as a firm cap.
- exact failure mode: destination-book tail risk at larger buckets; for GUA and ENJ, repeatable rebalancing remains separately blocked.
- stop condition: restore any larger bucket only after a fresh longer pass is 100% positive with materially positive minimum and the route-specific account/chain/deposit gate is resolved.

## KILL - 11:53 Liquid Static Taker Refresh

- reason: the broad static scanner produced no positive sane-priority route after generic fees and latency.
- evidence:
  - 2026-05-29 11:53 CST `scripts/market_probe.py` scanned 10,204 public markets with zero endpoint errors.
  - Best sane-priority rows were already negative before depth: BTC Crypto.com -> Bitfinex USD -2.027 bps, SOL Crypto.com -> Bitfinex -2.317, XRP Crypto.com -> Bitfinex -2.443, ETH Crypto.com -> Bitfinex -2.578, and SUI Crypto.com -> Bitfinex -2.776.
  - Best USDT rows were also negative, led by NEAR Bitget -> Binance/Bybit/OKX at -6.615 bps and SUI Gate -> MEXC at -7.184.
- exact failure mode: no top-of-book edge survived even the first fee/latency layer, so executable book walking is not justified.
- stop condition: revisit only if the static scanner finds a route whose first ranking layer is materially positive and then the first 100/1,000 quote depth buckets remain positive after exact fees.

## KILL - 11:58 Event-Window Repeatable Transfer Routes

- reason: the fresh event-window sampler found real book dislocations, but every repeatable-transfer route was blocked by destination deposit status, identity, or depth.
- evidence:
  - 2026-05-29 11:55 CST sampler ran three public top-of-book samples across 10,122 markets each with zero endpoint errors and 77 persistent filtered rows.
  - UPC MEXC -> Bitget survived depth through 5,000 USDT with +2,050.440 bps at 5,000 after exact fees. MEXC and Bitget match on ERC20 contract `0x487d62468282bd04ddf976631c23128a425555ee`, but Bitget UPC reports `rechargeable=false`.
  - POWER Bitget -> Gate survived through 5,000 USDT at +227.138 bps, and POWER MEXC -> Gate survived through 2,500 at +820.137, but Gate POWER reports `deposit_disabled=true`.
  - IAG Gate/KuCoin -> Bitget survived through 1,000 USDT but Bitget IAG reports `rechargeable=false`.
  - HYDRA MEXC -> KuCoin survived through 1,000 USDT but KuCoin HYDRA reports deposits disabled.
  - SWEAT and VRA sell into Gate were blocked by Gate deposit-disabled metadata. ARTFI, AVT, PVT, NERO, TOWER, ALKIMI, TTD, and TYCOON failed meaningful depth, hit known identity issues, or were too small.
- exact failure mode: sell-venue deposit gates prevent replenishing inventory; remaining rows fail depth or identity.
- stop condition: promote only if destination deposits reopen and a fresh multi-sample depth pass remains positive at meaningful size after exact fees and transfer fee.

## KILL - 12:01 Blocked-Route Deposit Reopen Sweep

- reason: public destination-deposit status did not reopen for the high-value blocked routes.
- evidence:
  - Gate deposits remain disabled for GUA, TBC, ESPORTS, RAVE, POWER, SWEAT, VRA, and ARTFI.
  - KuCoin deposits remain disabled for RAVE and HYDRA. KuCoin deposits are enabled for ULTIMA, IAG, TOWER, and XMN, but those routes remain blocked by other gates: ULTIMA representation mismatch, IAG Bitget destination deposits disabled, TOWER contract mismatch, and XMN pending MEXC withdrawal status/fee.
  - Bitget deposits remain disabled for UPC, IAG, RAVE, BTR, and SUP.
  - Gate TYCOON deposits are enabled, but TYCOON depth failed by 100-250 USDT in the event-window pass.
- exact failure mode: no deposit-status change removes the current execution blockers.
- stop condition: rerun periodically; promote only when destination deposits reopen and fresh depth/identity checks also pass.

## KILL - 12:03 XMN MEXC -> KuCoin Current Route

- reason: resolving the MEXC withdrawal fee turns the stale XMN micro-route negative at every tested bucket.
- evidence:
  - MEXC exchangeInfo and KuCoin metadata both identify XMN/xMoney on SUI contract `0x97c7571f4406cdd7a95f3027075ab80d3e9c937c2a567690d31e14ab1872ccee::xmn::XMN`.
  - MEXC public fee endpoint lists XMN SUI withdrawal fee `8`, deposit fee `0`, and withdrawal minimum `20`.
  - KuCoin SUI deposits and withdrawals are enabled with withdrawal fee `100` XMN, but the route direction needs deposits into KuCoin, not withdrawals out.
  - Fresh 12:03 CST depth after MEXC 5 bps, KuCoin 10 bps, 2 bps latency, and 8 XMN withdrawal fee: 50 USDT -124.436 bps, 100 -174.141, 250 -253.750, 500 -326.768, 1,000 -364.574, and 2,500 -1,760.965.
- exact failure mode: withdrawal-fee drag plus current book depth overwhelms the stale micro spread.
- stop condition: revisit only if a future event-window sampler redetects XMN with positive 500+ USDT depth after the 8 XMN fee.

## KILL - 11:12 Funding Refresh

- reason: the scheduled public spot/perp funding refresh returned no positive one-period proxy.
- evidence:
  - 2026-05-29 11:12 CST `scripts/funding_probe.py` returned Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5, and zero endpoint errors.
  - Best one-period proxy was Coinbase INTX XRP -7.416 bps.
  - Next best rows were Coinbase INTX ETH -8.661 bps, Coinbase INTX BTC -8.846, Coinbase INTX DOGE -9.890, Coinbase INTX SOL -10.583, OKX WLD -16.845, Binance TRX -17.161, Bybit WLD -17.283, Bybit TRX -18.487, and OKX TRX -18.669.
- exact failure mode: funding plus entry basis does not overcome modeled taker round-trip fees.
- stop condition: revisit on scheduled funding refresh only if a route turns positive before borrow/margin/exit-basis costs.

## KILL - 11:12 Bitso MXN Stable/Crypto Basis

- reason: Bitso's current MXN/stable/crypto basis remains negative after conservative taker fees.
- evidence:
  - 2026-05-29 11:12 CST public ticker refresh returned USD/MXN 17.326/17.335, USDT/MXN 17.316/17.318, PYUSD/MXN 17.383/17.438, BTC/MXN 1,281,390/1,284,810, and BTC/USD 74,068/74,101.
  - Best stable comparison was PYUSD/MXN sell bid vs USD/MXN buy ask at +27.690 bps gross but -72.310 bps net after two 50 bps legs.
  - USDT/MXN buy ask vs USD/MXN sell bid was -95.381 bps net; USDT/MXN sell bid vs USD/MXN buy ask was -110.960 bps net.
  - Crypto implied MXN routes were all negative after three legs: XRP/MXN best was -152.816 bps, BTC/MXN best was -161.736, and ETH/MXN best was -162.676.
- exact failure mode: Bitso fee stack exceeds the local FX/stable/crypto dislocation before order-book walking and fiat settlement friction.
- stop condition: revisit on scheduled MXN refresh only if gross spread is above the fee stack by a wide margin before depth.

## KILL - 11:14 Liquid Static Taker Refresh

- reason: the broad static scanner again produced only tiny top-of-book positives that failed direct depth.
- evidence:
  - 2026-05-29 11:13-11:14 CST `scripts/market_probe.py` scanned 10,204 markets with zero endpoint errors.
  - Top sane priority positives after generic fees were INJ Gate -> MEXC +5.652 bps, XLM Crypto.com -> Bitfinex +5.437 bps, and XLM MEXC -> Binance +1.815 bps.
  - Direct depth with stricter/exact fees killed each from the first tested bucket: INJ Gate -> MEXC -34.493 bps at 100 USDT; XLM Crypto.com -> Bitfinex -15.519 bps at 100 USD; XLM MEXC -> Binance -12.285 bps at 100 USDT.
- exact failure mode: tiny top-of-book edge disappears under executable book walking and exact fee assumptions.
- stop condition: revisit only if the static scanner finds a route whose first 100/1,000 quote depth buckets are positive after exact fees.

## KILL - 11:28 Event-Window Sampler And TSLAON

- reason: the fresh event-window sampler found persistent positives, but none survived executable depth and persistence with enough margin.
- evidence:
  - Three samples across 10,122 markets per sample returned zero endpoint errors.
  - Persistent positives included ASSET KuCoin -> MEXC, NIBI MEXC -> KuCoin, TX Bitget -> Gate, TSLAON MEXC -> Bitget, and DEXE KuCoin -> MEXC/Binance.
  - ASSET was positive only through 250 USDT and negative by 500; NIBI and TX were negative from 50 USDT; DEXE was positive only through 100 and negative by 250.
  - TSLAON metadata looked operationally plausible: MEXC and Bitget expose matching ERC20 contract `0xf6b1117ec07684d3958cad8beb1b302bfd21103f`, Bitget deposits/withdrawals are enabled, and MEXC fee-page metadata lists a 0.002 TSLAON ERC20 withdrawal fee.
  - TSLAON four-sample persistence after transfer fee was still too weak: 1,000 USDT was only 3/4 positive, avg +3.755 bps, min -0.066; 2,500 was 1/4 positive, avg -2.256.
- exact failure mode: the only metadata-plausible route had an edge smaller than normal public-book staleness and execution tail risk after transfer fee.
- stop condition: revisit TSLAON only if a future pass shows 1,000+ USDT 100% positive with a materially positive minimum after exact fees and current MEXC withdrawal status is verified.
