#!/bin/bash

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print messages
function info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

function warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

function error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
    exit 1
}

# Step 1: Copy .env.template to .env if it doesn't exist
if [ -f "$dir/.env" ]; then
    info ".env file already exists. Skipping copy step."
else
    if [ -f "$dir/.env.template" ]; then
        info "Copying .env.template to .env..."
        cp "$dir/.env.template" "$dir/.env"
    else
        error ".env.example does not exist. Cannot create .env."
    fi
fi

# Step 2: Create a Python virtual environment if it doesn't exist
if [ -d "$dir/.venv" ]; then
    info "Virtual environment (.venv) already exists. Skipping creation step."
else
    info "Creating Python virtual environment in .venv..."
    python3 -m venv .venv ||
        error "Failed to create virtual environment."
fi

# Step 3: Activate the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    info "Activating the virtual environment..."
    source "$dir/.venv/bin/activate" ||
        error "Failed to activate virtual environment."
else
    info "Virtual environment already active. Skipping activation step."
fi

# Step 4: Install dependencies from requirements.txt if not already installed
if [ -f "$dir/requirements.txt" ]; then
    info "Checking and installing dependencies from requirements.txt..."
    pip install -r "$dir/requirements.txt" --quiet || error "Failed to install dependencies."
else
    warn "requirements.txt does not exist. Skipping dependencies installation."
fi

cd $dir/.venv/bin && ln -s $dir/scripts/run.sh run

info "Environment initialization complete!"
