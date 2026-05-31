# Exchange Fee Model

Checked: 2026-05-30.

The engine uses taker fees by default because the current arbitrage path buys at ask and sells at bid, which consumes liquidity. Maker fees only apply to future post-only/resting-order strategies.

Internal unit: `bps_x100`, where `1000 = 10 bps = 0.10%` and `675 = 6.75 bps = 0.0675%`.

## Defaults Used In Code

| Exchange | Default tier | Maker bps | Taker bps | Source |
|---|---:|---:|---:|---|
| Binance | Regular / VIP0 | 10 | 10 | https://www.binance.com/en/fee/trading |
| BitMEX Spot | Public spot instrument metadata | 5 | 5 | `GET /api/v1/instrument/active` |
| Bybit | VIP0 | 10 | 10 | https://www.bybit.com/en/help-center/article/Trading-Fee-Structure |
| OKX | Regular / Group 1 | 8 | 10 | https://www.okx.com/en-us/fees |
| Coinbase | Intro 1 | 60 | 120 | https://www.coinbase.com/advanced-vip |
| Kraken | $0 Kraken Pro Spot Crypto | 25 | 40 | https://www.kraken.com/features/fee-schedule |
| Gemini | $0 ActiveTrader | 60 | 120 | https://www.gemini.com/fees/activetrader-fee-schedule |
| Bitfinex | All customers | 0 | 0 | https://www.bitfinex.com/zero-fee-trading/ |
| WhiteBIT | Public market metadata | varies | varies, often 10 | `GET /api/v4/public/markets` |
| Upbit | Conservative public default | unknown | 25 | hard-coded conservative default |
| Indodax | Public pair metadata | varies | varies | `GET /api/pairs` |
| Buda | Public market metadata | varies | varies, often 80 | `GET /api/v2/markets` |
| NovaDAX | Conservative public default | unknown | 25 | hard-coded conservative default |
| Foxbit | Public market metadata | varies | varies, often 50 | `GET /rest/v3/markets` |
| Mercado Bitcoin | Conservative public default | unknown | 70 | hard-coded conservative default |
| Bitvavo | Conservative public default | unknown | 25 | hard-coded conservative default |
| Luno | Conservative public default | unknown | 25 | hard-coded conservative default |
| VALR | Conservative public default | unknown | 10 | hard-coded conservative default |
| Bitkub | Conservative public default | unknown | 25 | hard-coded conservative default |
| bitFlyer | Conservative public default | unknown | 15 | hard-coded conservative default |
| Bithumb | Conservative public default | unknown | 25 | hard-coded conservative default |
| Bitbank | Conservative public default | unknown | 12 | hard-coded conservative default |
| Bitrue | Conservative public default | unknown | 10 | hard-coded conservative default |
| Coincheck | Conservative public default | unknown | 10 | hard-coded conservative default |
| CoinTR | Public market metadata | varies | varies, often 10 | `GET /api/v2/spot/public/symbols` |
| CoinW | Conservative public default | unknown | 20 | hard-coded conservative default |
| Deribit Spot | Public spot instrument metadata | varies | varies, often 0 | `GET /public/get_instruments?kind=spot` |
| HitBTC | Public symbol metadata | varies | varies, often 25 | `GET /api/3/public/symbol` |
| Coins.ph | Conservative public default | unknown | 10 | hard-coded conservative default |
| Coinone | Conservative public default | unknown | 20 | hard-coded conservative default |
| Korbit | Conservative public default | unknown | 20 | hard-coded conservative default |
| GMO Coin | Public market metadata | varies | varies | `GET /public/v1/symbols` |
| Independent Reserve | Conservative public default | unknown | 50 | hard-coded conservative default |
| BTC Markets | Conservative public default | unknown | 85 | hard-coded conservative default |
| NDAX | Conservative public default | unknown | 20 | hard-coded conservative default |
| BitoPro | Conservative public default | unknown | 20 | hard-coded conservative default |
| DigiFinex | Conservative public default | unknown | 20 | hard-coded conservative default |
| LATOKEN | Conservative public default | unknown | 20 | hard-coded conservative default |
| Hyperliquid Spot | Conservative public default | unknown | 10 | hard-coded conservative default |
| Pionex | Conservative public default | unknown | 10 | hard-coded conservative default |
| Toobit | Conservative public default | unknown | 10 | hard-coded conservative default |
| XT.com | Public market metadata | varies | varies, often 20 | `GET /v4/public/symbol` |
| HashKey Global | Conservative public default | unknown | 10 | hard-coded conservative default |
| BingX | Conservative public default | unknown | 10 | hard-coded conservative default |
| Backpack | Conservative public default | unknown | 10 | hard-coded conservative default |
| Phemex | Public spot product metadata | varies | varies, often 10 | `GET /public/products` |
| Bullish | Conservative public default | unknown | 10 | hard-coded conservative default |
| WOO X | Conservative public default | unknown | 10 | hard-coded conservative default |

## Caveats

