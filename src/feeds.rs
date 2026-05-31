use crate::book::OrderBook;
use crate::model::{parse_price, parse_qty, BookEvent, Exchange, Lane, Side, VenueBook};
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use std::time::{Duration, Instant};
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};

pub fn spawn_public_feeds(tx: mpsc::Sender<BookEvent>) {
    for base in ["BTC", "ETH", "SOL", "XRP", "DOGE", "LTC"] {
        let binance_symbol = leak(format!("{base}USDT"));
        spawn_json_ws(
            "binance",
            leak(format!(
                "wss://stream.binance.com:9443/ws/{}@depth20@100ms",
                binance_symbol.to_ascii_lowercase()
            )),
            vec![],
            Exchange::Binance,
            base,
            Lane::Usdt,
            binance_symbol,
            handle_binance,
            tx.clone(),
        );

        let bybit_symbol = leak(format!("{base}USDT"));
        spawn_json_ws(
            "bybit",
            "wss://stream.bybit.com/v5/public/spot",
            vec![json!({"req_id": format!("bybit-{bybit_symbol}"), "op":"subscribe","args":[format!("orderbook.50.{bybit_symbol}")]}).to_string()],
            Exchange::Bybit,
            base,
            Lane::Usdt,
            bybit_symbol,
            handle_bybit,
            tx.clone(),
        );

        let okx_symbol = leak(format!("{base}-USDT"));
        spawn_json_ws(
            "okx",
            "wss://ws.okx.com:8443/ws/v5/public",
            vec![json!({"id":"1","op":"subscribe","args":[{"channel":"books5","instId":okx_symbol}]}).to_string()],
            Exchange::Okx,
            base,
            Lane::Usdt,
            okx_symbol,
            handle_okx,
            tx.clone(),
        );
    }

    for base in ["BTC", "ETH", "SOL"] {
        let coinbase_symbol = leak(format!("{base}-USD"));
        spawn_json_ws(
            "coinbase",
            "wss://advanced-trade-ws.coinbase.com",
            vec![
                json!({"type":"subscribe","product_ids":[coinbase_symbol],"channel":"level2"})
                    .to_string(),
                json!({"type":"subscribe","product_ids":[coinbase_symbol],"channel":"heartbeats"})
                    .to_string(),
            ],
            Exchange::Coinbase,
            base,
            Lane::Usd,
            coinbase_symbol,
            handle_coinbase,
            tx.clone(),
        );

        let kraken_symbol = leak(format!("{base}/USD"));
        spawn_json_ws(
            "kraken",
            "wss://ws.kraken.com/v2",
            vec![json!({"method":"subscribe","params":{"channel":"book","symbol":[kraken_symbol],"depth":25,"snapshot":true},"req_id":1}).to_string()],
            Exchange::Kraken,
            base,
            Lane::Usd,
            kraken_symbol,
            handle_kraken,
            tx.clone(),
        );
    }

    for base in ["BTC", "ETH"] {
        let gemini_symbol = leak(format!("{}usd", base.to_ascii_lowercase()));
        spawn_json_ws(
            "gemini",
            leak(format!(
                "wss://api.gemini.com/v1/marketdata/{gemini_symbol}?top_of_book=false&bids=true&offers=true"
            )),
            vec![],
            Exchange::Gemini,
            base,
            Lane::Usd,
            gemini_symbol,
            handle_gemini,
            tx.clone(),
        );
    }
}

type Handler = fn(
    &mut OrderBook,
    &Value,
    Instant,
    Exchange,
    &'static str,
    Lane,
    &'static str,
) -> Option<VenueBook>;

