# Overnight Profit Research Prompt

Use this prompt for an overnight `/goal` session.

```text
/goal

Actua como The Operator para el challenge de arbitraje BTC/crypto.

Objetivo:
Durante la noche, explorar sin sesgo y rankear los mejores approaches para sacar profit realista de exchanges. No te limites al scanner actual ni a una arquitectura especifica. Quiero manana una lista priorizada, con evidencia, que diga que enfoques tienen mayor probabilidad de imprimir dinero y cuales hay que matar.

Repo:
/Users/pedrorios/Desktop/gold/hackathon-btc

Lee primero:
- docs/exchange-map.md
- docs/market-discovery-spec.md
- docs/profit-engine-spec.md
- docs/profit-engine-test-cases.md

Si existen, lee tambien:
- docs/engine-architecture.md
- docs/exchange-fees.md

Si no existe docs/exchange-fees.md, crealo con assumptions iniciales de taker fees, min order sizes, tick/step sizes y fuentes oficiales por exchange.

Contexto:
- Hay otra sesion trabajando en scanner, pero no te limites a eso. Si el mejor approach requiere otro scanner, otro flujo, otra crypto, triangular, FX, funding, market making o una tactica distinta, investigalo y rankealo.
- El scanner actual es solo MVP. La prioridad real es automatic market discovery: descargar mercados spot publicos por exchange, filtrar por quote/liquidez/spread/depth, generar rutas automaticamente y rankearlas por edge neto, duracion y frecuencia.
- Puedes crear scripts pequenos de medicion no destructiva si ayudan a rankear oportunidades.
- No uses private API keys.
- No hagas trading real.
- Tiempo total del challenge: 48 horas. La prioridad es profit ejecutable, no investigacion decorativa.

Principio central:
Solo cuenta una oportunidad si sobrevive order book depth, taker fees, slippage, inventory constraints, quote-lane separation, latency/stale-data haircut y tamano minimo. Nunca reportes gross spread como profit.

Scope prioritario:
1. Automatic market discovery:
   - Descargar todos los mercados spot publicos por exchange.
   - Filtrar quotes: USDT, USDC, USD, MXN, opcional EUR.
   - Mantener bases comunes en 2+ exchanges.
   - Rankear por liquidez, spread, depth, fees, edge neto, duracion y frecuencia.
2. BTC spot cross-exchange, mismas quote lanes:
   - USD: Coinbase, Kraken, Gemini, Bitstamp/Bitfinex si conviene.
   - USDT: Binance, Bybit, OKX, KuCoin/Gate si conviene.
   - MXN: Bitso solo con FX/haircut explicito.
3. Triangular arbitrage intra-exchange si encuentras pares concretos, liquidez suficiente y fee math que lo justifique.
4. Cross-asset / altcoin arbitrage si una crypto tiene mejor edge que BTC por fragmentacion, menor eficiencia o venues locales. Prioriza ETH, SOL, XRP, DOGE, LTC, ADA, AVAX, LINK, SUI, TON, NEAR, APT, ARB, OP, BCH, TRX, DOT, INJ, SEI, BNB.
5. MXN/fiat/FX approaches: Bitso `BTC/MXN` o stablecoin/MXN contra precio implicito USD/MXN, siempre con haircut.
6. Market making / maker-taker / rebate approaches si las fees y la microestructura pueden producir EV positivo.
7. Spot-perp basis, funding-rate capture, CEX-DEX y latency/stat-arb solo si se pueden medir rapido y tienen path a ejecucion.

Trabajo continuo:
- Trabaja en ciclos de 60-90 minutos.
- En cada ciclo elige una hipotesis de profit, validala, decide DO NOW / MEASURE / LATER / KILL y actualiza los docs.
- Usa endpoints publicos o docs oficiales para validar fees, order book depth, min sizes, latency constraints, regional/account restrictions y quote lanes.
- Si no hay evidencia suficiente, marca confianza baja. No inventes.

Metricas obligatorias por oportunidad:
- approach_type: cross-exchange / triangular / cross-lane FX / altcoin / market-making / statistical / funding-inventory
- buy venue / sell venue
- pair/lane
- required scanner/adapter/execution work
- public market-data quality
- fee assumptions
- estimated net_bps_after_costs
- executable_notional_usd
- frequency_per_hour o proxy de evidencia
- edge_duration_ms o stale risk
- inventory/funding requirements
- implementation_hours
- risk flags
- confidence: alta/media/baja
- expected_value_score

Formula de ranking:
expected_value_score =
(net_bps_after_costs positivo)
* executable_notional_usd
* frequency_per_hour
* confidence_multiplier
/ implementation_hours

Penaliza por stale risk, regional restrictions, low liquidity, bad docs, unclear fees, inventory difficulty, or implementation complexity.

Deliverables obligatorios:
1. Escribe docs/overnight-profit-opportunities.md
   - Top 10 oportunidades rankeadas.
   - Top 3 approaches para perseguir manana primero.
   - Evidencia y links/sources por oportunidad.
   - Que codigo habria que tocar.
   - Que tests habria que agregar.
   - Config inicial recomendada: exchanges, pairs, min profit, max trade size, stale thresholds, fee assumptions.

2. Escribe docs/overnight-rejected-ideas.md
   - Ideas descartadas.
   - Razon exacta: negative after fees, cross-lane risk, low liquidity, bad API, region blocked, too slow to implement, fake edge.

3. Escribe docs/implementation-queue.md
   - Checklist ejecutable para scanner/engine/UI/research/live-readiness.
   - Ordenado por impacto.
   - Cada tarea debe ser pequena, verificable y tener acceptance criteria.

4. Cada 60-90 minutos actualiza docs/overnight-profit-checkpoints.md
   - Hallazgos nuevos.
   - Top candidates actuales.
   - Ideas descartadas.
   - Bloqueos/riesgos.

5. Escribe docs/profit-approach-playbook.md
   - Explica los 3-5 enfoques mas prometedores como playbooks: hipotesis, por que puede imprimir dinero, como medirlo, como ejecutarlo, riesgos, y stop conditions.

Criterio de exito:
Manana debo poder abrir los docs y saber exactamente:
- que approach perseguir primero,
- por que esa y no otra,
- que edge esperamos,
- que evidencia la soporta,
- que riesgo puede invalidarla,
- que archivos/codigo tocar para capturarla.

Se brutal. Si la mejor respuesta es "todavia no hay profit confiable, primero scanner + measurement", dilo. El objetivo no es sonar optimista; es maximizar la probabilidad de encontrar y capturar rendimiento real.
```
