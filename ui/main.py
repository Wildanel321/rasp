#!/usr/bin/env python3
"""
CyberDeck OS - Main User Interface
Optimized for 3.5" (480x320) TFT Touchscreen & USB Keyboard on Raspberry Pi 3
"""

import os
import sys
import argparse
import signal
import pygame

# Add project root to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG_DARK,
    HEADER_HEIGHT, FOOTER_HEIGHT
)
from ui.widgets.status_bar import HeaderBar, FooterBar
from ui.services.system_monitor import SystemMonitor
from ui.screens.menu import MenuScreen
from ui.screens.terminal import TerminalScreen
from ui.screens.system import SystemScreen
from ui.screens.network import NetworkScreen
from ui.screens.esp32_screen import ESP32Screen
from ui.screens.gpio_screen import GPIOScreen
from ui.screens.tools_screen import ToolsScreen
from ui.screens.audit_screen import AuditScreen
from ui.screens.wifi_screen import WiFiScreen
from ui.screens.settings import SettingsScreen
from ui.screens.about import AboutScreen

class CyberDeckApp:
    def __init__(self, fullscreen=False, windowed=False):
        self.fullscreen = fullscreen
        self.windowed = windowed
        self.running = True

        # Framebuffer / Display environment configuration for RPi TFT
        if not self.windowed and os.path.exists("/dev/fb1"):
            os.environ["SDL_FBDEV"] = "/dev/fb1"
            if "SDL_VIDEODRIVER" not in os.environ:
                os.environ["SDL_VIDEODRIVER"] = "fbcon"

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("CyberDeck OS v0.1.0")

        flags = 0
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        self.clock = pygame.time.Clock()

        # Hide cursor on physical touchscreen if not in windowed debug mode
        if not self.windowed and os.name == "posix":
            pygame.mouse.set_visible(False)

        # Background Services
        self.sys_monitor = SystemMonitor(interval=1.0)
        self.sys_monitor.start()

        # UI Bars
        self.header_bar = HeaderBar()
        self.footer_bar = FooterBar(on_back_click=self.navigate_to_menu)

        # Instantiate Screens
        self.screens = {
            "menu": MenuScreen(on_navigate=self.navigate_to),
            "terminal": TerminalScreen(on_navigate=self.navigate_to),
            "audit": AuditScreen(on_navigate=self.navigate_to),
            "wifi": WiFiScreen(on_navigate=self.navigate_to),
            "system": SystemScreen(self.sys_monitor, on_navigate=self.navigate_to),
            "network": NetworkScreen(on_navigate=self.navigate_to),
            "esp32": ESP32Screen(on_navigate=self.navigate_to),
            "gpio": GPIOScreen(on_navigate=self.navigate_to),
            "tools": ToolsScreen(on_navigate=self.navigate_to),
            "settings": SettingsScreen(on_navigate=self.navigate_to),
            "about": AboutScreen(on_navigate=self.navigate_to)
        }

        self.current_screen_id = "menu"
        self.current_screen = self.screens["menu"]

        # Signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._sig_handler)
        signal.signal(signal.SIGTERM, self._sig_handler)

    def _sig_handler(self, sig, frame):
        self.running = False

    def navigate_to(self, screen_id):
        if screen_id in self.screens:
            self.current_screen_id = screen_id
            self.current_screen = self.screens[screen_id]

    def navigate_to_menu(self):
        self.navigate_to("menu")

    def run(self):
        while self.running:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                # Global hotkey: Escape or 'M' returns to Main Menu (except when in terminal)
                if event.type == pygame.KEYDOWN and self.current_screen_id != "terminal":
                    if event.key in (pygame.K_ESCAPE, pygame.K_m):
                        self.navigate_to_menu()
                        continue

                # Pass event to Footer (Back button)
                is_main = (self.current_screen_id == "menu")
                if not is_main and self.footer_bar.handle_event(event):
                    continue

                # Pass event to active screen
                self.current_screen.handle_event(event)

            # 2. State updates
            self.current_screen.update()

            # 3. Drawing
            self.screen.fill(COLOR_BG_DARK)

            # Draw active screen content
            self.current_screen.draw(self.screen)

            # Draw Header Bar
            self.header_bar.draw(
                self.screen,
                current_screen_title=self.current_screen.title,
                cpu_percent=self.sys_monitor.cpu_percent,
                ram_percent=self.sys_monitor.ram_percent
            )

            # Draw Footer Bar
            self.footer_bar.draw(
                self.screen,
                wifi_status=self.sys_monitor.wifi_status,
                cpu_temp=self.sys_monitor.cpu_temp,
                ip_address=self.sys_monitor.ip_address,
                is_main_menu=(self.current_screen_id == "menu")
            )

            pygame.display.flip()
            self.clock.tick(FPS)

        # Cleanup
        self.sys_monitor.stop()
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="CyberDeck OS User Interface")
    parser.add_argument("--fullscreen", "-f", action="store_true", help="Launch in fullscreen mode")
    parser.add_argument("--windowed", "-w", action="store_true", help="Launch in windowed mode (for host development)")
    args = parser.parse_args()

    app = CyberDeckApp(fullscreen=args.fullscreen, windowed=args.windowed)
    app.run()

if __name__ == "__main__":
    main()
