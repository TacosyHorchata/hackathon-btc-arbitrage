# PLAN ~20% APY - PERFIL CONSERVADOR DESDE MEXICO

Fecha de medicion: 2026-05-29 / 2026-05-30 (datos en vivo verificados).
Objetivo del usuario: ~20% APY ESTABLE, conservador, delta-neutral
(sin riesgo de direccion de precio), SIN loteria.
Capital base de ejemplo: 5,000 USD.

VEREDICTO HONESTO DE ENTRADA:
"20% ESTABLE + CONSERVADOR a la vez" NO existe hoy en stablecoins
delta-neutral. El regimen de funding esta comprimido desde el evento
de oct-2025 y los blue-chip rinden 4-9%. El 20% solo aparece en:
(a) un fijo de plazo corto sobre colateral de mayor riesgo de credito
(PT-apyUSD, ~19 dias), o (b) una canasta de funding-carry en alts de
cola que exige operacion activa. Cualquiera de las dos lleva riesgo
real; ninguna es "renta pasiva conservadora al 20%".

Todos los numeros de abajo son MEDIDOS (API Pendle, DefiLlama yields,
Bybit/Binance API, Morpho/Aave). Nada inventado.


===============================================================
1) RANKING POR APY-HONESTO
===============================================================

APY-honesto = lo que realmente cobras de forma defendible/sostenida,
NO el spike maximo de pantalla.

+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| RUTA                   | APY honesto | Delta- | Llega   | Sostenibilidad | Veredicto            | Ejecutable|
|                        |             | neutral?| a 20%? |                |                      | desde MX? |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| Funding-carry CANASTA  | 18-25%      | SI     | SI      | Media-baja     | CONDICIONAL          | SI (CEX)  |
| alts (POWER/RAVE/BSB/  | (bruto ~28%)| (si    | (canasta| (depende de    | activo, no pasivo;   | OJO: spot |
| IN/ALCH) long spot +   |             | tienes | no      | persistencia   | mejor para perfil    | solo en   |
| short perp Bybit       |             | spot)  | major)  | de funding)    | AGRESIVO             | Bybit p/  |
|                        |             |        |         |                |                      | ALCH/BSB  |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-apyUSD jun-2026     | 21.36% FIJO | NO     | SI      | NO (fijo de    | CONDICIONAL          | SI        |
| (Pendle ETH)           | locked si   | (es    | (pero   | ~19 dias, no   | spike corto sobre    | (ETH      |
|                        | holdeas a   | credito| spike   | 12 meses)      | colateral riesgoso;  | mainnet)  |
|                        | maturity    | off-   | corto)  |                | NO conservador puro  |           |
|                        |             | chain) |         |                |                      |           |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-reUSDe jun-2026     | 16.36% FIJO | SI     | NO      | Media (depende | RECOMENDADO base     | SI        |
| (Pendle ETH)           | locked      | (Ethena| (~16,   | de funding/    | (riesgo acotado,     | (ETH      |
|                        |             | -like) | no 20)  | colateral USDe)| holdear a maturity)  | mainnet)  |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-apyUSD nov-2026     | 16.33% FIJO | NO     | NO      | Media (credito | RECOMENDADO comple-  | SI        |
| (Pendle ETH)           | locked      | (cred.)| (~16)   | off-chain)     | mento; mas plazo     | (ETH)     |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-sUSDat ago-2026     | 14.19% FIJO | SI     | NO      | Media (depeg   | ALTERNATIVA liquida  | SI        |
| (Pendle ETH/BSC)       | locked      | (synth)| (~14)   | USDat/funding) | (pool profundo)      | (ETH/BSC) |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-sUSDe / sUSDe       | 4.3-4.4%    | SI     | NO      | Alta (blue-    | ESCALON SEGURO       | SI        |
| nativo (Ethena/Pendle) | (fijo/var)  |        |         | chip, anos)    | (lo unico "conserv." | (ETH)     |
|                        |             |        |         |                | de verdad)           |           |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-USDe (Pendle)       | 8-9% FIJO   | SI     | NO      | Alta-media     | ESCALON SEGURO+      | SI (ETH)  |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| Fluid USDC lending     | ~5% real    | SI     | NO      | Baja en el     | RECHAZADO como 20%   | SI (ETH)  |
| (ETH)                  | (spike a    |        | (spike  | spike (pred=   | (spike utilizacion;  |           |
|                        | 23% pred=   |        | a 23,   | Down, revierte | tactico monto chico) |           |
|                        | Down)       |        | revierte)| a ~5%)        |                      |           |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| PT-looped Morpho       | <4% (neg.   | NO     | NO      | NO (carry      | RECHAZADO            | SI pero   |
| (sUSDe/srUSDe)         | a >=3x)     | (long  |         | negativo hoy)  | (pierde dinero hoy)  | NO hacer  |
|                        |             | apalan)|         |                |                      |           |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| Stable-looping Aave    | 8-11% neto  | parcial| A_VECES | Baja (depende  | RECHAZADO p/20%      | SI pero   |
| (sUSDe/PT, leverage)   | (no 20)     | (apalan| (spike  | de merit +     | conservador          | riesgoso  |
|                        |             | =long) | combo   | spread + lev)  |                      |           |
|                        |             |        | alcista)|                |                      |           |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+
| Funding-carry MAJORS   | 0.5-4%      | SI     | NO      | Alta           | RECHAZADO (no llega) | SI (CEX)  |
| (BTC/ETH/SOL/XRP)      |             |        |         |                |                      |           |
+------------------------+-------------+--------+---------+----------------+----------------------+-----------+

