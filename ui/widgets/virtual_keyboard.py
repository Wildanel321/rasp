"""
CyberDeck QuickKey Bar Widget
Provides essential on-screen touch shortcuts for terminal interaction (ESC, TAB, CTRL+C, ARROWS)
"""

import pygame
from ui.config import (
    COLOR_BG_DARK, COLOR_BG_PANEL, COLOR_BORDER, COLOR_CYAN,
    COLOR_AMBER, COLOR_RED, COLOR_TEXT_MAIN, get_font
)
from ui.widgets.button import Button

class QuickKeyBar:
    def __init__(self, rect, on_key_send):
        self.rect = pygame.Rect(rect)
        self.on_key_send = on_key_send
        self.buttons = []
        self._build_buttons()

    def _build_buttons(self):
        keys = [
            ("ESC", "\x1b", COLOR_RED),
            ("TAB", "\t", COLOR_CYAN),
            ("^C", "\x03", COLOR_RED),
            ("^D", "\x04", COLOR_AMBER),
            ("▲", "\x1b[A", COLOR_CYAN),
            ("▼", "\x1b[B", COLOR_CYAN),
            ("◄", "\x1b[D", COLOR_CYAN),
            ("►", "\x1b[C", COLOR_CYAN),
            ("ENTER", "\r", COLOR_CYAN),
        ]

        total_btn = len(keys)
        btn_width = (self.rect.width - (total_btn + 1) * 3) // total_btn
        btn_height = self.rect.height

        for idx, (label, val, accent) in enumerate(keys):
            x = self.rect.x + 3 + idx * (btn_width + 3)
            # Create button callback closure
            def make_cb(seq):
                return lambda: self.on_key_send(seq)

            btn = Button(
                rect=(x, self.rect.y, btn_width, btn_height),
                text=label,
                callback=make_cb(val),
                color_accent=accent,
                font_size=11
            )
            self.buttons.append(btn)

    def handle_event(self, event):
        handled = False
        for btn in self.buttons:
            if btn.handle_event(event):
                handled = True
        return handled

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_BG_DARK, self.rect)
        for btn in self.buttons:
            btn.draw(surface)
