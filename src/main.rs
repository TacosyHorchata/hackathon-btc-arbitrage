mod book;
mod feeds;
mod fees;
mod model;
mod strategy;

use crate::feeds::spawn_public_feeds;
use crate::fees::{fee_sources_summary_line, fee_summary_line, format_bps_x100};
use crate::model::BookEvent;
use crate::strategy::{EngineConfig, StrategyCore};
use tokio::sync::mpsc;
use tokio::time::{interval, Duration};

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "btc_arb_engine=info,info".into()),
        )
        .init();

    let (tx, mut rx) = mpsc::channel::<BookEvent>(2048);
    spawn_public_feeds(tx);

    let config = EngineConfig::from_env();
    let mut core = StrategyCore::new(config);
    let mut status_tick = interval(Duration::from_secs(2));

    println!("btc-arb-engine live public scanner");
    println!("assets: BTC/ETH/SOL on USD; BTC/ETH/SOL/XRP/DOGE/LTC on USDT");
    println!("lanes: USD = Coinbase/Kraken/Gemini, USDT = Binance/Bybit/OKX");
    println!(
        "risk: max_notional={} fee_mode={} override_taker_fee={} latency_bps={} min_gross_bps={}",
        crate::model::format_money(core.config.max_notional_quote),
        if core.config.override_taker_fee_bps_x100.is_some() {
            "override"
        } else {
            "exchange_taker"
        },
        core.config
            .override_taker_fee_bps_x100
            .map(format_bps_x100)
            .unwrap_or_else(|| "-".to_string()),
        core.config.latency_buffer_bps,
        core.config.min_required_bps,
    );
    println!("fees: {}", fee_summary_line());
    println!("fee_sources: {}", fee_sources_summary_line());
    println!("mode: public data only, paper execution math, no private keys\n");

    loop {
        tokio::select! {
            Some(event) = rx.recv() => {
                for decision in core.on_book(event.book) {
                    if decision.net_profit_quote > core.config.min_print_profit_quote {
                        println!("{}", decision.format_line());
                    }
                }
            }
            _ = status_tick.tick() => {
                println!("{}", core.status_line());
                for line in core.feed_lines() {
                    println!("{line}");
                }
                for line in core.best_lines() {
                    println!("{line}");
                }
            }
        }
    }
}