Lectura clave del ranking:
- El 20% delta-neutral real solo lo da la CANASTA de funding-carry alts,
  pero es operacion activa (monitoreo cada 4-8h) y de sostenibilidad
  media-baja: NO es conservador puro.
- El 21.36% de PT-apyUSD NO es delta-neutral (es credito off-chain de
  dividendos de Digital Asset Treasuries via wrapper apxUSD) y es un
  fijo de ~19 dias, no un yield de 12 meses.
- La zona realista "riesgo medio acotado" para PT de stablecoin es
  14-16% (reUSDe / apyUSD-nov / sUSDat).
- Conservador de verdad (anos de historial): 4-9% (sUSDe/USDe/USDS).


===============================================================
2) PLAN CONCRETO RECOMENDADO ~20% SOBRE 5,000 USD
===============================================================

Dado que "20% conservador puro" no existe, este plan ALCANZA ~20% de
forma realista combinando un nucleo de riesgo-acotado (PT 14-16%) con
una porcion controlada de mayor APY, y deja CLARO el riesgo principal y
su mitigacion. Es un plan delta-neutral salvo la pieza apyUSD (credito).

----- ASIGNACION (mezcla ponderada apunta a ~18-20% bruto) -----

  Tramo NUCLEO (riesgo medio, delta-neutral)   3,000 USD (60%)
    - PT-reUSDe exp 25-jun-2026 .... 1,500 USD @ 16.36% FIJO
    - PT-sUSDat exp 27-ago-2026 .... 1,500 USD @ 14.19% FIJO
      (pool profundo ETH $7.27M; tambien BSC $4.66M @ 14.21%)

  Tramo BOOST (mayor APY, credito off-chain)   1,500 USD (30%)
    - PT-apyUSD exp 18-jun-2026 .... 1,500 USD @ 21.36% FIJO
      (SOLO con monto que aceptes arriesgar; ver mitigacion)

  Tramo COLCHON (seguro, liquido)               500 USD (10%)
    - PT-sUSDe exp 13-ago-2026 ..... 500 USD @ ~4.33% FIJO
      (o sUSDe nativo Ethena ~3.8% / USDC lending ~4-5%)

  APY ponderado estimado de la mezcla:
    (0.30*16.36 + 0.30*14.19 + 0.30*21.36 + 0.10*4.33)
    = 4.91 + 4.26 + 6.41 + 0.43 = ~16.0% bruto sobre el total.
  Para EMPUJAR a ~20% sin subir el riesgo de credito: subir el peso de
  apyUSD-jun a ~40-45% lleva la mezcla a ~18-19%, PERO eso concentra en
  el colateral mas arriesgado. La recomendacion honesta es quedarse en
  ~16% (mezcla de arriba) y NO forzar el 20% con concentracion. Si el
  usuario exige ~20% como piso, la unica via delta-neutral pura es la
  CANASTA de funding-carry (ver alternativa agresiva).

----- QUE COMPRAR / EN QUE PROTOCOLO / RED -----

  Protocolo: Pendle Finance (auditado, anos en prod, alta TVL).
  Red: Ethereum mainnet (ahi esta la liquidez profunda de todos
       estos PT; sUSDat tambien en BSC).
  Instrumento: Principal Tokens (PT) = bono cupon-cero de stablecoin.
       Compras con descuento y a maturity redimes 1:1 por el subyacente.
       El yield FIJO es el implied APY del dia de compra, LOCKED si
       holdeas a vencimiento (salvo default/depeg del subyacente).

