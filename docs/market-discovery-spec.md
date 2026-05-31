# Market Discovery Spec

Checked: 2026-05-29.

The curated scanner is not enough to find real profit. It is an MVP. The next jump is automatic market discovery.

## Objective

Continuously discover which assets, quote lanes, and exchange routes are worth scanning for executable edge.

The system should not rely on a hand-picked list like BTC/ETH/SOL only. It should build the opportunity graph from exchange market metadata and live liquidity.

## Core Loop

1. Download all public spot markets per exchange.
2. Keep only quote lanes we can model:
   - `USDT`
   - `USDC`
   - `USD`
   - `MXN`
   - optionally `EUR` later
3. Normalize symbols into:
   - base asset
   - quote asset
   - exchange
   - min order size
   - tick size
   - lot size
   - status/tradability
4. Keep only bases listed on at least 2 exchanges in the same quote lane.
5. Pull top-of-book and depth snapshots for candidates.
6. Filter by:
   - minimum 24h volume
   - maximum spread
   - minimum top-N depth
   - stable WebSocket/API quality
   - known fee schedule
7. Rank routes continuously by:
   - net edge after taker fees
   - executable notional
   - frequency per hour
   - edge duration
   - implementation/trading readiness
8. Promote the best routes into the live scanner.

## Asset Coverage

Start with common high-liquidity bases, then let discovery expand:

- Core: `BTC`, `ETH`, `SOL`, `XRP`, `DOGE`, `LTC`
- Next: `ADA`, `AVAX`, `LINK`, `SUI`, `TON`, `NEAR`, `APT`, `ARB`, `OP`, `BCH`, `TRX`, `DOT`, `INJ`, `SEI`, `BNB`
- Stable/fx: `USDT`, `USDC`, `USD`, `MXN`

Do not manually add hundreds of assets. Use exchange metadata and liquidity filters.

## Exchange Coverage

Tier A scanner:

- Binance
- Bybit
- OKX
- Coinbase
- Kraken
- Gemini

Expansion scanner:

- MEXC
- Gate.io
- Bitget
- KuCoin
- Crypto.com Exchange
- Bitfinex
- Bitstamp
- Bitso
- HTX
- Upbit, only if region/API/data quality make sense

## Strategy Coverage

Do not stop at simple spot-spot taker arbitrage. Market discovery should score:

- Same-quote cross-exchange spot arbitrage.
- USD/USDT/USDC basis, only with explicit haircut.
- MXN/USD/USDT basis through Bitso, only with explicit FX model.
- Triangular arbitrage inside one exchange.
- Maker/taker hybrid routes.
- Spot-perp basis and funding-rate capture.
- CEX-DEX arbitrage if a route can be measured without derailing the 48h build.

## Required Outputs

The discovery module should emit:

```ts
type DiscoveredMarket = {
  exchange: string;
  base: string;
  quote: 'USD' | 'USDT' | 'USDC' | 'MXN' | 'EUR';
  symbol: string;
  status: 'online' | 'offline' | 'restricted' | 'unknown';
  minOrderSize?: string;
  minNotional?: string;
  priceTick?: string;
  sizeStep?: string;
  volume24hQuote?: string;
  source: 'exchange' | 'aggregator';
};

type RankedRoute = {
  approachType:
    | 'cross_exchange_spot'
    | 'triangular'
    | 'cross_lane_basis'
    | 'mxn_fx_basis'
    | 'maker_taker'
    | 'spot_perp_basis'
    | 'cex_dex';
  base: string;
  quote: string;
  buyExchange?: string;
  sellExchange?: string;
  venues: string[];
  estimatedNetBps: string;
  executableNotionalUsd: string;
  frequencyPerHour?: string;
  confidence: 'high' | 'medium' | 'low';
  implementationHours: string;
  verdict: 'DO_NOW' | 'MEASURE' | 'LATER' | 'KILL';
};
```

## Success Criteria

Market discovery is successful when tomorrow's work is not "which assets should we add?" but:

- Here are the top 20 routes by estimated net edge.
- Here are the top 5 that are implementable today.
- Here are the routes that are fake after fees/depth.
- Here is the exact scanner config to enable next.

