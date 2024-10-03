from flask import Flask, jsonify
import requests
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['stock_database']
collection = db['stocks']

# Alpha Vantage API configuration
API_KEY = 'HV8ERYBJP6R0SFTH'  # Replace with your actual API key
BASE_URL = 'https://www.alphavantage.co/query'

# Fetch stock data from Alpha Vantage API
def fetch_real_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '5min',
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Check if the data is available
    if "Time Series (5min)" in data:
        last_refreshed = list(data['Time Series (5min)'].keys())[0]
        stock_info = data['Time Series (5min)'][last_refreshed]
        stock_data = {
            "symbol": symbol,
            "price": stock_info["1. open"],  # Use real-time price data
            "currency": "USD",
            "timestamp": last_refreshed
        }
        return stock_data
    else:
        return None

# API endpoint to fetch stock data
@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    stock_data = fetch_real_stock_data(symbol)

    if stock_data:
        # Insert the stock data into MongoDB
        result = collection.insert_one(stock_data)
        stock_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string

        return jsonify(stock_data)
    else:
        return jsonify({"error": "Stock data not available"}), 404

# Status endpoint to check if the service is running
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "Stock Data Service is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
