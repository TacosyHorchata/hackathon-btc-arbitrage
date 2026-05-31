# Agent 2 Next Actions

Updated: 2026-05-29 12:16 CST

## Current Active Ranking

1. `DO_NOW` - Account/region proof before any execution design. Official MEXC, KuCoin, LBank, and BingX materials currently restrict U.S.-resident users, and Binance.US does not list VANRY; if Pedro's execution account is U.S.-resident, the current MEXC/KuCoin/Binance-global/LBank/BingX routes are compliance-blocked.
2. `DO_NOW` - VANRY MEXC -> Binance scanner/watchlist, firm public-book cap 10,000 USDT for non-U.S. compliant accounts; latest 12:05 refresh stayed 3/3 positive after the 80 VANRY withdrawal fee, min +236.042 bps.
3. `DO_NOW` - VANRY MEXC -> KuCoin scanner/watchlist, public-book cap 5,000 USDT for non-U.S. compliant accounts; latest 12:05 refresh stayed 3/3 positive after the 80 VANRY withdrawal fee, min +229.884 bps.
4. `MEASURE` - U.S.-available ENJ Kraken -> Bitstamp USD scanner-only pocket, firm cap 500 USD after the latest refresh stayed 3/3 positive with min +1,038.871 bps. The 1,000 USD bucket also printed 3/3 positive, min +182.584, but do not restore it as a firm cap yet because the prior refresh was 0/4 and repeatable transfer remains killed by Kraken Enjin Relaychain vs Bitstamp Ethereum.
5. `MEASURE` - VANRY MEXC -> Binance USDC lane, firm measurement cap remains 2,500 USDC after the latest refresh stayed 3/3 positive with min +709.668 bps after the 80 VANRY fee. 5,000 USDC was only 2/3 positive with min -177.208, so keep it killed-current.
6. `LATER` - ULTIMA MEXC -> KuCoin chain-proof-only watch. 5,000 USDT stayed 3/3 positive in the latest refresh, min +432.244 bps before chain proof, but repeatable execution remains blocked by unresolved MEXC SMART/native vs KuCoin BEP20 delivery.
7. `LATER` - GUA MEXC -> Gate pre-positioned watch, current lower cap 1,000 USDT only. Latest refresh was 3/3 positive at 1,000 with min +108.160 bps; 2,500 was 0/3 positive and repeatable transfer remains killed while Gate deposits are disabled.
8. `LATER` - UPC MEXC -> Bitget pre-positioned-inventory watch. Clean 12:09 direct retest was positive through 10,000 USDT with +1,575.217 bps at 10,000 after exact fees, but repeatable transfer remains killed because Bitget public coin metadata has UPC `rechargeable=false`.
9. `LATER` - POWER Bitget/MEXC -> Gate pre-positioned-inventory watch. Bitget -> Gate stayed positive through 5,000 USDT (+227.138 bps) and MEXC -> Gate through 2,500 (+820.137), but Gate deposits are disabled.
10. `LATER` - ESPORTS MEXC -> Gate, RAVE Bitget -> KuCoin/Gate, and TBC MEXC -> Gate pre-positioned-inventory watches. Sell-venue deposits are disabled, so repeatable transfer execution is killed.
11. `KILL_CURRENT` - ESPORTS LBank -> MEXC current scanner cap. The 12:05 refresh flipped 2,500 USDT to 0/3 positive, avg -23.699 bps, min -36.068; 5,000 was also 0/3. Revisit only if rediscovered by a fresh event-window pass plus LBank transfer/account proof.
12. `KILL_CURRENT` - ATLA MEXC -> BitMart. The 10:34 refresh was 0/8 positive at 250, 500, and 1,000 USDT, so the prior 500 USDT micro-measure is dead until rediscovered.
13. `KILL_CURRENT` - XMN MEXC -> KuCoin. MEXC public fee metadata now resolves SUI withdrawal fee at 8 XMN and minimum 20 XMN, but the fresh 12:03 depth check was negative from 50 USDT after the withdrawal fee.
14. `DO_NOW` - Fee-aware event-window detector with identity, depth, persistence, median/positive-ratio, transfer/deposit status, region/account eligibility, and staleness/RTT fields. Add a hard Gemini parser gate: use per-symbol details because `opgusd` is `OP/GUSD`, not `OPG/USD`.
15. `KILL_CURRENT` - SPX Bybit/MEXC -> KuCoin. It was 0/12 positive in the 09:25 watch refresh; revisit only if a fresh event-window sampler re-detects persistent positive depth.

## Latest Discovery Update

2026-05-29 06:38-06:45 CST: a corrected exclusion scan found 14 tail top-of-book route candidates from 10,216 markets / 2,048 same-lane routes, with zero endpoint errors. It produced no promotion.

- `JASMY` was the only candidate with apparent batch capacity, but a 20-sample retest from 06:41:16 to 06:45:00 CST had 0/20 positive on Binance/Bitget/Bybit -> MEXC at every tested size from 1,000 to 10,000 USDT before transfer fees.
- `BOS`, `EGL1`, `GROK`, and `NYM` were micro pockets only, positive below 250 USDT and not actionable.
- `ETN`, `QKC`, `UNION`, and `POKT` failed live depth from 50 USDT.
- No discovery-driven promotion; route-refresh cap changes are handled below.

Funding refresh at 08:54 CST also produced no promotion: 47 public spot/perp proxies across Binance, Bybit, OKX, and Coinbase INTX all remained negative after fees and entry-basis proxy. Best result was Coinbase INTX SOL at -7.842 bps over the one-hour proxy, followed by Coinbase INTX BTC at -9.243 bps and XRP at -11.183 bps. Best USDT negative-funding route was Binance WLD at -12.422 bps over the 8h proxy.

Bitso MXN/stables refresh at 08:54 CST also produced no promotion: best stablecoin-vs-USD/MXN comparison was PYUSD/MXN sell-vs-USD/MXN at -51.857 bps after two fees. USD/MXN sell-vs-USDT/MXN was -91.759 bps, and MXN/USD/USDT triangles remained negative (-131.442 bps and -172.542 bps).

Binance.US same-venue triangular scan at 08:56 CST also produced no promotion. Using the prior official 2 bps taker assumption, 261 tradable symbols produced 264 USD/USDT/USDC-starting 3-leg cycles. Best cycle was USDT -> USD -> USDC -> USDT at -6.710 bps; all top crypto bridge cycles were negative as well.

MEXC same-venue triangular scan at 08:57 CST also produced no execution promotion. Scope was 2,323 tradable symbols and 1,810 USDT/USDC/BTC/ETH-starting cycles. Three top-of-book cycles were positive, but all were dust-constrained: AWF/USD1/USDT was capped by 0.01 AWF on the sell leg, and the ADA/EUR cycles were capped by roughly 0.006 EUR on the ADAEUR ask. Best non-dust stable/EUR loops were already negative.

KuCoin same-venue triangular scan at 08:58 CST also produced no execution promotion. Scope was 1,082 tradable symbols and 982 USDT/USDC/BTC/ETH-starting cycles. There were zero positive cycles after a 10 bps per-leg taker assumption; best cycle was USDT -> VSYS -> BTC -> USDT at -6.389 bps.

Gate same-venue triangular scan at 09:00-09:04 CST also produced no execution promotion. A corrected all-symbol scan found 10 positive top-of-book cycles from 2,206 tradable symbols and 710 USDT/USDC/BTC/ETH-starting cycles, led by GALA and smaller LIKE/XRD/REZ loops. Immediate executable-book depth killed every row at the smallest tested bucket: GALA USDT -130.644 bps at 10 USDT, GALA USDC -160.048 bps at 10 USDC, LIKE -244.170 bps at 10 USDT, XRD -123.478 bps at 10 USDT, and REZ -134.798 bps at 10 USDT. Gate triangles should only re-enter ranking through a capacity-aware scanner.

Hyperliquid same-venue spot/perp funding probe at 09:08 CST also produced no immediate promotion. Using official tier-0 taker fees, the model charges 23.0 bps round-trip for spot entry/exit plus perp entry/exit. Nineteen raw common spot/perp candidates collapsed to 12 sane pairs after rejecting spot/perp mids more than 200 bps apart. Best clean one-hour proxy was ETH at -10.934 bps after fees; BTC -15.658 bps, SOL -16.395 bps, wrapped PUMP -18.746 bps, and HYPE -29.235 bps. Keep Hyperliquid carry as `LATER` only for maker/post-only or multi-hour funding persistence with exit modeling.

HTX expansion scan at 09:11-09:15 CST produced one strong but operationally blocked watch route. ULTIMA HTX -> KuCoin was 10/10 positive at 1,000, 2,500, and 5,000 USDT before transfer, with 5,000 USDT avg +398.199 bps and min +340.505 bps. Do not promote to repeatable execution: HTX public metadata exposes ULTIMA on `ultima1` with deposits/withdrawals enabled and fee `0.00001`, while KuCoin exposes only BEP20/BSC contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`. ZEC HTX -> OKX also had strong depth through 10,000 USDT, but HTX ZEC withdrawals are prohibited. Other HTX rows failed depth or transfer status. Keep HTX in discovery; route ULTIMA only as pre-positioned/bridge-only until chain compatibility is proven.

BitMart expansion scan at 09:18-09:20 CST produced no immediate promotion. BitMart added 1,107 parsed markets; a metadata-backed request returned one transient 502 before ticker parsing succeeded. ULTIMA BitMart -> KuCoin was positive through 2,500 USDT but negative by 5,000 and suffers the same chain split: BitMart exposes SMART ULTIMA contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`, while KuCoin exposes BEP20/BSC `0x5668a83b46016b494a30dd14066a451e5417a8b8`. QAIT failed by 1,000 USDT; BTR had no compatible Bitget deposit path. Keep BitMart as discovery-only.

Watch refresh at 09:25 CST kept the main caps but killed current SPX. VANRY MEXC -> Binance USDT 10,000 stayed 12/12 positive after the 80 VANRY fee, avg +310.346 bps, min +289.750. VANRY MEXC -> KuCoin USDT 5,000 stayed 12/12 positive, avg +192.664, min +153.914. VANRY MEXC -> Binance USDC 2,500 stayed 12/12 positive, avg +840.599, min +653.161, but 5,000 USDC was only 9/12 positive with min -207.212. ULTIMA MEXC -> KuCoin 5,000 stayed 12/12 positive before chain proof, avg +410.174, min +318.532; 10,000 had one negative and one KuCoin 502. ULTIMA HTX -> KuCoin 5,000 stayed 12/12 positive, avg +392.967, min +307.767, but remains chain-split blocked. SPX was 0/12 positive on all current tested buckets and is removed from active measure.

ULTIMA chain source check at 09:27 CST reinforced the block: BitMart's official listing classifies ULTIMA as `SMART` and links SMART contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`; KuCoin's official listing says deposits use `BSC-BEP20`, and KuCoin's public API exposes only BEP20 contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`. No official/public bridge proof was found. Treat ULTIMA premium as cross-representation until logged-in BEP20 withdrawal or bridge proof exists.

Expanded event-window depth pass at 09:31-09:38 CST produced one new pre-positioned-only watch and no repeatable-transfer promotion. GUA MEXC -> Gate survived executable depth before transfer through 2,500 USDT (+209.824 bps) but Gate public metadata shows GUA deposits disabled on BSC contract `0xa5c8e1513b6a08334b479fe4d71f1253259469be`; repeatable transfer is killed, pre-positioned Gate inventory is `LATER`. ORDI HTX -> Bybit/Bitget was positive through 1,000 USDT before transfer, but HTX's `5.004459` ORDI withdrawal fee is roughly 170 bps at the checked price and wipes the edge. RACA/TST/BLAST/STRK/GOMINING/STETH/NEXO/AWE collapsed by depth.

