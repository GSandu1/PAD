from flask import Flask, jsonify, request
import requests
from pymongo import MongoClient
import joblib
import numpy as np
import json

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['stock_database']
stock_collection = db['stocks']
prediction_collection = db['predictions']
transaction_history_collection = db['transaction_history']

# Alpha Vantage API configuration
API_KEY = 'PQMIDA6PVK1S96NQ'  
BASE_URL = 'https://www.alphavantage.co/query'

# Load the pre-trained machine learning model
model = joblib.load('stock_model.pkl')

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
        # Insert stock data into MongoDB
        stock_collection.insert_one(stock_data)
        return stock_data
    else:
        return None

# Fetch stock data from MongoDB or Alpha Vantage API if not cached
def get_stock_data(symbol):
    stock_data = stock_collection.find_one({"symbol": symbol}, sort=[("timestamp", -1)])
    if not stock_data:
        stock_data = fetch_real_stock_data(symbol)
    return stock_data

# Status endpoint to check if the service is running
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "Unified Stock Data & Prediction Service is running!"})


@app.route('/api/stocks/<symbol>/details', methods=['GET'])
def get_stock_details(symbol):
    # Fetch stock data from MongoDB
    stock_data = stock_collection.find_one({"symbol": symbol}, sort=[("timestamp", -1)])

    if not stock_data:
        return jsonify({"error": "Stock data not available"}), 404

    # Prepare the response
    stock_details = {
        "id": str(stock_data["_id"]),
        "symbol": stock_data["symbol"],
        "price": stock_data["price"],
        "currency": stock_data["currency"]
    }

    return jsonify(stock_details)


# API endpoint to fetch stock data and make predictions
@app.route('/api/predict/<symbol>', methods=['GET'])
def predict_stock(symbol):
    # Fetch stock data
    stock_data = get_stock_data(symbol)
    if not stock_data:
        return jsonify({"error": "Stock data not available"}), 404

    # Prepare the data for the ML model (using previous price as input)
    stock_price = float(stock_data["price"])
    input_data = np.array([[stock_price]])

    # Use the machine learning model to make a prediction
    prediction = model.predict(input_data)[0]

    # Determine "buy" or "sell" based on prediction value
    action = "buy" if prediction > 0 else "sell"

    # Construct prediction data in desired format
    prediction_data = {
        "symbol": symbol,
        "prediction": prediction,
        "action": action,
        "timestamp": stock_data["timestamp"]
    }

    # Insert prediction data into MongoDB
    inserted_data = prediction_collection.insert_one(prediction_data)
    
    # Update prediction_data with the ObjectId as a string
    prediction_data["_id"] = str(inserted_data.inserted_id)

    return jsonify(prediction_data)

# Endpoint to store transaction details
@app.route('/api/transactions/store', methods=['POST'])
def store_transaction():
    try:
        transaction_data = request.json
        print("Received transaction data:", transaction_data)
        
        # Force MongoDB to create collection by inserting sample data if empty
        if transaction_history_collection.count_documents({}) == 0:
            transaction_history_collection.insert_one({"test_key": "test_value"})
        
        transaction_history_collection.insert_one(transaction_data)
        return jsonify({"message": "Transaction stored successfully"}), 201
    except Exception as e:
        print(f"Error in store_transaction: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
