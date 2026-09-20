#!/usr/bin/env python3
"""
CyberDeck OS - NetworkManager Wi-Fi Engine
CLI & Library for Wi-Fi scanning, profile management, and hotspot connection
"""

import os
import re
import sys
import json
import shutil
import subprocess

class WiFiManager:
    @staticmethod
    def is_nmcli_available():
        return shutil.which("nmcli") is not None

    @staticmethod
    def scan_networks():
        """Scans for visible Wi-Fi networks (including smartphone hotspots) using nmcli."""
        if not WiFiManager.is_nmcli_available():
            # Simulation fallback for development host
            return [
                {"ssid": "Pixel_Hotspot_5G", "signal": 95, "security": "WPA2", "active": True},
                {"ssid": "Lab_CyberDeck_Net", "signal": 78, "security": "WPA2", "active": False},
                {"ssid": "Field_AP_Open", "signal": 45, "security": "NONE", "active": False},
            ]

        networks = []
        try:
            cmd = ["nmcli", "--terse", "--fields", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list", "--rescan", "yes"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
            if res.returncode == 0:
                seen_ssids = set()
                for line in res.stdout.splitlines():
                    parts = line.split(":")
                    if len(parts) >= 4:
                        in_use = (parts[0] == "*")
                        ssid = parts[1].strip()
                        # Unescape nmcli colon escapes
                        ssid = ssid.replace(r"\:", ":")
                        if not ssid or ssid in seen_ssids:
                            continue
                        seen_ssids.add(ssid)
                        try:
                            signal = int(parts[2])
                        except ValueError:
                            signal = 50
                        sec = parts[3].strip() or "OPEN"
                        networks.append({
                            "ssid": ssid,
                            "signal": signal,
                            "security": sec,
                            "active": in_use
                        })
        except Exception:
            pass
        return networks

    @staticmethod
    def get_saved_profiles():
        """Returns list of saved Wi-Fi connection profiles."""
        if not WiFiManager.is_nmcli_available():
            return ["Pixel_Hotspot_5G", "Lab_CyberDeck_Net"]

        saved = []
        try:
            cmd = ["nmcli", "--terse", "--fields", "NAME,TYPE", "connection", "show"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=4)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    parts = line.split(":")
                    if len(parts) >= 2 and "wireless" in parts[1]:
                        name = parts[0].replace(r"\:", ":")
                        saved.append(name)
        except Exception:
            pass
        return saved

    @staticmethod
    def connect(ssid, password=None):
        """Connects to a new Wi-Fi network or smartphone hotspot."""
        if not WiFiManager.is_nmcli_available():
            return True, f"Simulated connection to {ssid}"

        try:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
            if password:
                cmd.extend(["password", password])
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
            if res.returncode == 0:
                return True, f"Connected to {ssid}"
            return False, res.stderr.strip() or res.stdout.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def connect_saved(ssid):
        """Activates a previously saved network profile."""
        if not WiFiManager.is_nmcli_available():
            return True, f"Simulated switch to {ssid}"

        try:
            cmd = ["nmcli", "connection", "up", "id", ssid]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            if res.returncode == 0:
                return True, f"Connected to {ssid}"
            return False, res.stderr.strip() or res.stdout.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_profile(ssid):
        """Deletes a saved Wi-Fi connection profile."""
        if not WiFiManager.is_nmcli_available():
            return True, f"Simulated deletion of {ssid}"

        try:
            cmd = ["nmcli", "connection", "delete", "id", ssid]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                return True, f"Profile '{ssid}' deleted."
            return False, res.stderr.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def disconnect():
        """Disconnects wlan0 interface."""
        if not WiFiManager.is_nmcli_available():
            return True, "Simulated disconnect"

        try:
            cmd = ["nmcli", "dev", "disconnect", "wlan0"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            return res.returncode == 0, res.stdout.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_current_info():
        """Returns currently active Wi-Fi connection information."""
        info = {"ssid": "DISCONNECTED", "ip": "127.0.0.1", "signal": 0, "status": "DISCONNECTED"}
        if not WiFiManager.is_nmcli_available():
            return {"ssid": "Pixel_Hotspot_5G", "ip": "192.168.43.120", "signal": 95, "status": "CONNECTED"}

        try:
            # Check active SSID via nmcli
            cmd = ["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL", "dev", "wifi"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if line.startswith("yes:"):
                        parts = line.split(":")
                        if len(parts) >= 3:
                            info["ssid"] = parts[1].replace(r"\:", ":")
                            info["signal"] = int(parts[2]) if parts[2].isdigit() else 80
                            info["status"] = "CONNECTED"
                            break
        except Exception:
            pass
        return info


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 wifi_manager.py scan")
        print("  python3 wifi_manager.py saved")
        print("  python3 wifi_manager.py connect <SSID> [PASSWORD]")
        print("  python3 wifi_manager.py delete <SSID>")
        print("  python3 wifi_manager.py disconnect")
        print("  python3 wifi_manager.py status")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "scan":
        nets = WiFiManager.scan_networks()
        print(json.dumps(nets, indent=2))
    elif cmd == "saved":
        saved = WiFiManager.get_saved_profiles()
        print(json.dumps(saved, indent=2))
    elif cmd == "connect":
        if len(sys.argv) < 3:
            print("Error: SSID required")
            sys.exit(1)
        ssid = sys.argv[2]
        pwd = sys.argv[3] if len(sys.argv) > 3 else None
        ok, msg = WiFiManager.connect(ssid, pwd)
        print(f"[{'+' if ok else '-'}] {msg}")
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Error: SSID required")
            sys.exit(1)
        ok, msg = WiFiManager.delete_profile(sys.argv[2])
        print(f"[{'+' if ok else '-'}] {msg}")
    elif cmd == "disconnect":
        ok, msg = WiFiManager.disconnect()
        print(f"[{'+' if ok else '-'}] {msg}")
    elif cmd == "status":
        info = WiFiManager.get_current_info()
        print(json.dumps(info, indent=2))

if __name__ == "__main__":
    main()
