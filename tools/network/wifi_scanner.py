#!/usr/bin/env python3
"""
CyberDeck OS - Wi-Fi Access Point Scanner CLI
"""

import os
import re
import subprocess

def main():
    print("[*] Scanning wireless networks on interface wlan0...")
    try:
        res = subprocess.run(["sudo", "iwlist", "wlan0", "scan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=6)
        if res.returncode == 0:
            ssids = re.findall(r'ESSID:"([^"]+)"', res.stdout)
            signals = re.findall(r'Quality=([0-9/]+)', res.stdout)
            for idx, ssid in enumerate(ssids):
                sig = signals[idx] if idx < len(signals) else "N/A"
                print(f"[+] SSID: {ssid:<24} | Signal: {sig}")
        else:
            print(f"[-] Scan error: {res.stderr}")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    main()
