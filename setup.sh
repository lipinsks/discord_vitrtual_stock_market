#!/bin/bash

# Create a virtual environment
python3 -m venv bot_venv

# Activate the virtual environment
source bot_venv/bin/activate

# Install requirements
pip install -r resources/requirements.txt

# Initialize the SQLite database
sqlite3 game.db < resources/schema.sql

# Allow running script
chmod +x run_bot.sh
