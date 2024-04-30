import yfinance as yf
import logging
import stocks_names as stocks_names

# Configure logging
logging.basicConfig(level=logging.INFO)


class Stock:
    def __init__(self, name, symbol, price):
        self.name = name
        self.symbol = symbol
        self.price = price

    @staticmethod
    def get_stock_price(symbol):
        try:
            stock = yf.Ticker(symbol)
            today_price = stock.history(period='1d')
            if today_price.empty:
                # logging.warning(f"No data available for symbol {symbol}")
                return None
            else:
                price = today_price['Close'].iloc[0]
                return price
        except Exception as e:
            # logging.error(f"An error occurred while fetching data for {symbol}: {e}")
            return None


def get_stocks(stock_names):
    stocks_list = []
    for company, symbol in stock_names.items():
        price = Stock.get_stock_price(symbol)
        if price is not None:
            stocks_list.append(Stock(company, symbol, price))
    return stocks_list


def print_stocks(available_stocks):
    for stock in available_stocks:
        print(f"{stock.name}: {stock.price:.2f}")  # Format price to have one decimal place


def choose_stock(name):
    for stock in stocks:
        if stock.name == name:
            return stock.name, stock.price


# Fetch stocks data
stocks = get_stocks(stocks_names.stocks_names)
