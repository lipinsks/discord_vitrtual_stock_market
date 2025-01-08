#TODO dodac parametry do get_stocks (period opcjonalne na "1mo") jest razem 8 funkcji do poprawienia -- BARDZO WAZNE !!!!!!

from datetime import datetime
import json
import logging
import sqlite3
import time
import pytz
import discord
from discord.ext import commands

from stocks_names import stocks_names
from stocks import get_stocks, choose_stock

conn = sqlite3.connect('game.db')
c = conn.cursor()

BOT_TOKEN = "YOUR DISCORD BOT TOKEN HERE"


# Define your class for user instances
class UserPlayer:
    def __init__(self, user_id, username, balance=10000.00, portfolio=None):
        self.user_id = user_id
        self.username = username
        self.balance = balance
        self.portfolio = portfolio or []

    def save_player_db(self):
        try:
            formatted_balance = "{:.2f}".format(self.balance)
            portfolio_json = json.dumps(self.portfolio)

            # Check if the user already exists in the database
            c.execute("SELECT * FROM discord_users WHERE user_id=?", (self.user_id,))
            existing_user = c.fetchone()

            if existing_user is None:
                # If the user doesn't exist, insert a new record
                c.execute("INSERT INTO discord_users (user_id, username, balance, portfolio) VALUES (?, ?, ?, ?)",
                          (self.user_id, self.username, formatted_balance, portfolio_json))
                conn.commit()
            else:
                print("Already saved")

        except Exception as e:
            logging.error(f"Error occurred while saving player to database: {e}")

    def update_player_db(self):
        try:
            formatted_balance = "{:.2f}".format(self.balance)
            # Convert the portfolio list to a JSON string
            portfolio_json = json.dumps(self.portfolio)

            # Execute SQL UPDATE query to update player's details
            c.execute("UPDATE discord_users SET balance=?, portfolio=? WHERE user_id=?",
                      (formatted_balance, portfolio_json, self.user_id))
            conn.commit()
        except Exception as e:
            logging.error(f"Error occurred while updating player in database: {e}")

    def combine_duplicate_entries(self):
        combined_portfolio = {}
        for stock_name, amount in self.portfolio:
            if stock_name in combined_portfolio:
                combined_portfolio[stock_name] += amount
            else:
                combined_portfolio[stock_name] = amount
        self.portfolio = [(stock_name, amount) for stock_name, amount in combined_portfolio.items()]

    def get_total_value(self, company, stocks):
        chosen_stock = choose_stock(company, stocks)
        stock_name = chosen_stock[0]
        stock_price = chosen_stock[1]

        value = 0
        for index, stock in enumerate(self.portfolio):
            if stock[0] == stock_name:  # Check if the stock is of the specified company
                amount_of_stock = stock[1]
                if amount_of_stock > 0:  # Ensure there are stocks available to sell
                    current_value = amount_of_stock * float(stock_price)
                    value += current_value
        if value >= 0:
            return value
        else:
            return 0

    def remove_zero(self):
        non_zero_stocks = []
        for stock in self.portfolio:
            stock_price = stock[1]
            if stock_price != 0:
                non_zero_stocks.append(stock)
        self.portfolio = non_zero_stocks
        print(self.portfolio)


# load users from sqlite3 database
def load_users_from_db():
    users = {}
    c.execute("SELECT user_id, username, balance, portfolio FROM discord_users")
    rows = c.fetchall()
    for row in rows:
        user_id, username, balance_str, portfolio_json = row
        user_id = int(user_id)  # Convert user_id to integer
        balance = float(balance_str)
        portfolio = json.loads(portfolio_json)
        users[user_id] = UserPlayer(user_id, username, balance, portfolio)
    return users


# Initialize bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Bot event: when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    # Load users from the database
    global user_instances
    user_instances = load_users_from_db()

    # Print the number of users loaded
    print(f'Loaded {len(user_instances)} users from the database.')


@bot.command()
async def register(ctx):
    user_id = ctx.author.id
    print(f"User ID from Discord: {user_id}")
    print(f"user_instances keys: {list(user_instances.keys())}")
    if user_id not in user_instances:
        print("User not found in user_instances")
        user_instance = UserPlayer(user_id, ctx.author.name)
        user_instances[user_id] = user_instance
        user_instance.save_player_db()
        await ctx.send(f"Successfully registered {ctx.author.name}, balance: ${user_instance.balance}.")
        print(f"user_instances: {user_instances}")

    else:
        await ctx.send("User already registered")


