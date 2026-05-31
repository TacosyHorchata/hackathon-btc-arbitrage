#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.pedro.hackathonbtc.signal-monitor"
RUNTIME_DIR="$HOME/Library/Application Support/hackathon-btc"
LOG_DIR="$HOME/Library/Logs/hackathon-btc"
AGENT_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$RUNTIME_DIR/signals" "$LOG_DIR" "$AGENT_DIR"

cp "$ROOT_DIR/scripts/profit_signal_monitor.py" "$RUNTIME_DIR/profit_signal_monitor.py"
chmod 644 "$RUNTIME_DIR/profit_signal_monitor.py"

if [[ -f "$ROOT_DIR/config/inventory.example.json" ]]; then
  cp "$ROOT_DIR/config/inventory.example.json" "$RUNTIME_DIR/inventory.example.json"
  chmod 644 "$RUNTIME_DIR/inventory.example.json"
fi

cp "$ROOT_DIR/ops/$LABEL.plist" "$AGENT_DIR/$LABEL.plist"
chmod 644 "$AGENT_DIR/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$AGENT_DIR/$LABEL.plist"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

launchctl print "gui/$(id -u)/$LABEL" | rg 'state|pid|runs|last exit' || true
