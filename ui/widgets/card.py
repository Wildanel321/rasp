"""
CyberDeck Info Card Widget
Reusable container for metrics, hardware status, and network data
"""

import pygame
from ui.config import (
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_PRIMARY,
    COLOR_CYAN, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, get_font
)

class InfoCard:
    def __init__(self, rect, title, value="--", subtitle="", accent_color=COLOR_PRIMARY):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.accent_color = accent_color
        
        self.title_font = get_font(11, bold=True)
        self.value_font = get_font(16, bold=True, mono=True)
        self.sub_font = get_font(10, bold=False)

    def update(self, value, subtitle=None):
        self.value = str(value)
        if subtitle is not None:
            self.subtitle = str(subtitle)

    def draw(self, surface):
        # Card body
        pygame.draw.rect(surface, COLOR_BG_PANEL, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, width=1, border_radius=6)
        
        # Left accent stripe
        accent_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 4, 3, self.rect.height - 8)
        pygame.draw.rect(surface, self.accent_color, accent_rect, border_radius=2)

        # Title
        title_surf = self.title_font.render(self.title.upper(), True, COLOR_TEXT_MUTED)
        surface.blit(title_surf, (self.rect.x + 10, self.rect.y + 6))

        # Value
        val_surf = self.value_font.render(str(self.value), True, self.accent_color)
        surface.blit(val_surf, (self.rect.x + 10, self.rect.y + 20))

        # Subtitle
        if self.subtitle:
            sub_surf = self.sub_font.render(self.subtitle, True, COLOR_TEXT_MUTED)
            surface.blit(sub_surf, (self.rect.x + 10, self.rect.y + 42))