# Bot command: show balance
@bot.command()
async def balance(ctx):
    user_id = ctx.author.id
    if user_id in user_instances:
        # Fetch the UserPlayer object from user_instances
        user_instance = user_instances[user_id]
        # Fetch the balance from the UserPlayer object
        balance = user_instance.balance
        await ctx.send(f'{user_instance.username}, your balance is ${balance:.2f}')
    else:
        await ctx.send("Please register first. - !register")


# Bot command: show portfolio
@bot.command()
async def portfolio(ctx):
    user_id = ctx.author.id
    if user_id in user_instances:
        user_instance = user_instances[user_id]
        user_instance.combine_duplicate_entries()
        user_instance.remove_zero()
        if user_instance.portfolio:
            message = ""
            await ctx.send("Calculating...")
            stocks_for_total_value = get_stocks(stocks_names)
            if not user_instance.portfolio:
                await ctx.send("Your portfolio is empty.")

            full_value = 0

            for company, _ in user_instance.portfolio:
                stock_value = user_instance.get_total_value(company, stocks_for_total_value)
                full_value += stock_value

            for entry in user_instance.portfolio:
                stock_name, shares = entry  # Unpack the tuple
                formatted_value = f"{user_instance.get_total_value(stock_name, stocks_for_total_value):.2f}"
                formatted_shares = f"{shares:.4f}"
                message += f"{stock_name} - shares: {formatted_shares}, total value: ${formatted_value}\n"

            if user_instance.portfolio:
                message += f'Your portfolio is worth ${"{:.2f}".format(full_value)}'

            await ctx.send(message)

        else:
            await ctx.send("Your portfolio is empty.")
    else:
        await ctx.send("Please register first - !register")


# TODO finish
# print available stocks
@bot.command()
async def show_stocks(ctx, period: str):
    await ctx.send("Fetching stocks...")
    start_time = time.time()
    if period:
        stocks = get_stocks(stocks_names, period)
        message = "1 MONTH OLD STOCKS AND PRICES: "
    else:
        stocks = get_stocks(stock_names)
        message = "CURRENT STOCKS AND PRICES: "
    for stock in stocks:
        message += f"{stock.name} - price: ${stock.price:.2f}\n"
    finish_time = time.time()
    overall_time = finish_time - start_time
    await ctx.send(message)
    print(f"fetching stocks took: {overall_time} seconds.")

@bot.command()
async def buy(ctx, company: str, for_how_much: float):
    user_id = ctx.author.id
    if user_id in user_instances:
        user_instance = user_instances[user_id]

        if for_how_much > user_instance.balance:
            await ctx.send("Sorry, you don't have enough balance")
            return
        else:
            await ctx.send(f"Buying {company}...")

        stocks = get_stocks(stocks_names)
        chosen_stock = choose_stock(company,stocks)
        stock_name = chosen_stock[0]
        stock_price = chosen_stock[1]

        bought_stock_amount = for_how_much / float(stock_price)
        user_instance.portfolio.append((stock_name, bought_stock_amount))

        user_instance.balance -= for_how_much
        formatted_balance = "{:.2f}".format(user_instance.balance)

        user_instance.update_player_db()
        user_instance.combine_duplicate_entries()

        formatted_shares = f"{bought_stock_amount:.4f}"
        formatted_price = f"{for_how_much:.2f}"

        await ctx.send(
            f"Bought {formatted_shares} stocks of {company}, for: ${formatted_price}, remaining balance: ${formatted_balance}")
    else:
        await ctx.send("Please register first. - !register")


@bot.command()
async def sell(ctx, company: str, desired_price: float):
    user_id = ctx.author.id
    if user_id in user_instances:
        user_instance = user_instances[user_id]
        await ctx.send(f"Loading {company} stock...")

        stocks = get_stocks(stocks_names)
        chosen_stock = choose_stock(company, stocks)
        stock_name = chosen_stock[0]
        stock_price = chosen_stock[1]

        total_value = 0

        # Check if there are stocks available to sell for the specified company
        if any(stock[0] == stock_name and stock[1] > 0 for stock in user_instance.portfolio):
            for index, stock in enumerate(user_instance.portfolio):
                if stock[0] == stock_name and stock[1] > 0:
                    current_value = stock[1] * float(stock_price)
                    if current_value >= desired_price:
                        # Calculate the amount of stocks to sell to meet the desired price
                        amount_to_sell = desired_price / float(stock_price)
                        total_value += desired_price
                        user_instance.portfolio[index] = (
                            stock_name, stock[1] - amount_to_sell)  # Update the amount of stocks in portfolio
                        user_instance.balance += desired_price
                        await ctx.send(
                            f"Sold {company} stock for ${desired_price}. New balance: ${user_instance.balance}")

                        user_instance.update_player_db()
                        user_instance.combine_duplicate_entries()

                        return
        else:
            await ctx.send(f"You don't have enough {company} stock in your portfolio.")
    else:
        await ctx.send("Please register first - !register")


