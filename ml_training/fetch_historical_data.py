import requests
import pandas as pd

# Alpha Vantage API configuration
API_KEY = 'HV8ERYBJP6R0SFTH'
BASE_URL = 'https://www.alphavantage.co/query'

def get_historical_data(symbol):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Parse the stock prices
    daily_data = data.get('Time Series (Daily)', {})
    stock_prices = []
    for date, price_data in daily_data.items():
        stock_prices.append({
            'date': date,
            'price': float(price_data['4. close'])  # Close price
        })
    
    return pd.DataFrame(stock_prices)

# Example usage
symbol = 'AAPL'
df = get_historical_data(symbol)
df.to_csv('aapl_historical_data.csv', index=False)
