# CyberDeck OS — Hardware & Electrical Guide

CyberDeck OS is engineered specifically for field computing with Raspberry Pi 3 (3B / 3B+) hardware.

---

## 1. Supported Hardware Specifications

| Component | Target Specification |
|---|---|
| **SBC** | Raspberry Pi 3 Model B or 3 Model B+ |
| **SoC** | Broadcom BCM2837 (Quad-core ARM Cortex-A53 @ 1.2GHz / 1.4GHz) |
| **RAM** | 1 GB LPDDR2 |
| **Display** | 3.5 inch 480x320 SPI TFT (ILI9486 / MPI3501 driver) |
| **Touchscreen** | 4-Wire Resistive Touch via XPT2046 / ADS7846 SPI controller |
| **Companion MCU** | ESP32-WROOM-32 / ESP32-S2 / ESP32-S3 via USB-Serial |
| **Input Device** | USB Keyboard / 2.4GHz Wireless mini keyboard / On-screen Touch |
| **Storage** | 32 GB+ Class 10 / A1 High Endurance microSD Card |
| **Power Source** | 5V / 2.5A+ Powerbank (Quick Charge / USB-PD 5V output) |

---

## 2. Power Consumption & Powerbank Tuning

Raspberry Pi 3B typical power draw:
- **Idle (with 3.5" TFT lit)**: ~450 mA (~2.25 W)
- **Active UI / Terminal**: ~550–650 mA (~2.75–3.25 W)
- **Heavy Wi-Fi Scan / Network Load**: ~800–950 mA (~4.0–4.75 W)

### Battery Life on 10,000 mAh (37 Wh) Powerbank:
- **Expected runtime**: 8 to 11 hours of field operation.

### Low-Power Tuning:
To maximize battery life, CyberDeck OS includes CPU governor switching:
```bash
# Enable low power mode
sudo /opt/cyberdeck/tools/system/power_manager.sh powersave

# Return to balanced mode
sudo /opt/cyberdeck/tools/system/power_manager.sh ondemand
```

---

## 3. Raspberry Pi 3 40-Pin Header Allocation

When a 3.5" SPI TFT is installed directly on the 40-pin header, the following pins are utilized by the display & touch:

| Pin # | Function | Used By |
|---|---|---|
| Pin 1 | 3.3V Power | Display & Touch VCC |
| Pin 2, 4 | 5.0V Power | Backlight Inverter |
| Pin 6, 9, 14, 20 | GND | Ground |
| Pin 19 (GPIO 10) | SPI0 MOSI | TFT Data Out |
| Pin 21 (GPIO 9) | SPI0 MISO | Touch Data In |
| Pin 23 (GPIO 11) | SPI0 SCLK | SPI Clock |
| Pin 24 (GPIO 8) | SPI0 CE0 | TFT Chip Select |
| Pin 26 (GPIO 7) | SPI0 CE1 | Touch Chip Select |
| Pin 18 (GPIO 24) | D/C | Data / Command Select |
| Pin 22 (GPIO 25) | TP_IRQ | Touch Interrupt IRQ |

### Available Free GPIOs for User / Sensors:
- **GPIO 17 (Pin 11)**
- **GPIO 27 (Pin 13)**
- **GPIO 22 (Pin 15)**
- **GPIO 23 (Pin 16)**
- **I2C Bus (GPIO 2 / Pin 3, GPIO 3 / Pin 5)** (if display does not bridge them)
