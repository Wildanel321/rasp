# CyberDeck OS — 3.5" Display & Touchscreen Guide

This document describes the setup, device tree overlays, calibration, and troubleshooting for the **3.5" 480x320 SPI TFT with XPT2046 touch controller**.

---

## 1. Hardware Architecture

- **LCD Driver**: ILI9486 / MPI3501 (driven via BCM2835 Hardware SPI @ 16–32MHz)
- **Touch Controller**: XPT2046 (ADS7846 compatible, SPI CE1, PenIRQ GPIO 25)
- **Linux Framebuffer Device**: `/dev/fb1`
- **Linux Input Device**: `/dev/input/touchscreen` (or `/dev/input/event*`)

---

## 2. Kernel Device Tree Configuration

The custom image pre-configures `/boot/firmware/config.txt` (or `/boot/config.txt`):

```ini
# Enable SPI Hardware
dtparam=spi=on

# 3.5" LCD Overlay
dtoverlay=piscreen,speed=16000000,rotate=90

# XPT2046 / ADS7846 Touchscreen Overlay
dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=1,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=150,ymax=4000

# Resolution defaults
hdmi_force_hotplug=1
hdmi_cvt 480 320 60 6 0 0 0
framebuffer_width=480
framebuffer_height=320
gpu_mem=64
```

### Alternative LCD Overlays for Different Clones:
If your screen is a Waveshare or KeDei variant:
- **Waveshare 3.5" A/B**: `dtoverlay=waveshare35a:rotate=90` or `dtoverlay=waveshare35b:rotate=90`
- **KeDei v6.3+**: `dtoverlay=kedei` or `fbtft_device name=kedei`

---

## 3. Touchscreen Calibration

### Framebuffer / TSLib Calibration:
```bash
sudo ts_calibrate
sudo ts_test
```
This writes the calibration matrix to `/etc/pointercal`.

### X11 Calibration (`xinput_calibrator`):
```bash
DISPLAY=:0 xinput_calibrator
```
Copy the generated snippet into `/etc/X11/xorg.conf.d/99-calibration.conf`:
```ini
Section "InputClass"
    Identifier      "calibration"
    MatchProduct    "ADS7846 Touchscreen"
    Option  "MinX"  "3936"
    Option  "MaxX"  "227"
    Option  "MinY"  "268"
    Option  "MaxY"  "3880"
    Option  "SwapXY" "1"
EndSection
```

---

## 4. Testing & Verification

1. **Verify Framebuffer**:
   ```bash
   ls -l /dev/fb*
   # Should list /dev/fb0 (HDMI) and /dev/fb1 (SPI TFT)
   ```

2. **Test Raw Touch Events**:
   ```bash
   sudo evtest /dev/input/touchscreen
   ```
   Touch the screen and verify coordinates stream to the console.

3. **Restart CyberDeck UI**:
   ```bash
   sudo systemctl restart cyberdeck-ui
   ```

---

## 5. Troubleshooting Display Issues

- **White Screen / No Image**:
  - Verify display header is firmly seated on GPIO pins.
  - Check `dmesg | grep -i fb1` or `dmesg | grep -i spi` to verify driver loaded.
- **Inverted / Mirrored Touch**:
  - Adjust `SwapXY`, `InvertX`, or `InvertY` in `/etc/X11/xorg.conf.d/99-calibration.conf` or `/boot/firmware/config.txt`.
