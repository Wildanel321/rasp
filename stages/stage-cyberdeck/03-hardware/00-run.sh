#!/bin/bash -e
# ==============================================================================
# CyberDeck OS - Stage 03: Hardware Configuration (Display, SPI, Touch XPT2046)
# ==============================================================================

on_chroot << EOF
echo "[CyberDeck] Configuring hardware interfaces and 3.5\" TFT XPT2046..."

# Detect config.txt location (Bookworm uses /boot/firmware/config.txt, older uses /boot/config.txt)
CONFIG_TXT="/boot/firmware/config.txt"
if [ ! -f "\$CONFIG_TXT" ]; then
    CONFIG_TXT="/boot/config.txt"
fi

echo "[CyberDeck] Modifying \$CONFIG_TXT..."

# Ensure base interfaces are enabled
cat >> "\$CONFIG_TXT" << 'CFGEOF'

# ==============================================================================
# CYBERDECK OS - Hardware & Display Overlays (3.5" 480x320 SPI TFT - XPT2046)
# ==============================================================================
dtparam=spi=on
dtparam=i2c_arm=on
enable_uart=1

# Disable unneeded power-hungry interfaces
dtoverlay=disable-bt
dtoverlay=disable-wifi-off

# 3.5" RPi LCD / Waveshare / KeDei / MPI3501 (ILI9486 & XPT2046 Touchscreen)
# Default overlay configuration for 3.5 inch SPI display
dtoverlay=piscreen,speed=16000000,rotate=90
dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=1,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=150,ymax=4000

# HDMI fallback / Headless framebuffer resolution default
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt 480 320 60 6 0 0 0
framebuffer_width=480
framebuffer_height=320

# GPU memory allocation for Raspberry Pi 3 (1GB RAM)
gpu_mem=64
CFGEOF

# Touchscreen X11 Calibration configuration
mkdir -p /etc/X11/xorg.conf.d
cat > /etc/X11/xorg.conf.d/99-calibration.conf << 'CALEOF'
Section "InputClass"
    Identifier      "calibration"
    MatchProduct    "ADS7846 Touchscreen"
    Option  "MinX"  "3936"
    Option  "MaxX"  "227"
    Option  "MinY"  "268"
    Option  "MaxY"  "3880"
    Option  "SwapXY" "1"
    Option  "InvertX" "0"
    Option  "InvertY" "0"
    Option  "EmulateThirdButton" "1"
    Option  "EmulateThirdButtonTimeout" "750"
    Option  "EmulateThirdButtonThreshold" "30"
EndSection
CALEOF

# Ensure SPI & I2C kernel modules load at boot
mkdir -p /etc/modules-load.d
cat > /etc/modules-load.d/cyberdeck-hw.conf << 'MODEOF'
spi_bcm2835
i2c_dev
i2c_bcm2835
uinput
evdev
MODEOF

echo "[CyberDeck] Hardware configuration complete."
EOF
