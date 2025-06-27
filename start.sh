#!/bin/bash

# ==============================================================================
# Intelligent Startup Script for Mobile Network QoE Tool
# ==============================================================================
# This script automates the setup and launch process, ensuring that all
# dependencies, database migrations, and initial data are in place before
# starting the application.
#
# It is idempotent, meaning it can be run safely multiple times.
# ==============================================================================

# --- Configuration ---
# Define colors for better output readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Step 1: Check for and install dependencies ---
echo -e "${YELLOW}Step 1: Checking and installing dependencies...${NC}"

if ! python3 -m pip install -r requirements.txt; then
    echo "Error: Failed to install dependencies. Please check your Python environment." >&2
    exit 1
fi
echo -e "${GREEN}Dependencies are up to date.${NC}
"

# --- Step 2: Initialize and migrate the database ---
echo -e "${YELLOW}Step 2: Setting up the database...${NC}"

# Check if the migrations directory exists. If not, initialize it.
if [ ! -d "migrations" ]; then
    echo "Migrations directory not found. Initializing database..."
    flask db init
    flask db migrate -m "Initial database setup"
fi

# Always run upgrade to apply any pending migrations
flask db upgrade
echo -e "${GREEN}Database is up to date.${NC}
"

# --- Step 3: Seed database and ensure admin user exists ---
echo -e "${YELLOW}Step 3: Seeding data and ensuring default admin user exists...${NC}"

# The 'setup-all' command is idempotent and will only create the user
# and seed data if it hasn't been done already.
flask setup-all
echo -e "${GREEN}Initial data is in place.${NC}
"

# --- Step 4: Start the application ---
echo -e "${YELLOW}Step 4: Launching the Mobile Network QoE Tool...${NC}"
echo "You can access the application at http://127.0.0.1:5000"

flask run
