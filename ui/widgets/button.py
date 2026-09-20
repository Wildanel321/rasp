"""
CyberDeck Touch Button Widget
Optimized for 3.5" touchscreen touch targets (min 40px height)
"""

import pygame
from ui.config import (
    COLOR_BG_PANEL, COLOR_BG_HOVER, COLOR_BORDER,
    COLOR_PRIMARY, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, get_font
)

class Button:
    def __init__(self, rect, text, callback=None, shortcut=None, color_accent=COLOR_PRIMARY, 
                 bg_color=COLOR_BG_PANEL, text_color=COLOR_TEXT_MAIN, font_size=15, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.shortcut = shortcut
        self.color_accent = color_accent
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.enabled = enabled
        self.is_pressed = False
        self.font = get_font(size=self.font_size, bold=True)
        self.shortcut_font = get_font(size=11, bold=False, mono=True)

    def handle_event(self, event):
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    if self.callback:
                        self.callback()
                    return True
        elif event.type == pygame.KEYDOWN and self.shortcut:
            if event.unicode.lower() == self.shortcut.lower():
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface):
        # Determine background color based on state
        if not self.enabled:
            bg = (20, 24, 30)
            border_color = (40, 45, 50)
            text_color = COLOR_TEXT_MUTED
        elif self.is_pressed:
            bg = COLOR_BG_HOVER
            border_color = self.color_accent
            text_color = self.color_accent
        else:
            bg = self.bg_color
            border_color = COLOR_BORDER
            text_color = self.text_color

        # Background and outline
        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        border_width = 2 if self.is_pressed else 1
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=6)

        # Draw left accent indicator line
        if self.enabled:
            accent_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 6, 3, self.rect.height - 12)
            pygame.draw.rect(surface, self.color_accent, accent_rect, border_radius=2)

        # Draw Text
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.centerx + 4, self.rect.centery))
        surface.blit(text_surf, text_rect)

        # Draw Shortcut badge if available (e.g. "[1]")
        if self.shortcut and self.enabled:
            badge_surf = self.shortcut_font.render(f"[{self.shortcut.upper()}]", True, COLOR_TEXT_MUTED)
            surface.blit(badge_surf, (self.rect.right - badge_surf.get_width() - 8, self.rect.y + 4))
