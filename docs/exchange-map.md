# Exchange Map For BTC Arbitrage

Checked: 2026-05-29.

Goal: maximize the graph of safe, liquid, programmable, fundable venues where BTC price divergence can become executable profit.

Use this file to decide:

- Which exchanges to connect to for live scanning.
- Which exchanges are candidates for real trading once accounts and inventory are ready.
- What API credentials and permissions are needed.
- Which quote lanes must not be mixed without explicit conversion/haircut.

## Operating Principle

More venues create more arbitrage edges, but only usable venues count. A venue is useful when it has:

- Strong reputation and acceptable counterparty risk.
- Public order book API with WebSocket depth.
- Private trading API with reliable order placement/cancel/fill tracking.
- BTC pair liquidity.
- API keys with trade permission and no withdrawal permission.
- Fast funding path and no unexpected withdrawal/account holds.
- Fees/minimums low enough that spreads can survive.

## Immediate Priority

1. Build scanner adapters first for Tier A venues.
2. Keep USD, USDT, USDC, and MXN lanes separate.
3. Measure executable spreads live before deciding where to fund inventory.
4. Enable live trading only on venues where API keys, balances, limits, and permissions are verified.

## Fastest Path To Start Today

No API keys are needed for the first scanner. Start with public market data:

- USD lane: Coinbase `BTC-USD`, Kraken `BTC/USD`, Gemini `btcusd`.
- USDT lane: Binance `BTCUSDT`, Bybit `BTCUSDT`, OKX `BTC-USDT`.
- MXN lane: Bitso `btc_mxn`, once the USD/USDT scanner is stable.

Private trading starts only after the scanner proves live edge. For live order placement, every venue needs a dedicated API key with read + trade/order permissions and no withdrawal permission.

Minimum `.env` shape for live trading:

```bash
COINBASE_API_KEY=
COINBASE_API_SECRET=
KRAKEN_API_KEY=
KRAKEN_API_SECRET=
BINANCE_API_KEY=
BINANCE_API_SECRET=
BYBIT_API_KEY=
BYBIT_API_SECRET=
GEMINI_API_KEY=
GEMINI_API_SECRET=
OKX_API_KEY=
OKX_API_SECRET=
OKX_PASSPHRASE=
BITSO_API_KEY=
BITSO_API_SECRET=
```

Do not request or store withdrawal permissions.

## Registration Priority For Live Trading

Public market-data APIs do not require registration for the first scanner. Registration/KYC/API keys are only needed when we want balances, private order streams, or live order placement.

Register in this order:

1. **Bitso** - MXN lane. Highest local edge potential via `BTC/MXN` versus implied USD/MXN. Needed for any Mexico-fiat arbitrage.
2. **Kraken** - USD lane. Strong API, serious liquidity, good reliability profile.
3. **Coinbase Advanced Trade** - USD lane. Strong liquidity if Advanced Trade is available for the account/region.
4. **Gemini or Bitstamp** - third USD venue. Register both if time allows; Gemini has a cleaner sandbox, Bitstamp adds another reputable USD/USDT venue.
5. **Binance Spot** - USDT lane and maximum liquidity, if available for the account/region.
6. **OKX** - USDT/USDC lane and useful demo trading.
7. **Bybit** - USDT lane, only if the account/region is allowed. Do not bypass restrictions.
8. **Gate.io, KuCoin, Bitget, MEXC** - scanner first; register for live trading only if the scanner shows persistent edge worth the counterparty/API complexity.
9. **Bitfinex** - strong USD venue, worth adding if account onboarding is fast.
10. **Crypto.com Exchange** - only if Pedro already has exchange account access or onboarding is low-friction.

If Pedro is operating from the United States, verify exchange-specific restrictions before spending time on Binance global, Bybit, OKX, Gate, KuCoin, Bitget, or MEXC. If Pedro is operating from Mexico, Bitso and Binance/OKX-style USDT lanes become more important, but each venue still needs account-level availability confirmation.

