"""
CyberDeck Network Audit & Security Inspection Screen
Fast touch-based tools for authorized network assessment and packet analysis
"""

import os
import re
import socket
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

class AuditScreen:
    def __init__(self, on_navigate=None):
        self.title = "NETWORK AUDIT & RECON"
        self.on_navigate = on_navigate
        self.buttons = []
        self.log_lines = ["Network Audit Engine Ready.", "Select a diagnostic utility below."]
        self.font = get_font(size=11, bold=False, mono=True)
        self.is_busy = False
        self._build_ui()

    def _build_ui(self):
        actions = [
            ("ARP DISCOVERY", self._arp_discovery, "a", COLOR_PRIMARY),
            ("PORT AUDIT (TOP)", self._port_audit, "p", COLOR_CYAN),
            ("PACKET SNIFF (5s)", self._packet_sniff, "s", COLOR_AMBER),
            ("WI-FI RECON", self._wifi_recon, "w", COLOR_PRIMARY),
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

    def _arp_discovery(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Running ARP layer host discovery...")
            # Try arp-scan if available, else socket fallback
            try:
                res = subprocess.run(["sudo", "arp-scan", "--localnet", "--interface=wlan0"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if re.match(r"^\d+\.\d+\.\d+\.\d+", line):
                            parts = line.split()
                            self._log(f"[+] {parts[0]} -> {parts[1][:17]}")
                else:
                    self._run_socket_scan()
            except Exception:
                self._run_socket_scan()
            self.is_busy = False
        threading.Thread(target=task, daemon=True).start()

    def _run_socket_scan(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            my_ip = s.getsockname()[0]
            s.close()
            prefix = ".".join(my_ip.split(".")[:3])
        except Exception:
            prefix = "192.168.1"
        self._log(f"[*] Probing subnet {prefix}.0/24...")
        found = 0
        for i in range(1, 35):
            tip = f"{prefix}.{i}"
            try:
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sk.settimeout(0.08)
                if sk.connect_ex((tip, 80)) == 0 or sk.connect_ex((tip, 22)) == 0:
                    self._log(f"[+] Active Host: {tip}")
                    found += 1
                sk.close()
            except Exception:
                pass
        self._log(f"[*] Discovery complete. ({found} active)")

    def _port_audit(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Auditing common service ports...")
            target = "127.0.0.1"
            ports = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1883, 3306, 5000, 8080]
            open_p = []
            for p in ports:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.15)
                if s.connect_ex((target, p)) == 0:
                    open_p.append(p)
                    self._log(f"[+] Port {p:<5} [OPEN]")
                s.close()
            if not open_p:
                self._log("[+] No common open ports on localhost.")
            self.is_busy = False
        threading.Thread(target=task, daemon=True).start()

    def _packet_sniff(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Sniffing live packets (5 seconds)...")
            try:
                # Run tcpdump sample
                res = subprocess.run(["sudo", "tcpdump", "-c", "5", "-nn", "-i", "any"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=6)
                if res.returncode == 0:
                    for line in res.stdout.splitlines()[:5]:
                        self._log(f"[>] {line[:34]}")
                else:
                    self._log("[-] tcpdump capture error or interface busy.")
            except Exception as e:
                self._log(f"[-] Sniff error: {e}")
            self.is_busy = False
        threading.Thread(target=task, daemon=True).start()

    def _wifi_recon(self):
        if self.is_busy:
            return
        def task():
            self.is_busy = True
            self._log("[*] Performing Wi-Fi reconnaissance...")
            try:
                res = subprocess.run(["sudo", "iw", "dev", "wlan0", "scan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                if res.returncode == 0:
                    ssids = re.findall(r'SSID:\s*([^\n]+)', res.stdout)
                    signals = re.findall(r'signal:\s*([^\n]+)', res.stdout)
                    for idx, s in enumerate(ssids[:4]):
                        sig = signals[idx] if idx < len(signals) else "N/A"
                        self._log(f"[+] {s[:16]:<16} ({sig[:7]})")
                else:
                    self._log("[-] Wireless interface wlan0 unavailable.")
            except Exception as e:
                self._log(f"[-] Recon error: {e}")
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

        header_surf = self.font.render("AUDIT LOG & PACKET CONSOLE", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        y = panel_rect.y + 30
        for line in self.log_lines:
            color = COLOR_PRIMARY if line.startswith("[+]") else (COLOR_AMBER if line.startswith("[>]") else (COLOR_RED if line.startswith("[-]") else COLOR_TEXT_MAIN))
            txt_surf = self.font.render(line[:36], True, color)
            surface.blit(txt_surf, (panel_rect.x + 10, y))
            y += 16