Liquid static refresh at 09:41-09:42 CST produced no promotion. `scripts/market_probe.py` scanned 10,204 markets with zero endpoint errors; only tiny sane priority positives appeared, led by XLM Gate -> Bybit +6.559 bps and INJ Gate -> MEXC +3.952 bps. Immediate depth checks made every XLM/INJ Gate-buy route negative from the 1,000 USDT bucket, so liquid static routes remain below event-window and operational-feasibility work.

CoinEx expansion scan at 09:43-09:45 CST produced no promotion. It added 1,080 online spot markets and brought the integrated static scan to 11,202 markets, but zero CoinEx-involved routes were positive after CoinEx per-market taker fees, existing venue fees, latency, 100,000+ quote-volume proxy, and gross <=1,000 bps filters. Best near miss was BABYDOGE OKX -> CoinEx at -6.160 bps before depth.

Funding refresh at 09:46 CST produced no promotion. Binance, Bybit, and Coinbase INTX returned data; OKX returned one `502 Bad Gateway`. Best proxy was Coinbase INTX DOGE -7.896 bps over the one-hour model, followed by Coinbase INTX BTC -10.628, XRP -11.183, Bybit WLD -13.020, Coinbase INTX ETH -14.936, and Binance WLD -15.320.

Bitso MXN/stable refresh at 09:48 CST produced no promotion. Best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -64.852 bps net after two Bitso fees. USDT/MXN comparisons were -91.925 and -114.405 bps net; BTC/MXN implied USD comparisons were -156.047 and -173.774 bps net after three fees.

Active watch refresh at 09:52-09:54 CST changed the live caps. VANRY MEXC -> Binance USDT 10,000 stayed 8/8 positive after the 80 VANRY fee, avg +275.623 bps, min +79.560. VANRY MEXC -> KuCoin USDT 2,500 stayed 8/8 positive, avg +584.783, min +154.962, but 5,000 was only 7/8 positive with min -130.747, so firm cap drops to 2,500. VANRY MEXC -> Binance USDC 2,500 stayed 8/8 positive, avg +911.620, min +590.155, while 5,000 was 7/8 with min -253.295. GUA MEXC -> Gate pre-positioned-only stayed 8/8 positive at 2,500, avg +254.447, min +208.167; 5,000 was only 1/8 positive. ULTIMA MEXC/HTX -> KuCoin lost the 5,000 cap: follow-up small-bucket check showed both buy venues positive only through 500 and negative by 1,000 before chain proof.

OKX funding retry at 09:57 CST closed the earlier 502 gap and still produced no promotion. Binance, Bybit, OKX, and Coinbase INTX all returned data with zero errors. Best proxy was Coinbase INTX XRP -7.391 bps, followed by Coinbase INTX BTC -9.247, SOL -9.705, ETH -10.006, OKX WLD -10.614, Coinbase INTX DOGE -11.880, Binance WLD -12.038, and Bybit WLD -16.121.

Fresh event-window exclusion scan at 09:59-10:04 CST produced one micro `MEASURE`: ATLA MEXC -> BitMart. Four top-of-book samples found persistent positives after excluding the current watchlist and recent kills. Most rows were known HTX transfer/depth traps. ATLA survived depth at 500 USDT and a six-sample persistence check stayed 6/6 positive, avg +54.386 bps, min +44.291 before transfer. 1,000 USDT had a negative tail and 2,500 was 0/6 positive. BitMart native ATLA deposits are enabled; MEXC official listing history says deposits opened and withdrawals were scheduled for 2025-08-18, but current MEXC withdrawal status/fee remains unverified because public MEXC coin/fee endpoints returned `Access Denied`.

U.S.-available core venue refresh at 10:15-10:20 CST produced no promotion. The bounded scan covered 110 markets across Binance.US, Coinbase, Kraken, Gemini, and Bitstamp. XLM/USD Kraken -> Binance.US and Bitstamp -> Binance.US were the only top-of-book positives after fees, but depth was negative from 100 USD on both routes.

Strict new-name refresh at 10:23-10:33 CST produced no promotion. A first pass resurfaced old killed BTR/HOOLI/PHB/MAPO and HTX no-depth rows. A corrected pass parsed 11,231 markets including BitMart with zero endpoint errors; all new rows failed meaningful depth. ARRR Gate -> MEXC was the only plausible micro survivor, but after correcting Gate to its actual 20 bps pair fee, six-sample persistence showed only 100 USDT 6/6 positive, while 250 was 1/6 positive and 500/1,000 were 0/6. Keep this as a scanner-regression kill, not an active opportunity.

Active watch refresh at 10:34-10:36 CST changed current caps. VANRY MEXC -> Binance USDT 10,000 stayed 8/8 positive, avg +270.132 bps, min +106.909 after the 80 VANRY withdrawal fee. VANRY MEXC -> KuCoin 5,000 recovered to 8/8 positive, avg +238.039, min +76.284, so restore the 5,000 cap with tail-risk monitoring. VANRY MEXC -> Binance USDC 5,000 recovered to 8/8 positive, avg +595.583, min +197.250, so restore the 5,000 measurement cap. GUA 2,500 pre-positioned-only stayed 8/8 positive after exact Gate fee, but 5,000 was only 6/8 positive. ATLA was 0/8 positive at every tested bucket and is killed current. ULTIMA MEXC -> KuCoin recovered through 2,500, but remains chain-proof-only.

Funding refresh at 10:39 CST produced no promotion. Binance 14, Bybit 14, OKX 14, and Coinbase INTX 5 routes returned with zero endpoint errors. Best one-period proxy was Coinbase INTX BTC -9.942 bps, followed by Coinbase INTX SOL -10.943, ETH -11.556, XRP -12.695, DOGE -12.874, Bybit WLD -15.894, OKX WLD -16.737, and Bybit TRX -17.936. Keep funding as scheduled monitor only.

Bitso MXN refresh at 10:40 CST produced no promotion. Best stable comparison was PYUSD/MXN sell bid vs USD/MXN buy ask at -63.085 bps net after two Bitso legs. USDT/MXN was -92.495 / -110.382 bps net depending on direction. Crypto implied MXN routes were worse: XRP best -153.531 bps, ETH best -162.577, BTC best -168.674 after three legs.

BingX/LBank venue expansion at 10:41-10:46 CST produced one new scanner-only `MEASURE`: ESPORTS LBank -> MEXC capped at 2,500 USDT. LBank public withdrawal config shows BEP20 withdrawals enabled with fee `4.6915` ESPORTS, but official LBank notice `https://www.lbank.com/fa/support/articles/2058904083074383872` says ESPORTS deposits/withdrawals were suspended at 2026-05-25 13:20 UTC, with no resume notice found in the quick official search. Six-sample persistence after conservative fees and the LBank withdrawal fee: 1,000 USDT 6/6 positive avg +305.079 bps, 2,500 6/6 avg +177.340 min +41.913, 5,000 only 4/6 and avg negative, 10,000 0/6. Do not execute before LBank transfer-status conflict, LBank contract identity, live MEXC deposit status, actual fee tier, and non-U.S. account/region proof are resolved.

U.S.-available full-venue scan at 10:55-11:03 CST found one new scanner-only pocket. A one-shot top-of-book pass across Binance.US, Coinbase endpoint probe, Kraken, and Bitstamp checked 1,146 markets; Coinbase's all-products endpoint did not expose actionable bid/ask in this pass. Positives were Kraken -> Bitstamp `LIT`, `ENJ`, and `MANA`. Depth/identity killed `LIT` as a same-ticker trap and `MANA` by sell-depth collapse. `ENJ` survived at 500 USD: three individual book-walk samples were 3/3 positive with avg +1,090.153 bps and min +1,081.106 after 40 bps Kraken, 40 bps Bitstamp, and 2 bps latency; 1,000 USD was only 2/3 positive with min -8.649. Repeatable transfer is blocked because Kraken's official ENJ support page says ERC-20 ENJ funding was phased out and Enjin Relaychain funding remains supported, while Bitstamp public currency metadata shows ENJ deposits/withdrawals enabled only on Ethereum.

Active watch refresh at 11:06-11:09 CST changed caps again. VANRY MEXC -> Binance USDT 10,000 stayed 4/4 positive, avg +279.010 bps, min +209.416. VANRY MEXC -> KuCoin USDT 5,000 stayed 4/4 positive, avg +240.279, min +134.193. VANRY MEXC -> Binance USDC 5,000 degraded to 3/4 positive, min -32.644, so the 5,000 USDC measurement cap is killed-current pending 2,500 retest. GUA MEXC -> Gate pre-positioned 2,500 also degraded to 3/4 positive with min -64.011; kill the firm 2,500 cap. ULTIMA MEXC -> KuCoin 5,000 recovered to 4/4 positive but remains chain-proof-only. ESPORTS LBank -> MEXC stayed 4/4 positive at 2,500, min +221.900, while 5,000 was thin but positive. ENJ Kraken -> Bitstamp stayed 4/4 positive at 500 USD, min +1,088.802, and 1,000 was 0/4 positive.

Scheduled funding and Bitso refreshes at 11:12 CST produced no promotion. Funding returned Binance 14, Bybit 14, OKX 14, Coinbase INTX 5, zero endpoint errors; best proxy was Coinbase INTX XRP -7.416 bps, then ETH -8.661, BTC -8.846, DOGE -9.890, SOL -10.583, OKX WLD -16.845, and Binance TRX -17.161. Bitso best stable comparison was PYUSD/MXN sell bid vs USD/MXN ask at -72.310 bps net after two fees; USDT/MXN was -95.381 / -110.960 bps net, and crypto implied MXN routes remained worse than -152.816 bps net.

Broad static refresh at 11:13-11:14 CST produced no promotion. `scripts/market_probe.py` scanned 10,204 markets with zero endpoint errors. Only three sane priority rows were positive top-of-book after generic fees: INJ Gate -> MEXC +5.652 bps, XLM Crypto.com -> Bitfinex +5.437 bps, and XLM MEXC -> Binance +1.815 bps. Direct depth with stricter/exact fees killed all from 100 quote: INJ Gate -> MEXC -34.493 bps at 100 USDT, XLM Crypto.com -> Bitfinex -15.519 bps at 100 USD, and XLM MEXC -> Binance -12.285 bps at 100 USDT.

Fresh event-window sampler at 11:15-11:28 CST produced no promotion. Three samples across 10,122 markets found persistent positives led by ASSET KuCoin -> MEXC, NIBI MEXC -> KuCoin, TX Bitget -> Gate, TSLAON MEXC -> Bitget, and DEXE KuCoin -> MEXC/Binance. Depth killed ASSET above 250 USDT, NIBI/TX from 50 USDT, and DEXE above 100 USDT. TSLAON had matched ERC20 metadata and Bitget deposits enabled, but four-sample persistence after the 0.002 TSLAON MEXC withdrawal fee was not strong enough: 1,000 USDT was only 3/4 positive with min -0.066 bps, and 2,500 was 1/4 positive. Kill current TSLAON rather than adding a fragile watch route.

Lower-cap retest at 11:29-11:31 CST clarified the degraded buckets. VANRY MEXC -> Binance USDC 2,500 was 4/4 positive, avg +944.584 bps, min +917.416 after the 80 VANRY fee; 5,000 was 4/4 positive but thin, avg +180.869, min +17.544, so only 2,500 is firm. GUA MEXC -> Gate pre-positioned was 4/4 positive at 500 and 1,000, with 1,000 min +139.719 bps; 2,500 remained unstable at 2/4 positive with min -132.673, so restore only a 1,000 pre-positioned lower cap.

Coinbase-inclusive U.S.-available scan at 11:32-11:34 CST produced no new promotion. Concurrent public Coinbase Exchange ticker calls added 165 Coinbase markets to Binance.US/Kraken/Bitstamp for 1,311 total usable markets. Positives were already-known traps: LIT Kraken -> Bitstamp, VELO/SUP Kraken -> Coinbase ticker collisions, ENJ Kraken -> Bitstamp chain-mismatch basis, and MANA into Bitstamp. MANA Coinbase -> Bitstamp depth was negative from 25 USD (-1,619.081 bps) and exhausted Bitstamp bids by 500 USD.

