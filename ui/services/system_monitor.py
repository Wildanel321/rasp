"""
CyberDeck System Monitor Service
Collects real-time CPU, RAM, Disk, Thermal, and Uptime metrics with minimal CPU impact
"""

import os
import time
import socket
import threading

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class SystemMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False
        self._thread = None
        
        # Current telemetry snapshot
        self.cpu_percent = 0.0
        self.ram_percent = 0.0
        self.ram_used_mb = 0
        self.ram_total_mb = 1024
        self.disk_percent = 0.0
        self.disk_free_gb = 0.0
        self.cpu_temp = 0.0
        self.uptime_str = "00:00:00"
        self.hostname = socket.gethostname()
        self.ip_address = "127.0.0.1"
        self.wifi_status = "DISCONNECTED"
        self.load_avg = (0.0, 0.0, 0.0)

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _update_loop(self):
        while self.running:
            try:
                self._collect_metrics()
            except Exception:
                pass
            time.sleep(self.interval)

    def _collect_metrics(self):
        # 1. CPU and RAM
        if HAS_PSUTIL:
            self.cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            self.ram_percent = mem.percent
            self.ram_used_mb = int(mem.used / (1024 * 1024))
            self.ram_total_mb = int(mem.total / (1024 * 1024))
            
            disk = psutil.disk_usage('/')
            self.disk_percent = disk.percent
            self.disk_free_gb = round(disk.free / (1024 ** 3), 1)
        else:
            # Fallback for minimal systems without psutil
            self.cpu_percent = 15.0
            self.ram_percent = 35.0
            self.ram_used_mb = 350
            self.ram_total_mb = 950
            self.disk_percent = 20.0
            self.disk_free_gb = 24.5

        # 2. CPU Temperature (RPi thermal sysfs)
        self.cpu_temp = self._read_cpu_temp()

        # 3. Uptime
        self.uptime_str = self._read_uptime()

        # 4. Primary IP address
        self.ip_address = self._read_primary_ip()

        # 5. Wi-Fi status
        self.wifi_status = self._check_wifi_status()

        # 6. Load Average
        try:
            self.load_avg = os.getloadavg()
        except (AttributeError, OSError):
            self.load_avg = (0.1, 0.1, 0.1)

    def _read_cpu_temp(self):
        thermal_path = "/sys/class/thermal/thermal_zone0/temp"
        if os.path.exists(thermal_path):
            try:
                with open(thermal_path, "r") as f:
                    return float(f.read().strip()) / 1000.0
            except Exception:
                pass
        return 42.0  # Default simulation value if running on dev host

    def _read_uptime(self):
        uptime_path = "/proc/uptime"
        if os.path.exists(uptime_path):
            try:
                with open(uptime_path, "r") as f:
                    seconds = float(f.read().split()[0])
                    hours, rem = divmod(int(seconds), 3600)
                    minutes, seconds = divmod(rem, 60)
                    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except Exception:
                pass
        return "01:23:45"

    def _read_primary_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.2)
            # Connect to public DNS address without sending packet
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _check_wifi_status(self):
        # Check /sys/class/net/wlan0/operstate if on Linux
        wlan_state = "/sys/class/net/wlan0/operstate"
        if os.path.exists(wlan_state):
            try:
                with open(wlan_state, "r") as f:
                    state = f.read().strip().upper()
                    return "CONNECTED" if state == "UP" else "DOWN"
            except Exception:
                pass
        return "CONNECTED" if self.ip_address not in ("127.0.0.1", "") else "DISCONNECTED"
