use crate::fees::{
    default_taker_bps_x100, fee_for_notional, format_bps_x100, BPS_SCALE,
};
use crate::model::{
    format_money, format_price, format_qty, parse_scaled_decimal, Exchange, Lane, MarketKey,
    MarketVenueKey, VenueBook, PRICE_SCALE, QTY_SCALE,
};
use std::collections::HashMap;
use std::env;
use std::time::{Duration, Instant};

#[derive(Debug, Clone)]
pub struct EngineConfig {
    pub max_notional_quote: i128,
    pub min_print_profit_quote: i128,
    pub min_required_bps: i64,
    pub override_taker_fee_bps_x100: Option<i128>,
    pub latency_buffer_bps: i128,
    pub stale_usd: Duration,
    pub stale_usdt: Duration,
}

impl Default for EngineConfig {
    fn default() -> Self {
        Self {
            min_print_profit_quote: 0,
            max_notional_quote: 500_i128 * PRICE_SCALE as i128, // $500 notional per candidate
            min_required_bps: 1,
            override_taker_fee_bps_x100: None,
            latency_buffer_bps: 2,
            stale_usd: Duration::from_millis(2500),
            stale_usdt: Duration::from_millis(1500),
        }
    }
}

impl EngineConfig {
    pub fn from_env() -> Self {
        let mut config = Self::default();
        if let Some(value) = parse_quote_env("ARB_MAX_NOTIONAL") {
            config.max_notional_quote = value;
        }
        if let Some(value) = parse_quote_env("ARB_MIN_PRINT_PROFIT") {
            config.min_print_profit_quote = value;
        }
        if let Some(value) = parse_i64_env("ARB_MIN_GROSS_BPS") {
            config.min_required_bps = value;
        }
        if let Some(value) = parse_i128_env("ARB_FEE_BPS") {
            config.override_taker_fee_bps_x100 = Some(value * BPS_SCALE);
        }
        if let Some(value) = parse_bps_x100_env("ARB_FEE_BPS_X100") {
            config.override_taker_fee_bps_x100 = Some(value);
        }
        if let Some(value) = parse_i128_env("ARB_LATENCY_BPS") {
            config.latency_buffer_bps = value;
        }
        config
    }
}

#[derive(Debug, Clone)]
pub struct Decision {
    pub market: MarketKey,
    pub buy: Exchange,
    pub sell: Exchange,
    pub qty: i64,
    pub buy_avg: i64,
    pub sell_avg: i64,
    pub gross_bps: i128,
    pub buy_fee_bps_x100: i128,
    pub sell_fee_bps_x100: i128,
    pub buy_cost_quote: i128,
    pub sell_proceeds_quote: i128,
    pub fee_quote: i128,
    pub latency_buffer_quote: i128,
    pub net_profit_quote: i128,
    pub detected_at: Instant,
}

impl Decision {
    pub fn format_line(&self) -> String {
        format!(
            "[EDGE {lane}] buy={buy} sell={sell} qty={qty} buy_avg={buy_avg} sell_avg={sell_avg} gross={gross_bps}bps buy_fee={buy_fee}bps sell_fee={sell_fee}bps buy_cost={buy_cost} sell_proceeds={sell_proceeds} net={net} fees={fees} latency={latency} age_ms={age}",
            lane = self.market,
            buy = self.buy,
            sell = self.sell,
            qty = format_qty(self.qty),
            buy_avg = format_price(self.buy_avg),
            sell_avg = format_price(self.sell_avg),
            gross_bps = self.gross_bps,
            buy_fee = format_bps_x100(self.buy_fee_bps_x100),
            sell_fee = format_bps_x100(self.sell_fee_bps_x100),
            buy_cost = format_money(self.buy_cost_quote),
            sell_proceeds = format_money(self.sell_proceeds_quote),
            net = format_money(self.net_profit_quote),
            fees = format_money(self.fee_quote),
            latency = format_money(self.latency_buffer_quote),
            age = Instant::now().duration_since(self.detected_at).as_millis(),
        )
    }
}

