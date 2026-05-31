use crate::model::Exchange;

pub const BPS_SCALE: i128 = 100;
const FEE_DENOMINATOR: i128 = 10_000 * BPS_SCALE;

#[derive(Debug, Clone, Copy)]
pub struct FeeTier {
    pub label: &'static str,
    pub min_30d_volume_usd: Option<u128>,
    pub maker_bps_x100: i128,
    pub taker_bps_x100: i128,
}

#[derive(Debug)]
pub struct ExchangeFeeSchedule {
    pub exchange: Exchange,
    pub default_tier_label: &'static str,
    pub source_url: &'static str,
    pub caveat: &'static str,
    pub tiers: &'static [FeeTier],
}

const BINANCE_TIERS: &[FeeTier] = &[
    tier("regular", Some(0), 1_000, 1_000),
    tier("vip1", Some(1_000_000), 900, 1_000),
    tier("vip2", Some(5_000_000), 800, 1_000),
    tier("vip3", Some(20_000_000), 400, 600),
    tier("vip4", Some(75_000_000), 400, 520),
    tier("vip5", Some(150_000_000), 250, 310),
    tier("vip6", Some(400_000_000), 200, 290),
    tier("vip7", Some(800_000_000), 190, 280),
    tier("vip8", Some(2_000_000_000), 160, 250),
    tier("vip9", Some(4_000_000_000), 110, 230),
];

const BYBIT_TIERS: &[FeeTier] = &[
    tier("vip0", Some(0), 1_000, 1_000),
    tier("vip1", Some(1_000_000), 675, 800),
    tier("vip2", Some(5_000_000), 650, 775),
    tier("vip3", Some(10_000_000), 625, 750),
    tier("vip4", Some(25_000_000), 500, 600),
    tier("vip5", Some(50_000_000), 400, 500),
    tier("supreme_vip", Some(100_000_000), 300, 450),
    tier("pro1", Some(25_000_000), 400, 600),
    tier("pro2", Some(50_000_000), 300, 500),
    tier("pro3", Some(100_000_000), 200, 400),
    tier("pro4", Some(200_000_000), 150, 300),
    tier("pro5", Some(500_000_000), 100, 200),
    tier("pro6", Some(1_000_000_000), 50, 150),
];

const OKX_TIERS: &[FeeTier] = &[
    tier("regular", Some(0), 800, 1_000),
    tier("vip1", None, 675, 800),
    tier("vip2", None, 600, 700),
    tier("vip3", None, 550, 650),
    tier("vip4", None, 300, 450),
    tier("vip5", None, 250, 350),
    tier("vip6", None, 0, 300),
    tier("vip7", None, -20, 250),
    tier("vip8", None, -50, 200),
    tier("vip9", None, -75, 175),
];

const COINBASE_TIERS: &[FeeTier] = &[
    tier("intro1", Some(0), 6_000, 12_000),
    tier("intro2", Some(10_000), 4_000, 8_000),
    tier("advanced1", Some(25_000), 2_500, 5_000),
    tier("advanced2", Some(75_000), 1_250, 2_500),
    tier("advanced3", Some(250_000), 750, 1_500),
    tier("vip1", Some(500_000), 600, 1_250),
    tier("vip2", Some(1_000_000), 500, 1_000),
    tier("vip3", Some(5_000_000), 400, 850),
    tier("vip4", Some(10_000_000), 250, 650),
    tier("vip5", Some(20_000_000), 100, 500),
    tier("vip6", Some(50_000_000), 0, 350),
    tier("vip7", Some(100_000_000), 0, 250),
    tier("vip8", Some(250_000_000), 0, 200),
];

const KRAKEN_TIERS: &[FeeTier] = &[
    tier("0", Some(0), 2_500, 4_000),
    tier("10k", Some(10_000), 2_000, 3_500),
    tier("50k", Some(50_000), 1_400, 2_400),
    tier("100k", Some(100_000), 1_200, 2_200),
    tier("250k", Some(250_000), 1_000, 2_000),
    tier("500k", Some(500_000), 800, 1_800),
    tier("1m", Some(1_000_000), 600, 1_600),
    tier("2.5m", Some(2_500_000), 400, 1_400),
    tier("5m", Some(5_000_000), 200, 1_200),
    tier("10m", Some(10_000_000), 0, 1_000),
    tier("100m", Some(100_000_000), 0, 800),
    tier("500m", Some(500_000_000), 0, 500),
];

const GEMINI_TIERS: &[FeeTier] = &[
    tier("0", Some(0), 6_000, 12_000),
    tier("10k", Some(10_000), 4_000, 8_000),
    tier("25k", Some(25_000), 2_500, 5_000),
    tier("75k", Some(75_000), 1_250, 2_500),
    tier("250k", Some(250_000), 750, 1_500),
    tier("500k", Some(500_000), 600, 1_250),
    tier("1m", Some(1_000_000), 500, 1_000),
    tier("5m", Some(5_000_000), 400, 850),
    tier("10m", Some(10_000_000), 250, 650),
    tier("20m", Some(20_000_000), 100, 500),
    tier("50m", Some(50_000_000), 0, 350),
    tier("100m", Some(100_000_000), 0, 250),
    tier("250m", Some(250_000_000), 0, 200),
];

