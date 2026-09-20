#!/usr/bin/env python3
"""
CyberDeck OS - System Information CLI Tool
"""

import os
import sys
import platform
import subprocess
import json

def get_cpu_info():
    info = {"model": platform.processor() or "ARMv7 Processor", "cores": os.cpu_count() or 4}
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "Hardware" in line:
                    info["hardware"] = line.split(":")[1].strip()
                elif "Revision" in line:
                    info["revision"] = line.split(":")[1].strip()
    except Exception:
        pass
    return info

def get_throttled_state():
    try:
        out = subprocess.check_output(["vcgencmd", "get_throttled"], text=True)
        return out.strip()
    except Exception:
        return "throttled=0x0 (normal)"

def main():
    data = {
        "hostname": platform.node(),
        "os": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "python": sys.version.split()[0],
        "cpu": get_cpu_info(),
        "throttled": get_throttled_state()
    }
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
