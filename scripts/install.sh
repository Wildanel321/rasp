#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - Direct Installation Script (For existing Raspberry Pi OS)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Installing CyberDeck OS Software Suite ==="

# 1. Check Root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run this script with sudo."
    exit 1
fi

TARGET_USER="${SUDO_USER:-deck}"

# 2. Install dependencies
echo "[*] Installing required apt packages..."
apt-get update -y
apt-get install -y \
    python3 python3-pip python3-pygame python3-psutil python3-serial \
    python3-evdev python3-requests python3-tabulate \
    fbset evtest tslib libts-bin xinput-calibrator \
    wireless-tools wpasupplicant iw net-tools iproute2 dnsutils \
    nmap iperf3 traceroute curl htop tmux haveged

# 3. Setup /opt/cyberdeck
echo "[*] Copying files to /opt/cyberdeck..."
mkdir -p /opt/cyberdeck /var/log/cyberdeck
cp -r "$SCRIPT_DIR/ui" /opt/cyberdeck/
cp -r "$SCRIPT_DIR/tools" /opt/cyberdeck/
cp -r "$SCRIPT_DIR/services" /opt/cyberdeck/
cp -r "$SCRIPT_DIR/hardware" /opt/cyberdeck/

chown -R "$TARGET_USER:$TARGET_USER" /opt/cyberdeck
chown -R "$TARGET_USER:$TARGET_USER" /var/log/cyberdeck

# 4. Install systemd units and udev rules
echo "[*] Installing systemd services..."
cp /opt/cyberdeck/services/cyberdeck-ui.service /etc/systemd/system/
cp /opt/cyberdeck/services/cyberdeck-esp32.service /etc/systemd/system/
cp /opt/cyberdeck/services/99-cyberdeck.rules /etc/udev/rules.d/

# Wrapper binary
cat > /usr/local/bin/cyberdeck << 'EOF'
#!/usr/bin/env bash
exec python3 /opt/cyberdeck/ui/main.py "$@"
EOF
chmod +x /usr/local/bin/cyberdeck

# 5. Enable services
systemctl daemon-reload
udevadm control --reload-rules || true
systemctl enable cyberdeck-ui.service
systemctl enable cyberdeck-esp32.service

echo "[+] Installation complete! Start UI now with: sudo systemctl start cyberdeck-ui"
