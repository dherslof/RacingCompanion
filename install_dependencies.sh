#!/bin/env bash
#
# File name: install_dependencies.sh
# Author: dherslof
# Licence: MIT
# Description: This simple script installs the dependencies required for running
#              the racing-companion app.

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Dependencies
APT_PACKAGES="python3-tk"
PIP_PACKAGES="numpy customtkinter matplotlib pytest"

log() {
    local message="$1"
    local level="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[$level]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[$level]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[$level]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[$level]${NC} $message"
            ;;
        *)
            echo -e "[$level] $message"
            ;;
    esac
}

command_exists() {
    command -v "$1" &> /dev/null
}

apt_package_installed() {
    dpkg -l "$1" 2>/dev/null | grep -q "^ii"
}

pip_package_installed() {
    pip3 show "$1" &>/dev/null
}

handle_error() {
    local exit_code=$1
    local error_message=$2
    
    if [ $exit_code -ne 0 ]; then
        log "$error_message (Exit code: $exit_code)" "ERROR"
        log "Installation failed" "ERROR"
        exit $exit_code
    fi
}

# Print header
log "Starting dependency installation" "INFO"
log "APT packages to install: $APT_PACKAGES" "INFO"
log "PIP packages to install: $PIP_PACKAGES" "INFO"
echo

# Check if running as root for apt installations
if [ "$(id -u)" -ne 0 ]; then
    log "Warning: Not running as root. Dependency installations may fail. Consider running with sudo." "WARNING"
fi

# Check if apt is available
if ! command_exists apt; then
    log "APT package manager not found. This script requires a Debian-based system." "ERROR"
    exit 1
fi

# Check if pip is available before attempting pip installations
if ! command_exists pip3; then
    log "Python pip not found. Will attempt to install it with apt." "ERROR"
    exit 1
fi

# Check which APT packages need to be installed
apt_to_install=()
for package in $APT_PACKAGES; do
    if apt_package_installed "$package"; then
        log "$package is already installed" "INFO"
    else
        apt_to_install+=("$package")
    fi
done

# Update apt repository if there are packages to install
if [ ${#apt_to_install[@]} -gt 0 ]; then
    log "Updating APT repositories..." "INFO"
    apt_output=$(apt update 2>&1)
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log "Failed to update APT repositories" "ERROR"
        echo -e "${RED}Error output:${NC}\n$apt_output"
        exit $exit_code
    fi
    log "APT repositories updated successfully" "SUCCESS"
    
    # Install apt packages
    log "Installing APT packages: ${apt_to_install[*]}" "INFO"
    for package in "${apt_to_install[@]}"; do
        log "Installing $package..." "INFO"
        apt_output=$(apt install -y "$package" 2>&1)
        exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            log "Failed to install $package" "ERROR"
            echo -e "${RED}Error output:${NC}\n$apt_output"
            continue
        else
            log "$package installed successfully" "SUCCESS"
        fi
    done
else
    log "All APT packages are already installed" "SUCCESS"
fi

# Check which pip packages need to be installed
pip_to_install=()
for package in $PIP_PACKAGES; do
    if pip_package_installed "$package"; then
        log "$package is already installed" "INFO"
    else
        pip_to_install+=("$package")
    fi
done

# Install pip packages
if [ ${#pip_to_install[@]} -gt 0 ]; then
    log "Installing PIP packages: ${pip_to_install[*]}" "INFO"
    for package in "${pip_to_install[@]}"; do
        log "Installing $package..." "INFO"
        pip_output=$(pip3 install "$package" 2>&1)
        exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            log "Failed to install $package" "ERROR"
            echo -e "${RED}Error output:${NC}\n$pip_output"
            continue
        else
            log "$package installed successfully" "SUCCESS"
        fi
    done
else
    log "All PIP packages are already installed" "SUCCESS"
fi

# Final verification
log "Verifying installations..." "INFO"
missing_apt=()
missing_pip=()

# Check apt packages
for package in $APT_PACKAGES; do
    
    # For some packages we need to check differently
    if [[ "$package" == "python3" ]]; then
        if ! command_exists python3; then
            missing_apt+=("$package")
        fi
    elif [[ "$package" == "python3-tk" ]]; then
        # Check if tkinter can be imported in Python, since it's a Python package and not a command
        if ! python3 -c "import tkinter" &>/dev/null; then
            missing_apt+=("$package")
        fi
    else
        if ! command_exists "$package"; then
            missing_apt+=("$package")
        fi
    fi
done

# Check pip packages
for package in $PIP_PACKAGES; do
    if ! pip3 show "$package" &> /dev/null; then
        missing_pip+=("$package")
    fi
done

# Report verification results
if [ ${#missing_apt[@]} -eq 0 ] && [ ${#missing_pip[@]} -eq 0 ]; then
    log "All dependencies were installed successfully!" "SUCCESS"
    log "Package updates is not part of this installation script, and some might be needed in order for racing-companion to run properly."
else
    log "Some dependencies may not have been installed correctly:" "WARNING"
    
    if [ ${#missing_apt[@]} -gt 0 ]; then
        log "Missing APT packages: ${missing_apt[*]}" "WARNING"
    fi
    
    if [ ${#missing_pip[@]} -gt 0 ]; then
        log "Missing PIP packages: ${missing_pip[*]}" "WARNING"
    fi
    
    exit 1
fi

log "Installation completed successfully" "SUCCESS"
