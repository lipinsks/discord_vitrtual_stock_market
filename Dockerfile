# REMEMBER TO FIRST UPDATE YOUR BOT TOKEN

FROM ubuntu:latest

WORKDIR /discord_bot

# Install Python3, pip, and SQLite3
RUN apt-get update && apt-get install -y python3 python3-pip sqlite3

# Copy project files into the container
COPY . /discord_bot

# Create a virtual environment and install requirements in one step
RUN python3 -m venv bot_venv && \
    /discord_bot/bot_venv/bin/pip install -r resources/requirements.txt

# Initialize the SQLite database
RUN sqlite3 game.db < resources/schema.sql

# Ensure the bot script is executable (before copying it in local machine)
RUN chmod +x /discord_bot/run_bot.sh

# Run the bot using the virtual environment
CMD ["/discord_bot/bot_venv/bin/python", "./run_bot.sh"]

