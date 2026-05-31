"use strict";
const $ = s => document.querySelector(s);
const fmtUsd = n => (n<0?"-":"")+"$"+Math.abs(n).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtN = (n,d=2) => n==null?"-":Number(n).toLocaleString("en-US",{minimumFractionDigits:d,maximumFractionDigits:d});
const cls = n => n>0?"pos":(n<0?"neg":"dim");

let filter = "all";
let cfg = null;

async function jget(u){ const r = await fetch(u); return r.json(); }
async function jpost(u,b){ const r = await fetch(u,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)}); return r.json(); }

/* ---------- main refresh ---------- */
async function tick(){
  try{
    const st = await jget("/api/state");
    cfg = st.config;
    renderHeader(st);
    renderFeeds(st.feeds);
    const [opps, trades, pnl, wallets, summary] = await Promise.all([
      jget("/api/opportunities?limit=150"),
      jget("/api/trades"),
      jget("/api/pnl"),
      jget("/api/wallets"),
      jget("/api/summary"),
    ]);
    renderOpps(opps.opportunities);
    renderTrades(trades.trades);
    renderWallets(wallets.wallets);
    renderStates(summary.decision_states);
    drawPnl(pnl.series, st);
    syncScenario(st.config.scenario);
  }catch(e){ /* transient */ }
}

function renderHeader(st){
  $("#venues").textContent = st.venues_online+"/"+st.venues_total;
  $("#cycles").textContent = st.cycles;
  $("#ntrades").textContent = st.accepted_total;
  const p = $("#pnl"); p.textContent = fmtUsd(st.realized_pnl);
  p.className = "v num "+cls(st.realized_pnl);
  $("#equity").textContent = fmtUsd(st.equity);
  $("#realized").textContent = fmtUsd(st.realized_pnl);
  $("#realized").className = "v num "+cls(st.realized_pnl);
  const u = st.uptime_s; $("#uptime").textContent = (u>=3600? Math.floor(u/3600)+"h ":"")+Math.floor(u%3600/60)+"m "+(u%60)+"s";
}

function syncScenario(s){
  document.querySelectorAll("#scen button").forEach(b=>b.classList.toggle("on",b.dataset.s===s));
  $("#scenBadge").style.display = s==="stress" ? "inline-block" : "none";
  $("#scenBadge").textContent = s==="stress" ? "SIMULATED DISLOCATION (+"+cfg.stress_bps+" bps)" :
    (s==="zerofee" ? "ZERO-FEE SCENARIO" : "");
  if(s==="zerofee"){ $("#scenBadge").style.display="inline-block"; }
}

function renderFeeds(feeds){
  const mid = feeds.find(f=>f.online);
  $("#feedAge").textContent = mid&&mid.age_ms!=null ? (mid.age_ms/1000).toFixed(1)+"s ago" : "";
  $("#feeds").innerHTML = feeds.map(f=>`
    <tr>
      <td><span class="dot ${f.online?'up':'down'}"></span>${f.venue}</td>
      <td><span class="lane">${f.lane}</span></td>
      <td class="r num">${f.bid?fmtN(f.bid,1):'<span class=dim>'+(f.err?'err':'-')+'</span>'}</td>
      <td class="r num">${f.ask?fmtN(f.ask,1):'-'}</td>
      <td class="r num dim">${f.spread_bps!=null?f.spread_bps.toFixed(1):'-'}</td>
    </tr>`).join("");
}

function renderOpps(opps){
  let rows = opps;
  if(filter==="ENTER_SIM") rows = opps.filter(o=>o.state==="ENTER_SIM");
  else if(filter==="rej") rows = opps.filter(o=>o.state!=="ENTER_SIM");
  $("#oppcnt").textContent = rows.length+" shown";
  $("#opps").innerHTML = rows.slice(0,120).map(o=>`
    <tr class="clickable" onclick="inspect(${o.id})">
      <td>${o.buy_venue}<span class="dim">&rarr;</span>${o.sell_venue}</td>
      <td><span class="lane">${o.lane}</span></td>
      <td class="r num dim">${o.gross_bps?o.gross_bps.toFixed(1):'-'}</td>
      <td class="r num ${cls(o.net_bps)}">${o.net_bps?o.net_bps.toFixed(1):'-'}</td>
      <td class="r num ${cls(o.net_profit)}">${o.net_profit?fmtUsd(o.net_profit):'-'}</td>
      <td><span class="st ${o.state}">${o.state.replace('SKIP_','')}</span></td>
    </tr>`).join("") || `<tr><td colspan=6 class=dim style=padding:14px>No opportunities in this filter. In LIVE mode, real BTC spreads rarely clear fees &mdash; that is the honest result.</td></tr>`;
}

