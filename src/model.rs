use crate::book::OrderBook;
use std::fmt;
use std::time::Instant;

pub const PRICE_SCALE: i64 = 100_000_000; // 1e-8 quote units for USD/USDT/MXN lanes
pub const QTY_SCALE: i64 = 100_000_000; // 1e-8 base units

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Lane {
    Usd,
    Usdt,
}

impl fmt::Display for Lane {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Lane::Usd => write!(f, "USD"),
            Lane::Usdt => write!(f, "USDT"),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Exchange {
    Binance,
    Bybit,
    Okx,
    Coinbase,
    Kraken,
    Gemini,
}

impl Exchange {
    pub fn as_str(self) -> &'static str {
        match self {
            Exchange::Binance => "binance",
            Exchange::Bybit => "bybit",
            Exchange::Okx => "okx",
            Exchange::Coinbase => "coinbase",
            Exchange::Kraken => "kraken",
            Exchange::Gemini => "gemini",
        }
    }
}

impl fmt::Display for Exchange {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

#[derive(Debug, Clone)]
pub struct VenueBook {
    pub exchange: Exchange,
    pub base: &'static str,
    pub lane: Lane,
    pub symbol: &'static str,
    pub book: OrderBook,
    pub received_at: Instant,
    pub exchange_ts_ms: Option<u64>,
    pub sequence: Option<i64>,
}

impl VenueBook {
    pub fn key(&self) -> MarketVenueKey {
        MarketVenueKey {
            exchange: self.exchange,
            base: self.base,
            lane: self.lane,
        }
    }

    pub fn market(&self) -> MarketKey {
        MarketKey {
            base: self.base,
            lane: self.lane,
        }
    }

    pub fn best_bid(&self) -> Option<i64> {
        self.book.bids.first().map(|level| level.price)
    }

    pub fn best_ask(&self) -> Option<i64> {
        self.book.asks.first().map(|level| level.price)
    }

    pub fn is_crossed(&self) -> bool {
        match (self.best_bid(), self.best_ask()) {
            (Some(bid), Some(ask)) => bid >= ask,
            _ => true,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct MarketKey {
    pub base: &'static str,
    pub lane: Lane,
}

impl fmt::Display for MarketKey {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}/{}", self.base, self.lane)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct MarketVenueKey {
    pub exchange: Exchange,
    pub base: &'static str,
    pub lane: Lane,
}

#[derive(Debug)]
pub struct BookEvent {
    pub book: VenueBook,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Level {
    pub price: i64,
    pub qty: i64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Side {
    Bid,
    Ask,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Fill {
    pub qty: i64,
    pub quote_units: i128,
    pub avg_price: i64,
}

pub fn parse_price(raw: &str) -> Option<i64> {
    parse_scaled_decimal(raw, PRICE_SCALE)
}

pub fn parse_qty(raw: &str) -> Option<i64> {
    parse_scaled_decimal(raw, QTY_SCALE)
}

pub fn parse_scaled_decimal(raw: &str, scale: i64) -> Option<i64> {
    let text = raw.trim();
    if text.is_empty() || text.starts_with('-') {
        return None;
    }

    let (whole, frac) = match text.split_once('.') {
        Some(parts) => parts,
        None => (text, ""),
    };

    let whole_value = if whole.is_empty() {
        0
    } else {
        whole.parse::<i64>().ok()?
    };

    let mut frac_value = 0_i64;
    let mut multiplier = scale / 10;
    for ch in frac.chars() {
        if multiplier == 0 {
            break;
        }
        let digit = ch.to_digit(10)? as i64;
        frac_value += digit * multiplier;
        multiplier /= 10;
    }

    whole_value.checked_mul(scale)?.checked_add(frac_value)
}

pub fn format_price(price: i64) -> String {
    format_scaled(price, PRICE_SCALE, 8)
}

pub fn format_qty(qty: i64) -> String {
    format_scaled(qty, QTY_SCALE, 8)
}

pub fn format_money(quote_units: i128) -> String {
    let sign = if quote_units < 0 { "-" } else { "" };
    let abs = quote_units.abs();
    format!(
        "{sign}{}.{:08}",
        abs / PRICE_SCALE as i128,
        abs % PRICE_SCALE as i128
    )
}

fn format_scaled(value: i64, scale: i64, decimals: usize) -> String {
    let sign = if value < 0 { "-" } else { "" };
    let abs = value.abs();
    format!(
        "{sign}{}.{:0width$}",
        abs / scale,
        abs % scale,
        width = decimals
    )
}
