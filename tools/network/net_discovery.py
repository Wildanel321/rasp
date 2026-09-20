#!/usr/bin/env python3
"""
CyberDeck OS - Subnet Discovery Tool (Authorized Lab / Local Diagnostic)
"""

import sys
import socket
import threading

def probe(ip, port=80, timeout=0.3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        if s.connect_ex((ip, port)) == 0:
            s.close()
            return True
        s.close()
    except Exception:
        pass
    return False

def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "192.168.1"
    print(f"[*] Scanning subnet {prefix}.0/24 (Hosts 1-60)...")
    
    active = []
    threads = []
    lock = threading.Lock()

    def scan_host(host_ip):
        for port in (80, 22, 53, 443):
            if probe(host_ip, port):
                with lock:
                    active.append((host_ip, port))
                print(f"[+] Active Host: {host_ip} (Port {port} open)")
                break

    for i in range(1, 61):
        target = f"{prefix}.{i}"
        t = threading.Thread(target=scan_host, args=(target,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=2.0)

    print(f"[*] Scan complete. Total active hosts found: {len(active)}")

if __name__ == "__main__":
    main()
