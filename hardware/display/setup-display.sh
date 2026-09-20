#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - 3.5" TFT Display Setup & Activation Script
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SNIPPET="${SCRIPT_DIR}/config.txt.snippet"

CONFIG_TXT="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_TXT" ]; then
    CONFIG_TXT="/boot/config.txt"
fi

if [ ! -f "$CONFIG_TXT" ]; then
    echo "Error: Cannot locate config.txt file!"
    exit 1
fi

echo "[*] Appending 3.5\" TFT Display overlays to $CONFIG_TXT..."
sudo tee -a "$CONFIG_TXT" < "$SNIPPET" > /dev/null

echo "[+] Display configuration applied. Please reboot your Raspberry Pi to activate /dev/fb1."
