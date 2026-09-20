"""
CyberDeck Settings & Power Screen
Touch calibration, screen rotation, UI restart, and safe power controls
"""

import os
import subprocess
import threading
import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button

class SettingsScreen:
    def __init__(self, on_navigate=None):
        self.title = "SYSTEM SETTINGS"
        self.on_navigate = on_navigate
        self.buttons = []
        self.log_lines = ["Select system configuration setting."]
        self.font = get_font(size=11, bold=False, mono=True)
        self._build_ui()

    def _build_ui(self):
        actions = [
            ("CALIBRATE TOUCH", self._calibrate_touch, "c", COLOR_CYAN),
            ("RESTART UI", self._restart_ui, "u", COLOR_AMBER),
            ("REBOOT SYSTEM", self._reboot, "r", COLOR_AMBER),
            ("SHUTDOWN SAFE", self._poweroff, "s", COLOR_RED),
        ]

        btn_y = HEADER_HEIGHT + 10
        for label, cb, shortcut, color in actions:
            btn = Button(
                rect=(10, btn_y, 160, 48),
                text=label,
                callback=cb,
                shortcut=shortcut,
                color_accent=color,
                font_size=13
            )
            self.buttons.append(btn)
            btn_y += 56

    def _log(self, text):
        self.log_lines.append(text)
        if len(self.log_lines) > 12:
            self.log_lines = self.log_lines[-12:]

    def _calibrate_touch(self):
        self._log("[*] Launching touchscreen calibration...")
        try:
            subprocess.Popen(["ts_calibrate"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log("[+] ts_calibrate process spawned.")
        except Exception:
            self._log("[-] Calibration tool not active in simulator.")

    def _restart_ui(self):
        self._log("[*] Restarting CyberDeck UI service...")
        def task():
            try:
                subprocess.run(["sudo", "systemctl", "restart", "cyberdeck-ui"], check=False)
            except Exception:
                pass
        threading.Thread(target=task, daemon=True).start()

    def _reboot(self):
        self._log("[*] Initiating system reboot...")
        def task():
            try:
                subprocess.run(["sudo", "reboot"], check=False)
            except Exception:
                pass
        threading.Thread(target=task, daemon=True).start()

    def _poweroff(self):
        self._log("[*] Shutting down CyberDeck...")
        def task():
            try:
                subprocess.run(["sudo", "poweroff"], check=False)
            except Exception:
                pass
        threading.Thread(target=task, daemon=True).start()

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def update(self):
        pass

    def draw(self, surface):
        for btn in self.buttons:
            btn.draw(surface)

        panel_rect = pygame.Rect(180, HEADER_HEIGHT + 10, 290, CONTENT_HEIGHT - 20)
        pygame.draw.rect(surface, COLOR_BG_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=6)

        header_surf = self.font.render("SETTINGS & POWER CONTROL", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        y = panel_rect.y + 30
        for line in self.log_lines:
            color = COLOR_PRIMARY if line.startswith("[+]") else (COLOR_RED if line.startswith("[-]") else COLOR_TEXT_MAIN)
            txt_surf = self.font.render(line[:36], True, color)
            surface.blit(txt_surf, (panel_rect.x + 10, y))
            y += 16