pub static BINANCE_FEES: ExchangeFeeSchedule = ExchangeFeeSchedule {
    exchange: Exchange::Binance,
    default_tier_label: "regular",
    source_url: "https://www.binance.com/en/fee/trading",
    caveat: "Standard Spot & Margin fees, excluding BNB discount and USDC special rates.",
    tiers: BINANCE_TIERS,
};

pub static BYBIT_FEES: ExchangeFeeSchedule = ExchangeFeeSchedule {
    exchange: Exchange::Bybit,
    default_tier_label: "vip0",
    source_url: "https://www.bybit.com/en/help-center/article/Trading-Fee-Structure",
    caveat: "Spot crypto-crypto fees; actual account rate may vary by region and VIP status.",
    tiers: BYBIT_TIERS,
};

pub static OKX_FEES: ExchangeFeeSchedule = ExchangeFeeSchedule {
    exchange: Exchange::Okx,
    default_tier_label: "regular",
    source_url: "https://www.okx.com/en-us/help/trading-fee-rules-faq",
    caveat: "Regular-user spot example from official OKX fee rules; full fee page is region/account dependent.",
    tiers: OKX_TIERS,
};

pub static COINBASE_FEES: ExchangeFeeSchedule = ExchangeFeeSchedule {
    exchange: Exchange::Coinbase,
    default_tier_label: "intro1",
    source_url: "https://www.coinbase.com/advanced-vip",
    caveat: "Coinbase Advanced spot VIP table; exact account tier is available from authenticated transaction_summary.",
    tiers: COINBASE_TIERS,
};

pub static KRAKEN_FEES: ExchangeFeeSchedule = ExchangeFeeSchedule {
    exchange: Exchange::Kraken,
    default_tier_label: "0",
    source_url: "https://www.kraken.com/features/fee-schedule",
    caveat: "Kraken Pro Spot Crypto fees; BTC/USD and ETH/USD use this table.",
    tiers: KRAKEN_TIERS,
};

pub static GEMINI_FEES: ExchangeFeeSchedule = ExchangeFeeSchedule {
    exchange: Exchange::Gemini,
    default_tier_label: "0",
    source_url: "https://www.gemini.com/fees/activetrader-fee-schedule",
    caveat: "Gemini ActiveTrader spot fees; stablecoin pairs have separate fees.",
    tiers: GEMINI_TIERS,
};

const fn tier(
    label: &'static str,
    min_30d_volume_usd: Option<u128>,
    maker_bps_x100: i128,
    taker_bps_x100: i128,
) -> FeeTier {
    FeeTier {
        label,
        min_30d_volume_usd,
        maker_bps_x100,
        taker_bps_x100,
    }
}

pub fn fee_schedule(exchange: Exchange) -> &'static ExchangeFeeSchedule {
    match exchange {
        Exchange::Binance => &BINANCE_FEES,
        Exchange::Bybit => &BYBIT_FEES,
        Exchange::Okx => &OKX_FEES,
        Exchange::Coinbase => &COINBASE_FEES,
        Exchange::Kraken => &KRAKEN_FEES,
        Exchange::Gemini => &GEMINI_FEES,
    }
}

pub fn default_fee_tier(exchange: Exchange) -> &'static FeeTier {
    &fee_schedule(exchange).tiers[0]
}

pub fn default_taker_bps_x100(exchange: Exchange) -> i128 {
    default_fee_tier(exchange).taker_bps_x100
}

pub fn fee_for_notional(notional_quote_units: i128, fee_bps_x100: i128) -> i128 {
    (notional_quote_units * fee_bps_x100) / FEE_DENOMINATOR
}

pub fn format_bps_x100(value: i128) -> String {
    let sign = if value < 0 { "-" } else { "" };
    let abs = value.abs();
    if abs % BPS_SCALE == 0 {
        format!("{sign}{}", abs / BPS_SCALE)
    } else {
        format!("{sign}{}.{:02}", abs / BPS_SCALE, abs % BPS_SCALE)
            .trim_end_matches('0')
            .trim_end_matches('.')
            .to_string()
    }
}

pub fn fee_summary_line() -> String {
    [
        Exchange::Binance,
        Exchange::Bybit,
        Exchange::Okx,
        Exchange::Coinbase,
        Exchange::Kraken,
        Exchange::Gemini,
    ]
    .into_iter()
    .map(|exchange| {
        let tier = default_fee_tier(exchange);
        format!(
            "{}({}) maker={}bps taker={}bps",
            exchange,
            tier.label,
            format_bps_x100(tier.maker_bps_x100),
            format_bps_x100(tier.taker_bps_x100)
        )
    })
    .collect::<Vec<_>>()
    .join(" | ")
}

pub fn fee_sources_summary_line() -> String {
    [
        Exchange::Binance,
        Exchange::Bybit,
        Exchange::Okx,
        Exchange::Coinbase,
        Exchange::Kraken,
        Exchange::Gemini,
    ]
    .into_iter()
    .map(|exchange| {
        let schedule = fee_schedule(exchange);
        let tier = default_fee_tier(exchange);
        let min_volume = tier
            .min_30d_volume_usd
            .map(|value| value.to_string())
            .unwrap_or_else(|| "account-tier".to_string());
        format!(
            "{} default={} min30d={} source={} caveat={}",
            schedule.exchange,
            schedule.default_tier_label,
            min_volume,
            schedule.source_url,
            schedule.caveat
        )
    })
    .collect::<Vec<_>>()
    .join(" | ")
}
