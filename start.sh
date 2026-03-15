#!/usr/bin/env bash
# start.sh — Start all services for the Medical Translation project locally.
# Press Ctrl+C to stop everything cleanly.

set -euo pipefail

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Keep track of background PIDs so we can kill them on exit.
PIDS=()

cleanup() {
    echo ""
    info "Shutting down all services..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait 2>/dev/null || true
    success "All services stopped. Goodbye!"
}

trap cleanup EXIT INT TERM

echo ""
echo "=================================================="
echo "  Medical Radiology Translation — Start Services"
echo "=================================================="
echo ""

# ---------------------------------------------------------------------------
# 1. Start Ollama if not already running
# ---------------------------------------------------------------------------
info "Checking Ollama status..."

if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    success "Ollama is already running."
else
    if ! command -v ollama &>/dev/null; then
        warn "Ollama not found. Skipping — make sure it is started separately."
    else
        info "Starting Ollama in the background..."
        ollama serve &>/dev/null &
        PIDS+=($!)
        # Give Ollama a moment to bind its port
        sleep 2
        if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
            success "Ollama started (PID ${PIDS[-1]})."
        else
            warn "Ollama may not have started yet — proceeding anyway."
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 2. Start backend
# ---------------------------------------------------------------------------
info "Starting FastAPI backend on port 8000..."

# Activate virtual environment
if [[ ! -f "${SCRIPT_DIR}/venv/bin/activate" ]]; then
    warn "Virtual environment not found. Run: python -m venv venv && pip install -r backend/requirements.txt"
    exit 1
fi

(
    cd "${SCRIPT_DIR}/backend"
    source "${SCRIPT_DIR}/venv/bin/activate"
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!
PIDS+=($BACKEND_PID)
success "Backend started (PID $BACKEND_PID)."

# ---------------------------------------------------------------------------
# 3. Start frontend
# ---------------------------------------------------------------------------
info "Starting Next.js frontend on port 3000..."

(
    cd "${SCRIPT_DIR}/frontend"
    npm run dev
) &
FRONTEND_PID=$!
PIDS+=($FRONTEND_PID)
success "Frontend started (PID $FRONTEND_PID)."

# ---------------------------------------------------------------------------
# 4. Print URLs
# ---------------------------------------------------------------------------
echo ""
echo "=================================================="
success "All services are running!"
echo ""
echo -e "  Backend  → ${CYAN}http://localhost:8000${NC}"
echo -e "  API Docs → ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  Frontend → ${CYAN}http://localhost:3000${NC}"
echo ""
echo "  Press Ctrl+C to stop all services."
echo "=================================================="
echo ""

# ---------------------------------------------------------------------------
# 5. Wait — cleanup trap fires on Ctrl+C
# ---------------------------------------------------------------------------
wait
