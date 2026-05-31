# Continuous Profit Scout Agent 2

Use this prompt file for a second `/goal` agent running in parallel.

This agent must not edit the same deliverables as the primary overnight agent.

## Mission

Run continuously until Pedro explicitly stops you.

Your job is to scout profit approaches that the main overnight agent may miss. Do not stop after producing one report. Keep cycling through discovery, measurement, ranking, and backlog updates.

## Repository

`/Users/pedrorios/Desktop/gold/hackathon-btc`

Read first:

- `docs/exchange-map.md`
- `docs/market-discovery-spec.md`
- `docs/profit-engine-spec.md`
- `docs/profit-engine-test-cases.md`
- `docs/overnight-goal-prompt.md`

## Do Not Collide

Do not edit these primary-agent files:

- `docs/overnight-profit-opportunities.md`
- `docs/overnight-rejected-ideas.md`
- `docs/implementation-queue.md`
- `docs/overnight-profit-checkpoints.md`
- `docs/profit-approach-playbook.md`

Write only these Agent 2 files:

- `docs/agent2-continuous-scout-report.md`
- `docs/agent2-opportunity-candidates.md`
- `docs/agent2-kill-list.md`
- `docs/agent2-next-actions.md`

## Scope

Look for approaches beyond the obvious scanner path:

- New exchanges worth adding.
- New high-liquidity assets worth scanning.
- USDT/USDC/USD/MXN basis.
- Bitso MXN/FX opportunities.
- Triangular arbitrage inside exchanges.
- Spot-perp basis and funding capture.
- Maker/taker or rebate strategies.
- Cross-exchange stablecoin routes.
- CEX-DEX routes only if measurable quickly.

## Rules

- No real trading.
- No order placement.
- No private API key usage unless Pedro explicitly directs it in this agent.
- Prefer public endpoints and official docs.
- Do not report gross spread as profit.
- Profit means net after fees, depth, slippage, inventory, quote-lane separation, latency/stale risk, and venue minimums.
- Be ruthless. Kill weak ideas quickly.

## Continuous Loop

Repeat forever until stopped:

1. Pick one profit hypothesis.
2. Gather evidence with public data/docs or non-destructive scripts.
3. Score it.
4. Mark it `DO_NOW`, `MEASURE`, `LATER`, or `KILL`.
5. Update Agent 2 files.
6. Move to the next hypothesis.

Every 45-60 minutes, append a checkpoint to `docs/agent2-continuous-scout-report.md`.

## Scoring

For every candidate include:

- approach type
- route/assets/exchanges
- quote lane
- why edge might exist
- public data quality
- fee assumptions
- estimated net bps
- executable notional estimate
- frequency/duration evidence or proxy
- implementation effort
- inventory/funding requirements
- risks
- confidence
- verdict

## Success

This agent succeeds if it keeps expanding the opportunity frontier without colliding with the main agent, and leaves Pedro with additional high-EV routes or a clean kill list.