- Coinbase exact account tier should come from authenticated `GET /api/v3/brokerage/transaction_summary`; public table is still enough for conservative no-auth defaults.
- Kraken exact account/pair schedule can be read from authenticated `TradeVolume`; public `AssetPairs` also exposes pair fee arrays.
- Binance should use `GET /api/v3/account/commission?symbol=...` or order test with commission rates for live trading; BNB discount is not enabled in code by default.
- BitMEX spot exposes public per-instrument `makerFee` and `takerFee`; the broad monitor includes only `typ=IFXXXP` spot symbols, normalizes `XBT` to `BTC`, converts integer book sizes with `underlyingToPositionMultiplier`, and drops stale public order-book levels by `transactTime`.
- Bybit should use `GET /v5/account/fee-rate?category=spot&symbol=...` for account-specific rates.
- OKX should use `GET /api/v5/account/trade-fee?instType=SPOT&instId=...`; signed fee values use OKX's sign convention and must be normalized.
- Gemini ActiveTrader/API spot uses the same table; stablecoin pairs have separate pricing and are not used for BTC/ETH/SOL USD books.
- Bitfinex publicly says all customers are eligible for zero maker/taker trading fees across spot and margin. Verify account availability and non-trading fees before live use.
- WhiteBIT, Indodax, and Buda expose per-market public fee fields; the broad monitor uses those when available instead of a single exchange-wide default.
- Upbit fees vary by market and account context; the broad monitor uses a conservative 25 bps taker default until authenticated/account-specific fee discovery exists.
- Foxbit exposes per-market public fee fields; the broad monitor converts decimal fraction fees like `0.005` into 50 bps.
- NovaDAX fees vary by account context; the broad monitor uses a conservative 25 bps taker default until account-specific fee discovery exists.
- Mercado Bitcoin fees vary by account context; the broad monitor uses a conservative 70 bps taker default and currently includes `BRL` crypto spot pairs where the public legacy order book endpoint is available.
- Bitvavo fees vary by account tier/category; the broad monitor uses a conservative 25 bps taker default until account-specific fee discovery exists.
- Luno, VALR, Bitkub, bitFlyer, Bithumb, Bitbank, Bitrue, and Coincheck fees vary by market/account context; the broad monitor uses conservative hard-coded taker defaults until account-specific fee discovery exists.
- GMO Coin exposes public per-symbol fee fields; the broad monitor converts decimal fraction taker fees into bps.
- Coinone, Korbit, Independent Reserve, BTC Markets, NDAX, and BitoPro fees vary by market/account context; the broad monitor uses conservative hard-coded taker defaults until account-specific fee discovery exists.
- DigiFinex, LATOKEN, Hyperliquid, Pionex, and Toobit fees vary by market/account context; the broad monitor uses conservative hard-coded taker defaults until account-specific fee discovery exists. LATOKEN, Hyperliquid, Pionex, and Toobit public tickers/books are gated by timestamp to avoid stale rows. Pionex is off-default because the public REST API rate-limited this environment after smoke testing.
- HashKey Global fees vary by market/account context; the broad monitor uses a conservative hard-coded 10 bps taker default until account-specific fee discovery exists.
- XT.com exposes public per-symbol `takerFeeRate`; the broad monitor converts decimal fraction fees like `0.002` into 20 bps.
- BingX and Backpack fees vary by market/account context; the broad monitor uses conservative hard-coded 10 bps taker defaults until account-specific fee discovery exists.
- CoinTR exposes public per-symbol `takerFeeRate`; the broad monitor converts decimal fraction fees like `0.001` into 10 bps.
- CoinW fees vary by market/account context; the broad monitor uses a conservative hard-coded 20 bps taker default until account-specific fee discovery exists.
- Deribit exposes public per-instrument `maker_commission` and `taker_commission`; the broad monitor converts decimal fraction taker commissions into bps and currently observes zero-fee spot rows where public metadata reports `0.0`.
- HitBTC exposes public per-symbol `take_rate`; the broad monitor converts decimal fraction fees like `0.0025` into 25 bps and filters to `type=spot`, `status=working` symbols.
- Coins.ph fees vary by market/account context; the broad monitor uses a conservative hard-coded 10 bps taker default until account-specific fee discovery exists.
- Phemex exposes public spot `defaultTakerFee` per product; the broad monitor converts decimal fraction fees like `0.001` into 10 bps.
- Bullish fees vary by market/account context; the broad monitor uses a conservative hard-coded 10 bps taker default until account-specific fee discovery exists. The profit adapter is off-default because broad per-symbol tick sweeps returned HTTP 429 in this environment.
- WOO X fees vary by account context; the broad monitor uses a conservative hard-coded 10 bps taker default until account-specific fee discovery exists.
- Buy-side fees may be charged in base asset on some exchanges. The current scanner converts all fees into quote-equivalent P&L cost; a live executor must reconcile against fill-level `feeCurrency`/`commissionAsset`.

## Source Notes

- Binance regular/VIP0 spot and margin for USDT pairs is 10/10 bps before BNB discount.
- Bybit spot VIP0 is 10/10 bps; VIP/Pro tiers can go lower, down to Pro 6 0.5 bps maker and 1.5 bps taker.
- OKX `BTC-USDT` is Spot Group 1; regular user is 8 bps maker and 10 bps taker. Higher VIP levels include maker rebates.
- Coinbase Intro 1 is 60 bps maker and 120 bps taker; this makes retail Coinbase aggressive arbitrage extremely expensive.
- Kraken Pro Spot Crypto starts at 25 bps maker and 40 bps taker for low volume.
- Gemini ActiveTrader starts at 60 bps maker and 120 bps taker for low volume.
- Bitfinex zero-fee trading is the biggest fee-hurdle exception found so far. It deserves immediate scanner coverage, but depth/stale checks still killed the first XLM/XRP USD top-of-book candidates.
