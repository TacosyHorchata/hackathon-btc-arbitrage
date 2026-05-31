use btc_arb_engine::book::OrderBook;
use btc_arb_engine::fees::{default_taker_bps_x100, fee_for_notional, format_bps_x100};
use btc_arb_engine::model::{
    parse_price, parse_qty, Exchange, Lane, Level, Side, VenueBook, PRICE_SCALE, QTY_SCALE,
};
use std::time::Instant;

#[test]
fn parses_fixed_point_without_float_math() {
    assert_eq!(parse_price("70000.25"), Some(7_000_025_000_000));
    assert_eq!(parse_qty("0.01000000"), Some(1_000_000));
}

#[test]
fn normalizes_book_sides_in_market_order() {
    let book = OrderBook::from_pairs(
        vec![
            ("100.00".to_string(), "1.0".to_string()),
            ("101.00".to_string(), "1.0".to_string()),
        ],
        vec![
            ("103.00".to_string(), "1.0".to_string()),
            ("102.00".to_string(), "1.0".to_string()),
        ],
    );

    assert_eq!(book.bids[0].price, parse_price("101.00").unwrap());
    assert_eq!(book.asks[0].price, parse_price("102.00").unwrap());
}

#[test]
fn zero_size_update_removes_level() {
    let mut book = OrderBook::default();
    let price = parse_price("100.00").unwrap();
    book.apply_update(Side::Bid, price, parse_qty("1.0").unwrap());
    book.apply_update(Side::Bid, price, 0);
    assert!(book.bids.is_empty());
}

#[test]
fn vwap_consumes_depth_not_only_top_of_book() {
    let book = OrderBook {
        bids: vec![],
        asks: vec![
            Level {
                price: parse_price("100.00").unwrap(),
                qty: parse_qty("0.005").unwrap(),
            },
            Level {
                price: parse_price("102.00").unwrap(),
                qty: parse_qty("0.005").unwrap(),
            },
        ],
    };

    let fill = book.buy_vwap(QTY_SCALE / 100).unwrap();
    assert_eq!(fill.qty, QTY_SCALE / 100);
    assert_eq!(fill.avg_price, parse_price("101.00").unwrap());
}

#[test]
fn lane_enum_separates_usd_and_usdt() {
    assert_ne!(Lane::Usd, Lane::Usdt);
}

#[test]
fn crossed_books_are_invalid() {
    let book = OrderBook {
        bids: vec![Level {
            price: parse_price("101.00").unwrap(),
            qty: parse_qty("1").unwrap(),
        }],
        asks: vec![Level {
            price: parse_price("100.00").unwrap(),
            qty: parse_qty("1").unwrap(),
        }],
    };

    let venue = VenueBook {
        exchange: Exchange::Gemini,
        base: "BTC",
        lane: Lane::Usd,
        symbol: "btcusd",
        book,
        received_at: Instant::now(),
        exchange_ts_ms: None,
        sequence: None,
    };

    assert!(venue.is_crossed());
}

#[test]
fn exchange_fee_defaults_are_not_global_placeholder() {
    assert_eq!(default_taker_bps_x100(Exchange::Binance), 1_000);
    assert_eq!(default_taker_bps_x100(Exchange::Bybit), 1_000);
    assert_eq!(default_taker_bps_x100(Exchange::Okx), 1_000);
    assert_eq!(default_taker_bps_x100(Exchange::Coinbase), 12_000);
    assert_eq!(default_taker_bps_x100(Exchange::Kraken), 4_000);
    assert_eq!(default_taker_bps_x100(Exchange::Gemini), 12_000);
}

#[test]
fn fee_math_supports_fractional_bps() {
    let notional = 500_i128 * PRICE_SCALE as i128;
    assert_eq!(fee_for_notional(notional, 1_000), 50_000_000);
    assert_eq!(fee_for_notional(notional, 675), 33_750_000);
    assert_eq!(format_bps_x100(675), "6.75");
}
