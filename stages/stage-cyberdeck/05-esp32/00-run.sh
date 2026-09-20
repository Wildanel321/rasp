#!/bin/bash -e
# ==============================================================================
# CyberDeck OS - Stage 05: ESP32 Serial Companion Microcontroller Setup
# ==============================================================================

on_chroot << EOF
echo "[CyberDeck] Setting up ESP32 USB-Serial udev rules and companion bridge..."

cat > /etc/udev/rules.d/99-esp32-companion.rules << 'RLEOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="cyberdeck-esp32", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="cyberdeck-esp32", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="cyberdeck-esp32", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", SYMLINK+="cyberdeck-esp32", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="0002", SYMLINK+="cyberdeck-esp32", MODE="0666", GROUP="dialout"
RLEOF

echo "[CyberDeck] ESP32 companion rules configured."
EOF
