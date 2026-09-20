"""
CyberDeck ESP32 Companion Serial Client
Handles JSON-based serial communication with ESP32 microcontroller
"""

import os
import glob
import json
import time
import threading

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

class ESP32Client:
    def __init__(self, port=None, baudrate=115200, timeout=1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.connected = False
        self.last_error = ""
        self.lock = threading.Lock()
        
        # Simulated responses for dev environments
        self.simulated_gpio = {2: False, 4: False, 5: False, 18: False}

    def auto_connect(self):
        """Scans for ESP32 serial ports and attempts connection."""
        if not HAS_SERIAL:
            self.connected = True
            return True, "Simulated ESP32 (pyserial not found)"

        candidate_ports = []
        if os.path.exists("/dev/cyberdeck-esp32"):
            candidate_ports.append("/dev/cyberdeck-esp32")
        candidate_ports.extend(glob.glob("/dev/ttyUSB*"))
        candidate_ports.extend(glob.glob("/dev/ttyACM*"))

        if not candidate_ports:
            self.connected = False
            self.last_error = "No serial device found"
            return False, self.last_error

        for port in candidate_ports:
            try:
                self.serial_conn = serial.Serial(port, self.baudrate, timeout=self.timeout)
                time.sleep(1.0) # Wait for DTR reset
                self.port = port
                self.connected = True
                return True, f"Connected to {port}"
            except Exception as e:
                self.last_error = str(e)

        self.connected = False
        return False, f"Connection failed: {self.last_error}"

    def send_command(self, cmd_dict):
        """Sends a JSON command to the ESP32 and waits for JSON response."""
        with self.lock:
            if not self.connected or not self.serial_conn:
                return self._simulate_response(cmd_dict)

            try:
                # Flush existing buffers
                self.serial_conn.reset_input_buffer()
                msg = json.dumps(cmd_dict) + "\n"
                self.serial_conn.write(msg.encode("utf-8"))
                
                # Read response line
                line = self.serial_conn.readline().decode("utf-8").strip()
                if line:
                    return json.loads(line)
                return {"success": False, "error": "Timeout waiting for ESP32"}
            except Exception as e:
                self.connected = False
                self.last_error = str(e)
                return {"success": False, "error": str(e)}

    def ping(self):
        return self.send_command({"command": "ping"})

    def set_gpio(self, pin: int, state: bool):
        return self.send_command({"command": "gpio", "pin": pin, "state": state})

    def read_analog(self, pin: int = 34):
        return self.send_command({"command": "read_analog", "pin": pin})

    def get_telemetry(self):
        return self.send_command({"command": "telemetry"})

    def _simulate_response(self, cmd_dict):
        cmd = cmd_dict.get("command")
        if cmd == "ping":
            return {"success": True, "pong": True, "device": "ESP32-Companion-SIM", "firmware": "v0.1.0"}
        elif cmd == "gpio":
            pin = cmd_dict.get("pin", 2)
            state = bool(cmd_dict.get("state", False))
            self.simulated_gpio[pin] = state
            return {"success": True, "pin": pin, "state": state}
        elif cmd == "read_analog":
            return {"success": True, "pin": cmd_dict.get("pin", 34), "voltage": 3.30, "raw": 4095}
        elif cmd == "telemetry":
            return {"success": True, "battery_v": 4.12, "temp_c": 27.5, "uptime_s": 320}
        return {"success": False, "error": f"Unknown simulated command: {cmd}"}

    def close(self):
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.connected = False