## Tier A - First Scanner + Trading Candidates

| Exchange | Lane/pairs | Public data docs | Trading/API docs | What we need to start | Notes |
|---|---:|---|---|---|---|
| Coinbase Advanced Trade | USD: `BTC-USD`; validate `BTC-USDC` with products endpoint | WebSocket market data: `wss://advanced-trade-ws.coinbase.com`; user data: `wss://advanced-trade-ws-user.coinbase.com`. Docs: https://docs.cdp.coinbase.com/coinbase-business/advanced-trade-apis/websocket/websocket-overview | Advanced Trade REST supports trading/order management. Docs/FAQ: https://docs.cdp.coinbase.com/coinbase-business/advanced-trade-apis/faq | Coinbase account with Advanced Trade API key, portfolio access, `view` + `trade` permissions, no withdrawal permission. Verify CDP key auth and portfolio scope. | Strong USD venue. Public WS mostly unauthenticated. Sandbox exists but is static/mock for accounts/orders; do not use it for price discovery. |
| Kraken Spot | USD: `BTC/USD`; validate `BTC/USDT` via AssetPairs | L2 book WebSocket v2: `wss://ws.kraken.com/v2`, channel `book`, depths 10/25/100/500/1000. Docs: https://docs.kraken.com/api/docs/websocket-v2/book/ | REST `AddOrder`; private WS endpoint `wss://ws-auth.kraken.com/v2` after REST token. Docs: https://docs.kraken.com/api/docs/rest-api/add-order/ | Kraken account, API key with Query Funds, Query Open/Closed Orders, Modify Orders, Cancel/Close Orders, Access WebSockets API; do not grant Withdraw Funds. | Excellent serious venue. Need map BTC vs legacy XBT carefully. Maintain checksum for local book correctness. |
| Binance Spot | USDT: `BTCUSDT`; validate `BTCFDUSD`, `BTCUSDC` with `/exchangeInfo` | Official Spot market-data WebSocket streams: `wss://stream.binance.com:9443` or `:443`; market-only `wss://data-stream.binance.vision`; testnet `wss://stream.testnet.binance.vision`. Docs repo: https://github.com/binance/binance-spot-api-docs | Spot REST `/api/v3/order` with `TRADE`; user-data streams. Same docs repo. | Binance account where available, Spot API key with `TRADE` + user data/read permissions, IP whitelist if possible, no withdrawal permission. Verify regional availability. | Highest liquidity. Full local book needs REST snapshot + update-id continuity. WS has message limits and 24h reconnect expectation. |
| Bybit Spot | USDT: `BTCUSDT` | Public WS endpoint `wss://stream.bybit.com/v5/public/spot`; orderbook depths 1/50/200/1000, topic `orderbook.{depth}.{symbol}`. Docs: https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook | V5 order create, private WS, and order-entry WS. Docs: https://bybit-exchange.github.io/docs/v5/order/create-order | Bybit Unified Account, API key with SpotTrade/read/write, order/fill streams, no withdrawal. Check KYC/region. | Good Binance pair for USDT lane. Testnet exists. Market orders may become IOC limits with slippage protection. Some regions/IPs may be blocked. |
| Gemini | USD: `btcusd` | Public market data WebSocket; `btcusd@bookTicker`, `btcusd@depth20@100ms`; sandbox `wss://api.sandbox.gemini.com`. Docs: https://developer.gemini.com/websocket/streams | REST orders and WS auth/trading. Docs: https://docs.gemini.com/rest/orders and https://developer.gemini.com/trading/websocket/authentication | Gemini account, API key/session key with `Trader` role for orders, read balances/orders, no withdrawal. | Simple USD venue. Full sandbox exists with test funds. Nonce + HMAC-SHA384. Check minimums/order options. |
| OKX | USDT: `BTC-USDT`; validate `BTC-USDC`, `BTC-USD` with instruments endpoint | REST + WebSocket v5 public/private/business; prod public `wss://ws.okx.com:8443/ws/v5/public`; demo `wss://wspap.okx.com:8443/ws/v5/public`. Docs: https://www.okx.com/docs-v5/en/ | `POST /api/v5/trade/order`; WS order ops; key permissions `Read`, `Trade`, `Withdraw`. Same docs. | OKX account, region-correct domain (`openapi.okx.com`, `us.okx.com`, or `eea.okx.com` depending registration), API key + secret + passphrase with Read/Trade only, IP binding. | Strong USDT venue. Demo trading exists. Important regional domain requirement; keys with trade/withdraw and no IP can expire after inactivity. |

