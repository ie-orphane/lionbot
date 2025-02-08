#!/bin/bash

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print messages
function echo_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

function echo_warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

function echo_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
    exit 1
}

# Step 1: Copy .env.template to .env if it doesn't exist
if [ -f "$dir/.env" ]; then
    echo_info ".env file already exists. Skipping copy step."
else
    if [ -f "$dir/.env.template" ]; then
        echo_info "Copying .env.template to .env..."
        cp "$dir/.env.template" "$dir/.env"
    else
        echo_error ".env.template does not exist. Cannot create .env."
    fi
fi

# Step 2: Create a Python virtual environment if it doesn't exist
if [ -d "$dir/.venv" ]; then
    echo_info "Virtual environment (.venv) already exists. Skipping creation step."
else
    echo_info "Creating Python virtual environment in .venv..."
    python3 -m venv .venv ||
        echo_error "Failed to create virtual environment."
fi

# Step 3: Activate the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo_info "Activating the virtual environment..."
    source "$dir/.venv/bin/activate" ||
        echo_error "Failed to activate virtual environment."
else
    echo_info "Virtual environment already active. Skipping activation step."
fi

# Step 4: Install dependencies from requirements.txt if not already installed
if [ -f "$dir/requirements.txt" ]; then
    echo_info "Checking and installing dependencies from requirements.txt..."
    pip install -r "$dir/requirements.txt" --quiet || echo_error "Failed to install dependencies."
else
    echo_warn "requirements.txt does not exist. Skipping dependencies installation."
fi

echo_info "Environment initialization complete!"