fn spawn_json_ws(
    name: &'static str,
    url: &'static str,
    subscriptions: Vec<String>,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
    handler: Handler,
    tx: mpsc::Sender<BookEvent>,
) {
    tokio::spawn(async move {
        let mut reconnects = 0_u64;
        loop {
            reconnects += 1;
            tracing::info!(exchange = name, reconnects, "connecting public websocket");
            match connect_async(url).await {
                Ok((stream, _)) => {
                    tracing::info!(exchange = name, "connected");
                    let (mut write, mut read) = stream.split();
                    for message in &subscriptions {
                        if let Err(error) = write.send(Message::Text(message.clone().into())).await
                        {
                            tracing::warn!(exchange = name, %error, "subscription send failed");
                        }
                    }

                    let mut book = OrderBook::default();
                    while let Some(message) = read.next().await {
                        let received_at = Instant::now();
                        match message {
                            Ok(Message::Text(text)) => match serde_json::from_str::<Value>(&text) {
                                Ok(value) => {
                                    if let Some(book) = handler(
                                        &mut book,
                                        &value,
                                        received_at,
                                        exchange,
                                        base,
                                        lane,
                                        symbol,
                                    ) {
                                        if tx.send(BookEvent { book }).await.is_err() {
                                            return;
                                        }
                                    } else if name == "okx" || name == "kraken" {
                                        tracing::debug!(
                                            exchange = name,
                                            raw = %value,
                                            "unhandled websocket payload"
                                        );
                                    }
                                }
                                Err(error) => {
                                    tracing::debug!(exchange = name, %error, "json parse failed")
                                }
                            },
                            Ok(Message::Ping(payload)) => {
                                let _ = write.send(Message::Pong(payload)).await;
                            }
                            Ok(Message::Close(frame)) => {
                                tracing::warn!(exchange = name, ?frame, "websocket closed");
                                break;
                            }
                            Err(error) => {
                                tracing::warn!(exchange = name, %error, "websocket error");
                                break;
                            }
                            _ => {}
                        }
                    }
                }
                Err(error) => tracing::warn!(exchange = name, %error, "connect failed"),
            }

            tokio::time::sleep(Duration::from_secs(2)).await;
        }
    });
}

fn handle_binance(
    _book: &mut OrderBook,
    value: &Value,
    received_at: Instant,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
) -> Option<VenueBook> {
    let bids = array_pairs(value.get("bids")?)?;
    let asks = array_pairs(value.get("asks")?)?;
    Some(VenueBook {
        exchange,
        base,
        lane,
        symbol,
        book: OrderBook::from_pairs(bids, asks),
        received_at,
        exchange_ts_ms: None,
        sequence: value.get("lastUpdateId").and_then(Value::as_i64),
    })
}

fn handle_bybit(
    book: &mut OrderBook,
    value: &Value,
    received_at: Instant,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
) -> Option<VenueBook> {
    let data = value.get("data")?;
    let msg_type = value.get("type").and_then(Value::as_str)?;
    let bids = array_pairs(data.get("b")?)?;
    let asks = array_pairs(data.get("a")?)?;

    if msg_type == "snapshot" {
        *book = OrderBook::from_pairs(bids, asks);
    } else {
        apply_pairs(book, Side::Bid, bids);
        apply_pairs(book, Side::Ask, asks);
    }

    if book.bids.is_empty() || book.asks.is_empty() {
        return None;
    }

    Some(VenueBook {
        exchange,
        base,
        lane,
        symbol,
        book: book.clone(),
        received_at,
        exchange_ts_ms: value.get("ts").and_then(Value::as_u64),
        sequence: data.get("seq").and_then(Value::as_i64),
    })
}

fn handle_okx(
    _book: &mut OrderBook,
    value: &Value,
    received_at: Instant,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
) -> Option<VenueBook> {
    let data = value.get("data")?.as_array()?.first()?;
    let bids = array_pairs(data.get("bids")?)?;
    let asks = array_pairs(data.get("asks")?)?;

    Some(VenueBook {
        exchange,
        base,
        lane,
        symbol,
        book: OrderBook::from_pairs(bids, asks),
        received_at,
        exchange_ts_ms: data.get("ts").and_then(as_u64_string_or_number),
        sequence: data.get("seqId").and_then(as_i64_string_or_number),
    })
}

fn handle_coinbase(
    book: &mut OrderBook,
    value: &Value,
    received_at: Instant,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
) -> Option<VenueBook> {
    if value.get("channel").and_then(Value::as_str) != Some("l2_data") {
        return None;
    }

    let events = value.get("events")?.as_array()?;
    for event in events {
        for update in event
            .get("updates")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            let side = match update.get("side").and_then(Value::as_str)? {
                "bid" | "buy" => Side::Bid,
                "offer" | "ask" | "sell" => Side::Ask,
                _ => continue,
            };
            let price = parse_price(update.get("price_level").and_then(Value::as_str)?)?;
            let qty = parse_qty(update.get("new_quantity").and_then(Value::as_str)?)?;
            book.apply_update(side, price, qty);
        }
    }

    if book.bids.is_empty() || book.asks.is_empty() {
        return None;
    }

    Some(VenueBook {
        exchange,
        base,
        lane,
        symbol,
        book: book.clone(),
        received_at,
        exchange_ts_ms: None,
        sequence: value.get("sequence_num").and_then(Value::as_i64),
    })
}

