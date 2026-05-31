#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.pedro.hackathonbtc.status-monitor"
RUNTIME_DIR="$HOME/Library/Application Support/hackathon-btc"
LOG_DIR="$HOME/Library/Logs/hackathon-btc"
AGENT_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$RUNTIME_DIR/status" "$LOG_DIR" "$AGENT_DIR"

cp "$ROOT_DIR/scripts/status_monitor.py" "$RUNTIME_DIR/status_monitor.py"
chmod 644 "$RUNTIME_DIR/status_monitor.py"

cp "$ROOT_DIR/ops/$LABEL.plist" "$AGENT_DIR/$LABEL.plist"
chmod 644 "$AGENT_DIR/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$AGENT_DIR/$LABEL.plist"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

launchctl print "gui/$(id -u)/$LABEL" | rg 'state|pid|runs|last exit' || true
