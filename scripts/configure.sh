#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - Post-Installation Configuration Wizard
# ==============================================================================

set -euo pipefail

echo "=========================================="
echo "      CYBERDECK OS CONFIGURATION TOOL     "
echo "=========================================="
echo "1. Configure Wi-Fi SSID & Passphrase"
echo "2. Setup 3.5\" SPI TFT Display & Touch"
echo "3. Calibrate Touchscreen"
echo "4. Change Hostname"
echo "5. Restart CyberDeck UI Service"
echo "6. Exit"
echo "=========================================="
read -rp "Select option [1-6]: " OPT

case "$OPT" in
    1)
        read -rp "Enter Wi-Fi SSID: " W_SSID
        read -rsp "Enter Wi-Fi Password: " W_PASS
        echo ""
        if command -v wpa_passphrase >/dev/null 2>&1; then
            wpa_passphrase "$W_SSID" "$W_PASS" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf >/dev/null
            sudo wpa_cli -i wlan0 reconfigure || true
            echo "[+] Wi-Fi credentials saved."
        fi
        ;;
    2)
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        bash "$SCRIPT_DIR/hardware/display/setup-display.sh"
        ;;
    3)
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        bash "$SCRIPT_DIR/hardware/touchscreen/calibrate.sh"
        ;;
    4)
        read -rp "Enter new hostname: " NEW_HOST
        sudo hostnamectl set-hostname "$NEW_HOST"
        echo "[+] Hostname changed to $NEW_HOST."
        ;;
    5)
        sudo systemctl restart cyberdeck-ui
        echo "[+] CyberDeck UI restarted."
        ;;
    6)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid selection."
        exit 1
        ;;
esac
