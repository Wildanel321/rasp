#!/bin/bash -e
# ==============================================================================
# CyberDeck OS - Stage 04: Network Diagnostic & Utility Configuration
# ==============================================================================

on_chroot << EOF
echo "[CyberDeck] Setting up network diagnostics and permissions..."

# Allow deck user to run network scanning and packet capture without full root
if command -v setcap >/dev/null 2>&1; then
    setcap cap_net_raw,cap_net_admin+eip \$(which ping) 2>/dev/null || true
    if [ -f /usr/bin/nmap ]; then
        setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap 2>/dev/null || true
    fi
    if [ -f /usr/bin/dumpcap ]; then
        setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap 2>/dev/null || true
    fi
    if [ -f /usr/bin/tcpdump ]; then
        setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump 2>/dev/null || true
    fi
fi

# Add deck user to wireshark and netdev groups
TARGET_USER="\${FIRST_USER_NAME:-deck}"
if getent group wireshark >/dev/null 2>&1; then
    usermod -a -G wireshark "\${TARGET_USER}" || true
fi
if getent group netdev >/dev/null 2>&1; then
    usermod -a -G netdev "\${TARGET_USER}" || true
fi

# Configure polkit permission for NetworkManager for netdev group (allows modifying Wi-Fi without password prompt)
mkdir -p /etc/polkit-1/localauthority/50-local.d/
cat > /etc/polkit-1/localauthority/50-local.d/10-network-manager.pkla << 'PKLAEOF'
[Allow netdev group to manage network]
Identity=unix-group:netdev
Action=org.freedesktop.NetworkManager.*
ResultAny=yes
ResultInactive=yes
ResultActive=yes
PKLAEOF

# Ensure Wi-Fi regulatory domain fallback
if [ -f /etc/default/crda ]; then
    sed -i 's/REGDOMAIN=.*/REGDOMAIN=US/' /etc/default/crda || true
fi

echo "[CyberDeck] Network tools configuration complete."
EOF
