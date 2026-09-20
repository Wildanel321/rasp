# CyberDeck OS — Developer & Extensibility Guide

This document covers local development, testing, architectural patterns, and how to add new screens or custom pi-gen stages to CyberDeck OS.

---

## 1. Local Development on Host PC (Simulator Mode)

You can develop, test, and preview all CyberDeck UI screens directly on your Linux, macOS, or Windows PC without needing physical Raspberry Pi hardware.

### Prerequisites:
```bash
pip install pygame psutil pyserial
```

### Running the UI Locally in Windowed Mode:
```bash
python3 ui/main.py --windowed
```

In simulator mode:
- Display runs in a 480x320 window.
- CPU/RAM/Disk metrics read host hardware or fallback gracefully.
- Mouse clicks simulate resistive touchscreen taps.
- ESP32 client automatically falls back to internal simulation if no serial port is connected.

---

## 2. Architecture Overview

```
cyberdeck-os/
├── ui/                   # Main Pygame Framebuffer UI Engine (<40MB RAM)
│   ├── config.py         # 480x320 geometry, Cyberpunk high-contrast theme
│   ├── widgets/          # Touch buttons, status bars, info cards, quickkeys
│   ├── screens/          # Modular screen components (Menu, Terminal, System, etc.)
│   └── services/         # System monitor, network scanner, ESP32 client
├── tools/                # Standalone CLI tools & ESP32 firmware
├── services/             # Systemd service units & udev rules
├── hardware/             # Display & Touch device-tree overlays and calibration
├── stages/               # Custom pi-gen stages injected into image build
└── docs/                 # Hardware, Display, Build, and Dev guides
```

---

## 3. Adding a New Screen to CyberDeck UI

To add a new screen (e.g. `sensors`):

1. **Create Screen Class** in `ui/screens/sensors.py`:
   ```python
   import pygame
   from ui.config import HEADER_HEIGHT, CONTENT_HEIGHT, COLOR_CYAN, get_font
   from ui.widgets.button import Button

   class SensorScreen:
       def __init__(self, on_navigate=None):
           self.title = "FIELD SENSORS"
           self.on_navigate = on_navigate
           self.font = get_font(12, mono=True)

       def handle_event(self, event):
           return False

       def update(self):
           pass

       def draw(self, surface):
           # Render sensor graphics
           text = self.font.render("BME280: 25.4C | 1013 hPa", True, COLOR_CYAN)
           surface.blit(text, (20, HEADER_HEIGHT + 20))
   ```

2. **Register Screen in `ui/main.py`**:
   ```python
   from ui.screens.sensors import SensorScreen
   # Add to self.screens dictionary:
   self.screens["sensors"] = SensorScreen(on_navigate=self.navigate_to)
   ```

3. **Add Button to `ui/screens/menu.py`**:
   Add an entry into `_build_menu()` items list.

---

## 4. Modifying the pi-gen Build Stage

The custom OS customization lives in `stages/stage-cyberdeck/`:
- `00-packages/00-packages`: Add debian packages to install via `apt`.
- `01-cyberdeck-core/00-run.sh`: System-level security and journald config.
- `02-cyberdeck-ui/00-run.sh`: Payload copy and systemd service enabling.
- `03-hardware/00-run.sh`: Device tree overlays in `/boot/firmware/config.txt`.
- `04-network-tools/00-run.sh`: Diagnostic permissions.
- `05-esp32/00-run.sh`: USB serial udev rules.

Run `scripts/test.sh` to validate syntax after making edits.
