"""
CyberDeck Status Bars (Header and Footer)
Provides continuous system health telemetry and quick navigation
"""

import time
import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, FOOTER_HEIGHT, SCREEN_HEIGHT,
    COLOR_BG_DARK, COLOR_BG_PANEL, COLOR_BORDER, COLOR_PRIMARY,
    COLOR_CYAN, COLOR_AMBER, COLOR_RED, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button

class HeaderBar:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, HEADER_HEIGHT)
        self.font_title = get_font(13, bold=True)
        self.font_stat = get_font(12, bold=True, mono=True)
        self.font_time = get_font(12, bold=False, mono=True)

    def draw(self, surface, current_screen_title, cpu_percent, ram_percent):
        # Draw bar background and bottom separator
        pygame.draw.rect(surface, COLOR_BG_PANEL, self.rect)
        pygame.draw.line(surface, COLOR_BORDER, (0, HEADER_HEIGHT - 1), (SCREEN_WIDTH, HEADER_HEIGHT - 1), 1)

        # Title / Screen indicator
        title_text = f"DECK // {current_screen_title.upper()}"
        title_surf = self.font_title.render(title_text, True, COLOR_CYAN)
        surface.blit(title_surf, (10, 8))

        # CPU Indicator Badge
        cpu_color = COLOR_PRIMARY if cpu_percent < 70 else (COLOR_AMBER if cpu_percent < 90 else COLOR_RED)
        cpu_text = f"CPU {int(cpu_percent):2d}%"
        cpu_surf = self.font_stat.render(cpu_text, True, cpu_color)
        surface.blit(cpu_surf, (220, 9))

        # RAM Indicator Badge
        ram_color = COLOR_PRIMARY if ram_percent < 75 else (COLOR_AMBER if ram_percent < 90 else COLOR_RED)
        ram_text = f"RAM {int(ram_percent):2d}%"
        ram_surf = self.font_stat.render(ram_text, True, ram_color)
        surface.blit(ram_surf, (300, 9))

        # Live Clock
        time_str = time.strftime("%H:%M:%S")
        time_surf = self.font_time.render(time_str, True, COLOR_TEXT_MUTED)
        surface.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 10, 9))


class FooterBar:
    def __init__(self, on_back_click=None):
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - FOOTER_HEIGHT, SCREEN_WIDTH, FOOTER_HEIGHT)
        self.font_stat = get_font(11, bold=True, mono=True)
        self.on_back_click = on_back_click
        
        # Back / Menu button on footer
        self.back_btn = Button(
            rect=(SCREEN_WIDTH - 76, SCREEN_HEIGHT - FOOTER_HEIGHT + 2, 70, FOOTER_HEIGHT - 4),
            text="MENU",
            callback=self.on_back_click,
            shortcut="m",
            color_accent=COLOR_CYAN,
            font_size=12
        )

    def handle_event(self, event):
        return self.back_btn.handle_event(event)

    def draw(self, surface, wifi_status, cpu_temp, ip_address, is_main_menu=False):
        # Draw bar background and top separator
        pygame.draw.rect(surface, COLOR_BG_PANEL, self.rect)
        pygame.draw.line(surface, COLOR_BORDER, (0, SCREEN_HEIGHT - FOOTER_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - FOOTER_HEIGHT), 1)

        # Wi-Fi status indicator
        wifi_color = COLOR_PRIMARY if wifi_status == "CONNECTED" else COLOR_TEXT_MUTED
        wifi_text = f"WIFI: {wifi_status}"
        wifi_surf = self.font_stat.render(wifi_text, True, wifi_color)
        surface.blit(wifi_surf, (10, SCREEN_HEIGHT - FOOTER_HEIGHT + 7))

        # CPU Temperature
        temp_color = COLOR_PRIMARY if cpu_temp < 60 else (COLOR_AMBER if cpu_temp < 75 else COLOR_RED)
        temp_text = f"TEMP: {int(cpu_temp)}°C" if cpu_temp > 0 else "TEMP: --"
        temp_surf = self.font_stat.render(temp_text, True, temp_color)
        surface.blit(temp_surf, (140, SCREEN_HEIGHT - FOOTER_HEIGHT + 7))

        # IP Address
        ip_text = f"IP: {ip_address}" if ip_address else "IP: NO LINK"
        ip_surf = self.font_stat.render(ip_text, True, COLOR_TEXT_MUTED)
        surface.blit(ip_surf, (240, SCREEN_HEIGHT - FOOTER_HEIGHT + 7))

        # Render Back/Menu button if not already on Main Menu
        if not is_main_menu:
            self.back_btn.draw(surface)
