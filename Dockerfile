FROM ubuntu:latest

WORKDIR /discord_bot

# Install Python3, pip, venv, and SQLite3
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv sqlite3

# Copy project files into the container
COPY . /discord_bot

# Create a virtual environment and install requirements
RUN python3 -m venv bot_venv && \
    ./bot_venv/bin/python3 -m ensurepip --upgrade && \
    ./bot_venv/bin/python3 -m pip install --upgrade pip && \
    ./bot_venv/bin/python3 -m pip install -r resources/requirements.txt

# Initialize the SQLite database
RUN sqlite3 game.db < resources/schema.sql

# Run the bot directly using the virtual environment's Python interpreter
CMD ["./bot_venv/bin/python3", "src/discord_bot.py"]

