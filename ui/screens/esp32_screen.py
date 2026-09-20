"""
CyberDeck ESP32 Companion Control Screen
Interactive interface for ESP32 GPIO, ADC reading, telemetry and serial communication
"""

import json
import threading
import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button
from ui.services.esp32_client import ESP32Client

class ESP32Screen:
    def __init__(self, on_navigate=None):
        self.title = "ESP32 COMPANION"
        self.on_navigate = on_navigate
        self.client = ESP32Client()
        self.buttons = []
        self.log_lines = ["ESP32 Companion Interface Ready."]
        self.gpio_state = False
        self.font = get_font(size=11, bold=False, mono=True)
        self._build_ui()
        
        # Initial scan in background
        threading.Thread(target=self._connect, daemon=True).start()

    def _build_ui(self):
        actions = [
            ("SCAN / CONNECT", self._connect, "c", COLOR_CYAN),
            ("PING ESP32", self._ping, "p", COLOR_PRIMARY),
            ("TOGGLE GPIO 2", self._toggle_gpio, "g", COLOR_AMBER),
            ("READ ADC PIN 34", self._read_adc, "a", COLOR_PRIMARY),
            ("GET TELEMETRY", self._get_telemetry, "t", COLOR_CYAN),
        ]

        btn_y = HEADER_HEIGHT + 8
        for label, cb, shortcut, color in actions:
            btn = Button(
                rect=(10, btn_y, 160, 42),
                text=label,
                callback=cb,
                shortcut=shortcut,
                color_accent=color,
                font_size=12
            )
            self.buttons.append(btn)
            btn_y += 48

    def _log(self, text):
        self.log_lines.append(text)
        if len(self.log_lines) > 12:
            self.log_lines = self.log_lines[-12:]

    def _connect(self):
        self._log("[*] Probing serial ports for ESP32...")
        ok, msg = self.client.auto_connect()
        if ok:
            self._log(f"[+] {msg}")
        else:
            self._log(f"[-] {msg}")

    def _ping(self):
        def task():
            self._log("[*] Sending ping RPC...")
            res = self.client.ping()
            self._log(f"-> {json.dumps(res)}")
        threading.Thread(target=task, daemon=True).start()

    def _toggle_gpio(self):
        def task():
            self.gpio_state = not self.gpio_state
            self._log(f"[*] Setting GPIO 2 -> {self.gpio_state}")
            res = self.client.set_gpio(2, self.gpio_state)
            self._log(f"-> {json.dumps(res)}")
        threading.Thread(target=task, daemon=True).start()

    def _read_adc(self):
        def task():
            self._log("[*] Reading Analog Pin 34...")
            res = self.client.read_analog(34)
            self._log(f"-> {json.dumps(res)}")
        threading.Thread(target=task, daemon=True).start()

    def _get_telemetry(self):
        def task():
            self._log("[*] Requesting telemetry...")
            res = self.client.get_telemetry()
            self._log(f"-> {json.dumps(res)}")
        threading.Thread(target=task, daemon=True).start()

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def update(self):
        pass

    def draw(self, surface):
        # Draw control buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Draw Output Panel
        panel_rect = pygame.Rect(180, HEADER_HEIGHT + 8, 290, CONTENT_HEIGHT - 16)
        pygame.draw.rect(surface, COLOR_BG_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=6)

        # Header status
        status_color = COLOR_PRIMARY if self.client.connected else COLOR_RED
        status_str = f"STATUS: {'ONLINE' if self.client.connected else 'OFFLINE'}"
        stat_surf = self.font.render(status_str, True, status_color)
        surface.blit(stat_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        # Render Log lines
        y = panel_rect.y + 30
        for line in self.log_lines:
            color = COLOR_PRIMARY if line.startswith("[+]") else (COLOR_RED if line.startswith("[-]") else (COLOR_CYAN if line.startswith("->") else COLOR_TEXT_MAIN))
            txt_surf = self.font.render(line[:36], True, color)
            surface.blit(txt_surf, (panel_rect.x + 10, y))
            y += 16
