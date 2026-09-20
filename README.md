# CYBERDECK OS — Raspberry Pi 3 Custom OS

**CyberDeck OS** is a lightweight, purpose-built custom Linux operating system image for **Raspberry Pi 3 (3B / 3B+)** designed as a portable CyberDeck and field computer. Built upon **Raspberry Pi OS Lite** using **pi-gen**, it boots directly into a high-contrast 3.5" (480x320) touch-optimized interface with an integrated genuine Linux terminal, real-time telemetry, authorized network diagnostic tools, and an ESP32 companion coprocessor bridge.

---

## Key Highlights

- **Ultra-Lightweight & Fast**: Direct framebuffer engine consuming **< 40MB RAM** (No Electron, No heavy Desktop Environment).
- **Targeted for 3.5" TFT (480x320)**: Big tactile touch buttons (XPT2046 resistive touch) & full USB keyboard support.
- **Genuine Linux Terminal**: Embedded real PTY terminal running `/bin/bash` with on-screen touch quickkeys (`ESC`, `TAB`, `^C`, Arrows).
- **Live System Monitor**: Real-time CPU load, RAM allocation, microSD storage, SoC thermal load, uptime, and IP status.
- **Network Analysis Tools**: Wi-Fi scanner, interface inspector, ping latency tester, and authorized local subnet discovery.
- **ESP32 Companion Integration**: USB-Serial JSON RPC bridge for analog sensor telemetry, battery monitoring, and GPIO expansion.
- **Headless & MicroSD Friendly**: Full SSH access, low microSD wear (RAM-backed journald), `Restart=on-failure` systemd self-healing.
- **Reproducible Build**: Automated pipeline with `pi-gen` and Docker support.

---

## 1. Hardware Requirements

- **SBC**: Raspberry Pi 3 Model B or 3 Model B+ (1GB RAM)
- **Storage**: 32 GB or larger microSD card (Class 10 / A1 recommended)
- **Display**: 3.5 inch SPI TFT LCD (ILI9486 / MPI3501 driver, 480x320)
- **Touch Controller**: XPT2046 / ADS7846 (SPI CE1, IRQ GPIO 25)
- **Keyboard**: USB wired or 2.4GHz wireless mini keyboard
- **Companion MCU**: ESP32 Dev Module via Micro-USB / USB-C
- **Power**: 5V / 2.5A+ Powerbank

---

## 2. Flashing the Image

1. Download or build `CyberDeckOS-v0.1.0.img.xz` and its checksum `CyberDeckOS-v0.1.0.img.xz.sha256`.
2. Verify checksum:
   ```bash
   sha256sum -c CyberDeckOS-v0.1.0.img.xz.sha256
   ```
3. Flash using **Raspberry Pi Imager** or **BalenaEtcher**:
   - Choose **Use Custom** -> Select `CyberDeckOS-v0.1.0.img.xz`
   - Select your target microSD card -> Click **Write**.

---

## 3. First Boot & Credentials

- **Default Username**: `deck`
- **Default Password**: `cyberdeck`
- **Default Hostname**: `cyberdeck`
- **SSH**: Enabled by default on Port `22`

On initial power-on, CyberDeck OS initializes the SPI bus, attaches the touchscreen driver, and launches the CyberDeck UI on the 3.5" TFT automatically.

---

## 4. Display & Touchscreen Setup