U.S.-available same-venue triangular scan at 11:35-11:36 CST produced no promotion. Binance.US was closest with ETH USDT -> USDC -> USDT at -5.836 bps after its 2 bps taker assumption. Coinbase cycles were worse than -355 bps under the conservative 120 bps taker model; Kraken and Bitstamp were around -117 bps or worse. No depth work justified.

Active watch refresh at 11:36-11:38 CST kept the main caps and killed thin expansion buckets. VANRY MEXC -> Binance USDT 10,000 stayed 4/4 positive, avg +301.248 bps, min +256.660. VANRY MEXC -> KuCoin 5,000 stayed 4/4 positive, avg +366.447, min +284.561. VANRY MEXC -> Binance USDC 2,500 stayed 4/4 positive, avg +821.553, min +632.805; 5,000 was only 2/4 positive with min -248.499. ESPORTS LBank -> MEXC 2,500 stayed 4/4 positive, avg +200.590, min +182.457; 5,000 was 0/4 positive. ENJ Kraken -> Bitstamp 500 stayed 4/4 positive, min +1,015.964; 1,000 stayed 0/4 positive.

Processed-base exclusion scan at 07:01 CST produced seven new top-of-book routes across five bases (`ACA`, `ES`, `IN`, `OBOL`, `SBUXON`) and zero endpoint errors. Depth killed all of them: `ACA`, `IN`, and `OBOL` were negative from 50 USDT; `ES` and `SBUXON` were positive only below 500 USDT.

U.S.-available venue substitution scan at 07:29 CST produced no promotion: 1,971 public markets across Binance.US, Coinbase Exchange, Kraken, Gemini, and Bitstamp; 378 common USD/USDT/USDC keys; zero endpoint errors. Liquid major-pair routes were negative after conservative fees, and the positive long-tail rows were ticker collisions (`LIT`, `VELO`, `SUP`) or failed depth (`GWEI`, `TRAC`).

Maker/rebate fee check at 07:34 CST also produced no immediate promotion. Binance.US 0 maker / 2 bps taker is useful for future post-only scanning, but fee improvement alone does not flip the killed liquid static routes. Kraken and Coinbase public rebate/VIP paths require high-volume or program eligibility, so maker/rebate stays `LATER` until account fee tier and queue/fill model exist.

Targeted corrected-fee retest at 08:02 CST still did not rescue the U.S.-available static route. With Binance.US taker corrected to 2 bps, prior best liquid rows remained negative: BTC/USD Bitstamp -> Binance.US -38.074 bps, BTC/USDT Bitstamp -> Binance.US -47.772 bps, SOL/USD Bitstamp -> Binance.US -44.893 bps, HYPE/USD Bitstamp -> Binance.US -53.955 bps, and USDT/USD Kraken -> Binance.US -42.495 bps.

Fresh global public probe at 07:48 CST scanned 10,216 markets and found 99 filtered top-of-book watch rows with zero endpoint errors. Depth-checking the top new rows produced no execution promotion. `TBC` MEXC -> Gate was the only robust depth survivor through 5,000 USDT, but Gate's official public currency endpoint has TBC deposits disabled, so it is repeatability-killed and only a pre-positioned-inventory watch case. `YFII`, `DCK`, `DN`, `AO`, `HONEY`, `AVL`, and `QAIT` were killed by depth/capacity.

TBC persistence check at 07:48-07:49 CST stayed 10/10 positive at 1,000, 2,500, and 5,000 USDT, with 5,000 USDT avg +198.175 bps and min +196.087 bps. Verdict unchanged: `LATER` / pre-positioned inventory only because Gate deposits are disabled.

Fresh public probe at 08:09 CST found only small sane top-of-book positives on Crypto.com USD buy -> Bitfinex USD sell for majors, after Bitfinex's current official zero-fee schedule. Depth killed ETH/XRP/SOL immediately; BTC/USD looked barely positive in one snapshot but failed a 10-sample persistence check from 08:10:32 to 08:11:18 CST with 0/10 positive at 1,000-25,000 USD. Verdict: `KILL` immediate Crypto.com -> Bitfinex execution; Bitfinex is also account-gated for U.S. persons.

Fresh hard-filter discovery at 08:21-08:24 CST found new high-bps long-tail pockets. ESPORTS MEXC -> Gate stayed 10/10 positive at 5,000 USDT, avg +2400.213 bps; RAVE Bitget -> KuCoin stayed 10/10 positive at 5,000 USDT, avg +1482.521 bps; RAVE Bitget -> Gate stayed 10/10 positive at 5,000 USDT, avg +194.290 bps. All are `LATER` / pre-positioned-inventory only because the relevant sell venues report deposits disabled. RWA was killed as a same-ticker collision: MEXC/Gate/Bitget identify BSC Allo, while KuCoin identifies Base RWA Inc.

Deposit-enabled follow-up at 08:28-08:30 CST produced no direct promotion. AI Gate -> KuCoin/MEXC was killed as a ticker collision: Gate `AI` is Sleepless AI on BSC, while KuCoin/MEXC `AI` is Gensyn. ALEX, PUSH, SNEK, REACT, AFC, ROUTE, SAMO, and OGPU either turned negative by 250-500 USDT or were negative from the first bucket.

Fresh processed-base exclusion scan at 08:39 CST covered 10,213 markets with zero endpoint errors and found 58 filtered long-tail rows after excluding already processed bases. Depth-checking the top cluster produced no promotion: SHR and LKI were negative from 50 USDT; BNKR was positive only through 500 USDT and negative by 1,000 USDT; GHX, CWEB, PYBOBO, KEKIUS, DEVVE, and ASSET all failed by 250-1,000 USDT; WOJAK was negative from 50 USDT.

Event-window sampler at 08:41-08:44 CST ran 8 repeated public top-of-book samples across the main venues, excluding Bitso and processed bases, with zero endpoint errors. Most persistent rows failed live depth; `SPX` was the only measured survivor. SPX Bybit -> KuCoin stayed 10/10 positive through 5,000 USDT before unknown Bybit transfer fee, but 10,000 USDT was 0/10 positive. SPX MEXC -> KuCoin stayed 10/10 positive at 1,000 and 2,500 USDT after the 3 SPX MEXC ERC20 withdrawal fee, but 2,500 USDT had a thin +4.044 bps min and 5,000 USDT was 0/10 positive.

## Latest Route Refresh

2026-05-29 12:05 CST, compact active watch refresh.

- VANRY MEXC -> Binance USDT: 10,000 USDT 3/3 positive after the 80 VANRY fee, avg +328.791 bps, min +236.042. Keep the 10,000 USDT cap.
- VANRY MEXC -> KuCoin USDT: 5,000 USDT 3/3 positive after the 80 VANRY fee, avg +290.453 bps, min +229.884. Keep the 5,000 USDT cap.
- VANRY MEXC -> Binance USDC: 2,500 USDC 3/3 positive after the 80 VANRY fee, avg +921.386 bps, min +709.668. 5,000 USDC was only 2/3 positive, avg +308.857, min -177.208, so keep firm cap at 2,500 and keep 5,000 killed-current.
- ESPORTS LBank -> MEXC scanner-only: 2,500 USDT flipped to 0/3 positive, avg -23.699 bps, min -36.068. 5,000 USDT was also 0/3, avg -318.594. Kill the current ESPORTS LBank cap until rediscovered.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD 3/3 positive, avg +1,041.487 bps, min +1,038.871. 1,000 USD also printed 3/3 positive, avg +194.732, min +182.584, but prior 1,000 was 0/4 and repeatable transfer remains chain-mismatch blocked, so keep firm cap at 500 pending a longer retest.
- ULTIMA MEXC -> KuCoin chain-proof-only: 5,000 USDT 3/3 positive, avg +439.480 bps, min +432.244 before chain proof. Keep `LATER`.
- GUA MEXC -> Gate pre-positioned-only: 1,000 USDT 3/3 positive, avg +159.317 bps, min +108.160; 2,500 USDT 0/3, avg -198.137. Keep only the 1,000 pre-positioned cap.
- UPC MEXC -> Bitget pre-positioned-only: active-watch row errored and is not evidence. Keep the 11:58 direct-depth measurement until a clean retest.

UPC clean retest at 12:09 CST:

- UPC MEXC -> Bitget direct depth fetched cleanly: 50 USDT +3,071.889 bps, 100 +2,984.681, 250 +2,861.136, 500 +2,814.170, 1,000 +2,681.199, 2,500 +2,279.171, 5,000 +2,038.202, and 10,000 +1,575.217 after MEXC 5 bps, Bitget 10 bps, and 2 bps latency.
- Bitget public coin metadata still reports UPC ERC20 `rechargeable=false` on contract `0x487d62468282bd04ddf976631c23128a425555ee`, so the route remains pre-positioned-inventory only despite the book.

Previous 11:49-11:51 CST compact active watch refresh:

2026-05-29 11:49-11:51 CST, compact active watch refresh.

- VANRY MEXC -> Binance USDT: 10,000 USDT 4/4 positive after the 80 VANRY fee, avg +290.414 bps, min +208.947. Keep the 10,000 USDT cap.
- VANRY MEXC -> KuCoin USDT: 5,000 USDT 4/4 positive after the 80 VANRY fee, avg +225.427 bps, min +123.462. Keep the 5,000 USDT cap.
- VANRY MEXC -> Binance USDC: 2,500 USDC 4/4 positive after the 80 VANRY fee, avg +853.068 bps, min +751.993. 5,000 USDC was 4/4 positive but thin, avg +368.305, min +12.665, so keep firm cap at 2,500 after prior negative tails.
- ESPORTS LBank -> MEXC scanner-only: 2,500 USDT 4/4 positive, avg +89.088 bps, min +72.064. 5,000 USDT was 0/4 positive, avg -199.662, min -229.905. Keep scanner cap at 2,500 and kill 5,000 current.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD 4/4 positive, avg +1,053.865 bps, min +1,049.290. 1,000 USD was 0/4 positive, avg -529.055. Keep cap at 500.
- ULTIMA MEXC -> KuCoin chain-proof-only: 5,000 USDT 4/4 positive, avg +364.068 bps, min +324.264 before chain proof. Keep `LATER`.
- GUA MEXC -> Gate pre-positioned-only: 1,000 USDT 4/4 positive, avg +43.522 bps, min +22.969; 2,500 USDT 0/4, avg -195.169. Keep only the 1,000 pre-positioned lower cap and monitor decay.

Previous 11:36-11:38 CST compact active watch refresh:

2026-05-29 11:36-11:38 CST, compact active watch refresh.

Previous 11:29-11:31 CST lower-cap retest:

2026-05-29 11:29-11:31 CST, lower-cap retest after the 11:06 active refresh degraded VANRY USDC and GUA.

- VANRY MEXC -> Binance USDC: 2,500 USDC 4/4 positive after the 80 VANRY fee, avg +944.584 bps, min +917.416. Restore 2,500 USDC as the firm measurement cap. 5,000 USDC was 4/4 positive, avg +180.869, min +17.544, but keep 5,000 live-threshold-only because it had a negative tail in the prior active refresh.
- GUA MEXC -> Gate pre-positioned-only: 500 USDT 4/4 positive, avg +494.485 bps, min +380.031; 1,000 USDT 4/4 positive, avg +331.502, min +139.719; 2,500 USDT only 2/4 positive, avg -11.679, min -132.673. Restore only a 1,000 USDT pre-positioned lower cap while Gate deposits remain disabled.

Previous 11:06-11:09 CST active refresh:

2026-05-29 11:06-11:09 CST, 4 active samples with six-second spacing. The route set expanded to include ESPORTS LBank -> MEXC and ENJ Kraken -> Bitstamp. VANRY rows include the 80 VANRY MEXC ETH/ERC20 withdrawal fee; ESPORTS includes the LBank `4.6915` ESPORTS fee; ENJ excludes transfer because it is chain-mismatch blocked.

