#!/bin/bash -e
# ==============================================================================
# CyberDeck OS - Stage 02: Install CyberDeck UI, Tools, and Systemd Services
# ==============================================================================

# 1. Install payload files into /opt/cyberdeck in the rootfs
echo "[CyberDeck] Installing CyberDeck software payload into target rootfs..."
mkdir -p "${ROOTFS_DIR}/opt/cyberdeck"

if [ -d "${STAGE_DIR}/02-cyberdeck-ui/payload" ]; then
    cp -r "${STAGE_DIR}/02-cyberdeck-ui/payload/"* "${ROOTFS_DIR}/opt/cyberdeck/"
fi

# 2. Copy systemd service units
if [ -d "${ROOTFS_DIR}/opt/cyberdeck/services" ]; then
    install -m 644 "${ROOTFS_DIR}/opt/cyberdeck/services/cyberdeck-ui.service" "${ROOTFS_DIR}/etc/systemd/system/"
    install -m 644 "${ROOTFS_DIR}/opt/cyberdeck/services/cyberdeck-esp32.service" "${ROOTFS_DIR}/etc/systemd/system/"
    if [ -f "${ROOTFS_DIR}/opt/cyberdeck/services/99-cyberdeck.rules" ]; then
        install -m 644 "${ROOTFS_DIR}/opt/cyberdeck/services/99-cyberdeck.rules" "${ROOTFS_DIR}/etc/udev/rules.d/"
    fi
fi

# 3. Chroot configuration
on_chroot << EOF
echo "[CyberDeck] Configuring UI environment and enabling services..."

TARGET_USER="\${FIRST_USER_NAME:-deck}"
chown -R "\${TARGET_USER}:\${TARGET_USER}" /opt/cyberdeck
chown -R "\${TARGET_USER}:\${TARGET_USER}" /var/log/cyberdeck

# Create wrapper runner script
cat > /usr/local/bin/cyberdeck << 'CEOF'
#!/usr/bin/env bash
exec python3 /opt/cyberdeck/ui/main.py "$@"
CEOF
chmod +x /usr/local/bin/cyberdeck

# Enable systemd services
systemctl daemon-reload
systemctl enable cyberdeck-ui.service || true
systemctl enable cyberdeck-esp32.service || true

echo "[CyberDeck] UI & services installation complete."
EOF
