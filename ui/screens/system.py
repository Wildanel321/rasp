"""
CyberDeck System Monitor Screen
Live metrics dashboard displaying CPU, RAM, Disk, Temperature, and Uptime
"""

import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_BORDER
)
from ui.widgets.card import InfoCard
from ui.widgets.button import Button

class SystemScreen:
    def __init__(self, sys_monitor, on_navigate=None):
        self.title = "SYSTEM MONITOR"
        self.sys_monitor = sys_monitor
        self.on_navigate = on_navigate
        self.cards = []
        self._build_cards()

    def _build_cards(self):
        # 6 Cards in 3x2 Grid
        cols = 3
        rows = 2
        spacing = 8
        start_x = 10
        start_y = HEADER_HEIGHT + 10
        
        card_w = (SCREEN_WIDTH - start_x * 2 - (cols - 1) * spacing) // cols  # ~148px
        card_h = (CONTENT_HEIGHT - 20 - (rows - 1) * spacing) // rows         # ~114px

        self.card_cpu = InfoCard((0, 0, card_w, card_h), "CPU USAGE", "--%", "Load: 0.00", COLOR_PRIMARY)
        self.card_ram = InfoCard((0, 0, card_w, card_h), "MEMORY (RAM)", "--%", "0 / 1024 MB", COLOR_CYAN)
        self.card_disk = InfoCard((0, 0, card_w, card_h), "DISK USAGE", "--%", "Free: -- GB", COLOR_CYAN)
        self.card_temp = InfoCard((0, 0, card_w, card_h), "THERMAL", "--°C", "SoC BCM2837", COLOR_AMBER)
        self.card_uptime = InfoCard((0, 0, card_w, card_h), "UPTIME", "--", "Active session", COLOR_PRIMARY)
        self.card_host = InfoCard((0, 0, card_w, card_h), "HOST & NODE", self.sys_monitor.hostname, "RPi 3 Model B", COLOR_CYAN)

        card_list = [self.card_cpu, self.card_ram, self.card_disk, self.card_temp, self.card_uptime, self.card_host]
        
        for idx, card in enumerate(card_list):
            r = idx // cols
            c = idx % cols
            card.rect.x = start_x + c * (card_w + spacing)
            card.rect.y = start_y + r * (card_h + spacing)
            self.cards.append(card)

    def handle_event(self, event):
        return False

    def update(self):
        # Update CPU card
        cpu_load = f"Load: {self.sys_monitor.load_avg[0]:.2f}"
        self.card_cpu.update(f"{int(self.sys_monitor.cpu_percent)}%", cpu_load)
        if self.sys_monitor.cpu_percent > 85:
            self.card_cpu.accent_color = COLOR_RED
        elif self.sys_monitor.cpu_percent > 65:
            self.card_cpu.accent_color = COLOR_AMBER
        else:
            self.card_cpu.accent_color = COLOR_PRIMARY

        # Update RAM card
        ram_sub = f"{self.sys_monitor.ram_used_mb} / {self.sys_monitor.ram_total_mb} MB"
        self.card_ram.update(f"{int(self.sys_monitor.ram_percent)}%", ram_sub)

        # Update Disk card
        disk_sub = f"Free: {self.sys_monitor.disk_free_gb} GB"
        self.card_disk.update(f"{int(self.sys_monitor.disk_percent)}%", disk_sub)

        # Update Temp card
        self.card_temp.update(f"{int(self.sys_monitor.cpu_temp)}°C", "SoC BCM2837")
        if self.sys_monitor.cpu_temp > 75:
            self.card_temp.accent_color = COLOR_RED
        elif self.sys_monitor.cpu_temp > 60:
            self.card_temp.accent_color = COLOR_AMBER
        else:
            self.card_temp.accent_color = COLOR_PRIMARY

        # Update Uptime
        self.card_uptime.update(self.sys_monitor.uptime_str, "Active session")

    def draw(self, surface):
        for card in self.cards:
            card.draw(surface)
