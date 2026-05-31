use crate::model::{parse_price, parse_qty, Fill, Level, Side, QTY_SCALE};

const TOP_K: usize = 50;

#[derive(Debug, Clone, Default)]
pub struct OrderBook {
    pub bids: Vec<Level>,
    pub asks: Vec<Level>,
}

impl OrderBook {
    pub fn from_pairs(
        bids: impl IntoIterator<Item = (String, String)>,
        asks: impl IntoIterator<Item = (String, String)>,
    ) -> Self {
        let mut book = Self::default();
        book.bids = normalize_levels(bids, Side::Bid);
        book.asks = normalize_levels(asks, Side::Ask);
        book
    }

    pub fn apply_update(&mut self, side: Side, price: i64, qty: i64) {
        let levels = match side {
            Side::Bid => &mut self.bids,
            Side::Ask => &mut self.asks,
        };

        if let Some(index) = levels.iter().position(|level| level.price == price) {
            if qty <= 0 {
                levels.remove(index);
            } else {
                levels[index].qty = qty;
            }
        } else if qty > 0 {
            levels.push(Level { price, qty });
        }

        sort_and_cap(levels, side);
    }

    pub fn buy_vwap(&self, target_qty: i64) -> Option<Fill> {
        consume_levels(&self.asks, target_qty)
    }

    pub fn sell_vwap(&self, target_qty: i64) -> Option<Fill> {
        consume_levels(&self.bids, target_qty)
    }
}

pub fn normalize_levels(raw: impl IntoIterator<Item = (String, String)>, side: Side) -> Vec<Level> {
    let mut levels = raw
        .into_iter()
        .filter_map(|(price, qty)| {
            Some(Level {
                price: parse_price(&price)?,
                qty: parse_qty(&qty)?,
            })
        })
        .filter(|level| level.price > 0 && level.qty > 0)
        .collect::<Vec<_>>();

    sort_and_cap(&mut levels, side);
    levels
}

fn sort_and_cap(levels: &mut Vec<Level>, side: Side) {
    match side {
        Side::Bid => levels.sort_unstable_by(|a, b| b.price.cmp(&a.price)),
        Side::Ask => levels.sort_unstable_by(|a, b| a.price.cmp(&b.price)),
    }

    levels.dedup_by_key(|level| level.price);
    if levels.len() > TOP_K {
        levels.truncate(TOP_K);
    }
}

fn consume_levels(levels: &[Level], target_qty: i64) -> Option<Fill> {
    if target_qty <= 0 {
        return None;
    }

    let mut remaining = target_qty;
    let mut filled = 0_i64;
    let mut quote_units = 0_i128;

    for level in levels {
        if remaining <= 0 {
            break;
        }
        if level.qty <= 0 || level.price <= 0 {
            continue;
        }

        let take = remaining.min(level.qty);
        quote_units += (level.price as i128 * take as i128) / QTY_SCALE as i128;
        filled += take;
        remaining -= take;
    }

    if filled <= 0 {
        return None;
    }

    let avg_price = ((quote_units * QTY_SCALE as i128) / filled as i128) as i64;
    Some(Fill {
        qty: filled,
        quote_units,
        avg_price,
    })
}
