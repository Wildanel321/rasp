"""
CyberDeck Wi-Fi & Hotspot Manager Screen
NetworkManager integration for mobile hotspot, scanning, profile management, and auto-connect
"""

import threading
import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button
from tools.network.wifi_manager import WiFiManager

class WiFiScreen:
    def __init__(self, on_navigate=None):
        self.title = "WI-FI & HOTSPOT MANAGER"
        self.on_navigate = on_navigate
        self.buttons = []
        self.log_lines = ["Wi-Fi Engine Active (NetworkManager).", "Ready to connect to AP or Mobile Hotspot."]
        self.font = get_font(size=11, bold=False, mono=True)
        self.font_bold = get_font(size=11, bold=True, mono=True)
        self.is_busy = False
        self._build_ui()

    def _build_ui(self):
        actions = [
            ("SCAN HOTSPOTS", self._scan_networks, "s", COLOR_PRIMARY),
            ("SAVED PROFILES", self._show_saved, "p", COLOR_CYAN),
            ("DISCONNECT", self._disconnect_wifi, "d", COLOR_RED),
            ("WI-FI STATUS", self._show_status, "i", COLOR_CYAN),
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

    def _scan_networks(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Scanning 2.4GHz/5GHz & Phone Hotspots...")
            nets = WiFiManager.scan_networks()
            if nets:
                self._log(f"[+] Found {len(nets)} network(s):")
                for n in nets[:5]:
                    in_use = " *" if n.get("active") else ""
                    self._log(f"    - {n['ssid'][:14]:<14} {n['signal']:2d}% ({n['security'][:4]}){in_use}")
            else:
                self._log("[-] No Wi-Fi networks in range.")
            self.is_busy = False
        threading.Thread(target=task, daemon=True).start()

    def _show_saved(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Querying saved Wi-Fi profiles...")
            saved = WiFiManager.get_saved_profiles()
            if saved:
                self._log(f"[+] {len(saved)} Saved Profile(s) (Auto-Connect ON):")
                for s in saved[:5]:
                    self._log(f"    - {s[:22]}")
            else:
                self._log("[-] No saved profiles found.")
            self.is_busy = False
        threading.Thread(target=task, daemon=True).start()

    def _disconnect_wifi(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Disconnecting Wi-Fi...")
            ok, msg = WiFiManager.disconnect()
            if ok:
                self._log("[+] Wi-Fi disconnected.")
            else:
                self._log(f"[-] {msg}")
            self.is_busy = False
        threading.Thread(target=task, daemon=True).start()

    def _show_status(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            info = WiFiManager.get_current_info()
            self._log("[*] Current Wi-Fi Status:")
            self._log(f"    SSID   : {info.get('ssid', 'N/A')}")
            self._log(f"    State  : {info.get('status', 'DISCONNECTED')}")
            self._log(f"    Signal : {info.get('signal', 0)}%")
            self.is_busy = False
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

        header_surf = self.font.render("NETWORKMANAGER WI-FI CONSOLE", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        y = panel_rect.y + 30
        for line in self.log_lines:
            color = COLOR_PRIMARY if line.startswith("[+]") else (COLOR_RED if line.startswith("[-]") else COLOR_TEXT_MAIN)
            txt_surf = self.font.render(line[:36], True, color)
            surface.blit(txt_surf, (panel_rect.x + 10, y))
            y += 16
