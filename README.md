# BTC Arbitrage Bot Simulator

Repositorio para el **Coding Challenge Mexico: Arbitraje de Bitcoin**. La app
monitorea order books publicos de BTC en multiples exchanges, detecta rutas
ask < bid, calcula rentabilidad neta con costos reales, simula ejecucion
buy/sell, actualiza wallets prefundeadas y muestra P&L en una web app.

La tesis tecnica es simple: **el bot que gana no imprime P&L falso**. La mayoria
de los spreads visibles mueren al incluir profundidad, fees, latencia,
rebalance/retiro, stale books e inventario. Este sistema los rechaza con
evidencia y solo simula fills cuando sobreviven todos los filtros.

## Live Demo

Demo publica para el jurado: **https://hackathon-btc-arb.fly.dev**

## Judge In 60 Seconds

1. Abre https://hackathon-btc-arb.fly.dev.
2. Deja el modo `LIVE`: veras order books reales, rutas evaluadas y rechazos
   explicados. Esto es intencional; BTC liquido rara vez sobrevive costos.
3. Haz click en cualquier ruta: el inspector muestra waterfall por profundidad,
   VWAP, fees, latencia, reserva de rebalance/retiro, net bps y decision.
4. Cambia a `STRESS`: la app etiqueta una dislocacion simulada y demuestra la
   ruta completa de ejecucion, drift de wallets y P&L.
5. Regresa a `LIVE`: el motor vuelve a operar con libros y costos reales.

## Por Que Esta Solucion Compite Para Ganar

- **Real market data**: 7 venues publicos: Coinbase, Kraken, Gemini, Bitfinex,
  Binance, Bybit y OKX.
- **Deteccion eficiente**: polling REST concurrente cada 3s en la web app; el
  scanner Rust incluido soporta feeds WebSocket/event-driven para hot path.
- **Calculo neto serio**: depth-aware VWAP, taker fees por exchange, slippage
  por profundidad, latency haircut, reserva de rebalance/retiro y min edge.
- **No mezcla USD con USDT**: las rutas solo comparan venues dentro de la misma
  lane. No hay arbitraje falso por basis entre activos distintos.
- **Parciales e inventario**: si el bucket completo no cabe, evalua el fill
  parcial simetrico; cada venue tiene wallet propia y nunca puede ir negativa.
- **Risk controls**: stale-book rejection, max notional, min notional, min net
  bps, route prioritization, one accepted route per venue per cycle, inventory
  caps y configuracion validada.
- **Trazabilidad**: cada aceptacion/rechazo tiene razon e evidencia inspeccionable.
- **Presentacion**: dashboard en vivo con feeds, rutas, decisiones, trades,
  wallets, equity y realized P&L.

## Challenge Requirements -> Implementacion

| Requisito | Implementacion |
|---|---|
| Monitoreo real-time de order books BTC | `app/server.py` fetch concurrente, 7 venues, ciclo 3s; `src/` incluye scanner Rust WebSocket |
| Deteccion ask < bid | `Engine.eval_route()` evalua cada ruta dirigida dentro de la misma quote lane |
| Rentabilidad neta | VWAP de libro, taker fees, latency haircut, reserva rebalance/retiro, min edge |
| Ejecucion simulada | `Wallets.apply()` actualiza buy/sell venues; `Engine._record_trade()` registra fills |
| Costos reales | Fees por venue, slippage por profundidad, latencia y costo configurable de rebalance/retiro |
| Ordenes parciales | Si no cabe el bucket, recalcula el tamano simetrico ejecutable antes de rechazar |
| Wallet balances | Quote/base por venue, prefunded inventory, guard invariant contra saldos negativos |
| Historial y P&L | SQLite + buffers in-memory, `/api/opportunities`, `/api/trades`, `/api/pnl` |
| Web app desplegada | Fly.io app publica, frontend vanilla sin build step |
| README / decisiones tecnicas | Este README + `app/README.md` + `docs/` |

## Architecture

```text
Browser dashboard
  app/static/index.html
  app/static/app.js
  app/static/styles.css
        |
        | HTTP/JSON
        v
Python stdlib backend
  ThreadingHTTPServer
  concurrent REST fetcher
  arbitrage engine
  wallet ledger
  SQLite history
        |
        | public market APIs
        v
Coinbase / Kraken / Gemini / Bitfinex / Binance / Bybit / OKX
```

El repo tambien incluye un scanner Rust (`src/`) para el hot path de mercado:
WebSockets, libros normalizados, fixed-point math, fees por exchange y pruebas
unitarias del motor.

## Net Profit Formula

```text
buy_fee       = buy_notional * buy_taker_fee_bps / 10000
sell_fee      = sell_notional * sell_taker_fee_bps / 10000
latency_cost  = buy_notional * latency_bps / 10000
rebalance_res = buy_notional * rebalance_bps / 10000

buy_debit     = buy_notional + buy_fee + latency_cost + rebalance_res
sell_credit   = sell_notional - sell_fee
net_profit    = sell_credit - buy_debit
net_bps       = net_profit / buy_debit * 10000
```

`buy_notional` y `sell_notional` salen de caminar el L2 order book, no del
top-of-book. A mayor tamano, el VWAP empeora y el edge se comprime.

## Execution Modes

- `LIVE`: libros reales + fees reales + costos. Modo honesto.
- `ZERO-FEE`: libros reales con taker fees en cero para sensibilidad de edge.
- `STRESS`: libros reales + dislocacion sell-side simulada y etiquetada. Sirve
  para demostrar ejecucion, wallet drift y P&L sin fingir que el mercado real
  regalo ese edge.

## Run Locally

```bash
python3 app/server.py
# open http://localhost:8080

PORT=9000 python3 app/server.py
```

No requiere `pip install`: backend Python stdlib, frontend estatico.

## Rust Scanner

```bash
cargo run
cargo test
```

Scope actual:

- BTC/ETH/SOL en venues USD donde aplica.
- BTC/ETH/SOL/XRP/DOGE/LTC en venues USDT.
- Fixed-point money math.
- VWAP por profundidad.
- Fee schedules por exchange.
- Event-driven route scanning.

## API

```text
GET  /api/state
GET  /api/opportunities?limit=150
GET  /api/trades
GET  /api/pnl
GET  /api/wallets
GET  /api/decision/<id>
GET  /api/summary
POST /api/config
```

`POST /api/config` esta validado con rangos conservadores para evitar demos con
fees negativos o parametros absurdos.

## Tests / Verification

```bash
python3 -m py_compile app/server.py
python3 -m unittest tests/test_app_server.py
cargo test
```

Las pruebas Python cubren validacion de config y fills parciales del deliverable
web. Las pruebas Rust cubren parsing fixed-point, normalizacion de libros, VWAP
por profundidad, crossed books, lanes USD/USDT y fee math.

## Assumptions

- La web app usa polling REST concurrente porque todos los venues exponen APIs
  publicas sin API keys. El scanner Rust muestra el camino WebSocket/event-driven.
- La ejecucion es simulada; no envia ordenes reales ni requiere credenciales.
- El arbitraje hot path usa inventario prefundeado; la reserva de
  rebalance/retiro modela el costo de sostener la estrategia despues del fill.
- Si un datacenter bloquea Binance/Bybit, el sistema degrada y opera con los
  venues alcanzables.

## Core Engineering Decision

Un bot promedio detecta spreads brutos. Un bot serio decide **no operar** cuando
el edge es falso. Esta app esta disenada para mostrar esa disciplina con numeros
auditables por el jurado.