function renderTrades(trades){
  $("#tradecnt").textContent = trades.length;
  $("#trades").innerHTML = trades.slice(0,80).map(t=>`
    <tr>
      <td>${t.buy_venue}<span class="dim">&rarr;</span>${t.sell_venue}</td>
      <td class="r num dim">${fmtN(t.notional,0)}</td>
      <td class="r num pos">${t.net_bps.toFixed(1)}</td>
      <td class="r num pos">${fmtUsd(t.net_profit)}</td>
    </tr>`).join("") || `<tr><td colspan=4 class=dim style=padding:12px>No fills yet.</td></tr>`;
}

function renderWallets(wallets){
  const maxEq = Math.max(...wallets.map(w=>w.equity_quote),1);
  $("#wallets").innerHTML = wallets.map(w=>`
    <div class="wal">
      <span>${w.venue} <span class="lane">${w.lane}</span></span>
      <span class="v">${fmtN(w.base,4)} BTC &middot; ${fmtUsd(w.quote)}</span>
    </div>
    <div class="bar"><i style="width:${(w.equity_quote/maxEq*100).toFixed(0)}%"></i></div>
  `).join("");
}

function renderStates(states){
  const order=["ENTER_SIM","SKIP_NEGATIVE","SKIP_CROSSED","SKIP_THIN","SKIP_STALE","SKIP_INVENTORY"];
  const keys = Object.keys(states||{}).sort((a,b)=>order.indexOf(a)-order.indexOf(b));
  $("#states").innerHTML = keys.map(k=>`
    <div class="wal"><span><span class="st ${k}">${k.replace('SKIP_','')}</span></span>
    <span class="v">${states[k].toLocaleString()}</span></div>`).join("") || "<span class=dim>warming up...</span>";
}

/* ---------- P&L canvas chart ---------- */
function drawPnl(series, st){
  const cv = $("#pnl"), ctx = cv.getContext("2d");
  const W = cv.width = cv.clientWidth*2, H = cv.height = 320; ctx.scale(1,1);
  ctx.clearRect(0,0,W,H);
  if(!series || series.length<2){ return; }
  const xs = series.map(p=>p.t), ys = series.map(p=>p.realized);
  const minX=xs[0], maxX=xs[xs.length-1];
  let minY=Math.min(...ys,0), maxY=Math.max(...ys,1);
  const pad = (maxY-minY)*0.1||1; maxY+=pad; minY-=pad;
  const px = t => 40 + (t-minX)/(maxX-minX||1)*(W-60);
  const py = v => H-30 - (v-minY)/(maxY-minY||1)*(H-50);
  // zero line
  ctx.strokeStyle="#222a3a"; ctx.lineWidth=1; ctx.beginPath();
  ctx.moveTo(40,py(0)); ctx.lineTo(W-20,py(0)); ctx.stroke();
  ctx.fillStyle="#4d5870"; ctx.font="20px monospace";
  ctx.fillText("$"+maxY.toFixed(0),4,py(maxY)+6);
  ctx.fillText("$"+minY.toFixed(0),4,py(minY)+6);
  ctx.fillText("$0",4,py(0)+6);
  // area + line
  ctx.beginPath(); ctx.moveTo(px(xs[0]),py(ys[0]));
  for(let i=1;i<series.length;i++) ctx.lineTo(px(xs[i]),py(ys[i]));
  const last = ys[ys.length-1];
  ctx.strokeStyle = last>=0?"#39d98a":"#ff6b6b"; ctx.lineWidth=2.5; ctx.stroke();
  ctx.lineTo(px(xs[xs.length-1]),py(0)); ctx.lineTo(px(xs[0]),py(0)); ctx.closePath();
  ctx.fillStyle = last>=0?"rgba(57,217,138,.08)":"rgba(255,107,107,.08)"; ctx.fill();
}

