"""
CyberDeck About Screen
Hardware and software specifications display
"""

import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER,
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)

class AboutScreen:
    def __init__(self, on_navigate=None):
        self.title = "ABOUT CYBERDECK OS"
        self.on_navigate = on_navigate
        self.font = get_font(size=11, bold=False, mono=True)
        self.font_bold = get_font(size=12, bold=True, mono=True)

    def handle_event(self, event):
        return False

    def update(self):
        pass

    def draw(self, surface):
        panel_rect = pygame.Rect(10, HEADER_HEIGHT + 10, SCREEN_WIDTH - 20, CONTENT_HEIGHT - 20)
        pygame.draw.rect(surface, COLOR_BG_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=6)

        # Header
        header_surf = self.font_bold.render("CYBERDECK OS // FIELD UNIT SPECIFICATION", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 14, panel_rect.y + 10))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 28), (panel_rect.right, panel_rect.y + 28), 1)

        specs = [
            ("OS Release", "CyberDeck OS v0.1.0-alpha"),
            ("Base Distro", "Raspberry Pi OS Lite (Debian Bookworm armhf)"),
            ("Target SoC", "Broadcom BCM2837 Quad-Core 64-bit ARMv8 @ 1.2GHz"),
            ("Target Board", "Raspberry Pi 3 Model B / 3B+ (1GB RAM)"),
            ("Display Unit", "3.5\" TFT LCD 480x320 SPI (ILI9486 Driver)"),
            ("Touch Engine", "Resistive Touch via XPT2046 / ADS7846 SPI"),
            ("Companion MCU", "ESP32 USB-Serial (JSON RPC Protocol)"),
            ("UI Engine", "Hardware Framebuffer Direct Engine (<40MB RAM)"),
            ("License", "MIT Open Source License (2026)")
        ]

        y = panel_rect.y + 36
        for label, val in specs:
            lbl_surf = self.font.render(f"{label:14}:", True, COLOR_PRIMARY)
            val_surf = self.font.render(val, True, COLOR_TEXT_MAIN)
            surface.blit(lbl_surf, (panel_rect.x + 14, y))
            surface.blit(val_surf, (panel_rect.x + 130, y))
            y += 18
