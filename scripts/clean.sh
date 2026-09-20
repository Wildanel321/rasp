#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - Clean Build and Temp Artifacts Script
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[*] Cleaning Python bytecode and cache..."
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "[*] Cleaning pi-gen work artifacts..."
rm -rf "$SCRIPT_DIR/pi-gen/work" 2>/dev/null || true

echo "[+] Cleanup complete."
