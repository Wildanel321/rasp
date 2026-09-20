# CyberDeck OS — ESP32 Companion Integration Guide

CyberDeck OS connects to an **ESP32 microcontroller** as a companion coprocessor via USB-Serial to handle real-time I/O, ADC analog voltage reading (e.g. battery monitoring), sensor bus monitoring, and extra GPIO expansion.

---

## 1. Hardware Connection

Connect the ESP32 to any Raspberry Pi 3 USB port using a Micro-USB or USB-C data cable.

### Serial Device Discovery:
CyberDeck OS automatically creates a persistent symlink via `/etc/udev/rules.d/99-esp32-companion.rules`:
- Target Symlink: `/dev/cyberdeck-esp32`
- Default Baudrate: `115200`

Supported USB-UART chips:
- Silicon Labs **CP2102 / CP2104**
- WCH **CH340 / CH341**
- FTDI **FT232R**
- Espressif Native **USB CDC (ESP32-S2 / ESP32-S3)**

---

## 2. JSON RPC Serial Protocol

All communication between Raspberry Pi 3 and ESP32 uses newline-terminated (`\n`) JSON strings.

### A. Ping / Health Check
**Request:**
```json
{"command": "ping"}
```
**Response:**
```json
{"success": true, "pong": true, "firmware": "CyberDeck-ESP32-v0.1.0", "uptime_ms": 14250}
```

### B. GPIO Output Control
**Request:**
```json
{"command": "gpio", "pin": 2, "state": true}
```
**Response:**
```json
{"success": true, "pin": 2, "state": true}
```

### C. ADC Analog Voltage Reading
**Request:**
```json
{"command": "read_analog", "pin": 34}
```
**Response:**
```json
{"success": true, "pin": 34, "raw": 4095, "voltage": 3.30}
```

### D. System Telemetry & Battery
**Request:**
```json
{"command": "telemetry"}
```
**Response:**
```json
{"success": true, "battery_v": 4.12, "uptime_s": 350}
```

---

## 3. Flashing ESP32 Firmware

### Option A: Using PlatformIO
```bash
cd tools/esp32/firmware
pio run --target upload
```

### Option B: Using Arduino IDE
1. Open `tools/esp32/firmware/esp32_firmware.ino` in Arduino IDE.
2. Install the **ArduinoJson** library (`v6.x` or `v7.x`) via Library Manager.
3. Select board: **ESP32 Dev Module**.
4. Click **Upload**.

---

## 4. Testing Serial Communication from Raspberry Pi

### Using the CyberDeck CLI:
```bash
# Ping test
python3 /opt/cyberdeck/tools/esp32/companion_bridge.py --send '{"command": "ping"}'

# Toggle LED on Pin 2
python3 /opt/cyberdeck/tools/esp32/companion_bridge.py --send '{"command": "gpio", "pin": 2, "state": true}'

# Read Telemetry
python3 /opt/cyberdeck/tools/esp32/companion_bridge.py --send '{"command": "telemetry"}'
```

### Checking Background Daemon Logs:
```bash
sudo systemctl status cyberdeck-esp32
sudo journalctl -u cyberdeck-esp32 -f
```
