#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - Touchscreen Calibration Script (XPT2046 / ADS7846)
# ==============================================================================

set -euo pipefail

echo "=== Touchscreen Calibration Wizard ==="
echo "1. Calibrate via TSLib (Console / Framebuffer)"
echo "2. Calibrate via Xinput (X11 Desktop / Kiosk)"
read -rp "Select mode [1-2]: " MODE

if [ "$MODE" = "1" ]; then
    if command -v ts_calibrate >/dev/null 2>&1; then
        export TSLIB_TSDEVICE=/dev/input/touchscreen
        sudo ts_calibrate
        sudo ts_test
    else
        echo "Error: ts_calibrate not found. Please install 'libts-bin'."
    fi
elif [ "$MODE" = "2" ]; then
    if command -v xinput_calibrator >/dev/null 2>&1; then
        DISPLAY=:0 xinput_calibrator
    else
        echo "Error: xinput_calibrator not found. Please install 'xinput-calibrator'."
    fi
else
    echo "Invalid option."
fi