pub struct StrategyCore {
    pub config: EngineConfig,
    books: HashMap<MarketVenueKey, VenueBook>,
    evaluated_routes: u64,
    positive_edges: u64,
    started_at: Instant,
    best_by_market: HashMap<MarketKey, Decision>,
}

impl StrategyCore {
    pub fn new(config: EngineConfig) -> Self {
        Self {
            config,
            books: HashMap::new(),
            evaluated_routes: 0,
            positive_edges: 0,
            started_at: Instant::now(),
            best_by_market: HashMap::new(),
        }
    }

    pub fn on_book(&mut self, updated: VenueBook) -> Vec<Decision> {
        let updated_key = updated.key();
        let market = updated.market();
        self.books.insert(updated_key, updated);

        let peers = self
            .books
            .values()
            .filter(|book| book.market() == market && book.exchange != updated_key.exchange)
            .cloned()
            .collect::<Vec<_>>();

        let Some(updated_book) = self.books.get(&updated_key).cloned() else {
            return vec![];
        };

        let mut decisions = Vec::new();
        for peer in peers {
            if let Some(decision) = self.evaluate_route(&updated_book, &peer) {
                decisions.push(decision);
            }
            if let Some(decision) = self.evaluate_route(&peer, &updated_book) {
                decisions.push(decision);
            }
        }

        decisions
    }

    fn evaluate_route(&mut self, buy: &VenueBook, sell: &VenueBook) -> Option<Decision> {
        self.evaluated_routes += 1;

        let now = Instant::now();
        if self.is_unusable(buy, now) || self.is_unusable(sell, now) {
            return None;
        }

        let buy_ask = buy.best_ask()?;
        let sell_bid = sell.best_bid()?;
        if sell_bid <= buy_ask {
            return None;
        }

        let gross_bps = ((sell_bid - buy_ask) as i128 * 10_000) / buy_ask as i128;
        if gross_bps < self.config.min_required_bps as i128 {
            return None;
        }

        let target_qty =
            ((self.config.max_notional_quote * QTY_SCALE as i128) / buy_ask as i128) as i64;
        let buy_fill = buy.book.buy_vwap(target_qty)?;
        let sell_fill = sell.book.sell_vwap(buy_fill.qty)?;
        let qty = buy_fill.qty.min(sell_fill.qty);
        if qty <= 0 {
            return None;
        }

        let buy_fill = buy.book.buy_vwap(qty)?;
        let sell_fill = sell.book.sell_vwap(qty)?;
        let buy_fee_bps_x100 = self.taker_fee_bps_x100(buy.exchange);
        let sell_fee_bps_x100 = self.taker_fee_bps_x100(sell.exchange);
        let buy_fee = fee_for_notional(buy_fill.quote_units, buy_fee_bps_x100);
        let sell_fee = fee_for_notional(sell_fill.quote_units, sell_fee_bps_x100);
        let fee_quote = buy_fee + sell_fee;
        let latency_buffer_quote =
            (buy_fill.quote_units * self.config.latency_buffer_bps) / 10_000;
        let net_profit_quote =
            sell_fill.quote_units - buy_fill.quote_units - fee_quote - latency_buffer_quote;

        let decision = Decision {
            market: buy.market(),
            buy: buy.exchange,
            sell: sell.exchange,
            qty,
            buy_avg: buy_fill.avg_price,
            sell_avg: sell_fill.avg_price,
            gross_bps,
            buy_fee_bps_x100,
            sell_fee_bps_x100,
            buy_cost_quote: buy_fill.quote_units,
            sell_proceeds_quote: sell_fill.quote_units,
            fee_quote,
            latency_buffer_quote,
            net_profit_quote,
            detected_at: now,
        };

        let should_replace = self
            .best_by_market
            .get(&decision.market)
            .map(|best| decision.net_profit_quote > best.net_profit_quote)
            .unwrap_or(true);
        if should_replace {
            self.best_by_market
                .insert(decision.market, decision.clone());
        }

        if net_profit_quote <= 0 {
            return None;
        }

        self.positive_edges += 1;
        Some(decision)
    }

