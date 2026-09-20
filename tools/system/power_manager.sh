#!/usr/bin/env bash
# ==============================================================================
# CyberDeck OS - CPU Governor & Power Profile Manager
# ==============================================================================

set -euo pipefail

GOVERNOR="${1:-status}"

case "$GOVERNOR" in
    status)
        echo "=== CPU Scaling Status ==="
        if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
            echo "Current Governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
            echo "Current Frequency: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq) kHz"
        else
            echo "cpufreq sysfs not available."
        fi
        ;;
    powersave|ondemand|performance)
        echo "Setting CPU Governor to: $GOVERNOR"
        for cpu_gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            if [ -f "$cpu_gov" ]; then
                echo "$GOVERNOR" | sudo tee "$cpu_gov" > /dev/null
            fi
        done
        echo "CPU Governor set successfully."
        ;;
    *)
        echo "Usage: $0 [status | powersave | ondemand | performance]"
        exit 1
        ;;
esac
