#!/usr/bin/env python3
"""
CyberDeck OS - GPIO Control CLI Utility
"""

import sys
import subprocess
import os

def set_pin(pin: int, val: int):
    # Try gpioset (libgpiod) first
    try:
        subprocess.run(["gpioset", "0", f"{pin}={val}"], check=True)
        print(f"[+] GPIO {pin} set to {val} via gpioset.")
        return
    except Exception:
        pass

    # Fallback to sysfs gpio
    gpio_dir = f"/sys/class/gpio/gpio{pin}"
    if not os.path.exists(gpio_dir):
        try:
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(pin))
        except Exception as e:
            print(f"[-] Failed to export GPIO {pin}: {e}")
            return
    try:
        with open(f"{gpio_dir}/direction", "w") as f:
            f.write("out")
        with open(f"{gpio_dir}/value", "w") as f:
            f.write(str(val))
        print(f"[+] GPIO {pin} set to {val} via sysfs.")
    except Exception as e:
        print(f"[-] Error writing GPIO {pin}: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 gpio_control.py <pin_number> <0|1>")
        sys.exit(1)
    pin = int(sys.argv[1])
    val = int(sys.argv[2])
    set_pin(pin, val)

if __name__ == "__main__":
    main()