- VANRY MEXC -> Binance USDT: 10,000 USDT 4/4 positive after withdrawal fee, avg +279.010 bps, min +209.416. Keep firm public-book cap at 10,000 USDT for non-U.S. compliant account setups.
- VANRY MEXC -> KuCoin USDT: 5,000 USDT 4/4 positive after withdrawal fee, avg +240.279 bps, min +134.193. Keep 5,000 USDT as the current cap.
- VANRY MEXC -> Binance USDC: 5,000 USDC only 3/4 positive after withdrawal fee, avg +228.828 bps, min -32.644. Kill current 5,000 USDC cap; retest 2,500 before restoring.
- GUA MEXC -> Gate pre-positioned-only: 2,500 USDT only 3/4 positive after exact Gate 20 bps pair fee, avg +168.507 bps, min -64.011. 5,000 was 1/4 positive, avg -357.768. Kill the current firm GUA caps until lower buckets are retested.
- ULTIMA MEXC -> KuCoin: 5,000 USDT was 4/4 positive, avg +322.931 bps, min +162.210 before chain proof. Keep as `LATER` chain-proof-only.
- ESPORTS LBank -> MEXC scanner-only: 2,500 USDT 4/4 positive, avg +243.315 bps, min +221.900 after conservative fees and the LBank withdrawal fee. 5,000 was also 4/4 positive but thin, min +19.854; keep firm scanner cap at 2,500 due transfer-status/account blockers.
- ENJ Kraken -> Bitstamp scanner-only: 500 USD 4/4 positive, avg +1,095.851 bps, min +1,088.802. 1,000 USD was 0/4 positive, avg -169.338. Keep cap at 500 USD and chain-mismatch blocked.

Previous 10:34-10:36 CST refresh:

- VANRY MEXC -> Binance USDT: 10,000 USDT 8/8 positive after withdrawal fee, avg +270.132 bps, median +298.558, min +106.909. Keep firm public-book cap at 10,000 USDT for non-U.S. compliant account setups.
- VANRY MEXC -> KuCoin USDT: 5,000 USDT 8/8 positive after withdrawal fee, avg +238.039 bps, median +261.240, min +76.284. Restore 5,000 USDT as the current cap, but keep tail-risk monitoring because the prior refresh had a negative print.
- VANRY MEXC -> Binance USDC: 5,000 USDC 8/8 positive after withdrawal fee, avg +595.583 bps, median +567.803, min +197.250. Restore the measurement cap to 5,000 USDC.
- GUA MEXC -> Gate pre-positioned-only: 2,500 USDT 8/8 positive after exact Gate 20 bps pair fee, avg +354.473 bps, median +365.543, min +244.780. 5,000 was only 6/8 positive with min -50.063. Keep cap at 2,500 USDT and only for pre-positioned Gate inventory.
- ATLA MEXC -> BitMart: 250/500/1,000 USDT were all 0/8 positive; 500 averaged -170.470 bps. Kill current ATLA until rediscovered.
- ULTIMA MEXC -> KuCoin: 2,500 USDT was 8/8 positive, avg +448.475 bps, min +424.615 before chain proof. Keep as `LATER` chain-proof-only; do not promote repeatable execution or restore 5,000/10,000.

## Latest Event-Window Depth Pass

2026-05-29 12:13-12:15 CST, fresh event-window sampler across the existing no-key venue set excluding recent watchlist/kill bases and known false positives.

- Discovery pass: three top-of-book samples across 10,122 markets per sample, zero endpoint errors after excluding Bitso for speed.
- Persistent filtered rows: 83 after current watchlist/recent false-positive exclusions. Top clusters were known traps: RWA Gate/MEXC/Bitget -> KuCoin same-ticker collision and AI Binance/Gate -> KuCoin/MEXC/OKX identity conflict.
- Depth checked the next tier: REACT KuCoin -> Gate was positive only at 50-100 USDT and negative by 250; GHX Gate/KuCoin -> MEXC stayed positive through 500 but flipped negative by 1,000; LOFI, EQTY, MODE, KARRAT, CTA, ITHACA, and PIN were negative from 50 or failed sell depth; BRISE and LONG were positive only at 50-100.
- Action: no promotion. Add this pass to the kill list; keep event-window threshold at meaningful 1,000+ USDT depth after exact fees.

Previous 11:55-11:58 CST event-window sampler:

2026-05-29 11:55-11:58 CST, fresh event-window sampler across the existing no-key venue set excluding recent watchlist/kill bases and known false positives.

Previous 11:15-11:28 CST event-window sampler:

2026-05-29 11:15-11:28 CST, fresh event-window sampler across the existing no-key venue set excluding recent watchlist/kill bases.

Previous 10:23-10:33 CST strict new-name refresh:

- First pass ran three samples across 11,820 markets but missed BitMart due to parser shape; it mostly resurfaced already killed BTR/HOOLI/PHB/MAPO and HTX no-depth rows.
- Corrected pass ran two samples across 11,231 markets with BitMart parsed correctly and zero endpoint errors.
- Best corrected top rows were OWL, CELL, WEXO, MAGA, ARRR, MEY, ORAI, NAKA, ESE, KAIO, CHIRP, TBK, WPAY, BEAT, and ID.
- Depth killed actionable size: no row stayed positive at 1,000 USDT. CELL/WEXO were positive only through 100; WPAY only through 500 with thin +16.940 bps before transfer; ARRR failed persistence above 100 after exact Gate pair fee.
- ARRR Gate -> MEXC after Gate 20 bps + MEXC 5 bps + 2 bps latency: 100 USDT 6/6 positive avg +120.727 bps, 250 USDT 1/6 positive avg -14.114, 500/1,000 USDT 0/6 positive.
- Action: `KILL` current new-name refresh; add these bases to processed exclusions unless they reappear with positive 1,000+ USDT depth after exact pair fees.

Previous 09:59-10:04 CST event-window pass:

- Scope: four top-of-book samples across 12,290-12,928 markets, excluding the current watchlist and many processed bases. Two early Bitget ticker reads timed out; later samples succeeded.
- Most persistent positives were known HTX traps: ONE/MTL/CETUS/US/CARV/ZEC and related rows. Do not promote without fresh transfer-status proof.
- Depth killed plausible survivors at meaningful size: DAG negative by 250-500 USDT, DGB/ETHW/ZEN negative by 100-250 or worse, and GENIUS negative by 500-1,000 depending on sell venue.
- ATLA MEXC -> BitMart is the only micro survivor: 500 USDT 6/6 positive avg +54.386 bps, min +44.291 before transfer. 1,000 had a negative tail and 2,500 was 0/6 positive.
- ATLA action: `MEASURE` at 500 USDT only, pending MEXC withdrawal status/fee.

## Latest Liquid Static Refresh

2026-05-29 12:11 CST, 10,204 public markets across the existing venue set, zero endpoint errors.

- There were no positive sane priority top-of-book rows after generic fees/latency. Best rows were already negative: BTC Crypto.com -> Bitfinex USD -2.237 bps, XRP Crypto.com -> Bitfinex -3.212, SOL Crypto.com -> Bitfinex -4.133, LTC Crypto.com -> Bitfinex -4.200, and ETH Crypto.com -> Bitfinex -4.646.
- Best USDT rows were also negative: TON MEXC -> Bitget -11.398 bps, SUI Gate -> MEXC -11.536, APT Bitget -> MEXC -11.715, HBAR Crypto.com -> MEXC -11.895, and XLM MEXC -> Bybit/Bitget -12.394.
- No depth work justified because the first ranking layer was negative.
- Do not prioritize liquid static taker routes unless the first book-walk pass is positive; this path remains a regression monitor only.

## Latest Venue Expansion

2026-05-29 10:41-10:46 CST, BingX/LBank public spot expansion.

- Added BingX and LBank smoke adapters. BingX returned 883 parsed markets with bid/ask and depth. LBank returned 976 parsed markets, but the all-ticker endpoint lacks bid/ask, so LBank must be order-book-first for scoring.
- Integrated scan size: 12,006 markets. Endpoint errors: 0.
- Non-ESPORTS rows killed: RAVE into KuCoin has deposits disabled; RAVE into BitMart/BingX lacks a repeatable deposit path or has venue max-notional limits; KAT -> BingX is negative by 1,000; CAS/TOWER/PUSS/YEE/DHN/POD/KELLYCLAUDE/KAIO/AI4 failed depth.
- New scanner-only `MEASURE`: ESPORTS LBank -> MEXC, 2,500 USDT cap before final transfer/account proof. Persistence after LBank withdrawal fee: 1,000 USDT 6/6 positive avg +305.079 bps; 2,500 6/6 avg +177.340, min +41.913; 5,000 only 4/6 and avg -25.452; 10,000 0/6.
- Operational blocker: LBank withdrawal config says ESPORTS BEP20 withdrawal is enabled, but official LBank notice says ESPORTS deposits/withdrawals were suspended on 2026-05-25. Resolve this conflict in logged-in LBank before execution work.
- Account/region blocker: official LBank and BingX materials exclude U.S.-resident users; treat these adapters as non-U.S.-compliant-account-only unless Pedro proves a lawful account setup.
- Keep BingX/LBank adapters `LATER` but useful; add hard gates for LBank order-book-first ranking, LBank contract identity, live destination deposit status, and non-U.S. account/region eligibility.

Previous CoinEx expansion at 09:43-09:45 CST:

- Added 1,080 online CoinEx markets with public bid/ask and per-market taker fees.
- Integrated scan size was 11,202 markets across CoinEx plus the existing public venues.
- CoinEx-involved sane positives after fees/latency/liquidity filters: 0.

## Latest Funding Refresh

2026-05-29 12:11 CST, `scripts/funding_probe.py` scheduled refresh.

- Data returned: Binance 14 routes, Bybit 14, OKX 14, Coinbase INTX 5. Endpoint errors: 0.
- Best one-period proxy: Coinbase INTX SOL -7.932 bps. Next: Coinbase INTX BTC -8.328, DOGE -8.888, ETH -9.443, XRP -9.679, Bybit WLD -14.551, OKX TRX -16.123, OKX WLD -16.725, Bybit TRX -17.725, and Binance TRX -18.480.
- No immediate funding promotion; keep scheduled monitor only.

## Latest Bitso MXN Refresh

2026-05-29 12:10 CST, public Bitso tickers.

- USD/MXN bid/ask: 17.332/17.333. USDT/MXN: 17.317/17.318. PYUSD/MXN: 17.365/17.428.
- Best stable comparison: PYUSD/MXN sell bid vs USD/MXN ask -81.472 bps net after two fees.
- USDT/MXN comparisons were -91.747 and -108.889 bps net.
- Crypto/MXN implied basis stayed negative after three fees: XRP sell-MXN-vs-USD-buy was best at -152.358 bps, followed by ETH -154.422 and BTC -154.926.
- No MXN-lane promotion.

## Latest U.S.-Available Refresh

2026-05-29 11:42-11:44 CST, Gemini-inclusive U.S.-available public-market pass across Coinbase Exchange, Binance.US, Kraken, Bitstamp, and Gemini.

