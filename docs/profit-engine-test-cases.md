# Profit Engine Test Cases

Checked: 2026-05-29.

These cases should become unit tests as soon as the TypeScript project exists.

Use decimal strings in implementation. Numeric values below are written plainly for readability.

## 1. Gross Spread Positive, Net Profit Positive

Buy book:

- Exchange: `coinbase`
- Quote: `USD`
- Asks: `100000 @ 0.10`

Sell book:

- Exchange: `kraken`
- Quote: `USD`
- Bids: `100200 @ 0.10`

Trade size: `0.01 BTC`

Fees:

- Buy taker: `10 bps`
- Sell taker: `10 bps`
- Latency haircut: `2 bps`

Expected:

- Buy notional: `1000.00`
- Sell notional: `1002.00`
- Buy fee: `1.00`
- Sell fee: `1.002`
- Latency haircut: `0.2004`
- Net profit: about `-0.2024`
- Decision: `REJECT_NEGATIVE_AFTER_COSTS`

Purpose: prove a visible spread can still be negative.

## 2. Bigger Spread Survives Costs

Buy: `100000 @ 0.10`

Sell: `100500 @ 0.10`

Size: `0.01 BTC`

Fees:

- Buy taker: `10 bps`
- Sell taker: `10 bps`
- Latency haircut: `2 bps`

Expected:

- Gross profit: `5.00`
- Total cost: about `2.205`
- Net profit: about `2.795`
- Decision: `EXECUTE` if above min profit.

Purpose: happy path.

## 3. Depth Kills Profit

Buy asks:

- `100000 @ 0.005`
- `100600 @ 0.005`

Sell bids:

- `100500 @ 0.010`

Requested size: `0.01 BTC`

Expected:

- Buy VWAP: `100300`
- Sell VWAP: `100500`
- Gross profit before costs: `2.00`
- After fees/latency likely rejected.

Purpose: prove top-of-book alone is insufficient.

## 4. Partial Liquidity

Buy asks:

- `100000 @ 0.02`

Sell bids:

- `100500 @ 0.005`

Requested size: `0.02 BTC`

Expected:

- Executable size capped at `0.005 BTC`.
- If below venue minimum size, decision is `REJECT_BELOW_MIN_SIZE`.
- Otherwise evaluate costs at `0.005`.

Purpose: both legs must support same executable size.

## 5. Inventory Constraint On Sell Exchange

Wallets:

- Buy exchange quote: `2000 USD`
- Sell exchange BTC: `0.0001 BTC`

Requested size: `0.01 BTC`

Expected:

- Decision: `REJECT_INSUFFICIENT_SELL_BTC`.

Purpose: cannot sell BTC that is not already on sell venue.

## 6. Inventory Constraint On Buy Exchange

Wallets:

- Buy exchange quote: `100 USD`
- Sell exchange BTC: `0.10 BTC`

Buy notional required: `1000 USD`.

Expected:

- Decision: `REJECT_INSUFFICIENT_BUY_QUOTE`.

Purpose: buy leg requires quote inventory before trade.

## 7. Stale Book Rejection

Risk config:

- `maxBookAgeMs = 1500`

Buy book age: `200 ms`

Sell book age: `3000 ms`

Expected:

- Decision: `REJECT_STALE_BOOK`.

Purpose: stale books cannot generate execution.

## 8. Quote Mismatch Rejection

Buy book quote: `USD`

Sell book quote: `USDT`

No FX module active.

Expected:

- Decision: `REJECT_CROSS_QUOTE`.

Purpose: USD, USDT, USDC, and MXN are not the same asset.

## 9. Rounding Breaks Minimum Notional

Venue rules:

- `sizeStep = 0.001 BTC`
- `minNotional = 100 USD`

Raw executable size: `0.0014 BTC`

Rounded executable size: `0.001 BTC`

Price: `99000 USD`

Expected notional after rounding: `99 USD`

Expected:

- Decision: `REJECT_BELOW_MIN_NOTIONAL`.

Purpose: validate after venue rounding, not before.

## 10. Duplicate Decision Idempotency

Same `decisionId` applied twice.

Expected:

- First application creates one simulated trade and mutates wallets.
- Second application is rejected or ignored without wallet mutation.

Purpose: prevent double-counted P&L.

## 11. One-Leg Live Partial Fill

Live buy order partially fills `0.005 BTC`.

Sell leg has not filled.

Expected:

- Ledger records `LIVE_PARTIAL_FILL`.
- BTC inventory changes.
- Closed P&L does not increase.
- Open exposure is visible.

Purpose: order ack/partial fill is not closed arbitrage profit.

## 12. Replay Mode Isolation

Replay event has positive net P&L.

Expected:

- Replay P&L appears only under replay/demo metrics.
- Live P&L remains unchanged.

Purpose: demo mode cannot contaminate live results.