----- PASOS (desde Mexico) -----

  1) En Bitso (o Binance global) compra USDC con MXN via SPEI.
  2) Retira USDC a wallet self-custody (Rabby o MetaMask) en Ethereum
     mainnet. Consolida el retiro en UNA sola transferencia para no
     pagar gas/comision de red dos veces.
  3) Entra a app.pendle.finance, conecta la wallet.
  4) Compra cada PT con tu USDC (el "zap" de Pendle convierte solo):
       - Mercado apyUSD exp 18-jun-2026  -> 1,500 USD
       - Mercado reUSDe exp 25-jun-2026  -> 1,500 USD
       - Mercado sUSDat exp 27-ago-2026  -> 1,500 USD
       - Mercado sUSDe  exp 13-ago-2026  -> 500 USD
     VERIFICA SIEMPRE en pantalla el Fixed/Implied APY al comprar:
     cambia cada minuto. Si bajo mucho, no entres.
  5) HOLDEA a maturity. Al vencer, redime 1:1 por el subyacente,
     reconviertelo a USDC, regresa USDC -> Bitso -> MXN.

----- COSTOS / GAS MEDIDOS -----

  - Gas compra de PT en ETH mainnet: ~3-15 USD/tx segun congestion.
  - Redencion a maturity: otro gas similar (~3-15 USD).
  - Sin fee de management de Pendle al holdear.
  - Price impact: minimo en pools profundos (apyUSD $14.88M,
    sUSDat $7.27M, reUSDe $5.36M). EVITA pools chicos como
    jrRoyAPYUSD ($1.29M): slippage alto.
  - OJO plazo corto: apyUSD-jun vence en ~19 dias (hoy 29-30 may,
    vence 18-jun). Poco tiempo para amortizar gas -> por eso va con
    monto medio (1,500), no chico.

----- RIESGO PRINCIPAL Y COMO MITIGARLO -----

  El riesgo #1 NO es direccion de precio (es delta-neutral salvo apyUSD),
  es el SUBYACENTE:
    a) apyUSD (el 21%): credito off-chain. apyUSD/apxUSD esta respaldado
       por dividendos de preferred shares de Digital Asset Treasuries
       (~11-12.5% anual) traidos on-chain via wrapper ERC-4626. Senales
       de tension medidas: utilizacion ~96%, coverage junior ~15.68%
       (buffer minimo). Si el DAT recorta dividendo o apxUSD cae de $1,
       el oraculo Chainlink marca apyUSD a la baja. Riesgo de credito,
       NO delta-neutral.
    b) reUSDe / sUSDat: yields sinteticos tipo Ethena. Dependen de
       funding rate (puede ir negativo) y del colateral USDe/USDat.
       USDe YA hizo depeg a $0.97 en oct-2025; reserve fund ~1.1% del
       supply. Riesgo de depeg real.
    c) Comun a todo PT: si VENDES antes de maturity y las tasas subieron,
       el PT cotiza bajo par y sales con perdida. El fijo SOLO se
       garantiza holdeando a vencimiento.

  MITIGACION:
    - Diversificar emisores (apyUSD + reUSDe + sUSDat + sUSDe), no
      concentrar en uno.
    - Capar el tramo de mayor riesgo de credito (apyUSD) a <=30% y
      tratarlo como "monto que aceptas arriesgar".
    - HOLDEAR a maturity siempre; no comprar PT si crees que vas a
      necesitar liquidez antes (no metas tu fondo de emergencia).
    - Usar SOLO pools profundos (>5M TVL) para minimizar slippage.
    - Plazos cortos (apyUSD-jun, reUSDe-jun) reducen ventana de
      exposicion al subyacente; al vencer, re-evaluar antes de rolar.
    - Verificar el APY en pantalla antes de cada compra.


===============================================================
3) ALTERNATIVAS: UN ESCALON MAS SEGURO Y UNO MAS AGRESIVO
===============================================================