    fn is_stale(&self, book: &VenueBook, now: Instant) -> bool {
        let threshold = match book.lane {
            Lane::Usd => self.config.stale_usd,
            Lane::Usdt => self.config.stale_usdt,
        };
        now.duration_since(book.received_at) > threshold
    }

    fn is_unusable(&self, book: &VenueBook, now: Instant) -> bool {
        self.is_stale(book, now) || book.is_crossed()
    }

    fn taker_fee_bps_x100(&self, exchange: Exchange) -> i128 {
        self.config
            .override_taker_fee_bps_x100
            .unwrap_or_else(|| default_taker_bps_x100(exchange))
    }

    pub fn status_line(&self) -> String {
        let now = Instant::now();
        let live = self
            .books
            .values()
            .filter(|book| !self.is_unusable(book, now))
            .count();
        let stale = self.books.len().saturating_sub(live);
        format!(
            "[STATUS] feeds={}/{} live stale={} routes={} positive_edges={} uptime={}s",
            live,
            self.books.len(),
            stale,
            self.evaluated_routes,
            self.positive_edges,
            now.duration_since(self.started_at).as_secs(),
        )
    }

    pub fn feed_lines(&self) -> Vec<String> {
        let now = Instant::now();
        let mut lines = self
            .books
            .values()
            .map(|book| {
                let state = if book.is_crossed() {
                    "invalid"
                } else if self.is_stale(book, now) {
                    "stale"
                } else {
                    "live"
                };
                let age = now.duration_since(book.received_at).as_millis();
                let bid = book.best_bid().map(format_price).unwrap_or_else(|| "-".to_string());
                let ask = book.best_ask().map(format_price).unwrap_or_else(|| "-".to_string());
                let seq = book
                    .sequence
                    .map(|value| value.to_string())
                    .unwrap_or_else(|| "-".to_string());
                let ts = book
                    .exchange_ts_ms
                    .map(|value| value.to_string())
                    .unwrap_or_else(|| "-".to_string());
                format!(
                    "[FEED {state}] {exchange:<8} {symbol:<8} lane={lane:<4} bid={bid} ask={ask} age_ms={age} seq={seq} ts={ts}",
                    exchange = book.exchange,
                    symbol = book.symbol,
                    lane = book.lane,
                )
            })
            .collect::<Vec<_>>();
        lines.sort();
        lines
    }

    pub fn best_lines(&self) -> Vec<String> {
        let mut lines = self
            .best_by_market
            .values()
            .map(|decision| format!("[BEST {}] {}", decision.market, decision.format_line()))
            .collect::<Vec<_>>();
        lines.sort();
        lines
    }
}

fn parse_quote_env(key: &str) -> Option<i128> {
    env::var(key)
        .ok()
        .and_then(|raw| parse_scaled_decimal(&raw, PRICE_SCALE).map(i128::from))
}

fn parse_i64_env(key: &str) -> Option<i64> {
    env::var(key).ok().and_then(|raw| raw.parse::<i64>().ok())
}

fn parse_i128_env(key: &str) -> Option<i128> {
    env::var(key)
        .ok()
        .and_then(|raw| raw.parse::<i128>().ok())
}

fn parse_bps_x100_env(key: &str) -> Option<i128> {
    env::var(key).ok().and_then(|raw| {
        let (whole, frac) = raw.trim().split_once('.').unwrap_or((raw.trim(), ""));
        let whole = whole.parse::<i128>().ok()?;
        let mut frac_value = 0_i128;
        let mut multiplier = 10_i128;
        for ch in frac.chars().take(2) {
            let digit = ch.to_digit(10)? as i128;
            frac_value += digit * multiplier;
            multiplier /= 10;
        }
        Some(whole * BPS_SCALE + frac_value)
    })
}
