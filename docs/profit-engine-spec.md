# Profit Engine Spec

Checked: 2026-05-29.

This is the contract between the scanner session and the arbitrage/profit engine.

The scanner finds live books. The profit engine decides whether those books contain executable yield.

## Objective

Generate returns by executing only opportunities that remain positive after:

- Order book depth.
- Trading fees on both legs.
- Slippage from consuming levels.
- Inventory constraints on both venues.
- Quote currency lane constraints.
- Latency/stale-data haircut.
- Minimum profit threshold.

The engine must reject fake profit aggressively. A visible rejection is better than a false execution.

Use decimal math. Do not use JavaScript `number` for money, BTC size, fees, prices, or P&L.

## Input Contract From Scanner

All scanner adapters must emit normalized books in this shape:

```ts
export type QuoteCurrency = 'USD' | 'USDT' | 'USDC' | 'MXN';

export type BookLevel = {
  price: string; // decimal string, quote per BTC
  size: string;  // decimal string, BTC
};

export type NormalizedBook = {
  exchange: string;
  symbol: string;
  base: 'BTC';
  quote: QuoteCurrency;
  bids: BookLevel[]; // sorted descending by price
  asks: BookLevel[]; // sorted ascending by price
  receivedAtMs: number;
  exchangeTsMs?: number;
  sequence?: string;
  source: 'ws' | 'rest' | 'replay';
};
```

Rules:

- `bids[0]` is the best executable sell price.
- `asks[0]` is the best executable buy price.
- Levels must be positive numbers as strings.
- Books with empty bids or asks are not tradable.
- Books from different quote lanes must not be compared unless an explicit FX/basis conversion module is active.

## Venue Config Contract

```ts
export type VenueConfig = {
  exchange: string;
  quote: QuoteCurrency;
  takerFeeBps: string;
  makerFeeBps?: string;
  withdrawalFeeBtc?: string;
  minOrderBtc: string;
  minNotionalQuote: string;
  priceTick: string;
  sizeStep: string;
  maxBookAgeMs: number;
  latencyHaircutBps: string;
};
```

Use taker fees for the first live version. Maker assumptions are only valid once we implement maker order placement and cancellation logic.

Round order prices and sizes to venue `priceTick` and `sizeStep` before final validation. Re-check minimum notional after rounding.

## Wallet Contract

```ts
export type WalletBalance = {
  exchange: string;
  quote: QuoteCurrency;
  btcAvailable: string;
  quoteAvailable: string;
  btcReserved: string;
  quoteReserved: string;
};
```

Inventory-based arbitrage requires:

- Quote inventory on the buy exchange.
- BTC inventory on the sell exchange.

Do not assume BTC bought on exchange A can be sold immediately on exchange B. Cross-exchange transfer is a separate strategy with transfer fees and settlement time.

If a fee is charged in BTC instead of quote currency, record it in the ledger as BTC and adjust resulting inventory. Do not silently convert it into quote P&L without an explicit conversion.

## Opportunity Detection

For every pair of books in the same quote lane:

```text
buyExchange.ask < sellExchange.bid
```

Candidate:

```ts
export type OpportunityCandidate = {
  id: string;
  quote: QuoteCurrency;
  buyExchange: string;
  sellExchange: string;
  buySymbol: string;
  sellSymbol: string;
  detectedAtMs: number;
  grossTopOfBookSpreadQuote: string;
  grossTopOfBookSpreadBps: string;
};
```

`id` should be deterministic for one decision window:

```text
{detectedAtMsBucket}:{quote}:{buyExchange}:{sellExchange}:{buySequence}:{sellSequence}
```

## Executable Size

Target size is capped by:

```text
maxTradeBtc
buy book ask liquidity
sell book bid liquidity
buy exchange quoteAvailable / executable buy VWAP
sell exchange btcAvailable
venue min/max constraints
```

If resulting size is below either venue's minimum, reject.

## VWAP Fill Calculation

