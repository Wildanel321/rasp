"""
CyberDeck Main Menu Screen
2x4 Grid with large tactile touch targets and number hotkeys
"""

import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_TEXT_MAIN
)
from ui.widgets.button import Button

class MenuScreen:
    def __init__(self, on_navigate):
        self.title = "MAIN MENU"
        self.on_navigate = on_navigate
        self.buttons = []
        self._build_menu()

    def _build_menu(self):
        items = [
            ("TERMINAL", "terminal", "1", COLOR_PRIMARY),
            ("AUDIT / LAB", "audit", "2", COLOR_RED),
            ("NETWORK", "network", "3", COLOR_CYAN),
            ("SYSTEM", "system", "4", COLOR_CYAN),
            ("ESP32", "esp32", "5", COLOR_AMBER),
            ("GPIO", "gpio", "6", COLOR_AMBER),
            ("TOOLS", "tools", "7", COLOR_PRIMARY),
            ("SETTINGS", "settings", "8", COLOR_PRIMARY),
        ]

        cols = 2
        rows = 4
        spacing = 8
        start_x = 10
        start_y = HEADER_HEIGHT + 8
        
        btn_width = (SCREEN_WIDTH - start_x * 2 - (cols - 1) * spacing) // cols  # ~226px
        btn_height = (CONTENT_HEIGHT - 16 - (rows - 1) * spacing) // rows        # ~50px

        for idx, (label, route, shortcut, color) in enumerate(items):
            r = idx // cols
            c = idx % cols
            x = start_x + c * (btn_width + spacing)
            y = start_y + r * (btn_height + spacing)

            def make_cb(target_route):
                return lambda: self.on_navigate(target_route)

            btn = Button(
                rect=(x, y, btn_width, btn_height),
                text=label,
                callback=make_cb(route),
                shortcut=shortcut,
                color_accent=color,
                font_size=15
            )
            self.buttons.append(btn)

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
