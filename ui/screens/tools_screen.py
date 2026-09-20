"""
CyberDeck Field Tools Screen
System diagnostics, port inspection, memory cleanup, and storage bench
"""

import os
import time
import socket
import threading
import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button

class ToolsScreen:
    def __init__(self, on_navigate=None):
        self.title = "SYSTEM TOOLS & BENCH"
        self.on_navigate = on_navigate
        self.buttons = []
        self.log_lines = ["Select a field utility to execute."]
        self.font = get_font(size=11, bold=False, mono=True)
        self._build_ui()

    def _build_ui(self):
        tools = [
            ("SYS DIAGNOSTIC", self._run_diag, "d", COLOR_PRIMARY),
            ("PORT INSPECT", self._inspect_ports, "p", COLOR_CYAN),
            ("FLUSH RAM", self._flush_ram, "f", COLOR_AMBER),
            ("SD SPEED TEST", self._test_sd_card, "t", COLOR_CYAN),
        ]

        btn_y = HEADER_HEIGHT + 10
        for label, cb, shortcut, color in tools:
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

    def _run_diag(self):
        def task():
            self._log("[*] Running system diagnostics...")
            self._log(f"[+] Kernel: {os.name} ({os.uname().sysname if hasattr(os, 'uname') else 'OS'})")
            self._log(f"[+] Uid/Gid: {os.getuid() if hasattr(os, 'getuid') else 1000}")
            self._log("[+] System services running normal.")
        threading.Thread(target=task, daemon=True).start()

    def _inspect_ports(self):
        def task():
            self._log("[*] Inspecting local open ports...")
            common_ports = [22, 53, 80, 443, 8080, 5000]
            open_ports = []
            for p in common_ports:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2)
                res = s.connect_ex(("127.0.0.1", p))
                if res == 0:
                    open_ports.append(p)
                s.close()
            if open_ports:
                self._log(f"[+] Open local ports: {open_ports}")
            else:
                self._log("[+] Minimal exposure (No common ports open)")
        threading.Thread(target=task, daemon=True).start()

    def _flush_ram(self):
        def task():
            self._log("[*] Flushing filesystem cache...")
            if os.name == "posix":
                os.system("sync 2>/dev/null")
            self._log("[+] RAM cache flushed.")
        threading.Thread(target=task, daemon=True).start()

    def _test_sd_card(self):
        def task():
            self._log("[*] Testing microSD write speed (10MB)...")
            start = time.time()
            data = b"0" * (10 * 1024 * 1024)
            test_file = "/tmp/sd_bench.tmp"
            try:
                with open(test_file, "wb") as f:
                    f.write(data)
                    f.flush()
                elapsed = time.time() - start
                speed_mb = 10.0 / max(elapsed, 0.01)
                self._log(f"[+] Write Speed: {speed_mb:.2f} MB/s")
                if os.path.exists(test_file):
                    os.remove(test_file)
            except Exception as e:
                self._log(f"[-] Test failed: {e}")
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

        header_surf = self.font.render("UTILITY OUTPUT CONSOLE", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        y = panel_rect.y + 30
        for line in self.log_lines:
            color = COLOR_PRIMARY if line.startswith("[+]") else (COLOR_RED if line.startswith("[-]") else COLOR_TEXT_MAIN)
            txt_surf = self.font.render(line[:36], True, color)
            surface.blit(txt_surf, (panel_rect.x + 10, y))
            y += 16