- Markets checked: 1,904 usable bid/ask markets: Coinbase 423, Binance.US 256, Kraken 771, Bitstamp 138, Gemini 316. Endpoint errors: 4, mostly harmless Coinbase 429/Gemini symbol-detail misses.
- Positive top-of-book rows after conservative fees were `LIT` Kraken -> Bitstamp, `VELO` Kraken -> Coinbase, `SUP` Kraken -> Coinbase, `OPG` Gemini -> Coinbase, `ENJ` Kraken -> Bitstamp, `MANA` into Bitstamp, and `INJ` into Gemini.
- No new U.S.-available promotion. `LIT`, `VELO`, and `SUP` are identity/ticker-collision traps. `ENJ` remains the existing 500 USD scanner-only chain-mismatch pocket. `MANA` remains killed by Bitstamp destination depth.
- The new Gemini `OPG` row is a parser false positive: Gemini per-symbol details for `opgusd` report base `OP`, quote `GUSD`, and contract price currency `GUSD`, while Coinbase `OPG` is Opengradient on Base. Treat this as `OP/GUSD`, not `OPG/USD`.
- Gemini/Bitstamp/Kraken/Coinbase `INJ/USD` looked positive at top of book, but executable depth killed it immediately: Bitstamp -> Gemini was -118.986 bps from 25-500 USD, Kraken -> Gemini was about -130 bps from the first bucket, and Coinbase -> Gemini was about -195 bps from the first bucket.
- Scanner action: add Gemini per-symbol metadata, reject GUSD symbols from USD-lane scoring unless explicitly modeled, and keep U.S.-available taker routes killed except the already-recorded ENJ 500 USD scanner-only watch.

Previous 11:32-11:34 CST Coinbase-inclusive pass:

2026-05-29 11:32-11:34 CST, Coinbase-inclusive U.S.-available public-market pass across Coinbase Exchange, Binance.US, Kraken, and Bitstamp.

- Markets checked: 1,311 usable bid/ask markets: Coinbase 165, Binance.US 256, Kraken 753, Bitstamp 137.
- Coinbase broker `best_bid_ask` is authenticated; this pass used concurrent no-key Coinbase Exchange ticker calls instead.
- Positive top-of-book rows after conservative fees: `LIT` Kraken -> Bitstamp, `VELO` Kraken -> Coinbase, `SUP` Kraken -> Coinbase, `ENJ` Kraken -> Bitstamp, `MANA` Kraken -> Bitstamp, and `MANA` Coinbase -> Bitstamp.
- `LIT`, `VELO`, and `SUP` are already killed ticker-collision/asset-migration traps. `ENJ` remains scanner-only and chain-mismatch blocked. `MANA` into Bitstamp is killed by destination depth.
- MANA Coinbase -> Bitstamp depth after Coinbase 120 bps, Bitstamp 40 bps, and 2 bps latency: 25 USD -1,619.081 bps, 100 USD -1,805.005, 250 USD -3,504.835, and Bitstamp bids exhausted by 500 USD.
- No U.S.-available promotion.

Previous 10:55-11:03 CST U.S.-available pass:

- Markets checked: 1,146 public markets with bid/ask from Binance.US 256, Bitstamp 137, and Kraken 753. Coinbase's no-key all-products endpoint returned products but blank bid/ask fields in this pass, so Coinbase was not included in route scoring.
- Positive top-of-book rows after fees: `LIT` Kraken -> Bitstamp, `ENJ` Kraken -> Bitstamp, and `MANA` Kraken -> Bitstamp.
- `ENJ` was the only scanner survivor, capped at 500 USD and chain-mismatch blocked.

Previous 10:15-10:20 CST bounded core-asset scan across Binance.US, Coinbase, Kraken, Gemini, and Bitstamp:

- Markets checked: 110 public core markets across USD/USDT/USDC.
- Positive top-of-book rows after fees: XLM/USD Kraken -> Binance.US +21.089 bps and XLM/USD Bitstamp -> Binance.US +19.488 bps.
- Depth killed both from 100 USD: Kraken -> Binance.US -124.181 bps; Bitstamp -> Binance.US -124.981 bps.
- No U.S.-available taker promotion.

## Latest Operational Metadata

Deposit-status sweep added 2026-05-29 12:01 CST:

- Gate deposits remain disabled for GUA, TBC, ESPORTS, RAVE, POWER, SWEAT, VRA, and ARTFI. TYCOON deposits are enabled on BSC, but the event-window depth pass already failed by 100-250 USDT.
- KuCoin deposits remain disabled for RAVE and HYDRA. KuCoin deposits are enabled for ULTIMA BEP20, IAG ADA, TOWER ERC20, and XMN SUI, but ULTIMA remains MEXC representation-mismatch blocked, IAG sell venue Bitget deposits are disabled, TOWER is contract-mismatch killed, and XMN is killed-current after fresh depth with MEXC's public 8 XMN withdrawal fee.
- Bitget deposits remain disabled for UPC, IAG, RAVE, BTR, and SUP. Bitget VELO deposits are enabled on BEP20, but the U.S. VELO row is a Kraken/Coinbase identity trap and not a Bitget route.
- No blocked high-value route moved from pre-positioned-only to repeatable transfer.

Region/account gate added 2026-05-29 07:21 CST:

- MEXC official restricted-jurisdiction page, updated Apr 17, 2026, lists the United States among prohibited jurisdictions and says MEXC does not accept user registrations or trading applications from those areas: `https://www.mexc.com/learn/article/mexc-restricted-countries-complete-list-of-prohibited-limited-regions/1?handleDefaultLocale=keep`.
- KuCoin Terms of Use, last updated Jan 29, 2026, require users to not be residents of or registered in restricted locations, and the restricted list includes the United States and U.S. territories: `https://www.kucoin.com/legal/terms-of-use`.
- Binance.US is not a VANRY fallback: `https://api.binance.us/api/v3/exchangeInfo?symbol=VANRYUSDT` and `VANRYUSDC` returned `{"code":-1121,"msg":"Invalid symbol."}`, the full Binance.US `exchangeInfo` response had 623 symbols and no `VANRY`, and the official Binance.US supported-crypto page contains no `VANRY`: `https://support.binance.us/hc/en-us/articles/360049417674-List-of-supported-cryptocurrencies`.
- Operational verdict: do not label any MEXC/KuCoin route execution-ready until Pedro confirms a compliant, non-U.S.-restricted account setup and live account UI/API access. The books can remain in scanner/watchlist mode.

Additional venue-region gate added 2026-05-29 10:52 CST:

- LBank's current user agreement says it does not provide services to personal accounts of U.S. residents or corporate accounts of entities located in, established in, or resident in the United States or Mainland China, and its restricted-jurisdiction list includes the United States: `https://www.lbank.com/support/articles/21436496711705`.
- BingX's Customer Agreement bars residents/passport holders of restricted jurisdictions, and its Disclaimer lists the United States, including U.S. territories and minor outlying islands, among restricted jurisdictions: `https://bingx.com/en/support/articles/12803820985231/` and `https://bingx.com/en/support/articles/11263347398927`.
- Operational verdict: LBank and BingX remain useful scanner venues, but no LBank/BingX route should be treated as execution-ready for a U.S.-resident setup.

MEXC public web coin metadata:

- VANRY: `coin/introduce?coinName=VANRY` reports `ct="ETH"` and Etherscan token `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`; this matches Binance/KuCoin ERC20 identity. Deposit/withdraw status and fee are still not exposed publicly.
- ULTIMA: `coin/introduce?coinName=ULTIMA` reports `ct="SMART"` and primary UltimaChain explorer, but also lists BSC explorer links for `0x5668a83B46016B494A30Dd14066A451E5417A8B8`, matching KuCoin BEP20. This reduces identity ambiguity but does not prove MEXC SMART/BEP20 withdrawal compatibility.
- BitMart official ULTIMA listing says token type `SMART` and links SMART explorer contract `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`: `https://bitmart.zendesk.com/hc/en-us/articles/32179256550427-Ultima-ULTIMA`.
- KuCoin official ULTIMA listing says deposits are supported on `BSC-BEP20`: `https://www.kucoin.com/announcement/ua-ultima-ultima-gets-listed-on-kucoin`.
- VANRY official announcement: MEXC said VANRY withdrawals opened Dec 2, 2023 15:00 UTC after the TVK swap and listed the same ERC20 contract. This is historical support evidence, not current fee/status.
- ULTIMA official announcement: MEXC said ULTIMA Mainnet deposits/withdrawals would be available starting Apr 29, 2025 14:00 UTC. This supports MEXC mainnet availability but keeps KuCoin BEP20 compatibility unresolved.
- MEXC fee-page API `https://www.mexc.com/api/platform/asset/api/coin/fee/rate/query` lists current VANRY rows: native Vanar fee `0.01`, min `0.02`; ETH/ERC20 fee `80`, min `200`; deposit fee `0`.
- The same MEXC fee-page API lists ULTIMA rows for `ULTIMA` and `SMART BLOCKCHAIN` only, not BEP20. This reinforces that ULTIMA -> KuCoin BEP20 is not repeatable without bridge/pre-positioned inventory.
- VANRY transfer-fee haircut is negligible at active sizes, but live depth still matters: latest refresh kept MEXC -> Binance 10,000 USDT and MEXC -> KuCoin 5,000 USDT positive after the 80 VANRY fee. VANRY USDC 5,000 remains rejected/live-threshold-only after another negative tail. Public-book caps are still account/region-gated.
- MEXC asset-page JavaScript exposes current deposit/withdraw status endpoints, but unauthenticated calls to the status/config endpoints return `401 Unauthorized`; VANRY's public coin id is `5e1d77a033064e60bfdbac3c93a9579f`. Current MEXC VANRY enabled flags require logged-in account-level verification.
- ATLA official MEXC listing article says deposits were opened and withdrawals were scheduled for 2025-08-18 08:00 UTC: `https://www.mexc.com/en-GB/support/articles/17827791529014`. MEXC exchange metadata currently shows `ATLAUSDT` spot trading allowed and no contract address, matching native ATLA style, but MEXC public coin/fee endpoints returned `Access Denied`; current withdrawal status/fee still requires logged-in verification.

## Earlier Loop Notes

1. Test the event-window hypothesis on `ALLO`, `GENIUS`, and `BSB`.
   - Run identity -> depth -> persistence for each.
   - Promote the approach if multiple symbols show short-lived positive windows.
   - Kill individual routes if their median net is negative or positive ratio is below 70%.
   - `ALLO`, `GENIUS`, `BSB`, `SD`, `CTR`, and `BDX` are now killed.

2. Convert the discovery lesson into scanner requirements.
   - Candidate output must include positive-ratio and median net by notional bucket.
   - Average net alone is misleading when a short spike dominates the sample.
   - Candidate output must use venue-specific fees; generic assumptions created false positives for Gate and Bitfinex.

3. Keep `IO/USDT` on watch as an event replay case.
   - It is the best observed proof that real-looking windows exist.
   - It is not a standing route after the window collapses.

4. Measure cross-exchange stablecoin/USD basis next.
   - Explicitly separate USD, USDT, USDC, and MXN lanes.
   - Do not rank Crypto.com -> Bitfinex USD routes until Bitfinex taker fee is verified instead of assumed zero.
   - Candidate must survive fees, conversion haircut, and depth.
   - USDT/USD and USDC/USD taker routes are now killed; revisit only with maker/rebate or stress-dislocation conditions.

## Next Loop

1. Convert empirical failures into scanner gates.
   - Same-symbol identity must be verified before route scoring.
   - Venue-specific fee metadata must be loaded before ranking.
   - Depth buckets must be computed before persistence sampling.
   - Median net and positive ratio must be shown beside average net.
   - Event-window decay must be measured; IO showed why averages can lie.

2. Run one more fresh discovery pass after documenting gates.
   - Ignore already killed symbols unless they reappear with materially different spread.
   - Prioritize only candidates with gross spread above known fee burden by at least 25 bps.
   - Treat Crypto.com -> Bitfinex as fee-model blocked until Bitfinex fee assumptions are corrected.
   - Latest public probe found `TBC` as a depth survivor, but Gate deposits are disabled, so it is not repeatable.

## Scanner Gate Backlog

1. Asset identity gate.
   - Same ticker is not enough.
   - Require official metadata/full name/contract address or curated mapping before route scoring.

2. Fee gate.
   - Venue-specific taker fees must be present.
   - Reject routes with unknown or placeholder fees.

3. Depth bucket gate.
   - Compute net bps at fixed notional buckets.
   - Do not rank top-of-book-only spreads.

