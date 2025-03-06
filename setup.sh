#!/bin/bash

# Debug mode - set to 1 to show detailed output, 0 to hide it
DEBUG=0

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --debug) DEBUG=1 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Helper function to log messages only in debug mode
log() {
    if [ "$DEBUG" -eq 1 ]; then
        echo "$1"
    fi
}

# Create virtual environment if it does not exist
if [ ! -d "venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv venv > /dev/null 2>&1
fi

# Activate virtual environment
log "Activating virtual environment..."
source venv/bin/activate

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    log "Installing dependencies from requirements.txt..."
    if [ "$DEBUG" -eq 1 ]; then
        pip install -r requirements.txt
    else
        pip install -r requirements.txt > /dev/null 2>&1
    fi
fi

# Check if Chrome is installed (needed for Selenium)
log "Checking Chrome installation (needed for Company Prospector)..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux check
    if ! command -v google-chrome &> /dev/null; then
        log "Google Chrome is required for the Company Prospector feature."
        log "You can install it with: sudo apt update && sudo apt install google-chrome-stable"
        log "Continuing with installation..."
    else
        log "Google Chrome is installed."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS check
    if ! [ -d "/Applications/Google Chrome.app" ]; then
        log "Google Chrome is required for the Company Prospector feature."
        log "You can install it from: https://www.google.com/chrome/"
        log "Continuing with installation..."
    else
        log "Google Chrome is installed."
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows check - basic check, might not work in all setups
    if ! [ -d "/c/Program Files/Google/Chrome" ] && ! [ -d "/c/Program Files (x86)/Google/Chrome" ]; then
        log "Google Chrome is required for the Company Prospector feature."
        log "You can install it from: https://www.google.com/chrome/"
        log "Continuing with installation..."
    else
        log "Google Chrome is installed."
    fi
fi

# Note about ChromeDriver
if [ "$DEBUG" -eq 1 ]; then
    log "Note: ChromeDriver is needed to run the Company Prospector feature."
    log "Selenium will attempt to find ChromeDriver automatically."
    log "If you experience issues, you may need to install ChromeDriver manually:"
    log "  - Visit https://chromedriver.chromium.org/downloads"
    log "  - Download the version matching your Chrome browser"
    log "  - Add it to your system PATH"
fi

# Update requirements.txt
log "Updating requirements.txt..."
if [ "$DEBUG" -eq 1 ]; then
    pip freeze > requirements.txt
else
    pip freeze > requirements.txt 2>/dev/null
fi

# Run main.py
log "Running main.py..."
# Export DEBUG flag so Python can access it
export CRM_DEBUG=$DEBUG
python3 main.py