fn handle_kraken(
    book: &mut OrderBook,
    value: &Value,
    received_at: Instant,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
) -> Option<VenueBook> {
    if value.get("channel").and_then(Value::as_str) != Some("book") {
        return None;
    }
    let msg_type = value.get("type").and_then(Value::as_str)?;
    let data = value.get("data")?.as_array()?.first()?;
    let bids = object_pairs(data.get("bids")?)?;
    let asks = object_pairs(data.get("asks")?)?;

    if msg_type == "snapshot" {
        *book = OrderBook::from_pairs(bids, asks);
    } else {
        apply_pairs(book, Side::Bid, bids);
        apply_pairs(book, Side::Ask, asks);
    }

    Some(VenueBook {
        exchange,
        base,
        lane,
        symbol,
        book: book.clone(),
        received_at,
        exchange_ts_ms: None,
        sequence: None,
    })
}

fn handle_gemini(
    book: &mut OrderBook,
    value: &Value,
    received_at: Instant,
    exchange: Exchange,
    base: &'static str,
    lane: Lane,
    symbol: &'static str,
) -> Option<VenueBook> {
    let events = value.get("events")?.as_array()?;
    for event in events {
        if event.get("type").and_then(Value::as_str) != Some("change") {
            continue;
        }
        let side = match event.get("side").and_then(Value::as_str)? {
            "bid" => Side::Bid,
            "ask" | "offer" => Side::Ask,
            _ => continue,
        };
        let price = parse_price(event.get("price").and_then(Value::as_str)?)?;
        let qty = parse_qty(event.get("remaining").and_then(Value::as_str)?)?;
        book.apply_update(side, price, qty);
    }

    if book.bids.is_empty() || book.asks.is_empty() {
        return None;
    }

    Some(VenueBook {
        exchange,
        base,
        lane,
        symbol,
        book: book.clone(),
        received_at,
        exchange_ts_ms: value.get("timestampms").and_then(Value::as_u64),
        sequence: value.get("socket_sequence").and_then(Value::as_i64),
    })
}

fn array_pairs(value: &Value) -> Option<Vec<(String, String)>> {
    Some(
        value
            .as_array()?
            .iter()
            .filter_map(|level| {
                let row = level.as_array()?;
                Some((value_to_string(row.get(0)?)?, value_to_string(row.get(1)?)?))
            })
            .collect(),
    )
}

fn object_pairs(value: &Value) -> Option<Vec<(String, String)>> {
    Some(
        value
            .as_array()?
            .iter()
            .filter_map(|level| {
                if let Some(row) = level.as_array() {
                    return Some((value_to_string(row.get(0)?)?, value_to_string(row.get(1)?)?));
                }

                Some((
                    value_to_string(level.get("price")?)?,
                    value_to_string(level.get("qty").or_else(|| level.get("size"))?)?,
                ))
            })
            .collect(),
    )
}

fn value_to_string(value: &Value) -> Option<String> {
    if let Some(text) = value.as_str() {
        return Some(text.to_string());
    }
    if let Some(number) = value.as_i64() {
        return Some(number.to_string());
    }
    if let Some(number) = value.as_u64() {
        return Some(number.to_string());
    }
    if let Some(number) = value.as_f64() {
        return Some(number.to_string());
    }
    None
}

fn apply_pairs(book: &mut OrderBook, side: Side, pairs: Vec<(String, String)>) {
    for (price, qty) in pairs {
        if let (Some(price), Some(qty)) = (parse_price(&price), parse_qty(&qty)) {
            book.apply_update(side, price, qty);
        }
    }
}

fn as_u64_string_or_number(value: &Value) -> Option<u64> {
    value.as_u64().or_else(|| value.as_str()?.parse().ok())
}

fn as_i64_string_or_number(value: &Value) -> Option<i64> {
    value.as_i64().or_else(|| value.as_str()?.parse().ok())
}

fn leak(value: String) -> &'static str {
    Box::leak(value.into_boxed_str())
}
