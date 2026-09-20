"""
CyberDeck OS - UI Configuration and Theme Constants
Target Display: 3.5" 480x320 SPI TFT (XPT2046 Touchscreen)
"""

import os
import pygame

# Display Dimensions
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 30

# UI Layout Heights
HEADER_HEIGHT = 34
FOOTER_HEIGHT = 30
CONTENT_HEIGHT = SCREEN_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT # 256px

# Color Palette (High-Contrast Cyberdeck Theme)
COLOR_BG_DARK = (13, 17, 23)        # #0d1117 Deep background
COLOR_BG_PANEL = (22, 27, 34)       # #161b22 Card / Panel background
COLOR_BG_HOVER = (33, 38, 45)       # #21262d Highlighted panel
COLOR_BORDER = (48, 54, 61)         # #30363d Subtle border

COLOR_PRIMARY = (0, 255, 128)       # Neon Green (Cyberdeck Green)
COLOR_CYAN = (0, 216, 255)          # Cyber Cyan
COLOR_AMBER = (255, 170, 0)         # Warning / Warm Yellow
COLOR_RED = (255, 68, 85)           # Alert Red
COLOR_TEXT_MAIN = (240, 246, 252)   # High readability white
COLOR_TEXT_MUTED = (139, 148, 158)  # Secondary text grey
COLOR_TEXT_DIM = (80, 90, 100)      # Dim labels

COLOR_TERMINAL_BG = (10, 12, 16)
COLOR_TERMINAL_FG = (0, 255, 128)

# Fonts loader helper
def get_font(size=14, bold=False, mono=False):
    """Returns a pygame Font object, falling back to system monospace or default."""
    try:
        if mono:
            return pygame.font.SysFont("monospace", size, bold=bold)
        return pygame.font.SysFont("dejavusans,freesans,sans-serif", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)