@bot.command()
async def sell_shares(ctx, company: str, shares: float):
    user_id = ctx.author.id
    if user_id in user_instances:
        user_instance = user_instances[user_id]
        await ctx.send(f"Loading {company} stock...")

        stocks = get_stocks(stocks_names)
        chosen_stock = choose_stock(company, stocks)
        stock_name = chosen_stock[0]
        stock_price = chosen_stock[1]

        for index, stock in enumerate(user_instance.portfolio):
            if stock[0] == stock_name and stock[1] >= shares:  # Check if enough stocks are available
                total_value = shares * float(stock_price)
                user_instance.balance += total_value
                remaining_shares = round(stock[1] - shares, 2)  # Round to 2 decimal places for remaining shares
                user_instance.portfolio[index] = (
                    stock_name, remaining_shares)  # Update the amount of stocks in portfolio
                formatted_balance = "{:.2f}".format(user_instance.balance)
                formatted_shares = "{:.2f}".format(shares)
                formatted_total_value = "{:.2f}".format(total_value)
                await ctx.send(
                    f"Sold {formatted_shares} shares of {company}, for total value of: ${formatted_total_value}, remaining balance: ${formatted_balance}")

                user_instance.update_player_db()
                user_instance.combine_duplicate_entries()

                return  # Exit the loop after selling the shares
        else:
            await ctx.send(f"You don't have enough shares of {company} to sell.")
    else:
        await ctx.send("Please register first - !register")


@bot.command()
async def sell_all(ctx, company: str):
    user_id = ctx.author.id
    if user_id in user_instances:
        user_instance = user_instances[user_id]
        await ctx.send(f"Loading {company} stock...")

        stocks = get_stocks(stocks_names)
        chosen_stock = choose_stock(company, stocks)
        stock_name = chosen_stock[0]
        stock_price = chosen_stock[1]

        total_value = 0
        for index, stock in enumerate(user_instance.portfolio):
            if stock[0] == stock_name:  # Check if the stock is of the specified company
                amount_of_stock = stock[1]
                if amount_of_stock > 0:  # Ensure there are stocks available to sell
                    current_value = amount_of_stock * float(stock_price)
                    total_value += current_value
                    user_instance.balance += current_value
                    user_instance.portfolio[index] = (stock_name, 0)  # Update the amount of stocks in portfolio

                    user_instance.update_player_db()
                    user_instance.combine_duplicate_entries()

        if total_value > 0:
            formatted_balance = "{:.2f}".format(user_instance.balance)
            formatted_total_value = "{:.2f}".format(total_value)
            await ctx.send(
                f"Sold all stocks of {company}, for total value of: ${formatted_total_value}, remaining balance: ${formatted_balance}")
        else:
            await ctx.send(f"You don't have any stocks of {company} to sell.")
    else:
        await ctx.send("Please register first - !register")


@bot.command()
async def market_status(ctx):
    def is_between_working_hours():
        # Get current time
        current_time = datetime.now(pytz.timezone('US/Eastern'))

        # Define working hours
        start_time = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        end_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)

        # Check if current time is between working hours
        return start_time <= current_time <= end_time

    if is_between_working_hours():
        await ctx.send("Market is open")
    else:
        await ctx.send("Market is closed")


@bot.command()
async def helper(ctx):
    await ctx.send("""

---------- WELCOME TO FINN VIRTUAL STOCK MARKET ----------

Trade with virtual money on a real life stock market:

Each player gets assigned $10000 to invest into top 50 stocks from Yahoo Stock Market.  
Whoever ends up with the biggest balance after n days wins.

To play along: !register

 - Available commands:
 
    - !show_stocks - show stock market prices
    
    - !balance - show balance of your account
    - !portfolio - show your portfolio content
    
    - !buy <company> <desired_price> - buy company shares for respective amount
    
    - !sell <company> <desired_price> - sell chosen company shares for respective amount
    - !sell_shares <company> <shares amount> - sell number of shares of chosen company
    - !sell_all <company> - sell all shares of chosen company
    
    - !market_status - check if market is open (you can still make trades when market is closed, only prices stay the same)
    
    
---------- GOOD LUCK ----------
""")


# Run the bot
bot.run(BOT_TOKEN)