4. Persistence gate.
   - Include positive ratio, median net, average net, min/max, and decay over time.
   - Reject candidates where median is negative even if average is positive.

5. Inventory gate.
   - Require quote inventory on buy venue and base inventory on sell venue.
   - Mark transfer-dependent routes as non-hot-path.

6. Lane gate.
   - Do not compare USD/USDT/USDC/MXN directly.
   - Require explicit conversion and haircut module for cross-lane candidates.

## Next Hypotheses

1. Maker/rebate version of triangular or stablecoin basis.
   - Only worth measuring if public fee schedules show maker rebate or near-zero maker fee and the account can qualify.
   - Binance.US is the one low-fee venue worth keeping in discovery, but the 07:29 U.S.-available static taker scan found no promotion.
   - 07:34 fee check killed immediate maker/rebate rescue: Binance.US 0 maker helps but is not enough by itself; Kraken/Coinbase rebate paths require high-volume or program eligibility.

2. CEX-DEX route measurability.
   - Only if public pool quotes can be pulled quickly for the same assets as the CEX event-window candidates.
   - ParaSwap public quotes make WETH/USDC measurable; current route is negative but monitorable.

3. Continue event-window scans.
   - Re-run hard-filter discovery periodically.
   - Promote only routes that survive identity, fee, depth, and persistence gates.
   - Latest fresh pass found `HOOLI/USDT`; killed after correct Gate fee and depth.

## Venue Expansion Notes

1. Binance.US should be treated as a separate venue from Binance global.
   - Public API base: `https://api.binance.us/api/v3/`.
   - Fee source: `https://blog.binance.us/zero-fee-trading/`.
   - Current advertised fees: 0 bps maker, 2 bps taker on Advanced Spot pairs.
   - Priority: add public discovery first; live trading requires U.S. account availability and balances.

2. CEX-DEX monitor should start with ETH/USDC only.
   - Public quote source tested: `https://api.paraswap.io/prices/`.
   - Required fields: destAmount, gasCostUSD, route source.
   - Reject unless net remains positive after CEX fee, gas, slippage, and MEV buffer.

## Fee-Aware Discovery Requirement

Before the next event-window scan is trusted:

1. Gate routes must use `GET /api/v4/spot/currency_pairs/{pair}` and its `fee` field before ranking.
2. Bitfinex routes must not use `0.0` bps taker; mark fee as unknown or use a conservative public tier.
3. KuCoin symbols should use `feeCategory` as a risk flag; route scoring must not assume all KuCoin symbols have the same fee tier.
4. Rankings should include both generic and venue-specific fee source labels so false positives are visible.
5. Preserve zero bps venue-specific fees as real values. The current ad hoc discovery helper treated MEXC `takerCommission: 0` on `VANRYUSDC` as missing and fell back to 5 bps.

## ULTIMA Follow-Up

1. Keep `ULTIMA/USDT` MEXC -> KuCoin at the top of Agent 2 watchlist.
   - It survived two 60-sample persistence windows and two 30-sample watch windows.
   - 500-5,000 USDT buckets were 100% positive in all four windows.
   - Latest 20-sample refresh had 5,000 USDT 20/20 positive, avg +225.097 bps.
   - Latest 20-sample refresh had 10,000 USDT only 15/20 positive, avg +26.957 bps, min -146.025 bps.
   - New 2026-05-29 05:11:58-05:14:34 CST refresh had 5,000 USDT 20/20 positive, avg +280.773 bps, min +274.943 bps.
   - The same refresh had 10,000 USDT 20/20 positive, avg +129.771 bps, min +125.464 bps.
   - Targeted 2026-05-29 05:17:36-05:20:05 CST confirmation had 5,000 USDT 30/30 positive, avg +300.533 bps, min +294.818 bps.
   - The same confirmation had 10,000 USDT 30/30 positive, avg +145.404 bps, min +140.081 bps.
   - New 2026-05-29 05:33:43-05:36:14 CST refresh had 10,000 USDT 20/20 positive, avg +175.212 bps, min +104.929 bps.
   - New 2026-05-29 05:50:09-05:52:31 CST refresh had 10,000 USDT 20/20 positive, avg +184.409 bps, min +138.382 bps.
   - New 2026-05-29 06:23:09-06:26:10 CST refresh kept 5,000 USDT 20/20 positive, avg +413.193 bps, min +248.627 bps, but 10,000 USDT degraded to 18/20 positive with min -134.628 bps.
   - New 2026-05-29 06:48:35-06:50:59 CST refresh kept 5,000 USDT 20/20 positive, avg +424.332 bps, min +326.369 bps; 10,000 USDT improved to 20/20 positive, avg +188.336 bps, min +111.057 bps.
   - New 2026-05-29 07:03:53-07:06:17 CST refresh kept 5,000 USDT 20/20 positive, avg +386.570 bps, min +319.192 bps; 10,000 USDT also stayed 20/20 positive, avg +156.310 bps, min +87.097 bps.
   - New 2026-05-29 07:17:53-07:20:54 CST refresh kept 5,000 USDT 20/20 positive, avg +452.052 bps, min +322.974 bps; 10,000 USDT slipped to 19/20 positive, avg +210.970 bps, min -9.418 bps.
   - New 2026-05-29 07:36:10-07:39:15 CST refresh kept 5,000 USDT 20/20 positive, avg +427.839 bps, min +329.718 bps; 10,000 USDT recovered to 20/20 positive, avg +159.973 bps, min +36.634 bps.
   - New 2026-05-29 07:50:48-07:53:52 CST refresh kept 5,000 USDT 20/20 positive, avg +418.842 bps, min +347.424 bps; 10,000 USDT stayed 20/20 positive, avg +172.344 bps, min +124.205 bps.
   - Treat as scanner/actionability research, not live-trading permission.
   - Public-book scanner/watch cap is back to 10,000 USDT after two clean windows following the prior negative tail. This is not execution permission; chain/rebalance proof is still required.
   - Live execution remains blocked until chain/rebalance compatibility and sell-venue inventory are proven.

2. Verify operational feasibility before any execution work.
   - MEXC metadata contract: `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.
   - MEXC web coin metadata reports chain type `SMART`, primary explorer `https://ultimachain.info/`, and also lists BSC explorer links for KuCoin's BEP20 contract `0x5668a83B46016B494A30Dd14066A451E5417A8B8`.
   - MEXC official announcement says ULTIMA Mainnet deposits/withdrawals became available Apr 29, 2025 14:00 UTC.
   - MEXC public fee API lists ULTIMA and SMART BLOCKCHAIN rows only; it does not list BEP20.
   - Gate SMART chain also points to `sWd6JcnEA3QJdh3zK1NHchyU2j4cEsiUdi`.
   - KuCoin deposit/withdraw endpoint shows BEP20 contract `0x5668a83b46016b494a30dd14066a451e5417a8b8`.
   - KuCoin public endpoint shows BEP20 deposits and withdrawals enabled.
   - Gate public endpoint shows SMART deposits and withdrawals enabled.
   - MEXC deposit/withdraw status was not publicly verified in this run.
   - Rechecked at 2026-05-29 05:23 CST: MEXC capital config is key-gated; public status remains unverified.
   - Need to prove whether SMART and BEP20 are bridge-compatible representations of the same asset and whether MEXC supports the required withdrawal path.

3. Required next measurement.
   - Continue periodic persistence windows later.
   - Record staleness fields where possible: KuCoin book timestamp is available, but current local clock skew made absolute age unreliable; MEXC public depth did not expose an exchange timestamp.
   - Record REST round-trip time as a fallback staleness proxy.
   - Track 500, 1,000, 2,500, 5,000, and 10,000 USDT buckets.

4. Stop condition.
   - Kill or downgrade if chain compatibility cannot be verified, deposits/withdrawals are disabled, or the 5,000 USDT bucket drops below 70% positive.

5. Execution-readiness checklist for ULTIMA.
   - Account access available on MEXC and KuCoin.
   - USDT inventory on MEXC.
   - ULTIMA inventory already on KuCoin.
   - MEXC buy-side order size complies with quote precision and max quote amount.
   - KuCoin sell-side order size complies with base increment and min funds.
   - Rebalance plan exists for MEXC SMART/BEP20 mismatch before any repeated strategy is considered.

## VANRY Follow-Up

1. Keep `VANRY/USDT` at the top of Agent 2 watchlist.
   - MEXC -> Binance survived 30/30 samples positive through 10,000 USDT.
   - Latest 20-sample refresh had MEXC -> Binance 10,000 USDT 20/20 positive, avg +276.935 bps, min +211.850 bps.
   - MEXC -> KuCoin survived 30/30 samples positive through 5,000 USDT and failed at 10,000 USDT.
   - Latest 20-sample refresh had MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +167.085 bps.
   - New 2026-05-29 05:11:58-05:14:34 CST refresh had MEXC -> Binance 10,000 USDT 20/20 positive, avg +220.249 bps, min +111.804 bps.
   - The same refresh had MEXC -> KuCoin 5,000 USDT 19/20 positive, avg +117.878 bps, min -22.662 bps.
   - Targeted 2026-05-29 05:17:36-05:20:05 CST confirmation had MEXC -> KuCoin 2,500 USDT 30/30 positive, avg +507.283 bps, min +318.907 bps.
   - The same confirmation had MEXC -> KuCoin 5,000 USDT 29/30 positive, avg +171.561 bps, min -1.653 bps.
   - New 2026-05-29 05:33:43-05:36:14 CST refresh had MEXC -> Binance 10,000 USDT 20/20 positive, avg +199.935 bps, min +100.148 bps.
   - The same refresh had MEXC -> KuCoin 5,000 USDT 19/19 positive, avg +88.318 bps, min +3.113 bps after one KuCoin timeout.
   - New 2026-05-29 05:50:09-05:52:31 CST refresh had MEXC -> Binance 10,000 USDT 20/20 positive, avg +242.131 bps, min +155.345 bps.
   - The same refresh had MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +118.634 bps, min +3.898 bps.
   - New 2026-05-29 06:06:31-06:09:33 CST refresh had MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +325.173 bps, min +205.403 bps.
   - New 2026-05-29 06:23:09-06:26:10 CST refresh had MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +320.221 bps, min +171.396 bps.
   - New 2026-05-29 06:48:35-06:50:59 CST refresh, after the 80 VANRY MEXC withdrawal fee, had MEXC -> Binance 10,000 USDT 20/20 positive, avg +288.674 bps, min +186.532 bps; MEXC -> KuCoin 2,500 USDT 20/20 positive, avg +531.164 bps, min +389.500 bps; MEXC -> KuCoin 5,000 USDT 19/20 positive, min -6.995 bps.
   - New 2026-05-29 07:03:53-07:06:17 CST refresh, after the 80 VANRY MEXC withdrawal fee, had MEXC -> Binance 10,000 USDT 20/20 positive, avg +247.835 bps, min +166.938 bps; MEXC -> KuCoin 2,500 USDT 20/20 positive, avg +497.716 bps, min +418.315 bps; MEXC -> KuCoin 5,000 USDT 20/20 positive, min +98.752 bps.
   - New 2026-05-29 07:17:53-07:20:54 CST refresh, after the 80 VANRY MEXC withdrawal fee, had MEXC -> Binance 10,000 USDT 20/20 positive, avg +335.844 bps, min +302.966 bps; MEXC -> KuCoin 2,500 USDT 20/20 positive, avg +571.989 bps, min +549.809 bps; MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +200.446 bps, min +167.040 bps.
   - New 2026-05-29 07:36:10-07:39:15 CST refresh, after the 80 VANRY MEXC withdrawal fee, had MEXC -> Binance 10,000 USDT 20/20 positive, avg +383.266 bps, min +313.524 bps; MEXC -> KuCoin 2,500 USDT 20/20 positive, avg +613.227 bps, min +549.855 bps; MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +264.939 bps, min +127.310 bps.
   - New 2026-05-29 07:50:48-07:53:52 CST refresh, after the 80 VANRY MEXC withdrawal fee, had MEXC -> Binance 10,000 USDT 20/20 positive, avg +329.739 bps, min +198.804 bps; MEXC -> KuCoin 2,500 USDT 20/20 positive, avg +678.036 bps, min +573.681 bps; MEXC -> KuCoin 5,000 USDT 20/20 positive, avg +338.403 bps, min +147.427 bps.
   - Current public-book watch caps for non-U.S. compliant setups after the 09:54 refresh: 10,000 USDT firm for Binance sell leg; 2,500 USDT firm for KuCoin sell leg because 5,000 printed a negative tail.
   - Treat as scanner/actionability research, not live-trading permission.
   - U.S.-resident execution path is killed for now: MEXC is the buy venue and officially lists the United States as prohibited; KuCoin also lists the United States as restricted; Binance.US does not list VANRY.

