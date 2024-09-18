# 📈 Welcome to the Virtual Stock Market 📉

Welcome to our Virtual Stock Market project where you can engage with real-life stocks and prices in a virtual environment. Whether you're a seasoned investor or just curious about the stock market, this project offers a dynamic and interactive way to explore the world of stocks.

## Getting Started

If this is your first time running the project, follow these steps to set up your environment:

First of all, change BOT_TOKEN in src/discord_bot.py to your own generated token. 

```bash
source setup.sh
```
This command will initialize the database, set up a virtual environment with all the required dependencies, and prepare you to run the project.

## Running the project

Once the initial setup is complete, you can start the Discord bot by running:

```bash
./run_bot.sh
```

This command will launch the Discord bot in the background, allowing you to interact with the Virtual Stock Market. To terminate the bot, find its process ID by running:
```bash
ps aux | grep python
```

Then, run the following to kill the process found with command used before:
```bash
kill <PID>
```

### DOCKER
Alternatively, you can switch over to branch "dockerization" and complete deployment using Docker :)


### Feedback
Feel free to send me your feedback :)