The image is pre-configured for standard 3.5" TFT LCDs. If your display requires manual calibration:
```bash
# Launch interactive calibration
sudo /opt/cyberdeck/hardware/touchscreen/calibrate.sh
```
Detailed hardware wiring and alternative display driver details are in [docs/DISPLAY.md](file:///c:/Users/Wildan/Documents/coder/rasp/docs/DISPLAY.md).

---

## 5. Wi-Fi Setup

To connect to a Wi-Fi network from the terminal or SSH:
```bash
sudo raspi-config
# or via command line:
sudo nmcli dev wifi connect "SSID_NAME" password "PASSPHRASE"
# or via configuration wizard:
/opt/cyberdeck/scripts/configure.sh
```

---

## 6. SSH & Headless Maintenance

If the display is detached, CyberDeck OS remains fully manageable over the network:
```bash
ssh deck@cyberdeck.local
```
Useful service commands:
```bash
# Check UI status
sudo systemctl status cyberdeck-ui

# Restart UI
sudo systemctl restart cyberdeck-ui

# View live UI logs
sudo journalctl -u cyberdeck-ui -f
```

---

## 7. ESP32 Companion Setup

1. Connect the ESP32 to the Raspberry Pi 3 via USB.
2. Flash the companion firmware located in `tools/esp32/firmware/`:
   ```bash
   cd tools/esp32/firmware
   pio run --target upload
   ```
3. Test communication:
   ```bash
   python3 /opt/cyberdeck/tools/esp32/companion_bridge.py --send '{"command": "ping"}'
   ```
See [docs/ESP32.md](file:///c:/Users/Wildan/Documents/coder/rasp/docs/ESP32.md) for full JSON RPC protocol details.

---

## 8. Building the Custom Image (`pi-gen`)

Build the complete `.img.xz` image from source using the provided `build.sh` script:

### Using Docker (Recommended for Windows WSL / macOS / Linux):
```bash
./build.sh --docker
```

### Using Native Linux (Debian / Ubuntu):
```bash
sudo ./build.sh
```

The output image and `.sha256` hash will be generated inside the `deploy/` directory. See [docs/BUILD.md](file:///c:/Users/Wildan/Documents/coder/rasp/docs/BUILD.md) for build customization.

---

## 9. Local Development & Simulator Mode

You can test and modify the UI directly on your development workstation:
```bash
# Install host dependencies
pip install pygame psutil pyserial

# Run test suite
./scripts/test.sh

# Run UI in windowed mode
python3 ui/main.py --windowed
```
See [docs/DEVELOPMENT.md](file:///c:/Users/Wildan/Documents/coder/rasp/docs/DEVELOPMENT.md) for screen creation guides.

---

## 10. Repository Structure

```
cyberdeck-os/
├── README.md                 # Project Overview & Quickstart
├── LICENSE                   # MIT License
├── build.sh                  # pi-gen automated image builder
├── config.env                # OS build & system configuration
├── stages/
│   └── stage-cyberdeck/      # Custom pi-gen build stage
│       ├── prereqs           # Stage dependency (stage2)
│       ├── 00-packages/      # Minimal debian packages
│       ├── 01-cyberdeck-core/# System optimizations & user permissions
│       ├── 02-cyberdeck-ui/  # UI & systemd payload installation
│       ├── 03-hardware/      # SPI & XPT2046 device-tree overlays
│       ├── 04-network-tools/ # Diagnostic utilities configuration
│       └── 05-esp32/         # USB-Serial udev rules & bridge
├── ui/                       # CyberDeck UI Application (<40MB RAM)
│   ├── main.py               # Application entrypoint & event loop
│   ├── config.py             # 480x320 geometry & Cyberpunk theme
│   ├── screens/              # Modular UI screens (Terminal, System, etc.)
│   ├── widgets/              # Touch buttons, status bars, info cards
│   └── services/             # System monitor, network & ESP32 services
├── tools/                    # System & Network diagnostic CLI tools
│   ├── system/               # System info & power governor manager
│   ├── network/              # Subnet scanner & port inspector
│   ├── gpio/                 # RPi GPIO control utility
│   └── esp32/                # Bridge daemon & Arduino firmware
├── services/                 # systemd service units & udev rules
├── hardware/                 # Display & touchscreen configuration
├── scripts/                  # Install, configure, test & clean scripts
└── docs/                     # Detailed architectural documentation
    ├── BUILD.md
    ├── HARDWARE.md
    ├── DISPLAY.md
    ├── ESP32.md
    └── DEVELOPMENT.md
```

---

## License

This project is licensed under the [MIT License](file:///c:/Users/Wildan/Documents/coder/rasp/LICENSE).
