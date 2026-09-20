#!/bin/bash -e
# ==============================================================================
# CyberDeck OS - Stage 01: Core System Optimization & NetworkManager Setup
# ==============================================================================

on_chroot << EOF
echo "[CyberDeck] Configuring core system optimizations & NetworkManager..."

# 1. Create CyberDeck System Directories
mkdir -p /opt/cyberdeck
mkdir -p /var/log/cyberdeck
mkdir -p /etc/cyberdeck
chmod 755 /opt/cyberdeck
chmod 775 /var/log/cyberdeck

# 2. Add 'deck' user to hardware and network access groups
TARGET_USER="\${FIRST_USER_NAME:-deck}"
if id "\${TARGET_USER}" &>/dev/null; then
    usermod -a -G dialout,gpio,i2c,spi,video,input,audio,netdev,sudo "\${TARGET_USER}"
fi

# 3. MicroSD Card Longevity: Limit journald logging size & disable excess writes
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/00-cyberdeck.conf << 'JEOF'
[Journal]
Storage=volatile
RuntimeMaxUse=25M
SystemMaxUse=30M
ForwardToSyslog=no
JEOF

# 4. Configure NetworkManager as primary network backend (supports mobile hotspots & auto-connect)
systemctl enable NetworkManager || true

# 5. Disable heavy unneeded background services for RPi3 RAM preservation
DISABLE_SERVICES=(
    avahi-daemon.service
    ModemManager.service
    cups.service
    cups-browsed.service
    triggerhappy.service
)

for srv in "\${DISABLE_SERVICES[@]}"; do
    if systemctl is-enabled "\$srv" &>/dev/null; then
        systemctl disable "\$srv" || true
    fi
done

# 6. Set up welcome banner
cat > /etc/motd << 'MEOF'
============================================================
              CYBERDECK OS - FIELD SYSTEM v0.1
              Raspberry Pi 3 Portable Terminal
============================================================
* UI Service   : sudo systemctl status cyberdeck-ui
* ESP32 Daemon : sudo systemctl status cyberdeck-esp32
* Wi-Fi CLI    : nmcli dev wifi list
* Logs         : sudo journalctl -u cyberdeck-ui -f
============================================================
MEOF

echo "[CyberDeck] Core system configuration complete."
EOF
