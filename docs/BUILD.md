# CyberDeck OS — Build Guide (pi-gen)

This guide explains how to build the custom **CyberDeck OS** image for Raspberry Pi 3 using the automated `pi-gen` pipeline.

---

## 1. Prerequisites & Build Environments

Building Raspberry Pi OS images requires root permissions for creating loopback devices and running `debootstrap`/`qemu-arm-static`.

You can build using either:
- **Docker Mode (Recommended)**: Runs anywhere Docker is available (Linux, macOS, Windows WSL2).
- **Native Linux Mode**: Runs on a Debian / Ubuntu host with `sudo`.

### Host Tool Requirements (Native Build)
```bash
sudo apt-get update
sudo apt-get install -y git coreutils quilt parted dosfstools qemu-user-static \
    debootstrap zerofree zip libarchive-tools pkg-config libcap2-bin \
    rscds xz-utils libarchive-zip-perl binfmt-support
```

---

## 2. Configuration (`config.env`)

Before initiating the build, you can inspect or modify `config.env`:

```bash
# Image Metadata
IMG_NAME="CyberDeckOS"
RELEASE_VERSION="v0.1.0"

# Target Architecture
TARGET_ARCH="armhf"         # 32-bit recommended for 1GB RAM RPi3
BASE_DISTRO="bookworm"

# User Credentials
TARGET_HOSTNAME="cyberdeck"
FIRST_USER_NAME="deck"
FIRST_USER_PASS="cyberdeck" # Change this before deployment!

# Hardware Overlays
ENABLE_SSH=1
ENABLE_SPI=1
ENABLE_I2C=1
ENABLE_UART=1
```

---

## 3. Running the Build

### Option A: Build via Docker (Recommended)
```bash
./build.sh --docker
```

### Option B: Build Natively on Linux
```bash
sudo ./build.sh
```

### Build Options
| Flag | Description |
|---|---|
| `--docker`, `-d` | Use containerized pi-gen builder. |
| `--clean`, `-c` | Remove previous work cache before building. |
| `--dry-run` | Validate configs and stage structure without compiling. |
| `--help`, `-h` | Display usage options. |

---

## 4. Build Output & Flashing

Once the build finishes successfully:
1. The image is located in `deploy/`:
   - `deploy/image_CyberDeckOS-v0.1.0.img.xz`
   - `deploy/image_CyberDeckOS-v0.1.0.img.xz.sha256`
2. Flash to a microSD card (32GB+ Recommended):
   - **Using Raspberry Pi Imager**: Choose OS -> "Use custom" -> select `.img.xz` file -> Select SD card -> Write.
   - **Using `dd` on Linux/macOS**:
     ```bash
     xz -dc deploy/image_CyberDeckOS-v0.1.0.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
     ```

---

## 5. Troubleshooting Builds

- **Disk Space Error**: Building requires at least **15 GB** of free disk space for chroot debootstrap stages.
- **Docker Permission Issues**: Ensure your current user is in the `docker` group (`sudo usermod -aG docker $USER`).
- **Stage Cache Invalidation**: If you modify `stage-cyberdeck`, run with `--clean` to ensure old cached stages are re-executed.
