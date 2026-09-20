#!/usr/bin/env python3
"""
CyberDeck OS - ESP32 Companion Daemon & Bridge
Runs in background to maintain serial connection and telemetry logging
"""

import os
import sys
import time
import json
import logging
import argparse

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ui.services.esp32_client import ESP32Client

LOG_FILE = "/var/log/cyberdeck/esp32.log"

def setup_logging():
    log_dir = os.path.dirname(LOG_FILE)
    if os.path.exists(log_dir) and os.access(log_dir, os.W_OK):
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="ESP32 Companion Bridge Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous background daemon mode")
    parser.add_argument("--send", type=str, help="Send raw JSON command to ESP32")
    args = parser.parse_args()

    setup_logging()
    logging.info("Starting ESP32 Companion Bridge...")

    client = ESP32Client()
    connected, msg = client.auto_connect()
    logging.info(f"ESP32 auto_connect status: {msg}")

    if args.send:
        try:
            cmd = json.loads(args.send)
            res = client.send_command(cmd)
            print(json.dumps(res, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        return

    if args.daemon:
        logging.info("Entering telemetry polling daemon loop...")
        while True:
            if not client.connected:
                client.auto_connect()
            else:
                telemetry = client.get_telemetry()
                logging.info(f"Telemetry: {telemetry}")
            time.sleep(10)

if __name__ == "__main__":
    main()
