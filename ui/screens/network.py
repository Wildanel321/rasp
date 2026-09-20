"""
CyberDeck Network Screen
Network interface status, latency probing, and local discovery utilities
"""

import threading
import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_DARK, COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button
from ui.services.network_service import NetworkService

class NetworkScreen:
    def __init__(self, on_navigate=None):
        self.title = "NETWORK UTILITIES"
        self.on_navigate = on_navigate
        self.buttons = []
        self.log_lines = ["Ready for network diagnostics."]
        self.is_scanning = False
        self.font = get_font(size=11, bold=False, mono=True)
        self._build_ui()

    def _build_ui(self):
        # Actions on Left column (width: 170px)
        actions = [
            ("PING INTERNET", self._ping_internet, "p", COLOR_PRIMARY),
            ("SCAN SUBNET", self._scan_subnet, "s", COLOR_CYAN),
            ("SCAN WI-FI", self._scan_wifi, "w", COLOR_AMBER),
            ("SHOW IFACES", self._show_interfaces, "i", COLOR_CYAN),
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

    def _ping_internet(self):
        def task():
            self._log("[*] Pinging 1.1.1.1 (Cloudflare DNS)...")
            ok, lat = NetworkService.ping_host("1.1.1.1")
            if ok:
                self._log(f"[+] Ping Success! Latency: {lat} ms")
            else:
                self._log("[-] Ping Failed (Host Unreachable)")
        threading.Thread(target=task, daemon=True).start()

    def _scan_subnet(self):
        def task():
            self._log("[*] Scanning local subnet hosts...")
            hosts = NetworkService.discover_local_hosts()
            if hosts:
                self._log(f"[+] Found {len(hosts)} active host(s):")
                for h in hosts[:4]:
                    self._log(f"    - {h}")
            else:
                self._log("[-] No active hosts responding.")
        threading.Thread(target=task, daemon=True).start()

    def _scan_wifi(self):
        def task():
            self._log("[*] Scanning 2.4GHz / 5GHz Wi-Fi...")
            nets = NetworkService.scan_wifi_networks()
            self._log(f"[+] Found {len(nets)} wireless network(s):")
            for n in nets[:5]:
                self._log(f"    - {n['ssid'][:14]} ({n['signal']})")
        threading.Thread(target=task, daemon=True).start()

    def _show_interfaces(self):
        self._log("[*] Active Network Interfaces:")
        ifaces = NetworkService.get_interfaces()
        for iface in ifaces:
            self._log(f"    {iface['name']}: {iface['ip']}")

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def update(self):
        pass

    def draw(self, surface):
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Draw Log / Results Display Panel (Right area: 180, HEADER_HEIGHT+10, 290, 230)
        panel_rect = pygame.Rect(180, HEADER_HEIGHT + 10, 290, CONTENT_HEIGHT - 20)
        pygame.draw.rect(surface, COLOR_BG_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=6)

        # Panel Header
        header_surf = self.font.render("CONSOLE LOG & OUTPUT", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        # Render Log lines
        y = panel_rect.y + 30
        for line in self.log_lines:
            text_color = COLOR_PRIMARY if line.startswith("[+]") else (COLOR_RED if line.startswith("[-]") else COLOR_TEXT_MAIN)
            txt_surf = self.font.render(line[:36], True, text_color)
            surface.blit(txt_surf, (panel_rect.x + 10, y))
            y += 16
