#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - Automated Testing & Verification Script
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${SCRIPT_DIR}"

echo "=========================================="
echo "      CYBERDECK OS TEST RUNNER            "
echo "=========================================="

echo "[*] Step 1: Checking Python file syntax..."
find "$SCRIPT_DIR" -name "*.py" -not -path "*/pi-gen/*" -exec python3 -m py_compile {} +
echo "[+] All Python files compiled cleanly."

echo "[*] Step 2: Testing SystemMonitor service..."
python3 -c "
import sys
from ui.services.system_monitor import SystemMonitor
mon = SystemMonitor()
mon._collect_metrics()
print(f'   CPU: {mon.cpu_percent}%, RAM: {mon.ram_percent}%, Temp: {mon.cpu_temp}C, IP: {mon.ip_address}')
assert mon.cpu_temp >= 0
"
echo "[+] SystemMonitor verified."

echo "[*] Step 3: Testing ESP32 JSON Protocol simulation..."
python3 -c "
from ui.services.esp32_client import ESP32Client
client = ESP32Client()
ping_res = client.ping()
print(f'   Ping: {ping_res}')
assert ping_res['success'] == True
gpio_res = client.set_gpio(2, True)
print(f'   GPIO 2 ON: {gpio_res}')
assert gpio_res['state'] == True
adc_res = client.read_analog(34)
print(f'   ADC 34: {adc_res}')
assert adc_res['voltage'] > 0
"
echo "[+] ESP32 Protocol simulation verified."

echo "[*] Step 4: Testing Shell Scripts syntax..."
for sh in $(find "$SCRIPT_DIR" -name "*.sh" -not -path "*/pi-gen/*"); do
    bash -n "$sh"
done
echo "[+] All Bash scripts passed syntax validation."

echo ""
echo "=========================================="
echo "       ALL VERIFICATION TESTS PASSED      "
echo "=========================================="
echo "To test the interactive UI on your computer:"
echo "   python3 ui/main.py --windowed"
