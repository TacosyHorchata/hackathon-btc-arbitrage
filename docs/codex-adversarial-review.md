TOKENS: 18441
RAN_COMMANDS: (none — good, stayed in prompt)
============================================================
**Ranked Problems**

1. **Bitfinex access may be fatal**
   If the trader is a US person, Bitfinex eligibility kills the route before execution. Binance.US strongly implies US venue/user context. No account access, no arb.

2. **Two REST snapshots are not a tradable spread**
   Unsynchronized books are observations, not executable state. A 13 bps gross spread can disappear between fetch, decision, order routing, matching, and partial fill. REST-book VWAP is not proof of simultaneous fill.

3. **This is likely venue basis, not arbitrage**
   “583 appearances” may mean Binance.US structurally trades cheaper than Bitfinex because capital, access, fiat rails, settlement, KYC, jurisdiction, or withdrawal constraints prevent convergence. Persistent spread often signals friction, not free edge.

4. **One-directional inventory breaks the strategy**
   Buy BTC on Binance.US and sell BTC on Bitfinex consumes USD on Binance.US and BTC on Bitfinex. After enough trades, you are stuck unless you can cheaply and quickly move USD/BTC back. The real trade includes rebalancing.

5. **Rebalancing costs and settlement dominate**
   Withdrawal fees, blockchain confirmation time, fiat rails, holds, limits, compliance delays, and exchange transfer risk are excluded. If rebalancing is slow or expensive, the apparent $5 edge is irrelevant.

6. **Capital efficiency is overstated**
   A $5k “trade” needs at least $5k USD on Binance.US plus ~$5k BTC on Bitfinex, so roughly $10k gross capital is tied up. $5 profit is not 10 bps on actual deployed capital; it is closer to 5 bps before operational costs and idle balance risk.

7. **BTC inventory risk is real**
   Pre-funding BTC on Bitfinex means you are long BTC inventory unless hedged. If BTC moves while waiting for windows or during rebalance, the $5 edge is noise relative to mark-to-market variance.

8. **Latency haircut is arbitrary**
   “2 bps latency” is not a model. Slippage is state-dependent: queue position, toxic flow, book refresh cadence, partial fills, market order protection, API jitter, and adverse selection. Fixed bps latency assumptions are fake precision.

9. **Taker fee assumption is fragile**
   Claimed round-trip near 1 bp depends on exact pairs, tiers, promotions, user eligibility, and fee currency. One wrong fee flag can erase most of the edge.

10. **VWAP depth is not guaranteed executable**
   “5 levels buy, 1 level sell” from books assumes displayed liquidity remains there and accepts your taker order. Thin spreads are often pulled or consumed exactly when they look attractive.

11. **Partial-fill asymmetry can create outright exposure**
   If one leg fills and the other slips/fails, you are no longer arbitraging; you are taking directional BTC and venue-basis risk. The downside tail is much larger than $5.

12. **No proof of post-trade PnL**
   Simulated gross proceeds are not exchange-confirmed fills, fees, balances, and realized account equity after both legs. The only PnL that matters is balance delta after execution and rebalance.

**Single strongest reason it makes $0 in practice:** the observed 13 bps is probably a non-capturable venue/access/settlement basis from unsynchronized REST snapshots, not a simultaneously executable arbitrage spread.