For a buy leg, consume ask levels from low to high until target BTC is reached.

For a sell leg, consume bid levels from high to low until target BTC is reached.

Return:

```ts
export type FillEstimate = {
  side: 'buy' | 'sell';
  requestedBtc: string;
  executableBtc: string;
  averagePrice: string;
  notionalQuote: string;
  fullyFilled: boolean;
  levelsConsumed: number;
};
```

If both legs cannot execute the same BTC size, use the smaller executable size and recompute both VWAPs for that size.

## Profit Formula

```text
buyNotional = buyAvgPrice * btcSize
sellNotional = sellAvgPrice * btcSize

buyFee = buyNotional * buyTakerFeeBps / 10000
sellFee = sellNotional * sellTakerFeeBps / 10000
latencyHaircut = sellNotional * max(buyLatencyHaircutBps, sellLatencyHaircutBps) / 10000

grossProfit = sellNotional - buyNotional
netProfit = grossProfit - buyFee - sellFee - latencyHaircut
netProfitBps = netProfit / buyNotional * 10000
```

Do not subtract withdrawal fees for inventory-based same-time arbitrage. Add transfer fees only for a separate rebalance strategy.

## Decision States

```ts
export type DecisionStatus =
  | 'OBSERVED'
  | 'CANDIDATE_BUILT'
  | 'EXECUTE'
  | 'REJECT_STALE_BOOK'
  | 'REJECT_CROSS_QUOTE'
  | 'REJECT_NO_SPREAD'
  | 'REJECT_INSUFFICIENT_LIQUIDITY'
  | 'REJECT_INSUFFICIENT_BUY_QUOTE'
  | 'REJECT_INSUFFICIENT_SELL_BTC'
  | 'REJECT_BELOW_MIN_SIZE'
  | 'REJECT_BELOW_MIN_NOTIONAL'
  | 'REJECT_NEGATIVE_AFTER_COSTS'
  | 'REJECT_BELOW_MIN_PROFIT'
  | 'REJECT_CIRCUIT_BREAKER'
  | 'SIMULATED_EXECUTED'
  | 'LIVE_SUBMITTED'
  | 'LIVE_PARTIAL_FILL'
  | 'LIVE_FILLED'
  | 'LIVE_CANCELLED'
  | 'LIVE_FAILED'
  | 'RECONCILED';
```

The UI must show the rejection reason. Rejections are evidence that the engine is not naive.

Only `SIMULATED_EXECUTED`, `LIVE_FILLED`, and `RECONCILED` can affect closed P&L. `EXECUTE` or `LIVE_SUBMITTED` means intent, not profit.

## Decision Output

```ts
export type ArbitrageDecision = {
  id: string;
  status: DecisionStatus;
  quote: QuoteCurrency;
  buyExchange: string;
  sellExchange: string;
  btcSize: string;
  buyAvgPrice: string;
  sellAvgPrice: string;
  buyNotional: string;
  sellNotional: string;
  grossProfit: string;
  buyFee: string;
  sellFee: string;
  latencyHaircut: string;
  netProfit: string;
  netProfitBps: string;
  detectedAtMs: number;
  decidedAtMs: number;
  bookAgesMs: {
    buy: number;
    sell: number;
  };
  explanation: string;
};
```

## Simulated Execution Ledger

When a decision is `EXECUTE`, append one immutable trade event:

```ts
export type SimulatedTrade = {
  id: string;
  decisionId: string;
  executedAtMs: number;
  quote: QuoteCurrency;
  btcSize: string;
  buyExchange: string;
  sellExchange: string;
  buyAvgPrice: string;
  sellAvgPrice: string;
  buyFee: string;
  sellFee: string;
  netProfit: string;
  before: {
    buyWallet: WalletBalance;
    sellWallet: WalletBalance;
  };
  after: {
    buyWallet: WalletBalance;
    sellWallet: WalletBalance;
  };
};
```

Balance updates:

