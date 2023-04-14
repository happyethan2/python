import openai
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
import re

ALPACA_API_KEY = "X"
ALPACA_SECRET_KEY = "X"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

OPENAI_API_KEY = "sk-X"

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')
openai.api_key = OPENAI_API_KEY

def test_alpaca_api():
    account = api.get_account()
    print("Alpaca API test:")
    print("Account status:", account.status)

test_alpaca_api()

from datetime import timedelta

from datetime import timedelta

def calculate_sma(symbol, time_period, interval='day'):
    end_date = datetime.now().replace(second=0, microsecond=0)
    start_date = end_date - timedelta(days=time_period * 2)

    # Convert start_date and end_date to ISO 8601 format
    start_date_iso = start_date.isoformat()
    end_date_iso = end_date.isoformat()

    # Fetch historical price data using Alpaca's get_barset method
    data = api.get_barset(symbol, interval, start=start_date_iso, end=end_date_iso).df[symbol]

    if data.empty:
        return None
    sma = data['close'].rolling(window=time_period).mean().iloc[-1]
    if pd.isna(sma):
        return None
    return sma




def sma_crossover(symbol, sma_short_period=50, sma_long_period=200):
    sma_short = calculate_sma(symbol, sma_short_period)
    sma_long = calculate_sma(symbol, sma_long_period)
    if sma_short is None or sma_long is None:
        return None, None
    return sma_short, sma_long

def trade_signal(symbol):
    sma_short, sma_long = sma_crossover(symbol)
    if sma_short is None or sma_long is None:
        return None
    if sma_short > sma_long:
        return 'buy'
    else:
        return 'sell'

def ask_gpt3(system_content, user_content, max_tokens, n=1, stop=None, temperature=0):
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        max_tokens=max_tokens,
        n=n,
        stop=stop,
        temperature=temperature,
    )

    message = response.choices[0].message['content'].strip().lower()
    return message

def get_gpt3_analysis(statement):
    system_content = "You are a helpful assistant that analyzes monetary policy statements and rates their financial sentiment on a scale of -1 (very negative) to 1 (very positive)."
    user_content = f"Analyze the following monetary policy statement: {statement}"
    response = ask_gpt3(system_content, user_content, 100, temperature=0.5)
    print(response)

    # Extract the numerical sentiment score from the
    match = re.search(r"(-?\d\.\d)", response)
    if match:
        sentiment_score = float(match.group(1))
    else:
        sentiment_score = 0

    return sentiment_score

# Retrieve monetary policy statement (for demonstration purposes)
statement = "The economy is growing steadily, and the central bank is committed to maintaining stable inflation."

# Trading strategy
def execute_trading_strategy():
    # Define symbols for the ASX200 market index (initially) and commodities (later)
    symbols = ["SPY"]

    # Loop through the symbols and implement the trading strategy
    for symbol in symbols:
        # Get the trading signal based on SMA crossover
        signal = trade_signal(symbol)
        
        # Get the sentiment analysis score for the monetary policy statement
        sentiment_score = get_gpt3_analysis(statement)

        # Define trading rules based on sentiment score and trading signal
        if signal == 'buy' and sentiment_score > 0:
            # Submit a buy order, implement dynamic stop loss and take profit
            pass
        elif signal == 'sell' and sentiment_score < 0:
            # Submit a sell order, implement dynamic stop loss and take profit
            pass
        else:
            # Do nothing
            pass

# Run the trading strategy
execute_trading_strategy()