/* ---------- decision inspector ---------- */
window.inspect = async function(id){
  const o = await jget("/api/decision/"+id);
  const ev = o.evidence||{buckets:[]};
  const buckets = (ev.buckets||[]).map(b=>`
    <tr><td class="num">${fmtN(b.notional,0)}</td>
      <td class="num">${b.buy_vwap?fmtN(b.buy_vwap,1):'-'}</td>
      <td class="num">${b.sell_vwap?fmtN(b.sell_vwap,1):'-'}</td>
      <td class="num ${cls(b.gross_bps)}">${b.gross_bps!=null?b.gross_bps.toFixed(1):'-'}</td>
      <td class="num ${cls(b.net_bps)}">${b.net_bps!=null?b.net_bps.toFixed(1):'-'}</td>
      <td class="dim">${b.status}</td></tr>`).join("");
  $("#drawerBody").innerHTML = `
    <h3>${o.buy_venue||''} &rarr; ${o.sell_venue||''} <span class="st ${o.state}">${o.state}</span></h3>
    <p class="dim" style="margin:6px 0 14px">${o.reason||''}</p>
    ${o.net_bps!=null?`
    <div class="kv"><span class="k">Lane</span><span class="num">${o.lane}</span></div>
    <div class="kv"><span class="k">Gross edge</span><span class="num">${(o.gross_bps||0).toFixed(2)} bps</span></div>
    <div class="kv"><span class="k">Net after fees+latency</span><span class="num ${cls(o.net_bps)}">${(o.net_bps||0).toFixed(2)} bps</span></div>
    <div class="kv"><span class="k">Net profit</span><span class="num ${cls(o.net_profit)}">${fmtUsd(o.net_profit||0)}</span></div>
    <div class="kv"><span class="k">Executable size</span><span class="num">${fmtUsd(o.notional||0)} (${fmtN(o.base_size,5)} BTC)</span></div>`:''}
    <h2 style="margin:16px 0 8px">Depth Waterfall</h2>
    <table class="waterfall"><thead><tr><th>Notional</th><th>Buy VWAP</th><th>Sell VWAP</th><th>Gross</th><th>Net</th><th>Status</th></tr></thead>
    <tbody>${buckets||'<tr><td colspan=6 class=dim>no depth walk (rejected earlier)</td></tr>'}</tbody></table>
    <p class="note">The engine walks increasing size through the real book. Net bps shrinks as larger orders eat deeper levels &mdash; depth-aware VWAP, not top-of-book.</p>`;
  openDrawer("#drawer");
}

/* ---------- drawers ---------- */
function openDrawer(sel){ $(sel).classList.add("open"); $("#overlay").classList.add("open"); }
function closeAll(){ document.querySelectorAll(".drawer").forEach(d=>d.classList.remove("open")); $("#overlay").classList.remove("open"); }
$("#close").onclick = closeAll; $("#cfgClose").onclick = closeAll; $("#overlay").onclick = closeAll;

/* config drawer */
$("#gear").onclick = ()=>{
  const fees = cfg.taker_fee_bps;
  $("#cfgBody").innerHTML =
    `<div class="cfgrow"><label>Latency haircut (bps)</label><input id="c_lat" value="${cfg.latency_bps}"></div>
     <div class="cfgrow"><label>Min net edge (bps)</label><input id="c_min" value="${cfg.min_net_bps}"></div>
     <div class="cfgrow"><label>Max notional ($)</label><input id="c_max" value="${cfg.max_notional}"></div>
     <h2 style="margin:14px 0 6px">Taker fees (bps)</h2>` +
    Object.keys(fees).map(k=>`<div class="cfgrow"><label>${k}</label><input id="fee_${k}" value="${fees[k]}"></div>`).join("");
  openDrawer("#cfgDrawer");
};
$("#cfgApply").onclick = async ()=>{
  const body = {
    latency_bps:+$("#c_lat").value, min_net_bps:+$("#c_min").value,
    max_notional:+$("#c_max").value, taker_fee_bps:{}
  };
  Object.keys(cfg.taker_fee_bps).forEach(k=>{ const el=$("#fee_"+k); if(el) body.taker_fee_bps[k]=+el.value; });
  await jpost("/api/config",body); closeAll(); tick();
};

/* scenario buttons */
document.querySelectorAll("#scen button").forEach(b=>{
  b.onclick = async ()=>{ await jpost("/api/config",{scenario:b.dataset.s}); tick(); };
});
/* filters */
document.querySelectorAll("#filters button").forEach(b=>{
  b.onclick = ()=>{ filter=b.dataset.f; document.querySelectorAll("#filters button").forEach(x=>x.classList.toggle("on",x===b)); tick(); };
});

tick();
setInterval(tick, 3000);
