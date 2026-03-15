#!/usr/bin/env bash
# setup.sh — One-command local setup for the Medical Translation project.
# Run this once before starting the servers for the first time.

set -euo pipefail

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

echo ""
echo "=================================================="
echo "  Medical Radiology Translation — Project Setup"
echo "=================================================="
echo ""

# ---------------------------------------------------------------------------
# 1. Check Ollama
# ---------------------------------------------------------------------------
info "Checking for Ollama..."

if ! command -v ollama &>/dev/null; then
    error "Ollama is not installed or not on your PATH."
    echo ""
    echo "  Please install Ollama before continuing:"
    echo ""
    echo "    macOS / Linux:"
    echo "      curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "    Windows:"
    echo "      Download the installer from https://ollama.com/download"
    echo ""
    echo "  After installation, re-run this script."
    exit 1
fi

success "Ollama found: $(ollama --version 2>/dev/null || echo 'version unknown')"

# ---------------------------------------------------------------------------
# 2. Pull primary model
# ---------------------------------------------------------------------------
info "Pulling primary model: qwen2.5:14b  (this may take several minutes on first run)..."
if ollama pull qwen2.5:14b; then
    success "qwen2.5:14b pulled successfully."
else
    warn "Failed to pull qwen2.5:14b. The fallback model will be used instead."
fi

# ---------------------------------------------------------------------------
# 3. Pull fallback model
# ---------------------------------------------------------------------------
info "Pulling fallback model: llama3.1:8b..."
if ollama pull llama3.1:8b; then
    success "llama3.1:8b pulled successfully."
else
    warn "Failed to pull llama3.1:8b. Make sure Ollama can reach the internet."
fi

# ---------------------------------------------------------------------------
# 4. Python dependencies
# ---------------------------------------------------------------------------
info "Installing Python dependencies from backend/requirements.txt..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "${SCRIPT_DIR}/backend/requirements.txt" ]; then
    error "backend/requirements.txt not found. Are you running this from the project root?"
    exit 1
fi

pip install -r "${SCRIPT_DIR}/backend/requirements.txt"
success "Python dependencies installed."

# ---------------------------------------------------------------------------
# 5. Node.js dependencies
# ---------------------------------------------------------------------------
info "Installing Node.js dependencies in frontend/..."

if [ ! -d "${SCRIPT_DIR}/frontend" ]; then
    error "frontend/ directory not found. Are you running this from the project root?"
    exit 1
fi

(cd "${SCRIPT_DIR}/frontend" && npm install)
success "Node.js dependencies installed."

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "=================================================="
success "Setup complete!"
echo ""
echo "  Run the following command to start all services:"
echo ""
echo -e "    ${CYAN}./start.sh${NC}"
echo ""
echo "  Or with Docker Compose:"
echo ""
echo -e "    ${CYAN}docker compose up --build${NC}"
echo "=================================================="
echo ""
