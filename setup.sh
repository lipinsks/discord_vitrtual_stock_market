#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "bot_venv" ]; then
    python3 -m venv bot_venv
fi

# Activate the virtual environment
source bot_venv/bin/activate

# Use the virtual environment's pip to install requirements
pip install -r resources/requirements.txt

# Check if the SQLite database already exists
if [ -f "game.db" ]; then
    echo "Database 'game.db' already exists. Skipping initialization."
else
    echo "Database 'game.db' does not exist. Initializing..."
    # Initialize the SQLite database
    sqlite3 game.db < resources/schema.sql
fi

# Allow running script
chmod +x run_bot.sh

echo "Setup completed."

