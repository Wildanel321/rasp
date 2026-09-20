"""
CyberDeck Raspberry Pi GPIO Screen
Interactive 40-pin GPIO header monitor and pin state toggler
"""

import pygame
from ui.config import (
    SCREEN_WIDTH, HEADER_HEIGHT, CONTENT_HEIGHT,
    COLOR_PRIMARY, COLOR_CYAN, COLOR_AMBER, COLOR_RED,
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, get_font
)
from ui.widgets.button import Button

class GPIOScreen:
    def __init__(self, on_navigate=None):
        self.title = "GPIO PINOUT & CONTROL"
        self.on_navigate = on_navigate
        self.font = get_font(size=11, bold=False, mono=True)
        self.font_bold = get_font(size=11, bold=True, mono=True)
        self.buttons = []
        
        # Track state of user toggleable GPIOs
        self.gpio_pins = {
            17: False,
            27: False,
            22: False,
            23: False,
            24: False,
        }
        self._build_ui()

    def _build_ui(self):
        # Left side: Quick toggle buttons for standard Raspberry Pi user GPIOs
        start_y = HEADER_HEIGHT + 10
        for pin in self.gpio_pins.keys():
            def make_cb(p):
                return lambda: self._toggle_pin(p)

            btn = Button(
                rect=(10, start_y, 140, 42),
                text=f"TOGGLE GPIO {pin}",
                callback=make_cb(pin),
                color_accent=COLOR_AMBER,
                font_size=12
            )
            self.buttons.append(btn)
            start_y += 48

    def _toggle_pin(self, pin):
        self.gpio_pins[pin] = not self.gpio_pins[pin]
        # Attempt hardware write if on Raspberry Pi with gpiod / sysfs
        try:
            import subprocess
            val = "1" if self.gpio_pins[pin] else "0"
            subprocess.run(["gpioset", "0", f"{pin}={val}"], check=False, timeout=0.5)
        except Exception:
            pass

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def update(self):
        pass

    def draw(self, surface):
        # Draw control buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Draw 40-Pin Header Reference Panel (Right side: 160, HEADER_HEIGHT+10, 310, 230)
        panel_rect = pygame.Rect(160, HEADER_HEIGHT + 10, 310, CONTENT_HEIGHT - 20)
        pygame.draw.rect(surface, COLOR_BG_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=6)

        header_surf = self.font_bold.render("RPi 3B 40-PIN HEADER MAP", True, COLOR_CYAN)
        surface.blit(header_surf, (panel_rect.x + 10, panel_rect.y + 8))
        pygame.draw.line(surface, COLOR_BORDER, (panel_rect.x, panel_rect.y + 24), (panel_rect.right, panel_rect.y + 24), 1)

        pin_map = [
            ("Pin 1: 3V3 PWR", "Pin 2: 5V PWR"),
            ("Pin 3: GPIO 2 (SDA)", "Pin 4: 5V PWR"),
            ("Pin 5: GPIO 3 (SCL)", "Pin 6: GND"),
            ("Pin 7: GPIO 4", "Pin 8: GPIO 14 (TXD)"),
            ("Pin 11: GPIO 17 [ACTIVE]", "Pin 12: GPIO 18 (PWM)"),
            ("Pin 13: GPIO 27 [ACTIVE]", "Pin 14: GND"),
            ("Pin 15: GPIO 22 [ACTIVE]", "Pin 16: GPIO 23 [ACTIVE]"),
            ("Pin 19: SPI0 MOSI (TFT)", "Pin 20: GND"),
            ("Pin 24: SPI0 CE0 (TFT)", "Pin 26: SPI0 CE1 (TOUCH)")
        ]

        y = panel_rect.y + 30
        for left_pin, right_pin in pin_map:
            l_color = COLOR_PRIMARY if "ACTIVE" in left_pin else (COLOR_AMBER if "PWR" in left_pin else COLOR_TEXT_MAIN)
            r_color = COLOR_PRIMARY if "ACTIVE" in right_pin else (COLOR_AMBER if "PWR" in right_pin else COLOR_TEXT_MAIN)
            
            l_surf = self.font.render(left_pin[:17], True, l_color)
            r_surf = self.font.render(right_pin[:17], True, r_color)
            
            surface.blit(l_surf, (panel_rect.x + 8, y))
            surface.blit(r_surf, (panel_rect.x + 155, y))
            y += 18