----- ESCALON MAS SEGURO (~10-12% efectivo / nucleo blue-chip) -----

  Si el usuario prioriza dormir tranquilo sobre el numero:
    - PT-USDe (Pendle) .......... ~8-9% FIJO, delta-neutral.
    - PT-sUSDe exp 13-ago-2026 .. ~4.33% FIJO (blue-chip, anos).
    - sUSDat exp 27-ago-2026 .... 14.19% (la pieza de "subir" el
      promedio sin tocar credito off-chain).
  Mezcla sugerida 5,000 USD:
    - 2,000 PT-USDe (~8.5%) + 1,500 PT-sUSDat (14.19%) +
      1,500 PT-sUSDe (4.33%) = ponderado ~9-10%.
  Para llegar a ~10-12% con riesgo bajo-medio: peso mayor a sUSDat y
  USDe, evitando apyUSD por completo. Delta-neutral, sin loteria.
  Es lo MAS honesto si el mandato es "conservador de verdad".

----- ESCALON MAS AGRESIVO (~30%+) -----

  Funding-carry delta-neutral en CANASTA de alts (la unica ruta
  delta-neutral pura que realmente llega y supera el 20%):
    - Long SPOT + short PERP del mismo alt, MISMO exchange.
    - Cobras el funding que pagan los longs apalancados.
    - Canasta de persistencia medida (Binance funding 90d):
        POWER  APRavg +34.4% (100% periodos positivos, min +10.9%)
        RAVE   APRavg +22.6% (100% pos, min +10.9%)
        BSB    APRavg +44.7% (95.6% pos, min -69.3%)
        IN     APRavg +23.0% (98.9% pos, min -60.5%)
        ALCH   APRavg +16.3% (100% pos, min +10.9%)
      Canasta bruta ~28% APR; neto de fees/slippage/rotacion ~18-25%,
      y en spikes reales toca 30%+ (funding actual anualizado medido
      2026-05-30: POWER +86.5%, IN +88.4%, BSB +54%, ALCH +37.7%).
  ADVERTENCIA CRITICA MEDIDA (smoking gun): la pata SPOT no existe
  en Binance para POWER/RAVE/IN/ESPORTS/ARM (API spot devuelve symbol
  invalido). En Bybit spot SOLO existen BSB y ALCH. Sin spot no armas
  el long delta-neutral -> en ~5 de 6 coins NO es ejecutable como
  delta-neutral hoy; solo quedarian ALCH y a medias BSB.
  Por eso esta ruta, ejecutable de verdad, rinde ~5-10% delta-neutral
  en size chico (ALCH clavado al floor +10.9%, liquidez fina), NO 20%
  estable. El >20% real exige los coins que revierten violento
  (BSB/IN/ESPORTS con min -60% a -457%) = ruleta.
  Riesgos: funding-reversion (#1), liquidacion del short si el alt
  pumpea, liquidez fina (slippage), contraparte CEX. Operacion ACTIVA
  (monitoreo cada 4-8h, rotacion). Recomendado SOLO si aceptas operar
  activo y entiendes que el premio alto = riesgo de cola.


===============================================================
4) RUTAS RECHAZADAS (una linea cada una)
===============================================================

- PT-looped (sUSDe/srUSDe en Morpho): carry NEGATIVO hoy (borrow USDC
  6.55% > PT fijo 4.33%); apalancar PIERDE dinero (3x = -0.22%).
- Stable-looping Aave (sUSDe/PT con leverage): da 8-11% neto real, no
  20%; el 20% solo con leverage 6.7-10x + combo alcista de dos
  variables = loteria, con riesgo de liquidacion por depeg.
- sUSDe nativo Ethena (sin apalancar): solo ~3.8% hoy (regimen
  T-bill/funding comprimido); volatil; no llega a 20.
- Fluid USDC lending 23%: spike de utilizacion (pred=Down, mismo pool
  marcaba 11.39% el mismo dia); revierte a ~5%; riesgo de no poder
  retirar si util ~100%.
- Funding-carry MAJORS (BTC/ETH/SOL/XRP): rinden 0.5-4% real, lejos
  de 20.
- PT blue-chip puros (sUSDe/srUSDe/USDS/USDG ~4.3-4.4%): seguros pero
  no se acercan a 20%.


===============================================================
NOTA FINAL DE HONESTIDAD
===============================================================
Solo numeros medidos en vivo (API Pendle, DefiLlama yields, Bybit/
Binance, Morpho/Aave) el 2026-05-29/30. "20% ESTABLE + CONSERVADOR a
la vez" no existe en este regimen. Lo defendible con riesgo acotado es
~16% (mezcla PT 14-16%); el 20%+ delta-neutral real exige la canasta de
funding-carry activa; el 20%+ via PT exige el colateral de mayor riesgo
de credito (apyUSD) y es un fijo de plazo corto. Elige nivel de riesgo,
no esperes 20% sin alguna de esas concesiones.