## Tier B - Add After Core Scanner Works

| Exchange | Lane/pairs | Public data docs | Trading/API docs | What we need to start | Notes |
|---|---:|---|---|---|---|
| Bitfinex | USD: `tBTCUSD`; USDT possible | Public WS v2 endpoint `wss://api-pub.bitfinex.com/ws/2`. Docs: https://docs.bitfinex.com/docs/ws-general | Auth WS endpoint `wss://api.bitfinex.com/ws/2`. Docs: https://docs.bitfinex.com/docs/ws-auth | Bitfinex account, API key with order/balance/read permissions, no withdrawal; respect auth/public WS rate limits. | Mature venue. Symbol format uses `t` prefix. Watch precision rules and rate limits. |
| Bitstamp | USD/USDT/EUR: `btcusd`, `btcusdt`, `btceur` | REST book + WS v2 `wss://ws.bitstamp.net`. Docs: https://www.bitstamp.net/api/ and https://www.bitstamp.net/websocket/v2/ | Buy/sell/cancel/status endpoints in REST API; private WS requires token. | Bitstamp account, API key with trading permissions, read balances/fees/orders, no withdrawal. | Add if USD lane needs another reputable venue. Lowercase market symbols. Sandbox REST exists at `sandbox.bitstamp.net`. |
| KuCoin | USDT/USDC: `BTC-USDT`, `BTC-USDC` | REST partial book + WS spot. Docs: https://www.kucoin.com/docs-new | Spot/HF orders and private WS. Same docs. | KuCoin account, API key + secret + passphrase, `General` read + `Spot` trade permissions, IP whitelist, no withdrawal. | Broad market coverage. Sandbox is not a dependable blocker-free path; use small live funds/order test. |
| Gate.io | USDT/USDC: `BTC_USDT`, `BTC_USDC` | API v4 WS endpoint `wss://api.gateio.ws/ws/v4/`. Docs: https://www.gate.com/docs/developers/apiv4/ws/en/ | REST base `https://api.gateio.ws/api/v4`; spot order APIs. Docs: https://www.gate.com/docs/apiv4/index.html | Gate account, APIv4 key with spot read/write, IP whitelist if enabled, no withdrawal. | Good extra USDT venue. Pair format uses `_`. Beware cancel-all behavior if omitting `currency_pair`. |
| Crypto.com Exchange | USDT/USD depending products: validate `BTC_USDT`, `BTC_USD` | Exchange API docs: https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html | Private `create-order`, cancel, order detail/trades. Same docs. | Crypto.com Exchange account, API key/secret from Exchange, trade permissions, read balances/orders, no withdrawal. | Useful if account access exists. UAT sandbox exists. Confirm via user order stream because create-order is async. |
| MEXC | USDT/USDC: `BTCUSDT`, validate `BTCUSDC` | Spot v3 docs: https://mexcdevelop.github.io/apidocs/spot_v3_en/ | Spot order endpoints and `/api/v3/order/test` in same docs. | MEXC account, `SPOT_DEAL_WRITE`, `SPOT_DEAL_READ`, `SPOT_ACCOUNT_READ`, no withdrawal. | Scanner first, trade later if edge/counterparty comfort justify. WS disconnects after 24h; max subscriptions per connection. |
| Bitget | USDT: `BTCUSDT` | API docs: https://www.bitget.com/api-doc/ | Place order docs: https://www.bitget.com/api-doc/uta/trade/Place-Order | Bitget account, API key with UTA trade read/write, passphrase, IP whitelist, no withdrawal. | Good additional USDT venue. Useful client order IDs; check product/account mode. |

