#!/bin/bash

# This file is part of the Racing-Companion project.

# Description: Support lint script for development using Ruff - https://github.com/astral-sh/ruff?tab=readme-ov-file

# Variables for colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RCFUNC_DIR=$(realpath "$SCRIPT_DIR/../../rcfunc")
RCTABS_DIR=$(realpath "$SCRIPT_DIR/../../rctabs")
RCTEST_DIR=$(realpath "$SCRIPT_DIR/../../tests")


log_info() {
    { echo -e "${BLUE}[$(date +%H:%M:%S)] [INFO] - ${NC} $1"; }
}
log_error() {
    { echo -e "${RED}[$(date +%H:%M:%S)] [ERROR] - ${NC} $1"; }
}
log_success() {
      { echo -e "${GREEN}[$(date +%H:%M:%S)] [SUCCESS] - ${NC} $1"; }
   }

log_warning() {
    { echo -e "${YELLOW}[$(date +%H:%M:%S)] [WARNING] - ${NC} $1"; }
}

# Print usage information with nice frame formatting
usage() {
      echo " "
      echo -e "Usage: lint_prj.sh [options]"
      echo -e "Options:"
      echo -e "  --help, -h\t\tShow this help message"
      echo -e "Description:"
      echo -e "  This script lints the Racing Companion project using Ruff."
      echo -e "  It checks the rcfunc, rctabs, and tests directories for linting issues."
      echo " "
}

# Execution entry point
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
   usage
   exit 0
fi

# Check if Ruff is installed
if ! command -v ruff &> /dev/null; then
    log_error "Unable to find 'ruff' in your PATH"
    read -p "Do you want to install it using uv? [Y/n] " answer
    answer=${answer:-Y}
    if [[ "$answer" =~ ^[Yy]$ ]]; then
       log_info "Installing ruff..."
       if command -v uv &> /dev/null; then
          log_info "uv is already installed. Proceeding with ruff installation..."
       else
          log_info "uv is not installed. Installing uv first..."
          if curl -LsSf https://astral.sh/uv/install.sh | sh; then
             log_success "uv installed successfully."
          else
             log_error "Failed to install uv. Unable to continue. Install uv manually and try again. Exiting..."
             exit 1
          fi
       fi

       uv tool install ruff@latest &> /dev/null
       # Check if Ruff was installed successfully
       if command -v ruff &> /dev/null; then
          log_success "ruff installed successfully."
       else
          log_error "ruff installation failed. Unable to continue. Install ruff manually and try again. Exiting..."
          exit 1
       fi
       log_success "ruff (uv) installation script completed successfully."
    else
       log_warning "Unable to continue without Ruff installed. Exiting..."
       exit 1
    fi
    exit 1
fi

# lint the project files
echo " "
log_info "Linting functionality in $RCFUNC_DIR"
ruff check "$RCFUNC_DIR" --preview

echo " "
log_info "Linting GUI tabs in $RCTABS_DIR"
ruff check "$RCTABS_DIR" --preview

echo " "
log_info "Linting tests in $RCTEST_DIR"
ruff check "$RCTEST_DIR" --preview

log_success "Linting completed successfully. Some options may be solved automatically by running manually with 'ruff check --fix' in the respective directories."
exit 0
