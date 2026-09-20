#!/usr/bin/env bash
# ==============================================================================
# CYBERDECK OS - Image Builder Script (pi-gen wrapper)
# Targets: Raspberry Pi 3 / 3B / 3B+
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_ENV="${SCRIPT_DIR}/config.env"
PIGEN_DIR="${SCRIPT_DIR}/pi-gen"
DEPLOY_DIR="${SCRIPT_DIR}/deploy"
STAGE_CUSTOM_SRC="${SCRIPT_DIR}/stages/stage-cyberdeck"

# Text styling
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

log_info() { echo -e "${CYAN}[INFO]${NC} $*"; }
log_ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }

print_banner() {
    echo -e "${BOLD}${CYAN}"
    echo "================================================================"
    echo "         CYBERDECK OS - RASPBERRY PI 3 IMAGE BUILDER           "
    echo "================================================================"
    echo -e "${NC}"
}

print_banner

# Load configuration
if [[ -f "${CONFIG_ENV}" ]]; then
    log_info "Loading configuration from ${CONFIG_ENV}"
    # shellcheck disable=SC1090
    source "${CONFIG_ENV}"
else
    log_err "Configuration file ${CONFIG_ENV} not found!"
    exit 1
fi

# Parse CLI arguments
USE_DOCKER=0
CLEAN_FIRST=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --docker|-d)
            USE_DOCKER=1
            shift
            ;;
        --clean|-c)
            CLEAN_FIRST=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --help|-h)
            echo "Usage: ./build.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker, -d     Build inside official pi-gen Docker container (Recommended on non-Debian / macOS / Windows WSL2)"
            echo "  --clean, -c      Clean previous work/ and deploy/ directories before building"
            echo "  --dry-run        Validate stages and environment without starting build"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            log_err "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Step 1: Pre-flight checks
log_info "Running pre-flight environment checks..."

# Check required host commands
if [[ ${USE_DOCKER} -eq 1 ]]; then
    if ! command -v docker >/dev/null 2>&1; then
        log_err "Docker is required for --docker mode but 'docker' was not found in PATH."
        exit 1
    fi
    log_ok "Docker is available."
else
    # Native Linux requirements check
    if [[ "$(uname)" != "Linux" ]]; then
        log_warn "Host OS is not native Linux. Auto-switching to --docker mode for compatibility."
        USE_DOCKER=1
    elif [[ $EUID -ne 0 ]]; then
        log_warn "Native pi-gen build requires root privileges. Please consider using --docker or rerun with sudo."
    fi

    REQUIRED_BINS=(git coreutils sed awk xz)
    for bin in "${REQUIRED_BINS[@]}"; do
        if ! command -v "$bin" >/dev/null 2>&1; then
            log_err "Missing required build tool: $bin. Install it via your package manager."
            exit 1
        fi
    done
fi

# Step 2: Ensure pi-gen repository is present
if [[ ! -d "${PIGEN_DIR}/.git" ]]; then
    log_info "Cloning official pi-gen repository..."
    git clone --depth 1 https://github.com/RPi-Distro/pi-gen.git "${PIGEN_DIR}"
    log_ok "pi-gen cloned successfully."
else
    log_info "Found existing pi-gen directory at ${PIGEN_DIR}."
fi

# Step 3: Handle clean if requested
if [[ ${CLEAN_FIRST} -eq 1 ]]; then
    log_info "Cleaning previous build work directories..."
    rm -rf "${PIGEN_DIR}/work"
    rm -rf "${DEPLOY_DIR}"
    log_ok "Clean completed."
fi

mkdir -p "${DEPLOY_DIR}"

# Step 4: Inject custom CyberDeck stage and configuration
log_info "Injecting custom CyberDeck stage into pi-gen..."

# Create stage-cyberdeck in pi-gen
TARGET_STAGE_DIR="${PIGEN_DIR}/stage-cyberdeck"
rm -rf "${TARGET_STAGE_DIR}"
mkdir -p "${TARGET_STAGE_DIR}"

if [[ -d "${STAGE_CUSTOM_SRC}" ]]; then
    cp -r "${STAGE_CUSTOM_SRC}/"* "${TARGET_STAGE_DIR}/"
    log_ok "Custom stage copied from ${STAGE_CUSTOM_SRC}"
else
    log_err "Source stage directory ${STAGE_CUSTOM_SRC} not found!"
    exit 1
fi

# Copy CyberDeck UI, Tools, Hardware, and Services into stage payload
PAYLOAD_DIR="${TARGET_STAGE_DIR}/02-cyberdeck-ui/payload"
mkdir -p "${PAYLOAD_DIR}"
cp -r "${SCRIPT_DIR}/ui" "${PAYLOAD_DIR}/"
cp -r "${SCRIPT_DIR}/tools" "${PAYLOAD_DIR}/"
cp -r "${SCRIPT_DIR}/services" "${PAYLOAD_DIR}/"
cp -r "${SCRIPT_DIR}/hardware" "${PAYLOAD_DIR}/"