## Mexico / MXN Lane

| Exchange | Lane/pairs | Public data docs | Trading/API docs | What we need to start | Notes |
|---|---:|---|---|---|---|
| Bitso | MXN: `btc_mxn`; validate `btc_usd` if active | WebSocket `wss://ws.bitso.com`; orders/diff-orders docs: https://docs.bitso.com/bitso-api/docs/general and https://docs.bitso.com/bitso-api/docs/orders-channel | Place order: `POST /orders`; docs: https://docs.bitso.com/bitso-api/docs/place-an-order; credentials: https://docs.bitso.com/bitso-api/docs/2-generate-your-api-credentials | Bitso account, API key with `Place orders`, `View balances`, `View account information`, no withdrawal. Need MXN and BTC inventory. | Very important local lane. Real edge may appear in `BTC/MXN` versus implied USD/MXN. Must include FX rate, fees, and transfer friction. Sandbox exists at `api-sandbox.bitso.com`. |
| Luno | Fiat lanes such as `XBTZAR`; usefulness depends on supported country/account | API docs: https://www.luno.com/developers/api | Orders endpoint `postorder` in same docs. | Luno account in supported country, API key with order permissions. | Not first priority unless account/funding path exists. Useful as template for fiat-lane arbitrage. |

## What We Need From Pedro For Live Trading

For each venue we want to trade live:

1. Confirm account exists, KYC is complete, and API trading is allowed in Pedro's jurisdiction.
2. Create a dedicated API key named for this bot.
3. Grant minimum permissions:
   - Read balances/account.
   - Read open orders/trades/fills.
   - Place/modify/cancel spot orders.
   - User-data WebSocket if separate.
   - No withdrawals.
4. Add IP whitelist if the deploy host has stable egress IP. If not, use local runner first or choose host with static outbound IP.
5. Share only through local `.env`, never commit keys.
6. Fund tiny inventory per venue:
   - Quote balance on venues where we may buy.
   - BTC balance on venues where we may sell.
   - Use tiny size until paper trading proves positive EV.
7. Record fee tier, minimum order size, tick size, lot size, and withdrawal/transfer fee.

## Scanner Implementation Order

1. Public scanner, no keys: Coinbase, Kraken, Gemini, Binance, Bybit, OKX.
2. Normalize books into one shape:

```ts
type NormalizedBook = {
  exchange: string;
  symbol: string;
  base: 'BTC';
  quote: 'USD' | 'USDT' | 'USDC' | 'MXN';
  bids: { price: string; size: string }[];
  asks: { price: string; size: string }[];
  receivedAtMs: number;
  exchangeTsMs?: number;
  source: 'ws' | 'rest';
};
```

3. Compute same-lane arbitrage only.
4. Add Bitso MXN lane with explicit FX conversion/haircut.
5. Add Tier B venues only after Tier A scanner is stable.
6. Only then add private trading connectors for 2-4 venues with proven live spreads and available inventory.

## Live Trading Safety Defaults

- API keys: read + trade only, no withdraw.
- Order type: IOC/FOK or tight limit orders first, no market orders until slippage model is proven.
- Max notional per trade: tiny initial value.
- Kill switch: global pause and cancel-all per venue.
- Max daily loss and max consecutive failed fills.
- Reject if either book age exceeds threshold.
- Reject if balance is insufficient on either side.
- Reject if spread is not positive after fees, depth, slippage, and latency buffer.
