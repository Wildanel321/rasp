#!/usr/bin/env python3
"""
CyberDeck OS - Local Port & Service Inspector
"""

import sys
import socket

COMMON_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    1883: "MQTT",
    3000: "Dev Web",
    5000: "Flask API",
    8080: "HTTP Proxy/Alt",
    8888: "Jupyter/App"
}

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    print(f"[*] Checking common listening ports on {target}...")
    
    open_count = 0
    for port, name in COMMON_SERVICES.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        if s.connect_ex((target, port)) == 0:
            print(f"[+] Port {port:<5} is OPEN  ({name})")
            open_count += 1
        s.close()
        
    print(f"[*] Done. {open_count} open service(s) identified.")

if __name__ == "__main__":
    main()