```text
buyExchange.btcAvailable += btcSize
buyExchange.quoteAvailable -= buyNotional + buyFee

sellExchange.btcAvailable -= btcSize
sellExchange.quoteAvailable += sellNotional - sellFee
```

The simulated trade's `netProfit` must equal:

```text
(sellNotional - sellFee) - (buyNotional + buyFee) - latencyHaircut
```

For live trading, use an append-only event model:

```ts
export type LedgerEvent = {
  id: string;
  candidateId: string;
  type:
    | 'SIMULATED_FILL'
    | 'LIVE_ORDER_ACK'
    | 'LIVE_FILL'
    | 'REJECT'
    | 'CANCEL'
    | 'RECONCILE';
  exchange: string;
  side?: 'BUY' | 'SELL';
  baseDelta?: string;
  quoteDelta?: string;
  feeCurrency?: 'BTC' | 'USD' | 'USDT' | 'USDC' | 'MXN';
  feeAmount?: string;
  balancesBefore: WalletBalance;
  balancesAfter: WalletBalance;
  timestampMs: number;
};
```

An order ack does not count as execution. A partial fill on one leg creates open exposure; do not count it as closed arbitrage P&L until the opposite leg is filled or the exposure is explicitly marked to market.

## Ledger Invariants

Every executed trade must satisfy:

- No balance becomes negative.
- Buy and sell BTC size match exactly.
- `after.buyWallet.btcAvailable - before.buyWallet.btcAvailable = btcSize`.
- `before.sellWallet.btcAvailable - after.sellWallet.btcAvailable = btcSize`.
- Quote deltas reconcile with buy/sell notional and fees.
- Duplicate `decisionId` cannot execute twice.
- Rejected decisions never mutate wallets.
- Cross-lane decisions cannot execute without an explicit conversion module.
- Replay/mock events never contaminate live P&L metrics.
- P&L accumulated in the UI equals the sum of closed ledger events only.

## Circuit Breakers

Global:

- Pause all execution if any adapter reports disconnected for more than threshold.
- Pause all execution after `maxConsecutiveFailedFills`.
- Pause all execution after `maxDailyLossQuote`.
- Pause one exchange if its book is stale or sequence/checksum is invalid.

Per decision:

- Reject if book age exceeds `maxBookAgeMs`.
- Reject if spread is unrealistically large unless replay/stress mode is active.
- Reject if either side consumes more than allowed levels or exceeds slippage threshold.

## UI Requirements For The Engine

Expose:

- Best current opportunity per lane.
- Decision waterfall:
  - gross spread
  - buy fee
  - sell fee
  - depth/slippage
  - latency haircut
  - net profit
- Rejection stream with reason.
- Executed trades.
- Wallet balances per exchange.
- Cumulative net P&L by lane and exchange pair.

## Must-Have Tests

1. Reject when quotes differ (`USD` vs `USDT`) without conversion.
2. Reject when either book is stale.
3. Reject when ask >= bid.
4. Compute VWAP across multiple levels.
5. Partial executable size uses the smaller leg.
6. Reject when buy quote balance is insufficient.
7. Reject when sell BTC balance is insufficient.
8. Reject when net profit is negative after fees.
9. Reject when net profit is positive but below minimum threshold.
10. Execute valid trade and reconcile both wallets.
11. Prevent duplicate decision execution.
12. Preserve wallet non-negativity under random generated books.
13. Fees charged in BTC update BTC inventory rather than quote balance.
14. Rounding by `priceTick` and `sizeStep` cannot break min notional.
15. One-leg partial fill does not increase closed P&L.
16. Replay mode never changes live P&L.

## First Implementation Slice

Implement these functions first:

```ts
estimateFill(levels, side, targetBtc): FillEstimate
findCandidates(books): OpportunityCandidate[]
evaluateCandidate(candidate, books, wallets, venueConfig, riskConfig): ArbitrageDecision
applySimulatedTrade(decision, wallets): SimulatedTrade
```

This can be built and tested before the scanner is finished by using static fixture books.