2. Verify operational feasibility before any execution work.
   - MEXC metadata contract: `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`.
   - MEXC web coin metadata reports chain type `ETH` and Etherscan token `0x8DE5B80a0C1B02Fe4976851D030B36122dbb8624`.
   - MEXC official swap announcement says VANRY withdrawals opened Dec 2, 2023 15:00 UTC and lists the same ERC20 contract.
   - MEXC public fee API lists ETH/ERC20 deposits at fee `0`, withdrawal minimum `200` VANRY, and withdrawal fee `80` VANRY. Native Vanar is also listed with withdrawal minimum `0.02` and fee `0.01`.
   - MEXC public coin id for VANRY is `5e1d77a033064e60bfdbac3c93a9579f`.
   - MEXC asset-page status/config endpoints are account-gated: unauthenticated calls returned `401 Unauthorized`. Public-only work cannot prove current enabled flags beyond fee/minimum rows.
   - KuCoin ERC20 contract: `0x8de5b80a0c1b02fe4976851d030b36122dbb8624`; deposits/withdrawals enabled.
   - Binance public web asset metadata identifies asset code `VANRY`, asset name `Vanar`, trading enabled, old asset code `TVK`.
   - Binance public web asset endpoint confirms ERC20 parent `ETH`, deposits enabled, withdrawals enabled, withdrawal fee `65` VANRY, minimum withdrawal `130` VANRY.
   - KuCoin public endpoint confirms ERC20 deposits/withdrawals enabled, withdrawal fee `167` VANRY, withdrawal minimum `334` VANRY, deposit minimum `15` VANRY.
   - MEXC deposit/withdraw status was not publicly verified; capital config endpoint returned `api key required`.

3. Stop condition.
   - Kill or downgrade if Binance/KuCoin sell inventory cannot be pre-positioned, MEXC withdrawal path is unavailable, the 10,000 USDT Binance bucket drops below 70% positive, or the 5,000 USDT KuCoin bucket drops below 70% positive.

4. Execution-readiness checklist for VANRY.
   - Account access available on MEXC and Binance or KuCoin.
   - Logged-in MEXC UI/API read confirms VANRY ETH/ERC20 deposit and withdrawal are currently enabled.
   - USDT inventory on MEXC.
   - USDC inventory on MEXC if enabling the USDC lane.
   - VANRY inventory already on Binance or KuCoin.
   - MEXC buy-side order size complies with precision/max quote.
   - Binance/KuCoin sell-side order size complies with lot size/min notional.
   - Rebalance plan exists before repeated strategy is considered.

5. USDC lane.
   - MEXC -> Binance `VANRYUSDC` survived 20/20 positive at 1,000 and 2,500 USDC.
   - 5,000 USDC was 18/20 positive but had a negative tail; do not promote above 2,500 USDC yet.
   - 10,000 USDC was 3/20 positive and should stay rejected.
   - New 2026-05-29 05:11:58-05:14:34 CST refresh had 2,500 USDC 20/20 positive, avg +747.947 bps, min +551.253 bps.
   - The same refresh had 5,000 USDC 20/20 positive, avg +514.622 bps, min +50.598 bps.
   - Targeted 2026-05-29 05:17:36-05:20:05 CST confirmation had 2,500 USDC 30/30 positive, avg +731.160 bps, min +270.968 bps.
   - The same confirmation had 5,000 USDC only 26/30 positive with min -464.123 bps, and 10,000 USDC only 2/30 positive.
   - New 2026-05-29 05:33:43-05:36:14 CST refresh had 2,500 USDC 20/20 positive, avg +705.950 bps, min +542.378 bps.
   - The same refresh had 5,000 USDC only 18/20 positive with min -127.744 bps.
   - New 2026-05-29 05:50:09-05:52:31 CST refresh had 2,500 USDC 20/20 positive, avg +702.884 bps, min +541.989 bps.
   - The same refresh had 5,000 USDC 20/20 positive, avg +448.729 bps, min +74.765 bps.
   - New 2026-05-29 06:06:31-06:09:33 CST refresh, using real MEXC zero taker fee, had 5,000 USDC 20/20 positive, avg +620.881 bps, min +193.250 bps.
   - New 2026-05-29 06:23:09-06:26:10 CST refresh had 5,000 USDC 20/20 positive, avg +679.794 bps, min +342.530 bps.
   - New 2026-05-29 06:48:35-06:50:59 CST refresh, after the 80 VANRY MEXC withdrawal fee, had 2,500 USDC 20/20 positive, avg +840.004 bps, min +628.647 bps; 5,000 USDC degraded to 19/20 positive with min -39.902 bps.
   - New 2026-05-29 07:03:53-07:06:17 CST refresh, after the 80 VANRY MEXC withdrawal fee, had 2,500 USDC 20/20 positive, avg +777.271 bps, min +696.118 bps; 5,000 USDC recovered to 20/20 positive but with thin min +35.959 bps.
   - New 2026-05-29 07:17:53-07:20:54 CST refresh, after the 80 VANRY MEXC withdrawal fee, had 2,500 USDC 20/20 positive, avg +858.697 bps, min +826.696 bps; 5,000 USDC also stayed 20/20 positive, avg +659.351 bps, min +395.431 bps.
   - New 2026-05-29 07:36:10-07:39:15 CST refresh, after the 80 VANRY MEXC withdrawal fee, had 2,500 USDC 20/20 positive, avg +903.328 bps, min +806.101 bps; 5,000 USDC also stayed 20/20 positive, avg +458.736 bps, min +52.608 bps.
   - New 2026-05-29 07:50:48-07:53:52 CST refresh, after the 80 VANRY MEXC withdrawal fee, had 2,500 USDC 20/20 positive, avg +870.145 bps, min +705.368 bps; 5,000 USDC degraded to 19/20 positive, avg +569.820 bps, min -240.917 bps.
   - New 2026-05-29 08:33:56-08:35:42 CST refresh, after the 80 VANRY MEXC withdrawal fee, had 2,500 USDC 20/20 positive, avg +1036.801 bps, min +951.777 bps; 5,000 USDC recovered to 20/20 positive, avg +735.275 bps, min +265.036 bps.
   - Current firm measurement cap is 2,500 USDC for non-U.S. compliant setups; 5,000 USDC is live-threshold-only until another clean window follows the 08:19 negative tail.

## Non-Gate Candidate Queue

The latest fee-aware non-Gate queue is exhausted.

1. `EUL/USDT` Binance <-> KuCoin: killed after negative depth in both directions.
2. `GOMINING/USDT` Bitget -> MEXC: persisted only at 50-250 USDT; keep as `LATER` regression case, kill as execution priority.
3. `CPOOL/USDT` Bybit <-> KuCoin: killed after negative depth in both directions.
4. `DAG/USDT` MEXC <-> KuCoin: killed after negative depth and MEXC `isSpotTradingAllowed=false`.

Do not hand-pick another ticker from the same stale ranking. Next event-window work should be a fresh fee-aware discovery pass with corrected Gate pair fees, conservative Bitfinex fees, and KuCoin fee-category risk labels.

## Fresh Discovery Queue

Latest corrected fee-aware discovery pass produced:

