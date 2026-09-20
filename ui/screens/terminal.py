"""
CyberDeck Terminal Screen
Embedded Real Linux Terminal with PTY integration and Touch QuickKeys
"""

import os
import sys
import time
import select
import threading
import pygame
from ui.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HEADER_HEIGHT, FOOTER_HEIGHT,
    COLOR_TERMINAL_BG, COLOR_TERMINAL_FG, COLOR_BG_PANEL,
    COLOR_BORDER, COLOR_CYAN, COLOR_TEXT_MUTED, get_font
)
from ui.widgets.virtual_keyboard import QuickKeyBar

class TerminalScreen:
    def __init__(self, on_navigate=None):
        self.title = "TERMINAL"
        self.on_navigate = on_navigate
        self.font = get_font(size=11, bold=False, mono=True)
        self.char_w = 7
        self.char_h = 13
        
        # Geometry
        self.term_y = HEADER_HEIGHT
        self.quickbar_h = 24
        self.term_h = SCREEN_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - self.quickbar_h
        self.quickbar_y = self.term_y + self.term_h
        
        self.cols = SCREEN_WIDTH // self.char_w
        self.rows = self.term_h // self.char_h

        # Buffer
        self.lines = ["Welcome to CyberDeck OS Terminal (v0.1.0)", "Type commands or use USB keyboard / touch keys."]
        self.scroll_offset = 0
        self.max_scroll = 500

        # PTY Master FD
        self.pty_fd = None
        self.pty_pid = None
        self.running = True
        self.lock = threading.Lock()

        # QuickKeys Bar
        self.quickbar = QuickKeyBar(
            rect=(0, self.quickbar_y, SCREEN_WIDTH, self.quickbar_h),
            on_key_send=self.send_input
        )

        self._start_pty()

    def _start_pty(self):
        """Starts genuine /bin/bash process inside pseudo-terminal (on Linux)."""
        if os.name != "posix":
            self.lines.append("Simulation mode (non-POSIX system detected).")
            self.lines.append("deck@cyberdeck:~$ ")
            return

        try:
            import pty
            self.pty_pid, self.pty_fd = pty.fork()
            if self.pty_pid == 0:
                # Child process: spawn bash
                os.environ["TERM"] = "linux"
                os.environ["PS1"] = r"\u@\h:\w\$ "
                os.execlp("/bin/bash", "/bin/bash", "-i")
            else:
                # Parent process: reader thread
                t = threading.Thread(target=self._pty_reader, daemon=True)
                t.start()
        except Exception as e:
            self.lines.append(f"Failed to spawn PTY: {e}")

    def _pty_reader(self):
        buf = ""
        while self.running and self.pty_fd is not None:
            try:
                r, _, _ = select.select([self.pty_fd], [], [], 0.1)
                if self.pty_fd in r:
                    data = os.read(self.pty_fd, 1024).decode("utf-8", errors="replace")
                    if not data:
                        break
                    with self.lock:
                        for ch in data:
                            if ch == "\r":
                                pass
                            elif ch == "\n":
                                self.lines.append(buf)
                                buf = ""
                            elif ch == "\x08" or ch == "\x7f":
                                buf = buf[:-1]
                            elif ch == "\x1b":
                                # Strip basic ANSI escapes for clean RPi3 rendering
                                pass
                            else:
                                buf += ch
                        if buf:
                            if len(self.lines) > 0:
                                self.lines[-1] = buf
                            else:
                                self.lines.append(buf)
                        if len(self.lines) > self.max_scroll:
                            self.lines = self.lines[-self.max_scroll:]
            except Exception:
                break

    def send_input(self, text):
        """Sends keystrokes or escape sequences to PTY."""
        if self.pty_fd is not None and os.name == "posix":
            try:
                os.write(self.pty_fd, text.encode("utf-8"))
            except Exception:
                pass
        else:
            # Simulation fallback
            if text == "\r":
                last = self.lines[-1] if self.lines else ""
                cmd = last.replace("deck@cyberdeck:~$ ", "").strip()
                if cmd == "clear":
                    self.lines = ["deck@cyberdeck:~$ "]
                elif cmd == "uname -a":
                    self.lines.append("Linux cyberdeck 6.1.0-rpi3-v7+ #1 SMP armv7l GNU/Linux")
                    self.lines.append("deck@cyberdeck:~$ ")
                else:
                    self.lines.append(f"cyberdeck: command executed: {cmd}")
                    self.lines.append("deck@cyberdeck:~$ ")
            elif text == "\x03":
                self.lines.append("^C")
                self.lines.append("deck@cyberdeck:~$ ")
            else:
                self.lines[-1] += text

    def handle_event(self, event):
        # 1. Quickbar touch events
        if self.quickbar.handle_event(event):
            return True

        # 2. Touch scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: # Scroll Up
                self.scroll_offset = min(self.scroll_offset + 2, len(self.lines) - self.rows)
                return True
            elif event.button == 5: # Scroll Down
                self.scroll_offset = max(self.scroll_offset - 2, 0)
                return True

        # 3. Keyboard typing
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.send_input("\r")
            elif event.key == pygame.K_BACKSPACE:
                self.send_input("\x7f")
            elif event.key == pygame.K_TAB:
                self.send_input("\t")
            elif event.key == pygame.K_ESCAPE:
                self.send_input("\x1b")
            elif event.key == pygame.K_UP:
                self.send_input("\x1b[A")
            elif event.key == pygame.K_DOWN:
                self.send_input("\x1b[B")
            elif event.key == pygame.K_LEFT:
                self.send_input("\x1b[D")
            elif event.key == pygame.K_RIGHT:
                self.send_input("\x1b[C")
            elif event.unicode:
                self.send_input(event.unicode)
            return True

        return False

    def update(self):
        pass

    def draw(self, surface):
        # Draw terminal background
        term_rect = pygame.Rect(0, self.term_y, SCREEN_WIDTH, self.term_h)
        pygame.draw.rect(surface, COLOR_TERMINAL_BG, term_rect)
        pygame.draw.line(surface, COLOR_BORDER, (0, self.quickbar_y), (SCREEN_WIDTH, self.quickbar_y), 1)

        # Render visible terminal lines
        with self.lock:
            visible_lines = self.lines[-(self.rows + self.scroll_offset): len(self.lines) - self.scroll_offset] if self.scroll_offset > 0 else self.lines[-self.rows:]
        
        y = self.term_y + 4
        for line in visible_lines:
            # Wrap or truncate to screen width
            truncated = line[:self.cols]
            text_surf = self.font.render(truncated, True, COLOR_TERMINAL_FG)
            surface.blit(text_surf, (6, y))
            y += self.char_h

        # Draw quickbar
        self.quickbar.draw(surface)
