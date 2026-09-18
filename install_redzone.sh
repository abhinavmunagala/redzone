#!/bin/bash

# 🎯 RedZone Complete Installation Script
# Installs all dependencies, tools, and validates setup

set -e

REDZONE_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🎯 RedZone Installation Script"
echo "Home: $REDZONE_HOME"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Step 1: Check Python
log_step "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_success "Python found: $PYTHON_VERSION"
else
    log_error "Python3 not found. Please install Python 3.10+"
    exit 1
fi

# Step 2: Check/Create venv
log_step "Checking Python virtual environment..."
if [ ! -d "$REDZONE_HOME/.venv" ]; then
    log_warning "Virtual environment not found. Creating..."
    cd "$REDZONE_HOME"
    python3 -m venv .venv
    log_success "Virtual environment created"
else
    log_success "Virtual environment found"
fi

# Step 3: Activate venv and install Python deps
log_step "Installing Python dependencies..."
cd "$REDZONE_HOME"
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
log_success "Python dependencies installed"

# Step 4: Check for Amass
log_step "Checking Amass installation..."
if command -v amass &> /dev/null; then
    AMASS_VERSION=$(amass -version 2>&1 | head -1)
    log_success "Amass found: $AMASS_VERSION"
else
    log_warning "Amass not found"
    echo "To install Amass:"
    echo "  macOS: brew install amass"
    echo "  Linux: apt-get install amass"
    echo "  From source: go install -v github.com/owasp-amass/amass/v3/...@latest"
fi

# Step 5: Check for Sn1per
log_step "Checking Sn1per installation..."
if command -v sniper &> /dev/null; then
    log_success "Sn1per found"
else
    log_warning "Sn1per not found"
    echo "To install Sn1per:"
    echo "  cd /opt"
    echo "  sudo git clone https://github.com/1N3/Sn1per.git"
    echo "  cd Sn1per && sudo bash install.sh"
fi

# Step 6: Verify CLI tool
log_step "Verifying RedZone CLI..."
cd "$REDZONE_HOME"
if [ -x "redzone_recon" ]; then
    log_success "CLI tool found and executable"
else
    log_error "CLI tool not executable. Making it executable..."
    chmod +x redzone_recon
    log_success "CLI tool is now executable"
fi

# Step 7: Test basic functionality
log_step "Testing basic functionality..."
cd "$REDZONE_HOME"
source .venv/bin/activate
python3 -c "
from agents.passive_recon.agent import run_passive_recon
print('✓ Imports working')
"
if [ $? -eq 0 ]; then
    log_success "Basic functionality test passed"
else
    log_error "Basic functionality test failed"
fi

# Step 8: Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_success "RedZone Installation Complete! ✅"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check what's installed
echo "📊 System Status:"
command -v python3 &> /dev/null && echo "  ✓ Python3" || echo "  ✗ Python3"
[ -d "$REDZONE_HOME/.venv" ] && echo "  ✓ Virtual Environment" || echo "  ✗ Virtual Environment"
[ -f "$REDZONE_HOME/requirements.txt" ] && echo "  ✓ Requirements" || echo "  ✗ Requirements"
[ -x "$REDZONE_HOME/redzone_recon" ] && echo "  ✓ CLI Tool" || echo "  ✗ CLI Tool"
command -v amass &> /dev/null && echo "  ✓ Amass" || echo "  ✗ Amass (optional)"
command -v sniper &> /dev/null && echo "  ✓ Sn1per" || echo "  ✗ Sn1per (optional)"
echo ""

# Next steps
echo "🚀 Next Steps:"
echo ""
echo "1️⃣  Test the CLI:"
echo "   cd $REDZONE_HOME"
echo "   source .venv/bin/activate"
echo "   ./redzone_recon github.com --json"
echo ""
echo "2️⃣  Start the Web UI:"
echo "   cd $REDZONE_HOME"
echo "   source .venv/bin/activate"
echo "   python3 redzone_server.py 8000"
echo "   Open: http://localhost:8000"
echo ""
echo "3️⃣  Install Amass (recommended):"
echo "   brew install amass"
echo ""
echo "4️⃣  Install Sn1per (recommended):"
echo "   cd /opt"
echo "   sudo git clone https://github.com/1N3/Sn1per.git"
echo "   cd Sn1per && sudo bash install.sh"
echo ""
echo "5️⃣  Run full test:"
echo "   ./redzone_recon github.com --deep --json"
echo ""

echo "📚 Documentation:"
echo "  - README_FULL_STACK.md - Complete guide"
echo "  - PASSIVE_RECON_SETUP.md - Setup instructions"
echo "  - PASSIVE_RECON_EXAMPLES.md - Usage examples"
echo "  - SYSTEM_TEST_REPORT.md - Test results"
echo ""

echo "✨ Happy Reconnaissance! 🎯"
echo ""
