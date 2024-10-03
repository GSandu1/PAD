from flask import Flask, jsonify
import requests
import redis
import psycopg2
import json
import joblib
import numpy as np

app = Flask(__name__)

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="predictions_db", 
    user="postgres",
    password="1234",  # Replace with your PostgreSQL password
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Load the pre-trained machine learning model
model = joblib.load('stock_model.pkl')

# Fetch stock data from the Stock Data Service
def fetch_stock_data(symbol):
    response = requests.get(f'http://localhost:5001/api/stocks/{symbol}')
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Status endpoint to check if the service is running
@app.route('/status', methods=['GET'])
def status():
    return jsonify({'message': 'Prediction Service is running!'})

# Prediction endpoint using the machine learning model
@app.route('/api/predict/<symbol>', methods=['GET'])
def predict_stock(symbol):
    # Check if the prediction is cached in Redis
    cached_prediction = redis_client.get(symbol)
    if cached_prediction:
        return jsonify(json.loads(cached_prediction))

    # Fetch real stock data from Stock Data Service
    stock_data = fetch_stock_data(symbol)
    if not stock_data:
        return jsonify({"error": "Stock data not available"}), 404

    # Prepare the data for the ML model (using previous price as input)
    stock_price = float(stock_data["price"])
    input_data = np.array([[stock_price]])

    # Use the machine learning model to make a prediction
    prediction = model.predict(input_data)[0]

    # Insert the prediction into PostgreSQL
    cursor.execute("INSERT INTO predictions (symbol, prediction) VALUES (%s, %s)", (symbol, float(prediction)))
    conn.commit()

    # Cache the prediction in Redis
    prediction_data = {
        "symbol": symbol,
        "prediction": prediction
    }
    redis_client.set(symbol, json.dumps(prediction_data), ex=3600)  # Cache for 1 hour

    return jsonify(prediction_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