1. `VANRY/USDT` MEXC -> Binance/KuCoin: `DO_NOW` scanner/watchlist, but execution is account/region gated.
2. `VANRY/USDC` MEXC -> Binance: `MEASURE`, firm public-book measurement cap 2,500 USDC for non-U.S. compliant setups; 5,000 USDC recovered at 08:36 but needs another clean window after the 08:19 negative-tail refresh.
3. `BTR/USDT` MEXC -> Bitget: `KILL`, public contract mismatch and Bitget deposits disabled.
4. `HOOLI/USDT` MEXC -> Bitget: `KILL`, Bitget deposits disabled despite matching SOL contract.
5. `GUA/USDT` MEXC -> Gate: `KILL` repeatable transfer while Gate deposits are disabled; `LATER` only for pre-positioned Gate inventory after the 09:38 depth pass showed +209.824 bps at 2,500 USDT before transfer.
6. `QAIT/USDT` MEXC/KuCoin -> Gate: `KILL`, no meaningful depth.
7. `PHB/USDT` MEXC -> Gate: `KILL`, Gate deposits disabled.
8. `AI/USDT` Gate/Binance vs MEXC/KuCoin/OKX: `KILL`, Sleepless AI vs Gensyn ticker collision.
9. `ESPORTS/USDT` KuCoin -> Bitget: `KILL`, both venues report deposits disabled despite clean BEP20 identity and large positive depth.
10. `BTR/USDT` MEXC -> Bitget: `KILL`, public contract mismatch and Bitget deposits disabled.
11. `HOOLI/USDT` MEXC -> Bitget: `KILL`, Bitget deposits disabled despite matching SOL contract.
12. `SWEAT/USDT` MEXC/Bitget -> Gate: `KILL`, Gate deposits disabled.
13. `SPARKLET/USDT` MEXC -> Gate: `KILL`, micro edge dies by 1,000 USDT and is too small after rebalance overhead.
14. `SNEK/USDT` KuCoin/MEXC -> Bitget/Gate: `KILL`, positive only below 500 USDT and transfer fee wipes the pocket.
15. `COQ/USDT` KuCoin -> MEXC/Gate: `KILL`, negative after live depth even at 50 USDT.
16. `VOOI/USDT` MEXC/KuCoin/Gate -> Bybit: `KILL`, positive only at 50-100 USDT and negative by 250 USDT; Bybit network status key-gated.
17. `RAVE/USDT` Bitget -> Gate/KuCoin: `KILL`, destination deposits disabled.
18. `UPC/USDT` MEXC -> Bitget: `KILL`, Bitget deposits disabled.
19. `RWA/USDT` Gate/MEXC -> KuCoin: `KILL`, Allo vs RWA Inc ticker collision.
20. `TOWER/USDT` MEXC -> KuCoin: `KILL`, contract mismatch.
21. `ARRR/USDT` Gate -> MEXC: `KILL`, positive only at 50 USDT and negative by 100 USDT.
22. `XMN/USDT` MEXC -> KuCoin: `LATER`, 500 USDT micro pocket but not execution-ready.
23. `SWCH/USDT` Gate -> MEXC: `KILL`, MEXC spot trading not allowed.
24. `CWEB/USDT` KuCoin -> MEXC: `KILL`, positive only below 500 USDT and KuCoin withdrawal fee wipes the pocket.
25. `GHX/USDT` Gate/KuCoin -> MEXC: `KILL`, positive only at tiny size and negative by 500 USDT.
26. `BBT/USDT` MEXC -> Gate: `KILL`, MEXC spot trading not allowed.
27. `IMT/USDT` Gate -> MEXC: `KILL`, negative after live depth even at 50 USDT.
28. `SIX/USDT` MEXC -> Gate: `KILL`, contract mismatch.
29. `REACT/USDT` KuCoin -> Gate: `KILL`, matching ERC20 withdrawal disabled on KuCoin.
30. `PYBOBO/USDT` MEXC -> Bybit: `KILL`, positive only at 50-100 USDT and negative by 250 USDT.
31. `WBAI/USDT` KuCoin -> MEXC: `KILL`, negative after live depth even at 50 USDT.
32. `MAPO/USDT` MEXC/KuCoin -> Bitget: `KILL`, Bitget deposits/withdrawals disabled and KuCoin deposits disabled.
33. `CTA/USDT` Bybit -> KuCoin: `KILL`, negative after live depth even at 50 USDT.
34. `ALEX/USDT` KuCoin -> MEXC: `KILL`, positive only at 50-100 USDT and negative by 250 USDT.
35. `DEVVE/USDT` Gate -> MEXC: `KILL`, positive only at 50 USDT and negative by 100 USDT.
36. `TYCOON/USDT` Gate -> MEXC: `KILL`, MEXC spot trading not allowed.
37. `EPIC/USDT` Gate -> MEXC/Binance: `KILL`, clean identity but negative executable depth even at 50 USDT.
38. `SXT/USDT` Bybit -> MEXC/Binance/KuCoin/Bitget/Gate: `KILL`, only Bybit -> MEXC is positive at 50-100 USDT and it is negative by 250 USDT.
39. `CHIRP/USDT` MEXC -> KuCoin: `KILL`, positive only at 50 USDT and negative by 100 USDT.
40. `GAMEVIRTUAL/USDT` Gate -> MEXC: `KILL`, clean Base identity but negative from 50 USDT.
41. `AFC/USDT` MEXC -> Bybit: `KILL`, negative from 50 USDT; Bybit transfer status not worth chasing.
42. `LKI/USDT` MEXC -> KuCoin: `KILL`, matching BEP20 identity but deeply negative from 50 USDT.
43. `LYX/USDT` Gate -> KuCoin: `KILL`, positive only at 50-100 USDT and negative by 250 USDT.
44. `NOS/USDT` Gate -> MEXC: `KILL`, matching Solana identity but negative from 50 USDT.
45. `ID/USDT` MEXC -> Bybit: `KILL`, negative from 50 USDT; Bybit transfer status not worth chasing.
46. `SOUL/USDT` Gate -> KuCoin: `KILL`, negative from 50 USDT and chain labels are ambiguous.
47. `RIO/USDT` KuCoin -> MEXC: `KILL`, positive only at 50-100 USDT, negative by 250 USDT, identity ambiguous.
48. Fresh scan summary: 10,216 markets, 2,081 same-lane routes, 34 new filtered top-of-book candidates, 0 endpoint errors.
49. `DMTR/USDT` MEXC -> KuCoin: `KILL`, positive only below 1,000 USDT and KuCoin withdrawal fee wipes the pocket.
50. `WARD/USDT` Bitget/MEXC/KuCoin -> Gate: `KILL`, Gate BSC contract vs native Warden/no-contract buy venues.
51. `INSP/USDT` MEXC -> KuCoin: `KILL`, matching ERC20 identity but negative from 50 USDT.
52. `TX/USDT` Gate -> Bitget: `KILL`, compatible-looking TX metadata but negative from 50 USDT.
53. `SIN/USDT` KuCoin -> MEXC: `KILL`, matching BEP20 identity but negative from 50 USDT.
54. `STAY/USDT` MEXC -> KuCoin: `KILL`, positive only at 50 USDT and withdrawal fee wipes it.
55. `ASSET/USDT` KuCoin -> MEXC: `KILL`, positive only below 500 USDT and transfer fee consumes most edge.
56. `PIN/USDT` MEXC -> Gate: `KILL`, MEXC spot trading not allowed.
57. `GAIB/USDT` Bybit -> MEXC: `KILL`, barely positive at 50-100 USDT and negative by 250 USDT.
58. `HEART/USDT` KuCoin -> MEXC: `KILL`, negative from 50 USDT.
59. `BNKR/USDT` KuCoin/Gate -> MEXC: `KILL`, both routes negative from 50 USDT.
60. `ESE/USDT` MEXC -> Bybit/KuCoin: `KILL`, both sell routes negative from 50 USDT.
61. `RVV/USDT` Bitget -> MEXC: `KILL`, negative from 50 USDT.
62. `HEI/USDT` Binance -> MEXC: `KILL`, negative from 50 USDT.
63. `ROOBEE/USDT` Gate -> KuCoin: `KILL`, negative from 50 USDT.
64. `LAVA/USDT` Bybit -> MEXC: `KILL`, negative from 50 USDT.
65. `RMV/USDT` MEXC -> KuCoin: `KILL`, negative from 50 USDT.
66. `XELS/USDT` Gate -> MEXC: `KILL`, positive only at 50-100 USDT and negative by 250 USDT.
67. `IOTX/USDT` MEXC/Binance -> Gate: `KILL`, positive only at 50-100 USDT and negative by 250 USDT.
68. `HAI/USDT` KuCoin -> MEXC: `KILL`, negative from 50 USDT.
69. `LL/USDT` MEXC -> KuCoin: `KILL`, negative from 50 USDT.
70. `MCRT/USDT` Bybit -> MEXC: `KILL`, negative from 50 USDT.
71. `MSFTON/USDT` MEXC -> Bitget: `KILL`, identity clean but edge is too small for ERC20 transfer/rebalance and negative by 5,000 USDT.
72. `GXE/USDT` Gate -> MEXC: `KILL`, deeply negative from 50 USDT.
73. `IAUON/USDT` MEXC -> Gate: `KILL`, negative from 50 USDT.
74. `ZENT/USDT` Bybit -> OKX: `KILL`, negative from 50 USDT.
75. `HMSTR/USDT` Bitget -> Binance: `KILL`, negative from 50 USDT.
76. `SWFTC/USDT` MEXC -> OKX: `KILL`, negative from 50 USDT.
77. `ERG/USDT` Gate -> KuCoin: `KILL`, negative from 50 USDT.
78. Fresh exclusion scan summary: 10,216 markets, 2,048 same-lane routes, 14 filtered top-of-book route candidates, 0 endpoint errors, 0 promotions.
79. `BOS/USDT` KuCoin -> MEXC: `KILL`, matching ERC20 identity but positive only at 50 USDT and KuCoin withdrawal fee is 2,500 BOS.
80. `EGL1/USDT` KuCoin -> Bitget/Gate: `KILL`, positive only at 50 USDT and negative by 100-250 USDT.
81. `GROK/USDT` Gate -> MEXC: `KILL`, positive at 50-100 USDT but negative by 250 USDT.
82. `ETN/USDT` MEXC -> KuCoin: `KILL`, negative from 50 USDT.
83. `QKC/USDT` Binance/Gate -> MEXC: `KILL`, both routes negative from 50 USDT.
84. `UNION/USDT` MEXC -> Gate: `KILL`, negative from 50 USDT.
85. `JASMY/USDT` Binance/Bitget/Bybit/Crypto.com -> MEXC: `KILL`, initial positive batch did not persist; 20-sample retest had 0/20 positive on every Binance/Bitget/Bybit route and size.
86. `NYM/USDT` Bitget -> Bybit: `KILL`, positive only below 250 USDT.
87. `POKT/USDT` Gate -> KuCoin: `KILL`, deeply negative from 50 USDT.
88. Processed-base exclusion scan summary: 10,216 markets, 3,500 same-lane USDT/USDC keys, 110 processed bases excluded, 7 filtered top-of-book routes, 0 promotions.
89. `ACA/USDT` Gate -> MEXC: `KILL`, ticker looked positive but live depth was negative from 50 USDT.
90. `ES/USDT` Gate -> KuCoin/MEXC: `KILL`, Gate -> KuCoin positive only below 500 USDT; Gate -> MEXC negative from 50 USDT.
91. `IN/USDT` MEXC -> Bitget/KuCoin: `KILL`, both sell routes negative from 50 USDT.
92. `OBOL/USDT` Gate -> MEXC: `KILL`, negative from 50 USDT and sell depth exhausted by 2,500 USDT.
93. `SBUXON/USDT` Gate -> MEXC: `KILL`, tokenized-stock pocket positive only at 50-250 USDT and negative by 500 USDT.

The current discovery queue has no new repeatable-transfer promotion. Do not promote `XMN` above `LATER`. Current public-book watch caps for non-U.S. compliant setups are VANRY MEXC -> Binance 10,000 USDT, VANRY MEXC -> KuCoin 5,000 USDT, VANRY MEXC -> Binance 5,000 USDC measurement, and GUA MEXC -> Gate 2,500 USDT pre-positioned-only while Gate deposits are disabled. ULTIMA MEXC -> KuCoin recovered through 2,500 USDT but remains chain-proof-only; ATLA, ULTIMA 5,000/10,000, GUA 5,000, and SPX are killed for current execution. The U.S.-available static taker substitution scan is killed. The next best action is account/region proof first, then logged-in MEXC withdrawal status and GUA/ULTIMA chain-rebalance proof; if U.S.-only, shift to maker/rebate or event-window monitoring rather than static taker arb.

## HOOLI Follow-Up

1. `KILL` `HOOLI/USDT` as a repeatable route.
   - MEXC -> Bitget survived 20/20 samples positive through 500 USDT.
   - 1,000 USDT was 0/20 positive and deeply negative.
   - Bitget public coin endpoint reports the same SOL contract as MEXC, but deposits are disabled.

2. Stop condition.
   - Revisit only if Bitget deposits reopen and 500-1,000 USDT depth remains positive after fees.
   - Do not spend execution time here before VANRY and ULTIMA operational feasibility.

## BTR Follow-Up

1. `KILL` `BTR/USDT` MEXC -> Bitget.
   - MEXC -> Bitget survived 30/30 samples positive through 5,000 USDT.
   - Latest 20-sample refresh had 5,000 USDT 20/20 positive, avg +128.988 bps.
   - 10,000 USDT was 0/30 positive and deeply negative.
   - Latest 20-sample refresh also had 10,000 USDT 0/20 positive.
   - New 2026-05-29 05:11:58-05:14:34 CST refresh had 5,000 USDT 20/20 positive, avg +119.803 bps, min +98.886 bps.
   - The same refresh had 10,000 USDT 0/20 positive, avg -513.260 bps.
   - Bitget public coin endpoint reports ERC20 contract `0x6c76de483f1752ac8473e2b4983a873991e70da7`, which does not match MEXC `0x0e4cf4affdb72b39ea91fa726d291781cbd020bf`.
   - Bitget deposits are disabled.

2. Stop condition.
   - Revisit only if Bitget contract identity is reconciled with MEXC and deposits reopen.
   - Do not prioritize above VANRY or ULTIMA.

## Backlog

1. Add a market-identity validation layer to discovery.
   - Symbol equality is not enough.
   - Prefer official instrument metadata, status, and asset identifiers where venues expose them.

2. Add depth-aware candidate scoring.
   - Ticker top-of-book is only a prefilter.
   - Required output: net bps by notional bucket, not one headline spread.

3. Add funding monitor as a separate strategy class.
   - Track funding rate, mark-index basis, and estimated breakeven intervals.
   - Promote only when funding materially exceeds entry basis plus fees.
   - Latest 2026-05-29 06:56 CST refresh scanned 47 public routes with zero endpoint errors; best proxy was still Coinbase INTX BTC at -7.336 bps, so keep this below VANRY operational work.

4. Keep Bitso MXN monitoring but do not prioritize execution.
   - Trigger threshold: gross MXN/FX dislocation must exceed conservative fee + FX haircut by a wide margin.
   - Latest 2026-05-29 06:59 CST refresh: MXN -> USD -> USDT -> MXN -149.901 bps, reverse -151.290 bps after fees; best stable comparison -60.914 bps.

## Current Best Action For Pedro Tomorrow

Prioritize VANRY and ULTIMA operational due diligence plus automatic market discovery with strict rejection logic. BTR and HOOLI are dead reference cases for the scanner's identity/deposit gates; the highest-EV work is still proving whether the larger MEXC fragmentation routes can be made operational.