# Write pi-gen build configuration file
PIGEN_CONFIG_FILE="${PIGEN_DIR}/config"
log_info "Generating pi-gen config at ${PIGEN_CONFIG_FILE}..."

cat > "${PIGEN_CONFIG_FILE}" <<EOF
IMG_NAME="${IMG_NAME}"
RELEASE="${BASE_DISTRO}"
DEPLOY_DIR="${DEPLOY_DIR}"
TARGET_ARCH="${TARGET_ARCH}"
LOCALE_DEFAULT="${LOCALE_DEFAULT}"
TIMEZONE_DEFAULT="${TIMEZONE_DEFAULT}"
KEYBOARD_KEYMAP="${KEYBOARD_KEYMAP}"
KEYBOARD_LAYOUT="${KEYBOARD_LAYOUT}"
FIRST_USER_NAME="${FIRST_USER_NAME}"
FIRST_USER_PASS="${FIRST_USER_PASS}"
ENABLE_SSH="${ENABLE_SSH}"
DISABLE_FIRST_BOOT_USER_RENAME=1
STAGE_LIST="stage0 stage1 stage2 stage-cyberdeck"
EOF

# Skip desktop stages (stage3, stage4, stage5) to keep it minimal and lightweight
touch "${PIGEN_DIR}/stage3/SKIP" || true
touch "${PIGEN_DIR}/stage4/SKIP" || true
touch "${PIGEN_DIR}/stage5/SKIP" || true
touch "${PIGEN_DIR}/stage4/SKIP_IMAGE" || true
touch "${PIGEN_DIR}/stage5/SKIP_IMAGE" || true

# Ensure stage-cyberdeck will export an image
rm -f "${TARGET_STAGE_DIR}/SKIP_IMAGE" || true
touch "${TARGET_STAGE_DIR}/EXPORT_IMAGE" || true

log_ok "pi-gen configuration prepared."

if [[ ${DRY_RUN} -eq 1 ]]; then
    log_ok "Dry run completed successfully. Stages and configs validated."
    exit 0
fi

# Step 5: Execute build
log_info "Starting image build process (This can take 15-45 minutes depending on CPU/Network)..."

BUILD_START_TIME=$(date +%s)

if [[ ${USE_DOCKER} -eq 1 ]]; then
    log_info "Running pi-gen inside Docker container..."
    cd "${PIGEN_DIR}"
    ./build-docker.sh
else
    log_info "Running native pi-gen build..."
    cd "${PIGEN_DIR}"
    sudo ./build.sh
fi

BUILD_END_TIME=$(date +%s)
DURATION=$((BUILD_END_TIME - BUILD_START_TIME))

# Step 6: Post-build verification & checksum generation
log_info "Build finished in $((DURATION / 60))m $((DURATION % 60))s."
log_info "Scanning for output image in ${DEPLOY_DIR}..."

# Find the latest generated image or compressed image
OUTPUT_IMG=$(find "${DEPLOY_DIR}" -maxdepth 1 -type f \( -name "*.img.xz" -o -name "*.img" -o -name "*.zip" \) -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -f2- -d" ")

if [[ -n "${OUTPUT_IMG}" && -f "${OUTPUT_IMG}" ]]; then
    IMAGE_BASENAME="$(basename "${OUTPUT_IMG}")"
    RELEASE_IMG_NAME="${IMG_NAME}-${RELEASE_VERSION}.img.xz"
    
    log_ok "Generated image: ${OUTPUT_IMG}"
    
    # Generate SHA-256 Checksum
    log_info "Generating SHA256 checksum..."
    cd "${DEPLOY_DIR}"
    sha256sum "$(basename "${OUTPUT_IMG}")" > "${IMAGE_BASENAME}.sha256"
    log_ok "Checksum written to ${DEPLOY_DIR}/${IMAGE_BASENAME}.sha256"
    
    echo -e "${BOLD}${GREEN}"
    echo "================================================================"
    echo "             CYBERDECK OS BUILD SUCCESSFUL!                     "
    echo "================================================================"
    echo -e "${NC}"
    echo "Target Device : Raspberry Pi 3 / 3B / 3B+"
    echo "Output Image  : ${OUTPUT_IMG}"
    echo "Checksum File : ${DEPLOY_DIR}/${IMAGE_BASENAME}.sha256"
    echo ""
    echo "To flash to microSD card:"
    echo "  1. Use Raspberry Pi Imager or BalenaEtcher"
    echo "  2. Or use dd: sudo dd if=\"${OUTPUT_IMG}\" of=/dev/sdX bs=4M status=progress conv=fsync"
    echo ""
else
    log_err "Build did not produce an image file in ${DEPLOY_DIR}."
    log_err "Check the logs in ${PIGEN_DIR}/work/ for details."
    exit 1
fi
